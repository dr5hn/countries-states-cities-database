#!/usr/bin/env python3
"""Portugal CTT -> contributions/postcodes/PT.json importer for issue #1039.

Source data
-----------
The community-maintained ``centraldedados/codigos_postais`` repo
redistributes CTT's official Portuguese postcode database under an open
data licence. The CSV has 326,331 street-level rows representing
197,024 unique full postcodes (``####-###``).

  https://github.com/centraldedados/codigos_postais

Source columns include:
  cod_distrito | cod_concelho | cod_localidade | nome_localidade |
  ... (street fields) ... |
  num_cod_postal | ext_cod_postal | desig_postal

What this script does
---------------------
1. Reads codigos_postais.csv (UTF-8)
2. Picks ONE canonical record per unique postcode (first nome_localidade
   alphabetically) — many rows share the same postcode (one per address
   range) and Tier 4 schema is one-row-per-code
3. Emits codes in the canonical "####-###" form (regex requires it)
4. Resolves state by mapping cod_distrito (2-digit district code) to
   states.json iso2:
     01-18 -> direct mainland district match
     31-32 -> 30 (Madeira autonomous region)
     41-49 -> 20 (Açores autonomous region)
5. Writes contributions/postcodes/PT.json (~197k records)

License & attribution
---------------------
- Upstream: CTT (Correios de Portugal) via Central de Dados open-data project
- Mirror: github.com/centraldedados/codigos_postais
- Each row: source: "ctt"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://raw.githubusercontent.com/centraldedados/codigos_postais/master/data/codigos_postais.csv',
      '/tmp/pt_codigos.csv')"

    python3 bin/scripts/sync/import_portugal_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# CSV cod_distrito -> state.iso2 in this dataset's PT states.
# Mainland districts 01-18 use their literal 2-digit codes.
# Madeira autonomous region uses CSV codes 31-32 -> states iso2 "30".
# Açores autonomous region uses CSV codes 41-49 -> states iso2 "20".
def csv_district_to_iso2(csv_district: str) -> Optional[str]:
    if not csv_district or len(csv_district) != 2 or not csv_district.isdigit():
        return None
    n = int(csv_district)
    if 1 <= n <= 18:
        return csv_district  # direct mainland match (already padded)
    if 31 <= n <= 32:
        return "30"  # Madeira
    if 41 <= n <= 49:
        return "20"  # Açores
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/pt_codigos.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    pt = next((c for c in countries if c.get("iso2") == "PT"), None)
    if pt is None:
        print("ERROR: PT not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    pt_states = [s for s in states if s.get("country_id") == pt["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in pt_states if s.get("iso2")}
    print(f"Country: Portugal (id={pt['id']}); states indexed: {len(state_by_iso2)}")

    # First pass: stream CSV; for each unique postcode, keep the first
    # alphabetical desig_postal/locality + its district code. Streaming
    # keeps memory bounded for the 197k unique codes.
    chosen: Dict[str, dict] = {}
    bad = 0
    with src.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cp = (row.get("num_cod_postal") or "").strip()
            ext = (row.get("ext_cod_postal") or "").strip()
            if len(cp) != 4 or len(ext) != 3 or not cp.isdigit() or not ext.isdigit():
                bad += 1
                continue
            code = f"{cp}-{ext}"
            district = (row.get("cod_distrito") or "").strip()
            locality = (row.get("desig_postal") or row.get("nome_localidade") or "").strip()
            existing = chosen.get(code)
            # Pick the alphabetically first desig_postal so the canonical row is deterministic
            if existing is None or (locality and locality.upper() < (existing.get("locality") or "").upper()):
                chosen[code] = {"district": district, "locality": locality}

    print(f"Skipped malformed rows: {bad:,}")
    print(f"Unique postcodes:       {len(chosen):,}")

    records: List[dict] = []
    matched_state = 0
    for code in sorted(chosen):
        meta = chosen[code]
        record = {
            "code": code,
            "country_id": int(pt["id"]),
            "country_code": "PT",
        }
        iso2 = csv_district_to_iso2(meta["district"])
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
        if meta["locality"]:
            record["locality_name"] = meta["locality"]
        record["type"] = "full"
        record["source"] = "ctt"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PT.json"
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
