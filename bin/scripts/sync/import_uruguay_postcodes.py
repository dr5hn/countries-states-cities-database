#!/usr/bin/env python3
"""Uruguay -> contributions/postcodes/UY.json importer for issue #1039.

Source data
-----------
The community ``ale-uy/CPuy`` repository (Apache-2.0) ships a SQLite
database with Uruguay's full Localidades table:

    columns: Departamento (TEXT, uppercase), Localidad (TEXT, uppercase),
             CodigoPostal (INTEGER, 5-digit)

1,973 (departamento, localidad, código_postal) tuples covering 122
distinct postcodes across all 19 Uruguayan departments.

Source URL: https://raw.githubusercontent.com/ale-uy/CPuy/master/db

What this script does
---------------------
1. Fetches the SQLite db via urllib.
2. Reads via Python's stdlib sqlite3 (no extra deps).
3. Resolves state FK by ASCII-fold + name match against CSC's 19
   UY department entries.
4. Emits one row per (postcode, locality) tuple.
5. Writes contributions/postcodes/UY.json idempotently.

Coverage
--------
- 1,973 records / 100% state FK
- All 19 Uruguayan departments covered

License & attribution
---------------------
- Source: ale-uy/CPuy (Apache-2.0)
- Upstream: Correo Uruguayo public lookup
- Each row: ``source: "correo-uruguayo-via-ale-uy"``

Usage
-----
    python3 bin/scripts/sync/import_uruguay_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = "https://raw.githubusercontent.com/ale-uy/CPuy/master/db"


def _ascii_fold(value: str) -> str:
    return (
        "".join(
            c
            for c in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(c)
        )
        .strip()
        .lower()
    )


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local SQLite (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.input:
        db_path = args.input
        cleanup = False
    else:
        raw = fetch_bytes(SOURCE_URL)
        print(f"db size: {len(raw):,} bytes")
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.write(raw)
        tmp.close()
        db_path = tmp.name
        cleanup = True

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    uy_country = next((c for c in countries if c.get("iso2") == "UY"), None)
    if uy_country is None:
        print("ERROR: UY not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(uy_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    uy_states = [s for s in states if s.get("country_id") == uy_country["id"]]
    state_by_fold: Dict[str, dict] = {
        _ascii_fold(s["name"]): s for s in uy_states if s.get("name")
    }
    print(
        f"Country: Uruguay (id={uy_country['id']}); states indexed: {len(uy_states)}"
    )

    conn = sqlite3.connect(db_path)
    rows = list(
        conn.execute("SELECT Departamento, Localidad, CodigoPostal FROM Localidades")
    )
    conn.close()
    if cleanup:
        os.unlink(db_path)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_deps: Dict[str, int] = {}

    for dep, loc, cp in rows:
        code = str(cp).zfill(5)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        dep_str = (dep or "").strip()
        loc_str = (loc or "").strip()
        state = state_by_fold.get(_ascii_fold(dep_str))
        if state is None:
            unknown_deps[dep_str] = unknown_deps.get(dep_str, 0) + 1
            skipped_no_state += 1

        # Title-case the uppercase locality + dept for display
        locality = loc_str.title()
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(uy_country["id"]),
            "country_code": "UY",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "correo-uruguayo-via-ale-uy"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_deps:
        print("Unknown departments:")
        for d, n in sorted(unknown_deps.items(), key=lambda x: -x[1]):
            print(f"  {d!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/UY.json"
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
