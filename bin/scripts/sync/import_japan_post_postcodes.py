#!/usr/bin/env python3
"""Japan Post KEN_ALL -> contributions/postcodes/JP.json importer for issue #1039.

Source data
-----------
Japan Post publishes the canonical 7-digit postcode-to-locality mapping at:

  https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip

The file (KEN_ALL.CSV) is **Shift-JIS encoded**, ~12 MB raw, ~125,000 rows
covering all 47 prefectures. Each row has 15 columns; the relevant ones are:

  col 0   JIS X 0401/0402 municipality code
  col 1   legacy 5-digit zip (post-war system, kept for compatibility)
  col 2   modern 7-digit zip
  col 3-5 half-width katakana (prefecture, city, town)
  col 6-8 kanji (prefecture, city, town)
  col 9-14 various flags

The dataset publishes one row per (zip, town) pair, so a single zip code
that serves multiple towns appears multiple times. ~120,000 unique 7-digit
codes total.

Licence
-------
Japan Post permits free redistribution of the KEN_ALL data, including for
commercial use, with no formal licence (effectively public-domain in
practice). Each generated row records ``source: "japan-post"`` for
provenance.

What this script does
---------------------
1. Reads KEN_ALL.CSV (Shift-JIS) row by row
2. Picks ONE representative locality per unique 7-digit zip — the FIRST
   row encountered (KEN_ALL's natural ordering by JIS code is geographic,
   so this gives a stable "primary" town per zip without scoring)
3. Resolves country_id (JP) and state_id by stripping the prefecture suffix
   (県/府/都/道) from the kanji name and matching against states.native
4. Emits codes in the canonical "###-####" format (regex requires it)
5. Writes contributions/postcodes/JP.json (~120,000 records)
6. Idempotent merge with existing curated rows by (code, locality_name)

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://www.post.japanpost.jp/zipcode/dl/kogaki/zip/ken_all.zip',
      '/tmp/ken_all.zip')"
    unzip -o /tmp/ken_all.zip -d /tmp/

    python3 bin/scripts/sync/import_japan_post_postcodes.py \\
      --input /tmp/KEN_ALL.CSV
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


PREFECTURE_SUFFIXES = ("都", "道", "府", "県")  # Tokyo-to, Hokkai-do, Osaka/Kyoto-fu, *-ken


def strip_prefecture_suffix(name: str) -> str:
    """Drop the trailing 都/道/府/県 so 北海道 -> 北海, 青森県 -> 青森, etc.

    Hokkaido is the special case — its native form in states.json is
    literally '北海道' (the full name), so we keep that record's native
    intact and match BOTH the suffix-stripped CSV form ('北海') AND the
    full form. A two-pass lookup handles this without hardcoding.
    """
    if name and name.endswith(PREFECTURE_SUFFIXES):
        return name[:-1]
    return name


def build_state_lookup(states_for_jp: List[dict]) -> Dict[str, dict]:
    """Native-name -> state. Keys include both raw and suffix-stripped forms."""
    lookup: Dict[str, dict] = {}
    for s in states_for_jp:
        native = (s.get("native") or "").strip()
        if not native:
            continue
        lookup[native] = s
        stripped = strip_prefecture_suffix(native)
        if stripped:
            lookup[stripped] = s
    return lookup


def resolve_state(csv_kanji: str, lookup: Dict[str, dict]) -> Optional[dict]:
    """Match KEN_ALL's kanji prefecture name to a state record."""
    if not csv_kanji:
        return None
    # Direct match (handles the few states.json entries that already include 県/府)
    if csv_kanji in lookup:
        return lookup[csv_kanji]
    # Suffix-stripped fallback (the common case)
    stripped = strip_prefecture_suffix(csv_kanji)
    if stripped in lookup:
        return lookup[stripped]
    return None


def format_code(zip7: str) -> Optional[str]:
    """Convert KEN_ALL's 7-digit zip to canonical ###-#### form."""
    z = (zip7 or "").strip()
    if len(z) == 7 and z.isdigit():
        return f"{z[:3]}-{z[3:]}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/KEN_ALL.CSV",
                        help="Path to KEN_ALL.CSV (Shift-JIS encoded)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"ERROR: input not found: {csv_path}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    jp = next((c for c in countries if c.get("iso2") == "JP"), None)
    if jp is None:
        print("ERROR: JP not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    jp_states = [s for s in states if s.get("country_id") == jp["id"]]
    state_lookup = build_state_lookup(jp_states)
    print(f"Country: Japan (id={jp['id']}); states indexed: {len(jp_states)}")

    seen: set = set()
    records: List[dict] = []
    unresolved_prefs: Dict[str, int] = {}
    bad_codes = 0

    with csv_path.open(encoding="shift_jis", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 9:
                continue
            zip7 = row[2]
            kanji_pref = (row[6] or "").strip()
            kanji_city = (row[7] or "").strip()
            kanji_town = (row[8] or "").strip()
            code = format_code(zip7)
            if not code:
                bad_codes += 1
                continue
            if code in seen:
                continue
            seen.add(code)

            record = {
                "code": code,
                "country_id": int(jp["id"]),
                "country_code": "JP",
            }
            state = resolve_state(kanji_pref, state_lookup)
            if state is not None:
                record["state_id"] = int(state["id"])
                if state.get("iso2"):
                    record["state_code"] = state["iso2"]
            else:
                unresolved_prefs[kanji_pref] = unresolved_prefs.get(kanji_pref, 0) + 1

            # Build a human-readable locality "City, Town" using kanji.
            # KEN_ALL uses placeholder text like "以下に掲載がない場合"
            # ("the following is not listed") for catch-all entries; treat
            # those as no town so the locality_name reads cleanly.
            if kanji_town and kanji_town in {"以下に掲載がない場合", "（注）"}:
                locality = kanji_city
            elif kanji_city and kanji_town:
                locality = f"{kanji_city}{kanji_town}"
            else:
                locality = kanji_city or kanji_town
            if locality:
                record["locality_name"] = locality

            record["type"] = "full"
            record["source"] = "japan-post"
            records.append(record)

    records.sort(key=lambda r: (r["code"], r.get("locality_name", "")))

    with_state = sum(1 for r in records if "state_id" in r)
    print(f"Records:        {len(records):,}")
    print(f"  with state:   {with_state:,} ({with_state*100//max(1,len(records))}%)")
    print(f"  bad codes:    {bad_codes:,}")
    if unresolved_prefs:
        print(f"  unresolved prefectures: {sorted(unresolved_prefs.items(), key=lambda kv: -kv[1])[:5]}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/JP.json"
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        seen_pairs = {(r["code"], (r.get("locality_name") or "").lower()) for r in existing}
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in seen_pairs:
                merged.append(r)
                seen_pairs.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = records

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
