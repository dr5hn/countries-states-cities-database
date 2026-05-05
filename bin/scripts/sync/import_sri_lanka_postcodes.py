#!/usr/bin/env python3
"""Sri Lanka -> contributions/postcodes/LK.json importer for issue #1039.

Source data
-----------
The community ``madurapa/sri-lanka-provinces-districts-cities``
repository (MIT-licensed) ships SQL dumps for the full Sri Lankan
geographic hierarchy: 9 provinces, 25 districts, 2,053 cities with
5-digit postcodes and lat/lng centroids.

    cities: (id, district_id, name_en, name_si, name_ta,
             sub_name_en, sub_name_si, sub_name_ta,
             postcode, latitude, longitude)
    districts: (id, province_id, name_en, name_si, name_ta)

Source URL: https://raw.githubusercontent.com/madurapa/sri-lanka-provinces-districts-cities/master/cities.sql

What this script does
---------------------
1. Fetches both cities.sql and districts.sql via urllib.
2. Parses the INSERT tuples with regex (no MySQL needed).
3. Builds source district_id -> district_name from districts.sql.
4. Resolves state FK by direct district-name match against CSC's
   25 LK district entries.
5. Emits one row per (postcode, city, district) with English city
   name as locality_name and lat/lng centroid.
6. Writes contributions/postcodes/LK.json idempotently.

Coverage
--------
- 2,053 cities / 100% state FK
- All 25 CSC LK district entries covered (also covered by 9 provinces
  via the district->province hierarchy in CSC, but we map to district
  level which is the more specific resolution)

License & attribution
---------------------
- Source: madurapa/sri-lanka-provinces-districts-cities (MIT)
- Upstream: Sri Lanka Postal Department public lookup
- Each row: ``source: "sri-lanka-post-via-madurapa"``

Usage
-----
    python3 bin/scripts/sync/import_sri_lanka_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


CITIES_URL = (
    "https://raw.githubusercontent.com/madurapa/sri-lanka-provinces-districts-cities/"
    "master/cities.sql"
)
DISTRICTS_URL = (
    "https://raw.githubusercontent.com/madurapa/sri-lanka-provinces-districts-cities/"
    "master/districts.sql"
)

# District INSERT tuple: (id, province_id, name_en, name_si, name_ta)
DISTRICT_PATTERN = re.compile(
    r"\((\d+),\s*\d+,\s*'([^']*)',\s*'[^']*',\s*'[^']*'\)"
)

# City INSERT tuple: (id, district_id, name_en, name_si, name_ta,
#                    sub_name_en, sub_name_si, sub_name_ta,
#                    postcode, latitude, longitude)
CITY_PATTERN = re.compile(
    r"\(\d+,\s*(\d+),\s*'([^']*)',\s*'[^']*',\s*'[^']*',\s*"
    r"(?:NULL|'[^']*'),\s*(?:NULL|'[^']*'),\s*(?:NULL|'[^']*'),\s*"
    r"'([^']*)',\s*'([^']*)',\s*'([^']*)'\)"
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"fetching {DISTRICTS_URL}")
    districts_text = fetch_text(DISTRICTS_URL)
    district_id_to_name = {
        int(m[0]): m[1] for m in DISTRICT_PATTERN.findall(districts_text)
    }
    print(f"districts loaded: {len(district_id_to_name)}")

    print(f"fetching {CITIES_URL}")
    cities_text = fetch_text(CITIES_URL)
    city_rows = CITY_PATTERN.findall(cities_text)
    print(f"cities parsed: {len(city_rows):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    lk_country = next((c for c in countries if c.get("iso2") == "LK"), None)
    if lk_country is None:
        print("ERROR: LK not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(lk_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    lk_states = [s for s in states if s.get("country_id") == lk_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"]: s for s in lk_states if s.get("name")}
    print(
        f"Country: Sri Lanka (id={lk_country['id']}); "
        f"states indexed: {len(lk_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_districts: Dict[str, int] = {}

    for district_id_str, city_en, postcode, lat, lon in city_rows:
        district_id = int(district_id_str)
        district_name = district_id_to_name.get(district_id)

        code = postcode.strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        state = state_by_name.get(district_name) if district_name else None
        if state is None:
            unknown_districts[district_name or f"id={district_id}"] = (
                unknown_districts.get(district_name or f"id={district_id}", 0) + 1
            )
            skipped_no_state += 1

        locality = city_en.strip()
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(lk_country["id"]),
            "country_code": "LK",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        if lat and lon:
            record["latitude"] = lat
            record["longitude"] = lon
        record["type"] = "full"
        record["source"] = "sri-lanka-post-via-madurapa"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_districts:
        print("Unknown districts:")
        for d, n in sorted(unknown_districts.items(), key=lambda x: -x[1]):
            print(f"  {d!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/LK.json"
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
