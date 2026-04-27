#!/usr/bin/env python3
"""Greece -> contributions/postcodes/GR.json importer for issue #1039.

Source data
-----------
The community ``MentatInnovations/grpostcodes`` repository (CC-BY)
ships a CSV of every Greek 5-digit postcode with its Hellenic Post
"territory" name and approximate centroid coordinates. Each row has:

    tk, territory, lat, lon

Source URL: https://raw.githubusercontent.com/MentatInnovations/grpostcodes/master/data/postcode_lat_long_output_file.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked in the harness).
2. Emits one record per postcode with the Greek territory name as
   ``locality_name`` plus latitude/longitude.
3. Ships country-only (no state_id): Greek postcodes do not align
   with the 13 peripheries / 7 decentralised administrations cleanly
   (matches the SE/SI/ZA precedent in this repo).
4. Writes contributions/postcodes/GR.json idempotently.

License & attribution
---------------------
- Source: MentatInnovations/grpostcodes; data compiled via Hellenic
  Post and Google Maps geocoding.
- Each row: ``source: "elta-via-MentatInnovations"``

Usage
-----
    python3 bin/scripts/sync/import_greece_postcodes.py
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
    "https://raw.githubusercontent.com/MentatInnovations/grpostcodes/"
    "master/data/postcode_lat_long_output_file.csv"
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
    gr_country = next((c for c in countries if c.get("iso2") == "GR"), None)
    if gr_country is None:
        print("ERROR: GR not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(gr_country.get("postal_code_regex") or ".*")
    print(f"Country: Greece (id={gr_country['id']})")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for row in rows:
        code = (row.get("tk") or "").strip()
        if not code:
            continue
        if code.isdigit() and len(code) == 4:
            code = "0" + code
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        territory = (row.get("territory") or "").strip()
        key = (code, territory.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(gr_country["id"]),
            "country_code": "GR",
        }
        if territory:
            record["locality_name"] = territory
        try:
            lat = float(row.get("lat") or "")
            lon = float(row.get("lon") or "")
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                record["latitude"] = round(lat, 6)
                record["longitude"] = round(lon, 6)
        except (TypeError, ValueError):
            pass
        record["type"] = "full"
        record["source"] = "elta-via-MentatInnovations"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/GR.json"
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
