#!/usr/bin/env python3
"""La Poste -> contributions/postcodes/FR.json importer for issue #1039.

Source data
-----------
La Poste publishes the canonical commune-to-postcode mapping under the
**Licence Ouverte v2.0 (etalab-2.0)** at:

  https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/

The CSV resource (``laposte_hexasmal``) is hosted on Datanova and exported
as semicolon-delimited ISO-8859-1 with these columns:

  #Code_commune_INSEE | Nom_de_la_commune | Code_postal |
  Libellé_d_acheminement | Ligne_5

~39,000 commune-postcode rows; ~6,300 unique postcodes.

What this script does
---------------------
1. Reads laposte_hexasmal.csv (latin-1 encoded, semicolon-delimited)
2. Filters to metropolitan France only (skips 971-988 overseas prefixes —
   those are routed to their own ISO2 territory files in separate PRs)
3. Picks one canonical commune per unique postcode (first alphabetical)
4. Resolves state_id by mapping the postcode's first 2 digits to
   state.iso2 (French départements are keyed by 2-digit code: 75=Paris,
   13=Bouches-du-Rhône, etc.) with Corsica's special split:
     - 200xx-201xx -> 2A (Corse-du-Sud)
     - 202xx-209xx -> 2B (Haute-Corse)
5. Writes contributions/postcodes/FR.json
6. Idempotent merge with existing curated rows by (code, locality_name)

Why metropolitan only
---------------------
French overseas territories (Guadeloupe 971, Martinique 972, French Guiana
973, Réunion 974, Saint-Pierre-et-Miquelon 975, Mayotte 976, Wallis-et-
Futuna 986, French Polynesia 987, New Caledonia 988, Saint-Barthélemy
97133, Saint-Martin 97150) are SEPARATE countries in this dataset's
ISO2 schema, with their own contributions/postcodes/{ISO2}.json files
already curated (#1402 through #1426). Routing La Poste's overseas rows
to those files is a follow-up scope decision.

License & attribution
---------------------
- Source: La Poste / data.gouv.fr (Licence Ouverte v2.0 / etalab-2.0)
- Each row records source: "laposte"

Usage
-----
    python3 -c "import urllib.request; urllib.request.urlretrieve(
      'https://datanova.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw',
      '/tmp/laposte_hexasmal.csv')"

    python3 bin/scripts/sync/import_laposte_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


# Postcodes belonging to overseas territories or to Monaco: skip in FR import.
# Overseas land in their own ISO2 contribution files (BL/MF/GP/MQ/GF/RE/YT/PM/
# WF/PF/NC, already curated). 980 = Monaco (separate country, MC.json shipped
# in #1402).
SKIP_PREFIXES = ("971", "972", "973", "974", "975", "976", "980", "986", "987", "988")

# states.json uses suffixed iso2 codes for Paris (75C) and Lyon Metropolis (69M)
# instead of the bare 75 / 69. Map the postcode-prefix -> state-iso2 before
# falling back to the simple two-digit lookup.
PREFIX_OVERRIDES: Dict[str, str] = {
    "75": "75C",  # Paris
}


def resolve_state(code: str, state_by_iso2: Dict[str, dict]) -> Optional[dict]:
    """Map a metropolitan French postcode to a département state record."""
    if not code or len(code) < 2:
        return None
    # Corsica: 200xx-201xx -> 2A (Corse-du-Sud), 202xx-209xx -> 2B (Haute-Corse)
    if code.startswith("20"):
        if len(code) >= 3 and code[2] in ("0", "1"):
            return state_by_iso2.get("2A")
        return state_by_iso2.get("2B")
    prefix = code[:2]
    override = PREFIX_OVERRIDES.get(prefix)
    if override and override in state_by_iso2:
        return state_by_iso2[override]
    return state_by_iso2.get(prefix)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="/tmp/laposte_hexasmal.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"ERROR: input not found: {csv_path}", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    fr = next((c for c in countries if c.get("iso2") == "FR"), None)
    if fr is None:
        print("ERROR: FR not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    fr_states = [s for s in states if s.get("country_id") == fr["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in fr_states if s.get("iso2")}
    print(f"Country: France (id={fr['id']}); states indexed by iso2: {len(state_by_iso2)}")

    # Group rows by postcode; pick first alphabetical commune as canonical
    by_postcode: Dict[str, List[dict]] = {}
    skipped_overseas = 0
    skipped_bad = 0
    with csv_path.open(encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            code = (row.get("Code_postal") or "").strip()
            commune = (row.get("Nom_de_la_commune") or "").strip()
            if not code or not code.isdigit() or len(code) != 5:
                skipped_bad += 1
                continue
            if any(code.startswith(p) for p in SKIP_PREFIXES):
                skipped_overseas += 1
                continue
            by_postcode.setdefault(code, []).append({
                "commune": commune,
                "insee": (row.get("#Code_commune_INSEE") or "").strip(),
                "libelle": (row.get("Libellé_d_acheminement") or "").strip(),
            })

    print(f"Skipped overseas rows:  {skipped_overseas:,}")
    print(f"Skipped malformed:      {skipped_bad:,}")
    print(f"Unique metro postcodes: {len(by_postcode):,}")

    records: List[dict] = []
    matched_state = 0
    for code in sorted(by_postcode):
        rows = sorted(by_postcode[code], key=lambda r: r["commune"].upper())
        chosen = rows[0]
        record = {
            "code": code,
            "country_id": int(fr["id"]),
            "country_code": "FR",
        }
        state = resolve_state(code, state_by_iso2)
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2") or ""
            matched_state += 1
        # Prefer the cleaner Libellé d'acheminement (mailing label) for locality
        # over the raw commune name. INSEE commune names are often all-caps and
        # spell-stripped (e.g. "L ABERGEMENT CLEMENCIAT" vs the cleaner
        # "L'Abergement-Clémenciat" elsewhere). The acheminement label is the
        # version La Poste actually uses on mail.
        locality = chosen["libelle"] or chosen["commune"]
        if locality:
            record["locality_name"] = locality
        record["type"] = "full"
        record["source"] = "laposte"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/FR.json"
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)
        seen = {(r["code"], (r.get("locality_name") or "").lower()) for r in existing}
        merged = list(existing)
        for r in records:
            key = (r["code"], (r.get("locality_name") or "").lower())
            if key not in seen:
                merged.append(r)
                seen.add(key)
        merged.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    else:
        merged = sorted(records, key=lambda r: (r["code"], r.get("locality_name", "")))

    with target.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    size_mb = target.stat().st_size / (1024 * 1024)
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
