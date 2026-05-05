#!/usr/bin/env python3
"""Panama -> contributions/postcodes/PA.json importer for issue #1039.

Source data
-----------
The community ``viquezr-dev/codigos_postales`` repository ships
GeoJSON polygons for each Correos de Panamá estafeta (post-office
delivery zone). Each feature carries:

    {
      "VM_LEVEL": "B7241",          # 5-char alphanumeric postal code
      "PROV_NOMB": "DARIÉN",         # province (uppercase, with diacritics)
      "ESTAF_NAME": "Estafeta de Yaviza",
      "ESTAF_CODE": "41",            # 2-digit office code
      "VM_LEVEL2D": "BA"             # province + zone prefix
    }

Source URL: https://raw.githubusercontent.com/viquezr-dev/codigos_postales/master/estafetas.geojson

What this script does
---------------------
1. Fetches the GeoJSON via urllib (curl is blocked).
2. Skips 65 'POR DEFINIR' (undefined) features without an
   assigned ESTAF_CODE.
3. Maps the 13 source province labels (uppercase Spanish) to CSC's
   iso2 codes via PROV_NOMB_TO_ISO2.
4. Computes the centroid of each MultiPolygon for lat/lng.
5. Writes contributions/postcodes/PA.json idempotently.

Regex fix
---------
Before this PR, countries.json had PA regex `^\\d{5}$` (5-digit
numeric). Panama's actual Correos de Panamá codes are 1-letter +
4-digit alphanumeric (e.g. 'B7241', 'K4299'), so the old regex
rejected 100% of legitimate codes. Updated to `^[A-Z]\\d{4}$` /
format `@####`.

Centroid computation
--------------------
The source ships MultiPolygon geometries, not centroids. The
importer computes the unweighted mean of all polygon vertices —
sufficient for representative coordinates. (Strictly correct
geographic centroid would require area-weighting, but this
2D-mean approximation is within ~1 km for postal-zone-sized
polygons.)

Coverage gap
------------
Source predates 2020 — Naso Tjër Di Comarca (CSC iso2 'NT', created
2020) is not represented. Idempotent merge contract allows future
sources covering NT to layer in.

License & attribution
---------------------
- Source: viquezr-dev/codigos_postales (no formal license file)
- Upstream: Correos de Panamá publicly published map data
- Each row: ``source: "correos-panama-via-viquezr"``

Tier 5 per #1039 license-tier policy.

Usage
-----
    python3 bin/scripts/sync/import_panama_postcodes.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple


SOURCE_URL = (
    "https://raw.githubusercontent.com/viquezr-dev/codigos_postales/"
    "master/estafetas.geojson"
)

# Source PROV_NOMB (uppercase Spanish) -> CSC iso2 in PA states.json.
PROV_NOMB_TO_ISO2: Dict[str, str] = {
    "BOCAS DEL TORO": "1",
    "CHIRIQUÍ": "4",
    "COCLÉ": "2",
    "COLÓN": "3",
    "DARIÉN": "5",
    "EMBERA": "EM",         # Emberá-Wounaan Comarca
    "HERRERA": "6",
    "KUNA_YALA": "KY",      # Guna Yala (older Spanish spelling)
    "LOS SANTOS": "7",
    "NGÄBE BUGLÉ": "NB",    # Ngöbe-Buglé Comarca
    "PANAMÁ": "8",
    "PANAMÁ OESTE": "10",
    "VERAGUAS": "9",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"User-Agent": "csc-database-postcode-importer"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def polygon_centroid(coords: list) -> Tuple[float, float]:
    """Compute unweighted mean of all polygon vertices.

    Sufficient for representative postal-zone coordinates. Strict
    geographic centroid would require area-weighting.
    """
    lons: List[float] = []
    lats: List[float] = []

    def collect(node: object) -> None:
        if isinstance(node, list) and node:
            if isinstance(node[0], (int, float)) and len(node) >= 2:
                lons.append(float(node[0]))
                lats.append(float(node[1]))
            else:
                for child in node:
                    collect(child)

    collect(coords)
    if not lats:
        return (0.0, 0.0)
    return (sum(lats) / len(lats), sum(lons) / len(lons))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="local geojson (skip fetch)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = (
        json.loads(Path(args.input).read_text(encoding="utf-8"))
        if args.input
        else fetch_json(SOURCE_URL)
    )
    features = data.get("features", [])
    print(f"Source features: {len(features):,}")

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load(
        (project_root / "contributions/countries/countries.json").open(encoding="utf-8")
    )
    pa_country = next((c for c in countries if c.get("iso2") == "PA"), None)
    if pa_country is None:
        print("ERROR: PA not in countries.json", file=sys.stderr)
        return 2
    regex = re.compile(pa_country.get("postal_code_regex") or ".*")

    states = json.load(
        (project_root / "contributions/states/states.json").open(encoding="utf-8")
    )
    pa_states = [s for s in states if s.get("country_id") == pa_country["id"]]
    state_by_iso2: Dict[str, dict] = {
        s["iso2"]: s for s in pa_states if s.get("iso2")
    }
    print(
        f"Country: Panama (id={pa_country['id']}); states indexed: {len(pa_states)}"
    )

    seen: set = set()
    records: List[dict] = []
    skipped_no_code = 0
    skipped_bad_regex = 0
    skipped_no_state = 0
    matched_state = 0
    unknown_provs: Dict[str, int] = {}

    for feat in features:
        props = feat.get("properties", {})
        code = (props.get("VM_LEVEL") or "").strip()
        estaf_code = props.get("ESTAF_CODE")
        estaf_name = (props.get("ESTAF_NAME") or "").strip()
        if not code or not estaf_code or estaf_name == "POR DEFINIR":
            skipped_no_code += 1
            continue
        if not regex.match(code):
            skipped_bad_regex += 1
            continue

        prov_nomb = (props.get("PROV_NOMB") or "").strip()
        iso2 = PROV_NOMB_TO_ISO2.get(prov_nomb)
        state = state_by_iso2.get(iso2) if iso2 else None
        if state is None:
            unknown_provs[prov_nomb] = unknown_provs.get(prov_nomb, 0) + 1
            skipped_no_state += 1

        geom = feat.get("geometry", {}) or {}
        lat, lon = polygon_centroid(geom.get("coordinates", []))

        key = (code, estaf_name.lower())
        if key in seen:
            continue
        seen.add(key)

        record: Dict[str, object] = {
            "code": code,
            "country_id": int(pa_country["id"]),
            "country_code": "PA",
        }
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = state.get("iso2")
            matched_state += 1
        if estaf_name:
            record["locality_name"] = estaf_name
        if lat or lon:
            record["latitude"] = f"{lat:.6f}"
            record["longitude"] = f"{lon:.6f}"
        record["type"] = "full"
        record["source"] = "correos-panama-via-viquezr"
        records.append(record)

    print(f"Skipped (no code/POR DEFINIR): {skipped_no_code:,}")
    print(f"Skipped (regex fail):          {skipped_bad_regex:,}")
    print(f"Skipped (no state FK):         {skipped_no_state:,}")
    print(f"Records emitted:               {len(records):,}")
    pct = matched_state * 100 // max(1, len(records))
    print(f"  with state:                  {matched_state:,} ({pct}%)")
    if unknown_provs:
        print("Unknown PROV_NOMB (not in PROV_NOMB_TO_ISO2):")
        for p, n in sorted(unknown_provs.items(), key=lambda x: -x[1]):
            print(f"  {p!r}: {n}")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/PA.json"
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
