#!/usr/bin/env python3
"""SK + RO + SI batch importer for issue #1039.

Bundles three small-to-medium European countries with confirmed
redistributable postcode mirrors into a single pipeline:

  Slovakia (SK)   - FeroVolar/PSC-JSON (community redistribution of
                    Slovenská pošta data)        ~4,000 records
  Romania  (RO)   - alexionegit/coduripostaleRomaniaPS
                    (community CSV with judete)   ~13,750 records
  Slovenia (SI)   - dlabs/postcode_si
                    (community Posta Slovenije CSV) ~600 records

Each country has its own state-resolution strategy:
  SK -> KRAJ field is the 2-letter region ISO code matching states.iso2
  RO -> judet text needs ASCII-fold match to states.iso2
  SI -> ships country-only (source has no municipality/region info,
        and SI postcodes don't map cleanly to administrative regions)

Each row records source: "{provider}" for attribution.

Usage
-----
    # Fetches done out-of-band:
    curl -L -o /tmp/sk_obce.json   https://raw.githubusercontent.com/FeroVolar/PSC-JSON/master/obce.json
    curl -L -o /tmp/ro_coduri.csv  "https://raw.githubusercontent.com/alexionegit/coduripostaleRomaniaPS/master/coduri%20postale.csv"
    curl -L -o /tmp/si_codes.csv   https://raw.githubusercontent.com/dlabs/postcode_si/master/data/20130103-stevilke_final.csv

    python3 bin/scripts/sync/import_eu_batch1_postcodes.py
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional


def ascii_fold(s: str) -> str:
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    # Drop combining marks, then collapse hyphens/dashes to spaces and squeeze
    # whitespace — the source CSV uses spaces ("CARAS SEVERIN") where states.json
    # uses dashes ("Caraș-Severin").
    plain = "".join(ch for ch in nfkd if not unicodedata.combining(ch))
    plain = re.sub(r"[\-‐-―]", " ", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain


def parse_coord(v) -> Optional[str]:
    if v is None or v == "":
        return None
    try:
        f = float(v)
        if abs(f) > 180:
            return None
        return f"{f:.8f}".rstrip("0").rstrip(".") or "0"
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Slovakia: FeroVolar/PSC-JSON
# ---------------------------------------------------------------------------

def import_slovakia(project_root: Path, src: Path, country: dict, states: List[dict]) -> int:
    state_by_iso2 = {(s.get("iso2") or "").upper(): s for s in states if s.get("iso2")}
    rows = json.load(src.open(encoding="utf-8"))

    by_code: Dict[str, List[dict]] = {}
    for r in rows:
        psc_raw = (r.get("PSC") or "").strip()
        if not psc_raw:
            continue
        # Source format is "985 13"; SK regex accepts either form
        by_code.setdefault(psc_raw, []).append(r)

    records: List[dict] = []
    matched = 0
    for code in sorted(by_code):
        chosen = sorted(by_code[code], key=lambda x: (x.get("OBEC") or ""))[0]
        record = {
            "code": code,
            "country_id": int(country["id"]),
            "country_code": "SK",
        }
        kraj = (chosen.get("KRAJ") or "").strip().upper()
        state = state_by_iso2.get(kraj)
        if state is not None:
            record["state_id"] = int(state["id"])
            record["state_code"] = kraj
            matched += 1
        obec = (chosen.get("OBEC") or "").strip()
        if obec:
            record["locality_name"] = obec
        record["type"] = "full"
        record["source"] = "psc-json"
        records.append(record)

    target = project_root / "contributions/postcodes/SK.json"
    write_records(target, records)
    print(f"  SK: {len(records):,} records, {matched:,} ({matched*100//max(1,len(records))}%) with state")
    return len(records)


# ---------------------------------------------------------------------------
# Romania: alexionegit/coduripostaleRomaniaPS
# ---------------------------------------------------------------------------

# CSV "judet" UPPERCASE name -> CSC state.iso2 (built once at import time)
def build_ro_judet_map(states: List[dict]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for s in states:
        iso = s.get("iso2") or ""
        for name in (s.get("name"), s.get("native")):
            if name:
                key = ascii_fold(name).upper()
                out[key] = iso
    # Special case: CSV says "BUCURESTI SECTOR 1..6"; all 6 sectors map to "B"
    out["BUCURESTI"] = "B"
    return out


def import_romania(project_root: Path, src: Path, country: dict, states: List[dict]) -> int:
    judet_to_iso2 = build_ro_judet_map(states)
    state_by_iso2 = {s.get("iso2"): s for s in states if s.get("iso2")}

    by_code: Dict[str, List[dict]] = {}
    with src.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = (row.get("zipcode") or "").strip()
            if not code or not code.isdigit() or len(code) != 6:
                continue
            by_code.setdefault(code, []).append(row)

    records: List[dict] = []
    matched = 0
    for code in sorted(by_code):
        chosen = sorted(by_code[code], key=lambda x: (x.get("name") or "").upper())[0]
        record = {
            "code": code,
            "country_id": int(country["id"]),
            "country_code": "RO",
        }
        judet_raw = (chosen.get("judet") or "").strip().upper()
        # Strip "SECTOR N" suffix so all 6 Bucharest sectors map to "B"
        judet_lookup = re.sub(r"\s+SECTOR\s+\d+$", "", judet_raw, flags=re.I)
        iso = judet_to_iso2.get(ascii_fold(judet_lookup).upper())
        if iso and iso in state_by_iso2:
            state = state_by_iso2[iso]
            record["state_id"] = int(state["id"])
            record["state_code"] = iso
            matched += 1
        name = (chosen.get("name") or "").strip()
        if name:
            record["locality_name"] = name
        record["type"] = "full"
        record["source"] = "ro-coduri-postale"
        records.append(record)

    target = project_root / "contributions/postcodes/RO.json"
    write_records(target, records)
    print(f"  RO: {len(records):,} records, {matched:,} ({matched*100//max(1,len(records))}%) with state")
    return len(records)


# ---------------------------------------------------------------------------
# Slovenia: dlabs/postcode_si  (country-only — no source state info)
# ---------------------------------------------------------------------------

def import_slovenia(project_root: Path, src: Path, country: dict, states: List[dict]) -> int:
    by_code: Dict[str, List[dict]] = {}
    with src.open(encoding="utf-8", newline="") as f:
        # Headerless CSV: zip,locality,unused,country_name,lat,lng
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 6:
                continue
            code = (row[0] or "").strip()
            locality = (row[1] or "").strip()
            lat = (row[4] or "").strip()
            lng = (row[5] or "").strip()
            if not code or not code.isdigit() or len(code) != 4:
                continue
            by_code.setdefault(code, []).append({"locality": locality, "lat": lat, "lng": lng})

    records: List[dict] = []
    matched_coord = 0
    for code in sorted(by_code):
        chosen = sorted(by_code[code], key=lambda r: r["locality"].upper())[0]
        record = {
            "code": code,
            "country_id": int(country["id"]),
            "country_code": "SI",
        }
        if chosen["locality"]:
            record["locality_name"] = chosen["locality"]
        record["type"] = "full"
        lat_p = parse_coord(chosen["lat"])
        lng_p = parse_coord(chosen["lng"])
        if lat_p is not None and lng_p is not None:
            record["latitude"] = lat_p
            record["longitude"] = lng_p
            matched_coord += 1
        record["source"] = "postcode-si"
        records.append(record)

    target = project_root / "contributions/postcodes/SI.json"
    write_records(target, records)
    print(f"  SI: {len(records):,} records, country-only (no source state info), {matched_coord:,} with coords")
    return len(records)


# ---------------------------------------------------------------------------
# Common write logic
# ---------------------------------------------------------------------------

def write_records(target: Path, records: List[dict]) -> None:
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
        records = merged
    records.sort(key=lambda r: (r["code"], r.get("locality_name", "")))
    with target.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sk-input", default="/tmp/sk_obce.json")
    parser.add_argument("--ro-input", default="/tmp/ro_coduri.csv")
    parser.add_argument("--si-input", default="/tmp/si_codes.csv")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    countries = json.load((project_root / "contributions/countries/countries.json").open(encoding="utf-8"))
    all_states = json.load((project_root / "contributions/states/states.json").open(encoding="utf-8"))

    by_iso = {c["iso2"]: c for c in countries if c.get("iso2")}
    print("Batch import: SK + RO + SI")
    total = 0
    for iso, src_path, fn in [
        ("SK", args.sk_input, import_slovakia),
        ("RO", args.ro_input, import_romania),
        ("SI", args.si_input, import_slovenia),
    ]:
        country = by_iso.get(iso)
        if country is None:
            print(f"  {iso}: SKIP (not in countries.json)")
            continue
        src = Path(src_path)
        if not src.exists():
            print(f"  {iso}: SKIP (input not found: {src})")
            continue
        states = [s for s in all_states if s.get("country_id") == country["id"]]
        n = fn(project_root, src, country, states)
        total += n

    print(f"\nTotal: {total:,} records across 3 countries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
