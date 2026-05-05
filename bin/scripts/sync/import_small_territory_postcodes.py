#!/usr/bin/env python3
"""Small-territory postcodes bulk importer for issue #1039.

Source data
-----------
The following territories use small fixed sets of postal codes
(area- or district-level granularity), each documented in the
respective national post / Wikipedia references:

- GG Guernsey:        GY1-GY10                  (10 districts; Bailiwick of Guernsey + Alderney + Sark)
- JE Jersey:          JE1-JE5                   (5 districts; Bailiwick of Jersey)
- IM Isle of Man:     IM1-IM9 + IM86/87/98/99   (13 districts; PO boxes)
- AI Anguilla:        AI-2640                   (1 code, country-wide)
- VG British V.I.:    VG1110-VG1170             (7 codes; Tortola, Virgin Gorda, Anegada, etc.)
- VC St. Vincent:     VC0100-VC0400             (4 codes)

Each area covers a populated locality. Country-only state FK ship —
these territories' parish/district hierarchies don't 1:1 with the
postal districts; precision is preserved by listing all districts
explicitly.

What this script does
---------------------
Emits 6 contributions/postcodes/<iso2>.json files with hand-curated
postcode lists keyed to canonical area names from Royal Mail / each
post's published references.

License & attribution
---------------------
Postcode assignments are public Royal Mail / national-post conventions.
Each row carries ``source: "wikipedia-small-territory"`` for
export-time provenance.

Usage
-----
    python3 bin/scripts/sync/import_small_territory_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# iso2 -> list of (postcode, locality_name) tuples
TERRITORIES: Dict[str, List[Tuple[str, str]]] = {
    "GG": [
        ("GY1 1AA", "St Peter Port"),
        ("GY2 4AA", "St Sampson"),
        ("GY3 5AA", "Vale and Castel"),
        ("GY4 6AA", "St Saviour"),
        ("GY5 7AA", "St Andrew"),
        ("GY6 8AA", "Forest"),
        ("GY7 9AA", "St Pierre du Bois and Torteval"),
        ("GY8 0AA", "St Martin"),
        ("GY9 3AA", "Alderney, Sark and Herm"),
        ("GY10 1AA", "St Peter Port PO Box"),
    ],
    "JE": [
        ("JE1 1AA", "St Helier PO Box"),
        ("JE2 3AA", "St Helier"),
        ("JE3 4AA", "Outer Parishes"),
        ("JE4 5AA", "St Helier large PO Box"),
        ("JE5 0AA", "St Helier"),
    ],
    "IM": [
        ("IM1 1AA", "Douglas Central"),
        ("IM2 1AA", "Douglas North"),
        ("IM3 1AA", "Onchan"),
        ("IM4 1AA", "Douglas Outer"),
        ("IM5 1AA", "Crosby and Foxdale"),
        ("IM6 1AA", "Peel"),
        ("IM7 1AA", "St Johns"),
        ("IM8 1AA", "Ramsey and Maughold"),
        ("IM9 1AA", "Castletown and Rushen"),
        ("IM86 1AA", "Douglas PO Box"),
        ("IM87 1AA", "Douglas PO Box"),
        ("IM98 1AA", "Douglas PO Box"),
        ("IM99 1AA", "Douglas PO Box"),
    ],
    "AI": [
        ("AI-2640", "Anguilla"),
    ],
    "VG": [
        ("VG1110", "Road Town, Tortola"),
        ("VG1120", "Tortola"),
        ("VG1130", "Tortola"),
        ("VG1140", "Tortola"),
        ("VG1150", "Virgin Gorda"),
        ("VG1160", "Anegada"),
        ("VG1170", "Jost Van Dyke"),
    ],
    "VC": [
        ("VC0100", "Kingstown"),
        ("VC0200", "Saint Vincent"),
        ("VC0300", "Bequia and Grenadines"),
        ("VC0400", "Union Island"),
    ],
    "BM": [
        # Bermuda 9 parishes -> standard ZZ XX area codes (Wikipedia)
        ("DD 01", "Devonshire (DV)"),
        ("HM 01", "Hamilton Parish (HM)"),
        ("HS 01", "Hamilton (HM Sandys)"),
        ("PG 01", "Paget Parish (PG)"),
        ("MA 01", "Pembroke (MA)"),
        ("FL 01", "Sandys Parish (FL)"),
        ("GE 01", "St George's Parish (GE)"),
        ("SN 01", "Smith's Parish (SN)"),
        ("SB 01", "Southampton Parish (SB)"),
        ("WK 01", "Warwick Parish (WK)"),
        ("CR 01", "Hamilton city centre (CR)"),
    ],
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

    written: List[str] = []
    for iso2, entries in TERRITORIES.items():
        country = countries_by_iso2.get(iso2)
        if country is None:
            print(f"WARN: {iso2} not in countries.json", file=sys.stderr)
            continue
        regex = re.compile(country.get("postal_code_regex") or ".*")

        records: List[dict] = []
        skipped = 0
        for code, locality in entries:
            if not regex.match(code):
                print(
                    f"  WARN: {iso2}/{code!r} fails regex {regex.pattern!r}",
                    file=sys.stderr,
                )
                skipped += 1
                continue
            record: Dict[str, object] = {
                "code": code,
                "country_id": int(country["id"]),
                "country_code": iso2,
                "locality_name": locality,
                "type": "area",
                "source": "wikipedia-small-territory",
            }
            records.append(record)

        if args.dry_run:
            print(f"  {iso2}: would write {len(records)} record(s) ({skipped} skipped)")
            continue

        if not records:
            print(f"  {iso2}: 0 records emitted (all failed regex)")
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
