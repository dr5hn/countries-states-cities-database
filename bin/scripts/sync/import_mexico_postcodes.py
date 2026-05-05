#!/usr/bin/env python3
"""Mexico -> contributions/postcodes/MX.json importer for issue #1039.

Source data
-----------
The community ``redrbrt/sepomex-zip-codes`` repository publishes the
SEPOMEX (Servicio Postal Mexicano) postcode export for April 2016
under the Unlicense (public domain). Each row carries the full
estado / municipio / ciudad / colonia hierarchy plus the 5-digit CP.

    idEstado,estado,idMunicipio,municipio,ciudad,zona,cp,asentamiento,tipo
    1,Aguascalientes,1,Aguascalientes,Aguascalientes,Urbano,20000,"Zona Centro",Colonia

145,908 records / 32 states.

Source URL: https://raw.githubusercontent.com/redrbrt/sepomex-zip-codes/master/sepomex_abril-2016.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Resolves state FK via SEPOMEX ``idEstado`` (1-32) -> CSC iso2 map.
3. Pads 4-digit CPs to 5 digits (1,309 codes have a leading-zero
   stripped in the source).
4. Emits one row per (cp, asentamiento + ciudad) tuple.
5. Writes contributions/postcodes/MX.json idempotently.

Why idEstado map (not name-fold)
--------------------------------
SEPOMEX's numeric idEstado is stable across snapshots and avoids the
single name-drift between source ('México' for idEstado=15) and CSC
('Estado de México'). A 32-entry hand map is also more readable than
a name-fold + alias combo.

Staleness
---------
The data is the April 2016 snapshot — newer 5-digit codes added by
SEPOMEX since then will be missing. The idempotent merge contract
allows a future fresher mirror to be layered on without losing this
import. The repo's `source` URL paywalled SEPOMEX's official live
feed.

License & attribution
---------------------
- Source: redrbrt/sepomex-zip-codes (Unlicense / public domain;
  derived from SEPOMEX's free public download portal)
- Each row: ``source: "sepomex-via-redrbrt-2016"``

Usage
-----
    python3 bin/scripts/sync/import_mexico_postcodes.py
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
    "https://raw.githubusercontent.com/redrbrt/sepomex-zip-codes/"
    "master/sepomex_abril-2016.csv"
)

# SEPOMEX idEstado (1-32) -> CSC iso2 in MX states.json.
ID_ESTADO_TO_ISO2: Dict[str, str] = {
    "1": "AGU",   # Aguascalientes
    "2": "BCN",   # Baja California
    "3": "BCS",   # Baja California Sur
    "4": "CAM",   # Campeche
    "5": "COA",   # Coahuila de Zaragoza
    "6": "COL",   # Colima
    "7": "CHP",   # Chiapas
    "8": "CHH",   # Chihuahua
    "9": "CMX",   # Ciudad de México
    "10": "DUR",  # Durango
    "11": "GUA",  # Guanajuato
    "12": "GRO",  # Guerrero
    "13": "HID",  # Hidalgo
    "14": "JAL",  # Jalisco
    "15": "MEX",  # Estado de México (source label: 'México')
    "16": "MIC",  # Michoacán de Ocampo
    "17": "MOR",  # Morelos
    "18": "NAY",  # Nayarit
    "19": "NLE",  # Nuevo León
    "20": "OAX",  # Oaxaca
    "21": "PUE",  # Puebla
    "22": "QUE",  # Querétaro
    "23": "ROO",  # Quintana Roo
    "24": "SLP",  # San Luis Potosí
    "25": "SIN",  # Sinaloa
    "26": "SON",  # Sonora
    "27": "TAB",  # Tabasco
    "28": "TAM",  # Tamaulipas
    "29": "TLA",  # Tlaxcala
    "30": "VER",  # Veracruz de Ignacio de la Llave
    "31": "YUC",  # Yucatán
    "32": "ZAC",  # Zacatecas
}


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    mx_country = next((c for c in countries if c.get("iso2") == "MX"), None)
    if mx_country is None:
        print("ERROR: MX not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(mx_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    mx_states = [s for s in states if s.get("country_id") == mx_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in mx_states if s.get("iso2")
    }
    print(
        f"Country: Mexico (id={mx_country['id']}); states indexed: {len(mx_states)}"
    )

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_no_code = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_idestado: Dict[str, int] = {}

    for row in rows:
        raw_cp = (row.get("cp") or "").strip()
        if not raw_cp:
            skipped_no_code += 1
            continue
        code = raw_cp.zfill(5) if raw_cp.isdigit() else raw_cp
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        id_estado = (row.get("idEstado") or "").strip()
        iso2 = ID_ESTADO_TO_ISO2.get(id_estado)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_idestado[id_estado] = unknown_idestado.get(id_estado, 0) + 1
            skipped_no_state += 1

        asent = (row.get("asentamiento") or "").strip()
        ciudad = (row.get("ciudad") or "").strip()
        # Locality = "asentamiento, ciudad" if both present and distinct
        if asent and ciudad and asent.lower() != ciudad.lower():
            locality = f"{asent}, {ciudad}"
        else:
            locality = asent or ciudad

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(mx_country["id"]),
            "country_code": "MX",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "sepomex-via-redrbrt-2016"
        records.append(record)

    print(f"Skipped (no code):     {skipped_no_code:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_idestado:
        print("Unknown idEstado values (not in ID_ESTADO_TO_ISO2):")
        for v, n in sorted(unknown_idestado.items(), key=lambda x: -x[1]):
            print(f"  {v!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MX.json"
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
