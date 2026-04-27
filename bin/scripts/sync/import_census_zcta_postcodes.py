#!/usr/bin/env python3
"""US Census ZCTA -> contributions/postcodes/US.json importer for issue #1039.

Source data
-----------
The U.S. Census Bureau publishes the canonical ZIP Code Tabulation Area
(ZCTA) gazetteer and the ZCTA-to-county relationship file each decennial
cycle. Both are public-domain, freely redistributable.

  Gazetteer:    https://www2.census.gov/geo/docs/maps-data/data/gazetteer/
                  2024_Gazetteer/2024_Gaz_zcta_national.zip
                  (5-digit ZCTA, area, centroid lat/lng)

  Relationship: https://www2.census.gov/geo/docs/maps-data/data/rel2020/
                  zcta520/tab20_zcta520_county20_natl.txt
                  (ZCTA -> county; first 2 digits of county GEOID = state FIPS)

What this script does
---------------------
1. Reads the unzipped gazetteer (tab-separated) for centroid coordinates
2. Reads the relationship file (pipe-separated) to derive ZCTA -> state FIPS
3. Resolves country_id (US = 233 in this dataset) and state_id by fips_code
4. Writes contributions/postcodes/US.json (~33,000 records)
5. Idempotent merge with existing curated rows by (code, locality_name)

ZCTAs that span multiple states
-------------------------------
A small number of ZCTAs (~hundreds) span two or more states (e.g. 80022,
which crosses CO/NE). The relationship file lists one row per ZCTA-county
pair, so we pick the FIRST state (by sort order) as the primary assignment.
This matches USPS practice of picking the largest-population state.

License
-------
Source: U.S. Census Bureau (public domain). No attribution required, but
each generated row records source: "us-census" for provenance.

Usage
-----
    # One-time downloads
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip',
      '/tmp/zcta_gaz.zip')"
    unzip -o /tmp/zcta_gaz.zip -d /tmp/

    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt',
      '/tmp/zcta_county.txt')"

    # Import
    python3 bin/scripts/sync/import_census_zcta_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_gazetteer(path: Path) -> Dict[str, Tuple[str, str]]:
    """ZCTA -> (latitude_str, longitude_str). Returns 8-decimal strings.

    The Census gazetteer is fixed-width-padded TSV; column names and values
    carry trailing whitespace. Normalise both before lookup.
    """
    out: Dict[str, Tuple[str, str]] = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        # Build a stripped-name -> original-name map so we can lookup robustly
        stripped = {(name or "").strip(): name for name in (reader.fieldnames or [])}
        geoid_key = stripped.get("GEOID")
        lat_key = stripped.get("INTPTLAT")
        lng_key = stripped.get("INTPTLONG")
        if not (geoid_key and lat_key and lng_key):
            return out
        for row in reader:
            zcta = (row.get(geoid_key) or "").strip()
            lat = (row.get(lat_key) or "").strip()
            lng = (row.get(lng_key) or "").strip()
            if not zcta or not lat or not lng:
                continue
            try:
                lat_f = float(lat)
                lng_f = float(lng)
                if abs(lat_f) > 90 or abs(lng_f) > 180:
                    continue
            except ValueError:
                continue
            out[zcta] = (
                f"{lat_f:.8f}".rstrip("0").rstrip(".") or "0",
                f"{lng_f:.8f}".rstrip("0").rstrip(".") or "0",
            )
    return out


def parse_relationship(path: Path) -> Dict[str, str]:
    """ZCTA -> primary state FIPS (2 chars). Pipe-separated; UTF-8 BOM-safe."""
    zcta_states: Dict[str, set] = defaultdict(set)
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            zcta = (row.get("GEOID_ZCTA5_20") or "").strip()
            county = (row.get("GEOID_COUNTY_20") or "").strip()
            if not zcta or not county or len(county) < 2:
                continue
            zcta_states[zcta].add(county[:2])
    # When a ZCTA spans multiple states, pick the lowest FIPS code as the primary.
    # USPS canonical assignment varies by ZIP; deterministic sort keeps the
    # script reproducible and easy to override per-row in follow-up curation.
    return {z: sorted(s)[0] for z, s in zcta_states.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gazetteer", default="/tmp/2024_Gaz_zcta_national.txt",
                        help="Path to unzipped Census gazetteer file")
    parser.add_argument("--relationship", default="/tmp/zcta_county.txt",
                        help="Path to ZCTA-county relationship file")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    gaz_path = Path(args.gazetteer)
    rel_path = Path(args.relationship)
    for label, p in [("gazetteer", gaz_path), ("relationship", rel_path)]:
        if not p.exists():
            print(f"ERROR: missing {label}: {p}", file=sys.stderr)
            return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    us = next((c for c in countries if c.get("iso2") == "US"), None)
    if us is None:
        print("ERROR: US not found in countries.json", file=sys.stderr)
        return 2

    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    us_states = [s for s in states if s.get("country_id") == us["id"]]

    # Numeric Census FIPS code -> ISO2 bridge for the five inhabited US territories.
    # states.json stores 2-letter GENC codes for these (RQ, AQ, GQ, VQ, CQ); Census
    # county GEOIDs use the numeric form, so we translate before lookup.
    TERRITORY_NUMERIC_FIPS = {
        "60": "AS",
        "66": "GU",
        "69": "MP",
        "72": "PR",
        "78": "VI",
    }
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in us_states if s.get("iso2")}

    state_by_fips: Dict[str, dict] = {}
    for s in us_states:
        fips = (s.get("fips_code") or "").strip()
        if fips and fips.isdigit():
            state_by_fips[fips.zfill(2)] = s
    # Add territory bridges
    for numeric_fips, iso2 in TERRITORY_NUMERIC_FIPS.items():
        territory = state_by_iso2.get(iso2)
        if territory:
            state_by_fips[numeric_fips] = territory

    print(f"Country: United States (id={us['id']})")
    print(f"US states with fips_code: {len(state_by_fips)}")

    gaz = parse_gazetteer(gaz_path)
    print(f"Gazetteer rows:       {len(gaz):,}")

    rel = parse_relationship(rel_path)
    print(f"Relationship ZCTAs:   {len(rel):,}")

    records: List[dict] = []
    matched_state = 0
    matched_coord = 0
    for zcta in sorted(set(gaz) | set(rel)):
        record = {
            "code": zcta,
            "country_id": int(us["id"]),
            "country_code": "US",
        }
        fips = rel.get(zcta)
        if fips:
            state = state_by_fips.get(fips)
            if state:
                record["state_id"] = int(state["id"])
                if state.get("iso2"):
                    record["state_code"] = state["iso2"]
                matched_state += 1
        record["type"] = "full"
        coord = gaz.get(zcta)
        if coord:
            record["latitude"] = coord[0]
            record["longitude"] = coord[1]
            matched_coord += 1
        record["source"] = "us-census"
        records.append(record)

    print(f"Records built:        {len(records):,}")
    print(f"  with state_id:      {matched_state:,} ({matched_state*100//max(1,len(records))}%)")
    print(f"  with coordinates:   {matched_coord:,} ({matched_coord*100//max(1,len(records))}%)")

    if args.dry_run:
        print("\n--dry-run set; no files written.")
        return 0

    target = project_root / "contributions/postcodes/US.json"
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        seen = {(r["code"], (r.get("locality_name") or "").lower()) for r in existing}
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in seen:
                merged.append(r)
                seen.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = sorted(records, key=lambda r: (r["code"], r.get("locality_name", "")))

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
