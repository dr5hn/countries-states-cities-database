#!/usr/bin/env python3
"""Iceland -> contributions/postcodes/IS.json importer for issue #1039.

Source data
-----------
The community-maintained ``sveinbjornt/iceaddr`` Python package embeds
the canonical Icelandic postcode metadata (postcode -> place + region)
under MIT licence. The data is statically defined in:

  https://raw.githubusercontent.com/sveinbjornt/iceaddr/master/src/iceaddr/postcodes.py

Each entry has:
  lysing       (description, e.g. "Miðborg")
  stadur_nf    (place name nominative, e.g. "Reykjavík")
  svaedi_nf    (region name, e.g. "Höfuðborgarsvæðið")

What this script does
---------------------
1. Reads the iceaddr postcodes.py module from /tmp (downloaded out of band)
2. Iterates the POSTCODES dict
3. Resolves region via postcode prefix to states.json iso2 1-8
4. Writes contributions/postcodes/IS.json

Why prefix-based region resolution
----------------------------------
Iceland Post organises postcodes geographically by 1xx-9xx prefixes,
which align with the 8 statistical regions in states.json with one
caveat: 9xx codes (Eastern coast + Vestmannaeyjar) split between
Eastern (7) and Southern (8). The prefix map below matches Statistics
Iceland's 8-region NUTS-3 boundaries.

License & attribution
---------------------
- Source: iceaddr / Sveinbjorn Thordarson (MIT) embedding postdata
  from Pósturinn (Iceland Post)
- Each row: source: "iceaddr"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://raw.githubusercontent.com/sveinbjornt/iceaddr/master/src/iceaddr/postcodes.py',
      '/tmp/iceaddr_postcodes.py')"

    python3 bin/scripts/sync/import_iceland_postcodes.py
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Postcode prefix range -> state.iso2 in CSC dataset
def resolve_region(code: int) -> Optional[str]:
    if 100 <= code <= 299:
        return "1"  # Capital (Höfuðborgarsvæðið)
    if 300 <= code <= 399:
        return "3"  # Western (Vesturland)
    if 400 <= code <= 499:
        return "4"  # Westfjords
    if 500 <= code <= 599:
        return "5"  # Northwestern
    if 600 <= code <= 699:
        return "6"  # Northeastern
    if 700 <= code <= 799:
        return "7"  # Eastern
    if 800 <= code <= 899:
        return "8"  # Southern
    # 9xx: split between Eastern (Hornafjörður 780/900-902, Höfn) and
    # Southern (Vestmannaeyjar 900-902 historically). Default Southern
    # since Vestmannaeyjar dominates the 9xx residential range.
    if 900 <= code <= 999:
        return "8"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/iceaddr_postcodes.py")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    # Dynamically import the iceaddr postcodes module
    spec = importlib.util.spec_from_file_location("iceaddr_postcodes", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    postcodes_data = mod.POSTCODES

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    is_country = next((c for c in countries if c.get("iso2") == "IS"), None)
    if is_country is None:
        print("ERROR: IS not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    is_states = [s for s in states if s.get("country_id") == is_country["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in is_states if s.get("iso2")}
    print(f"Country: Iceland (id={is_country['id']}); states indexed: {len(state_by_iso2)}")

    print(f"Postcodes in source: {len(postcodes_data):,}")

    records: List[dict] = []
    matched_state = 0
    for code_int in sorted(postcodes_data.keys()):
        meta = postcodes_data[code_int]
        # IS regex requires 3-digit string
        code = f"{int(code_int):03d}"
        record = {
            "code": code,
            "country_id": int(is_country["id"]),
            "country_code": "IS",
        }
        iso2 = resolve_region(int(code_int))
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
        # Locality: use stadur_nf with optional lysing suffix when present
        place = meta.get("stadur_nf", "").strip()
        lysing = meta.get("lysing", "").strip()
        if place and lysing and place.lower() != lysing.lower():
            locality = f"{place}, {lysing}"
        else:
            locality = place or lysing
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "iceaddr"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/IS.json"
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
