#!/usr/bin/env python3
"""KY + BB + TT Caribbean postcodes for issue #1039.

Source data
-----------
The community ``usama216/shipping-market`` Laravel seeder
``CaribbeanLocationSeeder.php`` ships hand-curated parish/district
+ postal-code data for 22 Caribbean territories. This importer
extracts the three with non-null CSC ``postal_code_regex``:

    KY Cayman Islands     (KY#-#### format, 3 islands)
    BB Barbados           (BB##### format, 11 parishes)
    TT Trinidad & Tobago  (6-digit format, 15 administrative areas)

Source URL: https://raw.githubusercontent.com/usama216/shipping-market/
            main/database/seeders/CaribbeanLocationSeeder.php

What this script does
---------------------
1. Fetches the PHP seeder via urllib.
2. Walks each block delimited by ``// COUNTRY (XX) - Has postal codes``,
   then for each parish/district reads ``'City' => ['postal_code' =>
   '<code>']`` literals via regex.
3. Resolves CSC state FK by NAME match (TT has divergent iso2 codes
   in the seeder vs CSC; name match handles both).
4. Writes contributions/postcodes/{KY,BB,TT}.json idempotently.

Coverage
--------
- KY: 9 codes across 3 islands (~half of Cayman Post's published
  codes; covers the main settlement of each island).
- BB: ~20 codes across 11 parishes (Bridgetown, Holetown,
  Speightstown + parish capitals).
- TT: ~30 codes across 15 administrative areas (Port of Spain,
  San Fernando, Tobago + each region's capital).

Total: ~50 codes — small but covers the population centers of three
territories that previously had no #1039 coverage.

License & attribution
---------------------
- Source repo (``usama216/shipping-market``) ships **without a formal
  license**. Per CSC's #1039 source-class taxonomy this is Tier 5:
  acceptable for facts-only redistribution with explicit attribution.
- Postal codes themselves are factual data published by the
  respective national postal authorities (Cayman Post, Barbados
  Postal Service, TTPost) and are not copyrightable.
- Each row carries ``source: "shipping-market-caribbean-seeder"``
  for export-time provenance.

Usage
-----
    python3 bin/scripts/sync/import_caribbean_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


SOURCE_URL = (
    "https://raw.githubusercontent.com/usama216/shipping-market/"
    "main/database/seeders/CaribbeanLocationSeeder.php"
)

TARGETS = ("KY", "BB", "TT")

# Per-country aliases: seeder parish/region label -> CSC state name.
# Reasons:
#  TT 'Mayaro-Rio Claro': CSC orders the compound name as
#    'Rio Claro-Mayaro' (id=MRC).
STATE_NAME_ALIASES: Dict[str, Dict[str, str]] = {
    "TT": {"Mayaro-Rio Claro": "Rio Claro-Mayaro"},
}


def fetch_text(url: str) -> str:
    """Fetch a text resource via urllib with a timeout."""
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def fold(s: str) -> str:
    """Lowercase and strip diacritics for fuzzy state-name matching."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().replace("'", "").replace(".", "").strip()


