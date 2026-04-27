#!/usr/bin/env python3
"""Remap French cities from region-level state_code to department-level state_code,
the FR equivalent of the Italian region->province remap shipped in #1395 (issue #1349).

Cities in contributions/cities/FR.json are currently parented to the 12 metropolitan
regions (ARA, IDF, NOR, PDL, NAQ, BRE, OCC, GES, CVL, BFC, HDF, PAC) plus the
Corsica collectivity (20R), even though contributions/states/states.json carries
metropolitan-department rows whose iso2 is the INSEE department code (01-95, 2A,
2B, 75C, 69M, ...). The mismatch makes endpoints like
GET /v1/countries/FR/states/03/cities return [] for Allier even though ~316
Allier communes exist in the data — they just sit under "ARA". Issue #1352.

Sources:
  - geo.api.gouv.fr communes dump (offline snapshot bundled at
    bin/scripts/fixes/data/geo-api-gouv-communes.json). Refetch with --refresh-geo.
    Each record: {nom, code (INSEE commune), codeDepartement, codeRegion,
                  centre.coordinates [lon,lat], population}.
  - contributions/states/states.json (canonical FR state list).
  - contributions/cities/FR.json (10,079 records, source of truth).

Mapping rules:
  1. Build a name index over the geo dump. For each city in a region-level state,
     resolve its INSEE commune via three-priority cascade:
       a. INSEE-by-name + region-aware match: if the city's current state_code is
          a metro region (ARA/IDF/...), prefer commune candidates whose codeRegion
          maps to that state_code. With one such candidate, take it. With multiple,
          tie-break by closest coordinate.
       b. INSEE-by-name only: if no candidate sits in the current region (the
          region itself is misclassified — e.g. "Apremont" listed under ARA but
          all upstream Apremonts are in BFC/PDL/etc.), pick the candidate whose
          coordinates are closest to ours, regardless of region.
       c. K-nearest-neighbour proximity vote (k=5) when the name produces no
          match at all. Distances >25 km are reported as unmapped.
  2. INSEE -> CSC state mapping: state.iso2 == codeDepartement except dept "75"
     -> "75C" (Paris collectivity). Dept 69 collapses to state "69" (Rhône);
     Métropole de Lyon (69M) cannot be inferred from codeDepartement and is
     left untouched as out-of-scope (none of our region-coded rows currently
     belong to 69M anyway, and 69M is not in our source set).
  3. Source set: state_code in {ARA, IDF, NOR, PDL, NAQ, BRE, OCC, GES, CVL,
     BFC, HDF, PAC, 20R}. All other rows are skipped (already at dept level,
     overseas, or out of scope).
  4. Idempotent: re-running produces zero changes once the source set is empty.

Outputs:
  - Rewrites contributions/cities/FR.json in place; only state_id and state_code
    are mutated. name, native, latitude, longitude, wikiDataId, translations and
    every other field are preserved verbatim.
  - Prints per-department remap summary plus unmapped sample.
  - Writes a structured JSON report to --report PATH for the fix-doc author.

Usage:
    python3 bin/scripts/fixes/france_cities_remap.py [--dry-run] [--report path.json]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
GEO_JSON = REPO_ROOT / "bin/scripts/fixes/data/geo-api-gouv-communes.json"
GEO_URL = (
    "https://geo.api.gouv.fr/communes"
    "?fields=nom,code,codeDepartement,codeRegion,centre,population&format=json"
)
STATES_JSON = REPO_ROOT / "contributions/states/states.json"
CITIES_JSON = REPO_ROOT / "contributions/cities/FR.json"

# State codes that hold cities still parented at region (or Corsica-collectivity)
# level. These are the rows we remap. Every other state_code is left alone.
SOURCE_STATE_CODES = {
    "ARA", "IDF", "NOR", "PDL", "NAQ", "BRE", "OCC",
    "GES", "CVL", "BFC", "HDF", "PAC", "20R",
}

# INSEE region code -> CSC state_code. Used to honour the "current region as
# preferred candidate" tie-break in priority (a). Mirrors the table in PR #1394.
REGION_TO_CSC = {
    "11": "IDF",  # Île-de-France
    "24": "CVL",  # Centre-Val de Loire
    "27": "BFC",  # Bourgogne-Franche-Comté
    "28": "NOR",  # Normandie
    "32": "HDF",  # Hauts-de-France
    "44": "GES",  # Grand-Est
    "52": "PDL",  # Pays-de-la-Loire
    "53": "BRE",  # Bretagne
    "75": "NAQ",  # Nouvelle-Aquitaine
    "76": "OCC",  # Occitanie
    "84": "ARA",  # Auvergne-Rhône-Alpes
    "93": "PAC",  # Provence-Alpes-Côte-d'Azur
    "94": "20R",  # Corse (collectivity-level, current convention for some rows)
}

# INSEE codeDepartement -> CSC state.iso2 override (only Paris differs).
DEPT_TO_CSC = {"75": "75C"}

# Maximum proximity-fallback distance in km. Cities further than this from any
# upstream commune are reported unmapped instead of guessed.
PROXIMITY_LIMIT_KM = 25.0
PROXIMITY_K = 5

# French ligatures that NFKD does not decompose.
_LIGATURE_MAP = str.maketrans({"œ": "oe", "Œ": "oe", "æ": "ae", "Æ": "ae", "ß": "ss"})

# Toponymic preposition variants ("lès" / "lez" / "les" all collide as "lez").
_TOPONYM_VARIANTS = [
    (re.compile(r"\bles\b"), "lez"),
    (re.compile(r"\bsur\b"), "sur"),
]


def normalise_name(name: str) -> str:
    """Return an accent/punctuation-insensitive comparison key.

    Mirrors the helper from PR #1394 so name-based matches between this script
    and the diff report are bit-identical.
    """
    if not name:
        return ""
    s = name.translate(_LIGATURE_MAP)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    for pattern, replacement in _TOPONYM_VARIANTS:
        s = pattern.sub(replacement, s)
    return re.sub(r"[^a-z]+", "", s)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two WGS84 points."""
    r = 6371.0088
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def safe_float(value) -> Optional[float]:
    """Parse a numeric string, tolerating None or blank."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_geo_if_missing(refresh: bool) -> None:
    """Download the geo.api.gouv.fr commune dump if it's missing or --refresh-geo is set."""
    if GEO_JSON.exists() and not refresh:
        return
    GEO_JSON.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading geo.api.gouv.fr communes -> {GEO_JSON} ...", file=sys.stderr)
    with urllib.request.urlopen(GEO_URL, timeout=120) as resp:
        payload = resp.read()
    GEO_JSON.write_bytes(payload)


