#!/usr/bin/env python3
"""Moldova -> contributions/postcodes/MD.json importer for #1039.

Source data
-----------
The community ``vasilcovsky/moldova-geodata`` repository ships per-
district CSV files mapping each Poșta Moldovei 4-digit code to the
locality name + centroid coordinates:

    2032,Chişinău,47.00560,28.85750
    2032,…

Source URL: https://api.github.com/repos/vasilcovsky/moldova-geodata/contents/data

What this script does
---------------------
1. Lists the data/ directory via the GitHub API to enumerate
   district filenames.
2. Fetches each district's CSV via urllib (curl is blocked).
3. Resolves ``state_id`` from the filename via ASCII-fold name match.
4. Prefixes every code with the canonical ``MD-`` (the country regex
   ``^MD-\\d{4}$`` requires the prefix).
5. Emits one record per ``(prefixed code, locality)`` pair.
6. Writes contributions/postcodes/MD.json idempotently.

License & attribution
---------------------
- Source: vasilcovsky/moldova-geodata (open redistribution of Poșta
  Moldovei index plus geocoded centroids).
- Each row: ``source: "posta-moldovei-via-vasilcovsky"``

Usage
-----
    python3 bin/scripts/sync/import_moldova_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List


GH_LIST_URL = (
    "https://api.github.com/repos/vasilcovsky/moldova-geodata/contents/data"
)
RAW_BASE = (
    "https://raw.githubusercontent.com/vasilcovsky/moldova-geodata/master/data/"
)


def _fold(value: str) -> str:
    s = "".join(
        c for c in unicodedata.normalize("NFKD", (value or "").lower())
        if not unicodedata.combining(c)
    )
    return s.strip()


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def list_files() -> List[str]:
    resp = json.loads(fetch_text(GH_LIST_URL))
    return [f["name"] for f in resp if f["name"].endswith(".csv")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    md_country = next((c for c in countries if c.get("iso2") == "MD"), None)
    if md_country is None:
        print("ERROR: MD not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(md_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    md_states = [s for s in states if s.get("country_id") == md_country["id"]]
    state_by_fold: Dict[str, dict] = {_fold(s["name"]): s for s in md_states}
    print(f"Country: Moldova (id={md_country['id']}); states indexed: {len(md_states)}")

    files = list_files()
    print(f"Source files: {len(files)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for filename in files:
        district = filename.rsplit(".", 1)[0]
        state = state_by_fold.get(_fold(district))
        url = RAW_BASE + urllib.parse.quote(filename)
        text = fetch_text(url)
        for row in csv.reader(io.StringIO(text)):
            if not row or len(row) < 2:
                continue
            raw_code = row[0].strip()
            if not raw_code:
                continue
            code = f"MD-{raw_code.zfill(4)}"
            if not regex.match(code):
                skipped_bad_regex += 1
                continue
            locality = (row[1] or "").strip()
            key = (code, locality.lower())
            if key in seen:
                continue
            seen.add(key)

            record: Dict[str, object] = {
                "code": code,
                "country_id": int(md_country["id"]),
                "country_code": "MD",
            }
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = state.get("iso2")
                matched_state += 1
            else:
                skipped_no_state += 1

            if locality:
                record["locality_name"] = locality
            try:
                lat = float(row[2]) if len(row) > 2 else None
                lon = float(row[3]) if len(row) > 3 else None
                if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
                    record["latitude"] = round(lat, 6)
                    record["longitude"] = round(lon, 6)
            except (TypeError, ValueError, IndexError):
                pass
            record["type"] = "full"
            record["source"] = "posta-moldovei-via-vasilcovsky"
            records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/MD.json"
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
