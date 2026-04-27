#!/usr/bin/env python3
"""Mauritius -> contributions/postcodes/MU.json importer for #1039.

Source data
-----------
The community ``Samimveza/mauritius_postal_code`` repository ships
the Mauritius Post catalogue keyed by city -> sublocality:

    {"16eme Mille": [
        {"name": "Cite Anoushka", "code": "52601", "street": ""},
        ...
    ]}

Source URL: https://raw.githubusercontent.com/Samimveza/mauritius_postal_code/master/city-sublocality.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Walks city -> sublocality entries; emits one record per
   ``(5-digit code, sublocality + city)`` pair.
3. Ships country-only: source has no district mapping (``states.json``
   does carry 12 districts but the source's 144 cities don't directly
   align without a hand-curated crosswalk).
4. Writes contributions/postcodes/MU.json idempotently.

License & attribution
---------------------
- Source: Samimveza/mauritius_postal_code (open redistribution of
  Mauritius Post's publicly published index).
- Each row: ``source: "mauritius-post-via-Samimveza"``

Usage
-----
    python3 bin/scripts/sync/import_mauritius_postcodes.py
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
    "https://raw.githubusercontent.com/Samimveza/mauritius_postal_code/"
    "master/city-sublocality.json"
)


def fetch_json(url: str) -> dict:
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

    data = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    mu_country = next((c for c in countries if c.get("iso2") == "MU"), None)
    if mu_country is None:
        print("ERROR: MU not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(mu_country.get("postal_code_regex") or ".*")
    print(f"Country: Mauritius (id={mu_country['id']})")
    print(f"Source cities: {len(data):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for city, sublocs in data.items():
        if not isinstance(sublocs, list):
            continue
        for entry in sublocs:
            code = (entry.get("code") or "").strip()
            if not code:
                continue
            if not regex.match(code):
                skipped_bad_regex += 1
                continue
            sub_name = (entry.get("name") or "").strip()
            locality = ", ".join(p for p in (sub_name, city.strip()) if p)
            key = (code, locality.lower())
            if key in seen:
                continue
            seen.add(key)

            record: Dict[str, object] = {
                "code": code,
                "country_id": int(mu_country["id"]),
                "country_code": "MU",
            }
            if locality:
                record["locality_name"] = locality
            record["type"] = "full"
            record["source"] = "mauritius-post-via-Samimveza"
            records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MU.json"
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
