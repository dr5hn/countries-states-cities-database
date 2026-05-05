#!/usr/bin/env python3
"""Tanzania -> contributions/postcodes/TZ.json importer for issue #1039.

Source data
-----------
The community ``Msuluzya/TanzaniaRegions`` repository (MIT-licensed)
ships ``json/tanzania-regions.json`` — a deeply-nested geographical
database derived from the Tanzania National Postal Authority (NAPA):

    {Region: {District: {"wards": {WardKey: {"streets": [...],
                                              "code": "55",
                                              "places": [5-digit, ...],
                                              "villages": [...]}}}}}

The ``places`` array of each ward holds the 5-digit NAPA postcodes
covering that ward.

Source URL: https://raw.githubusercontent.com/Msuluzya/TanzaniaRegions/master/json/tanzania-regions.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Walks the 4-level Region/District/Ward/Place hierarchy.
3. Resolves state FK via direct region-name match against CSC TZ
   states + 11-entry SOURCE_TO_ISO2 alias map handling Swahili
   region labels (Kaskazini Unguja, Kusini Pemba, etc.) and a
   Swahili/English duplicate set.
4. Emits one row per (5-digit code, ward, district) tuple. Each
   ward's *first* listed locality (street/village) becomes the
   record's locality_name; if absent, the ward key itself is used.
5. Writes contributions/postcodes/TZ.json idempotently.

Coverage upgrade
----------------
The previously-tracked ``meshackjr/Tanzania-Postal-Codes-SQL``
shipped only 1 region (Dar es Salaam) of 31. Msuluzya covers
**25 mainland regions** with 3,684 distinct 5-digit codes. The
research doc Tier B note (`Only Dar es Salaam (1/31 regions)`) is
now superseded.

Coverage gap
------------
Source has 11 island/Dar source labels with empty `places` arrays:
the 5 Zanzibar/Pemba regions (in both English and Swahili) and
Dar es Salaam itself. CSC's 6 corresponding island/coastal regions
(Pemba North/South, Zanzibar North/South/West, Dar es Salaam) will
not receive rows from this source.

License & attribution
---------------------
- Source: Msuluzya/TanzaniaRegions (MIT)
- Upstream: Tanzania National Postal Authority (NAPA) public lookup
- Each row: ``source: "tanzania-napa-via-msuluzya"``

Usage
-----
    python3 bin/scripts/sync/import_tanzania_postcodes.py
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
    "https://raw.githubusercontent.com/Msuluzya/TanzaniaRegions/"
    "master/json/tanzania-regions.json"
)

# Source region label -> CSC name. Mainland regions match by direct
# name; island/Zanzibar regions need Swahili-to-English mapping.
SOURCE_TO_CSC_NAME: Dict[str, str] = {
    # Swahili island/Zanzibar names -> CSC English names
    "Kaskazini Pemba": "Pemba North",
    "Kusini Pemba": "Pemba South",
    "Kaskazini Unguja": "Zanzibar North",
    "Kusini Unguja": "Zanzibar South",
    "Mjini Magharibi": "Zanzibar West",
    # English variants the source also lists:
    "Pemba North": "Pemba North",
    "Pemba South": "Pemba South",
    "Zanzibar North": "Zanzibar North",
    "Zanzibar Central/South": "Zanzibar South",
    "Zanzibar Urban/West": "Zanzibar West",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    print(f"Source regions: {len(data)}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    tz_country = next((c for c in countries if c.get("iso2") == "TZ"), None)
    if tz_country is None:
        print("ERROR: TZ not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(tz_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    tz_states = [s for s in states if s.get("country_id") == tz_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"]: s for s in tz_states if s.get("name")}
    print(
        f"Country: Tanzania (id={tz_country['id']}); "
        f"states indexed: {len(tz_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_regions: Dict[str, int] = {}

    for region, districts in data.items():
        csc_name = SOURCE_TO_CSC_NAME.get(region, region)
        state = state_by_name.get(csc_name)
        if not isinstance(districts, dict):
            continue

        for district, dval in districts.items():
            if not isinstance(dval, dict):
                continue
            wards = dval.get("wards") or {}
            for ward_key, ward in wards.items():
                if not isinstance(ward, dict):
                    continue
                places = ward.get("places") or []
                streets = ward.get("streets") or []
                villages = ward.get("villages") or []
                # Pick a representative locality for each ward
                ward_name = (
                    streets[0]
                    if streets
                    else (villages[0] if villages else ward_key)
                )
                ward_name = str(ward_name).strip()
                # Strip newlines (source has 'Sumbawanga\ncbd' style names)
                district_clean = (
                    district.replace("\n", " ").strip()
                    if isinstance(district, str)
                    else str(district)
                )

                for place in places:
                    code = str(place).strip()
                    if not regex.match(code):
                        skipped_bad_regex += 1
                        continue

                    if state is None:
                        unknown_regions[region] = unknown_regions.get(region, 0) + 1
                        skipped_no_state += 1

                    # Locality = ward_name + district where useful
                    if ward_name and district_clean and ward_name.lower() != district_clean.lower():
                        locality = f"{ward_name}, {district_clean}"
                    else:
                        locality = ward_name or district_clean

                    key = (code, locality.lower())
                    if key in seen:
                        continue
                    seen.add(key)

                    record: Dict[str, object] = {
                        "code": code,
                        "country_id": int(tz_country["id"]),
                        "country_code": "TZ",
                    }
                    if state is not None:
                        record["state_id"] = int(state["id"])
                        record["state_code"] = state.get("iso2")
                        matched_state += 1
                    if locality:
                        record["locality_name"] = locality
                    record["type"] = "full"
                    record["source"] = "tanzania-napa-via-msuluzya"
                    records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_regions:
        print("Unknown regions (not in CSC + SOURCE_TO_CSC_NAME):")
        for r, n in sorted(unknown_regions.items(), key=lambda x: -x[1]):
            print(f"  {r!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/TZ.json"
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
