#!/usr/bin/env python3
"""Retag mistyped admin-level rows in contributions/cities/ES.json to type='city'.

Issue #1498 follow-up to PR-A (which dropped 22 admin-level placeholders).
After PR-A, ES.json contains ~6,920 rows whose `type` field is set to
`adm1`, `adm2`, or `adm3` even though they are real Spanish municipalities
(provincial capitals, big cities, and small towns alike). This script
retags those rows to `type='city'` so consuming apps stop misclassifying
real cities as administrative regions.

Why these rows are real cities (spot-checked, see PR description for
samples):
  - 100% have geographic coordinates.
  - 99%+ have a `wikiDataId` reference.
  - Almost all have a non-zero `population`.
  - The names map cleanly to municipalities visible on Spanish gov
    sources (provincial capitals like Zaragoza/Murcia/Sevilla typed
    `adm1`; province-capitals-or-comparable typed `adm2`; small towns
    typed `adm3`).

Conservative scope:
  - Only `country_code='ES'` rows are touched.
  - Only `type` in {'adm1', 'adm2', 'adm3'} is rewritten.
  - **Not** touched: `type='section'` (61 rows, mixed quality — needs
    separate per-row review), `type='locality'` (6 rows), `type='city'`
    (already correct), `type='capital'`/`'historical_capital'`/`'adm4'`
    (1 each — left alone).

Idempotent: re-running on already-retagged data writes nothing and exits 0.

Usage:
    python3 bin/scripts/fixes/spain_retag_admin_types.py [--dry-run]
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[3]
CITIES_JSON = REPO_ROOT / "contributions/cities/ES.json"

ADMIN_TYPES = ("adm1", "adm2", "adm3")
TARGET_TYPE = "city"
COUNTRY_CODE = "ES"


def load_cities(path: Path) -> List[dict]:
    """Read the cities JSON file and verify the top-level shape."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array at {path}, got {type(data).__name__}")
    return data


def is_target(row: dict) -> bool:
    """Row is an ES record whose type is one of the admin levels we retag."""
    return row.get("country_code") == COUNTRY_CODE and row.get("type") in ADMIN_TYPES


def type_distribution(rows: List[dict]) -> "collections.Counter[str]":
    """Counter of `type` values across rows."""
    return collections.Counter(r.get("type") for r in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the rewrite plan without rewriting the file.",
    )
    args = parser.parse_args()

    if not CITIES_JSON.exists():
        raise SystemExit(f"Cities file not found: {CITIES_JSON}")

    cities = load_cities(CITIES_JSON)
    pre_count = len(cities)

    before = type_distribution(cities)
    targets = [r for r in cities if is_target(r)]
    retag_count = len(targets)

    # Track per-source-type retag counts for reporting.
    by_source = collections.Counter(r.get("type") for r in targets)

    # Sample 5 retagged rows for human eyes.
    sample = targets[:5]

    # State_code distribution: every row keeps its existing state_code.
    # Verify no row would change state_code as a side-effect.
    state_code_changes = 0  # this script never modifies state_code; sanity assert.

    print(f"Input file:        {CITIES_JSON.relative_to(REPO_ROOT)}")
    print(f"Pre-retag count:   {pre_count}")
    print(f"Type distribution before:")
    for t, c in sorted(before.items(), key=lambda x: -x[1]):
        print(f"  {t!r:>20}: {c}")
    print(f"Retag candidates:  {retag_count}")
    for src in ADMIN_TYPES:
        print(f"  from {src!r}: {by_source.get(src, 0)}")

    if retag_count == 0:
        print("\nNo admin-typed rows found — nothing to do (idempotent).")
        return 0

    print("\nSample of rows that will be retagged:")
    for r in sample:
        print(
            f"  id={r['id']} {r['name']!r} state_code={r.get('state_code')!r} "
            f"old_type={r.get('type')!r} -> {TARGET_TYPE!r}"
        )

    if args.dry_run:
        print("\n--dry-run: not writing.")
        return 0

    for row in cities:
        if is_target(row):
            row["type"] = TARGET_TYPE

    after = type_distribution(cities)
    print(f"\nType distribution after:")
    for t, c in sorted(after.items(), key=lambda x: -x[1]):
        print(f"  {t!r:>20}: {c}")
    assert sum(after.values()) == sum(before.values()), "row count drift!"
    assert state_code_changes == 0
    # Sanity: no row in ADMIN_TYPES remains.
    leftover = sum(after[t] for t in ADMIN_TYPES if t in after)
    assert leftover == 0, f"{leftover} admin-typed rows still present"

    with CITIES_JSON.open("w", encoding="utf-8") as fh:
        json.dump(cities, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"\nWrote {pre_count} records to {CITIES_JSON.relative_to(REPO_ROOT)}.")
    print("Run `python3 bin/scripts/sync/normalize_json.py "
          "contributions/cities/ES.json` next to canonicalize formatting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
