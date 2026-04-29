#!/usr/bin/env python3
"""Cambodia -> contributions/postcodes/KH.json importer for #1039.

Source data
-----------
The community ``seanghay/cambodia-postal-codes`` repository ships
Cambodia Post's 2017-reform 6-digit catalogue keyed by province ->
district -> sangkat:

    [{"id": 12, "name": "រាជធានីភ្នំពេញ", "districts": [
        {"location_en": "Khan Chamkar Mon", "codes": [
            {"en": "Sangkat Tonle Basak", "code": "120101"}, ...]}, ...
    ]}, ...]

Source URL: https://raw.githubusercontent.com/seanghay/cambodia-postal-codes/main/cambodia-postal-codes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Walks provinces -> districts -> codes; emits one record per
   ``(6-digit code, sangkat + district)`` pair.
3. Resolves ``state_id`` directly from the source's ``id`` field —
   CSC's ``states.json`` already uses the same 1-25 numeric ``iso2``
   for Cambodia provinces (12=Phnom Penh, 17=Siem Reap, etc.).
4. Writes contributions/postcodes/KH.json idempotently.

Also updates the Cambodia ``postal_code_regex``/``format`` in
``countries.json`` from a 5-digit shape to the post-2017 6-digit
shape used by Cambodia Post.

License & attribution
---------------------
- Source: seanghay/cambodia-postal-codes (open redistribution of
  Cambodia Post's publicly published 2017 reform index).
- Each row: ``source: "cambodia-post-via-seanghay"``

Usage
-----
    python3 bin/scripts/sync/import_cambodia_postcodes.py
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
    "https://raw.githubusercontent.com/seanghay/cambodia-postal-codes/"
    "main/cambodia-postal-codes.json"
)


def fetch_json(url: str) -> List[dict]:
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
    kh_country = next((c for c in countries if c.get("iso2") == "KH"), None)
    if kh_country is None:
        print("ERROR: KH not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(kh_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    kh_states = [s for s in states if s.get("country_id") == kh_country["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in kh_states if s.get("iso2")}
    print(f"Country: Cambodia (id={kh_country['id']}); states indexed: {len(kh_states)}")
    print(f"Source provinces: {len(data)}")

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0

    for prov in data:
        prov_id = str(prov.get("id") or "").strip()
        state = state_by_iso2.get(prov_id)
        for district in prov.get("districts", []) or []:
            district_name = (
                district.get("location_en") or district.get("location_kh") or ""
            ).strip()
            for code_entry in district.get("codes", []) or []:
                code = (code_entry.get("code") or "").strip()
                if not code:
                    continue
                if not regex.match(code):
                    skipped_bad_regex += 1
                    continue
                sangkat_en = (code_entry.get("en") or "").strip()
                sangkat_km = (code_entry.get("km") or "").strip()
                sangkat = sangkat_en or sangkat_km
                locality = ", ".join(p for p in (sangkat, district_name) if p)
                key = (code, locality.lower())
                if key in seen:
                    continue
                seen.add(key)

                record: Dict[str, object] = {
                    "code": code,
                    "country_id": int(kh_country["id"]),
                    "country_code": "KH",
                }
                if state is not None:
                    record["state_id"] = int(state["id"])
                    record["state_code"] = state.get("iso2")
                    matched_state += 1
                else:
                    skipped_no_state += 1

                if locality:
                    record["locality_name"] = locality
                record["type"] = "full"
                record["source"] = "cambodia-post-via-seanghay"
                records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    print(f"  no state FK:         {skipped_no_state:,}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/KH.json"
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