def load_geo() -> List[dict]:
    """Read the bundled geo.api.gouv.fr commune dump."""
    return json.loads(GEO_JSON.read_text(encoding="utf-8"))


def build_commune_index(geo: List[dict]) -> Dict[str, List[dict]]:
    """Index communes by normalised name. Each entry stores INSEE, dept, region,
    coordinates and population for downstream tie-breaking and reporting.
    """
    index: Dict[str, List[dict]] = defaultdict(list)
    for rec in geo:
        nom = rec.get("nom") or ""
        key = normalise_name(nom)
        if not key:
            continue
        centre = rec.get("centre") or {}
        coords = centre.get("coordinates") if isinstance(centre, dict) else None
        if coords and len(coords) == 2:
            lon, lat = coords
        else:
            lat = lon = None
        index[key].append({
            "nom": nom,
            "insee": rec.get("code"),
            "dept": rec.get("codeDepartement"),
            "region": rec.get("codeRegion"),
            "lat": lat,
            "lon": lon,
            "population": rec.get("population"),
        })
    return index


def build_state_lookup(states: List[dict]) -> Dict[str, dict]:
    """Build {state.iso2: state_record} for FR states."""
    return {
        s["iso2"]: s
        for s in states
        if s.get("country_code") == "FR" and s.get("iso2")
    }


def resolve_state_for_dept(
    dept: str, fr_states: Dict[str, dict]
) -> Optional[Tuple[int, str]]:
    """Map an INSEE codeDepartement to (state_id, state_code). Honours the
    DEPT_TO_CSC override (only Paris). Returns None for unknown depts (overseas
    where no metro state row exists, etc.).
    """
    if not dept:
        return None
    target = DEPT_TO_CSC.get(dept, dept)
    state = fr_states.get(target)
    if state is None:
        return None
    return state["id"], state["iso2"]


def pick_by_distance(
    candidates: List[dict], lat: Optional[float], lon: Optional[float]
) -> Tuple[Optional[dict], Optional[float]]:
    """Return the candidate closest to (lat, lon) and the distance, or
    (candidates[0], None) when coordinates are missing or all candidates lack
    coordinates. Ties broken by INSEE for stable ordering.
    """
    if lat is None or lon is None:
        return candidates[0], None
    best: Optional[dict] = None
    best_dist = float("inf")
    for cand in candidates:
        if cand["lat"] is None or cand["lon"] is None:
            continue
        d = haversine_km(lat, lon, cand["lat"], cand["lon"])
        if d < best_dist or (d == best_dist and best and cand["insee"] < best["insee"]):
            best = cand
            best_dist = d
    if best is None:
        return candidates[0], None
    return best, best_dist


