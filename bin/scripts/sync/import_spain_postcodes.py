#!/usr/bin/env python3
"""Spain CP -> contributions/postcodes/ES.json importer for issue #1039.

Source data
-----------
The community-maintained ``walterleonardo/codigos_postales_espa-a`` archive
is a redistribution of the official INE/Correos Spanish postcode-municipio
mapping. The source file format is a header-less semicolon-OR-comma CSV
with three columns:

  id, postal_code, municipality_name

~12,000 unique postcodes covering all 50 provinces plus Ceuta (51) and
Melilla (52).

What this script does
---------------------
1. Reads the CSV (UTF-8, comma-delimited, no header)
2. Picks ONE canonical municipality per unique postcode (first alphabetical)
3. Resolves state by mapping the postcode's first 2 digits to province ISO
   codes via POSTAL_PREFIX_TO_ISO2 (the well-known Spanish convention,
   01=VI/Álava, 28=M/Madrid, 08=B/Barcelona, etc.)
4. Writes contributions/postcodes/ES.json

Why the prefix map
------------------
Spain's states.json uses license-plate-style ISO codes (A, B, M, GR, ...)
rather than numeric postal prefixes. Since the source CSV has no province
column, mapping from the postcode prefix is the only way to resolve state
and is universally documented.

License
-------
- Upstream: INE/Correos (open data, no formal redistribution licence text;
  used widely in commercial and open contexts)
- Mirror: github.com/walterleonardo/codigos_postales_espa-a
- Each row: source: "ine"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://raw.githubusercontent.com/walterleonardo/codigos_postales_espa-a/master/codigos_postales_municipios.csv',
      '/tmp/es_postales.csv')"

    python3 bin/scripts/sync/import_spain_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Spanish postcode-prefix -> state ISO2 (from states.json, license-plate style)
# Authoritative mapping; postal prefixes have been stable since the 1980s.
POSTAL_PREFIX_TO_ISO2: Dict[str, str] = {
    "01": "VI",  # Araba / Álava
    "02": "AB",  # Albacete
    "03": "A",   # Alicante
    "04": "AL",  # Almería
    "05": "AV",  # Ávila
    "06": "BA",  # Badajoz
    "07": "PM",  # Islas Baleares
    "08": "B",   # Barcelona
    "09": "BU",  # Burgos
    "10": "CC",  # Cáceres
    "11": "CA",  # Cádiz
    "12": "CS",  # Castellón
    "13": "CR",  # Ciudad Real
    "14": "CO",  # Córdoba
    "15": "C",   # A Coruña
    "16": "CU",  # Cuenca
    "17": "GI",  # Girona
    "18": "GR",  # Granada
    "19": "GU",  # Guadalajara
    "20": "SS",  # Gipuzkoa
    "21": "H",   # Huelva
    "22": "HU",  # Huesca
    "23": "J",   # Jaén
    "24": "LE",  # León
    "25": "L",   # Lleida
    "26": "LO",  # La Rioja (Logroño)
    "27": "LU",  # Lugo
    "28": "M",   # Madrid
    "29": "MA",  # Málaga
    "30": "MU",  # Murcia
    "31": "NA",  # Navarra
    "32": "OR",  # Ourense
    "33": "O",   # Asturias
    "34": "P",   # Palencia
    "35": "GC",  # Las Palmas
    "36": "PO",  # Pontevedra
    "37": "SA",  # Salamanca
    "38": "TF",  # Santa Cruz de Tenerife
    "39": "S",   # Cantabria
    "40": "SG",  # Segovia
    "41": "SE",  # Sevilla
    "42": "SO",  # Soria
    "43": "T",   # Tarragona
    "44": "TE",  # Teruel
    "45": "TO",  # Toledo
    "46": "V",   # Valencia
    "47": "VA",  # Valladolid
    "48": "BI",  # Bizkaia / Vizcaya
    "49": "ZA",  # Zamora
    "50": "Z",   # Zaragoza
    "51": "CE",  # Ceuta
    "52": "ML",  # Melilla
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/es_postales.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ERROR: input not found: {src}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    es = next((c for c in countries if c.get("iso2") == "ES"), None)
    if es is None:
        print("ERROR: ES not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    es_states = [s for s in states if s.get("country_id") == es["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in es_states if s.get("iso2")}

    print(f"Country: Spain (id={es['id']}); states indexed by iso2: {len(state_by_iso2)}")

    by_postcode: Dict[str, List[str]] = {}
    bad = 0
    with src.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            code = (row[1] or "").strip().zfill(5)
            commune = (row[2] or "").strip().strip('"')
            if not code.isdigit() or len(code) != 5:
                bad += 1
                continue
            by_postcode.setdefault(code, []).append(commune)

    print(f"Skipped malformed rows: {bad:,}")
    print(f"Unique postcodes:       {len(by_postcode):,}")

    records: List[dict] = []
    matched_state = 0
    for code in sorted(by_postcode):
        commune = sorted(by_postcode[code], key=lambda s: s.upper())[0]
        record = {
            "code": code,
            "country_id": int(es["id"]),
            "country_code": "ES",
        }
        prefix = code[:2]
        iso2 = POSTAL_PREFIX_TO_ISO2.get(prefix)
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
        if commune:
            record["locality_name"] = commune
        record["type"] = "full"
        record["source"] = "ine"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/ES.json"
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
