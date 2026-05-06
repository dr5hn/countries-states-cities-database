#!/usr/bin/env python3
"""Fix 72 city rows tagged with foreign IANA timezones.

Issue #1085 close-out follow-up: VN/PS/UZ/ID rows whose timezone field
points to a neighbouring country's zone instead of the correct local zone.

Idempotent. Safe to re-run.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "contributions" / "cities"

PLAN = [
    {
        "file": "VN.json",
        "rule": "Asia/Bangkok -> Asia/Ho_Chi_Minh",
        "match": lambda r: r.get("timezone") == "Asia/Bangkok",
        "set_tz": "Asia/Ho_Chi_Minh",
    },
    {
        "file": "PS.json",
        "rule": "Asia/Jerusalem -> Asia/Hebron (all 6 rows are West Bank governates)",
        "match": lambda r: r.get("timezone") == "Asia/Jerusalem",
        "set_tz": "Asia/Hebron",
    },
    {
        "file": "UZ.json",
        "rule": "Asia/Bishkek -> Asia/Tashkent (Fergana Region rows)",
        "match": lambda r: r.get("timezone") == "Asia/Bishkek",
        "set_tz": "Asia/Tashkent",
    },
    {
        "file": "ID.json",
        "rule": "Asia/Ho_Chi_Minh -> Asia/Pontianak (Sambas, West Kalimantan)",
        "match": lambda r: r.get("timezone") == "Asia/Ho_Chi_Minh",
        "set_tz": "Asia/Pontianak",
    },
]


def apply(plan):
    path = ROOT / plan["file"]
    if not path.exists():
        sys.exit(f"missing: {path}")
    rows = json.loads(path.read_text())
    changed = 0
    for r in rows:
        if plan["match"](r) and r.get("timezone") != plan["set_tz"]:
            r["timezone"] = plan["set_tz"]
            changed += 1
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    return changed, len(rows)


def main():
    print("Foreign-timezone cleanup (issue #1085 follow-up)")
    print("=" * 60)
    total = 0
    for plan in PLAN:
        changed, n = apply(plan)
        total += changed
        print(f"  {plan['file']:>10}  {plan['rule']}")
        print(f"  {'':>10}  changed {changed} of {n} rows")
    print("=" * 60)
    print(f"Total rows fixed: {total}")


if __name__ == "__main__":
    main()
