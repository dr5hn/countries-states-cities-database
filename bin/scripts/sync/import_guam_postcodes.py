#!/usr/bin/env python3
"""Guam -> contributions/postcodes/GU.json importer for issue #1039.

Source data
-----------
Guam uses US ZIP codes 96910-96932. The US Census ZCTA file
(already shipped to contributions/postcodes/US.json under
state_code='GU') contains 7 GU-mapped postcodes with WGS-84
lat/lng centroids.

CSC represents Guam as its own country (iso2=GU, country_id=80)
with 19 villages as states. This importer mirrors the same codes
into GU.json under the GU country namespace and FK'd to the
nearest GU city by centroid distance.

What this script does
---------------------
1. Reads existing US.json filtered to state_code='GU'.
2. Loads contributions/cities/GU.json (25 GU localities).
3. For each GU ZIP, finds the nearest GU city by haversine distance,
   uses that city's state_id (one of 19 villages).
4. Writes contributions/postcodes/GU.json with country_id=80.

License & attribution
---------------------
- Original source: US Census ZCTA Gazetteer (CC-0, public domain)
- Each row: ``source: "us-census-via-gu-mirror"``

Usage
-----
    python3 bin/scripts/sync/import_guam_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]

    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    gu_country = next((c for c in countries if c.get("iso2") == "GU"), None)
    if gu_country is None:
        print("ERROR: GU not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(gu_country.get("postal_code_regex") or ".*")

    us_path = project_root / "contributions/postcodes/US.json"
    us_data = json.load(us_path.open(encoding="utf-8"))
    gu_zips = [r for r in us_data if r.get("state_code") == "GU"]
    print(f"GU-mapped ZIPs in US.json: {len(gu_zips)}")

    cities_path = project_root / "contributions/cities/GU.json"
    gu_cities = json.load(cities_path.open(encoding="utf-8"))
    gu_cities_with_geo = []
    for c in gu_cities:
        try:
            lat = float(c.get("latitude") or 0)
            lon = float(c.get("longitude") or 0)
        except (ValueError, TypeError):
            continue
        if lat or lon:
            gu_cities_with_geo.append((lat, lon, c))
    print(f"GU cities with geo: {len(gu_cities_with_geo)}")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    gu_states = {s["id"]: s for s in states if s.get("country_id") == gu_country["id"]}
    print(
        f"Country: Guam (id={gu_country['id']}); "
        f"states indexed: {len(gu_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for r in gu_zips:
        code = r["code"]
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except (ValueError, TypeError, KeyError):
            lat = lon = None

        nearest_city = None
        if lat is not None and lon is not None and gu_cities_with_geo:
            best_d = float("inf")
            for clat, clon, city in gu_cities_with_geo:
                d = haversine_km(lat, lon, clat, clon)
                if d < best_d:
                    best_d = d
                    nearest_city = city

        state = None
        locality = None
        if nearest_city:
            state = gu_states.get(nearest_city.get("state_id"))
            locality = nearest_city.get("name")

        if state is None:
            skipped_no_state += 1
        else:
            matched_state += 1

        key = (code, (locality or "").lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(gu_country["id"]),
            "country_code": "GU",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
        if locality:
            record["locality_name"] = locality
        if lat is not None and lon is not None:
            record["latitude"] = f"{lat:.6f}"
            record["longitude"] = f"{lon:.6f}"
        record["type"] = "full"
        record["source"] = "us-census-via-gu-mirror"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/GU.json"
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
