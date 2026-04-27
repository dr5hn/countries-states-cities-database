#!/usr/bin/env python3
"""Mozambique -> contributions/postcodes/MZ.json importer for #1039.

Source data
-----------
The community ``PauloPhagula/cep`` repository ships Correios de
Moçambique's CEP catalogue keyed by province / district /
"posto administrativo":

    Província, Código de Província, Distrito, Código de Distrito,
    Posto administrativo, Código de Posto Administrativo, CEP
    Cidade de Maputo, 01, Distrito KaMpfumo, 01, Alto Maé A, 01, 0101-01

Source URL: https://raw.githubusercontent.com/PauloPhagula/cep/master/cep.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Strips the administrative ``-NN`` suffix to obtain the canonical
   4-digit CEP form (province+district) expected by the country
   regex ``^(\\d{4})$``.
3. Resolves ``state_id`` via case-insensitive name match against
   ``states.json`` with a 2-entry STATE_ALIASES bridge for the
   "Cidade de Maputo" -> Maputo city (``MPM``) and "Maputo Província"
   -> Maputo province (``L``) split.
4. Dedupes at (canonical CEP, district) so 555 source rows collapse
   to ~161 distinct 4-digit codes.
5. Writes contributions/postcodes/MZ.json idempotently.

License & attribution
---------------------
- Source: PauloPhagula/cep (open redistribution of Correios de
  Moçambique's publicly published CEP catalogue).
- Each row: ``source: "correios-mocambique-via-PauloPhagula"``

Usage
-----
    python3 bin/scripts/sync/import_mozambique_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/PauloPhagula/cep/master/cep.csv"
)

# Source province (lowercased) -> CSC states.json "name"
STATE_ALIASES: Dict[str, str] = {
    "cidade de maputo": "Maputo",       # CSC carries two "Maputo" entries (MPM city, L province)
    "maputo provincia": "Maputo",       # ASCII-folded form
    "maputo província": "Maputo",       # raw source form
    "zambezia": "Zambezia",
}

# When two CSC entries share the same name, prefer this iso2 by source label.
SOURCE_TO_ISO2: Dict[str, str] = {
    "cidade de maputo": "MPM",
    "maputo provincia": "L",
    "maputo província": "L",
}


def _fold(value: str) -> str:
    s = "".join(
        c for c in unicodedata.normalize("NFKD", (value or "").lower())
        if not unicodedata.combining(c)
    )
    return s.strip()


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
    mz_country = next((c for c in countries if c.get("iso2") == "MZ"), None)
    if mz_country is None:
        print("ERROR: MZ not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(mz_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    mz_states = [s for s in states if s.get("country_id") == mz_country["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in mz_states if s.get("iso2")}
    state_by_fold: Dict[str, dict] = {_fold(s["name"]): s for s in mz_states}
    print(f"Country: Mozambique (id={mz_country['id']}); states indexed: {len(mz_states)}")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        raw = (row.get("CEP") or "").strip()
        if not raw:
            continue
        # Canonical 4-digit form is the part before the "-".
        code = raw.split("-")[0].strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        province_raw = (row.get("Província") or row.get("Provincia") or "").strip()
        district = (row.get("Distrito") or "").strip()
        key = (code, district.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(mz_country["id"]),
            "country_code": "MZ",
        }
        prov_fold = _fold(province_raw)
        # Disambiguate the duplicate "Maputo" CSC names via SOURCE_TO_ISO2
        forced_iso2 = SOURCE_TO_ISO2.get(prov_fold)
        state = None
        if forced_iso2:
            state = state_by_iso2.get(forced_iso2)
        if state is None:
            target_name = STATE_ALIASES.get(prov_fold, province_raw)
            state = state_by_fold.get(_fold(target_name))
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if district:
            record["locality_name"] = district
        record["type"] = "full"
        record["source"] = "correios-mocambique-via-PauloPhagula"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MZ.json"
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
