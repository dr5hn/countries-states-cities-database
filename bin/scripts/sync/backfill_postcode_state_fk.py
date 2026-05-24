#!/usr/bin/env python3
"""Backfill state_id on existing postcode imports via cities.json lookup.

Context
-------
Several historical postcode imports (SE/NL/ZA/RS/SI/GB/VN) shipped
with ``state_id`` and ``state_code`` set to ``null`` because the
upstream sources didn't carry administrative-region information —
only ``(postcode, locality_name)`` pairs.

Insight
-------
CSC's own ``contributions/cities/<iso2>.json`` already has a
``(city → state_id)`` mapping for every city in those countries.
Folding both names (NFKD + lowercase) and joining unambiguous
matches lets us recover state FKs for ~60-80% of postcode rows
without any new external data.

What this script does
---------------------
For each target country:

1. Loads ``contributions/cities/<iso2>.json``.
2. Builds an unambiguous ``fold(name) → (state_id, state_code)``
   map. Names that map to multiple states are dropped (postcode
   data alone can't disambiguate).
3. Loads ``contributions/postcodes/<iso2>.json``.
4. For each row whose ``state_id`` is null AND whose folded
   ``locality_name`` is in the lookup, populates ``state_id`` and
   ``state_code``.
5. Writes the file back.

Match rate is country-dependent. Per offline audit on master:

    NL: 2,463 / 4,072 (60%)
    SE: 13,162 / 16,392 (80%)
    ZA: 2,906 / 5,685 (51%)
    RS: 343 / 1,170 (29%)
    SI: 271 / 522 (51%)
    GB: 98 / 124 (79%)
    VN: 29 / 63 (46%)

Total expected backfill: ~19,272 records — strict improvement over
the ``null`` status quo.

Skipped countries
-----------------
- LV: source ships codes without locality_name (no field to match).
- MT: postcode "localities" are street names, not cities.
- MU/GR/KE/NP: localities are post-office names, low match rate.

Usage
-----
    python3 bin/scripts/sync/backfill_postcode_state_fk.py
    python3 bin/scripts/sync/backfill_postcode_state_fk.py --dry-run
    python3 bin/scripts/sync/backfill_postcode_state_fk.py --only NL
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple


TARGETS: Tuple[str, ...] = ("NL", "SE", "ZA", "RS", "SI", "GB", "VN")


def fold(s: Optional[str]) -> str:
    """Lowercase, strip diacritics, normalise whitespace for fuzzy matching."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def build_city_lookup(
    cities: List[dict],
) -> Tuple[Dict[str, Tuple[int, Optional[str]]], int]:
    """Build unambiguous ``fold(name) → (state_id, state_code)``.

    Names appearing in multiple distinct states are dropped — postcode
    data alone can't disambiguate. Returns the lookup and the count of
    dropped ambiguous names for telemetry.
    """
    out: Dict[str, Tuple[int, Optional[str]]] = {}
    ambiguous: set = set()
    for c in cities:
        name = fold(c.get("name"))
        if not name:
            continue
        sid = c.get("state_id")
        if sid is None:
            continue
        existing = out.get(name)
        if existing is not None and existing[0] != sid:
            ambiguous.add(name)
        else:
            out.setdefault(name, (sid, c.get("state_code")))
    for n in ambiguous:
        out.pop(n, None)
    return out, len(ambiguous)


def backfill_country(project_root: Path, iso2: str, dry_run: bool) -> int:
    """Backfill one country's postcodes file. Returns rows updated."""
    pc_path = project_root / f"contributions/postcodes/{iso2}.json"
    cs_path = project_root / f"contributions/cities/{iso2}.json"
    if not pc_path.exists() or not cs_path.exists():
        print(f"[{iso2}] skipped — missing postcodes or cities file")
        return 0

    cities = json.load(cs_path.open(encoding="utf-8"))
    rows = json.load(pc_path.open(encoding="utf-8"))
    lookup, n_ambig = build_city_lookup(cities)
    print(
        f"[{iso2}] cities={len(cities):,} unambiguous_lookup={len(lookup):,} "
        f"(dropped {n_ambig} ambiguous); postcodes={len(rows):,}"
    )

    updated = 0
    already = 0
    no_loc = 0
    no_match = 0
    for r in rows:
        if r.get("state_id"):
            already += 1
            continue
        loc = r.get("locality_name")
        if not loc:
            no_loc += 1
            continue
        hit = lookup.get(fold(loc))
        if hit is None:
            no_match += 1
            continue
        state_id, state_code = hit
        r["state_id"] = state_id
        r["state_code"] = state_code
        updated += 1

    pct = updated * 100 // max(1, len(rows))
    print(
        f"[{iso2}]   updated={updated:,} ({pct}%) "
        f"already_set={already} no_locality={no_loc} no_match={no_match}"
    )

    if updated and not dry_run:
        with pc_path.open("w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"[{iso2}]   wrote {pc_path.relative_to(project_root)}")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--only", default=None, help="comma-separated iso2 list (skip others)"
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    targets: Tuple[str, ...] = TARGETS
    if args.only:
        wanted = {x.strip().upper() for x in args.only.split(",") if x.strip()}
        targets = tuple(t for t in TARGETS if t in wanted)
        if not targets:
            print(f"ERROR: no overlap between --only={args.only!r} and {TARGETS}", file=sys.stderr)
            return 2

    grand_total = 0
    for iso2 in targets:
        grand_total += backfill_country(project_root, iso2, args.dry_run)
        print()
    mode = "(dry-run, no writes)" if args.dry_run else ""
    print(f"=== TOTAL state_id backfilled: {grand_total:,} {mode}".rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
