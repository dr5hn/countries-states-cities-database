#!/usr/bin/env python3
"""Ecuador -> contributions/postcodes/EC.json importer for #1039.

Source data
-----------
The community ``danielparsdq/codigos-postales-ecuador`` repository
ships a GeoJSON FeatureCollection with one feature per Ecuadorean
parish-level Correos del Ecuador 6-digit code:

    {"type": "Feature",
     "properties": {"codigo_postal": "010101", "provincia": "AZUAY",
                    "lon": "-79.0029", "lat": "-2.8964"},
     "geometry": {...}}

Source URL: https://raw.githubusercontent.com/danielparsdq/codigos-postales-ecuador/master/codigos_postales_ecuador.json

What this script does
---------------------
1. Fetches the GeoJSON via urllib (curl is blocked).
2. Resolves ``state_id`` via ASCII+space-fold name match against
   ``states.json`` (handles MORONA SANTIAGO -> Morona-Santiago).
3. Drops rows in ``ZONA NO DELIMITADA`` (no canonical state).
4. Writes contributions/postcodes/EC.json idempotently.

License & attribution
---------------------
- Source: danielparsdq/codigos-postales-ecuador (open redistribution
  of Correos del Ecuador 6-digit codes).
- Each row: ``source: "correos-del-ecuador-via-danielparsdq"``

Usage
-----
    python3 bin/scripts/sync/import_ecuador_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/danielparsdq/codigos-postales-ecuador/"
    "master/codigos_postales_ecuador.json"
)


def _fold(value: str) -> str:
    s = "".join(
        c for c in unicodedata.normalize("NFKD", (value or "").lower())
        if not unicodedata.combining(c)
    )
    # Collapse whitespace + hyphen to a single space so MORONA SANTIAGO
    # matches CSC's "Morona-Santiago".
    return re.sub(r"[\s\-]+", " ", s).strip()


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
    ec_country = next((c for c in countries if c.get("iso2") == "EC"), None)
    if ec_country is None:
        print("ERROR: EC not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(ec_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    ec_states = [s for s in states if s.get("country_id") == ec_country["id"]]
    state_by_fold: Dict[str, dict] = {_fold(s["name"]): s for s in ec_states}
    print(f"Country: Ecuador (id={ec_country['id']}); states indexed: {len(ec_states)}")

    feats = data.get("features", []) if isinstance(data, dict) else []
    print(f"Source features: {len(feats):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    skipped_undelimited = 0

    for feat in feats:
        props = feat.get("properties") or {}
        code = (props.get("codigo_postal") or "").strip()
        if not code:
            continue
        if code.isdigit() and len(code) == 5:
            code = "0" + code
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        province = (props.get("provincia") or "").strip()
        if "no delimitada" in province.lower():
            skipped_undelimited += 1
            continue

        key = (code, province.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(ec_country["id"]),
            "country_code": "EC",
        }
        state = state_by_fold.get(_fold(province))
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        else:
            skipped_no_state += 1

        if province:
            record["locality_name"] = province.title()
        try:
            lat = float(props.get("lat") or "")
            lon = float(props.get("lon") or "")
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                # String form matches existing contributions/postcodes/*.json
                # convention (AU, BE, etc.) and avoids float-serialisation drift.
                record["latitude"] = f"{lat:.6f}"
                record["longitude"] = f"{lon:.6f}"
        except (TypeError, ValueError):
            pass
        record["type"] = "full"
        record["source"] = "correos-del-ecuador-via-danielparsdq"
        records.append(record)

    print(f"Skipped (regex fail):    {skipped_bad_regex:,}")
    print(f"Skipped (undelimited):   {skipped_undelimited:,}")
    print(f"Records emitted:         {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:            {matched_state:,} ({pct}%)")
    print(f"  no state FK:           {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/EC.json"
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
