#!/usr/bin/env python3
"""Mongolia -> contributions/postcodes/MN.json importer for #1039.

Source data
-----------
The community ``bekkaze/mnzipcode`` package ships Mongol Шуудан's
catalogue as a nested JSON tree of aimags / capital districts ->
sub-units, each carrying a 5-digit zipcode plus Mongolian + Latin
names:

    {"zipcode": [
       {"stat": "capital", "mnname": "Улаанбаатар", "name":
        "Ulaanbaatar", "zipcode": "11000", "sub_items": [...]},
       ...
    ]}

Source URL: https://raw.githubusercontent.com/bekkaze/mnzipcode/main/data/data.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Recursively flattens the aimag tree into ``(zipcode, locality)``
   tuples, carrying the top-level aimag/capital name forward for
   FK resolution.
3. Resolves ``state_id`` by ASCII-fold name match against
   ``states.json`` (handles Latin variants such as Khövsgöl).
4. Writes contributions/postcodes/MN.json idempotently.

Also updates the Mongolia ``postal_code_regex``/``format`` in
``countries.json`` from a 6-digit shape to the canonical 5-digit
shape used by Mongol Шуудан (matches every code in this dataset
and the UPU spec).

License & attribution
---------------------
- Source: bekkaze/mnzipcode (open redistribution of Mongol Шуудан's
  publicly published index).
- Each row: ``source: "mongol-shuudan-via-bekkaze"``

Usage
-----
    python3 bin/scripts/sync/import_mongolia_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


SOURCE_URL = (
    "https://raw.githubusercontent.com/bekkaze/mnzipcode/main/data/data.json"
)

# Source aimag-name (lowercased) -> CSC states.json "name"
STATE_ALIASES: Dict[str, str] = {
    "tuv": "Töv",        # source spells without diacritic; CSC uses Cyrillic-derived "ö"
    "dundgobi": "Dundgovi",  # source uses 'b'; CSC and UPU use 'v'
}


def _fold(value: str) -> str:
    s = "".join(
        c for c in unicodedata.normalize("NFKD", (value or "").lower())
        if not unicodedata.combining(c)
    )
    return s.strip()


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def walk(node: dict, aimag_name: Optional[str], rows: List[tuple]) -> None:
    """Recursively flatten the bekkaze tree into (zipcode, name, aimag) tuples."""
    code = (node.get("zipcode") or "").strip()
    name = (node.get("name") or node.get("mnname") or "").strip()
    if code:
        rows.append((code, name, aimag_name or name))
    next_aimag = aimag_name or name
    for child in node.get("sub_items", []) or []:
        if isinstance(child, dict):
            walk(child, next_aimag, rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    mn_country = next((c for c in countries if c.get("iso2") == "MN"), None)
    if mn_country is None:
        print("ERROR: MN not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(mn_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    mn_states = [s for s in states if s.get("country_id") == mn_country["id"]]
    state_by_fold: Dict[str, dict] = {_fold(s["name"]): s for s in mn_states}
    print(f"Country: Mongolia (id={mn_country['id']}); states indexed: {len(mn_states)}")

    rows: List[tuple] = []
    for top in (data.get("zipcode") or []):
        if isinstance(top, dict):
            walk(top, None, rows)
    print(f"Flattened source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for code, locality, aimag in rows:
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        key = (code, (locality or "").lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(mn_country["id"]),
            "country_code": "MN",
        }
        target_aimag = STATE_ALIASES.get(_fold(aimag), aimag)
        state = state_by_fold.get(_fold(target_aimag))
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "mongol-shuudan-via-bekkaze"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MN.json"
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
