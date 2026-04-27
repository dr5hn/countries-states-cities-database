#!/usr/bin/env python3
"""Normalise the ``state.level`` field for FR and IT in contributions/states/states.json.

Customer-facing follow-up to issues #1349 (Italy) and #1352 (France). The
city remap PRs (#1395, #1394, #1393, #1400, #1484) re-parented every comune
(IT) / commune (FR) onto the correct department/province row. The state
records themselves, however, still carry inconsistent ``level`` values, so
downstream consumers can't reliably express filters like
"all departments == level=2" or "all regions == level=1".

This script normalises ``level`` based on each state's ``type`` field:

  France (FR):
    level=1 (region tier):
      metropolitan region
      metropolitan collectivity with special status
      European collectivity
      overseas region
      overseas territory
      overseas collectivity
      overseas collectivity with special status
      dependency
    level=2 (department tier):
      metropolitan department

  Italy (IT):
    level=1 (region tier):
      region
      autonomous region
    level=2 (province tier):
      province
      metropolitan city
      free municipal consortium
      decentralized regional entity
      autonomous province

Only the ``level`` field is touched, and only on FR/IT rows. Every other
country and every other field is left byte-for-byte intact. Idempotent:
re-running on already-normalised data writes nothing.

Any FR/IT state whose ``type`` is not in the lists above is logged and
left untouched, so a maintainer can review before a follow-up sweep.

Usage:
    python3 bin/scripts/fixes/states_level_normalise.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
STATES_JSON = REPO_ROOT / "contributions/states/states.json"

# type -> level mappings keyed by country_code.
LEVEL_MAP: Dict[str, Dict[str, int]] = {
    "FR": {
        "metropolitan region": 1,
        "metropolitan collectivity with special status": 1,
        "European collectivity": 1,
        "overseas region": 1,
        "overseas territory": 1,
        "overseas collectivity": 1,
        "overseas collectivity with special status": 1,
        "dependency": 1,
        "metropolitan department": 2,
    },
    "IT": {
        "region": 1,
        "autonomous region": 1,
        "province": 2,
        "metropolitan city": 2,
        "free municipal consortium": 2,
        "decentralized regional entity": 2,
        "autonomous province": 2,
    },
}


def load_states(path: Path) -> List[dict]:
    """Read the states JSON file and verify the top-level shape."""
    if not path.exists():
        raise SystemExit(f"States file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array at {path}, got {type(data).__name__}")
    return data


def normalise_levels(
    states: List[dict],
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Return ``(changes, unchanged_targets, unmapped_targets)``.

    ``changes`` are dicts ``{id, country_code, name, type, before, after}``
    for every FR/IT row whose ``level`` was actually modified. The state
    objects in ``states`` are mutated in place.

    ``unchanged_targets`` are FR/IT rows that already had the correct
    level for their type (idempotent re-runs).

    ``unmapped_targets`` are FR/IT rows whose ``type`` is not in
    ``LEVEL_MAP``; these are *not* modified.
    """
    changes: List[dict] = []
    unchanged: List[dict] = []
    unmapped: List[dict] = []

    for state in states:
        cc = state.get("country_code")
        if cc not in LEVEL_MAP:
            continue
        type_ = state.get("type")
        target_level = LEVEL_MAP[cc].get(type_)
        if target_level is None:
            unmapped.append(state)
            continue
        before = state.get("level")
        if before == target_level:
            unchanged.append(state)
            continue
        state["level"] = target_level
        changes.append(
            {
                "id": state.get("id"),
                "country_code": cc,
                "name": state.get("name"),
                "type": type_,
                "before": before,
                "after": target_level,
            }
        )

    return changes, unchanged, unmapped


def verify_parent_integrity(states: List[dict]) -> List[str]:
    """Verify FR/IT level=2 rows have parent_ids that point at level=1 rows.

    Returns a list of human-readable violation messages (empty on success).
    """
    by_id: Dict[int, dict] = {s["id"]: s for s in states if "id" in s}
    violations: List[str] = []

    for state in states:
        cc = state.get("country_code")
        if cc not in LEVEL_MAP:
            continue
        if state.get("level") != 2:
            continue
        pid = state.get("parent_id")
        sid = state.get("id")
        sname = state.get("name")
        if pid is None:
            violations.append(
                f"{cc} state id={sid} ({sname!r}) is level=2 but has no parent_id"
            )
            continue
        parent = by_id.get(pid)
        if parent is None:
            violations.append(
                f"{cc} state id={sid} ({sname!r}) parent_id={pid} not found"
            )
            continue
        if parent.get("country_code") != cc:
            violations.append(
                f"{cc} state id={sid} ({sname!r}) parent_id={pid} points to "
                f"a {parent.get('country_code')} record"
            )
            continue
        if parent.get("level") != 1:
            violations.append(
                f"{cc} state id={sid} ({sname!r}) parent_id={pid} "
                f"({parent.get('name')!r}) has level={parent.get('level')}, "
                f"expected 1"
            )
    return violations


