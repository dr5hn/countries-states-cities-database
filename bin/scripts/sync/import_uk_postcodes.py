#!/usr/bin/env python3
"""United Kingdom -> contributions/postcodes/GB.json importer for issue #1039.

Source data
-----------
The community ``dwyl/uk-postcodes-latitude-longitude-complete-csv``
repository ships a 32 MB ZIP containing 1,738,243 UK postcodes with
WGS-84 lat/lng centroids (October 2017 snapshot from Ordnance Survey
Code-Point Open).

    id,postcode,latitude,longitude
    1,AB10 1XG,57.144165,-2.114848
    2,AB10 6RN,57.137880,-2.121487

What this script ships
----------------------
**Postcode-area level (1-2 letter prefix), 124 records.**

The full 6-7 character UK postcode list at 1.7M rows would generate
a ~500 MB JSON, which exceeds the in-band cities/*.json size envelope
(largest currently is PT.json at 38 MB). Per the maintainer's notes,
records >200k need the gz-to-Releases pattern (#1374) — not yet
deployed.

Postcode-area level is the UK equivalent of Canada's FSA: 124 1-2
letter prefixes (M, SW, EC1, etc.) each covering thousands of full
postcodes. Each row carries the area-centroid lat/lng (mean of all
underlying full postcode centroids) and the canonical city/region
locality label.

What this script does
---------------------
1. Fetches the ZIP via urllib (curl is blocked).
2. Extracts ukpostcodes.csv in-memory.
3. Aggregates 1.7M rows by 1-2 letter area prefix to compute mean
   centroid.
4. Joins each area to its canonical city/region label via
   AREA_TO_LOCALITY (124-entry hand-curated map).
5. Writes contributions/postcodes/GB.json idempotently.

Why country-only state FK
-------------------------
CSC has 221 GB states across nine types (unitary authority,
metropolitan district, london borough, council area, two-tier county,
district, country, province, city). Postcode areas often span
multiple unitary authorities or counties, so a 1:1 area->state map
would be misleading. Future PRs can layer in postcode-district-level
FK (~3,000 districts), which is finer-grained than area but still
manageable in size.

This matches the "country-only" pattern already used for SE (Sweden)
and SI (Slovenia) where source data doesn't map cleanly to CSC's
state hierarchy.

License & attribution
---------------------
- Source: dwyl/uk-postcodes-latitude-longitude-complete-csv (no
  formal license file, October 2017 snapshot)
- Upstream: Ordnance Survey Code-Point Open (OS OpenData / OGL3,
  Crown Copyright)
- Each row: ``source: "ordnance-survey-via-dwyl"``

Tier 5 per #1039 license-tier policy (free redistribution permitted,
no formal licence) — flagged in PR.

Usage
-----
    python3 bin/scripts/sync/import_uk_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/dwyl/"
    "uk-postcodes-latitude-longitude-complete-csv/master/ukpostcodes.csv.zip"
)

# The 124 UK postcode areas mapped to their canonical city/region label.
# Ref: Royal Mail Postcode Address File area definitions.
AREA_TO_LOCALITY: Dict[str, str] = {
    "AB": "Aberdeen",
    "AL": "St Albans",
    "B": "Birmingham",
    "BA": "Bath",
    "BB": "Blackburn",
    "BD": "Bradford",
    "BH": "Bournemouth",
    "BL": "Bolton",
    "BN": "Brighton",
    "BR": "Bromley",
    "BS": "Bristol",
    "BT": "Belfast",
    "CA": "Carlisle",
    "CB": "Cambridge",
    "CF": "Cardiff",
    "CH": "Chester",
    "CM": "Chelmsford",
    "CO": "Colchester",
    "CR": "Croydon",
    "CT": "Canterbury",
    "CV": "Coventry",
    "CW": "Crewe",
    "DA": "Dartford",
    "DD": "Dundee",
    "DE": "Derby",
    "DG": "Dumfries",
    "DH": "Durham",
    "DL": "Darlington",
    "DN": "Doncaster",
    "DT": "Dorchester",
    "DY": "Dudley",
    "E": "London East",
    "EC": "London East Central",
    "EH": "Edinburgh",
    "EN": "Enfield",
    "EX": "Exeter",
    "FK": "Falkirk",
    "FY": "Blackpool (Fylde)",
    "G": "Glasgow",
    "GL": "Gloucester",
    "GU": "Guildford",
    "GY": "Guernsey",
    "HA": "Harrow",
    "HD": "Huddersfield",
    "HG": "Harrogate",
    "HP": "Hemel Hempstead",
    "HR": "Hereford",
    "HS": "Outer Hebrides",
    "HU": "Hull",
    "HX": "Halifax",
    "IG": "Ilford",
    "IM": "Isle of Man",
    "IP": "Ipswich",
    "IV": "Inverness",
    "JE": "Jersey",
    "KA": "Kilmarnock",
    "KT": "Kingston upon Thames",
    "KW": "Kirkwall",
    "KY": "Kirkcaldy",
    "L": "Liverpool",
    "LA": "Lancaster",
    "LD": "Llandrindod Wells",
    "LE": "Leicester",
    "LL": "Llandudno",
    "LN": "Lincoln",
    "LS": "Leeds",
    "LU": "Luton",
    "M": "Manchester",
    "ME": "Medway",
    "MK": "Milton Keynes",
    "ML": "Motherwell",
    "N": "London North",
    "NE": "Newcastle upon Tyne",
    "NG": "Nottingham",
    "NN": "Northampton",
    "NP": "Newport",
    "NR": "Norwich",
    "NW": "London North West",
    "OL": "Oldham",
    "OX": "Oxford",
    "PA": "Paisley",
    "PE": "Peterborough",
    "PH": "Perth",
    "PL": "Plymouth",
    "PO": "Portsmouth",
    "PR": "Preston",
    "RG": "Reading",
    "RH": "Redhill",
    "RM": "Romford",
    "S": "Sheffield",
    "SA": "Swansea",
    "SE": "London South East",
    "SG": "Stevenage",
    "SK": "Stockport",
    "SL": "Slough",
    "SM": "Sutton",
    "SN": "Swindon",
    "SO": "Southampton",
    "SP": "Salisbury",
    "SR": "Sunderland",
    "SS": "Southend-on-Sea",
    "ST": "Stoke-on-Trent",
    "SW": "London South West",
    "SY": "Shrewsbury",
    "TA": "Taunton",
    "TD": "Tweeddale",
    "TF": "Telford",
    "TN": "Tonbridge",
    "TQ": "Torquay",
    "TR": "Truro",
    "TS": "Cleveland",
    "TW": "Twickenham",
    "UB": "Southall",
    "W": "London West",
    "WA": "Warrington",
    "WC": "London West Central",
    "WD": "Watford",
    "WF": "Wakefield",
    "WN": "Wigan",
    "WR": "Worcester",
    "WS": "Walsall",
    "WV": "Wolverhampton",
    "YO": "York",
    "ZE": "Shetland",
}

AREA_RE = re.compile(r"^([A-Z]{1,2})")


def fetch_zip(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local zip (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    raw = (
        Path(args.input).read_bytes()
        if args.input
        else fetch_zip(SOURCE_URL)
    )
    print(f"zip size: {len(raw):,} bytes")

    zf = zipfile.ZipFile(io.BytesIO(raw))
    csv_name = next(
        n
        for n in zf.namelist()
        if n.endswith(".csv") and not n.startswith("__")
    )
    with zf.open(csv_name) as f:
        text = f.read().decode("utf-8", errors="replace")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    gb_country = next((c for c in countries if c.get("iso2") == "GB"), None)
    if gb_country is None:
        print("ERROR: GB not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(gb_country.get("postal_code_regex") or ".*")
    print(f"Country: United Kingdom (id={gb_country['id']})")

    reader = csv.DictReader(io.StringIO(text))
    area_data: Dict[str, Dict[str, float]] = {}
    total = 0
    for row in reader:
        total += 1
        pc = (row.get("postcode") or "").replace(" ", "").upper()
        m = AREA_RE.match(pc)
        if not m:
            continue
        area = m.group(1)
        try:
            lat = float(row["latitude"])
            lon = float(row["longitude"])
        except (ValueError, TypeError, KeyError):
            continue
        d = area_data.setdefault(
            area, {"count": 0, "lat_sum": 0.0, "lon_sum": 0.0}
        )
        d["count"] += 1
        d["lat_sum"] += lat
        d["lon_sum"] += lon
    print(f"Source rows: {total:,}; distinct postcode areas: {len(area_data)}")

    records: List[dict] = []
    skipped_bad_regex = 0
    unknown_areas: List[str] = []

    for area in sorted(area_data):
        d = area_data[area]
        if not regex.match(area):
            skipped_bad_regex += 1
            continue
        lat = d["lat_sum"] / d["count"]
        lon = d["lon_sum"] / d["count"]
        locality = AREA_TO_LOCALITY.get(area)
        if locality is None:
            unknown_areas.append(area)
            locality = ""

        record: Dict[str, object] = {
            "code": area,
            "country_id": int(gb_country["id"]),
            "country_code": "GB",
        }
        if locality:
            record["locality_name"] = locality
        record["latitude"] = f"{lat:.6f}"
        record["longitude"] = f"{lon:.6f}"
        record["type"] = "area"
        record["source"] = "ordnance-survey-via-dwyl"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    if unknown_areas:
        print(f"Unknown areas (not in AREA_TO_LOCALITY): {unknown_areas}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/GB.json"
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
