#!/usr/bin/env python3
"""Argentina -> contributions/postcodes/AR.json importer for issue #1039.

Source data
-----------
The community-maintained ``androdron/localidades_AR`` repository
publishes a CSV scraped from Correo Argentino's CPA consultation
form. Each row contains:
  provincia, id, localidad, cp, id_prov_mstr

The CSV ships ``cp`` as the legacy 4-digit postal code (the original
Correo numeric system). Argentina's modern CPA Argentino prefixes the
4-digit code with a province letter and suffixes a 3-letter block code
(e.g. ``B1234ABC``); the community feed exposes the 4-digit core that
matches Correo's free consultation form. The repo regex
``^[A-Z]?\\d{4}[A-Z]{0,3}$`` accepts both forms.

Source URL: https://raw.githubusercontent.com/androdron/localidades_AR/master/localidades_cp_maestro.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked in the harness)
2. Normalises the provincia column (ASCII fold) and matches to states.json
3. Drops empty cp rows; emits one row per (cp, locality) pair
4. Writes contributions/postcodes/AR.json idempotently

Why ASCII fold for province match
---------------------------------
Source uses ``Cordoba``/``Tucuman``/``Rio Negro`` (no diacritics);
states.json uses ``Córdoba``/``Tucumán``/``Río Negro``. NFKD strip of
combining marks gives a stable join key. ``Ciudad Autonoma de Buenos
Aires`` is a CSC name mismatch (states.json uses ``Autonomous City of
Buenos Aires``) so ships via STATE_ALIASES.

License & attribution
---------------------
- Source: androdron/localidades_AR (no licence file, scraped from
  Correo Argentino's free public consultation endpoint)
- Each row: source: "correo-argentino-via-androdron"

Usage
-----
    python3 bin/scripts/sync/import_argentina_postcodes.py
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
from typing import Dict, List, Optional


SOURCE_URL = (
    "https://raw.githubusercontent.com/androdron/localidades_AR/"
    "master/localidades_cp_maestro.csv"
)

# Source-name -> CSC states.json "name" (after ASCII fold). Only entries
# where ASCII fold alone does not match.
STATE_ALIASES: Dict[str, str] = {
    "ciudad autonoma de buenos aires": "Autonomous City of Buenos Aires",
}


def _ascii_fold(value: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c)
    ).strip().lower()


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = fetch_csv(SOURCE_URL)

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    ar_country = next((c for c in countries if c.get("iso2") == "AR"), None)
    if ar_country is None:
        print("ERROR: AR not in countries.json", file=sys.stderr)
        return 2

    regex = re.compile(ar_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ar_states = [s for s in states if s.get("country_id") == ar_country["id"]]
    state_by_fold: Dict[str, dict] = {
        _ascii_fold(s["name"]): s for s in ar_states if s.get("name")
    }
    print(
        f"Country: Argentina (id={ar_country['id']}); states indexed: {len(ar_states)}"
    )

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_no_cp = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("cp") or "").strip()
        if not code:
            skipped_no_cp += 1
            continue
        # The legacy 4-digit code; pad to 4 (some short codes appear in CABA)
        if code.isdigit():
            code = code.zfill(4)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        prov_raw = (row.get("provincia") or "").strip()
        prov_fold = _ascii_fold(prov_raw)
        prov_alias = STATE_ALIASES.get(prov_fold)
        state = None
        if prov_alias:
            state = state_by_fold.get(_ascii_fold(prov_alias))
        if state is None:
            state = state_by_fold.get(prov_fold)
        if state is None:
            skipped_no_state += 1

        locality = (row.get("localidad") or "").strip()
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ar_country["id"]),
            "country_code": "AR",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "correo-argentino-via-androdron"
        records.append(record)

    print(f"Skipped (no cp):       {skipped_no_cp:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/AR.json"
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
