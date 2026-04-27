#!/usr/bin/env python3
"""OpenPLZ -> contributions/postcodes/{DE,AT,CH,LI}.json importer for issue #1039.

Source data
-----------
OpenPLZ API (https://openplzapi.org) publishes structured German-speaking
country postal data under the **ODbL-1.0** licence — an exact match for the
licence on this repository. The API exposes a hierarchical model:

  Germany       /de/FederalStates/{key}/Localities
  Austria       /at/FederalProvinces/{key}/Localities
  Switzerland   /ch/Cantons/{key}/Localities
  Liechtenstein /li/Communes (no drilldown, ~13 localities)

Each Locality record carries: postalCode, name, municipality, district,
and federalState/Province/Canton.

Volumes (as of 2026)
- DE: ~12,800 localities across 16 federal states
- AT: ~18,900 localities across 9 federal provinces
- CH: ~5,000 localities across 26 cantons
- LI: 13 localities (already curated manually in contributions/postcodes/LI.json)

What this script does
---------------------
1. Walks each country's regional hierarchy via the OpenPLZ REST API
2. Paginates through Localities (50/page) following x-total-count headers
3. Resolves country_id from countries.json by ISO2
4. Resolves state_id by exact case-insensitive name match against states.json
   (with light DE/AT/CH umlaut + Bezirk-suffix handling)
5. Writes contributions/postcodes/{ISO2}.json per country
6. Idempotent merge: existing curated rows preserved by code

License & attribution
---------------------
Source: OpenPLZ (https://openplzapi.org), licensed under ODbL-1.0.
Each generated row sets ``source: "openplz"`` for attribution tracking.
The repository's existing ODbL-1.0 stance covers redistribution.

Usage
-----
    # Direct fetch (requires network access to openplzapi.org)
    python3 bin/scripts/sync/import_openplz_postcodes.py

    # Single country
    python3 bin/scripts/sync/import_openplz_postcodes.py --countries DE

    # Dry run — print summary, do not write
    python3 bin/scripts/sync/import_openplz_postcodes.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

OPENPLZ_BASE = "https://openplzapi.org"

# Per-country region endpoint and locality drilldown shape
COUNTRY_CONFIG: Dict[str, dict] = {
    "DE": {
        "regions": "/de/FederalStates",
        "localities": "/de/FederalStates/{key}/Localities",
        "state_field": "federalState",
    },
    "AT": {
        "regions": "/at/FederalProvinces",
        "localities": "/at/FederalProvinces/{key}/Localities",
        "state_field": "federalProvince",
    },
    "CH": {
        "regions": "/ch/Cantons",
        "localities": "/ch/Cantons/{key}/Localities",
        "state_field": "canton",
    },
    # LI deliberately omitted: contributions/postcodes/LI.json is curated
    # (#1401) and OpenPLZ's per-code endpoint returns multiple sub-localities
    # per code that would muddy the existing clean 1:1 commune mapping.
}

PAGE_SIZE = 50
USER_AGENT = "csc-database-postcode-importer (+https://github.com/dr5hn/countries-states-cities-database)"


def http_get_json(url: str, timeout: int = 30) -> Tuple[List[dict], Optional[int]]:
    """GET a URL, return (json_body, x-total-count or None)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        total = resp.headers.get("x-total-count")
        try:
            total_n = int(total) if total else None
        except ValueError:
            total_n = None
        body = json.load(resp)
    if not isinstance(body, list):
        body = [body]
    return body, total_n


def fetch_regions(iso2: str) -> List[dict]:
    cfg = COUNTRY_CONFIG[iso2]
    body, _ = http_get_json(OPENPLZ_BASE + cfg["regions"])
    return body


def fetch_localities_for_region(iso2: str, region_key: str, sleep: float = 0.05) -> List[dict]:
    """Paginate /Localities for one region until x-total-count is reached."""
    cfg = COUNTRY_CONFIG[iso2]
    template = cfg.get("localities")
    if template is None:
        return []
    base = OPENPLZ_BASE + template.format(key=region_key)
    out: List[dict] = []
    page = 1
    total: Optional[int] = None
    while True:
        url = f"{base}?page={page}&pageSize={PAGE_SIZE}"
        body, hdr_total = http_get_json(url)
        if total is None and hdr_total is not None:
            total = hdr_total
        out.extend(body)
        if not body or (total is not None and len(out) >= total):
            break
        page += 1
        time.sleep(sleep)
    return out


