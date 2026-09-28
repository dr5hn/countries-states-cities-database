#!/usr/bin/env python3
"""Phase 2a of issue #1303: relocate US counties out of the cities dataset.

Genuine county-level admin units (type ``county``/``parish``) were stored in
``contributions/cities/US.json``, polluting city queries. This moves them to a
new ``contributions/counties/US.json`` dataset so they are available
*separately* rather than mixed into cities.

What it does
------------
* Partitions ``cities/US.json`` into settlements (kept) and county-level rows:
  type ``county``/``parish``, plus Alaska's county-equivalents, which were
  stored with type ``city`` and so were missed by the first run — boroughs and
  census areas. A consolidated city-borough ("X City and Borough", "City and
  Borough of X", "X Municipality") only moves when the city also has its own
  row; otherwise it is the city's only record and stays a city.
* Appends the county-level rows to ``contributions/counties/US.json`` (existing
  rows are kept), stripping the auto-managed fields
  (``id``/``created_at``/``updated_at``/``flag``) so the counties table assigns
  fresh ids on import. Alaska rows get type ``borough`` or ``census area``.
  All other geographic/translation data is preserved.
* Rewrites ``cities/US.json`` without those rows. Each file keeps its existing
  trailing-newline style, so only the moved rows show in the diff.

Idempotent: if no county-level rows remain in cities, it reports and exits
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


def consolidated_city(name: str):
    """Return the city name inside a consolidated-government name, else None.

    Matches "X City and Borough", "City and Borough of X" and "X Municipality".
    """
    if name.endswith(" City and Borough"):
        return name[: -len(" City and Borough")]
    if name.startswith("City and Borough of "):
        return name[len("City and Borough of "):]
    if name.endswith(" Municipality"):
        return name[: -len(" Municipality")]
    return None


def alaska_county_type(record: dict, ak_names: set, qid_counts: dict):
    """Return the counties `type` for an Alaska county-equivalent stored in cities, else None.

    Census areas and boroughs always qualify. A consolidated city-borough qualifies only when the
    city also has its own row (same name or same wikiDataId); if it is the city's only row it stays a
    city, matching how consolidated city-counties such as San Francisco and Denver are kept.
    """
    name = record.get("name", "")
    if record.get("state_code") != "AK":
        return None
    if name.endswith(" Census Area"):
        return "census area"
    city = consolidated_city(name)
    if city is not None:
        has_own_row = city in ak_names or qid_counts.get(record.get("wikiDataId"), 0) > 1
        return "borough" if has_own_row else None
    if name.endswith(" Borough"):
        return "borough"
    return None


def is_county_level(record: dict, ak_names: set, qid_counts: dict) -> bool:
    """True when a cities row is a county-level unit that belongs in the counties dataset."""
    return record.get("type") in COUNTY_TYPES or alaska_county_type(record, ak_names, qid_counts) is not None


def write_json(path: Path, rows: list, trailing_newline: bool) -> None:
    """Write rows as 2-space JSON, keeping the file's existing trailing-newline style."""
    text = json.dumps(rows, ensure_ascii=False, indent=2)
    path.write_text(text + ("\n" if trailing_newline else ""), encoding="utf-8")


def main() -> int:
    """Relocate (or preview) US county/parish rows from cities to counties."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args()

    if not CITIES.exists():
        print(f"ERROR: {CITIES} not found (run from repo root)", file=sys.stderr)
        return 1

    cities_text = CITIES.read_text(encoding="utf-8")
    records = json.loads(cities_text)
    qid_counts = {}
    for r in records:
        if r.get("wikiDataId"):
            qid_counts[r["wikiDataId"]] = qid_counts.get(r["wikiDataId"], 0) + 1
    ak_names = {r.get("name") for r in records if r.get("state_code") == "AK"}
    counties = [r for r in records if is_county_level(r, ak_names, qid_counts)]
    settlements = [r for r in records if not is_county_level(r, ak_names, qid_counts)]

    print(f"{CITIES}: {len(records)} rows -> {len(settlements)} settlements kept, "
          f"{len(counties)} county-level rows to relocate")

    if not counties:
        print("Nothing to relocate (already done).")
        return 0

    existing, counties_newline = [], True
    if COUNTIES.exists():
        counties_text = COUNTIES.read_text(encoding="utf-8")
        existing, counties_newline = json.loads(counties_text), counties_text.endswith("\n")
    seen = {(r.get("state_code"), r.get("name")) for r in existing}

    counties_out = []
    for r in counties:
        row = strip_auto(r)
        ak_type = alaska_county_type(r, ak_names, qid_counts)
        if ak_type:
            row["type"] = ak_type
        if (row.get("state_code"), row.get("name")) in seen:
            print(f"  skip (already in counties): {row['name']} ({row['state_code']})")
            continue
        counties_out.append(row)

    if args.dry_run:
        for row in counties_out:
            print(f"  would move: {row['name']} ({row['state_code']}) type={row.get('type')}")
        print(f"Would append {len(counties_out)} rows to {COUNTIES} ({len(existing)} existing kept)")
        print(f"Would rewrite {CITIES} with {len(settlements)} rows")
        print("\n(dry run — no changes written)")
        return 0

    COUNTIES.parent.mkdir(parents=True, exist_ok=True)
    write_json(COUNTIES, existing + counties_out, counties_newline)
    write_json(CITIES, settlements, cities_text.endswith("\n"))
    print(f"\nAppended {len(counties_out)} rows to {COUNTIES} ({len(existing) + len(counties_out)} total)")
    print(f"Rewrote {CITIES} ({len(settlements)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
