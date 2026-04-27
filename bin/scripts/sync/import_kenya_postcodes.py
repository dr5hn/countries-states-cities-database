#!/usr/bin/env python3
"""Kenya -> contributions/postcodes/KE.json importer for #1039.

Source data
-----------
The community ``njoguamos/kenya-postal-codes`` repository ships
Posta Kenya (Postal Corporation of Kenya) office codes:

    {"id": 1, "code": 40101, "office": "Ahero"}

Source URL: https://raw.githubusercontent.com/njoguamos/kenya-postal-codes/master/src/kenya-postal-codes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Pads codes to the 5-digit canonical form.
3. Ships country-only: source has no county / region mapping.
4. Writes contributions/postcodes/KE.json idempotently.

License & attribution
---------------------
- Source: njoguamos/kenya-postal-codes (open redistribution of
  Posta Kenya's publicly published office index).
- Each row: ``source: "posta-kenya-via-njoguamos"``

Usage
-----
    python3 bin/scripts/sync/import_kenya_postcodes.py
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
    "https://raw.githubusercontent.com/njoguamos/kenya-postal-codes/"
    "master/src/kenya-postal-codes.json"
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
    ke_country = next((c for c in countries if c.get("iso2") == "KE"), None)
    if ke_country is None:
        print("ERROR: KE not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ke_country.get("postal_code_regex") or ".*")
    print(f"Country: Kenya (id={ke_country['id']})")
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0

    for row in rows:
        raw = row.get("code")
        if raw is None:
            continue
        code = str(raw).strip().zfill(5)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        office = (row.get("office") or "").strip()
        key = (code, office.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ke_country["id"]),
            "country_code": "KE",
        }
        if office:
            record["locality_name"] = office
        record["type"] = "full"
        record["source"] = "posta-kenya-via-njoguamos"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/KE.json"
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
