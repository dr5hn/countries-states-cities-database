#!/usr/bin/env python3
"""Denmark DAWA -> contributions/postcodes/DK.json importer for issue #1039.

Source data
-----------
The Danish public-sector address database DAWA (Danmarks Adressers
Web API) is published by Dataforsyningen / SDFI under **CC-0**:

  https://api.dataforsyningen.dk/postnumre  - postcodes (~1,090)
  https://api.dataforsyningen.dk/kommuner   - municipalities with region info

Each postcode (postnummer) has:
  nr (4-digit code) | navn (locality) | kommuner (array of municipalities)
  | bbox / visueltcenter (centroid coords)

What this script does
---------------------
1. Fetches /kommuner to build a kommune-code -> region-name map
2. Fetches /postnumre and resolves region via the first kommune of each
   postcode (postcodes spanning multiple kommuner virtually always stay
   within one region; the first-kommune choice is a stable canonical pick)
3. Maps Danish region names to states.json iso2 codes
4. Writes contributions/postcodes/DK.json

License & attribution
---------------------
- Source: SDFI / Dataforsyningen DAWA (CC-0)
- Each row: source: "dawa"
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

DAWA_BASE = "https://api.dataforsyningen.dk"

# Danish region name (DAWA) -> state.iso2 in this dataset.
# states.json names "Denmark" iso2 84 — confusingly that's actually the
# Capital Region (Region Hovedstaden), not all of Denmark.
REGION_TO_ISO2: Dict[str, str] = {
    "Region Hovedstaden": "84",  # Capital Region (called "Denmark" in states.json)
    "Region Sjælland":    "85",  # Zealand
    "Region Syddanmark":  "83",  # Southern Denmark
    "Region Midtjylland": "82",  # Central Denmark
    "Region Nordjylland": "81",  # North Denmark
}


def fetch_json(path: str) -> list:
    req = urllib.request.Request(
        DAWA_BASE + path,
        headers={"User-Agent": "csc-database-postcode-importer", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    return body if isinstance(body, list) else [body]


def parse_coord(v) -> Optional[str]:
    if v is None:
        return None
    try:
        f = float(v)
        if abs(f) > 180:
            return None
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except (TypeError, ValueError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    dk = next((c for c in countries if c.get("iso2") == "DK"), None)
    if dk is None:
        print("ERROR: DK not in countries.json", file=sys.stderr)
        return 2
    states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))
    dk_states = [s for s in states if s.get("country_id") == dk["id"]]
    state_by_iso2: Dict[str, dict] = {(s.get("iso2") or "").upper(): s for s in dk_states if s.get("iso2")}
    print(f"Country: Denmark (id={dk['id']}); states indexed: {len(state_by_iso2)}")

    print("Fetching /kommuner...")
    kommuner = fetch_json("/kommuner")
    kommune_to_region: Dict[str, str] = {}
    for k in kommuner:
        kode = (k.get("kode") or "").strip()
        region = (k.get("region") or {}).get("navn") or ""
        if kode and region:
            kommune_to_region[kode] = region
    print(f"  kommuner indexed: {len(kommune_to_region)}")

    print("Fetching /postnumre...")
    postnumre = fetch_json("/postnumre")
    print(f"  postnumre: {len(postnumre)}")

    records: List[dict] = []
    matched_state = 0
    matched_coord = 0
    for p in sorted(postnumre, key=lambda r: r.get("nr") or ""):
        code = (p.get("nr") or "").strip()
        if not code or not code.isdigit() or len(code) != 4:
            continue
        record = {
            "code": code,
            "country_id": int(dk["id"]),
            "country_code": "DK",
        }
        kommuner_for_code = p.get("kommuner") or []
        if kommuner_for_code:
            kode = (kommuner_for_code[0].get("kode") or "").strip()
            region_name = kommune_to_region.get(kode, "")
            iso2 = REGION_TO_ISO2.get(region_name)
            if iso2 and iso2 in state_by_iso2:
                state = state_by_iso2[iso2]
                record["state_id"] = int(state["id"])
                record["state_code"] = iso2
                matched_state += 1
        navn = (p.get("navn") or "").strip()
        if navn:
            record["locality_name"] = navn
        record["type"] = "full"
        center = p.get("visueltcenter") or []
        if isinstance(center, list) and len(center) == 2:
            lng = parse_coord(center[0])
            lat = parse_coord(center[1])
            if lat is not None and lng is not None:
                record["latitude"] = lat
                record["longitude"] = lng
                matched_coord += 1
        record["source"] = "dawa"
        records.append(record)

    print(f"Records:        {len(records):,}")
    print(f"  with state:   {matched_state:,} ({matched_state*100//max(1,len(records))}%)")
    print(f"  with coords:  {matched_coord:,} ({matched_coord*100//max(1,len(records))}%)")

    if args.dry_run:
        return 0

    target = project_root / "contributions/postcodes/DK.json"
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
    size_kb = target.stat().st_size / 1024
    print(f"\n[OK] Wrote {target.relative_to(project_root)} ({len(merged):,} rows, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
