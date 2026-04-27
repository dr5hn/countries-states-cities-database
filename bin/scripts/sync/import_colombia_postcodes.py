#!/usr/bin/env python3
"""Colombia -> contributions/postcodes/CO.json importer for issue #1039.

Source data
-----------
The community ``JohaAlarcon/Load_postal_code`` repository ships the
official Colombian postcode catalogue published by 4-72 (Servicios
Postales Nacionales). Each row has:

  cod_departamento;cod_municipio;cod_postal;limite

- ``cod_departamento`` is the DANE 2-digit department code
- ``cod_municipio`` is the DANE 3-digit municipality code
- ``cod_postal`` is the 6-digit national postcode
- ``limite`` is a free-text boundary description (street-level)

Source URL: https://raw.githubusercontent.com/JohaAlarcon/Load_postal_code/master/C_digos_Postales_Nacionales.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked in the harness)
2. Maps DANE department code -> CSC ``states.json`` iso2 (3-letter)
3. Emits one record per (cod_postal, cod_municipio) pair
4. Writes contributions/postcodes/CO.json idempotently

The ``limite`` field is a street-level boundary description and not a
human-friendly locality name (and arrives double-encoded in the source
file); it is intentionally not surfaced as ``locality_name``.

License & attribution
---------------------
- Source: 4-72 (Servicios Postales Nacionales) via JohaAlarcon mirror
- Each row: source: "4-72-via-JohaAlarcon"

Usage
-----
    python3 bin/scripts/sync/import_colombia_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/JohaAlarcon/Load_postal_code/"
    "master/C_digos_Postales_Nacionales.csv"
)

# DANE department code (2 digits) -> CSC states.json iso2 (3 letters).
# Mapping derived from DANE División Político-Administrativa codes.
DANE_TO_ISO2: Dict[str, str] = {
    "05": "ANT",  # Antioquia
    "08": "ATL",  # Atlántico
    "11": "DC",   # Bogotá D.C.
    "13": "BOL",  # Bolívar
    "15": "BOY",  # Boyacá
    "17": "CAL",  # Caldas
    "18": "CAQ",  # Caquetá
    "19": "CAU",  # Cauca
    "20": "CES",  # Cesar
    "23": "COR",  # Córdoba
    "25": "CUN",  # Cundinamarca
    "27": "CHO",  # Chocó
    "41": "HUI",  # Huila
    "44": "LAG",  # La Guajira
    "47": "MAG",  # Magdalena
    "50": "MET",  # Meta
    "52": "NAR",  # Nariño
    "54": "NSA",  # Norte de Santander
    "63": "QUI",  # Quindío
    "66": "RIS",  # Risaralda
    "68": "SAN",  # Santander
    "70": "SUC",  # Sucre
    "73": "TOL",  # Tolima
    "76": "VAC",  # Valle del Cauca
    "81": "ARA",  # Arauca
    "85": "CAS",  # Casanare
    "86": "PUT",  # Putumayo
    "88": "SAP",  # San Andrés, Providencia y Santa Catalina
    "91": "AMA",  # Amazonas
    "94": "GUA",  # Guainía
    "95": "GUV",  # Guaviare
    "97": "VAU",  # Vaupés
    "99": "VID",  # Vichada
}


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8", errors="replace")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    co_country = next((c for c in countries if c.get("iso2") == "CO"), None)
    if co_country is None:
        print("ERROR: CO not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(co_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    co_states = [s for s in states if s.get("country_id") == co_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        (s.get("iso2") or "").upper(): s for s in co_states if s.get("iso2")
    }
    print(f"Country: Colombia (id={co_country['id']}); states indexed: {len(co_states)}")

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("cod_postal") or "").strip()
        if not code:
            continue
        # Source occasionally drops the leading zero (5-digit) or carries a
        # spurious extra zero (7-digit). Normalise to canonical 6-digit form.
        if code.isdigit():
            if len(code) == 5:
                code = "0" + code
            elif len(code) == 7 and code.startswith("0"):
                code = code[1:]
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        muni = (row.get("cod_municipio") or "").strip()
        key = (code, muni)
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(co_country["id"]),
            "country_code": "CO",
        }
        dept = (row.get("cod_departamento") or "").strip().zfill(2)
        iso2 = DANE_TO_ISO2.get(dept)
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
            else:
                skipped_no_state += 1
        else:
            skipped_no_state += 1

        record["type"] = "full"
        record["source"] = "4-72-via-JohaAlarcon"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/CO.json"
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
