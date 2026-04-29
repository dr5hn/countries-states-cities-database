#!/usr/bin/env python3
"""Italy CAP -> contributions/postcodes/IT.json importer for issue #1039.

Source data
-----------
The community-maintained ``matteocontrini/comuni-json`` archive is the
canonical redistribution of Istat's official Italian commune list with
postal codes (CAP). It carries Istat data under the original CC-BY 3.0
attribution (Istat licensing).

  https://github.com/matteocontrini/comuni-json

The JSON has 7,904 commune records, each with:
- nome (commune name, mixed-case)
- sigla (2-letter province ISO 3166-2:IT code, e.g. RM, MI, NA)
- cap (array of postal codes — large cities have many)
- regione, provincia, codiceCatastale, popolazione

About 4,678 unique CAPs across all comuni.

What this script does
---------------------
1. Reads comuni.json (UTF-8)
2. Expands each commune's cap[] array, one record per (cap, commune)
3. Picks ONE canonical commune per unique CAP (first alphabetical)
   — large cities like Rome/Milan have ~50-80 CAPs each, but each CAP
   points to one neighbourhood/zone within a single commune
4. Resolves state_id by mapping commune.sigla to state.iso2 directly
   (Italy's 2-letter province codes match exactly: RM = Rome, MI = Milan)
5. Writes contributions/postcodes/IT.json

License & attribution
---------------------
- Upstream source: Istat (CC-BY 3.0)
- Mirror: github.com/matteocontrini/comuni-json
- Each row: source: "istat"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json',
      '/tmp/it_comuni.json')"

    python3 bin/scripts/sync/import_italy_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/it_comuni.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    it = next((c for c in countries if c.get("iso2") == "IT"), None)
    if it is None:
        print("ERROR: IT not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    it_states = [s for s in states if s.get("country_id") == it["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in it_states if s.get("iso2")}

    # Aosta is sigla "AO" in the source, but states.json treats it as the
    # "Aosta Valley" autonomous region with iso2 "23" instead of a standard
    # province. Bridge it explicitly.
    if "23" in state_by_iso2 and "AO" not in state_by_iso2:
        state_by_iso2["AO"] = state_by_iso2["23"]

    print(f"Country: Italy (id={it['id']}); states indexed by iso2: {len(state_by_iso2)}")

    comuni = json.load(src.open(encoding="utf-8"))

    # Expand to one row per (cap, commune); group by cap; pick first commune alphabetically.
    by_cap: Dict[str, List[dict]] = {}
    for c in comuni:
        nome = (c.get("nome") or "").strip()
        sigla = (c.get("sigla") or "").strip().upper()
        for cap in c.get("cap", []):
            cap = (cap or "").strip()
            if not cap or not cap.isdigit() or len(cap) != 5:
                continue
            by_cap.setdefault(cap, []).append({"nome": nome, "sigla": sigla})

    print(f"Comuni:            {len(comuni):,}")
    print(f"Unique CAPs:       {len(by_cap):,}")

    records: List[dict] = []
    matched_state = 0
    for cap in sorted(by_cap):
        rows = sorted(by_cap[cap], key=lambda r: r["nome"].upper())
        chosen = rows[0]
        record = {
            "code": cap,
            "country_id": int(it["id"]),
            "country_code": "IT",
        }
        state = state_by_iso2.get(chosen["sigla"])
        if state is not None:
            record["state_id"] = int(state["id"])
            # Use the state's canonical iso2 from states.json, not the raw
            # source sigla — they differ for Aosta (AO -> 23) and any future
            # alias bridges.
            record["state_code"] = state.get("iso2") or chosen["sigla"]
            matched_state += 1
        if chosen["nome"]:
            record["locality_name"] = chosen["nome"]
        record["type"] = "full"
        record["source"] = "istat"
        records.append(record)

    print(f"Records:           {len(records):,}")
    print(f"  with state_id:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/IT.json"
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
