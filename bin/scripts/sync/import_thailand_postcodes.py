#!/usr/bin/env python3
"""Thailand -> contributions/postcodes/TH.json importer for issue #1039.

Source data
-----------
The community ``chawatvish/thailand_postcode_json`` repository ships
the Thai Post catalogue as a nested JSON of provinces -> districts ->
tambons + postcodes. Province names are in Thai script and not used
for FK resolution — Thai Post's 5-digit code carries the province
in its first two digits, which exactly match CSC's 2-digit numeric
``state.iso2`` for Thai provinces.

Source URL: https://raw.githubusercontent.com/chawatvish/thailand_postcode_json/master/thailand_postcode.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Walks provinces -> districts; emits one row per ``(postcode,
   district)`` pair (5-digit Thai Post code).
3. Resolves ``state_id`` directly from ``postcode[:2]`` because CSC's
   ``states.json`` iso2 for Thai provinces is the same 2-digit numeric
   prefix Thai Post uses (e.g. 10 = Bangkok, 50 = Chiang Mai).
4. Writes contributions/postcodes/TH.json idempotently.

License & attribution
---------------------
- Source: chawatvish/thailand_postcode_json (open redistribution of
  Thai Post's publicly published postcode index).
- Each row: ``source: "thai-post-via-chawatvish"``

Usage
-----
    python3 bin/scripts/sync/import_thailand_postcodes.py
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
    "https://raw.githubusercontent.com/chawatvish/thailand_postcode_json/"
    "master/thailand_postcode.json"
)


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
    th_country = next((c for c in countries if c.get("iso2") == "TH"), None)
    if th_country is None:
        print("ERROR: TH not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(th_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    th_states = [s for s in states if s.get("country_id") == th_country["id"]]
    # Resolve by source's Thai-script province name (state.native), NOT by
    # postal-prefix. Thai Post's 5-digit codes are NOT aligned with ISO 3166-2:TH
    # for ~10 provinces — Bangkok absorbs Samut Prakan in postal-prefix-land,
    # so every later province's postal prefix is off-by-one from CSC's iso2.
    # The source feed nests each postcode under its real province in Thai
    # script, which is the authoritative join key.
    state_by_native: Dict[str, dict] = {
        (s.get("native") or "").strip(): s for s in th_states if s.get("native")
    }
    # Source uses "กรุงเทพมหานคร" (formal Bangkok); CSC uses "กรุงเทพฯ" (short form)
    # CSC also has a typo in Nan's native ("แนน" vs source "น่าน") — alias both.
    NATIVE_ALIASES: Dict[str, str] = {
        "กรุงเทพมหานคร": "กรุงเทพฯ",
        "น่าน": "แนน",
    }
    print(f"Country: Thailand (id={th_country['id']}); states indexed: {len(th_states)}")

    provinces = data.get("provinces", []) if isinstance(data, dict) else []
    print(f"Source provinces: {len(provinces):,}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unresolved_provinces: set = set()

    for prov in provinces:
        prov_native = (prov.get("name") or "").strip()
        prov_native_csc = NATIVE_ALIASES.get(prov_native, prov_native)
        state = state_by_native.get(prov_native_csc)
        if state is None:
            unresolved_provinces.add(prov_native)
        for district in prov.get("districts", []) or []:
            district_name = (district.get("name") or "").strip()
            for code_int in district.get("postcodes", []) or []:
                code = str(code_int).zfill(5)
                if not regex.match(code):
                    skipped_bad_regex += 1
                    continue
                key = (code, district_name)
                if key in seen:
                    continue
                seen.add(key)

                record: Dict[str, object] = {
                    "code": code,
                    "country_id": int(th_country["id"]),
                    "country_code": "TH",
                }
                if state is not None:
                    record["state_id"] = int(state["id"])
                    record["state_code"] = state.get("iso2")
                    matched_state += 1
                else:
                    skipped_no_state += 1

                if district_name:
                    record["locality_name"] = district_name
                record["type"] = "full"
                record["source"] = "thai-post-via-chawatvish"
                records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")
    if unresolved_provinces:
        print(
            f"  unresolved provinces: "
            f"{sorted(unresolved_provinces)}"
        )

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/TH.json"
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
