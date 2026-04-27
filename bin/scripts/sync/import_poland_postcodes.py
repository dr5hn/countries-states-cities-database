#!/usr/bin/env python3
"""Poland -> contributions/postcodes/PL.json importer for issue #1039.

Source data
-----------
The community-maintained ``mberezinski/kody-pocztowe-geo`` repo
redistributes Polish postcode data with coordinates and voivodeship.

  https://github.com/mberezinski/kody-pocztowe-geo

CSV format (semicolon-delimited, UTF-8 BOM):
  Country;PostCode;Longitude;Latitude;Address;City;County;Voivodeship;CityBasedAproximation

~22k records.

What this script does
---------------------
1. Reads the CSV (UTF-8 with BOM, semicolon-delimited)
2. Picks one canonical record per unique postcode (first city alphabetical)
3. Resolves voivodeship via Polish-name -> CSC iso2 alias map
4. Writes contributions/postcodes/PL.json

License & attribution
---------------------
- Mirror: github.com/mberezinski/kody-pocztowe-geo
- Each row: source: "kody-pocztowe-geo"
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Polish "Województwo X" -> CSC state.iso2
VOIVODESHIP_TO_ISO2: Dict[str, str] = {
    "Województwo dolnośląskie":         "02",  # Lower Silesia
    "Województwo kujawsko-pomorskie":   "04",  # Kuyavia-Pomerania
    "Województwo lubelskie":            "06",  # Lublin
    "Województwo lubuskie":             "08",  # Lubusz
    "Województwo łódzkie":              "10",  # Łódź
    "Województwo małopolskie":          "12",  # Lesser Poland
    "Województwo mazowieckie":          "14",  # Mazovia
    "Województwo opolskie":             "16",  # Opole (states.json names "Upper Silesia")
    "Województwo podkarpackie":         "18",  # Subcarpathia
    "Województwo podlaskie":            "20",  # Podlaskie
    "Województwo pomorskie":            "22",  # Pomerania
    "Województwo śląskie":              "24",  # Silesia
    "Województwo świętokrzyskie":       "26",  # Holy Cross / Świętokrzyskie
    "Województwo warmińsko-mazurskie":  "28",  # Warmia-Masuria
    "Województwo wielkopolskie":        "30",  # Greater Poland
    "Województwo zachodniopomorskie":   "32",  # West Pomerania
}


def parse_coord(v: str) -> Optional[str]:
    if not v or v.strip().upper() == "NULL":
        return None
    try:
        f = float(v)
        if abs(f) > 180:
            return None
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/pl_kody.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    pl = next((c for c in countries if c.get("iso2") == "PL"), None)
    if pl is None:
        print("ERROR: PL not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    pl_states = [s for s in states if s.get("country_id") == pl["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in pl_states if s.get("iso2")}
    print(f"Country: Poland (id={pl['id']}); states indexed: {len(state_by_iso2)}")

    by_code: Dict[str, List[dict]] = {}
    bad = 0
    with src.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            code = (row.get("PostCode") or "").strip()
            if not code:
                bad += 1
                continue
            by_code.setdefault(code, []).append(row)
    print(f"Skipped malformed: {bad:,}")
    print(f"Unique postcodes:  {len(by_code):,}")

    records: List[dict] = []
    matched_state = 0
    matched_coord = 0
    for code in sorted(by_code):
        rows = sorted(by_code[code], key=lambda r: (r.get("City") or "").upper())
        chosen = rows[0]
        record = {
            "code": code,
            "country_id": int(pl["id"]),
            "country_code": "PL",
        }
        voiv = (chosen.get("Voivodeship") or "").strip()
        iso2 = VOIVODESHIP_TO_ISO2.get(voiv)
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
        city = (chosen.get("City") or "").strip()
        if city:
            record["locality_name"] = city
        record["type"] = "full"
        lat = parse_coord(chosen.get("Latitude") or "")
        lng = parse_coord(chosen.get("Longitude") or "")
        if lat is not None and lng is not None:
            record["latitude"] = lat
            record["longitude"] = lng
            matched_coord += 1
        record["source"] = "kody-pocztowe-geo"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")
    print(f"  with coords:  {matched_coord:,} ({matched_coord*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PL.json"
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
