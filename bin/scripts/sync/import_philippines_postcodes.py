#!/usr/bin/env python3
"""Philippines -> contributions/postcodes/PH.json importer for #1039.

Source data
-----------
The community ``jayson-panganiban/phzipcodes`` package ships the
PHLPost catalogue as a nested JSON keyed by Region -> Province ->
City -> [zip codes]:

    {
      "Region 1 (Ilocos Region)": {
        "Pangasinan": {
          "Alcala": ["2425"],
          ...
        },
        ...
      },
      ...
    }

Source URL: https://raw.githubusercontent.com/jayson-panganiban/phzipcodes/main/phzipcodes/data/ph_zip_codes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Walks Region -> Province -> City -> codes; emits one row per
   ``(zip code, city)`` pair.
3. Resolves ``state_id`` via case-insensitive province-name match
   against ``states.json``; STATE_ALIASES handles a handful of source
   names that carry parenthetical suffixes or use a region label.
4. Writes contributions/postcodes/PH.json idempotently.

License & attribution
---------------------
- Source: jayson-panganiban/phzipcodes; data scraped from PHLPost's
  publicly published postcode index.
- Each row: ``source: "phlpost-via-jayson-panganiban"``

Usage
-----
    python3 bin/scripts/sync/import_philippines_postcodes.py
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
    "https://raw.githubusercontent.com/jayson-panganiban/phzipcodes/"
    "main/phzipcodes/data/ph_zip_codes.json"
)

# Source name (lowercased) -> CSC states.json "name" (case-insensitive)
STATE_ALIASES: Dict[str, str] = {
    "metro manila": "National Capital Region (Metro Manila)",
    "camarines sur (camsur)": "Camarines Sur",
    "cotabato (north)": "Cotabato",
    "davao de oro (formerly compostela valley)": "Davao de Oro",
    # The source feed has a "Samar" entry (Region 8) that maps to
    # Western Samar (a/k/a Samar Province) — the post-1969 rename of
    # "Samar" to "Western Samar" is reflected in CSC's iso2 = WSA.
    "samar": "Western Samar",
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
    ph_country = next((c for c in countries if c.get("iso2") == "PH"), None)
    if ph_country is None:
        print("ERROR: PH not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ph_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ph_states = [s for s in states if s.get("country_id") == ph_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"].lower(): s for s in ph_states}
    print(f"Country: Philippines (id={ph_country['id']}); states indexed: {len(ph_states)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for _region, provinces in data.items():
        if not isinstance(provinces, dict):
            continue
        for prov_name, cities in provinces.items():
            prov_key = prov_name.strip().lower()
            if not prov_key:
                continue
            target_name = STATE_ALIASES.get(prov_key, prov_name).lower()
            state = state_by_name.get(target_name)
            if not isinstance(cities, dict):
                continue
            for city, codes in cities.items():
                if not isinstance(codes, list):
                    continue
                for raw_code in codes:
                    code = str(raw_code).strip()
                    if not code:
                        continue
                    if code.isdigit() and len(code) == 3:
                        code = "0" + code
                    if not regex.match(code):
                        skipped_bad_regex += 1
                        continue
                    key = (code, (city or "").strip().lower())
                    if key in seen:
                        continue
                    seen.add(key)

                    record: Dict[str, object] = {
                        "code": code,
                        "country_id": int(ph_country["id"]),
                        "country_code": "PH",
                    }
                    if state is not None:
                        record["state_id"] = int(state["id"])
                        record["state_code"] = state.get("iso2")
                        matched_state += 1
                    else:
                        skipped_no_state += 1

                    if city:
                        record["locality_name"] = city.strip()
                    record["type"] = "full"
                    record["source"] = "phlpost-via-jayson-panganiban"
                    records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PH.json"
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
