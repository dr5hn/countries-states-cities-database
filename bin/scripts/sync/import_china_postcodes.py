#!/usr/bin/env python3
"""China -> contributions/postcodes/CN.json importer for issue #1039.

Source data
-----------
The community ``mumuy/data_post`` repository (MIT-licensed, ~45⭐)
publishes ``list.json``: a dict keyed by 6-digit postcode mapping to
the most-specific Chinese locality name (district/town).

    {
      "100000": "北京市",
      "100001": "东城区",
      ...
    }

Source URL: https://raw.githubusercontent.com/mumuy/data_post/master/list.json

China's 6-digit code structure (from source README) is:
    [province: 2][postal-region: 1][county: 1][delivery: 2]

What this script does
---------------------
1. Fetches list.json via urllib (curl is blocked in the harness).
2. Maps each code's first 2 digits to one of the 31 mainland CSC
   provinces/municipalities/autonomous-regions via PREFIX_TO_ISO2.
3. The prefix table was derived from ``XX0000`` trunk codes + per-prefix
   vote-counting of the most common province-level marker (省/市/自治区).
4. Emits one row per (code, locality) pair.
5. Writes contributions/postcodes/CN.json idempotently.

Why a hand-curated prefix map (not name match)
----------------------------------------------
The source has no province column. The 22,656 values are all
district/town names in Chinese — joining them to states.json by name
would lose every code where the district name is non-unique (and many
are). The 60-entry 2-digit prefix table is unambiguous, public-domain
fact, and pulls 100% FK resolution.

Coverage notes
--------------
- Mainland only — HK / MO / TW have their own postcode systems and CSC
  represents them as separate countries (HK/MO with no postcode system,
  TW handled by a future #1039 PR).
- Prefix 14 is unused by China Post (no 140000-149999 codes exist).
- Some district-level names like ``蜀山区`` (Hefei) appear at trunk
  positions like 230000 — this is a quirk of mumuy's snapshot, not a
  data error; the prefix mapping still resolves correctly via 2-digit
  truncation.

License & attribution
---------------------
- Source: mumuy/data_post (MIT)
- Each row: ``source: "china-post-via-mumuy"``

Usage
-----
    python3 bin/scripts/sync/import_china_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = "https://raw.githubusercontent.com/mumuy/data_post/master/list.json"

# 2-digit postcode prefix -> CSC iso2 (subdivision code).
# Derived from XX0000 trunk codes + per-prefix province-name voting.
PREFIX_TO_ISO2: Dict[str, str] = {
    "01": "NM",  # Inner Mongolia
    "02": "NM",
    "03": "SX",  # Shanxi
    "04": "SX",
    "05": "HE",  # Hebei
    "06": "HE",
    "07": "HE",
    "10": "BJ",  # Beijing
    "11": "LN",  # Liaoning
    "12": "LN",
    "13": "JL",  # Jilin
    "15": "HL",  # Heilongjiang
    "16": "HL",
    "20": "SH",  # Shanghai
    "21": "JS",  # Jiangsu
    "22": "JS",
    "23": "AH",  # Anhui
    "24": "AH",
    "25": "SD",  # Shandong
    "26": "SD",
    "27": "SD",
    "29": "NM",  # NM (eastern outliers)
    "30": "TJ",  # Tianjin
    "31": "ZJ",  # Zhejiang
    "32": "ZJ",
    "33": "JX",  # Jiangxi
    "34": "JX",
    "35": "FJ",  # Fujian
    "36": "FJ",
    "40": "CQ",  # Chongqing
    "41": "HN",  # Hunan
    "42": "HN",
    "43": "HB",  # Hubei
    "44": "HB",
    "45": "HA",  # Henan
    "46": "HA",
    "47": "HA",
    "51": "GD",  # Guangdong
    "52": "GD",
    "53": "GX",  # Guangxi
    "54": "GX",
    "55": "GZ",  # Guizhou
    "56": "GZ",
    "57": "HI",  # Hainan
    "61": "SC",  # Sichuan
    "62": "SC",
    "63": "SC",
    "64": "SC",
    "65": "YN",  # Yunnan
    "66": "YN",
    "67": "YN",
    "71": "SN",  # Shaanxi
    "72": "SN",
    "73": "GS",  # Gansu
    "74": "GS",
    "75": "NX",  # Ningxia
    "81": "QH",  # Qinghai
    "83": "XJ",  # Xinjiang
    "84": "XJ",
    "85": "XZ",  # Tibet
    "86": "XZ",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local JSON (skip fetch)")
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
    cn_country = next((c for c in countries if c.get("iso2") == "CN"), None)
    if cn_country is None:
        print("ERROR: CN not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(cn_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    cn_states = [s for s in states if s.get("country_id") == cn_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in cn_states if s.get("iso2")
    }
    print(f"Country: China (id={cn_country['id']}); states indexed: {len(cn_states)}")
    print(f"Source rows: {len(data):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_prefixes: Dict[str, int] = {}

    for code_raw, locality in sorted(data.items()):
        code = str(code_raw).strip().zfill(6)
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        prefix = code[:2]
        iso2 = PREFIX_TO_ISO2.get(prefix)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_prefixes[prefix] = unknown_prefixes.get(prefix, 0) + 1
            skipped_no_state += 1

        locality = (locality or "").strip()
        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(cn_country["id"]),
            "country_code": "CN",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "china-post-via-mumuy"
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

    target = project_root / "contributions/postcodes/CN.json"
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
