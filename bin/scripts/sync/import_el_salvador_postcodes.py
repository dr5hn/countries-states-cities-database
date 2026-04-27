#!/usr/bin/env python3
"""El Salvador -> contributions/postcodes/SV.json importer for #1039.

Source data
-----------
The community ``micryptosv/SV-Postales-2025-API`` repository ships
the 2025 Correos de El Salvador catalogue keyed by department,
municipality, district and 5-digit code:

    Departamento, Municipio, Distrito, CodigoPostal
    Ahuachapán, Ahuachapán Norte, Atiquizaya, 02103

Source URL: https://raw.githubusercontent.com/micryptosv/SV-Postales-2025-API/main/data/elsalvador.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Strips the always-present leading ``0`` to recover the canonical
   4-digit form expected by the country regex ``^(?:CP)*(\\d{4})$``.
3. Resolves ``state_id`` via case-insensitive name match against
   ``states.json`` for all 14 departments.
4. Emits one record per ``(4-digit code, distrito)`` pair.
5. Writes contributions/postcodes/SV.json idempotently.

License & attribution
---------------------
- Source: micryptosv/SV-Postales-2025-API; data is the publicly
  published 2025 Correos de El Salvador catalogue.
- Each row: ``source: "correos-el-salvador-via-micryptosv"``

Usage
-----
    python3 bin/scripts/sync/import_el_salvador_postcodes.py
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
    "https://raw.githubusercontent.com/micryptosv/SV-Postales-2025-API/"
    "main/data/elsalvador.csv"
)


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None)
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
    sv_country = next((c for c in countries if c.get("iso2") == "SV"), None)
    if sv_country is None:
        print("ERROR: SV not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(sv_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    sv_states = [s for s in states if s.get("country_id") == sv_country["id"]]
    state_by_name: Dict[str, dict] = {
        s["name"].strip().lower(): s for s in sv_states
    }
    print(f"Country: El Salvador (id={sv_country['id']}); states indexed: {len(sv_states)}")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("CodigoPostal") or "").strip()
        # Strip the always-present leading "0" to get the canonical 4-digit
        if code.startswith("0") and len(code) == 5 and code.isdigit():
            code = code[1:]
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        province = (row.get("Departamento") or "").strip()
        distrito = (row.get("Distrito") or "").strip()
        municipio = (row.get("Municipio") or "").strip()
        locality = ", ".join(p for p in (distrito, municipio) if p)
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(sv_country["id"]),
            "country_code": "SV",
        }
        state = state_by_name.get(province.lower())
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "correos-el-salvador-via-micryptosv"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/SV.json"
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
