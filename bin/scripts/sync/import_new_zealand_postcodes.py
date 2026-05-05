#!/usr/bin/env python3
"""New Zealand -> contributions/postcodes/NZ.json importer for issue #1039.

Source data
-----------
The community ``WaimateWihongi/nz-postcodes`` repository ships
``postcodes.json`` — 900 unique 4-digit New Zealand postcodes with
WGS-84 lat/lng centroids and structured names.

    {"postcode": "0101",
     "lat": "-35.7487287", "lon": "174.3108415",
     "name": "Whangarei District, Northland, 0101, New Zealand / Aotearoa",
     "island": "North Island"}

Source URL: https://raw.githubusercontent.com/WaimateWihongi/nz-postcodes/master/postcodes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves state FK by substring-matching the ``name`` field
   against DESC_TO_ISO2 — a 30+-entry table mapping NZ region
   names plus common district/city sub-region names back to one
   of the 17 CSC regions.
3. Emits one row per postcode with lat/lng + structured name.
4. Writes contributions/postcodes/NZ.json idempotently.

State FK strategy
-----------------
Source's ``name`` field is inconsistently structured — sometimes
the second comma-separated field is the region (`'Whangarei
District, Northland, 0101, ...'`) and sometimes it's a district
or community name (`'Banks Peninsula Community, ...'`,
`'Christchurch City, ...'`).

DESC_TO_ISO2 maps both the 17 CSC regions and 15+ common district
/ city / community labels back to their parent CSC region. Records
where no entry matches ship country-only.

License & attribution
---------------------
- Source: WaimateWihongi/nz-postcodes (no formal LICENSE)
- Upstream: OpenStreetMap (per repo README — Nominatim-derived)
- Each row: ``source: "osm-via-waimate-wihongi"``

OSM is acceptable per #1039 license-tier policy (Tier 5, free
redistribution permitted). Note: explicitly NOT GeoNames-derived.

Usage
-----
    python3 bin/scripts/sync/import_new_zealand_postcodes.py
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
    "https://raw.githubusercontent.com/WaimateWihongi/nz-postcodes/"
    "master/postcodes.json"
)

# Region/district/city descriptor -> CSC iso2.
# Direct CSC region names + common sub-region labels (districts,
# cities, communities) that are part of a CSC region.
DESC_TO_ISO2: Dict[str, str] = {
    # 17 CSC regions (canonical English form)
    "Auckland": "AUK",
    "Bay of Plenty": "BOP",
    "Canterbury": "CAN",
    "Chatham Islands": "CIT",
    "Gisborne": "GIS",
    "Hawke's Bay": "HKB",
    "Marlborough": "MBH",
    "Manawatu-Whanganui": "MWT",
    "Manawatū-Whanganui": "MWT",  # source uses macron form
    "Nelson": "NSN",
    "Northland": "NTL",
    "Otago": "OTA",
    "Southland": "STL",
    "Tasman": "TAS",
    "Taranaki": "TKI",
    "Wellington": "WGN",
    "Waikato": "WKO",
    "West Coast": "WTC",
    # District / city / community sub-region labels
    "Far North District": "NTL",
    "Christchurch": "CAN",
    "Christchurch City": "CAN",
    "Banks Peninsula Community": "CAN",
    "Coastal-Burwood Community": "CAN",
    "Halswell-Hornby-Riccarton Community": "CAN",
    "Linwood-Central-Heathcote Community": "CAN",
    "Papanui-Innes Community": "CAN",
    "Spreydon-Cashmere Community": "CAN",
    "Lower Hutt": "WGN",
    "Porirua": "WGN",
    "Martinborough Community": "WGN",
    "South Wairarapa District": "WGN",
    "Napier City": "HKB",
    "Central Otago District": "OTA",
    "Queenstown-Lakes District": "OTA",
    "Southland District": "STL",
}


def fetch_json(url: str) -> List[dict]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def resolve_iso2(name: str) -> Optional[str]:
    """Find the first DESC_TO_ISO2 match in any comma-field of name."""
    parts = [p.strip() for p in name.split(",")]
    for part in parts:
        if part in DESC_TO_ISO2:
            return DESC_TO_ISO2[part]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    rows = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    print(f"Source rows: {len(rows):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    nz_country = next((c for c in countries if c.get("iso2") == "NZ"), None)
    if nz_country is None:
        print("ERROR: NZ not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(nz_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    nz_states = [s for s in states if s.get("country_id") == nz_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in nz_states if s.get("iso2")
    }
    print(
        f"Country: New Zealand (id={nz_country['id']}); "
        f"states indexed: {len(nz_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("postcode") or "").strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        name = (row.get("name") or "").strip()
        iso2 = resolve_iso2(name)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            skipped_no_state += 1

        # Locality: drop the trailing 'New Zealand / Aotearoa' + the
        # 4-digit postcode field; keep first 1-2 descriptive parts.
        parts = [p.strip() for p in name.split(",")]
        descriptive = [
            p
            for p in parts
            if p
            and not p.isdigit()
            and "New Zealand" not in p
            and "Aotearoa" not in p
        ]
        locality = ", ".join(descriptive[:2]) if descriptive else ""

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(nz_country["id"]),
            "country_code": "NZ",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        lat = (row.get("lat") or "").strip()
        lon = (row.get("lon") or "").strip()
        if lat and lon:
            record["latitude"] = lat
            record["longitude"] = lon
        record["type"] = "full"
        record["source"] = "osm-via-waimate-wihongi"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/NZ.json"
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
