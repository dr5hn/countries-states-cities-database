#!/usr/bin/env python3
"""Taiwan -> contributions/postcodes/TW.json importer for issue #1039.

Source data
-----------
The community ``flying-itmen-eagle/eagle-tw-open-data`` repository
publishes Taiwan government open-data feeds, including the canonical
3-digit Chunghwa Post postal-area code list:

    100,臺北市中正區,"Zhongzheng Dist., Taipei City"
    103,臺北市大同區,"Datong Dist., Taipei City"
    ...

Each row: 3-digit zip prefix, Chinese district label (city+district),
English district label.

Source URL: https://raw.githubusercontent.com/flying-itmen-eagle/eagle-tw-open-data/master/files/taiwan_postal_code_information.csv

What this script does
---------------------
1. Fetches the CSV via urllib (curl is blocked).
2. Decodes the CSV as **CP950 / Big5** (Taiwan government default
   encoding; UTF-8 read produces mojibake).
3. Resolves state FK by parsing the trailing ``X City`` / ``X County``
   from the English column and mapping via ENGLISH_TO_ISO2.
4. Emits one row per (3-digit code, Chinese district, English label).
5. Writes contributions/postcodes/TW.json idempotently.

Regex note
----------
Before this PR, countries.json had TW regex ``^\\d{5}$`` (5-digit).
Taiwan has used three postcode generations:
    - pre-2020: 3-digit area codes (this dataset)
    - intermediate: 3+2 = 5-digit (still listed in some sources)
    - 2020+: 3+3 = 6-digit (Chunghwa Post current canonical)
The companion regex fix sets it to ``^\\d{3}(\\d{2,3})?$`` to accept
all three generations.

Edge cases
----------
The 26 source labels include 22 standard administrative divisions +
4 special cases:
    - 'Taoyuan City City'   typo -> TAO
    - 'Diaoyutai'           Senkaku/Diaoyu islands (ROC -> Yilan/ILA)
    - 'Dongsha Islands'     Pratas (administered by Kaohsiung/KHH)
    - 'Nansha Islands'      Spratlys (administered by Kaohsiung/KHH)
These are mapped via SPECIAL_LABEL_TO_ISO2.

License & attribution
---------------------
- Source: flying-itmen-eagle/eagle-tw-open-data (GPL-3 — unusual for
  data but redistribution permitted with attribution; flagged in PR)
- Upstream: Chunghwa Post / Ministry of Interior open data
- Each row: ``source: "chunghwa-post-via-eagle-tw-open-data"``

Usage
-----
    python3 bin/scripts/sync/import_taiwan_postcodes.py
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
    "https://raw.githubusercontent.com/flying-itmen-eagle/eagle-tw-open-data/"
    "master/files/taiwan_postal_code_information.csv"
)

# Trailing English city/county label -> CSC iso2 in TW states.json.
ENGLISH_TO_ISO2: Dict[str, str] = {
    "Taipei City": "TPE",
    "New Taipei City": "NWT",
    "Keelung City": "KEE",
    "Hsinchu City": "HSZ",
    "Hsinchu County": "HSQ",
    "Taoyuan City": "TAO",
    "Miaoli County": "MIA",
    "Taichung City": "TXG",
    "Changhua County": "CHA",
    "Nantou County": "NAN",
    "Yunlin County": "YUN",
    "Chiayi City": "CYI",
    "Chiayi County": "CYQ",
    "Tainan City": "TNN",
    "Kaohsiung City": "KHH",
    "Pingtung County": "PIF",
    "Taitung County": "TTT",
    "Hualien County": "HUA",
    "Yilan County": "ILA",
    "Penghu County": "PEN",
    "Kinmen County": "KIN",
    "Lienchiang County": "LIE",
}

# Edge-case English labels not following 'X City' / 'X County' pattern.
SPECIAL_LABEL_TO_ISO2: Dict[str, str] = {
    "Taoyuan City City": "TAO",  # source typo
    "Diaoyutai": "ILA",  # Senkaku/Diaoyu (ROC administers under Yilan)
    "Dongsha Islands, Nanhai Islands": "KHH",  # Pratas (under Kaohsiung)
    "Nansha Islands, Nanhai Islands": "KHH",  # Spratlys (under Kaohsiung)
}


def fetch_csv(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("cp950")


def resolve_iso2(english_label: str) -> str | None:
    label = english_label.strip()
    if label in SPECIAL_LABEL_TO_ISO2:
        return SPECIAL_LABEL_TO_ISO2[label]
    # 'Zhongzheng Dist., Taipei City' -> trailing 'Taipei City'
    if "," in label:
        tail = label.rsplit(",", 1)[1].strip()
        if tail in ENGLISH_TO_ISO2:
            return ENGLISH_TO_ISO2[tail]
        if tail in SPECIAL_LABEL_TO_ISO2:
            return SPECIAL_LABEL_TO_ISO2[tail]
    if label in ENGLISH_TO_ISO2:
        return ENGLISH_TO_ISO2[label]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local CSV (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="cp950")
        if args.input
        else fetch_csv(SOURCE_URL)
    )

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    tw_country = next((c for c in countries if c.get("iso2") == "TW"), None)
    if tw_country is None:
        print("ERROR: TW not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(tw_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    tw_states = [s for s in states if s.get("country_id") == tw_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in tw_states if s.get("iso2")
    }
    print(
        f"Country: Taiwan (id={tw_country['id']}); states indexed: {len(tw_states)}"
    )

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    print(f"Source rows: {len(rows):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_labels: Dict[str, int] = {}

    for row in rows:
        if len(row) < 3:
            continue
        code, zh_label, en_label = row[0].strip(), row[1].strip(), row[2].strip()
        if not code:
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        iso2 = resolve_iso2(en_label)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_labels[en_label] = unknown_labels.get(en_label, 0) + 1
            skipped_no_state += 1

        # Locality = English district name (Chinese kept implicit via source col)
        locality = en_label

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(tw_country["id"]),
            "country_code": "TW",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "chunghwa-post-via-eagle-tw-open-data"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_labels:
        print("Unknown labels (not in ENGLISH_TO_ISO2 or SPECIAL_LABEL_TO_ISO2):")
        for label, n in sorted(unknown_labels.items(), key=lambda x: -x[1]):
            print(f"  {label!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/TW.json"
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
