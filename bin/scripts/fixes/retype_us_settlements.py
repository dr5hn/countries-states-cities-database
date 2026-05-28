#!/usr/bin/env python3
"""Phase 1 of issue #1303: retype mis-classified US settlements to 'city'.

Many genuine US settlements were imported with GeoNames admin-level types
instead of 'city':

* ``adm2`` — county-seat towns (Abbeville, Abilene, ...) — real places
* ``adm1`` — the 50 state capitals (Atlanta, Austin, Boston, ...)
* ``adm3`` — minor civil-division towns (NJ/RI/MA)
* ``cities`` — a plain typo of ``city``

All of these are real populated places, so this retypes them to ``city``.
It is a *type-only* change — no records are added, removed, or have any
other field touched — so it is fully reversible.

Out of scope (handled separately): ``county``/``parish`` (genuine admin
units, Phase 2 drop-or-relocate decision) and ``abandoned``/null types.

Idempotent. Run from the repo root.

Usage
-----
    python3 bin/scripts/fixes/retype_us_settlements.py --dry-run
    python3 bin/scripts/fixes/retype_us_settlements.py
"""

import argparse
import collections
import json
import sys
from pathlib import Path

FILE = Path("contributions/cities/US.json")
RETYPE_FROM = {"adm2", "adm1", "adm3", "cities"}
RETYPE_TO = "city"


def main() -> int:
    """Apply (or preview) the US settlement retype."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args()

    if not FILE.exists():
        print(f"ERROR: {FILE} not found (run from repo root)", file=sys.stderr)
        return 1

    records = json.loads(FILE.read_text(encoding="utf-8"))
    changed = collections.Counter()
    for r in records:
        if r.get("type") in RETYPE_FROM:
            changed[r["type"]] += 1
            r["type"] = RETYPE_TO

    total = sum(changed.values())
    print(f"{FILE}: {len(records)} rows, {total} retyped to '{RETYPE_TO}'")
    for t, n in changed.most_common():
        print(f"  {t} -> {RETYPE_TO}: {n}")

    if args.dry_run:
        print("\n(dry run — no changes written)")
        return 0

    FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
