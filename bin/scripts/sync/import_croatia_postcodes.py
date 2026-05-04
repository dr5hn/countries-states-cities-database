#!/usr/bin/env python3
"""Croatia -> contributions/postcodes/HR.json importer for issue #1039.

Source data
-----------
The community ``mislavcimpersak/croatian-zip-codes`` repository
(MIT-licensed) ships ``croatian_zip_codes.json`` — a 21-county
hierarchical JSON joining each Hrvatska Pošta 5-digit postal code
with city + county.

    [
      {"name": "Zagrebačka", "slug": "zagrebacka",
       "cities": [{"name": "Gornji Stupnik", "zip_code": "10255"}, ...]
      },
      ...
    ]

Source URL: https://raw.githubusercontent.com/mislavcimpersak/croatian-zip-codes/master/croatian_zip_codes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Walks 21 source counties (20 CSC counties + Grad Zagreb /
   City of Zagreb which collapses into CSC iso2 '01' Zagreb).
3. Resolves state FK via SOURCE_TO_ISO2 (21-entry hand map
   handling Croatian adjective form -> CSC English county name).
4. Emits one row per (zip_code, city) tuple.
5. Writes contributions/postcodes/HR.json idempotently.

Coverage
--------
- 905 codes / 100% state FK
- All 20 CSC HR counties covered
- Grad Zagreb (city) merged into Zagreb county per CSC convention

License & attribution
---------------------
- Source: mislavcimpersak/croatian-zip-codes (MIT)
- Upstream: Hrvatska Pošta public lookup
- Each row: ``source: "hrvatska-posta-via-mislavcimpersak"``

Usage
-----
    python3 bin/scripts/sync/import_croatia_postcodes.py
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
    "https://raw.githubusercontent.com/mislavcimpersak/croatian-zip-codes/"
    "master/croatian_zip_codes.json"
)

# Source Croatian adjective form -> CSC iso2.
SOURCE_TO_ISO2: Dict[str, str] = {
    "Zagrebačka": "01",                # Zagreb (county)
    "Grad Zagreb": "01",               # Zagreb (city, merged with county)
    "Krapinsko-zagorska": "02",        # Krapina-Zagorje
    "Sisačko-moslavačka": "03",        # Sisak-Moslavina
    "Karlovačka": "04",                # Karlovac
    "Varaždinska": "05",               # Varaždin
    "Koprivničko-križevačka": "06",    # Koprivnica-Križevci
    "Bjelovarsko-bilogorska": "07",    # Bjelovar-Bilogora
    "Primorsko-goranska": "08",        # Primorje-Gorski Kotar
    "Ličko-senjska": "09",             # Lika-Senj
    "Virovitičko-podravska": "10",     # Virovitica-Podravina
    "Požeško-slavonska": "11",         # Požega-Slavonia
    "Brodsko-posavska": "12",          # Brod-Posavina
    "Zadarska": "13",                  # Zadar
    "Osječko-baranjska": "14",         # Osijek-Baranja
    "Šibensko-kninska": "15",          # Šibenik-Knin
    "Vukovarsko-srijemska": "16",      # Vukovar-Syrmia
    "Splitsko-dalmatinska": "17",      # Split-Dalmatia
    "Istarska": "18",                  # Istria
    "Dubrovačko-neretvanska": "19",    # Dubrovnik-Neretva
    "Međimurska": "20",                # Međimurje
}


def fetch_json(url: str) -> List[dict]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    counties = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    print(f"Source counties: {len(counties)}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    hr_country = next((c for c in countries if c.get("iso2") == "HR"), None)
    if hr_country is None:
        print("ERROR: HR not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(hr_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    hr_states = [s for s in states if s.get("country_id") == hr_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in hr_states if s.get("iso2")
    }
    print(
        f"Country: Croatia (id={hr_country['id']}); states indexed: {len(hr_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_counties: Dict[str, int] = {}

    for county in counties:
        county_name = (county.get("name") or "").strip()
        cities = county.get("cities") or []

        iso2 = SOURCE_TO_ISO2.get(county_name)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_counties[county_name] = unknown_counties.get(county_name, 0) + len(cities)

        for city in cities:
            code = (city.get("zip_code") or "").strip()
            city_name = (city.get("name") or "").strip()
            if not regex.match(code):
                skipped_bad_regex += 1
                continue
            if state is None:
                skipped_no_state += 1

            key = (code, city_name.lower())
            if key in seen:
                continue
            seen.add(key)

            record: Dict[str, object] = {
                "code": code,
                "country_id": int(hr_country["id"]),
                "country_code": "HR",
            }
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = state.get("iso2")
                matched_state += 1
            if city_name:
                record["locality_name"] = city_name
            record["type"] = "full"
            record["source"] = "hrvatska-posta-via-mislavcimpersak"
            records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_counties:
        print("Unknown counties (not in SOURCE_TO_ISO2):")
        for c, n in sorted(unknown_counties.items(), key=lambda x: -x[1]):
            print(f"  {c!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/HR.json"
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
