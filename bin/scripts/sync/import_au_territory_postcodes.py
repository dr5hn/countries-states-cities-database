#!/usr/bin/env python3
"""AU-postcode territory importer for issue #1039.

Source data
-----------
The following Australian external territories use a single fixed
Australia Post 4-digit postcode each (already present in AU.json
under their nearest state):

    Country                              iso2  postcode   AU state
    Norfolk Island                       NF    2899       NSW
    Christmas Island                     CX    6798       WA
    Cocos (Keeling) Islands              CC    6799       WA

CSC represents these as their own countries (NF/CC/CX), so this
importer mirrors the codes into separate <iso2>.json files.

Source: Australia Post public postcode lookup, mirrored via the
already-shipped contributions/postcodes/AU.json (matthewproctor
mirror, CC-BY).

What this script does
---------------------
1. Reads existing AU.json filtered by code.
2. Writes contributions/postcodes/<iso2>.json with country_id remapped.
3. Country-only ship — these territories have no further sub-state
   subdivisions for postcodes.

License & attribution
---------------------
- Original source: Australia Post (CC-BY via matthewproctor mirror)
- Each row: ``source: "australia-post-via-matthewproctor"``

Usage
-----
    python3 bin/scripts/sync/import_au_territory_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# iso2 -> (postcode, locality_name, override_lat, override_lon)
# matthewproctor's AU mirror anchors postcode 2899 (Norfolk Island) to
# NSW mainland coordinates, which is geographically wrong (Norfolk Is.
# sits ~1,500 km NE of mainland Australia). We override with the
# canonical Norfolk Island centroid. CC/CX coordinates in AU.json are
# correct.
TERRITORIES: Dict[str, Tuple[str, str, str, str]] = {
    "NF": ("2899", "Norfolk Island", "-29.04080000", "167.95473500"),
    "CX": ("6798", "Christmas Island", "", ""),
    "CC": ("6799", "Cocos (Keeling) Islands", "", ""),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    countries_by_iso2 = {c["iso2"]: c for c in countries}

    au_path = project_root / "contributions/postcodes/AU.json"
    au_data = json.load(au_path.open(encoding="utf-8"))
    au_by_code = {r["code"]: r for r in au_data}

    written: List[str] = []
    for iso2, (code, locality, override_lat, override_lon) in TERRITORIES.items():
        country = countries_by_iso2.get(iso2)
        if country is None:
            print(f"WARN: {iso2} not in countries.json", file=sys.stderr)
            continue
        regex = re.compile(country.get("postal_code_regex") or ".*")
        if not regex.match(code):
            print(
                f"WARN: {iso2}/{code!r} fails regex {regex.pattern!r}",
                file=sys.stderr,
            )
            continue

        au_row = au_by_code.get(code)
        record: Dict[str, object] = {
            "code": code,
            "country_id": int(country["id"]),
            "country_code": iso2,
            "locality_name": locality,
        }
        if override_lat and override_lon:
            record["latitude"] = override_lat
            record["longitude"] = override_lon
        elif au_row:
            for field in ("latitude", "longitude"):
                v = au_row.get(field)
                if v is not None and v != "":
                    record[field] = v
        record["type"] = "full"
        record["source"] = "australia-post-via-matthewproctor"

        records = [record]

        if args.dry_run:
            print(f"  {iso2}: would write {len(records)} record(s)")
            continue

        target = project_root / f"contributions/postcodes/{iso2}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            with target.open(encoding="utf-8") as f:
                existing = json.load(f)
            existing_seen = {
                (r["code"], (r.get("locality_name") or "").lower())
                for r in existing
            }
            merged = list(existing)
            for r in records:
                key = (r["code"], (r.get("locality_name") or "").lower())
                if key not in existing_seen:
                    merged.append(r)
                    existing_seen.add(key)
            merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
        else:
            merged = sorted(
                records, key=lambda r: (r["code"], r.get("locality_name", ""))
            )

        with target.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
            f.write("\n")
        size_kb = target.stat().st_size / 1024
        print(
            f"  [OK] {target.relative_to(project_root)} "
            f"({len(merged)} record(s), {size_kb:.1f} KB)"
        )
        written.append(iso2)

    print(f"\nShipped: {len(written)} territories: {', '.join(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
