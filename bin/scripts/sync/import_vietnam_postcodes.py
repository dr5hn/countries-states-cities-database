#!/usr/bin/env python3
"""Vietnam -> contributions/postcodes/VN.json importer for #1039.

Source data
-----------
The community ``navuitag/dvhcvn`` repository ships Vietnam's
administrative-units catalogue, including province-level VNPost
postcodes. The MySQL dump exposes a ``provinces`` table:

    INSERT INTO `provinces` (`id`, `province_name`, `postcode`, ...)
    VALUES ('01', 'Thành phố Hà Nội', '100000', ...);

Source URL: https://raw.githubusercontent.com/navuitag/dvhcvn/master/database/database.sql

What this script does
---------------------
1. Fetches the SQL dump via urllib (curl is blocked).
2. Parses the ``provinces`` INSERT block with a tolerant regex.
3. Ships country-only (no state_id): Vietnam's 2024-2025
   administrative restructuring merged many of the source's 63
   pre-2024 provinces into the post-merger 34 provinces represented
   in CSC's ``states.json``, so a clean per-row state FK is no longer
   possible from this dataset (matches the SE/SI/ZA/GR precedent).
4. Writes contributions/postcodes/VN.json idempotently.

License & attribution
---------------------
- Source: navuitag/dvhcvn; the postcodes are VNPost's publicly
  published province-level codes.
- Each row: ``source: "vnpost-via-navuitag"``

Usage
-----
    python3 bin/scripts/sync/import_vietnam_postcodes.py
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
    "https://raw.githubusercontent.com/navuitag/dvhcvn/"
    "master/database/database.sql"
)

PROVINCES_INSERT_BLOCK = re.compile(
    r"INSERT\s+INTO\s+`provinces`.*?VALUES\s*(.*?);",
    re.IGNORECASE | re.DOTALL,
)
PROVINCE_ROW = re.compile(
    r"\(\s*'(?P<id>\d+)'\s*,\s*'(?P<name>[^']+)'\s*,\s*'(?P<postcode>\d{6})'"
)


def fetch_text(url: str) -> str:
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
        else fetch_text(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    vn_country = next((c for c in countries if c.get("iso2") == "VN"), None)
    if vn_country is None:
        print("ERROR: VN not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(vn_country.get("postal_code_regex") or ".*")
    print(f"Country: Vietnam (id={vn_country['id']})")

    block = PROVINCES_INSERT_BLOCK.search(text)
    if block is None:
        print("ERROR: provinces INSERT block not found", file=sys.stderr)
        return 2
    rows = list(PROVINCE_ROW.finditer(block.group(1)))
    print(f"Source province rows: {len(rows)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for m in rows:
        code = m.group("postcode").strip()
        name = m.group("name").strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        # Strip "Tỉnh " or "Thành phố " administrative prefix
        clean_name = re.sub(r"^(Tỉnh|Thành phố)\s+", "", name)
        key = (code, clean_name.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(vn_country["id"]),
            "country_code": "VN",
        }
        if clean_name:
            record["locality_name"] = clean_name
        record["type"] = "full"
        record["source"] = "vnpost-via-navuitag"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/VN.json"
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
