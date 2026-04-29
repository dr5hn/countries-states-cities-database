#!/usr/bin/env python3
"""South Africa -> contributions/postcodes/ZA.json importer for #1039.

Source data
-----------
The community-maintained ``raramuridesign-cc/South-African-Postal-Codes``
repository ships a CSV derived from SA Post Office's free public
postcode reference. Each row has:

  id, NumId, PlaceName, BoxCode, StrCode, Town, LAPLace, LAPTown

- ``BoxCode`` is the 4-digit code for PO Box delivery
- ``StrCode`` is the 4-digit code for street delivery
- ``Town`` is the human-friendly delivery town
- ``LAP*`` are Afrikaans-language fallbacks (typed as "Limited
  Afrikaans Place/Town" in the source)

Source URL: https://raw.githubusercontent.com/raramuridesign-cc/South-African-Postal-Codes/master/database/postcodes-za.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked in the harness)
2. Emits one row per (BoxCode, Town) and one per (StrCode, Town);
   when BoxCode == StrCode emits a single "full" record
3. Ships country-only (no state_id) because SA Post Office's 4-digit
   numbers were assigned along sorting routes and do not align with
   the 9 provinces (matches the SE/SI precedent in this repo)
4. Writes contributions/postcodes/ZA.json idempotently

License & attribution
---------------------
- Source: SA Post Office reference data, redistributed by the
  raramuridesign-cc/South-African-Postal-Codes repository
- Each row: source: "sapo-via-raramuridesign"

Usage
-----
    python3 bin/scripts/sync/import_south_africa_postcodes.py
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
    "https://raw.githubusercontent.com/raramuridesign-cc/South-African-Postal-Codes/"
    "master/database/postcodes-za.csv"
)


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
    za_country = next((c for c in countries if c.get("iso2") == "ZA"), None)
    if za_country is None:
        print("ERROR: ZA not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(za_country.get("postal_code_regex") or ".*")
    print(f"Country: South Africa (id={za_country['id']})")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_no_codes = 0
    skipped_bad_regex = 0

    def add_record(code: str, town: str, kind: str) -> None:
        code = code.strip()
        if not code:
            return
        if code.isdigit() and len(code) < 4:
            code = code.zfill(4)
        if not regex.match(code):
            return
        locality = (town or "").strip()
        key = (code, locality.lower(), kind)
        if key in seen:
            return
        seen.add(key)
        record: Dict[str, object] = {
            "code": code,
            "country_id": int(za_country["id"]),
            "country_code": "ZA",
        }
        if locality:
            record["locality_name"] = locality
        record["type"] = kind
        record["source"] = "sapo-via-raramuridesign"
        records.append(record)

    for row in rows:
        box = (row.get("BoxCode") or "").strip()
        strc = (row.get("StrCode") or "").strip()
        town = (row.get("Town") or "").strip()
        if not box and not strc:
            skipped_no_codes += 1
            continue
        if box and strc and box == strc:
            add_record(box, town, "full")
        else:
            if box:
                # Track invalid codes against regex without blowing the dataset
                if regex.match(box.zfill(4) if box.isdigit() and len(box) < 4 else box):
                    add_record(box, town, "po_box")
                else:
                    skipped_bad_regex += 1
            if strc:
                if regex.match(strc.zfill(4) if strc.isdigit() and len(strc) < 4 else strc):
                    add_record(strc, town, "street")
                else:
                    skipped_bad_regex += 1

    print(f"Skipped (no codes):    {skipped_no_codes:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/ZA.json"
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
