#!/usr/bin/env python3
"""Puerto Rico -> contributions/postcodes/PR.json importer for issue #1039.

Source data
-----------
Puerto Rico uses US ZIP codes in the 006xx-007xx + 009xx ranges.
The US Census ZCTA file (already shipped to contributions/postcodes/
US.json under state_code='PR') contains 132 PR-mapped postcodes
with WGS-84 lat/lng centroids.

Although these codes live in US.json under country_code='US', CSC
also represents Puerto Rico as its own country (iso2=PR, country_id=
178), with 78 municipalities as states. This importer derives a
companion PR.json with the same codes mirrored into the PR country
namespace and FK'd to the nearest PR municipality by centroid
distance.

Source: contributions/postcodes/US.json (already shipped; derived
        from US Census ZCTA Gazetteer per import_us_census_postcodes
        — Tier 1 license, public domain CC-0).

What this script does
---------------------
1. Reads existing US.json filtered to state_code='PR' (132 codes).
2. Loads contributions/cities/PR.json (78 PR municipalities with
   lat/lng centroids).
3. For each PR ZIP, finds the nearest PR municipality by haversine
   distance to the ZIP centroid, uses that city's state_id.
4. Writes contributions/postcodes/PR.json with country_id=178.

License & attribution
---------------------
- Original source: US Census ZCTA Gazetteer (CC-0, public domain)
- Each row: ``source: "us-census-via-pr-mirror"``

Usage
-----
    python3 bin/scripts/sync/import_puerto_rico_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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
    pr_country = next((c for c in countries if c.get("iso2") == "PR"), None)
    if pr_country is None:
        print("ERROR: PR not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(pr_country.get("postal_code_regex") or ".*")

    # Source: existing US.json
    us_path = project_root / "contributions/postcodes/US.json"
    if not us_path.exists():
        print("ERROR: contributions/postcodes/US.json missing", file=sys.stderr)
        return 2
    us_data = json.load(us_path.open(encoding="utf-8"))
    pr_zips = [r for r in us_data if r.get("state_code") == "PR"]
    print(f"PR-mapped ZIPs in US.json: {len(pr_zips)}")

    # PR cities with lat/lng (78 municipalities, 1:1 with PR states)
    cities_path = project_root / "contributions/cities/PR.json"
    pr_cities = json.load(cities_path.open(encoding="utf-8"))
    pr_cities_with_geo: List[Tuple[float, float, dict]] = []
    for c in pr_cities:
        try:
            lat = float(c.get("latitude") or 0)
            lon = float(c.get("longitude") or 0)
        except (ValueError, TypeError):
            continue
        if lat or lon:
            pr_cities_with_geo.append((lat, lon, c))
    print(f"PR cities with geo: {len(pr_cities_with_geo)}")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    pr_states = {s["id"]: s for s in states if s.get("country_id") == pr_country["id"]}
    print(
        f"Country: Puerto Rico (id={pr_country['id']}); "
        f"states indexed: {len(pr_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for r in pr_zips:
        code = r["code"]
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        try:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
        except (ValueError, TypeError, KeyError):
            lat = lon = None

        # Find nearest PR municipality
        nearest_city = None
        if lat is not None and lon is not None and pr_cities_with_geo:
            best_d = float("inf")
            for clat, clon, city in pr_cities_with_geo:
                d = haversine_km(lat, lon, clat, clon)
                if d < best_d:
                    best_d = d
                    nearest_city = city

        state = None
        locality = None
        if nearest_city:
            sid = nearest_city.get("state_id")
            state = pr_states.get(sid)
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
            "country_id": int(pr_country["id"]),
            "country_code": "PR",
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
        record["source"] = "us-census-via-pr-mirror"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PR.json"
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
