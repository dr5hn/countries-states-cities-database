#!/usr/bin/env python3
"""Somalia -> contributions/postcodes/SO.json importer for issue #1039.

Source data
-----------
The community ``yaasiinaxmed/Somali-Postal-Code-Explorer`` repository
ships a TypeScript array of Somali postal codes:

    { city: 'Mogadishu', postalCode: '1001', region: 'Banaadir',
      latitude: 2.0469, longitude: 45.3182 }

Approximately 70 records covering all major Somali cities + lat/lng
centroids + region names.

Source URL: https://raw.githubusercontent.com/yaasiinaxmed/Somali-Postal-Code-Explorer/main/data/postal-codes.ts

What this script does
---------------------
1. Fetches the TypeScript file via urllib.
2. Parses each ``{ ... }`` literal with regex (TypeScript syntax close
   enough to JSON for our needs).
3. Resolves state FK via 18-entry REGION_TO_ISO2 (handles Somali +
   Somaliland regional naming variants: 'Hiiraan' alias, 'Galmudug'
   semi-autonomous region -> Galguduud, etc.).
4. Writes contributions/postcodes/SO.json idempotently.

Regex fix
---------
Before this PR, countries.json had SO regex `^[A-Z]{2}\\d{5}$` which
required a 2-letter prefix (e.g. 'BN12345'). The actual Somalia
Postal Service codes (post-2019 reorganization) are 4-5 digit
numeric only. Updated regex to accept both forms:
`^([A-Z]{2}\\s*\\d{5}|\\d{4,5})$`.

Coverage upgrade
----------------
Resolves the research-doc Tier C dead-end note for Somalia. This
MIT-licensed mirror covers ~70 cities across all regions.

License & attribution
---------------------
- Source: yaasiinaxmed/Somali-Postal-Code-Explorer (MIT)
- Each row: ``source: "somali-postal-code-explorer"``

Usage
-----
    python3 bin/scripts/sync/import_somalia_postcodes.py
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
    "https://raw.githubusercontent.com/yaasiinaxmed/Somali-Postal-Code-Explorer/"
    "main/data/postal-codes.ts"
)

# Source region label -> CSC iso2.
REGION_TO_ISO2: Dict[str, str] = {
    "Awdal": "AW",
    "Banaadir": "BN",
    "Bari": "BR",
    "Bay": "BY",
    "Bakool": "BK",
    "Galguduud": "GA",
    "Gedo": "GE",
    "Hiran": "HI",
    "Hiiraan": "HI",  # Somali spelling variant
    "Lower Juba": "JH",
    "Middle Juba": "JD",
    "Lower Shabelle": "SH",
    "Middle Shabelle": "SD",
    "Mudug": "MU",
    "Nugal": "NU",
    "Sanaag": "SA",
    "Sool": "SO",
    "Togdheer": "TO",
    "Woqooyi Galbeed": "WO",
    # Semi-autonomous regions / federal members map to nearest CSC region:
    "Galmudug": "GA",       # Galmudug state covers Galguduud + parts of Mudug
    "Somaliland": "TO",     # Sheikh district sits in Togdheer
}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def parse_ts_records(text: str) -> List[dict]:
    """Parse `{ city: '...', postalCode: '...', region: '...',
    latitude: N, longitude: N }` literals from TypeScript source."""
    pattern = re.compile(
        r"\{\s*city:\s*'([^']*)'\s*,\s*"
        r"postalCode:\s*'([^']*)'\s*,\s*"
        r"region:\s*'([^']*)'\s*,\s*"
        r"latitude:\s*([\-\d.]+)\s*,\s*"
        r"longitude:\s*([\-\d.]+)\s*\}",
        re.M,
    )
    return [
        {
            "city": m[0],
            "postalCode": m[1],
            "region": m[2],
            "latitude": m[3],
            "longitude": m[4],
        }
        for m in pattern.findall(text)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local TS (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_text(SOURCE_URL)
    )
    rows = parse_ts_records(text)
    print(f"Source records: {len(rows):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    so_country = next((c for c in countries if c.get("iso2") == "SO"), None)
    if so_country is None:
        print("ERROR: SO not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(so_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    so_states = [s for s in states if s.get("country_id") == so_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in so_states if s.get("iso2")
    }
    print(
        f"Country: Somalia (id={so_country['id']}); "
        f"states indexed: {len(so_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_regions: Dict[str, int] = {}

    for row in rows:
        code = row["postalCode"].strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        region = row["region"].strip()
        iso2 = REGION_TO_ISO2.get(region)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_regions[region] = unknown_regions.get(region, 0) + 1
            skipped_no_state += 1

        locality = row["city"].strip()
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(so_country["id"]),
            "country_code": "SO",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        if row["latitude"] and row["longitude"]:
            record["latitude"] = row["latitude"]
            record["longitude"] = row["longitude"]
        record["type"] = "full"
        record["source"] = "somali-postal-code-explorer"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_regions:
        print("Unknown regions:")
        for r, n in sorted(unknown_regions.items(), key=lambda x: -x[1]):
            print(f"  {r!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/SO.json"
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
