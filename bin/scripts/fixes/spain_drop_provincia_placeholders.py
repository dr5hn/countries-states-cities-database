#!/usr/bin/env python3
"""Drop admin-level placeholder rows from contributions/cities/ES.json.

Issue #1498. The reporter flagged that `GetCity(...)` returns province-level
admin entries inside Spanish city dropdowns ("Provincia de Madrid" etc.).
This is the city-level cleanup PR — drops 22 rows that are not real cities:

  - 21 "Provincia de X" / "Província de X" rows (ids 36362, 36364, 36365,
    36373, 36375, 36376, 36377, 36379, 36381, 36383, 36385, 36386, 36387,
    36389, 36390, 36391, 36392, 36393, 36394, 36396, 36400). All are admin
    placeholders that duplicate concepts already represented by entries in
    contributions/states/states.json. The 50 Spanish provinces are already
    states, so a separate "Provincia de X" pseudo-city is redundant.

  - 1 cross-state placeholder (id 32244, name "Alicante", state_code=V).
    The real Alicante city lives at id 152158 ("Alicante/Alacant",
    state_code=A) under the Alicante province (iso2=A). Row 32244 is a
    legacy stub from when Valencia community was the parent of three
    provinces (Valencia, Alicante, Castellon) — Alicante now has its own
    state, so the stub is wrong both in name (missing the Valencian
    endonym) and in parentage.

The 21 "Provincia ..." ids are an explicit allowlist rather than a name-
prefix filter, because two real Spanish municipalities also begin with
"Provincia" in obscure forms — using ids guarantees we touch only what we
mean to. The script verifies each id's current name still matches the
expected prefix before dropping, refusing to touch rows that don't.

Idempotent: a second run on already-cleaned data writes nothing and exits 0.

Usage:
    python3 bin/scripts/fixes/spain_drop_provincia_placeholders.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[3]
CITIES_JSON = REPO_ROOT / "contributions/cities/ES.json"

# 21 admin-placeholder ids, expected to start with "Provincia " or "Província ".
PROVINCIA_IDS = frozenset({
    36362, 36364, 36365, 36373, 36375, 36376, 36377, 36379, 36381, 36383,
    36385, 36386, 36387, 36389, 36390, 36391, 36392, 36393, 36394, 36396,
    36400,
})

# 1 cross-state placeholder. id, expected name, expected wrong state_code.
CROSS_STATE_ALICANTE_ID = 32244
CROSS_STATE_ALICANTE_NAME = "Alicante"
CROSS_STATE_ALICANTE_STATE_CODE = "V"

EXPECTED_DROP_COUNT = len(PROVINCIA_IDS) + 1  # 22
EXPECTED_PRE_COUNT = 8427
EXPECTED_POST_COUNT = EXPECTED_PRE_COUNT - EXPECTED_DROP_COUNT  # 8405


def load_cities(path: Path) -> List[dict]:
    """Read the cities JSON file and verify the top-level shape."""
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array at {path}, got {type(data).__name__}")
    return data


def matches_provincia(row: dict) -> bool:
    """Row is one of the 21 'Provincia ...' admin placeholders, name verified."""
    if row.get("id") not in PROVINCIA_IDS:
        return False
    name = row.get("name", "")
    return isinstance(name, str) and (
        name.startswith("Provincia ") or name.startswith("Província ")
    )


def matches_cross_state_alicante(row: dict) -> bool:
    """Row is the cross-state Alicante stub (id 32244, name 'Alicante', state V)."""
    return (
        row.get("id") == CROSS_STATE_ALICANTE_ID
        and row.get("name") == CROSS_STATE_ALICANTE_NAME
        and row.get("state_code") == CROSS_STATE_ALICANTE_STATE_CODE
    )


def is_target(row: dict) -> bool:
    """True if this row is on the drop list."""
    return matches_provincia(row) or matches_cross_state_alicante(row)


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

    to_drop = [row for row in cities if is_target(row)]
    kept = [row for row in cities if not is_target(row)]

    drop_count = len(to_drop)
    post_count = len(kept)

    # Defensive check: any row whose id is in our allowlist but whose name
    # doesn't match the expected pattern (could indicate the data has
    # shifted since this script was written).
    rows_by_id = {row.get("id"): row for row in cities}
    suspicious: List[dict] = []
    for pid in PROVINCIA_IDS:
        row = rows_by_id.get(pid)
        if row is not None and not matches_provincia(row):
            suspicious.append(row)
    cross = rows_by_id.get(CROSS_STATE_ALICANTE_ID)
    if cross is not None and not matches_cross_state_alicante(cross):
        suspicious.append(cross)

    print(f"Input file:          {CITIES_JSON.relative_to(REPO_ROOT)}")
    print(f"Pre-clean count:     {pre_count}")
    print(f"Provincia drops:     "
          f"{sum(1 for r in to_drop if matches_provincia(r))} / "
          f"{len(PROVINCIA_IDS)} expected")
    print(f"Cross-state Alicante drop: "
          f"{sum(1 for r in to_drop if matches_cross_state_alicante(r))} / 1 expected")
    print(f"Total drops:         {drop_count}")
    print(f"Post-clean count:    {post_count}")

    if suspicious:
        print(
            "\nERROR: target ids exist but do not match expected name/state — "
            "refusing to drop them:",
            file=sys.stderr,
        )
        for row in suspicious:
            print(
                f"  id={row.get('id')} name={row.get('name')!r} "
                f"state_code={row.get('state_code')!r}",
                file=sys.stderr,
            )
        return 2

    if drop_count == 0:
        print("\nNo placeholder rows found — nothing to do (idempotent).")
        return 0

    if drop_count != EXPECTED_DROP_COUNT or pre_count != EXPECTED_PRE_COUNT:
        print(
            f"\nWARNING: counts diverge from the expected baseline "
            f"({EXPECTED_PRE_COUNT} -> drop {EXPECTED_DROP_COUNT} -> "
            f"{EXPECTED_POST_COUNT}). Got {pre_count} -> drop {drop_count} "
            f"-> {post_count}. Review the diff before merging.",
            file=sys.stderr,
        )

    if args.dry_run:
        print("\n--dry-run: not writing.")
        for r in to_drop:
            print(f"  would drop id={r['id']} name={r['name']!r} "
                  f"state_code={r.get('state_code')!r} type={r.get('type')!r}")
        return 0

    with CITIES_JSON.open("w", encoding="utf-8") as fh:
        json.dump(kept, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"\nWrote {post_count} records to {CITIES_JSON.relative_to(REPO_ROOT)}.")
    print("Run `python3 bin/scripts/sync/normalize_json.py "
          "contributions/cities/ES.json` next to canonicalize formatting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
