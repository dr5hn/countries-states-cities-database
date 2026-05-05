#!/usr/bin/env python3
"""Finland -> contributions/postcodes/FI.json importer for issue #1039.

Source data
-----------
Posti's official PCF (postal code file) is the canonical 5-digit
postal-code list for Finland, refreshed daily. The DAT format is
fixed-width ISO-8859-1 with one record per line at 220 chars/line.

URL pattern: https://www.posti.fi/webpcode/unzip/PCF_<YYYYMMDD>.dat

The importer probes recent dates back from today and uses the
freshest available file.

Fixed-width fields (1-indexed positions per Posti spec):
    1-5    record identifier (PONOT)
    6-13   extraction date (YYYYMMDD)
    14-18  postal code (5 digits)
    19-48  postal name (Finnish, 30 chars)
    49-78  postal name (Swedish, 30 chars)
    79-90  abbreviation (Finnish, 12 chars)
    91-102 abbreviation (Swedish, 12 chars)
    103-110 effective date (YYYYMMDD)
    111    type (1=normal)
    112-116 region code (FI1xx)
    117-146 region name (Finnish, 30 chars)
    147-176 region name (Swedish, 30 chars)
    177-179 municipality code
    180-199 municipality name (Finnish, 20 chars)
    200-219 municipality name (Swedish, 20 chars)
    220    language code

What this script does
---------------------
1. Probes the URL pattern back ~30 days to find the latest dated DAT.
2. Decodes as ISO-8859-1 (Posti standard).
3. Parses fixed-width records.
4. Skips Ahvenanmaa (region FI200) — those records belong to the
   separate AX (Åland Islands) CSC country and are shipped via a
   companion importer.
5. Resolves state FK via Finnish region-name match through
   FI_REGION_TO_ISO2 (18 mainland Finnish maakunta + Helsinki-Uusimaa
   merged into Uusimaa per ISO 3166-2:FI).
6. Writes contributions/postcodes/FI.json idempotently.

Coverage upgrade
----------------
The previously-tracked ``launis/areadata`` mirror is a wrapper-only
package with no bulk export. The research-doc note flagged the
date-stamped Posti URL as `difficult per memory`. Direct date probe
of Posti's webpcode endpoint resolves the freshest URL automatically.

License & attribution
---------------------
- Source: Posti.fi PCF (Finnish postal code file)
- Posti's terms: free redistribution permitted with attribution
  (Tier 5 per #1039 license-tier policy)
- Each row: ``source: "posti-fi-pcf"``

Usage
-----
    python3 bin/scripts/sync/import_finland_postcodes.py
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional


URL_TEMPLATE = "https://www.posti.fi/webpcode/unzip/PCF_{date}.dat"

# Finnish maakunta name -> CSC FI iso2.
# Helsinki-Uusimaa is a NUTS sub-division of the Uusimaa region;
# both map to CSC '18' Uusimaa.
FI_REGION_TO_ISO2: Dict[str, str] = {
    "Etelä-Karjala": "02",          # South Karelia
    "Etelä-Pohjanmaa": "03",         # Southern Ostrobothnia
    "Etelä-Savo": "04",              # Southern Savonia
    "Kainuu": "05",                  # Kainuu
    "Kanta-Häme": "06",              # Tavastia Proper
    "Keski-Pohjanmaa": "07",         # Central Ostrobothnia
    "Keski-Suomi": "08",             # Central Finland
    "Kymenlaakso": "09",             # Kymenlaakso
    "Lappi": "10",                   # Lapland
    "Pirkanmaa": "11",               # Pirkanmaa
    "Pohjanmaa": "12",               # Ostrobothnia
    "Pohjois-Karjala": "13",         # North Karelia
    "Pohjois-Pohjanmaa": "14",       # Northern Ostrobothnia
    "Pohjois-Savo": "15",            # Northern Savonia
    "Päijät-Häme": "16",             # Päijänne Tavastia
    "Satakunta": "17",               # Satakunta
    "Helsinki-Uusimaa": "18",        # NUTS sub-region of Uusimaa
    "Uusimaa": "18",                 # Uusimaa
    "Varsinais-Suomi": "19",         # Finland Proper
}


def resolve_pcf_url(max_days_back: int = 30) -> str:
    today = datetime.date.today()
    for delta in range(0, max_days_back):
        d = today - datetime.timedelta(days=delta)
        url = URL_TEMPLATE.format(date=d.strftime("%Y%m%d"))
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": "csc-database-postcode-importer"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                if r.status == 200:
                    return url
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
    raise RuntimeError(f"No PCF DAT found in last {max_days_back} days")


def fetch_text(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("iso-8859-1")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local DAT (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="iso-8859-1")
        print(f"loaded local input: {args.input}")
    else:
        url = resolve_pcf_url()
        print(f"fetching {url}")
        text = fetch_text(url)
    lines = text.splitlines()
    print(f"Source rows: {len(lines):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    fi_country = next((c for c in countries if c.get("iso2") == "FI"), None)
    if fi_country is None:
        print("ERROR: FI not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(fi_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    fi_states = [s for s in states if s.get("country_id") == fi_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in fi_states if s.get("iso2")
    }
    print(
        f"Country: Finland (id={fi_country['id']}); "
        f"states indexed: {len(fi_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_aland = 0
    skipped_short = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_regions: Dict[str, int] = {}

    for line in lines:
        if len(line) < 220:
            skipped_short += 1
            continue
        code = line[13:18].strip()
        postal_name_fi = line[18:48].strip()
        postal_name_sv = line[48:78].strip()
        region_code = line[111:116].strip()
        region_fi = line[116:146].strip()
        municipality_fi = line[179:199].strip()

        # Skip Åland — separate CSC country
        if region_code == "FI200" or region_fi == "Ahvenanmaa":
            skipped_aland += 1
            continue

        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        iso2 = FI_REGION_TO_ISO2.get(region_fi)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_regions[region_fi] = unknown_regions.get(region_fi, 0) + 1
            skipped_no_state += 1

        # Locality: Finnish postal name + municipality (when distinct)
        if postal_name_fi and municipality_fi and postal_name_fi.lower() != municipality_fi.lower():
            locality = f"{postal_name_fi}, {municipality_fi}"
        else:
            locality = postal_name_fi or municipality_fi

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(fi_country["id"]),
            "country_code": "FI",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "posti-fi-pcf"
        records.append(record)

    print(f"Skipped (Åland, ships to AX): {skipped_aland:,}")
    print(f"Skipped (short row):           {skipped_short:,}")
    print(f"Skipped (regex fail):          {skipped_bad_regex:,}")
    print(f"Skipped (no state FK):         {skipped_no_state:,}")
    print(f"Records emitted:               {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:                  {matched_state:,} ({pct}%)")
    if unknown_regions:
        print("Unknown regions (not in FI_REGION_TO_ISO2):")
        for r, n in sorted(unknown_regions.items(), key=lambda x: -x[1]):
            print(f"  {r!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/FI.json"
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
