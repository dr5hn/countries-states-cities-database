#!/usr/bin/env python3
"""Åland Islands -> contributions/postcodes/AX.json importer for issue #1039.

Source data
-----------
Same source as Finland: Posti.fi's daily PCF (postal code file).
Åland-specific records carry region code ``FI200`` / region name
``Ahvenanmaa`` (the Finnish name for Åland Islands).

The companion FI importer (``import_finland_postcodes.py``) skips
these 37 records since AX is its own CSC country (iso2=AX,
country_id=2).

Source URL: https://www.posti.fi/webpcode/unzip/PCF_<YYYYMMDD>.dat

What this script does
---------------------
1. Probes the URL pattern back ~30 days (same as FI importer).
2. Filters DAT records to region code FI200 only.
3. Resolves state FK by matching the source's municipality name
   against CSC's 16 AX states. Only one drift handled:
   'Maarianhamina' (Finnish) -> 'Mariehamn' (Swedish, the CSC
   canonical form).
4. Writes contributions/postcodes/AX.json idempotently.

License & attribution
---------------------
- Source: Posti.fi PCF (Tier 5 per #1039 license-tier policy)
- Each row: ``source: "posti-fi-pcf"``

Usage
-----
    python3 bin/scripts/sync/import_aland_postcodes.py
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List


URL_TEMPLATE = "https://www.posti.fi/webpcode/unzip/PCF_{date}.dat"

# Source municipality (Finnish form) -> CSC AX name (Swedish form).
# The 15 other municipality names already match CSC verbatim.
MUNICIPALITY_ALIASES: Dict[str, str] = {
    "Maarianhamina": "Mariehamn",
}


def resolve_pcf_url(max_days_back: int = 30) -> str:
    today = datetime.date.today()
    for delta in range(0, max_days_back):
        d = today - datetime.timedelta(days=delta)
        url = URL_TEMPLATE.format(date=d.strftime("%Y%m%d"))
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "csc-database-postcode-importer"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    return url
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
    raise RuntimeError(f"No PCF DAT found in last {max_days_back} days")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("iso-8859-1")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local DAT (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="iso-8859-1")
    else:
        url = resolve_pcf_url()
        print(f"fetching {url}")
        text = fetch_text(url)

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    ax_country = next((c for c in countries if c.get("iso2") == "AX"), None)
    if ax_country is None:
        print("ERROR: AX not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ax_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ax_states = [s for s in states if s.get("country_id") == ax_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"]: s for s in ax_states if s.get("name")}
    print(
        f"Country: Åland Islands (id={ax_country['id']}); "
        f"states indexed: {len(ax_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_munis: Dict[str, int] = {}
    total_aland_rows = 0

    for line in text.splitlines():
        if len(line) < 220:
            continue
        region_code = line[111:116].strip()
        if region_code != "FI200":
            continue
        total_aland_rows += 1

        code = line[13:18].strip()
        postal_name_fi = line[18:48].strip()
        postal_name_sv = line[48:78].strip()
        muni_fi = line[179:199].strip()
        muni_sv = line[199:219].strip()

        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        # Prefer Swedish municipality name (CSC canonical form);
        # fall back through alias map for Finnish-only labels.
        csc_name = (
            muni_sv
            if muni_sv in state_by_name
            else MUNICIPALITY_ALIASES.get(muni_fi, muni_fi)
        )
        state = state_by_name.get(csc_name)
        if state is None:
            unknown_munis[(muni_fi, muni_sv)] = (
                unknown_munis.get((muni_fi, muni_sv), 0) + 1
            )
            skipped_no_state += 1

        # Locality: use Swedish postal name (Åland's official language)
        if postal_name_sv and muni_sv and postal_name_sv.lower() != muni_sv.lower():
            locality = f"{postal_name_sv}, {muni_sv}"
        else:
            locality = postal_name_sv or muni_sv

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ax_country["id"]),
            "country_code": "AX",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "posti-fi-pcf"
        records.append(record)

    print(f"Åland source rows:    {total_aland_rows:,}")
    print(f"Skipped (regex fail): {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_munis:
        print("Unknown municipalities (not in CSC + MUNICIPALITY_ALIASES):")
        for m, n in sorted(unknown_munis.items(), key=lambda x: -x[1]):
            print(f"  {m!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/AX.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        existing_seen = {
            (r["code"], (r.get("locality_name") or "").lower()) for r in existing
        }
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in existing_seen:
                merged.append(r)
                existing_seen.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = sorted(records, key=lambda r: (r["code"], r.get("locality_name", "")))

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_kb = target.stat().st_size / 1024
    print(
        f"\n[OK] Wrote {target.relative_to(project_root)} "
        f"({len(merged):,} rows, {size_kb:.0f} KB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
