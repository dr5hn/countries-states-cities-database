#!/usr/bin/env python3
"""Tunisia -> contributions/postcodes/TN.json importer for issue #1039.

Source data
-----------
The community ``JenhaniChedli/TunisiaGeodataAPI`` repository ships
postcodes.json — 4,868 La Poste Tunisienne 4-digit postcodes joined
with the full Gouvernorat / Délégation / Cité (locality) hierarchy.

    [{"Gov": "Ariana", "Deleg": "Sidi Thabet",
      "Cite": "Cite Dridi", "zip": "2032"}, ...]

Source URL: https://raw.githubusercontent.com/JenhaniChedli/TunisiaGeodataAPI/master/postcodes.json

What this script does
---------------------
1. Fetches the JSON via urllib (curl is blocked).
2. Resolves state FK via ASCII-fold + name match against CSC's 24
   gouvernorat entries, with one alias for the source's
   'Mannouba' -> CSC 'Manouba' single-letter spelling drift.
3. Emits one row per (zip, Cite, Deleg) tuple.
4. Writes contributions/postcodes/TN.json idempotently.

Coverage upgrade
----------------
The previously-tracked ``hajer77/postCodeTunisia-api`` source ships
only ~9 records covering 8 of 24 governorates. This source has
**all 24 governorates** with 4,868 localities — confirmed via direct
inspection. The research doc Tier B note for Tunisia
(`Stub only (8/24)`) is now stale and superseded.

License & attribution
---------------------
- Source: JenhaniChedli/TunisiaGeodataAPI (no formal LICENSE file)
- Upstream: La Poste Tunisienne publicly published codes
- Each row: ``source: "la-poste-tunisienne-via-jenhani-chedli"``

Tier 5 per #1039 license-tier policy.

Usage
-----
    python3 bin/scripts/sync/import_tunisia_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, List


SOURCE_URL = (
    "https://raw.githubusercontent.com/JenhaniChedli/TunisiaGeodataAPI/"
    "master/postcodes.json"
)

# Source -> CSC name. Only entries where direct ASCII-fold match fails.
GOV_ALIASES: Dict[str, str] = {
    "Mannouba": "Manouba",  # source spells with double 'n'
}


def _ascii_fold(value: str) -> str:
    return (
        "".join(
            c
            for c in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(c)
        )
        .strip()
        .lower()
    )


def fetch_json(url: str) -> List[dict]:
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

    rows = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    print(f"Source rows: {len(rows):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    tn_country = next((c for c in countries if c.get("iso2") == "TN"), None)
    if tn_country is None:
        print("ERROR: TN not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(tn_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    tn_states = [s for s in states if s.get("country_id") == tn_country["id"]]
    state_by_fold: Dict[str, dict] = {
        _ascii_fold(s["name"]): s for s in tn_states if s.get("name")
    }
    print(
        f"Country: Tunisia (id={tn_country['id']}); states indexed: {len(tn_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_no_code = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_govs: Dict[str, int] = {}

    for row in rows:
        raw_code = (row.get("zip") or "").strip()
        if not raw_code:
            skipped_no_code += 1
            continue
        code = raw_code.zfill(4) if raw_code.isdigit() else raw_code
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        gov_raw = (row.get("Gov") or "").strip()
        gov_alias = GOV_ALIASES.get(gov_raw, gov_raw)
        state = state_by_fold.get(_ascii_fold(gov_alias))
        if state is None:
            unknown_govs[gov_raw] = unknown_govs.get(gov_raw, 0) + 1
            skipped_no_state += 1

        cite = (row.get("Cite") or "").strip()
        deleg = (row.get("Deleg") or "").strip()
        if cite and deleg and cite.lower() != deleg.lower():
            locality = f"{cite}, {deleg}"
        else:
            locality = cite or deleg

        key = (code, locality.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(tn_country["id"]),
            "country_code": "TN",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "la-poste-tunisienne-via-jenhani-chedli"
        records.append(record)

    print(f"Skipped (no code):     {skipped_no_code:,}")
    print(f"Skipped (regex fail):  {skipped_bad_regex:,}")
    print(f"Skipped (no state FK): {skipped_no_state:,}")
    print(f"Records emitted:       {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:          {matched_state:,} ({pct}%)")
    if unknown_govs:
        print("Unknown governorates (not in CSC + GOV_ALIASES):")
        for g, n in sorted(unknown_govs.items(), key=lambda x: -x[1]):
            print(f"  {g!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/TN.json"
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
