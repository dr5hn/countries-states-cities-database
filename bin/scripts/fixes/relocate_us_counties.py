#!/usr/bin/env python3
"""Phase 2a of issue #1303: relocate US counties out of the cities dataset.

Genuine county-level admin units (type ``county``/``parish``) were stored in
``contributions/cities/US.json``, polluting city queries. This moves them to a
new ``contributions/counties/US.json`` dataset so they are available
*separately* rather than mixed into cities.

What it does
------------
* Partitions ``cities/US.json`` into settlements (kept) and county/parish rows.
* Writes the county/parish rows to ``contributions/counties/US.json``, stripping
  the auto-managed fields (``id``/``created_at``/``updated_at``/``flag``) so the
  counties table assigns fresh ids on import. All geographic/translation data
  (name, native, translations, population, coords, timezone, wikiDataId, type)
  is preserved.
* Rewrites ``cities/US.json`` without those rows.

Idempotent: if no county/parish rows remain in cities, it reports and exits
without touching anything.

Usage
-----
    python3 bin/scripts/fixes/relocate_us_counties.py --dry-run
    python3 bin/scripts/fixes/relocate_us_counties.py
"""

import argparse
import json
import sys
from pathlib import Path

CITIES = Path("contributions/cities/US.json")
COUNTIES = Path("contributions/counties/US.json")
COUNTY_TYPES = {"county", "parish"}
AUTO_MANAGED = ("id", "created_at", "updated_at", "flag")


def strip_auto(record: dict) -> dict:
    """Return a copy of record without MySQL-auto-managed fields, order preserved."""
    return {k: v for k, v in record.items() if k not in AUTO_MANAGED}


def main() -> int:
    """Relocate (or preview) US county/parish rows from cities to counties."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args()

    if not CITIES.exists():
        print(f"ERROR: {CITIES} not found (run from repo root)", file=sys.stderr)
        return 1

    records = json.loads(CITIES.read_text(encoding="utf-8"))
    counties = [r for r in records if r.get("type") in COUNTY_TYPES]
    settlements = [r for r in records if r.get("type") not in COUNTY_TYPES]

    print(f"{CITIES}: {len(records)} rows -> {len(settlements)} settlements kept, "
          f"{len(counties)} county/parish to relocate")

    if not counties:
        print("Nothing to relocate (already done).")
        return 0

    counties_out = [strip_auto(r) for r in counties]

    if args.dry_run:
        print(f"Would write {len(counties_out)} rows to {COUNTIES}")
        print(f"Would rewrite {CITIES} with {len(settlements)} rows")
        print("\n(dry run — no changes written)")
        return 0

    COUNTIES.parent.mkdir(parents=True, exist_ok=True)
    COUNTIES.write_text(
        json.dumps(counties_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    CITIES.write_text(
        json.dumps(settlements, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {COUNTIES} ({len(counties_out)} rows)")
    print(f"Rewrote {CITIES} ({len(settlements)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
