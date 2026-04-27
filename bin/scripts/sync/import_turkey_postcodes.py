#!/usr/bin/env python3
"""Turkey -> contributions/postcodes/TR.json importer for issue #1039.

Source data
-----------
The community-maintained ``muratgozel/turkey-neighbourhoods`` package
(MIT) ships a flat JSON of every Turkish neighbourhood with its PTT
postal code. Each row is a 5-tuple:

    [city_code, city_name, district, neighbourhood, postal_code]

- ``city_code`` is the 2-digit Turkish plate/province code (01-81),
  which exactly matches CSC's ``states.json`` ``iso2`` for Turkey.
- ``postal_code`` is the 5-digit PTT code; its first two digits are
  always the province code.

Source URL: https://raw.githubusercontent.com/muratgozel/turkey-neighbourhoods/master/src/data/neighbourhoods.json

What this script does
---------------------
1. Fetches the neighbourhoods JSON via urllib (curl is blocked).
2. Dedupes at (postal_code, district) granularity (multiple
   neighbourhoods often share a district-level code).
3. Resolves ``state_id`` directly from the city_code which equals
   the CSC iso2 for that province.
4. Writes contributions/postcodes/TR.json idempotently.

License & attribution
---------------------
- Source: muratgozel/turkey-neighbourhoods (MIT) which redistributes
  publicly published PTT postcode data.
- Each row: ``source: "ptt-via-turkey-neighbourhoods"``

Usage
-----
    python3 bin/scripts/sync/import_turkey_postcodes.py
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
    "https://raw.githubusercontent.com/muratgozel/turkey-neighbourhoods/"
    "master/src/data/neighbourhoods.json"
)


def fetch_json(url: str) -> List[List[str]]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.input:
        rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    else:
        rows = fetch_json(SOURCE_URL)

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    tr_country = next((c for c in countries if c.get("iso2") == "TR"), None)
    if tr_country is None:
        print("ERROR: TR not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(tr_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    tr_states = [s for s in states if s.get("country_id") == tr_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        (s.get("iso2") or "").upper(): s for s in tr_states if s.get("iso2")
    }
    print(f"Country: Turkey (id={tr_country['id']}); states indexed: {len(tr_states)}")
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            continue
        city_code, _city_name, district, _neighbourhood, code = (
            (row[0] or "").strip(),
            (row[1] or "").strip(),
            (row[2] or "").strip(),
            (row[3] or "").strip(),
            (row[4] or "").strip(),
        )
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        # Dedup at (code, district)
        key = (code, district.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(tr_country["id"]),
            "country_code": "TR",
        }
        state = state_by_iso2.get(city_code.upper().zfill(2))
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if district:
            record["locality_name"] = district
        record["type"] = "full"
        record["source"] = "ptt-via-turkey-neighbourhoods"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/TR.json"
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
