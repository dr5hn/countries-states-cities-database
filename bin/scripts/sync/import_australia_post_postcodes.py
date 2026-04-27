#!/usr/bin/env python3
"""Australia Post -> contributions/postcodes/AU.json importer for issue #1039.

Source data
-----------
The community-maintained Matthew Proctor archive is the standard
redistributable mirror of Australia Post's open-data postcode list,
published under CC-BY 4.0 attribution to Australia Post:

  https://github.com/matthewproctor/australianpostcodes

The CSV has ~18,500 rows representing localities; ~3,175 unique postcodes
spread across the 8 Australian states/territories.

What this script does
---------------------
1. Reads the CSV (UTF-8, header row)
2. Picks ONE canonical record per unique postcode (first alphabetical
   locality name — gives a stable primary that future curated PRs can
   override per-row)
3. Resolves country_id (AU) and state_id by direct iso2 match
   (CSV uses ACT/NSW/NT/QLD/SA/TAS/VIC/WA — same codes as states.json)
4. Carries forward latitude/longitude when present
5. Writes contributions/postcodes/AU.json
6. Idempotent merge with existing curated rows

License & attribution
---------------------
- Upstream source: Australia Post (CC-BY 4.0)
- Mirror: github.com/matthewproctor/australianpostcodes
- Each generated row records source: "australia-post"

Usage
-----
    curl -L -o /tmp/au_postcodes.csv \\
      https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv

    python3 bin/scripts/sync/import_australia_post_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def parse_coord(v: str) -> Optional[str]:
    if not v or not v.strip():
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
    parser.add_argument("--input", default="/tmp/au_postcodes.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"ERROR: input not found: {csv_path}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    au = next((c for c in countries if c.get("iso2") == "AU"), None)
    if au is None:
        print("ERROR: AU not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    au_states = [s for s in states if s.get("country_id") == au["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in au_states if s.get("iso2")}

    print(f"Country: Australia (id={au['id']}); states: {len(au_states)}")

    # First pass: group rows by postcode, then pick a canonical one per postcode
    by_postcode: Dict[str, List[dict]] = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("postcode") or "").strip()
            if not code or not code.isdigit() or len(code) != 4:
                continue
            by_postcode.setdefault(code, []).append(row)

    # Sort each postcode's rows by locality name; first wins
    records: List[dict] = []
    matched_state = 0
    matched_coord = 0
    for code in sorted(by_postcode):
        rows = sorted(by_postcode[code], key=lambda r: (r.get("locality") or "").upper())
        chosen = rows[0]
        record = {
            "code": code,
            "country_id": int(au["id"]),
            "country_code": "AU",
        }
        st_iso = (chosen.get("state") or "").strip().upper()
        state = state_by_iso2.get(st_iso)
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = st_iso
            matched_state += 1
        locality = (chosen.get("locality") or "").strip()
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        lat = parse_coord(chosen.get("lat") or "")
        lng = parse_coord(chosen.get("long") or "")
        if lat is not None and lng is not None:
            record["latitude"] = lat
            record["longitude"] = lng
            matched_coord += 1
        record["source"] = "australia-post"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")
    print(f"  with coords:  {matched_coord:,} ({matched_coord*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/AU.json"
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
