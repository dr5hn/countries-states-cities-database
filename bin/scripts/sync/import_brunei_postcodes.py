#!/usr/bin/env python3
"""Brunei -> contributions/postcodes/BN.json importer for issue #1039.

Source data
-----------
The community ``xplorasia/brunei-zipcode`` repository publishes the
full Brunei Postal Services postcode list in CSV form:

    zipcode,area,city
    KF4138,"Kampong Bang Pukul, Bukit Sawat",Belait

The "city" column is actually the **district** (one of the four
Brunei districts). Codes follow the alphanumeric format `XXNNNN`
(2-letter prefix encoding the postal sector + 4-digit office code),
matching the country regex `^[A-Z]{2}\\d{4}$`.

Source URL: https://raw.githubusercontent.com/xplorasia/brunei-zipcode/master/bn-zipcode.csv

What this script does
---------------------
1. Fetches the CSV via urllib.
2. Maps the 4 source district labels onto CSC's 4 BN iso2 states
   via SOURCE_TO_ISO2 (handles 'Brunei Muara' -> CSC 'Brunei-Muara').
3. Emits one row per (code, area) pair.
4. Writes contributions/postcodes/BN.json idempotently.

License
-------
Repo has no LICENSE file. Postcode data is publicly published by the
Brunei Postal Services Department. Tier 5 (free redistribution
permitted, no formal licence) per #1039 license-tier policy.

Each row carries: ``source: "brunei-post-via-xplorasia"``

Usage
-----
    python3 bin/scripts/sync/import_brunei_postcodes.py
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
    "https://raw.githubusercontent.com/xplorasia/brunei-zipcode/"
    "master/bn-zipcode.csv"
)

# Source district label -> CSC iso2 in BN states.json
SOURCE_TO_ISO2: Dict[str, str] = {
    "Brunei Muara": "BM",  # CSC name is 'Brunei-Muara' (with hyphen)
    "Belait": "BE",
    "Tutong": "TU",
    "Temburong": "TE",
}


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

    text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    bn_country = next((c for c in countries if c.get("iso2") == "BN"), None)
    if bn_country is None:
        print("ERROR: BN not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(bn_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    bn_states = [s for s in states if s.get("country_id") == bn_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in bn_states if s.get("iso2")
    }
    print(
        f"Country: Brunei (id={bn_country['id']}); states indexed: {len(bn_states)}"
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
    unknown_district: Dict[str, int] = {}

    for row in rows:
        code = (row.get("zipcode") or "").strip().upper()
        if not code:
            skipped_no_code += 1
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        district = (row.get("city") or "").strip()
        area = (row.get("area") or "").strip()

        iso2 = SOURCE_TO_ISO2.get(district)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_district[district] = unknown_district.get(district, 0) + 1
            skipped_no_state += 1

        key = (code, area.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(bn_country["id"]),
            "country_code": "BN",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if area:
            record["locality_name"] = area
        record["type"] = "full"
        record["source"] = "brunei-post-via-xplorasia"
        records.append(record)

    print(f"Skipped (no code):     {skipped_no_code:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_district:
        print("Unknown district labels (not in SOURCE_TO_ISO2):")
        for d, n in sorted(unknown_district.items(), key=lambda x: -x[1]):
            print(f"  {d!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/BN.json"
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