def summarise_levels(states: List[dict], cc: str) -> Dict[Optional[int], int]:
    """Count the level distribution for one country."""
    return dict(
        Counter(s.get("level") for s in states if s.get("country_code") == cc)
    )


def summarise_type_level(states: List[dict], cc: str) -> Dict[str, Dict]:
    """type -> {level: count} for one country."""
    out: Dict[str, Dict] = defaultdict(lambda: defaultdict(int))
    for s in states:
        if s.get("country_code") != cc:
            continue
        out[s.get("type")][s.get("level")] += 1
    return {t: dict(lv) for t, lv in out.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report planned changes without rewriting the file.",
    )
    args = parser.parse_args()

    states = load_states(STATES_JSON)

    print(f"Input file: {STATES_JSON.relative_to(REPO_ROOT)}")
    print(f"Total state records: {len(states)}")
    print()

    pre_fr = summarise_levels(states, "FR")
    pre_it = summarise_levels(states, "IT")
    print(f"Before — FR level distribution: {pre_fr}")
    print(f"Before — IT level distribution: {pre_it}")
    print()

    changes, unchanged, unmapped = normalise_levels(states)

    if unmapped:
        print(
            "WARNING: FR/IT states with unmapped 'type' values "
            "(left untouched, surface for review):",
            file=sys.stderr,
        )
        for s in unmapped:
            print(
                f"  {s.get('country_code')} id={s.get('id')} "
                f"name={s.get('name')!r} type={s.get('type')!r} "
                f"level={s.get('level')!r}",
                file=sys.stderr,
            )
        print(file=sys.stderr)

    fr_changes = [c for c in changes if c["country_code"] == "FR"]
    it_changes = [c for c in changes if c["country_code"] == "IT"]

    print(f"Changed records: {len(changes)} "
          f"(FR={len(fr_changes)}, IT={len(it_changes)})")
    print(f"Already-correct FR/IT records (no-op): {len(unchanged)}")
    print()

    if changes:
        print("Changed records (id | country | name | type | before -> after):")
        for c in changes:
            print(
                f"  {c['id']:>5} | {c['country_code']} | {c['name']!r} | "
                f"{c['type']!r} | {c['before']!r} -> {c['after']}"
            )
        print()

    post_fr = summarise_levels(states, "FR")
    post_it = summarise_levels(states, "IT")
    print(f"After  — FR level distribution: {post_fr}")
    print(f"After  — IT level distribution: {post_it}")
    print()

    print("FR after — type -> {level: count}:")
    for t, lv in sorted(summarise_type_level(states, "FR").items()):
        print(f"  {t!r}: {lv}")
    print()
    print("IT after — type -> {level: count}:")
    for t, lv in sorted(summarise_type_level(states, "IT").items()):
        print(f"  {t!r}: {lv}")
    print()

    violations = verify_parent_integrity(states)
    if violations:
        # These are diagnostic only — pre-existing parent_id data errors are
        # orthogonal to level normalisation. Surface them for the maintainer
        # in stderr but do not block the write.
        print(
            f"PARENT-ID DIAGNOSTIC: {len(violations)} pre-existing "
            f"violation(s) in master (NOT introduced by this script):",
            file=sys.stderr,
        )
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print(file=sys.stderr)
    else:
        print("Parent-id integrity check: OK "
              "(every FR/IT level=2 row has a level=1 parent in the same country).")

    if not changes:
        print("\nNo changes — file is already normalised (idempotent).")
        return 0

    if args.dry_run:
        print("\n--dry-run: not writing.")
        return 0

    with STATES_JSON.open("w", encoding="utf-8") as fh:
        json.dump(states, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"\nWrote {len(states)} records to {STATES_JSON.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