def normalise_name(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    # OpenPLZ uses slash-separated multilingual names like
    # "Fribourg / Freiburg" or "Graubünden / Grigioni / Grischun".
    # Take the first variant before any slash so the state-name match is
    # against a single canonical form.
    if "/" in s:
        s = s.split("/", 1)[0].strip()
    # Replace common umlaut/eszett variants with ASCII equivalents
    table = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "s", "é": "e", "è": "e", "ê": "e"})
    s = s.translate(table)
    # Drop trailing administrative suffixes like ", Stadt" or "(Bezirk)"
    s = re.sub(r"[,\(].*$", "", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s


# Per-country aliases: canonical-state-name (in states.json normalised form)
# keyed by what OpenPLZ returns (also normalised). Used as a second-pass
# lookup when the direct normalised match misses (translation differences).
STATE_ALIASES: Dict[str, Dict[str, str]] = {
    "CH": {
        "luzern": "lucerne",
        "geneve": "geneva",
        "basel-landschaft": "basel-land",
    },
    "AT": {
        # OpenPLZ uses German names; states.json uses English
        "karnten": "carinthia",
        "niederosterreich": "lower austria",
        "oberosterreich": "upper austria",
        "steiermark": "styria",
        "tirol": "tyrol",
        "wien": "vienna",
    },
}


def build_state_lookup(states: List[dict], country_id: int) -> Dict[str, dict]:
    lookup: Dict[str, dict] = {}
    for s in states:
        if s.get("country_id") != country_id:
            continue
        for cand in (s.get("name"), s.get("native")):
            if cand:
                lookup[normalise_name(cand)] = s
    return lookup


def resolve_state(name: str, lookup: Dict[str, dict], iso2: Optional[str] = None) -> Optional[dict]:
    if not name:
        return None
    norm = normalise_name(name)
    if norm in lookup:
        return lookup[norm]
    aliases = STATE_ALIASES.get(iso2 or "") or {}
    aliased = aliases.get(norm)
    if aliased and aliased in lookup:
        return lookup[aliased]
    return None


def parse_coord(v) -> Optional[str]:
    if v in (None, ""):
        return None
    try:
        f = float(v)
        if abs(f) > 180:
            return None
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except (TypeError, ValueError):
        return None


def build_records(
    iso2: str,
    country_id: int,
    localities: Iterable[dict],
    state_lookup: Dict[str, dict],
) -> List[dict]:
    cfg = COUNTRY_CONFIG[iso2]
    state_field = cfg["state_field"]

    seen_codes: set = set()
    records: List[dict] = []
    for loc in localities:
        code = (loc.get("postalCode") or "").strip()
        name = (loc.get("name") or "").strip()
        if not code or not name:
            continue
        # OpenPLZ returns multiple rows when the same code serves several
        # localities (e.g. 80331 Munich Altstadt vs Lehel). The schema
        # treats one row per code as canonical, so dedupe on first occurrence
        # — alphabetical ordering keeps results deterministic across runs.
        dedup_key = (code, name.lower())
        if dedup_key in seen_codes:
            continue
        seen_codes.add(dedup_key)

        record = {
            "code": code,
            "country_id": country_id,
            "country_code": iso2,
        }

        state_obj = loc.get(state_field) or {}
        state = resolve_state(
            state_obj.get("name") if isinstance(state_obj, dict) else None,
            state_lookup,
            iso2,
        )
        if state is not None:
            record["state_id"] = int(state["id"])
            if state.get("iso2"):
                record["state_code"] = state["iso2"]

        record["locality_name"] = name
        record["type"] = "full"

        # OpenPLZ does not currently expose per-locality coordinates in the
        # localities endpoint; leaving lat/lng null is correct.
        record["source"] = "openplz"
        records.append(record)

    # Deterministic sort by code, then locality name
    records.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    return records


def merge_with_existing(project_root: Path, iso2: str, new_records: List[dict]) -> List[dict]:
    target = project_root / f"contributions/postcodes/{iso2}.json"
    if not target.exists():
        return sorted(new_records, key=lambda r: (r["code"], r.get("locality_name", "")))
    with target.open(encoding="utf-8") as f:
        existing = json.load(f)

    # Preserve existing rows by (code, locality_name) so a city with multiple
    # already-curated entries doesn't lose any of them. New OpenPLZ rows are
    # appended only if their (code, locality_name) is not already present.
    seen: set = set()
    merged: List[dict] = []
    for r in existing + new_records:
        key = (r["code"], (r.get("locality_name") or "").lower())
        if key in seen:
            continue
        seen.add(key)
        merged.append(r)
    merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countries", default="DE,AT,CH",
                        help="Comma-separated ISO2 codes to import (LI omitted; already curated)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print summary; do not write files")
    parser.add_argument("--sleep", type=float, default=0.05,
                        help="Sleep between API requests (seconds)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    countries_by_iso2 = {c["iso2"]: c for c in countries if c.get("iso2")}

    targets = [t.strip().upper() for t in args.countries.split(",") if t.strip()]
    summary: Dict[str, dict] = {}

    for iso2 in targets:
        if iso2 not in COUNTRY_CONFIG:
            print(f"skip {iso2}: not configured", file=sys.stderr)
            continue
        country = countries_by_iso2.get(iso2)
        if country is None:
            print(f"skip {iso2}: not in countries.json", file=sys.stderr)
            continue
        cid = int(country["id"])
        state_lookup = build_state_lookup(states, cid)
        print(f"\n=== {iso2} {country['name']} (id={cid}) ===")

        localities: List[dict] = []
        try:
            regions = fetch_regions(iso2)
            print(f"  regions: {len(regions)}")
            for region in regions:
                region_name = region.get("name") or region.get("shortName") or region.get("key")
                rows = fetch_localities_for_region(iso2, region["key"], sleep=args.sleep)
                localities.extend(rows)
                print(f"    {region_name}: {len(rows)}")
        except urllib.error.HTTPError as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            continue

        records = build_records(iso2, cid, localities, state_lookup)
        with_state = sum(1 for r in records if "state_id" in r)
        summary[iso2] = {
            "fetched": len(localities),
            "records": len(records),
            "with_state": with_state,
        }
        print(f"  records: {len(records):,}  state-resolved: {with_state:,} ({with_state*100//max(1,len(records))}%)")

        if not args.dry_run:
            merged = merge_with_existing(project_root, iso2, records)
            target = project_root / f"contributions/postcodes/{iso2}.json"
            with target.open("w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)
                f.write("\n")
            size_mb = target.stat().st_size / (1024 * 1024)
            print(f"  wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_mb:.1f} MB)")

    print("\n=== Summary ===")
    for iso2, s in summary.items():
        print(f"  {iso2}: fetched {s['fetched']:,}, records {s['records']:,}, with state {s['with_state']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
