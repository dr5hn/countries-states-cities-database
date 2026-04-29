#!/usr/bin/env python3
"""Norway Bring -> contributions/postcodes/NO.json importer for issue #1039.

Source data
-----------
Bring (Posten Norge) publishes the canonical Postnummerregister as a free
TSV download. The file is ISO-8859-1 (Windows-1252) encoded with 5 columns:

  postnummer | poststed | kommunenr | kommune | kategori (P/B/S/...)

  https://www.bring.no/postnummerregister-ansi.txt

What this script does
---------------------
1. Reads the TSV (latin-1 encoded, tab-separated, no header)
2. Picks one canonical record per unique postcode (first by row order —
   the file is naturally sorted by postcode and the first occurrence is
   the canonical "post place")
3. Resolves county/state via the first 2 digits of the kommunenr
   (Norwegian kommune codes encode the county in their first 2 digits;
   this is the official Statistics Norway convention)
4. Writes contributions/postcodes/NO.json

License
-------
- Source: Bring / Posten Norge (publicly downloadable, no formal licence
  text — Norwegian government policy treats this as open data)
- Each row: source: "bring"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://www.bring.no/postnummerregister-ansi.txt',
      '/tmp/no_postnumre.txt')"

    python3 bin/scripts/sync/import_norway_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/no_postnumre.txt")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    no = next((c for c in countries if c.get("iso2") == "NO"), None)
    if no is None:
        print("ERROR: NO not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    no_states = [s for s in states if s.get("country_id") == no["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in no_states if s.get("iso2")}
    print(f"Country: Norway (id={no['id']}); states indexed: {len(state_by_iso2)}")

    seen: set = set()
    records: List[dict] = []
    matched_state = 0
    bad = 0
    with src.open(encoding="latin-1", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if len(row) < 4:
                bad += 1
                continue
            code, poststed, kommunenr, kommune = (row[0] or "").strip(), (row[1] or "").strip(), (row[2] or "").strip(), (row[3] or "").strip()
            if not code or not code.isdigit() or len(code) != 4:
                bad += 1
                continue
            if code in seen:
                continue
            seen.add(code)

            record = {
                "code": code,
                "country_id": int(no["id"]),
                "country_code": "NO",
            }
            # Norwegian kommune codes: first 2 digits = county (fylke) code.
            # Statistics Norway / SSB convention.
            if len(kommunenr) == 4 and kommunenr.isdigit():
                county_iso2 = kommunenr[:2]
                state = state_by_iso2.get(county_iso2)
                if state is not None:
                    record["state_id"] = int(state["id"])
                    record["state_code"] = county_iso2
                    matched_state += 1

            if poststed:
                # Source data is upper-case ("OSLO"); keep as-is — Norwegian
                # poststed names are formally rendered in upper case on mail
                record["locality_name"] = poststed
            record["type"] = "full"
            record["source"] = "bring"
            records.append(record)

    records.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    print(f"Skipped malformed:  {bad:,}")
    print(f"Records:            {len(records):,}")
    print(f"  with state:       {matched_state:,} ({matched_state*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/NO.json"
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        seen_pairs = {(r["code"], (r.get("locality_name") or "").lower()) for r in existing}
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in seen_pairs:
                merged.append(r)
                seen_pairs.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = records

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_kb = target.stat().st_size / 1024
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
