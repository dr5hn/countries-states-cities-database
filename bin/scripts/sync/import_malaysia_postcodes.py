#!/usr/bin/env python3
"""Malaysia -> contributions/postcodes/MY.json importer for #1039.

Source data
-----------
The community ``AsyrafHussin/malaysia-postcodes`` repository ships
the Pos Malaysia catalogue as a nested JSON keyed by State -> City ->
[postcodes]:

    { "state": [
        {"name": "Selangor", "city": [{"name": "...", "postcode": ["..."]}]},
        ...
    ]}

Source URL: https://raw.githubusercontent.com/AsyrafHussin/malaysia-postcodes/master/all.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves ``state_id`` via case-insensitive name match against
   states.json with a 5-entry STATE_ALIASES bridge for Federal
   Territories (Wp prefix) and Malay-spelling variants.
3. Emits one record per ``(postcode, city)`` pair.
4. Writes contributions/postcodes/MY.json idempotently.

License & attribution
---------------------
- Source: AsyrafHussin/malaysia-postcodes (MIT) which redistributes
  the publicly published Pos Malaysia index.
- Each row: ``source: "pos-malaysia-via-AsyrafHussin"``

Usage
-----
    python3 bin/scripts/sync/import_malaysia_postcodes.py
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
    "https://raw.githubusercontent.com/AsyrafHussin/malaysia-postcodes/"
    "master/all.json"
)

# Source name (lowercased) -> CSC states.json "name"
STATE_ALIASES: Dict[str, str] = {
    "wp kuala lumpur": "Kuala Lumpur",
    "wp putrajaya": "Putrajaya",
    "wp labuan": "Labuan",
    "melaka": "Malacca",
    "pulau pinang": "Penang",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


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
    my_country = next((c for c in countries if c.get("iso2") == "MY"), None)
    if my_country is None:
        print("ERROR: MY not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(my_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    my_states = [s for s in states if s.get("country_id") == my_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"].lower(): s for s in my_states}
    print(f"Country: Malaysia (id={my_country['id']}); states indexed: {len(my_states)}")

    src_states = data.get("state", []) if isinstance(data, dict) else []
    print(f"Source states: {len(src_states)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for st in src_states:
        nm = (st.get("name") or "").strip()
        target_name = STATE_ALIASES.get(nm.lower(), nm).lower()
        state = state_by_name.get(target_name)
        for city in st.get("city", []) or []:
            city_name = (city.get("name") or "").strip()
            for raw_code in city.get("postcode", []) or []:
                code = str(raw_code).strip()
                if not code:
                    continue
                if not regex.match(code):
                    skipped_bad_regex += 1
                    continue
                key = (code, city_name.lower())
                if key in seen:
                    continue
                seen.add(key)

                record: Dict[str, object] = {
                    "code": code,
                    "country_id": int(my_country["id"]),
                    "country_code": "MY",
                }
                if state is not None:
                    record["state_id"] = int(state["id"])
                    record["state_code"] = state.get("iso2")
                    matched_state += 1
                else:
                    skipped_no_state += 1

                if city_name:
                    record["locality_name"] = city_name
                record["type"] = "full"
                record["source"] = "pos-malaysia-via-AsyrafHussin"
                records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MY.json"
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
