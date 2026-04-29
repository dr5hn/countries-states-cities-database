#!/usr/bin/env python3
"""Ukraine -> contributions/postcodes/UA.json importer for issue #1039.

Source data
-----------
The community ``rvolykh/UAPostcodes`` repository ships a SQL dump of
every Ukrainian city/town with its 5-digit Ukrposhta index.

  INSERT INTO City VALUES(id, "name", "postcode", region_id, district_id);

The companion ``regions.sql`` defines the 27 oblast IDs in source order.

Source URL: https://raw.githubusercontent.com/rvolykh/UAPostcodes/master/db_scripts/cities.sql

What this script does
---------------------
1. Fetches the cities SQL via urllib (curl is blocked).
2. Parses the INSERT statements with a tolerant regex.
3. Maps source ``region_id`` (1-27 in source's own numbering) to CSC's
   ``states.json`` iso2 via a hand-curated 27-entry table.
4. Writes contributions/postcodes/UA.json idempotently.

License & attribution
---------------------
- Source: rvolykh/UAPostcodes; data compiled from Ukrposhta's
  publicly published index.
- Each row: ``source: "ukrposhta-via-rvolykh"``

Usage
-----
    python3 bin/scripts/sync/import_ukraine_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL_CITIES = (
    "https://raw.githubusercontent.com/rvolykh/UAPostcodes/"
    "master/db_scripts/cities.sql"
)
SOURCE_URL_DISTRICTS = (
    "https://raw.githubusercontent.com/rvolykh/UAPostcodes/"
    "master/db_scripts/districts.sql"
)

# rvolykh region_id (1..27, source order from regions.sql) -> CSC iso2
REGION_TO_ISO2: Dict[int, str] = {
    1:  "43",  # Autonomous Republic of Crimea
    2:  "05",  # Vinnytska
    3:  "07",  # Volynska
    4:  "12",  # Dnipropetrovska
    5:  "14",  # Donetska
    6:  "18",  # Zhytomyrska
    7:  "21",  # Zakarpatska
    8:  "23",  # Zaporizka
    9:  "26",  # Ivano-Frankivska
    10: "30",  # Kyiv (city)
    11: "32",  # Kyivska (oblast)
    12: "35",  # Kirovohradska
    13: "09",  # Luhanska
    14: "46",  # Lvivska
    15: "48",  # Mykolaivska
    16: "51",  # Odeska
    17: "53",  # Poltavska
    18: "56",  # Rivnenska
    19: "40",  # Sevastopol (city)
    20: "59",  # Sumska
    21: "61",  # Ternopilska
    22: "63",  # Kharkivska
    23: "65",  # Khersonska
    24: "68",  # Khmelnytska
    25: "71",  # Cherkaska
    26: "77",  # Chernivetska
    27: "74",  # Chernihivska
}

# Tolerant INSERT parsers.
# City schema: (id, "name", "postcode", district_id, ord_in_district)
CITY_INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+City\s+VALUES\s*\(\s*"
    r"(\d+)\s*,\s*"
    r'"([^"]*)"\s*,\s*'
    r'"([^"]*)"\s*,\s*'
    r"(\d+)\s*,\s*"
    r"(\d+)\s*\)\s*;",
    re.IGNORECASE,
)
# District schema: (id, "name", ord_in_region, region_id)
DISTRICT_INSERT_RE = re.compile(
    r"INSERT\s+INTO\s+District\s+VALUES\s*\(\s*"
    r"(\d+)\s*,\s*"
    r'"([^"]*)"\s*,\s*'
    r"(\d+)\s*,\s*"
    r"(\d+)\s*\)\s*;",
    re.IGNORECASE,
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cities_text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_text(SOURCE_URL_CITIES)
    )
    districts_text = fetch_text(SOURCE_URL_DISTRICTS)

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    ua_country = next((c for c in countries if c.get("iso2") == "UA"), None)
    if ua_country is None:
        print("ERROR: UA not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ua_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ua_states = [s for s in states if s.get("country_id") == ua_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        (s.get("iso2") or "").upper(): s for s in ua_states if s.get("iso2")
    }
    print(f"Country: Ukraine (id={ua_country['id']}); states indexed: {len(ua_states)}")

    # Build district_id -> region_id from districts.sql
    district_to_region: Dict[int, int] = {}
    for d in DISTRICT_INSERT_RE.finditer(districts_text):
        d_id, _d_name, _ord, region_id = d.groups()
        district_to_region[int(d_id)] = int(region_id)
    print(f"Districts indexed: {len(district_to_region):,}")

    matches = list(CITY_INSERT_RE.finditer(cities_text))
    print(f"Source INSERTs: {len(matches):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for m in matches:
        _id, name, code, district_id_str, _ord = m.groups()
        region_id = district_to_region.get(int(district_id_str))
        region_id_str = str(region_id) if region_id is not None else "0"
        code = code.strip()
        if not code:
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        key = (code, name.strip().lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ua_country["id"]),
            "country_code": "UA",
        }
        iso2 = REGION_TO_ISO2.get(int(region_id_str))
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
            else:
                skipped_no_state += 1
        else:
            skipped_no_state += 1

        if name:
            record["locality_name"] = name
        record["type"] = "full"
        record["source"] = "ukrposhta-via-rvolykh"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/UA.json"
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
