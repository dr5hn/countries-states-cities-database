#!/usr/bin/env python3
"""Svalbard and Jan Mayen -> contributions/postcodes/SJ.json importer for issue #1039.

Source data
-----------
Svalbard archipelago and Jan Mayen Island are administered by
Norway and use Norwegian post codes:

    Svalbard codes  9170, 9171  Longyearbyen
                    9173        Ny-Ålesund
                    9174        Hopen weather station
                    9175        Sveagruva (decommissioned)
                    9176        Bjørnøya (Bear Island)
                    9178        Barentsburg (Russian mining settlement)

    Jan Mayen code  8099        Jan Mayen weather station

These codes are already shipped in contributions/postcodes/NO.json
under Norwegian state 21 (Svalbard) and 22 (Jan Mayen). CSC
represents Svalbard and Jan Mayen as their own country (iso2=SJ,
country_id=211), so this importer mirrors the codes into a
companion SJ.json under the SJ namespace.

What this script does
---------------------
1. Reads existing NO.json filtered to state codes 21 (Svalbard) +
   22 (Jan Mayen).
2. Re-FKs each row to country_id=211 (SJ).
3. Country-only ship — SJ has no sub-state hierarchy in CSC.

License & attribution
---------------------
- Original source: Bring (Norway Post) via the Norway importer
  (CC-BY-equivalent free-redistribution per #1039 license-tier policy)
- Each row: ``source: "bring-via-sj-mirror"``

Usage
-----
    python3 bin/scripts/sync/import_svalbard_jan_mayen_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List


SVALBARD_CODES = {"9170", "9171", "9173", "9174", "9175", "9176", "9178"}
JAN_MAYEN_CODES = {"8099"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]

    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    sj_country = next((c for c in countries if c.get("iso2") == "SJ"), None)
    if sj_country is None:
        print("ERROR: SJ not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(sj_country.get("postal_code_regex") or ".*")

    no_path = project_root / "contributions/postcodes/NO.json"
    if not no_path.exists():
        print("ERROR: NO.json missing", file=sys.stderr)
        return 2
    no_data = json.load(no_path.open(encoding="utf-8"))

    target_codes = SVALBARD_CODES | JAN_MAYEN_CODES
    sj_rows = [r for r in no_data if r.get("code") in target_codes]
    print(f"Source SJ-target rows in NO.json: {len(sj_rows)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for r in sj_rows:
        code = r["code"]
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        locality = r.get("locality_name") or ""
        # Title-case the bring-shipped uppercase locality
        if locality.isupper():
            locality = locality.title().replace("-Å", "-Å").replace("Ø", "Ø")
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(sj_country["id"]),
            "country_code": "SJ",
        }
        if locality:
            record["locality_name"] = locality
        for field in ("latitude", "longitude"):
            v = r.get(field)
            if v is not None and v != "":
                record[field] = v
        record["type"] = "full"
        record["source"] = "bring-via-sj-mirror"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/SJ.json"
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
