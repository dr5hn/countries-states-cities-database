#!/usr/bin/env python3
"""Drop the legacy half of the 6 unambiguous duplicate pairs flagged by the
issue #1349 city remap.  Two ambiguous pairs (Sermide/Felonica and
Corteolona/Genzone) are intentionally left for maintainer review — neither
of their records carries the modern ISTAT-canonical merged name.

Mapping (id_to_drop -> reason):
  58976  'Pozzaglio'             -> kept 'Pozzaglio ed Uniti' (id 58977, ISTAT canonical, Q42226)
  139523 'Limite'                -> kept 'Capraia e Limite'   (id 136799, ISTAT canonical, Q82639)
  140714 'Napoli'                -> kept 'Naples'             (id 140713, English name = repo convention)
  139215 'Inverno'               -> kept 'Inverno e Monteleone' (id 139216, ISTAT canonical, Q39917)
  61530  'Trinità d\\'Agultu'    -> kept 'Trinità d\\'Agultu e Vignola' (id 61531, ISTAT canonical, Q341096)
  61329  'Torino'                -> kept 'Turin'              (id 61575, English name = repo convention)

Idempotent: re-running on already-deduplicated data produces 0 changes.

Usage:
    python3 bin/scripts/fixes/italy_dedup_flagged_pairs.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
CITIES_JSON = REPO_ROOT / "contributions/cities/IT.json"

# id -> (city name, kept-id, kept-name, reason)
DROP = {
    58976:  ("Pozzaglio",            58977,  "Pozzaglio ed Uniti",          "ISTAT canonical merged comune"),
    139523: ("Limite",                136799, "Capraia e Limite",            "ISTAT canonical merged comune"),
    140714: ("Napoli",                140713, "Naples",                      "Italian-name duplicate of English-named record"),
    139215: ("Inverno",               139216, "Inverno e Monteleone",        "ISTAT canonical merged comune"),
    61530:  ("Trinità d'Agultu",      61531,  "Trinità d'Agultu e Vignola",  "ISTAT canonical merged comune"),
    61329:  ("Torino",                61575,  "Turin",                       "Italian-name duplicate of English-named record"),
}


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    cities = json.loads(CITIES_JSON.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cities}

    # Verify preconditions: every drop target must exist with the expected name,
    # and every keep target must exist with the expected name.  Refuse to mutate
    # otherwise — these are irreversible deletions, no silent failures.
    errors: List[str] = []
    for drop_id, (drop_name, keep_id, keep_name, _) in DROP.items():
        d = by_id.get(drop_id)
        k = by_id.get(keep_id)
        if d is None:
            # Missing drop target = already deduped; treat as idempotent skip later.
            continue
        if d.get("name") != drop_name:
            errors.append(f"id={drop_id} expected name={drop_name!r}, found {d.get('name')!r}")
        if k is None:
            errors.append(f"keep target id={keep_id} (would-be parent of dropped id={drop_id}) is missing")
        elif k.get("name") != keep_name:
            errors.append(f"keep target id={keep_id} expected name={keep_name!r}, found {k.get('name')!r}")
    if errors:
        print("Preconditions failed; refusing to mutate IT.json:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    dropped: List[dict] = []
    skipped_already_gone: List[int] = []
    new_cities: List[dict] = []
    for c in cities:
        if c["id"] in DROP:
            dropped.append(
                {
                    "id": c["id"],
                    "name": c["name"],
                    "kept_id": DROP[c["id"]][1],
                    "kept_name": DROP[c["id"]][2],
                    "reason": DROP[c["id"]][3],
                }
            )
        else:
            new_cities.append(c)

    for drop_id in DROP:
        if drop_id not in by_id:
            skipped_already_gone.append(drop_id)

    print(f"Input cities:        {len(cities)}")
    print(f"Dropped this run:    {len(dropped)}")
    print(f"Already gone (idempotent skip): {len(skipped_already_gone)}")
    print(f"Output cities:       {len(new_cities)}")
    print()
    print("Drops:")
    for d in dropped:
        print(f"  id={d['id']:7} {d['name']!r:35} -> kept id={d['kept_id']} ({d['kept_name']!r}) [{d['reason']}]")

    if args.dry_run:
        print("\n--dry-run: IT.json not modified.")
        return 0

    if not dropped:
        print("\nNothing to drop; IT.json untouched.")
        return 0

    text = json.dumps(new_cities, ensure_ascii=False, indent=2)
    CITIES_JSON.write_text(text, encoding="utf-8")
    print(f"\nWrote {len(new_cities)} cities to {CITIES_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
