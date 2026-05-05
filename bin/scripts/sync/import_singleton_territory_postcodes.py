#!/usr/bin/env python3
"""Singleton-postcode UK overseas territories importer for issue #1039.

Source data
-----------
The following territories use a single fixed Royal Mail-style
postcode each, assigned by the British postal system:

    Country                    iso2  postcode     ship to
    Falkland Islands           FK    FIQQ 1ZZ
    South Georgia (S. Sand.)   GS    SIQQ 1ZZ
    BIOT (Diego Garcia, ...)   IO    BBND 1ZZ
    Pitcairn Islands           PN    PCRN 1ZZ
    Saint Helena (Island)      SH    STHL 1ZZ
    Ascension Island           SH    ASCN 1ZZ  (same SH country)
    Tristan da Cunha           SH    TDCU 1ZZ  (same SH country)
    Turks and Caicos Islands   TC    TKCA 1ZZ
    Nauru                      NR    NRU68

Source: Royal Mail / Wikipedia public references for each Crown
Dependency or Overseas Territory's postcode assignment.

What this script does
---------------------
Emits 7 contributions/postcodes/<iso2>.json files (SH gets all
three Atlantic Saint-Helena-overseas postcodes in one file).

State FK
--------
Country-only ship for all (these countries have either a single
state or no formal sub-state postcode mapping).

License & attribution
---------------------
Postcode assignments are public Royal Mail / national-post conventions;
no formal license required. Each row carries
``source: "wikipedia-singleton-territory"`` for export-time provenance.

Usage
-----
    python3 bin/scripts/sync/import_singleton_territory_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List


# iso2 -> list of (postcode, locality_name) tuples
TERRITORIES: Dict[str, List[tuple]] = {
    "FK": [("FIQQ 1ZZ", "Falkland Islands")],
    "GS": [("SIQQ 1ZZ", "South Georgia and the South Sandwich Islands")],
    "IO": [("BBND 1ZZ", "British Indian Ocean Territory")],
    "PN": [("PCRN 1ZZ", "Pitcairn Islands")],
    "SH": [
        ("STHL 1ZZ", "Saint Helena"),
        ("ASCN 1ZZ", "Ascension Island"),
        ("TDCU 1ZZ", "Tristan da Cunha"),
    ],
    "TC": [("TKCA 1ZZ", "Turks and Caicos Islands")],
    "NR": [("NRU68", "Nauru")],
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
        for code, locality in entries:
            if not regex.match(code):
                print(
                    f"  WARN: {iso2}/{code!r} fails regex {regex.pattern!r}",
                    file=sys.stderr,
                )
                continue
            record: Dict[str, object] = {
                "code": code,
                "country_id": int(country["id"]),
                "country_code": iso2,
                "locality_name": locality,
                "type": "full",
                "source": "wikipedia-singleton-territory",
            }
            records.append(record)

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
