#!/usr/bin/env python3
"""Serbia -> contributions/postcodes/RS.json importer for #1039.

Source data
-----------
The community ``nebjak/serbia-zip-codes-js`` package ships Pošta
Srbije's catalogue as a flat JSON list of city + zip_code pairs:

    [{"city": "Beograd", "zip_code": "11000"}, ...]

Source URL: https://raw.githubusercontent.com/nebjak/serbia-zip-codes-js/master/data/serbia_zip_codes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Ships country-only (the source has no okrug / district mapping).
3. Writes contributions/postcodes/RS.json idempotently.

License & attribution
---------------------
- Source: nebjak/serbia-zip-codes-js (MIT) which redistributes the
  publicly published Pošta Srbije index.
- Each row: ``source: "posta-srbije-via-nebjak"``

Usage
-----
    python3 bin/scripts/sync/import_serbia_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/nebjak/serbia-zip-codes-js/"
    "master/data/serbia_zip_codes.json"
)


def fetch_json(url: str) -> List[dict]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    rs_country = next((c for c in countries if c.get("iso2") == "RS"), None)
    if rs_country is None:
        print("ERROR: RS not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(rs_country.get("postal_code_regex") or ".*")
    print(f"Country: Serbia (id={rs_country['id']})")
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for row in rows:
        code = (row.get("zip_code") or "").strip()
        if not code:
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        city = (row.get("city") or "").strip()
        key = (code, city.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(rs_country["id"]),
            "country_code": "RS",
        }
        if city:
            record["locality_name"] = city
        record["type"] = "full"
        record["source"] = "posta-srbije-via-nebjak"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/RS.json"
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
