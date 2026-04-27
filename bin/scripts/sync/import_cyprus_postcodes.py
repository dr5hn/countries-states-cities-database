#!/usr/bin/env python3
"""Cyprus -> contributions/postcodes/CY.json importer for #1039.

Source data
-----------
The community ``georgioupanayiotis/zip-postal-codes-cyprus``
repository ships Cyprus Post's catalogue keyed by street with
Postcode + Municipality + District:

    {"Street": "1 Apriliou", "Postcode": 2006,
     "Municipality": "Strovolos", "District": "Lefkosia"}

Source URL: https://raw.githubusercontent.com/georgioupanayiotis/zip-postal-codes-cyprus/master/postcodes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves ``state_id`` via case-insensitive name match against
   ``states.json`` with a 5-entry STATE_ALIASES bridge for the
   Greek-form district names ("Lefkosia" -> "Nicosia (Lefkoşa)" etc.).
3. Dedupes at (postcode, municipality) granularity (multiple streets
   share the same postcode within a municipality).
4. Writes contributions/postcodes/CY.json idempotently.

License & attribution
---------------------
- Source: georgioupanayiotis/zip-postal-codes-cyprus (open
  redistribution of Cyprus Post's publicly published index).
- Each row: ``source: "cyprus-post-via-georgioupanayiotis"``

Usage
-----
    python3 bin/scripts/sync/import_cyprus_postcodes.py
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
    "https://raw.githubusercontent.com/georgioupanayiotis/zip-postal-codes-cyprus/"
    "master/postcodes.json"
)

# Source District (lowercased) -> CSC states.json district lookup helper.
# CSC names embed both Greek and Turkish forms in parentheses
# ("Nicosia (Lefkoşa)"); the Greek form here is the source's own.
DISTRICT_ALIASES: Dict[str, str] = {
    "lefkosia":   "Nicosia (Lefkoşa)",
    "lemesos":    "Limassol (Leymasun)",
    "larnaka":    "Larnaca (Larnaka)",
    "ammochostos": "Famagusta (Mağusa)",
    "pafos":      "Paphos (Pafos)",
}


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
    cy_country = next((c for c in countries if c.get("iso2") == "CY"), None)
    if cy_country is None:
        print("ERROR: CY not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(cy_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    cy_states = [s for s in states if s.get("country_id") == cy_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"].lower(): s for s in cy_states}
    print(f"Country: Cyprus (id={cy_country['id']}); states indexed: {len(cy_states)}")
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        raw = row.get("Postcode")
        if raw is None:
            continue
        code = str(raw).strip().zfill(4)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        municipality = (row.get("Municipality") or "").strip()
        district = (row.get("District") or "").strip()
        key = (code, municipality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(cy_country["id"]),
            "country_code": "CY",
        }
        target = DISTRICT_ALIASES.get(district.lower(), district)
        state = state_by_name.get(target.lower())
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if municipality:
            record["locality_name"] = municipality
        record["type"] = "full"
        record["source"] = "cyprus-post-via-georgioupanayiotis"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/CY.json"
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
