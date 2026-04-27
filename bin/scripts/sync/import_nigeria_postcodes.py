#!/usr/bin/env python3
"""Nigeria -> contributions/postcodes/NG.json importer for #1039.

Source data
-----------
The community ``ifeLight/nigeria-lga-postalcodes`` repository ships
NIPOST's catalogue keyed by State -> LGA -> [postcodes]:

    {"Adamawa": {"Demsa": ["642108", ...], ...}, ...}

Source URL: https://raw.githubusercontent.com/ifeLight/nigeria-lga-postalcodes/master/src/resources/state-lga-postcode-map.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves ``state_id`` via case-insensitive name match against
   states.json with a 1-entry alias for the FCT (source: "Federal
   Capital Territory" -> CSC: "Abuja Federal Capital Territory").
3. Emits one record per ``(postcode, LGA)`` pair (one LGA can hold
   multiple unique 6-digit codes).
4. Writes contributions/postcodes/NG.json idempotently.

License & attribution
---------------------
- Source: ifeLight/nigeria-lga-postalcodes (open redistribution of
  NIPOST's publicly published postcode index).
- Each row: ``source: "nipost-via-ifeLight"``

Usage
-----
    python3 bin/scripts/sync/import_nigeria_postcodes.py
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
    "https://raw.githubusercontent.com/ifeLight/nigeria-lga-postalcodes/"
    "master/src/resources/state-lga-postcode-map.json"
)

STATE_ALIASES: Dict[str, str] = {
    "federal capital territory": "Abuja Federal Capital Territory",
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
    ng_country = next((c for c in countries if c.get("iso2") == "NG"), None)
    if ng_country is None:
        print("ERROR: NG not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ng_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ng_states = [s for s in states if s.get("country_id") == ng_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"].lower(): s for s in ng_states}
    print(f"Country: Nigeria (id={ng_country['id']}); states indexed: {len(ng_states)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for state_name, lgas in data.items():
        target = STATE_ALIASES.get(state_name.lower(), state_name).lower()
        state = state_by_name.get(target)
        if not isinstance(lgas, dict):
            continue
        for lga, codes in lgas.items():
            for raw in codes or []:
                code = str(raw).strip()
                if not code:
                    continue
                if code.isdigit() and len(code) == 5:
                    code = "0" + code
                if not regex.match(code):
                    skipped_bad_regex += 1
                    continue
                key = (code, lga.strip().lower())
                if key in seen:
                    continue
                seen.add(key)

                record: Dict[str, object] = {
                    "code": code,
                    "country_id": int(ng_country["id"]),
                    "country_code": "NG",
                }
                if state is not None:
                    record["state_id"] = int(state["id"])
                    record["state_code"] = state.get("iso2")
                    matched_state += 1
                else:
                    skipped_no_state += 1

                if lga:
                    record["locality_name"] = lga.strip()
                record["type"] = "full"
                record["source"] = "nipost-via-ifeLight"
                records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/NG.json"
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
