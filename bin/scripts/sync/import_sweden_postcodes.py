#!/usr/bin/env python3
"""Sweden -> contributions/postcodes/SE.json importer for issue #1039.

Source data
-----------
The community-maintained ``zegl/sweden-zipcode`` archive redistributes a
plain Zip,City CSV covering 16,393 Swedish postcodes.

  https://github.com/zegl/sweden-zipcode

What this script does
---------------------
1. Reads sweden-zipcode.csv (UTF-8, header: Zip,City)
2. Picks one canonical record per unique zip (first city alphabetically
   when multiple rows exist for one code)
3. Formats codes in the canonical "### ##" form expected by
   countries.postal_code_regex (^(?:SE)?\\d{3}\\s\\d{2}$)
4. Writes contributions/postcodes/SE.json

Why state_id is null
--------------------
Swedish postcodes were assigned by sorting-route geography rather than
by administrative county boundaries, so there is no reliable prefix-to-
county mapping. The source CSV has no kommune column either. State
resolution would require a separate kommune-postcode crosswalk that
isn't redistributable. Records ship with country_id only; state_id can
be backfilled in a follow-up PR once a clean kommune crosswalk is wired
in (e.g. via Skatteverket's open ortsdata).

License & attribution
---------------------
- Mirror: github.com/zegl/sweden-zipcode (community redistribution)
- Each row: source: "se-zipcode"
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/se_zipcodes.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    se = next((c for c in countries if c.get("iso2") == "SE"), None)
    if se is None:
        print("ERROR: SE not in countries.json", file=sys.stderr)
        return 2
    print(f"Country: Sweden (id={se['id']})")

    by_code: Dict[str, List[str]] = {}
    with src.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            zip_raw = (row.get("Zip") or "").strip()
            city = (row.get("City") or "").strip()
            if not zip_raw or not zip_raw.isdigit() or len(zip_raw) != 5:
                continue
            # Format ### ##
            code = f"{zip_raw[:3]} {zip_raw[3:]}"
            by_code.setdefault(code, []).append(city)

    print(f"Unique zips: {len(by_code):,}")

    records: List[dict] = []
    for code in sorted(by_code):
        cities = sorted(by_code[code], key=lambda c: c.upper())
        record = {
            "code": code,
            "country_id": int(se["id"]),
            "country_code": "SE",
        }
        if cities and cities[0]:
            record["locality_name"] = cities[0]
        record["type"] = "full"
        record["source"] = "se-zipcode"
        records.append(record)

    print(f"Records: {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/SE.json"
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        seen = {(r["code"], (r.get("locality_name") or "").lower()) for r in existing}
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in seen:
                merged.append(r)
                seen.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = sorted(records, key=lambda r: (r["code"], r.get("locality_name", "")))

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_kb = target.stat().st_size / 1024
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
