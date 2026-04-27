#!/usr/bin/env python3
"""Bangladesh -> contributions/postcodes/BD.json importer for #1039.

Source data
-----------
The community ``saaiful/postcode-bd`` repository ships Bangladesh
Post's catalogue keyed by postcode. Each entry carries an ``en`` and
``bn`` (Bangla) variant:

    {"1206 ": {
        "en": {"division": "Dhaka", "district": "Dhaka ",
               "thana": "Dhaka ", "suboffice": "...", "postcode": "1206 "},
        "bn": {...}
    }}

Source URL: https://raw.githubusercontent.com/saaiful/postcode-bd/master/postcode.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves ``state_id`` by matching the source's ``district`` name
   against ``states.json`` (CSC's BD states use 2-digit district
   codes). Falls back to division-name match (CSC's letter iso2
   A-H) when the district isn't represented.
3. Emits one record per ``(postcode, suboffice)`` pair.
4. Writes contributions/postcodes/BD.json idempotently.

License & attribution
---------------------
- Source: saaiful/postcode-bd; data scraped from Bangladesh Post's
  publicly published postcode index.
- Each row: ``source: "bangladesh-post-via-saaiful"``

Usage
-----
    python3 bin/scripts/sync/import_bangladesh_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


SOURCE_URL = (
    "https://raw.githubusercontent.com/saaiful/postcode-bd/"
    "master/postcode.json"
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
    bd_country = next((c for c in countries if c.get("iso2") == "BD"), None)
    if bd_country is None:
        print("ERROR: BD not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(bd_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    bd_states = [s for s in states if s.get("country_id") == bd_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"].strip().lower(): s for s in bd_states}
    print(f"Country: Bangladesh (id={bd_country['id']}); states indexed: {len(bd_states)}")
    print(f"Source rows: {len(data):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    def resolve_state(district: str, division: str) -> Optional[dict]:
        if district:
            s = state_by_name.get(district.strip().lower())
            if s is not None:
                return s
        if division:
            s = state_by_name.get(division.strip().lower())
            if s is not None:
                return s
        return None

    for raw_code, blob in data.items():
        en = (blob or {}).get("en") or {}
        code = (en.get("postcode") or raw_code or "").strip()
        if not code:
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        suboffice = (en.get("suboffice") or "").strip()
        thana = (en.get("thana") or "").strip()
        locality = suboffice or thana
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(bd_country["id"]),
            "country_code": "BD",
        }
        state = resolve_state(en.get("district") or "", en.get("division") or "")
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "bangladesh-post-via-saaiful"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/BD.json"
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