def candidate_for_city(
    city: dict,
    commune_index: Dict[str, List[dict]],
) -> Tuple[Optional[dict], str, Optional[float]]:
    """Pick the best upstream commune for a city.

    Returns (record, reason, distance_km). reason is one of:
        'name_unique'       single name match anywhere -> direct.
        'name_region'       multiple matches, current region holds exactly one.
        'name_region_multi' multiple matches in current region -> closest by coord.
        'name_other_region' name match exists but none in current region -> picked
                            globally closest, but only when within PROXIMITY_LIMIT_KM
                            (otherwise we treat it as no-match so the k-NN pass can
                            pick a local commune instead of a far-away namesake).
        'no_match'          no name match (or all matches are too far) -> caller
                            should fall back to k-NN.
    """
    keys = {normalise_name(city.get("name") or "")}
    keys.discard("")
    candidates: List[dict] = []
    seen: set = set()
    for key in keys:
        for rec in commune_index.get(key, []):
            ident = rec["insee"]
            if ident in seen:
                continue
            seen.add(ident)
            candidates.append(rec)

    if not candidates:
        return None, "no_match", None

    lat = safe_float(city.get("latitude"))
    lon = safe_float(city.get("longitude"))
    current_csc = city.get("state_code")

    if len(candidates) == 1:
        cand = candidates[0]
        d = None
        if lat is not None and lon is not None and cand["lat"] is not None:
            d = haversine_km(lat, lon, cand["lat"], cand["lon"])
        return cand, "name_unique", d

    in_region = [
        c for c in candidates
        if REGION_TO_CSC.get(c["region"] or "") == current_csc
    ]
    if len(in_region) == 1:
        cand = in_region[0]
        d = None
        if lat is not None and lon is not None and cand["lat"] is not None:
            d = haversine_km(lat, lon, cand["lat"], cand["lon"])
        return cand, "name_region", d
    if len(in_region) > 1:
        cand, d = pick_by_distance(in_region, lat, lon)
        return cand, "name_region_multi", d

    cand, d = pick_by_distance(candidates, lat, lon)
    if d is None or d > PROXIMITY_LIMIT_KM:
        # All namesakes are far away — current state was misclassified at a coarse
        # level (e.g. "Saint-Lambert" listed under PAC has no commune in Provence).
        # Trust k-NN proximity for these rather than a 500km global-closest match.
        return None, "no_match", None
    return cand, "name_other_region", d


def proximity_fallback(
    city: dict, geo_with_coords: List[dict]
) -> Tuple[Optional[dict], str, Optional[float]]:
    """K-NN majority vote across upstream communes for cities with no name match.

    Mirrors the Italy script's proximity_knn pass: keep the 5 closest communes,
    weight by inverse distance, and let the dept with highest weighted vote win.
    Distances >PROXIMITY_LIMIT_KM are rejected as unmapped (caller marks them).
    """
    lat = safe_float(city.get("latitude"))
    lon = safe_float(city.get("longitude"))
    if lat is None or lon is None or not geo_with_coords:
        return None, "no_match_no_coords", None

    scored = sorted(
        ((haversine_km(lat, lon, g["lat"], g["lon"]), g) for g in geo_with_coords),
        key=lambda x: x[0],
    )[:PROXIMITY_K]
    if not scored:
        return None, "no_match_no_coords", None
    nearest_dist = scored[0][0]
    if nearest_dist > PROXIMITY_LIMIT_KM:
        return None, f"too_far:{nearest_dist:.1f}km", nearest_dist

    votes: Counter = Counter()
    rep: Dict[str, dict] = {}
    for d, cand in scored:
        weight = 1.0 / max(d, 0.1)
        votes[cand["dept"]] += weight
        rep.setdefault(cand["dept"], cand)
    best_dept = votes.most_common(1)[0][0]
    return rep[best_dept], f"proximity_knn:{nearest_dist:.1f}km", nearest_dist


