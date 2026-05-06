#!/usr/bin/env python3
"""Namibia -> contributions/postcodes/NA.json importer for issue #1039.

Source data
-----------
The community ``KuberKode/namibia-postal-codes`` repository ships
NamPost (Namibia Post Limited) postal codes scraped from the
official PDF directory and reorganised into nested JSON:

    {
      "Country": { "Alpha-2": "NA", "Regions": [
        { "RegionName": "Erongo", "RegionCode": "NA-ER",
          "Locations": [
            { "Location": "Swakopmund", "Postal Code": 13001 }, ...
          ]
        }, ...
      ]}
    }

14 regions × ~10-35 locations each = ~155 codes, 5-digit numeric.

Source URL: https://raw.githubusercontent.com/KuberKode/namibia-postal-codes/main/namibia-postal-codes.json

What this script does
---------------------
1. Fetches the JSON via urllib.
2. Walks ``Country.Regions[].Locations[]``.
3. Maps source ``RegionCode`` ("NA-XX") to CSC iso2 by stripping
   the ``NA-`` prefix — all 14 region codes match CSC's states.json
   directly (ER, HA, KA, KE, KW, KH, KU, OW, OH, OS, ON, OT, OD, CA).
4. Writes contributions/postcodes/NA.json idempotently.

Coverage
--------
~155 records covering all 14 Namibian regions. Khomas (Windhoek
metro) is the densest at ~35 codes; sparser rural regions like
Kavango West average 2-6.

License & attribution
---------------------
- Source: KuberKode/namibia-postal-codes (Unlicense / public domain)
- Original data: NamPost public postal-code directory
- Each row: ``source: "nampost-via-kuberkode"``

Usage
-----
    python3 bin/scripts/sync/import_namibia_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/KuberKode/namibia-postal-codes/"
    "main/namibia-postal-codes.json"
)


def fetch_json(url: str) -> dict:
    """Fetch and parse JSON via urllib."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    payload = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    regions = payload.get("Country", {}).get("Regions", [])
    print(f"Source regions: {len(regions)}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    na_country = next((c for c in countries if c.get("iso2") == "NA"), None)
    if na_country is None:
        print("ERROR: NA not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(na_country.get("postal_code_regex") or ".*")

    states_all = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    na_states = [s for s in states_all if s.get("country_id") == na_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in na_states if s.get("iso2")
    }
    print(
        f"Country: Namibia (id={na_country['id']}); "
        f"states indexed: {len(na_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    matched_state = 0
    unknown_regions: Dict[str, int] = {}

    for region in regions:
        region_code = (region.get("RegionCode") or "").strip()
        # RegionCode is ISO 3166-2 ("NA-ER"); strip prefix.
        iso2 = region_code.split("-", 1)[-1] if region_code else ""
        state = state_by_iso2.get(iso2)
        if state is None:
            unknown_regions[region_code] = (
                unknown_regions.get(region_code, 0) + len(region.get("Locations", []))
            )

        for loc in region.get("Locations", []):
            raw_code = loc.get("Postal Code")
            if raw_code is None:
                continue
            # Codes ship as integers — re-pad to 5 digits.
            code = str(raw_code).zfill(5)
            if not regex.match(code):
                skipped_bad_regex += 1
                continue

            locality = (loc.get("Location") or "").strip()
            key = (code, locality.lower())
            if key in seen:
                continue
            seen.add(key)

            record: Dict[str, object] = {
                "code": code,
                "country_id": int(na_country["id"]),
                "country_code": "NA",
            }
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = state.get("iso2")
                matched_state += 1
            if locality:
                record["locality_name"] = locality
            record["type"] = "full"
            record["source"] = "nampost-via-kuberkode"
            records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_regions:
        print("Unknown RegionCodes (not in CSC states.json):")
        for r, n in sorted(unknown_regions.items(), key=lambda x: -x[1]):
            print(f"  {r!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/NA.json"
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
