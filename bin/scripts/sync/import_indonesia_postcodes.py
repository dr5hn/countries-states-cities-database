#!/usr/bin/env python3
"""Indonesia -> contributions/postcodes/ID.json importer for issue #1039.

Source data
-----------
The community ``pentagonal/Indonesia-Postal-Code`` repository (MIT)
ships an exhaustive JSON of every Pos Indonesia 5-digit postcode with
its administrative hierarchy. Each row has:

    {
      "urban":         <kelurahan / desa>,
      "sub_district":  <kecamatan>,
      "city":          <kabupaten / kota>,
      "province_code": <BPS 2-digit code>,
      "postal_code":   <5-digit code>
    }

Source URL: https://raw.githubusercontent.com/pentagonal/Indonesia-Postal-Code/master/Json/postal_array.json

What this script does
---------------------
1. Fetches the postal_array JSON via urllib (curl is blocked).
2. Maps the BPS 2-digit province code to CSC's ``states.json`` iso2
   via a hand-curated 34-entry table (the post-2022 Papua splits do
   not yet appear in the source feed and are not surfaced here).
3. Dedupes at (postal_code, city) granularity (each Pos code is
   shared by many urban/sub-district names within a single city).
4. Writes contributions/postcodes/ID.json idempotently.

License & attribution
---------------------
- Source: pentagonal/Indonesia-Postal-Code (MIT) which redistributes
  publicly published Pos Indonesia data.
- Each row: ``source: "pos-indonesia-via-pentagonal"``

Usage
-----
    python3 bin/scripts/sync/import_indonesia_postcodes.py
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
    "https://raw.githubusercontent.com/pentagonal/Indonesia-Postal-Code/"
    "master/Json/postal_array.json"
)

# BPS 2-digit province code -> CSC iso2 (states.json).
# Pre-2022 boundaries; Papua subdivisions added in 2022 are not yet
# present in the source feed.
BPS_TO_ISO2: Dict[str, str] = {
    "11": "AC",  # Aceh
    "12": "SU",  # Sumatera Utara
    "13": "SB",  # Sumatera Barat
    "14": "RI",  # Riau
    "15": "JA",  # Jambi
    "16": "SS",  # Sumatera Selatan
    "17": "BE",  # Bengkulu
    "18": "LA",  # Lampung
    "19": "BB",  # Kepulauan Bangka Belitung
    "21": "KR",  # Kepulauan Riau
    "31": "JK",  # DKI Jakarta
    "32": "JB",  # Jawa Barat
    "33": "JT",  # Jawa Tengah
    "34": "YO",  # DI Yogyakarta
    "35": "JI",  # Jawa Timur
    "36": "BT",  # Banten
    "51": "BA",  # Bali
    "52": "NB",  # Nusa Tenggara Barat
    "53": "NT",  # Nusa Tenggara Timur
    "61": "KB",  # Kalimantan Barat
    "62": "KT",  # Kalimantan Tengah
    "63": "KS",  # Kalimantan Selatan
    "64": "KI",  # Kalimantan Timur
    "65": "KU",  # Kalimantan Utara
    "71": "SA",  # Sulawesi Utara
    "72": "ST",  # Sulawesi Tengah
    "73": "SN",  # Sulawesi Selatan
    "74": "SG",  # Sulawesi Tenggara
    "75": "GO",  # Gorontalo
    "76": "SR",  # Sulawesi Barat
    "81": "MA",  # Maluku
    "82": "MU",  # Maluku Utara
    "91": "PA",  # Papua
    "92": "PB",  # Papua Barat
}


def fetch_json(url: str) -> List[dict]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
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
    id_country = next((c for c in countries if c.get("iso2") == "ID"), None)
    if id_country is None:
        print("ERROR: ID not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(id_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    id_states = [s for s in states if s.get("country_id") == id_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        (s.get("iso2") or "").upper(): s for s in id_states if s.get("iso2")
    }
    print(f"Country: Indonesia (id={id_country['id']}); states indexed: {len(id_states)}")
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for row in rows:
        code = (row.get("postal_code") or "").strip()
        if not code:
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        city = (row.get("city") or "").strip().title()
        key = (code, city.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(id_country["id"]),
            "country_code": "ID",
        }
        prov = (row.get("province_code") or "").strip()
        iso2 = BPS_TO_ISO2.get(prov)
        if iso2:
            state = state_by_iso2.get(iso2)
            if state is not None:
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
            else:
                skipped_no_state += 1
        else:
            skipped_no_state += 1

        if city:
            record["locality_name"] = city
        record["type"] = "full"
        record["source"] = "pos-indonesia-via-pentagonal"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/ID.json"
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
