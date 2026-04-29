#!/usr/bin/env python3
"""Malta -> contributions/postcodes/MT.json importer for #1039.

Source data
-----------
The community ``lucamuscat/Scrape_Malta_Addresses`` repository ships
MaltaPost's catalogue keyed by full postcode (e.g. "ATD 1010"):

    {" ATD 1010": {"latitude": 14.443686, "longitude": 35.891064,
                   "street": "Triq Tommaso Dingli "}}

Source URL: https://raw.githubusercontent.com/lucamuscat/Scrape_Malta_Addresses/master/output.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Normalises each key to the canonical "AAA NNNN" form expected by
   the country regex ``^[A-Z]{3}\\s?\\d{4}$``.
3. Ships country-only: mapping the 74 source 3-letter prefixes to
   CSC's 68 localities would need a hand-curated 74-entry table that
   is left for a follow-up.
4. Records carry the source's ``street`` as ``locality_name`` and
   centroid coordinates (the source's ``latitude``/``longitude``
   fields are swapped — Malta sits at ~35.9°N / 14.4°E so the value
   in ``latitude`` is the longitude and vice versa).
5. Writes contributions/postcodes/MT.json idempotently.

License & attribution
---------------------
- Source: lucamuscat/Scrape_Malta_Addresses (open scrape of MaltaPost
  search index).
- Each row: ``source: "maltapost-via-lucamuscat"``

Usage
-----
    python3 bin/scripts/sync/import_malta_postcodes.py
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
    "https://raw.githubusercontent.com/lucamuscat/Scrape_Malta_Addresses/"
    "master/output.json"
)

CODE_RE = re.compile(r"^([A-Z]{3})\s*(\d{4})$")


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
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
    mt_country = next((c for c in countries if c.get("iso2") == "MT"), None)
    if mt_country is None:
        print("ERROR: MT not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(mt_country.get("postal_code_regex") or ".*")
    print(f"Country: Malta (id={mt_country['id']})")
    print(f"Source rows: {len(data):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for raw_key, val in data.items():
        cleaned = (raw_key or "").strip().upper()
        m = CODE_RE.match(cleaned)
        if not m:
            skipped_bad_regex += 1
            continue
        code = f"{m.group(1)} {m.group(2)}"
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        street = (val.get("street") or "").strip() if isinstance(val, dict) else ""
        key = (code, street.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(mt_country["id"]),
            "country_code": "MT",
        }
        if street:
            record["locality_name"] = street
        if isinstance(val, dict):
            try:
                # The source's "latitude" field carries Malta longitude
                # values (~14°) and vice versa; un-swap on read.
                src_lat = float(val.get("latitude"))
                src_lon = float(val.get("longitude"))
                lat, lon = src_lon, src_lat
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    record["latitude"] = round(lat, 6)
                    record["longitude"] = round(lon, 6)
            except (TypeError, ValueError):
                pass
        record["type"] = "full"
        record["source"] = "maltapost-via-lucamuscat"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MT.json"
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
