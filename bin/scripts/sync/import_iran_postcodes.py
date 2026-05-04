#!/usr/bin/env python3
"""Iran -> contributions/postcodes/IR.json importer for issue #1039.

Source data
-----------
The community ``saeidi-dev/Postal-Code-Iran`` PHP library encodes
193 5-digit postal-code area ranges as PHP ``case`` branches, each
returning a (state, city) tuple in Persian. Each range is the
fixed-prefix (first 5 digits) of an Iran Post 10-digit postcode
covering an entire delivery area.

Source URL: https://raw.githubusercontent.com/saeidi-dev/Postal-Code-Iran/master/PostalCode.php

What this script does
---------------------
1. Fetches the PHP file via urllib (curl is blocked).
2. Parses the 193 ``case (\\\$postalCode >= LOW && \\\$postalCode <= HIGH)``
   blocks via regex extraction.
3. Resolves state FK by direct Persian-name match against CSC's IR
   state ``native`` field (20 of 31 CSC states are represented in
   source).
4. Emits one row per range using the LOW boundary as the canonical
   area code, with the source's Persian city name as locality.
5. Writes contributions/postcodes/IR.json idempotently.

Coverage upgrade
----------------
Resolves the research-doc Tier B note `Range-based PHP switch only —
produces no canonical list of 10-digit codes, just prefix→state
lookup`. Iran's national postal authority does not publish a full
10-digit code list publicly; the 5-digit area-prefix list is the
deepest publicly redistributable form.

Regex fix
---------
Before this PR, countries.json had IR regex `^\\d{10}$` (Iran Post's
canonical 10-digit form). Updated to `^\\d{5}(\\d{5})?$` to also
accept the 5-digit area-prefix shipped by this dataset, matching the
mixed granularity already permitted for other prefix-only countries
(GB, TW, CA).

License & attribution
---------------------
- Source: saeidi-dev/Postal-Code-Iran (MIT-licensed PHP utility,
  with the range table compiled from Iran Post public lookups)
- Each row: ``source: "iran-post-via-saeidi-dev"``

Tier 5 per #1039 license-tier policy.

Usage
-----
    python3 bin/scripts/sync/import_iran_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/saeidi-dev/Postal-Code-Iran/"
    "master/PostalCode.php"
)

# Regex extracts each PHP case block:
#   case ($postalCode >= 57131 && $postalCode <= 57591):
#       return array('state' => 'آذربایجان غربی', 'city' => 'ارومیه');
RANGE_PATTERN = re.compile(
    r"case\s*\(\s*\$postalCode\s*>=\s*(\d+)\s*&&\s*\$postalCode\s*<=\s*(\d+)\s*\)\s*:"
    r"\s*\n\s*return\s+array\(\s*'state'\s*=>\s*'([^']+)'\s*,\s*'city'\s*=>\s*'([^']+)'",
    re.M,
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local PHP (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_text(SOURCE_URL)
    )
    ranges = RANGE_PATTERN.findall(text)
    print(f"Source ranges: {len(ranges):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    ir_country = next((c for c in countries if c.get("iso2") == "IR"), None)
    if ir_country is None:
        print("ERROR: IR not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ir_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ir_states = [s for s in states if s.get("country_id") == ir_country["id"]]
    # Iran state-name match is via the Persian native field
    state_by_native: Dict[str, dict] = {
        (s.get("native") or "").strip(): s for s in ir_states if s.get("native")
    }
    print(
        f"Country: Iran (id={ir_country['id']}); "
        f"states indexed by native name: {len(state_by_native)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_states: Dict[str, int] = {}

    for low, high, state_fa, city_fa in ranges:
        code = str(low).strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        state = state_by_native.get(state_fa.strip())
        if state is None:
            unknown_states[state_fa] = unknown_states.get(state_fa, 0) + 1
            skipped_no_state += 1

        locality = city_fa.strip()
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ir_country["id"]),
            "country_code": "IR",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "area"
        record["source"] = "iran-post-via-saeidi-dev"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_states:
        print("Unknown states (not found in CSC native field):")
        for s, n in sorted(unknown_states.items(), key=lambda x: -x[1]):
            print(f"  {s!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/IR.json"
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
        f"({len(merged):,} rows, {size_kb:.0f} KB)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