def parse_country_block(text: str, iso2: str) -> List[Tuple[str, str, str]]:
    """Extract (parish_name, city_name, code) tuples for one country.

    Locates the marker ``// XX (ISO2) - Has postal codes``, walks until
    the next ``// XX (ISO2)`` country marker, and pulls every
    ``'parish' => ['code' => '<iso>', 'cities' => [ ... ]]`` block.
    """
    start_pat = re.compile(
        rf"//\s+\w[^(]*\({iso2}\)\s+-\s+Has postal codes", re.M
    )
    m = start_pat.search(text)
    if not m:
        return []
    start = m.start()
    next_country = re.compile(r"//\s+[A-Z][A-Z &]+\s+\([A-Z]{2}(?:-[A-Z]{2})?\)", re.M)
    after = next_country.search(text, start + 5)
    end = after.start() if after else len(text)
    block = text[start:end]

    # Naive non-greedy capture corrupts nested ['postal_code' => '...']
    # array literals. Instead, scan parish anchor offsets, then assign
    # each ('city' => ['postal_code' => '...']) match to the nearest
    # preceding parish anchor.
    parish_anchor_re = re.compile(
        r"'([^']+)'\s*=>\s*\[\s*'code'\s*=>\s*'[^']*'\s*,\s*'cities'\s*=>\s*\[",
        re.S,
    )
    city_re = re.compile(
        r"['\"]([^'\"]+)['\"]\s*=>\s*\[\s*'postal_code'\s*=>\s*'([^']+)'\s*\]"
    )
    parish_offsets: List[Tuple[int, str]] = [
        (m.end(), m.group(1)) for m in parish_anchor_re.finditer(block)
    ]
    if not parish_offsets:
        return []

    out: List[Tuple[str, str, str]] = []
    for cm in city_re.finditer(block):
        city_pos = cm.start()
        # Find the parish whose anchor immediately precedes city_pos.
        parish_name = ""
        for off, name in parish_offsets:
            if off <= city_pos:
                parish_name = name
            else:
                break
        out.append((parish_name, cm.group(1), cm.group(2)))
    return out


def write_country(
    project_root: Path,
    iso2: str,
    rows: List[Tuple[str, str, str]],
    countries: List[dict],
    states_all: List[dict],
    dry_run: bool,
) -> int:
    """Resolve FKs for one country and write its contributions JSON.

    Returns 0 on success, non-zero on missing country/regex failure.
    """
    country = next((c for c in countries if c.get("iso2") == iso2), None)
    if country is None:
        print(f"ERROR: {iso2} not in countries.json", file=sys.stderr)
        return 2
    regex_str = country.get("postal_code_regex") or ".*"
    regex = re.compile(regex_str)
    states = [s for s in states_all if s.get("country_id") == country["id"]]
    state_by_name: Dict[str, dict] = {fold(s["name"]): s for s in states}
    print(
        f"\n=== {iso2} {country['name']} (id={country['id']}) ===\n"
        f"states indexed: {len(states)}; regex: {regex_str}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_bad_regex = 0
    matched_state = 0
    unknown_states: Dict[str, int] = {}

    aliases = STATE_NAME_ALIASES.get(iso2, {})
    for parish, city, code in rows:
        if not regex.match(code):
            skipped_bad_regex += 1
            continue
        canonical = aliases.get(parish, parish)
        state = state_by_name.get(fold(canonical))
        if state is None:
            unknown_states[parish] = unknown_states.get(parish, 0) + 1
        key = (code, city.lower())
        if key in seen:
            continue
        seen.add(key)
        record: Dict[str, object] = {
            "code": code,
            "country_id": int(country["id"]),
            "country_code": iso2,
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if city:
            record["locality_name"] = city
        record["type"] = "full"
        record["source"] = "shipping-market-caribbean-seeder"
        records.append(record)

    print(f"Source rows:           {len(rows):,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_states:
        print("Unknown parish/district names (not in CSC states.json):")
        for s, n in sorted(unknown_states.items(), key=lambda x: -x[1]):
            print(f"  {s!r}: {n}")

    if dry_run:
        return 0

    target = project_root / f"contributions/postcodes/{iso2}.json"
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
        f"[OK] Wrote {target.relative_to(project_root)} "
        f"({len(merged):,} rows, {size_kb:.0f} KB)"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local PHP seeder")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    text = (
        Path(args.input).read_text(encoding="utf-8")
        if args.input
        else fetch_text(SOURCE_URL)
    )
    print(f"Source seeder bytes: {len(text):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )

    rc = 0
    for iso2 in TARGETS:
        rows = parse_country_block(text, iso2)
        if not rows:
            print(f"\n=== {iso2} === ERROR: no rows parsed", file=sys.stderr)
            rc = max(rc, 2)
            continue
        rc = max(rc, write_country(project_root, iso2, rows, countries, states, args.dry_run))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
