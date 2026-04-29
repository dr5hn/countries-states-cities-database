#!/usr/bin/env python3
"""India Post -> contributions/postcodes/IN.json importer for issue #1039.

Source data
-----------
India Post publishes the canonical pincode-to-post-office mapping under the
National Data Sharing and Accessibility Policy (Open Government Data) at:

  https://data.gov.in/catalog/all-india-pincode-directory

The CSV (``all_india_PO_list_without_APS_offices_ver2_lat_long.csv``) has
columns:
  officename, pincode, officeType, Deliverystatus, divisionname, regionname,
  circlename, Taluk, Districtname, statename, Telephone, Related Suboffice,
  Related Headoffice, longitude, latitude

Approximately 155k post-office rows covering ~19,132 unique pincodes across
all 36 Indian states and union territories.

What this script does
---------------------
1. Reads the India Post CSV from a local path
2. Groups rows by pincode and selects ONE representative record per pincode
   (preferring Head Office > Sub Office > Branch Office)
3. Resolves country_id (always India = 101)
4. Resolves state_id by normalised name match against states.json
5. Writes contributions/postcodes/IN.json (~19,000 rows)
6. Preserves any existing curated entries (idempotent merge)

Why one record per pincode
--------------------------
Each pincode in India serves a defined geographic area, with one Head Office
acting as the canonical delivery point. Sub-offices and branch-offices share
the same pincode but represent finer-grained service points. The repo's
``postcodes`` table has one row per code, so we pick the canonical Head Office
record (or the largest available office tier) for each pincode.

License
-------
Source: data.gov.in (National Data Sharing and Accessibility Policy / OGD).
Each generated record sets ``source: "india-post"`` for attribution.

Usage
-----
    python3 bin/scripts/sync/import_india_post_postcodes.py \\
      --input /tmp/in_pincodes.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

# Office-type ranking: lower number = preferred canonical record per pincode
OFFICE_TYPE_RANK = {"H.O": 0, "S.O": 1, "B.O": 2}


def normalise_state_name(s: str) -> str:
    """Lowercase, normalise '&' → 'and', strip extra whitespace."""
    s = s.strip().lower().replace("&", "and")
    return re.sub(r"\s+", " ", s)


# Hand-crafted aliases for India-specific edge cases where the CSV's state name
# does not directly map to the canonical states.json record.
STATE_NAME_ALIASES: Dict[str, str] = {
    # Merged UTs (2020): DADRA & NAGAR HAVELI / DAMAN & DIU → combined record
    "dadra and nagar haveli": "dadra and nagar haveli and daman and diu",
    "daman and diu": "dadra and nagar haveli and daman and diu",
    # Common spelling/formatting differences
    "chattisgarh": "chhattisgarh",
    "orissa": "odisha",
    "pondicherry": "puducherry",
    "uttaranchal": "uttarakhand",
}


def build_state_lookup(states_for_in: List[dict]) -> Dict[str, dict]:
    """Build normalised-name -> state record map for India."""
    lookup: Dict[str, dict] = {}
    for s in states_for_in:
        for key in (s.get("name"), s.get("native")):
            if key:
                lookup[normalise_state_name(key)] = s
    return lookup


def resolve_state(
    csv_state: str,
    state_lookup: Dict[str, dict],
) -> Optional[dict]:
    """Return the matching state record, or None if no confident match."""
    raw = normalise_state_name(csv_state)
    if not raw:
        return None
    if raw in state_lookup:
        return state_lookup[raw]
    aliased = STATE_NAME_ALIASES.get(raw)
    if aliased and aliased in state_lookup:
        return state_lookup[aliased]
    return None


def parse_csv(csv_path: Path) -> Dict[str, dict]:
    """Read the India Post CSV and pick one representative per pincode."""
    by_pincode: Dict[str, dict] = {}
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pincode = (row.get("pincode") or "").strip()
            if not pincode or not pincode.isdigit() or len(pincode) != 6:
                continue
            office_type = (row.get("officeType") or "").strip()
            current_rank = OFFICE_TYPE_RANK.get(office_type, 99)
            existing = by_pincode.get(pincode)
            if existing is None or current_rank < existing["_rank"]:
                row["_rank"] = current_rank
                by_pincode[pincode] = row
    # Drop the helper field
    for row in by_pincode.values():
        row.pop("_rank", None)
    return by_pincode


def parse_coord(value: str) -> Optional[str]:
    """Parse 'NA' / blank / numeric strings to a clean coordinate or None."""
    if not value:
        return None
    v = value.strip()
    if v.upper() == "NA" or v == "":
        return None
    try:
        f = float(v)
        # Coordinates outside ±90 / ±180 are spurious
        if abs(f) > 180:
            return None
        # Format with up to 8 decimal places (matches schema decimal(11,8) / decimal(10,8))
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except ValueError:
        return None


def build_records(
    by_pincode: Dict[str, dict],
    country_id: int,
    state_lookup: Dict[str, dict],
) -> List[dict]:
    """Build postcode JSON records sorted deterministically by pincode."""
    records: List[dict] = []
    for pincode in sorted(by_pincode):
        row = by_pincode[pincode]
        state = resolve_state(row.get("statename") or "", state_lookup)

        record = {
            "code": pincode,
            "country_id": country_id,
            "country_code": "IN",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            if state.get("iso2"):
                record["state_code"] = state["iso2"]

        locality = (row.get("officename") or "").strip()
        # Strip trailing " H.O" / " S.O" / " B.O" markers from office names so the
        # locality reads as a place rather than a Post Office designation.
        locality = re.sub(r"\s+(?:H\.O|S\.O|B\.O)\.?$", "", locality, flags=re.I)
        if locality:
            record["locality_name"] = locality

        record["type"] = "full"

        lat = parse_coord(row.get("latitude") or "")
        lng = parse_coord(row.get("longitude") or "")
        if lat is not None and lng is not None:
            record["latitude"] = lat
            record["longitude"] = lng

        record["source"] = "india-post"
        records.append(record)
    return records


def merge_with_existing(project_root: Path, new_records: List[dict]) -> List[dict]:
    """Preserve any existing manual records by code; append new ones."""
    target = project_root / "contributions/postcodes/IN.json"
    if not target.exists():
        return sorted(new_records, key=lambda r: r["code"])

    with target.open(encoding="utf-8") as f:
        existing = json.load(f)

    by_code: Dict[str, dict] = {r["code"]: r for r in existing}
    for r in new_records:
        by_code.setdefault(r["code"], r)
    return sorted(by_code.values(), key=lambda r: r["code"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/in_pincodes.csv",
                        help="Path to India Post pincode CSV")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print summary; do not write files")
    args = parser.parse_args()

    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"ERROR: input CSV not found: {csv_path}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]

    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    in_country = next((c for c in countries if c.get("iso2") == "IN"), None)
    if in_country is None:
        print("ERROR: India not found in countries.json", file=sys.stderr)
        return 2

    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    in_states = [s for s in states if s.get("country_id") == in_country["id"]]
    state_lookup = build_state_lookup(in_states)

    print(f"Country: India (id={in_country['id']})")
    print(f"States indexed: {len(in_states)}")

    print(f"Parsing {csv_path}...")
    by_pincode = parse_csv(csv_path)
    print(f"Unique pincodes: {len(by_pincode):,}")

    records = build_records(by_pincode, int(in_country["id"]), state_lookup)
    with_state = sum(1 for r in records if "state_id" in r)
    with_coords = sum(1 for r in records if "latitude" in r)
    print(f"Records built:   {len(records):,}")
    print(f"  with state_id: {with_state:,} ({with_state*100//max(1,len(records))}%)")
    print(f"  with coords:   {with_coords:,} ({with_coords*100//max(1,len(records))}%)")

    # Surface any state names from the CSV that we failed to resolve, for triage
    unresolved: Dict[str, int] = defaultdict(int)
    for pincode, row in by_pincode.items():
        if resolve_state(row.get("statename") or "", state_lookup) is None:
            unresolved[(row.get("statename") or "").strip()] += 1
    if unresolved:
        print("\nUnresolved state names (sample):")
        for name, count in sorted(unresolved.items(), key=lambda x: -x[1])[:10]:
            print(f"  {count:>5}  {name!r}")

    if args.dry_run:
        print("\n--dry-run set; no files written.")
        return 0

    merged = merge_with_existing(project_root, records)
    target = project_root / "contributions/postcodes/IN.json"
    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} records, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
