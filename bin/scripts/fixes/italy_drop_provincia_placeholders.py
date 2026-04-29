#!/usr/bin/env python3
"""Drop placeholder "Provincia ..." rows from contributions/cities/IT.json.

Issue #1349 follow-up. The reporter flagged entries like "Provincia di Lucca"
that "don't have sense to exist" — they are not comuni, they are leftover
province-level placeholder records from the pre-#1395 schema (cities used
to point at regions, so a separate "Provincia di X" pseudo-city stood in
for the province). Since #1395 (`italy_remap_cities.py`) re-parented every
real comune onto its province via `state_id` / `state_code`, these 87
placeholder rows are now duplicate concepts and should be removed.

Selection (defensive — both predicates must hold):
  - id in the contiguous range [59104, 59190] (87 records, no gaps).
  - name starts with "Provincia " (covers "Provincia di X",
    "Provincia autonoma di Trento", "Provincia dell' Aquila",
    "Provincia Verbano-Cusio-Ossola").

The script preserves every other record byte-for-byte; canonical
re-formatting is delegated to `bin/scripts/sync/normalize_json.py`.

Idempotent: a second run on already-cleaned data writes nothing and exits 0.

Usage:
    python3 bin/scripts/fixes/italy_drop_provincia_placeholders.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[3]
CITIES_JSON = REPO_ROOT / "contributions/cities/IT.json"

ID_MIN = 59104
ID_MAX = 59190
NAME_PREFIX = "Provincia "
EXPECTED_DROP_COUNT = 87
EXPECTED_PRE_COUNT = 9947
EXPECTED_POST_COUNT = EXPECTED_PRE_COUNT - EXPECTED_DROP_COUNT  # 9860


def load_cities(path: Path) -> List[dict]:
    """Read the cities JSON file and verify the top-level shape."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array at {path}, got {type(data).__name__}")
    return data


def is_placeholder(row: dict) -> bool:
    """Return True if the row is a legacy 'Provincia ...' placeholder."""
    rid = row.get("id")
    name = row.get("name", "")
    return (
        isinstance(rid, int)
        and ID_MIN <= rid <= ID_MAX
        and isinstance(name, str)
        and name.startswith(NAME_PREFIX)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be dropped without rewriting the file.",
    )
    args = parser.parse_args()

    if not CITIES_JSON.exists():
        raise SystemExit(f"Cities file not found: {CITIES_JSON}")

    cities = load_cities(CITIES_JSON)
    pre_count = len(cities)

    to_drop = [row for row in cities if is_placeholder(row)]
    kept = [row for row in cities if not is_placeholder(row)]

    drop_count = len(to_drop)
    post_count = len(kept)

    # Cross-check that nothing else in the id range slipped in.
    in_range = [row for row in cities if isinstance(row.get("id"), int)
                and ID_MIN <= row["id"] <= ID_MAX]
    non_placeholder_in_range = [row for row in in_range if not is_placeholder(row)]

    print(f"Input file:          {CITIES_JSON.relative_to(REPO_ROOT)}")
    print(f"Pre-clean count:     {pre_count}")
    print(f"Rows in id range:    {len(in_range)} (ids {ID_MIN}-{ID_MAX})")
    print(f"Placeholder matches: {drop_count}")
    print(f"Post-clean count:    {post_count}")

    if non_placeholder_in_range:
        print("\nERROR: rows in the placeholder id range that don't match "
              "the name prefix — refusing to touch them:", file=sys.stderr)
        for row in non_placeholder_in_range:
            print(f"  id={row.get('id')} name={row.get('name')!r}", file=sys.stderr)
        return 2

    if drop_count == 0:
        print("\nNo placeholder rows found — nothing to do (idempotent).")
        return 0

    if drop_count != EXPECTED_DROP_COUNT or pre_count != EXPECTED_PRE_COUNT:
        print(
            f"\nWARNING: counts diverge from the expected baseline "
            f"({EXPECTED_PRE_COUNT} → drop {EXPECTED_DROP_COUNT} → "
            f"{EXPECTED_POST_COUNT}). Got {pre_count} → drop {drop_count} "
            f"→ {post_count}. Review the diff before merging.",
            file=sys.stderr,
        )

    if args.dry_run:
        print("\n--dry-run: not writing.")
        sample = ", ".join(repr(r["name"]) for r in to_drop[:3])
        print(f"Sample drops: {sample}, ...")
        return 0

    with CITIES_JSON.open("w", encoding="utf-8") as fh:
        json.dump(kept, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"\nWrote {post_count} records to {CITIES_JSON.relative_to(REPO_ROOT)}.")
    print("Run `python3 bin/scripts/sync/normalize_json.py "
          "contributions/cities/IT.json` next to canonicalize formatting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
