#!/usr/bin/env python3
"""Venezuela -> contributions/postcodes/VE.json importer for #1039.

Source data
-----------
The community ``JhonnelN/codigos_postales_venezuela`` repository
ships IPOSTEL's catalogue keyed by estado / zona / postcode / city:

    estado, zona, codigo_postal, ciudad
    Anzoategui, Anaco, 6003, Anaco

Source URL: https://raw.githubusercontent.com/JhonnelN/codigos_postales_venezuela/master/codigos_postales.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Resolves ``state_id`` via ASCII-fold name match against
   ``states.json`` with a 1-entry STATE_ALIASES bridge for the 2019
   "Vargas" -> "La Guaira" rename.
3. Pads codes to the 4-digit canonical form.
4. Writes contributions/postcodes/VE.json idempotently.

License & attribution
---------------------
- Source: JhonnelN/codigos_postales_venezuela (open redistribution
  of IPOSTEL's publicly published index).
- Each row: ``source: "ipostel-via-JhonnelN"``

Usage
-----
    python3 bin/scripts/sync/import_venezuela_postcodes.py
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
    "https://raw.githubusercontent.com/JhonnelN/codigos_postales_venezuela/"
    "master/codigos_postales.csv"
)

# Source estado (ASCII-folded) -> CSC states.json "name"
STATE_ALIASES: Dict[str, str] = {
    "vargas": "La Guaira",  # 2019 rename
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
        return r.read().decode("utf-8", errors="replace")


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
    ve_country = next((c for c in countries if c.get("iso2") == "VE"), None)
    if ve_country is None:
        print("ERROR: VE not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ve_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ve_states = [s for s in states if s.get("country_id") == ve_country["id"]]
    state_by_fold: Dict[str, dict] = {_fold(s["name"]): s for s in ve_states}
    print(f"Country: Venezuela (id={ve_country['id']}); states indexed: {len(ve_states)}")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("codigo_postal") or "").strip().zfill(4)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        estado = (row.get("estado") or "").strip()
        ciudad = (row.get("ciudad") or "").strip()
        zona = (row.get("zona") or "").strip()
        locality = ciudad or zona
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ve_country["id"]),
            "country_code": "VE",
        }
        target_estado = STATE_ALIASES.get(_fold(estado), estado)
        state = state_by_fold.get(_fold(target_estado))
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "ipostel-via-JhonnelN"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/VE.json"
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
