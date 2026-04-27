#!/usr/bin/env python3
"""Costa Rica -> contributions/postcodes/CR.json importer for #1039.

Source data
-----------
The community ``llperez/codigos_cr`` repository ships Correos de
Costa Rica's 5-digit catalogue:

    CodigoPostal,Provincia,Canton,Distrito
    10101,San José,San José,Carmen

Source URL: https://raw.githubusercontent.com/llperez/codigos_cr/master/postal.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Resolves ``state_id`` via case-insensitive name match against
   states.json — all 7 CR provinces match directly.
3. Emits one record per ``(postcode, distrito)`` pair.
4. Writes contributions/postcodes/CR.json idempotently.

License & attribution
---------------------
- Source: llperez/codigos_cr; data is the publicly published Correos
  de Costa Rica catalogue.
- Each row: ``source: "correos-de-costa-rica-via-llperez"``

Usage
-----
    python3 bin/scripts/sync/import_costa_rica_postcodes.py
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
    "https://raw.githubusercontent.com/llperez/codigos_cr/master/postal.csv"
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
    cr_country = next((c for c in countries if c.get("iso2") == "CR"), None)
    if cr_country is None:
        print("ERROR: CR not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(cr_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    cr_states = [s for s in states if s.get("country_id") == cr_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"].lower(): s for s in cr_states}
    print(f"Country: Costa Rica (id={cr_country['id']}); states indexed: {len(cr_states)}")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("CodigoPostal") or "").strip().zfill(5)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        province = (row.get("Provincia") or "").strip()
        distrito = (row.get("Distrito") or "").strip()
        canton = (row.get("Canton") or "").strip()
        locality = ", ".join(p for p in (distrito, canton) if p)
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(cr_country["id"]),
            "country_code": "CR",
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
        record["source"] = "correos-de-costa-rica-via-llperez"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/CR.json"
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
