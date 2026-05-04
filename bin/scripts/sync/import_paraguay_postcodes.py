#!/usr/bin/env python3
"""Paraguay -> contributions/postcodes/PY.json importer for issue #1039.

Source data
-----------
The community ``3lD4m14n/mapa-codigos-postales-paraguay`` repository
(MIT-licensed) ships a 17 MB ESRI shapefile zip containing the
official zonal postal-code attribute table from Paraguay's INE
(Instituto Nacional de Estadística) and DINACOPA / Correos
Paraguayos.

DBF schema:
    DPTO        : 2-char dept code      (00-17)
    DPTO_DESC   : department name
    DISTRITO    : 2-char district code
    DIST_DESC   : district name
    BARLOC      : 3-char barrio code
    BARLO_DESC  : barrio/locality name
    DIV_POST    : 2-char postal subdivision
    ZONA        : 2-char zone code
    COD_POST    : 6-digit canonical postal code (DPTO + DISTRITO + DIV_POST)
    cod_bar     : 7-char barrio code

Source URL: https://raw.githubusercontent.com/3lD4m14n/mapa-codigos-postales-paraguay/main/ZONA_POSTAL_PARAGUAY.zip

What this script does
---------------------
1. Fetches the shapefile zip via urllib (curl is blocked).
2. Extracts only the .dbf (we don't need geometry — the DBF carries
   all attributes).
3. Decodes the DBF as latin-1 (source ships Spanish text in cp1252-
   compatible Latin-1, not UTF-8).
4. Maps the 18 source DPTO codes to CSC iso2 via DPTO_TO_ISO2,
   handling two CSC-specific reorderings: source DPTO 00 ->
   ASU (Asuncion); source DPTO 16/17 -> CSC iso2 19/16 (Boquerón,
   Alto Paraguay swapped).
5. Emits one row per (COD_POST, BARLO_DESC, DIST_DESC) tuple.
6. Writes contributions/postcodes/PY.json idempotently.

Regex fix
---------
Before this PR, countries.json had PY regex `^\\d{4}$` (DINACOPA's
2007 4-digit form). The dataset ships the canonical 6-digit
zone-level codes also published officially. Updated regex to
`^(\\d{4}|\\d{6})$` / format `####|######` to accept both forms.

Dependency
----------
- ``dbfread`` (MIT, pure-Python DBF parser). Install via:
    python3 -m pip install dbfread

License & attribution
---------------------
- Source: 3lD4m14n/mapa-codigos-postales-paraguay (MIT)
- Upstream: INE / DINACOPA Correos Paraguayos
- Each row: ``source: "dinacopa-via-3lD4m14n"``

Usage
-----
    python3 bin/scripts/sync/import_paraguay_postcodes.py
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List

import dbfread


SOURCE_URL = (
    "https://raw.githubusercontent.com/3lD4m14n/mapa-codigos-postales-paraguay/"
    "main/ZONA_POSTAL_PARAGUAY.zip"
)

# Source DPTO (2-digit) -> CSC iso2.
# CSC uses Paraguay's official ISO 3166-2:PY assignment which assigns
# numeric iso2 1-15 to most departments but reorders Boquerón (16
# in source -> 19 in CSC) and Alto Paraguay (17 in source -> 16 in
# CSC). 'ASU' is CSC's iso2 for Asunción (the capital district,
# DPTO=00 in source).
DPTO_TO_ISO2: Dict[str, str] = {
    "00": "ASU",  # Asunción (Capital District)
    "01": "1",    # Concepción
    "02": "2",    # San Pedro
    "03": "3",    # Cordillera
    "04": "4",    # Guairá
    "05": "5",    # Caaguazú
    "06": "6",    # Caazapá
    "07": "7",    # Itapúa
    "08": "8",    # Misiones
    "09": "9",    # Paraguarí
    "10": "10",   # Alto Paraná
    "11": "11",   # Central
    "12": "12",   # Ñeembucú
    "13": "13",   # Amambay
    "14": "14",   # Canindeyú
    "15": "15",   # Presidente Hayes
    "16": "19",   # Boquerón (CSC iso2 19, NOT 16)
    "17": "16",   # Alto Paraguay (CSC iso2 16, NOT 17)
}


def fetch_zip(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local zip (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    raw = (
        Path(args.input).read_bytes()
        if args.input
        else fetch_zip(SOURCE_URL)
    )
    print(f"zip size: {len(raw):,} bytes")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    py_country = next((c for c in countries if c.get("iso2") == "PY"), None)
    if py_country is None:
        print("ERROR: PY not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(py_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    py_states = [s for s in states if s.get("country_id") == py_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in py_states if s.get("iso2")
    }
    print(
        f"Country: Paraguay (id={py_country['id']}); "
        f"states indexed: {len(py_states)}"
    )

    zf = zipfile.ZipFile(io.BytesIO(raw))
    dbf_name = next(n for n in zf.namelist() if n.lower().endswith(".dbf"))

    with tempfile.TemporaryDirectory() as tmp:
        dbf_path = os.path.join(tmp, "py.dbf")
        with open(dbf_path, "wb") as f:
            f.write(zf.read(dbf_name))
        rows = list(dbfread.DBF(dbf_path, encoding="latin-1"))
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_no_code = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_dpto: Dict[str, int] = {}

    for row in rows:
        code = (row.get("COD_POST") or "").strip()
        if not code:
            skipped_no_code += 1
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        dpto = (row.get("DPTO") or "").strip()
        iso2 = DPTO_TO_ISO2.get(dpto)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_dpto[dpto] = unknown_dpto.get(dpto, 0) + 1
            skipped_no_state += 1

        barlo = (row.get("BARLO_DESC") or "").strip()
        dist = (row.get("DIST_DESC") or "").strip()
        if barlo and dist and barlo.lower() != dist.lower():
            locality = f"{barlo}, {dist}"
        else:
            locality = barlo or dist

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(py_country["id"]),
            "country_code": "PY",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "dinacopa-via-3lD4m14n"
        records.append(record)

    print(f"Skipped (no code):     {skipped_no_code:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_dpto:
        print("Unknown DPTO codes (not in DPTO_TO_ISO2):")
        for d, n in sorted(unknown_dpto.items(), key=lambda x: -x[1]):
            print(f"  {d!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PY.json"
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