def remap_cities(
    cities: List[dict],
    commune_index: Dict[str, List[dict]],
    geo: List[dict],
    fr_states: Dict[str, dict],
) -> dict:
    """Two-pass remap. Mutates cities in place; returns a structured report."""
    geo_with_coords = [g for g in geo if g["lat"] is not None and g["lon"] is not None]

    counters: Counter = Counter()
    by_target: Counter = Counter()
    by_source: Counter = Counter()
    annotations: List[dict] = []
    unmapped: List[dict] = []

    for city in cities:
        current_code = city.get("state_code")
        if current_code not in SOURCE_STATE_CODES:
            counters["skipped_out_of_scope"] += 1
            continue

        record, reason, dist = candidate_for_city(city, commune_index)
        if record is None:
            record, reason, dist = proximity_fallback(city, geo_with_coords)

        if record is None:
            counters["unmapped"] += 1
            unmapped.append({
                "id": city.get("id"),
                "name": city.get("name"),
                "current_state_code": current_code,
                "reason": reason,
            })
            continue

        target = resolve_state_for_dept(record["dept"], fr_states)
        if target is None:
            counters["unmapped"] += 1
            unmapped.append({
                "id": city.get("id"),
                "name": city.get("name"),
                "current_state_code": current_code,
                "reason": f"unknown_dept:{record['dept']}",
            })
            continue

        target_id, target_code = target
        counters[reason] += 1
        by_source[current_code] += 1

        if city.get("state_id") != target_id or city.get("state_code") != target_code:
            annotations.append({
                "id": city.get("id"),
                "name": city.get("name"),
                "from_state_id": city.get("state_id"),
                "from_state_code": current_code,
                "to_state_id": target_id,
                "to_state_code": target_code,
                "via": reason,
                "insee": record["insee"],
                "distance_km": round(dist, 2) if dist is not None else None,
            })
            city["state_id"] = target_id
            city["state_code"] = target_code
            counters["changed"] += 1
        else:
            counters["unchanged"] += 1
        by_target[target_code] += 1

    return {
        "totals": {
            "input": len(cities),
            "in_scope": sum(by_source.values()) + counters["unmapped"],
            "skipped_out_of_scope": counters["skipped_out_of_scope"],
            "changed": counters["changed"],
            "unchanged": counters["unchanged"],
            "unmapped": counters["unmapped"],
            "by_resolution": {
                "name_unique": counters.get("name_unique", 0),
                "name_region": counters.get("name_region", 0),
                "name_region_multi": counters.get("name_region_multi", 0),
                "name_other_region": counters.get("name_other_region", 0),
                "proximity_knn": sum(
                    v for k, v in counters.items() if k.startswith("proximity_knn:")
                ),
            },
        },
        "by_source_region": dict(sorted(by_source.items(), key=lambda x: -x[1])),
        "by_target_dept": dict(sorted(by_target.items(), key=lambda x: -x[1])),
        "unmapped": unmapped,
        "annotations_sample": annotations[:50],
    }


def write_cities_normalised(cities: List[dict]) -> None:
    """Write FR.json in repo's standard JSON shape (2-space indent, no trailing newline)."""
    text = json.dumps(cities, ensure_ascii=False, indent=2)
    CITIES_JSON.write_text(text, encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report without writing FR.json.",
    )
    parser.add_argument(
        "--refresh-geo",
        action="store_true",
        help="Re-download the geo.api.gouv.fr commune dump before running.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write the full structured report as JSON to this path.",
    )
    args = parser.parse_args(argv)

    fetch_geo_if_missing(args.refresh_geo)

    states = json.loads(STATES_JSON.read_text(encoding="utf-8"))
    fr_states = build_state_lookup(states)
    geo = load_geo()
    commune_index = build_commune_index(geo)
    cities = json.loads(CITIES_JSON.read_text(encoding="utf-8"))

    geo_recs = [
        {
            "nom": rec["nom"],
            "insee": rec["insee"],
            "dept": rec["dept"],
            "region": rec["region"],
            "lat": rec["lat"],
            "lon": rec["lon"],
            "population": rec["population"],
        }
        for bucket in commune_index.values()
        for rec in bucket
    ]

    report = remap_cities(cities, commune_index, geo_recs, fr_states)

    print("=" * 70)
    print("France city remap (issue #1352 PR-E) report")
    print("=" * 70)
    for k, v in report["totals"].items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk:24} {vv}")
        else:
            print(f"  {k:32} {v}")
    print()
    print("By source region (pre-remap):")
    for code, count in report["by_source_region"].items():
        print(f"  {code:6} {count:5}")
    print()
    print(f"By target department (post-remap, top 25 of {len(report['by_target_dept'])}):")
    for code, count in list(report["by_target_dept"].items())[:25]:
        state = next(
            (s for s in states if s.get("country_code") == "FR" and s["iso2"] == code),
            None,
        )
        label = state["name"] if state else "?"
        print(f"  {code:6} {count:5}  {label}")
    print()
    print(f"Unmapped: {len(report['unmapped'])}")
    for entry in report["unmapped"][:25]:
        print(
            f"  id={entry['id']!s:7}  {entry['name']!s:40}  "
            f"from={entry['current_state_code']!s:6} reason={entry['reason']}"
        )

    if args.report:
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nFull report written to {args.report}")

    if args.dry_run:
        print("\n--dry-run: FR.json NOT modified.")
        return 0

    write_cities_normalised(cities)
    print(f"\nWrote {len(cities)} cities to {CITIES_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
