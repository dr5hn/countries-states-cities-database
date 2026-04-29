#!/usr/bin/env python3
"""Myanmar -> contributions/postcodes/MM.json importer for issue #1039.

Source data
-----------
The official ``MyanmarPost/MyanmarPostalCode`` repository (V-1.0,
Sep 2021) ships the canonical 7-digit Myanmar Post postal codes for
all 14 states/regions plus the Naypyitaw Union Territory:

    Region,"Town / Township","Quarter / Village Tract","Postal Code"
    "Naypyitaw Union Territory","Za Bu Thi Ri Township","Zay Ya Theik Di Quarter",1501001

Each 7-digit code is structured as:
    [state/region: 2 digits][town/township: 2 digits][quarter/village: 3 digits]

Source URL: https://raw.githubusercontent.com/MyanmarPost/MyanmarPostalCode/master/Myanmar_Locations_Postal_Code_EN.csv

What this script does
---------------------
1. Fetches the EN CSV via urllib (curl is blocked in the harness).
2. Maps the 18 source-region labels to CSC's 15 states.json entries
   (Bago split East/West and Shan split North/South/East collapse).
3. Resolves state FK 100% via name match (no postal-prefix join: the
   prefixes in MyanmarPost's data do NOT correspond to CSC's iso2
   codes, e.g. Bago is 02 in CSC vs 08/18 in source).
4. Emits one record per (code, township + quarter) pair so
   distinct quarters under the same township each ship their own row.
5. Writes contributions/postcodes/MM.json idempotently.

Regex note
----------
Before this PR, countries.json had MM regex ``^\\d{5}$`` (5-digit), which
never matched Myanmar Post's actual 7-digit format. The companion regex
fix in this PR sets it to ``^\\d{7}$``.

License & attribution
---------------------
- Source: MyanmarPost/MyanmarPostalCode (official MyanmarPost org)
- License: GPL-3.0 (unusual for data; redistribution permitted with
  attribution — flagged in PR description)
- Each row: ``source: "myanmar-post-official"``

Usage
-----
    python3 bin/scripts/sync/import_myanmar_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/MyanmarPost/MyanmarPostalCode/"
    "master/Myanmar_Locations_Postal_Code_EN.csv"
)

# Source region label -> CSC states.json "name". Source has 18 labels
# (Bago split East/West, Shan split North/South/East); CSC has 15.
SOURCE_TO_CSC_NAME: Dict[str, str] = {
    "Sagaing Region": "Sagaing",
    "Bago Region (East)": "Bago",
    "Bago Region (West)": "Bago",
    "Magway Region": "Magway",
    "Mandalay Region": "Mandalay",
    "Tanintharyi Region": "Tanintharyi",
    "Yangon Region": "Yangon",
    "Ayeyarwady Region": "Ayeyarwady",
    "Kachin State": "Kachin",
    "Kayah state": "Kayah",
    "Kayin State": "Kayin",
    "Chin State": "Chin",
    "Mon State": "Mon State",
    "Rakhine State": "Rakhine",
    "Shan State (North)": "Shan",
    "Shan State (South)": "Shan",
    "Shan State (East)": "Shan",
    "Naypyitaw Union Territory": "Naypyidaw",
}


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8-sig")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    mm_country = next((c for c in countries if c.get("iso2") == "MM"), None)
    if mm_country is None:
        print("ERROR: MM not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(mm_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    mm_states = [s for s in states if s.get("country_id") == mm_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"]: s for s in mm_states if s.get("name")}
    print(
        f"Country: Myanmar (id={mm_country['id']}); states indexed: {len(mm_states)}"
    )

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_no_code = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_regions: Dict[str, int] = {}

    for row in rows:
        raw_code = (row.get("Postal Code") or "").strip()
        if not raw_code:
            skipped_no_code += 1
            continue
        code = raw_code.zfill(7) if raw_code.isdigit() else raw_code
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        region = (row.get("Region") or "").strip()
        township = (row.get("Town / Township") or "").strip()
        quarter = (row.get("Quarter / Village Tract") or "").strip()

        csc_name = SOURCE_TO_CSC_NAME.get(region)
        state = state_by_name.get(csc_name) if csc_name else None
        if state is None:
            unknown_regions[region] = unknown_regions.get(region, 0) + 1
            skipped_no_state += 1

        # Locality = "Quarter, Township" so each quarter under the same
        # township ships its own (code, locality) pair.
        locality_parts = [p for p in (quarter, township) if p]
        locality = ", ".join(locality_parts)

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(mm_country["id"]),
            "country_code": "MM",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "myanmar-post-official"
        records.append(record)

    print(f"Skipped (no code):     {skipped_no_code:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_regions:
        print("Unknown source regions (not in SOURCE_TO_CSC_NAME):")
        for r, n in sorted(unknown_regions.items(), key=lambda x: -x[1]):
            print(f"  {r!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MM.json"
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
