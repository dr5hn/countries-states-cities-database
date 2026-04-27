#!/usr/bin/env python3
"""La Poste -> contributions/postcodes/{ISO2}.json importer for issue #1039.

Source data
-----------
La Poste publishes the canonical French commune-to-postcode mapping under
the etalab-2.0 open license at:

  https://www.data.gouv.fr/fr/datasets/base-officielle-des-codes-postaux/

The CSV (``laposte_hexasmal.csv``) has columns:
  Code_commune_INSEE | Nom_commune | Code_postal | Libelle_d_acheminement | Ligne_5

Approximately 39,000 rows covering metropolitan France, Corsica, and the
five overseas departments (Guadeloupe 971, Martinique 972, French Guiana
973, Réunion 974, Mayotte 976) plus the collectivities (Saint-Barthélemy
971, Saint-Martin 971, Saint-Pierre-et-Miquelon 975, Wallis-et-Futuna 986,
French Polynesia 987, New Caledonia 988).

What this script does
---------------------
1. Reads ``laposte_hexasmal.csv`` from a local path (default ``/tmp/laposte_hexasmal.csv``)
2. Resolves country_id from postcode prefix → ISO2 via the OVERSEAS_PREFIX_MAP
3. Fuzzy-matches commune name to existing states (where applicable) for FK resolution
4. Writes one ``contributions/postcodes/{ISO2}.json`` per overseas territory
5. Preserves the existing manual entries (idempotent merge by code+country)

Why only overseas territories
-----------------------------
Metropolitan France has ~36,000 communes and would generate a 4 MB JSON
file — fits the gzip-to-Releases pipeline (#1374) but is a separate review
scope. This script handles the small (~250 row) overseas set first; metro
France is a follow-up flag.

License
-------
Source: data.gouv.fr (etalab-2.0, attribution required).
Each generated record sets ``source: "laposte"`` so attribution can be
programmatically assembled at export time.

Usage
-----
    # Manual download (one-time)
    curl -L -o /tmp/laposte_hexasmal.csv \\
      "https://www.data.gouv.fr/fr/datasets/r/d9faa17b-ee8b-414e-8a5f-95fde9ff0e80"

    # Run the importer (writes contributions/postcodes/{ISO2}.json)
    python3 bin/scripts/sync/import_laposte_postcodes.py \\
      --input /tmp/laposte_hexasmal.csv \\
      --territories GP,MQ,GF,RE,YT,PM,WF,PF,NC,BL,MF
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Postcode-prefix → (ISO2, label). Order matters: more-specific prefixes first.
OVERSEAS_PREFIX_MAP: List[Tuple[str, str, str]] = [
    ("97133", "BL", "Saint-Barthelemy"),
    ("97150", "MF", "Saint-Martin (French part)"),
    ("97500", "PM", "Saint Pierre and Miquelon"),
    ("971",   "GP", "Guadeloupe"),
    ("972",   "MQ", "Martinique"),
    ("973",   "GF", "French Guiana"),
    ("974",   "RE", "Reunion"),
    ("976",   "YT", "Mayotte"),
    ("986",   "WF", "Wallis and Futuna Islands"),
    ("987",   "PF", "French Polynesia"),
    ("988",   "NC", "New Caledonia"),
]


def classify(code: str) -> Optional[Tuple[str, str]]:
    """Return (iso2, label) for a postcode, or None if metropolitan/unmatched."""
    for prefix, iso2, label in OVERSEAS_PREFIX_MAP:
        if code.startswith(prefix):
            return iso2, label
    return None


def load_repo_data(project_root: Path) -> Tuple[Dict[str, dict], Dict[int, dict]]:
    """Load countries and states keyed for FK resolution."""
    with (project_root / "contributions/countries/countries.json").open(encoding="utf-8") as f:
        countries_by_iso2 = {c["iso2"]: c for c in json.load(f) if c.get("iso2")}
    with (project_root / "contributions/states/states.json").open(encoding="utf-8") as f:
        states = json.load(f)
    states_by_country: Dict[int, List[dict]] = defaultdict(list)
    for s in states:
        cid = s.get("country_id")
        if cid is not None:
            states_by_country[int(cid)].append(s)
    return countries_by_iso2, states_by_country


def resolve_state_id(
    locality_name: str,
    country_id: int,
    states_by_country: Dict[int, List[dict]],
) -> Tuple[Optional[int], Optional[str]]:
    """Best-effort exact-name match of commune to a state record.

    Returns (state_id, state_code) or (None, None) when no confident match exists.
    Deliberately conservative: only exact case-insensitive name matches succeed,
    so spurious associations are avoided. The state_id remains null when in doubt.
    """
    target = locality_name.strip().lower()
    for s in states_by_country.get(country_id, []):
        candidates = {
            (s.get("name") or "").strip().lower(),
            (s.get("native") or "").strip().lower(),
        }
        if target in candidates:
            return int(s["id"]), s.get("iso2")
    return None, None


def build_records(
    csv_path: Path,
    countries_by_iso2: Dict[str, dict],
    states_by_country: Dict[int, List[dict]],
    territories: Optional[set] = None,
) -> Dict[str, List[dict]]:
    """Stream the CSV and group rows into per-ISO2 record lists."""
    by_iso2: Dict[str, List[dict]] = defaultdict(list)
    seen: Dict[str, set] = defaultdict(set)  # de-dup (code, locality) per ISO2

    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            code = (row.get("Code_postal") or "").strip()
            commune = (row.get("Nom_commune") or row.get("Libelle_d_acheminement") or "").strip()
            if not code or not commune:
                continue

            classified = classify(code)
            if classified is None:
                continue
            iso2, _label = classified
            if territories is not None and iso2 not in territories:
                continue

            country = countries_by_iso2.get(iso2)
            if country is None:
                continue

            dedup_key = (code, commune.lower())
            if dedup_key in seen[iso2]:
                continue
            seen[iso2].add(dedup_key)

            country_id = int(country["id"])
            state_id, state_code = resolve_state_id(commune, country_id, states_by_country)

            record = {
                "code": code,
                "country_id": country_id,
                "country_code": iso2,
            }
            if state_id is not None:
                record["state_id"] = state_id
                if state_code:
                    record["state_code"] = state_code
            record["locality_name"] = commune
            record["type"] = "full"
            record["source"] = "laposte"
            by_iso2[iso2].append(record)

    return by_iso2


def merge_with_existing(
    project_root: Path, iso2: str, new_records: List[dict]
) -> List[dict]:
    """Merge new La Poste rows with the existing manual file.

    Existing manual rows win when they share the same code, so curated
    locality names and state assignments are preserved. New codes are appended.
    """
    target = project_root / f"contributions/postcodes/{iso2}.json"
    existing: List[dict] = []
    if target.exists():
        with target.open(encoding="utf-8") as f:
            existing = json.load(f)

    by_code: Dict[str, dict] = {}
    for rec in existing:
        by_code[rec["code"]] = rec
    for rec in new_records:
        by_code.setdefault(rec["code"], rec)

    return sorted(by_code.values(), key=lambda r: r["code"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="/tmp/laposte_hexasmal.csv",
        help="Path to laposte_hexasmal.csv (default: /tmp/laposte_hexasmal.csv)",
    )
    parser.add_argument(
        "--territories",
        default="GP,MQ,GF,RE,YT,PM,WF,PF,NC,BL,MF",
        help="Comma-separated ISO2 codes to import (default: all overseas)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary; do not write files",
    )
    args = parser.parse_args()

    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"ERROR: input CSV not found: {csv_path}", file=sys.stderr)
        print(
            "Download with:\n"
            "  curl -L -o /tmp/laposte_hexasmal.csv \\\n"
            "    https://www.data.gouv.fr/fr/datasets/r/d9faa17b-ee8b-414e-8a5f-95fde9ff0e80",
            file=sys.stderr,
        )
        return 2

    project_root = Path(__file__).resolve().parents[3]
    territories = {t.strip() for t in args.territories.split(",") if t.strip()}

    countries_by_iso2, states_by_country = load_repo_data(project_root)
    print(f"Loaded {len(countries_by_iso2)} countries, "
          f"{sum(len(v) for v in states_by_country.values())} states")

    by_iso2 = build_records(csv_path, countries_by_iso2, states_by_country, territories)

    print()
    print(f"{'ISO2':<6} {'Records':>8}  {'with-state':>12}  Sample code")
    print("-" * 50)
    for iso2 in sorted(by_iso2):
        records = by_iso2[iso2]
        with_state = sum(1 for r in records if "state_id" in r)
        sample = records[0]["code"] if records else "-"
        print(f"{iso2:<6} {len(records):>8}  {with_state:>12}  {sample}")

    if args.dry_run:
        print("\n--dry-run set; no files written.")
        return 0

    print()
    written = 0
    for iso2, records in sorted(by_iso2.items()):
        merged = merge_with_existing(project_root, iso2, records)
        target = project_root / f"contributions/postcodes/{iso2}.json"
        with target.open("w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
            f.write("\n")
        added = len(merged) - sum(1 for _ in (target.exists() and []))
        print(f"  + {target.relative_to(project_root)} ({len(merged)} records)")
        written += 1

    print(f"\n[OK] Wrote {written} country files. "
          f"Source attribution recorded as source=\"laposte\" on each new row.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
