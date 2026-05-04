#!/usr/bin/env python3
"""Czech Republic -> contributions/postcodes/CZ.json importer for issue #1039.

Source data
-----------
The community ``1nfinity84/PSC-Okres-Obec-OkresCZ`` repository ships
``mapping_data.json`` — a 4 MB join of Czech 5-digit PSČ
(poštovní směrovací číslo / postal code) onto okres (district) and
obec (municipality), generated from rotten77's SQL dump of Česká
pošta + ČSÚ.

    {
      "psc_to_okres": {"10000": "Praha", ...},
      "psc_to_obec":  {"10000": [obec1, obec2, ...], ...}
    }

Source URL: https://raw.githubusercontent.com/1nfinity84/PSC-Okres-Obec-OkresCZ/master/mapping_data.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves state FK by direct okres-name match against CSC's 76
   district entries plus a 1-entry alias ('Praha' -> CSC capital
   city iso2 '10').
3. For PSCs whose source value is an array of multiple okres, picks
   the first as primary state.
4. Joins each PSC's psc_to_obec list to derive a representative
   locality_name (first obec, with parenthetical hints stripped).
5. Writes contributions/postcodes/CZ.json idempotently.

Coverage upgrade
----------------
The previously-tracked ``soit-sk/czech_republic_post_codes_2007``
shipped only a Perl scraper for the 2007 stamps DB and required
running it against Česká pošta's b2b TLS-blocked endpoint. This
mirror is a static JSON join requiring no scraping, generated from
rotten77's open SQL dump of Česká pošta + Czech Statistical Office
(ČSÚ) data.

License & attribution
---------------------
- Source: 1nfinity84/PSC-Okres-Obec-OkresCZ (no formal LICENSE;
  derived from rotten77's open SQL dump, in turn from Česká pošta +
  ČSÚ public lookups)
- Each row: ``source: "ceska-posta-via-1nfinity84"``

Tier 5 per #1039 license-tier policy.

Usage
-----
    python3 bin/scripts/sync/import_czech_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Union


SOURCE_URL = (
    "https://raw.githubusercontent.com/1nfinity84/PSC-Okres-Obec-OkresCZ/"
    "master/mapping_data.json"
)

# Source okres label -> CSC name override. Most map directly by
# district name; only Praha (capital city, not a district) needs
# the alias.
OKRES_ALIASES: Dict[str, str] = {
    "Praha": "Praha, Hlavní město",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def _strip_obec(name: str) -> str:
    """Remove '(část)' / '(Praha N) (část)' parenthetical fragments."""
    return re.sub(r"\s*\([^)]*\)", "", name).strip()


def _primary_okres(value: Union[str, List[str]]) -> str:
    if isinstance(value, list):
        return value[0] if value else ""
    return str(value or "")


def _primary_obec(value: Union[str, List[str], None]) -> str:
    if not value:
        return ""
    if isinstance(value, list):
        return _strip_obec(value[0]) if value else ""
    return _strip_obec(str(value))


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
    psc_to_okres = data.get("psc_to_okres", {})
    psc_to_obec = data.get("psc_to_obec", {})
    print(f"Source PSCs: {len(psc_to_okres):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    cz_country = next((c for c in countries if c.get("iso2") == "CZ"), None)
    if cz_country is None:
        print("ERROR: CZ not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(cz_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    cz_states = [s for s in states if s.get("country_id") == cz_country["id"]]
    state_by_name: Dict[str, dict] = {s["name"]: s for s in cz_states if s.get("name")}
    print(
        f"Country: Czech Republic (id={cz_country['id']}); "
        f"states indexed: {len(cz_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_okres: Dict[str, int] = {}

    for psc, okres_value in psc_to_okres.items():
        code = str(psc).strip()
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        okres = _primary_okres(okres_value)
        csc_name = OKRES_ALIASES.get(okres, okres)
        state = state_by_name.get(csc_name)
        if state is None:
            unknown_okres[okres] = unknown_okres.get(okres, 0) + 1
            skipped_no_state += 1

        locality = _primary_obec(psc_to_obec.get(psc))

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(cz_country["id"]),
            "country_code": "CZ",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "ceska-posta-via-1nfinity84"
        records.append(record)

    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_okres:
        print("Unknown okres labels (not in CSC + OKRES_ALIASES):")
        for o, n in sorted(unknown_okres.items(), key=lambda x: -x[1]):
            print(f"  {o!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/CZ.json"
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
