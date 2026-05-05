#!/usr/bin/env python3
"""Faroe Islands -> contributions/postcodes/FO.json importer for issue #1039.

Source data
-----------
The Faroese Environment Agency (Umhvørvisstovan) publishes the
official address registry via an ArcGIS REST endpoint. Per
OpenAddresses' fo/countrywide.json source definition, the layer
``adressur/us_adr_husanr`` carries 26,301 addresses, each with
zip + city + municipality.

What this script does
---------------------
1. Issues a single ArcGIS REST groupBy query for distinct
   (zip, city, municipality) tuples — returns 117 unique postcodes.
2. Resolves state FK by mapping each Faroese kommuna (municipality)
   to one of CSC's 6 sýslur (regions) via MUNI_TO_ISO2.
3. Emits one row per postcode with municipality + city as locality.
4. Writes contributions/postcodes/FO.json idempotently.

Source URL: https://gis.us.fo/arcgis/rest/services/adressur/us_adr_husanr/MapServer/0

State FK strategy
-----------------
Source's ``municipality`` field uses the Faroese genitive form
(e.g. 'Tórshavnar', 'Klaksvíkar'). 22-entry MUNI_TO_ISO2 maps each
to one of 6 CSC FO regions (sýslur):
- Streymoy (ST): Tórshavnar, Vestmanna, Kvívíkar, Sunda
- Eysturoy (EY): Eiðis, Eystur, Runavíkar, Sjóvar, Fuglafjarðar, Nes
- Sandoy (SA): Sands, Húsavíkar, Skálavíkar, Skopunar, Skúvoyar
- Vágar (VA): Sørvágs, Vága
- Northern Isles (NO): Klaksvíkar, Kunoyar, Hvannasunds, Fugloyar,
  Viðareiðis
- Suðuroy (SU): Tvøroyrar, Hvalbiar, Fámjins, Vágs, Sumbiar, Hovs,
  Porkeris

License & attribution
---------------------
- Source: Faroese Environment Agency (Umhvørvisstovan)
- License: Føroyakort terms — free attribution; share-alike: false
- Each row: ``source: "umhvorvisstovan-fo-arcgis"``

Tier 4 per #1039 license-tier policy (Open Government / NDSAP-style).

Usage
-----
    python3 bin/scripts/sync/import_faroe_islands_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://gis.us.fo/arcgis/rest/services/adressur/us_adr_husanr/MapServer/0/query"
)

# Source municipality (Faroese genitive form) -> CSC iso2.
MUNI_TO_ISO2: Dict[str, str] = {
    # Streymoy (ST)
    "Tórshavnar": "ST",
    "Vestmanna": "ST",
    "Kvívíkar": "ST",
    "Sunda": "ST",
    # Eysturoy (EY)
    "Eiðis": "EY",
    "Eystur": "EY",
    "Runavíkar": "EY",
    "Sjóvar": "EY",
    "Fuglafjarðar": "EY",
    "Nes": "EY",
    # Sandoy (SA)
    "Sands": "SA",
    "Húsavíkar": "SA",
    "Skálavíkar": "SA",
    "Skopunar": "SA",
    "Skúvoyar": "SA",
    # Vágar (VA)
    "Sørvágs": "VA",
    "Vága": "VA",
    # Northern Isles (NO)
    "Klaksvíkar": "NO",
    "Kunoyar": "NO",
    "Hvannasunds": "NO",
    "Fugloyar": "NO",
    "Viðareiðis": "NO",
    # Suðuroy (SU)
    "Tvøroyrar": "SU",
    "Hvalbiar": "SU",
    "Fámjins": "SU",
    "Vágs": "SU",
    "Sumbiar": "SU",
    "Hovs": "SU",
    "Porkeris": "SU",
}


def fetch_distinct_postcodes() -> List[Dict]:
    """Query ArcGIS REST endpoint for distinct (zip, city, municipality)."""
    params = {
        "where": "zip>0",
        "outFields": "zip,city,municipality",
        "groupByFieldsForStatistics": "zip,city,municipality",
        "outStatistics": json.dumps(
            [
                {
                    "statisticType": "count",
                    "onStatisticField": "objectid",
                    "outStatisticFieldName": "cnt",
                }
            ]
        ),
        "f": "json",
        "resultRecordCount": "2000",
    }
    url = f"{SOURCE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data.get("features", [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"Fetching {SOURCE_URL}")
    features = fetch_distinct_postcodes()
    print(f"Source groups: {len(features)}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    fo_country = next((c for c in countries if c.get("iso2") == "FO"), None)
    if fo_country is None:
        print("ERROR: FO not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(fo_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    fo_states = [s for s in states if s.get("country_id") == fo_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in fo_states if s.get("iso2")
    }
    print(
        f"Country: Faroe Islands (id={fo_country['id']}); "
        f"states indexed: {len(fo_states)}"
    )

    # Pick first-seen city/muni per zip (groups may have multiple cities per zip)
    by_zip: Dict[str, Dict] = {}
    for f in features:
        a = f.get("attributes", {})
        z = str(a.get("zip", "")).zfill(3)
        if not z or z == "000":
            continue
        if z in by_zip:
            continue
        by_zip[z] = a

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_munis: Dict[str, int] = {}

    for code, a in sorted(by_zip.items()):
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        muni = (a.get("municipality") or "").strip()
        city = (a.get("city") or "").strip()
        iso2 = MUNI_TO_ISO2.get(muni)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_munis[muni] = unknown_munis.get(muni, 0) + 1
            skipped_no_state += 1

        # Locality: city, fall back to muni
        locality = city or muni

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(fo_country["id"]),
            "country_code": "FO",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "umhvorvisstovan-fo-arcgis"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_munis:
        print("Unknown municipalities (not in MUNI_TO_ISO2):")
        for m, n in sorted(unknown_munis.items(), key=lambda x: -x[1]):
            print(f"  {m!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/FO.json"
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
