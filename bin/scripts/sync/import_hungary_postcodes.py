#!/usr/bin/env python3
"""Hungary -> contributions/postcodes/HU.json importer for issue #1039.

Source data
-----------
Tamás Ferenci's ``ferenci-tamas/IrszHnk`` repo joins the official
Magyar Posta postal-code workbook with the KSH Helységnévtár
(Hungarian Central Statistical Office gazetteer) to produce a single
CSV keyed on `(IRSZ, Helység.megnevezése, Településrész)`.

Last refresh in repo: 09-Feb-2026.

Source URL: https://raw.githubusercontent.com/ferenci-tamas/IrszHnk/master/IrszHnk.csv

Schema (semicolon-delimited):
    Helység.megnevezése  -- settlement name
    IRSZ                  -- 4-digit postal code
    Településrész         -- sub-district / locality fragment (often blank)
    Vármegye.megnevezése -- megye/county name (state FK)
    Járás.kódja           -- subdistrict (járás) code
    Járás.neve            -- subdistrict name
    Helység.jogállása     -- legal status: község / város / fővárosi kerület / ...

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Joins the 20 source megye labels (19 megyék + ``főváros``) onto
   CSC's 20 county-level iso2 codes via SOURCE_TO_ISO2.
3. Emits one row per (code, settlement[+sub-district]) pair.
4. Writes contributions/postcodes/HU.json idempotently.

Why a hand-curated megye map (not name match)
---------------------------------------------
CSC's HU states.json has 43 entries: 19 megyék + Budapest + 23 cities
of county rank (megyei jogú város). The CSV authoritatively reports
megye, not city-of-county-rank, so the only meaningful join key is
the 20 county-level entries. Hand-curated map handles two name drifts:
``főváros`` (lit. "the capital") -> Budapest; ``Csongrád-Csanád``
(2020 renaming) -> CSC's older ``Csongrád County`` label.

License
-------
Repo has no LICENSE file. The two upstream sources (Magyar Posta and
KSH) are official Hungarian government open data — `data.gov.hu` style
but no formal CC-BY label. Acceptable per #1039 license-tier policy
(Tier 5: free redistribution permitted, no formal licence; flagged
in PR).

Each row carries: ``source: "magyar-posta-via-ferenci-tamas"``

Usage
-----
    python3 bin/scripts/sync/import_hungary_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/ferenci-tamas/IrszHnk/master/IrszHnk.csv"
)

# 20 source megye labels (19 counties + 'főváros' = Budapest)
# -> CSC iso2 in states.json.
SOURCE_TO_ISO2: Dict[str, str] = {
    "Baranya": "BA",
    "Borsod-Abaúj-Zemplén": "BZ",
    "Bács-Kiskun": "BK",
    "Békés": "BE",
    "Csongrád-Csanád": "CS",  # 2020 rename; CSC entry still 'Csongrád County'
    "Fejér": "FE",
    "Győr-Moson-Sopron": "GS",
    "Hajdú-Bihar": "HB",
    "Heves": "HE",
    "Jász-Nagykun-Szolnok": "JN",
    "Komárom-Esztergom": "KE",
    "Nógrád": "NO",
    "Pest": "PE",
    "Somogy": "SO",
    "Szabolcs-Szatmár-Bereg": "SZ",
    "Tolna": "TO",
    "Vas": "VA",
    "Veszprém": "VE",
    "Zala": "ZA",
    "főváros": "BU",  # Budapest
}


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8-sig")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8-sig")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    hu_country = next((c for c in countries if c.get("iso2") == "HU"), None)
    if hu_country is None:
        print("ERROR: HU not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(hu_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    hu_states = [s for s in states if s.get("country_id") == hu_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in hu_states if s.get("iso2")
    }
    print(
        f"Country: Hungary (id={hu_country['id']}); states indexed: {len(hu_states)}"
    )

    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_no_code = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_megye: Dict[str, int] = {}

    for row in rows:
        raw_code = (row.get("IRSZ") or "").strip()
        if not raw_code:
            skipped_no_code += 1
            continue
        code = raw_code.zfill(4) if raw_code.isdigit() else raw_code
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        megye = (row.get("Vármegye.megnevezése") or "").strip()
        helyseg = (row.get("Helység.megnevezése") or "").strip()
        resz = (row.get("Településrész") or "").strip()

        iso2 = SOURCE_TO_ISO2.get(megye)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_megye[megye] = unknown_megye.get(megye, 0) + 1
            skipped_no_state += 1

        # Locality = settlement + sub-district (when present)
        if resz:
            locality = f"{helyseg}, {resz}"
        else:
            locality = helyseg

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(hu_country["id"]),
            "country_code": "HU",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "magyar-posta-via-ferenci-tamas"
        records.append(record)

    print(f"Skipped (no code):     {skipped_no_code:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_megye:
        print("Unknown megye labels (not in SOURCE_TO_ISO2):")
        for m, n in sorted(unknown_megye.items(), key=lambda x: -x[1]):
            print(f"  {m!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/HU.json"
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
