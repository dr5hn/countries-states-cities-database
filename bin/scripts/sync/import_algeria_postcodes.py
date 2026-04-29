#!/usr/bin/env python3
"""Algeria -> contributions/postcodes/DZ.json importer for #1039.

Source data
-----------
The community ``badre429/dzcities`` repository ships every Algerian
commune with its 4-digit Algérie Poste code, the wilaya number, and
both Arabic + Latin names with centroid coordinates:

    {"code": 1001, "w": 1, "ar": "أدرار", "name": "Adrar",
     "lng": 27.9763317, "lat": -0.4841573}

Source URL: https://raw.githubusercontent.com/badre429/dzcities/master/all.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves ``state_id`` directly from the wilaya number, which
   matches CSC's 2-digit numeric ``state.iso2`` for Algeria.
3. Pads codes to the 5-digit canonical form (the source ships
   integer codes; values <10000 represent codes that begin with 0).
4. Writes contributions/postcodes/DZ.json idempotently.

License & attribution
---------------------
- Source: badre429/dzcities (publicly redistributed Algérie Poste data).
- Each row: ``source: "algerie-poste-via-badre429"``

Usage
-----
    python3 bin/scripts/sync/import_algeria_postcodes.py
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
    "https://raw.githubusercontent.com/badre429/dzcities/master/all.json"
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
    dz_country = next((c for c in countries if c.get("iso2") == "DZ"), None)
    if dz_country is None:
        print("ERROR: DZ not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(dz_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    dz_states = [s for s in states if s.get("country_id") == dz_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        (s.get("iso2") or "").upper(): s for s in dz_states if s.get("iso2")
    }
    print(f"Country: Algeria (id={dz_country['id']}); states indexed: {len(dz_states)}")
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        raw = row.get("code")
        if raw is None:
            continue
        code = str(raw).strip().zfill(5)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        name = (row.get("name") or "").strip()
        key = (code, name.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(dz_country["id"]),
            "country_code": "DZ",
        }
        wilaya = row.get("w")
        if wilaya is not None:
            iso2 = f"{int(wilaya):02d}"
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
            else:
                skipped_no_state += 1
        else:
            skipped_no_state += 1

        if name:
            record["locality_name"] = name
        try:
            lat = float(row.get("lng"))
            lon = float(row.get("lat"))
            # Source field names are swapped; lng holds latitude and lat
            # holds longitude in the ``badre429/dzcities`` JSON.
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                record["latitude"] = round(lat, 6)
                record["longitude"] = round(lon, 6)
        except (TypeError, ValueError):
            pass
        record["type"] = "full"
        record["source"] = "algerie-poste-via-badre429"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/DZ.json"
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
