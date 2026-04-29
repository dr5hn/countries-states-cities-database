#!/usr/bin/env python3
"""Latvia -> contributions/postcodes/LV.json importer for #1039.

Source data
-----------
The community ``IcebergBuilder/pasta_indeksi`` repository ships a
flat list of every Latvijas Pasts ``LV-NNNN`` index across two
files: ``Novadi`` (counties) and ``Riga`` (capital districts).

Source URLs:
- https://raw.githubusercontent.com/IcebergBuilder/pasta_indeksi/master/Novadi
- https://raw.githubusercontent.com/IcebergBuilder/pasta_indeksi/master/Riga

What this script does
---------------------
1. Fetches both files via urllib (curl is blocked).
2. Strips the ``LV-`` prefix to obtain the canonical 4-digit form
   that matches the country regex ``^(?:LV)*(\\d{4})$``.
3. Ships country-only: source has no locality / state mapping.
4. Writes contributions/postcodes/LV.json idempotently.

License & attribution
---------------------
- Source: IcebergBuilder/pasta_indeksi; data is the publicly
  published Latvijas Pasts index.
- Each row: ``source: "latvijas-pasts-via-IcebergBuilder"``

Usage
-----
    python3 bin/scripts/sync/import_latvia_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URLS = [
    "https://raw.githubusercontent.com/IcebergBuilder/pasta_indeksi/master/Novadi",
    "https://raw.githubusercontent.com/IcebergBuilder/pasta_indeksi/master/Riga",
]

LV_LINE_RE = re.compile(r"^LV[-\s]?(\d{4})$")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    lv_country = next((c for c in countries if c.get("iso2") == "LV"), None)
    if lv_country is None:
        print("ERROR: LV not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(lv_country.get("postal_code_regex") or ".*")
    print(f"Country: Latvia (id={lv_country['id']})")

    seen: set = set()
    records: List[dict] = []
    for url in SOURCE_URLS:
        text = fetch_text(url)
        for line in text.splitlines():
            line = line.strip()
            m = LV_LINE_RE.match(line)
            if not m:
                continue
            code = m.group(1)
            if not regex.match(code):
                continue
            if code in seen:
                continue
            seen.add(code)
            records.append(
                {
                    "code": code,
                    "country_id": int(lv_country["id"]),
                    "country_code": "LV",
                    "type": "full",
                    "source": "latvijas-pasts-via-IcebergBuilder",
                }
            )

    print(f"Records emitted: {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/LV.json"
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
