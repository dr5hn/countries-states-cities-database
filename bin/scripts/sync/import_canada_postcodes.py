#!/usr/bin/env python3
"""Canada -> contributions/postcodes/CA.json importer for issue #1039.

Source data
-----------
The community ``inkjet/pypostalcode`` repository (MIT-licensed) ships
1,645 Canada Post Forward Sortation Areas (FSAs — the 3-character
prefix of a Canadian postcode) with FSA centroid lat/lng. The data is
sourced from the Statistics Canada *Forward Sortation Area Boundary
File, 2011 Census*.

    fsa,city,province,latitude,longitude,timezone,dst
    T0A,Eastern Alberta (St. Paul),Alberta,53.9225,-111.0585,-7,1

Source URL: https://raw.githubusercontent.com/inkjet/pypostalcode/master/ca_postalcodes.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Resolves state FK via direct province-name match + 2-entry alias
   map (source 'Northwest Territory' -> CSC 'Northwest Territories',
   source 'Nunavut Territory' -> CSC 'Nunavut').
3. Emits one record per FSA with FSA centroid lat/lng + source's
   English locality description.
4. Writes contributions/postcodes/CA.json idempotently.

Why FSA-only (not full 6-char)
------------------------------
Canada Post's bulk PAF feed (~870k full 6-char codes) is paywalled.
Available public mirrors are either GeoNames-derived (excluded by
maintainer instruction) or unlicensed scrapes of geocoder.ca.
inkjet's StatsCan-sourced FSA list is the cleanest publicly
redistributable Canada postcode data.

Regex fix
---------
Before this PR, countries.json had CA regex
``^([ABCE...]\\d[ABCE...]) ?(\\d[ABCE...]\\d)$`` (full 6-char
required). Updated to make the LDU portion optional so 3-char FSAs
also validate:
    ^([ABCE...]\\d[ABCE...])(?: ?(\\d[ABCE...]\\d))?$

License & attribution
---------------------
- Source: inkjet/pypostalcode (MIT)
- Upstream: Statistics Canada FSA Boundary File 2011 Census
  (Statistics Canada Open Licence — free redistribution permitted)
- Each row: ``source: "statscan-fsa-via-inkjet"``

Usage
-----
    python3 bin/scripts/sync/import_canada_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/inkjet/pypostalcode/"
    "master/ca_postalcodes.csv"
)

# Source province name -> CSC name. Only entries where direct match fails.
PROVINCE_ALIASES: Dict[str, str] = {
    "Northwest Territory": "Northwest Territories",
    "Nunavut Territory": "Nunavut",
}


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    ca_country = next((c for c in countries if c.get("iso2") == "CA"), None)
    if ca_country is None:
        print("ERROR: CA not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ca_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ca_states = [s for s in states if s.get("country_id") == ca_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"]: s for s in ca_states if s.get("name")}
    print(
        f"Country: Canada (id={ca_country['id']}); states indexed: {len(ca_states)}"
    )

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_province: Dict[str, int] = {}

    for row in rows:
        code = (row.get("fsa") or "").strip().upper()
        if not code:
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        province = (row.get("province") or "").strip()
        csc_name = PROVINCE_ALIASES.get(province, province)
        state = state_by_name.get(csc_name)
        if state is None:
            unknown_province[province] = unknown_province.get(province, 0) + 1
            skipped_no_state += 1

        city = (row.get("city") or "").strip()
        lat = (row.get("latitude") or "").strip()
        lon = (row.get("longitude") or "").strip()

        key = (code, city.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ca_country["id"]),
            "country_code": "CA",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if city:
            record["locality_name"] = city
        if lat:
            record["latitude"] = lat
        if lon:
            record["longitude"] = lon
        record["type"] = "fsa"
        record["source"] = "statscan-fsa-via-inkjet"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_province:
        print("Unknown province values (not in PROVINCE_ALIASES):")
        for p, n in sorted(unknown_province.items(), key=lambda x: -x[1]):
            print(f"  {p!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/CA.json"
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
