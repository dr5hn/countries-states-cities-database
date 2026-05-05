#!/usr/bin/env python3
"""French Polynesia -> contributions/postcodes/PF.json importer for issue #1039.

Source data
-----------
French Polynesia uses 5-digit postcodes in the 987xx range, assigned
by Office des Postes et Télécommunications (OPT) and France's
La Poste. The codes are organised by archipelago:

    Range      Archipelago                Anchor code  Anchor city
    98700-29   Windward Islands           98714        Papeete (Tahiti)
    98730-49   Leeward Islands            98730        Uturoa (Raiatea)
    98741-49   Austral Islands*           98748        Mataura (Tubuai)
    98731-44   Marquesas Islands*         98742        Taiohae (Nuku Hiva)
    98750-99   Tuamotu-Gambier            98755        Rangiroa

    *overlapping ranges due to historical OPT block allocations

What this script ships
----------------------
A 5-record hand-curated list — one anchor postcode per CSC PF state
(archipelago / subdivision). Covers all 5 PF states with state FK.

Why a minimal hand-curated ship
-------------------------------
French Polynesia has approximately 80-100 active postcodes total,
but no clean public bulk source ships the per-island list. Datanova
laposte.fr API endpoints have moved, OPT.pf does not publish a CSV
export, and Wikipedia covers only the archipelago ranges.

Future: when a comprehensive PF dataset surfaces, this can be
overlaid via the idempotent merge contract.

License & attribution
---------------------
- Source: OPT (PF) / Wikipedia archipelago references
- Each row: ``source: "wikipedia-pf-archipelago-anchor"``

Usage
-----
    python3 bin/scripts/sync/import_french_polynesia_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# (postcode, locality_name, csc_iso2)
ANCHORS: List[Tuple[str, str, str]] = [
    ("98714", "Papeete (Tahiti)", "05"),       # Windward Islands
    ("98730", "Uturoa (Raiatea)", "02"),       # Leeward Islands
    ("98742", "Taiohae (Nuku Hiva)", "03"),    # Marquesas Islands
    ("98748", "Mataura (Tubuai)", "01"),       # Austral Islands
    ("98755", "Avatoru (Rangiroa)", "04"),     # Tuamotu-Gambier
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    pf_country = next((c for c in countries if c.get("iso2") == "PF"), None)
    if pf_country is None:
        print("ERROR: PF not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(pf_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    pf_states = [s for s in states if s.get("country_id") == pf_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in pf_states if s.get("iso2")
    }
    print(
        f"Country: French Polynesia (id={pf_country['id']}); "
        f"states indexed: {len(pf_states)}"
    )

    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for code, locality, iso2 in ANCHORS:
        if not regex.match(code):
            print(f"  WARN: {code!r} fails regex {regex.pattern!r}", file=sys.stderr)
            skipped_bad_regex += 1
            continue
        state = state_by_iso2.get(iso2)
        if state is None:
            print(f"  WARN: state iso2 {iso2!r} not found", file=sys.stderr)
            skipped_no_state += 1
            continue
        record: Dict[str, object] = {
            "code": code,
            "country_id": int(pf_country["id"]),
            "country_code": "PF",
            "state_id": int(state["id"]),
            "state_code": state.get("iso2"),
            "locality_name": locality,
            "type": "area",
            "source": "wikipedia-pf-archipelago-anchor",
        }
        records.append(record)
        matched_state += 1

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    print(f"  with state:          {matched_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PF.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        existing_seen = {
            (r["code"], (r.get("locality_name") or "").lower()) for r in existing
        }
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in existing_seen:
                merged.append(r)
                existing_seen.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = sorted(records, key=lambda r: (r["code"], r.get("locality_name", "")))

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_kb = target.stat().st_size / 1024
    print(
        f"\n[OK] Wrote {target.relative_to(project_root)} "
        f"({len(merged):,} rows, {size_kb:.1f} KB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
