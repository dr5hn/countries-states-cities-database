#!/usr/bin/env python3
"""Peru -> contributions/postcodes/PE.json importer for issue #1039.

Source data
-----------
The community ``peru-pe/cpn`` repository ships ``onlyCodes.json`` —
the 2,669 SERPOST 5-digit Código Postal Nacional codes published by
Peru's Ministerio de Transportes y Comunicaciones.

    ["01001", "01000", "01230", ...]

The 2-digit prefix is the department code (alphabetical, 01-25).

Source URL: https://raw.githubusercontent.com/peru-pe/cpn/master/onlyCodes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves state FK via 2-digit prefix -> CSC iso2 (PREFIX_TO_ISO2,
   25-entry hand map matching SERPOST's alphabetical ordering).
3. Writes contributions/postcodes/PE.json idempotently.

Locality
--------
Source ships postcode-only (no district / locality / centroid). Each
record carries `state_id` + `state_code` but no `locality_name` —
matching the country-only-with-state pattern used for similar lists.

Research-doc correction
-----------------------
The research doc Tier B note for Peru read
`UBIGEO admin codes != SERPOST 5-digit postal codes`. That note was
based on `mvegap/ubigeo-peru-select` which exposed UBIGEO admin codes
(not postal). `peru-pe/cpn` is the actual SERPOST national list with
2,669 codes — fully shippable.

License & attribution
---------------------
- Source: peru-pe/cpn (no formal LICENSE file)
- Upstream: SERPOST / MTC público
- Each row: ``source: "serpost-via-peru-pe-cpn"``

Tier 5 per #1039 license-tier policy.

Usage
-----
    python3 bin/scripts/sync/import_peru_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = "https://raw.githubusercontent.com/peru-pe/cpn/master/onlyCodes.json"

# 2-digit postcode prefix -> CSC iso2.
# SERPOST orders prefixes alphabetically by department name; the 25
# Peruvian departments + Constitutional Province of Callao (07) get
# 01-25. Lima prefix (15) covers both LIM (department) and LMA (Lima
# Metropolitan); we map to LIM since the source has no inner split.
PREFIX_TO_ISO2: Dict[str, str] = {
    "01": "AMA",  # Amazonas
    "02": "ANC",  # Áncash
    "03": "APU",  # Apurímac
    "04": "ARE",  # Arequipa
    "05": "AYA",  # Ayacucho
    "06": "CAJ",  # Cajamarca
    "07": "CAL",  # Callao (Constitutional Province)
    "08": "CUS",  # Cusco
    "09": "HUV",  # Huancavelica
    "10": "HUC",  # Huánuco
    "11": "ICA",  # Ica
    "12": "JUN",  # Junín
    "13": "LAL",  # La Libertad
    "14": "LAM",  # Lambayeque
    "15": "LIM",  # Lima (department + metropolitan)
    "16": "LOR",  # Loreto
    "17": "MDD",  # Madre de Dios
    "18": "MOQ",  # Moquegua
    "19": "PAS",  # Pasco
    "20": "PIU",  # Piura
    "21": "PUN",  # Puno
    "22": "SAM",  # San Martín
    "23": "TAC",  # Tacna
    "24": "TUM",  # Tumbes
    "25": "UCA",  # Ucayali
}


def fetch_json(url: str) -> List[str]:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    codes = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    print(f"Source codes: {len(codes):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    pe_country = next((c for c in countries if c.get("iso2") == "PE"), None)
    if pe_country is None:
        print("ERROR: PE not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(pe_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    pe_states = [s for s in states if s.get("country_id") == pe_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in pe_states if s.get("iso2")
    }
    print(
        f"Country: Peru (id={pe_country['id']}); states indexed: {len(pe_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_prefixes: Dict[str, int] = {}

    for raw in codes:
        code = str(raw).strip().zfill(5)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        prefix = code[:2]
        iso2 = PREFIX_TO_ISO2.get(prefix)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_prefixes[prefix] = unknown_prefixes.get(prefix, 0) + 1
            skipped_no_state += 1

        if code in seen:
            continue
        seen.add(code)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(pe_country["id"]),
            "country_code": "PE",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        record["type"] = "full"
        record["source"] = "serpost-via-peru-pe-cpn"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_prefixes:
        print("Unknown prefixes (not in PREFIX_TO_ISO2):")
        for p, n in sorted(unknown_prefixes.items(), key=lambda x: -x[1]):
            print(f"  {p!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PE.json"
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
