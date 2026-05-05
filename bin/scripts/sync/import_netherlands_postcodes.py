#!/usr/bin/env python3
"""Netherlands -> contributions/postcodes/NL.json importer for issue #1039.

Source data
-----------
The community ``mevdschee/postcodes-nl`` GitHub release ships a
17 MB 7zip archive containing a 401 MB CSV with all Dutch street-
level address data joining each postcode (PC6: 4-digit + 2-letter)
to a woonplaats (settlement).

Source URL: https://github.com/mevdschee/postcodes-nl/releases/latest

What this script does
---------------------
1. Resolves the latest release via the GitHub API.
2. Fetches the 17 MB 7zip and extracts the CSV in-memory via py7zr.
3. Aggregates 9M+ street-level rows into 4,072 unique PC4
   (4-digit) districts, picking the most-common woonplaats per PC4
   as the representative locality.
4. Writes contributions/postcodes/NL.json idempotently.

Why PC4 (not PC6)
-----------------
Unique PC6 codes total 467,109. JSON-export at PC6 level would
exceed the in-band cities/*.json size envelope (PT.json at 38 MB
is the current largest; PC6 expansion would be ~70 MB).

PC4 (4-digit) is the standard Dutch district-level postcode
granularity (~4,000 districts), comparable to UK postcode areas
and Canada FSAs already shipped at this scale.

Why country-only state FK
-------------------------
The Netherlands' 12 provinces span PC4 ranges with significant
overlap (e.g. PC4 1xxx covers parts of Noord-Holland and Flevoland).
A 1:1 PC4 -> province map would be misleading. CSC matches the
SE / SI / GB precedent for sources that don't map cleanly to a
hierarchy.

Regex fix
---------
Before this PR, countries.json had NL regex `^\\d{4}\\s?[a-zA-Z]{2}$`
(PC6 only). Updated to `^\\d{4}(?:\\s?[A-Za-z]{2})?$` to accept
PC4 also, matching the mixed-granularity pattern already permitted
for GB / TW / CA / IR.

Dependency
----------
- ``py7zr`` (LGPL, pure-Python 7zip reader). Install via:
    python3 -m pip install py7zr

License & attribution
---------------------
- Source: mevdschee/postcodes-nl (LGPL-3 per repo LICENSE)
- Upstream: Dutch Kadaster / BAG (Basisregistratie Adressen en
  Gebouwen), public open-data lookup
- Each row: ``source: "bag-via-mevdschee"``

Usage
-----
    python3 bin/scripts/sync/import_netherlands_postcodes.py
"""

from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import os
import re
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, List

import py7zr


RELEASES_API = "https://api.github.com/repos/mevdschee/postcodes-nl/releases/latest"


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def resolve_archive_url() -> str:
    req = urllib.request.Request(
        RELEASES_API, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        meta = json.loads(r.read())
    for asset in meta.get("assets", []):
        if asset.get("name", "").endswith(".7z"):
            return asset["browser_download_url"]
    raise RuntimeError("No .7z asset in latest release")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local 7z (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.input:
        raw = Path(args.input).read_bytes()
    else:
        url = resolve_archive_url()
        print(f"fetching {url}")
        raw = fetch_bytes(url)
    print(f"7z size: {len(raw):,} bytes")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    nl_country = next((c for c in countries if c.get("iso2") == "NL"), None)
    if nl_country is None:
        print("ERROR: NL not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(nl_country.get("postal_code_regex") or ".*")
    print(f"Country: Netherlands (id={nl_country['id']})")

    # Aggregate to PC4 with most-common woonplaats per PC4
    pc4_woonplaatsen: Dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )

    with tempfile.TemporaryDirectory() as tmp:
        with py7zr.SevenZipFile(io.BytesIO(raw), mode="r") as archive:
            archive.extractall(path=tmp)
        csv_path = next(
            os.path.join(tmp, n)
            for n in os.listdir(tmp)
            if n.endswith(".csv")
        )
        print(f"CSV: {os.path.getsize(csv_path):,} bytes")
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i and i % 2_000_000 == 0:
                    print(f"  processed {i:,}")
                pc = (row.get("postcode") or "").replace(" ", "").upper()
                wp = (row.get("woonplaats") or "").strip()
                if len(pc) >= 4 and pc[:4].isdigit():
                    pc4_woonplaatsen[pc[:4]][wp] += 1

    print(f"unique PC4: {len(pc4_woonplaatsen):,}")

    records: List[dict] = []
    skipped_bad_regex = 0

    for pc4 in sorted(pc4_woonplaatsen):
        if not regex.match(pc4):
            skipped_bad_regex += 1
            continue
        wp = pc4_woonplaatsen[pc4].most_common(1)[0][0]

        record: Dict[str, object] = {
            "code": pc4,
            "country_id": int(nl_country["id"]),
            "country_code": "NL",
        }
        if wp:
            record["locality_name"] = wp
        record["type"] = "area"
        record["source"] = "bag-via-mevdschee"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/NL.json"
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
