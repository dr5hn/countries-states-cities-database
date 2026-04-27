#!/usr/bin/env python3
"""Belgium -> contributions/postcodes/BE.json importer for issue #1039.

Source data
-----------
The community-maintained ``jief/zipcode-belgium`` repo redistributes a
clean Belgian postcode + locality + coordinates dataset derived from
bpost open data:

  https://github.com/jief/zipcode-belgium

The JSON has 2,757 city-postcode pairs covering 1,145 unique postcodes.

What this script does
---------------------
1. Reads zipcode-belgium.json (UTF-8)
2. Picks ONE canonical city per unique zip (first alphabetical)
3. Resolves state by mapping the postcode prefix to province via the
   standard Belgian convention (1xxx Brussels/Brabant, 2xxx Antwerp,
   etc.) — the source has no state field, so this is the only path
4. Writes contributions/postcodes/BE.json

Postal prefix -> province
-------------------------
Belgium's province assignment by postal range is well-documented:
  1000-1299  BRU (Brussels-Capital)
  1300-1499  WBR (Walloon Brabant)
  1500-1999  VBR (Flemish Brabant)
  2000-2999  VAN (Antwerp)
  3000-3499  VBR (Flemish Brabant)  - second Brabant range
  3500-3999  VLI (Limburg)
  4000-4999  WLG (Liège)
  5000-5999  WNA (Namur)
  6000-6599  WHT (Hainaut)         - Charleroi area
  6600-6999  WLX (Luxembourg)
  7000-7999  WHT (Hainaut)
  8000-8999  VWV (West Flanders)
  9000-9999  VOV (East Flanders)

License & attribution
---------------------
- Upstream: bpost open data
- Mirror: github.com/jief/zipcode-belgium
- Each row: source: "bpost"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://raw.githubusercontent.com/jief/zipcode-belgium/master/zipcode-belgium.json',
      '/tmp/be_zipcodes.json')"

    python3 bin/scripts/sync/import_belgium_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# (low, high, iso2) inclusive ranges; first match wins
PREFIX_RANGES = [
    (1000, 1299, "BRU"),  # Brussels-Capital
    (1300, 1499, "WBR"),  # Walloon Brabant
    (1500, 1999, "VBR"),  # Flemish Brabant (1)
    (2000, 2999, "VAN"),  # Antwerp
    (3000, 3499, "VBR"),  # Flemish Brabant (2)
    (3500, 3999, "VLI"),  # Limburg
    (4000, 4999, "WLG"),  # Liège
    (5000, 5999, "WNA"),  # Namur
    (6000, 6599, "WHT"),  # Hainaut (Charleroi area)
    (6600, 6999, "WLX"),  # Luxembourg
    (7000, 7999, "WHT"),  # Hainaut
    (8000, 8999, "VWV"),  # West Flanders
    (9000, 9999, "VOV"),  # East Flanders
]


def resolve_state(code: str, state_by_iso2: Dict[str, dict]) -> Optional[dict]:
    if not code or not code.isdigit() or len(code) != 4:
        return None
    n = int(code)
    for low, high, iso2 in PREFIX_RANGES:
        if low <= n <= high:
            return state_by_iso2.get(iso2)
    return None


def parse_coord(v) -> Optional[str]:
    if v is None:
        return None
    try:
        f = float(v)
        if abs(f) > 180:
            return None
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/be_zipcodes.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    be = next((c for c in countries if c.get("iso2") == "BE"), None)
    if be is None:
        print("ERROR: BE not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    be_states = [s for s in states if s.get("country_id") == be["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in be_states if s.get("iso2")}
    print(f"Country: Belgium (id={be['id']}); states indexed: {len(state_by_iso2)}")

    rows = json.load(src.open(encoding="utf-8"))

    by_zip: Dict[str, List[dict]] = {}
    for row in rows:
        code = (row.get("zip") or "").strip()
        if not code or not code.isdigit() or len(code) != 4:
            continue
        by_zip.setdefault(code, []).append(row)
    print(f"Unique zips: {len(by_zip):,}")

    records: List[dict] = []
    matched_state = 0
    matched_coord = 0
    for code in sorted(by_zip):
        chosen = sorted(by_zip[code], key=lambda r: (r.get("city") or "").upper())[0]
        record = {
            "code": code,
            "country_id": int(be["id"]),
            "country_code": "BE",
        }
        state = resolve_state(code, state_by_iso2)
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2") or ""
            matched_state += 1
        city = (chosen.get("city") or "").strip()
        if city:
            record["locality_name"] = city
        record["type"] = "full"
        lat = parse_coord(chosen.get("lat"))
        lng = parse_coord(chosen.get("lng"))
        if lat is not None and lng is not None:
            record["latitude"] = lat
            record["longitude"] = lng
            matched_coord += 1
        record["source"] = "bpost"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")
    print(f"  with coords:  {matched_coord:,} ({matched_coord*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/BE.json"
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
    size_kb = target.stat().st_size / 1024
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
