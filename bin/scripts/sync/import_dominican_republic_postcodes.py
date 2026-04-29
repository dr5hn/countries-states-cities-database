#!/usr/bin/env python3
"""Dominican Republic -> contributions/postcodes/DO.json importer for #1039.

Source data
-----------
The community ``manuelpgs/localidades-postales-rd`` repository ships
INPOSDOM's catalogue across two CSV files:

- ``provincias.csv``: ``id, ?, name``
- ``localidades.csv``: ``id, prov_id, name, postcode, ?, ?``

Source URLs:
- https://raw.githubusercontent.com/manuelpgs/localidades-postales-rd/master/csv/provincias.csv
- https://raw.githubusercontent.com/manuelpgs/localidades-postales-rd/master/csv/localidades.csv

What this script does
---------------------
1. Fetches both CSVs via urllib (curl is blocked).
2. Builds a source-prov-id -> CSC iso2 map by ASCII-fold name match
   with a 2-entry STATE_ALIASES bridge for "BAHORUCO" -> "Baoruco"
   (source spelling differs by an extra ``h``) and "SAN JUAN DE LA
   MAGUANA" -> "San Juan" (CSC drops the "de la Maguana" suffix).
3. Emits one record per ``(postcode, locality)`` pair.
4. Writes contributions/postcodes/DO.json idempotently.

License & attribution
---------------------
- Source: manuelpgs/localidades-postales-rd; data is the publicly
  published INPOSDOM postcode catalogue.
- Each row: ``source: "inposdom-via-manuelpgs"``

Usage
-----
    python3 bin/scripts/sync/import_dominican_republic_postcodes.py
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


SOURCE_URL_PROVINCES = (
    "https://raw.githubusercontent.com/manuelpgs/localidades-postales-rd/"
    "master/csv/provincias.csv"
)
SOURCE_URL_LOCALITIES = (
    "https://raw.githubusercontent.com/manuelpgs/localidades-postales-rd/"
    "master/csv/localidades.csv"
)

STATE_ALIASES: Dict[str, str] = {
    "bahoruco": "Baoruco",
    "san juan de la maguana": "San Juan",
}


def _fold(value: str) -> str:
    s = "".join(
        c for c in unicodedata.normalize("NFKD", (value or "").lower())
        if not unicodedata.combining(c)
    )
    return s.strip()


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    do_country = next((c for c in countries if c.get("iso2") == "DO"), None)
    if do_country is None:
        print("ERROR: DO not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(do_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    do_states = [s for s in states if s.get("country_id") == do_country["id"]]
    state_by_fold: Dict[str, dict] = {_fold(s["name"]): s for s in do_states}
    print(f"Country: Dominican Republic (id={do_country['id']}); states indexed: {len(do_states)}")

    prov_text = fetch_text(SOURCE_URL_PROVINCES)
    src_prov_to_state: Dict[str, dict] = {}
    for row in csv.reader(io.StringIO(prov_text)):
        if len(row) < 3:
            continue
        src_id = (row[0] or "").strip()
        name = (row[2] or "").strip()
        # Strip parenthetical alternate names ("SANTO DOMINGO (GRAN)" etc.)
        clean = name.split("(")[0].strip()
        target = STATE_ALIASES.get(_fold(clean), clean)
        state = state_by_fold.get(_fold(target))
        if state is not None:
            src_prov_to_state[src_id] = state
    print(f"Source provinces resolved: {len(src_prov_to_state)}")

    loc_text = fetch_text(SOURCE_URL_LOCALITIES)
    rows = list(csv.reader(io.StringIO(loc_text)))
    print(f"Source localities: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        if len(row) < 5:
            continue
        prov_id = (row[1] or "").strip()
        locality = (row[2] or "").strip()
        code = (row[3] or "").strip().zfill(5)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(do_country["id"]),
            "country_code": "DO",
        }
        state = src_prov_to_state.get(prov_id)
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "inposdom-via-manuelpgs"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/DO.json"
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
