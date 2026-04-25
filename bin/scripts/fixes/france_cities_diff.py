#!/usr/bin/env python3
"""france_cities_diff.py

Diff contributions/cities/FR.json against the canonical commune list from
data.gouv.fr (INSEE) and produce a conservative merge proposal.

Inputs (all required):
  --upstream PATH     villes.min.json  (https://github.com/user-attachments/files/25721910/villes.min.json)
                      Schema: [{nom, departement, region, code}, ...]   (no coords/population)
  --geo PATH          geo.api.gouv.fr communes dump fetched with:
                        https://geo.api.gouv.fr/communes?fields=nom,code,
                          codeDepartement,codeRegion,centre,population&format=json
                      Used to enrich missing communes with coordinates and population.
  --our PATH          contributions/cities/FR.json (default)
  --states PATH       contributions/states/states.json (default)

Outputs:
  --report-out PATH   JSON report listing missing / extra / cross-region matches.
  --merge-out  PATH   JSON list of proposed new city records (NOT applied unless --apply).

Modes:
  default             dry-run; writes report + merge proposal, leaves FR.json unchanged.
  --apply             rewrite contributions/cities/FR.json with the merge applied
                      (appends new records, preserves all existing IDs and ordering).

Scope: METROPOLITAN FRANCE ONLY. Overseas departments (971-989) are out of scope
for this script (PR-D in the #1352 plan handles them).

This script never reaches the network; both upstream and geo files must be
downloaded ahead of time.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# ---- Static reference data ------------------------------------------------

# INSEE region codes that are metropolitan (incl. Corsica = 94)
METRO_REGIONS = {"11", "24", "27", "28", "32", "44", "52", "53", "75", "76", "84", "93", "94"}

# INSEE region code -> CSC state iso2 (region-level state)
# Corsica (94) intentionally absent: communes use their dept code (2A/2B) per
# the existing FR.json convention (337 of 361 Corsican rows are dept-coded).
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
}

# Departments that the existing FR.json stores at department-level rather than
# region-level (i.e. cities in dept 55 have state_code="55", not "GES").
# Discovered empirically; all new records in these depts must follow suit.
DEPT_OVERRIDES = {"2A", "2B", "48", "52", "55"}

# CSC state codes that count as "metropolitan" for the purposes of cross-region
# fallback and "extra"-detection. Includes 20R (Corse collectivity) which holds
# a small number of historical Corsican cities that should match upstream 2A/2B.
METRO_CSC_CODES = set(REGION_TO_CSC.values()) | DEPT_OVERRIDES | {"20R"}

# France metropolitan bounding box (matches .github/data/country-bounds.json).
FR_BOUNDS = {"minLat": 41.36, "maxLat": 51.09, "minLon": -5.14, "maxLon": 9.56}

# Coordinate divergence threshold (km) for the coord-mismatch report.
COORD_MISMATCH_KM = 1.0

# ---- Helpers --------------------------------------------------------------


_LIGATURE_MAP = str.maketrans({"œ": "oe", "Œ": "oe", "æ": "ae", "Æ": "ae", "ß": "ss"})

# Common French toponymic prepositions that vary across sources. Map them to a
# canonical token so e.g. "Saint-Christol-lez-Alès" and "Saint-Christol-lès-Alès"
# collide as the same key.
_TOPONYM_VARIANTS = [
    (re.compile(r"\bles\b"), "lez"),
    (re.compile(r"\bsur\b"), "sur"),
]


def normalise_name(name: str) -> str:
    """Return an accent/punctuation-insensitive comparison key for a commune name.

    Handles:
      - Latin accents (NFKD + ASCII fold).
      - oe/ae ligatures (manual map; NFKD doesn't decompose them).
      - "lez"/"lès" preposition variation common in French place names.
    """
    s = name.translate(_LIGATURE_MAP)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()
    for pattern, replacement in _TOPONYM_VARIANTS:
        s = pattern.sub(replacement, s)
    return re.sub(r"[^a-z]+", "", s)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_json(path: Path):
    """Read a JSON file or exit with a useful error."""
    if not path.exists():
        sys.exit(f"ERROR: input file not found: {path}")
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: invalid JSON in {path}: {exc}")


def build_csc_state_lookup(states: list[dict]) -> dict[str, dict]:
    """Build {state_iso2: state_record} for FR states only."""
    return {s["iso2"]: s for s in states if s.get("country_code") == "FR" and s.get("iso2")}


def determine_target_state(rec: dict) -> str | None:
    """Map an upstream commune to the CSC state_code where new records should land.

    Returns None for non-metropolitan or unmapped (caller should skip).
    """
    dept = rec["departement"]
    region = rec["region"]
    if dept in DEPT_OVERRIDES:
        return dept
    if region == "94":  # Corsica — should already be DEPT_OVERRIDE; defensive
        return dept if dept in DEPT_OVERRIDES else None
    return REGION_TO_CSC.get(region)


# ---- Diff -----------------------------------------------------------------


def run_diff(upstream: list[dict], geo: list[dict], ours: list[dict]) -> dict:
    """Compute missing / extra / cross-region / coord-mismatch records.

    Match key: (target_state_code, normalise_name(name)).
    Falls back to scanning *all* metropolitan CSC state codes (incl. 20R and
    dept-coded depts) for the same name; cross-state hits are flagged as
    cross-region matches, which signal possible misclassifications.
    """
    geo_by_code = {g["code"]: g for g in geo}

    # Build CSC index by (state_code, norm_name)
    ours_index: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for c in ours:
        ours_index[(c["state_code"], normalise_name(c["name"]))].append(c)

    # Multiplicity index for unambiguous coord-mismatch reporting:
    # how many upstream metro communes share each normalised name?
    upstream_name_count: dict[str, int] = defaultdict(int)
    for r in upstream:
        if r["region"] in METRO_REGIONS:
            upstream_name_count[normalise_name(r["nom"])] += 1

    # Set of (state_code, norm_name) that we've matched, used to compute "extra"
    matched_keys: set[tuple[str, str]] = set()

    # Filter upstream to metropolitan
    metro_upstream = [r for r in upstream if r["region"] in METRO_REGIONS]

    missing: list[dict] = []
    cross_region_matches: list[dict] = []  # in CSC but under a different state than expected
    coord_mismatches: list[dict] = []
    coord_mismatches_skipped_homonym = 0
    matched_count = 0

    for rec in metro_upstream:
        name_n = normalise_name(rec["nom"])
        primary = determine_target_state(rec)

        # Try primary state
        match = None
        match_state = None
        if primary and (primary, name_n) in ours_index:
            match = ours_index[(primary, name_n)][0]
            match_state = primary

        # Fallback: another metropolitan CSC state code
        if match is None:
            for sc in METRO_CSC_CODES:
                if sc == primary:
                    continue
                if (sc, name_n) in ours_index:
                    match = ours_index[(sc, name_n)][0]
                    match_state = sc
                    cross_region_matches.append({
                        "insee": rec["code"],
                        "nom": rec["nom"],
                        "expected_state": primary,
                        "actual_state": sc,
                        "csc_id": match["id"],
                    })
                    break

        if match is None:
            geo_rec = geo_by_code.get(rec["code"]) or {}
            missing.append({
                "insee": rec["code"],
                "nom": rec["nom"],
                "departement": rec["departement"],
                "region": rec["region"],
                "target_state": primary,
                "centre": geo_rec.get("centre"),
                "population": geo_rec.get("population"),
            })
            continue

        matched_count += 1
        matched_keys.add((match_state, name_n))

        # Coord mismatch — only meaningful when the commune name is unique
        # in the upstream metro list. Otherwise the match could be a homonym
        # in a different department and the distance is meaningless.
        if upstream_name_count[name_n] != 1:
            coord_mismatches_skipped_homonym += 1
            continue
        geo_rec = geo_by_code.get(rec["code"])
        if not (geo_rec and geo_rec.get("centre")):
            continue
        up_lon, up_lat = geo_rec["centre"]["coordinates"]
        try:
            our_lat = float(match["latitude"])
            our_lon = float(match["longitude"])
        except (TypeError, ValueError):
            continue
        dist = haversine_km(up_lat, up_lon, our_lat, our_lon)
        if dist > COORD_MISMATCH_KM:
            coord_mismatches.append({
                "insee": rec["code"],
                "nom": rec["nom"],
                "csc_id": match["id"],
                "csc_state": match_state,
                "ours": [our_lat, our_lon],
                "upstream": [up_lat, up_lon],
                "distance_km": round(dist, 2),
            })

    # "Extra in our data": records present in CSC but not in upstream metro list,
    # filtered to records whose state_code is a metropolitan CSC code so that
    # overseas-territory cities aren't reported as extras here.
    extra = []
    for c in ours:
        if c.get("state_code") not in METRO_CSC_CODES:
            continue
        key = (c["state_code"], normalise_name(c["name"]))
        if key in matched_keys:
            continue
        extra.append({
            "csc_id": c["id"],
            "name": c["name"],
            "state_code": c["state_code"],
            "latitude": c["latitude"],
            "longitude": c["longitude"],
        })

    return {
        "stats": {
            "upstream_metro_total": len(metro_upstream),
            "ours_total": len(ours),
            "matched": matched_count,
            "missing": len(missing),
            "extra": len(extra),
            "cross_region_matches": len(cross_region_matches),
            "coord_mismatches": len(coord_mismatches),
            "coord_mismatches_skipped_homonym": coord_mismatches_skipped_homonym,
        },
        "missing": missing,
        "extra": extra,
        "cross_region_matches": cross_region_matches,
        "coord_mismatches": coord_mismatches,
    }


# ---- Merge proposal -------------------------------------------------------


def build_merge_proposal(missing: list[dict], csc_states: dict[str, dict],
                         pop_threshold: int) -> tuple[list[dict], list[dict]]:
    """Filter missing entries to those safe to auto-add and shape them into
    CSC city records.

    Returns (proposed_records, deferred_records).
    Deferred = entries we *won't* auto-apply (no coords, low population, or
    target state unmapped).
    """
    proposed: list[dict] = []
    deferred: list[dict] = []
    for m in missing:
        target = m["target_state"]
        state = csc_states.get(target) if target else None
        centre = m.get("centre") or {}
        pop = m.get("population")
        coords = centre.get("coordinates") if isinstance(centre, dict) else None
        skip_reasons = []
        if not state:
            skip_reasons.append("unmapped_state")
        if not coords:
            skip_reasons.append("no_coords")
        if pop is None:
            skip_reasons.append("no_population")
        elif pop < pop_threshold:
            skip_reasons.append(f"pop<{pop_threshold}")
        if not coords or not state:
            deferred.append({**m, "skip_reasons": skip_reasons})
            continue

        lon, lat = coords
        # Defensive bounds check (Corsica & metro mainland)
        if not (FR_BOUNDS["minLat"] <= lat <= FR_BOUNDS["maxLat"]
                and FR_BOUNDS["minLon"] <= lon <= FR_BOUNDS["maxLon"]):
            deferred.append({**m, "skip_reasons": skip_reasons + ["out_of_bounds"]})
            continue

        if pop is None or pop < pop_threshold:
            deferred.append({**m, "skip_reasons": skip_reasons})
            continue

        record = {
            "name": m["nom"],
            "state_id": state["id"],
            "state_code": state["iso2"],
            "country_id": 75,
            "country_code": "FR",
            "type": "city",
            "level": None,
            "parent_id": None,
            "latitude": f"{lat:.8f}",
            "longitude": f"{lon:.8f}",
            "native": m["nom"],
            "population": pop,
            "timezone": "Europe/Paris",
        }
        proposed.append(record)
    # Stable sort: by name (case-insensitive) so the diff is reviewable
    proposed.sort(key=lambda r: r["name"].lower())
    deferred.sort(key=lambda d: d["nom"].lower())
    return proposed, deferred


# ---- Apply ----------------------------------------------------------------


def apply_merge(our_path: Path, ours: list[dict], proposed: list[dict]) -> int:
    """Append new records to FR.json without disturbing existing ones."""
    # Defensive: drop any record whose key collides with an existing one
    existing_keys = {(c["state_code"], normalise_name(c["name"])) for c in ours}
    safe = [r for r in proposed if (r["state_code"], normalise_name(r["name"])) not in existing_keys]
    if len(safe) != len(proposed):
        print(f"WARNING: dropped {len(proposed) - len(safe)} proposed records "
              f"that collided with existing keys")
    merged = ours + safe
    with our_path.open("w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return len(safe)


# ---- Main -----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--upstream", required=True, type=Path,
                        help="path to villes.min.json")
    parser.add_argument("--geo", required=True, type=Path,
                        help="path to geo.api.gouv.fr communes dump")
    parser.add_argument("--our", type=Path,
                        default=repo_root / "contributions" / "cities" / "FR.json",
                        help="path to FR.json (default: repo's contributions/cities/FR.json)")
    parser.add_argument("--states", type=Path,
                        default=repo_root / "contributions" / "states" / "states.json",
                        help="path to states.json")
    parser.add_argument("--report-out", type=Path,
                        default=repo_root / "bin" / "scripts" / "fixes"
                        / "france_cities_diff.report.json",
                        help="where to write the diff report")
    parser.add_argument("--merge-out", type=Path,
                        default=repo_root / "bin" / "scripts" / "fixes"
                        / "france_cities_diff.merge.json",
                        help="where to write the merge proposal (always written)")
    parser.add_argument("--deferred-out", type=Path,
                        default=repo_root / "bin" / "scripts" / "fixes"
                        / "france_cities_diff.deferred.json",
                        help="where to write deferred (skipped) candidates for review")
    parser.add_argument("--pop-threshold", type=int, default=2000,
                        help="minimum population to auto-include in the merge "
                             "(conservative default keeps PR scope reviewable)")
    parser.add_argument("--apply", action="store_true",
                        help="rewrite FR.json with the merge applied")
    args = parser.parse_args(argv)

    upstream = load_json(args.upstream)
    geo = load_json(args.geo)
    ours = load_json(args.our)
    states = load_json(args.states)

    if not isinstance(upstream, list) or not isinstance(geo, list) \
            or not isinstance(ours, list) or not isinstance(states, list):
        sys.exit("ERROR: all four input files must be JSON arrays.")

    csc_states = build_csc_state_lookup(states)

    diff = run_diff(upstream, geo, ours)
    proposed, deferred = build_merge_proposal(
        diff["missing"], csc_states, args.pop_threshold)

    # Write reports
    args.report_out.write_text(json.dumps({
        "stats": diff["stats"],
        "pop_threshold": args.pop_threshold,
        "proposed_count": len(proposed),
        "deferred_count": len(deferred),
        "samples": {
            "missing_top_by_population": sorted(
                [m for m in diff["missing"] if m.get("population") is not None],
                key=lambda x: -x["population"],
            )[:50],
            "cross_region_matches": diff["cross_region_matches"][:50],
            "coord_mismatches_top": sorted(
                diff["coord_mismatches"], key=lambda x: -x["distance_km"]
            )[:50],
            "extra_sample": diff["extra"][:30],
        },
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    args.merge_out.write_text(
        json.dumps(proposed, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")
    args.deferred_out.write_text(
        json.dumps(deferred, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

    s = diff["stats"]
    print(f"upstream metro total : {s['upstream_metro_total']:,}")
    print(f"ours total           : {s['ours_total']:,}")
    print(f"matched              : {s['matched']:,}")
    print(f"missing              : {s['missing']:,}")
    print(f"extra (in CSC only)  : {s['extra']:,}")
    print(f"cross-region matches : {s['cross_region_matches']:,}  (flagged for PR-B)")
    print(f"coord mismatches >{COORD_MISMATCH_KM}km: {s['coord_mismatches']:,}  "
          f"({s['coord_mismatches_skipped_homonym']:,} ambiguous homonyms skipped)")
    print(f"merge proposal       : {len(proposed):,} records (pop ≥ {args.pop_threshold})")
    print(f"deferred (skipped)   : {len(deferred):,} records")
    print(f"report  -> {args.report_out}")
    print(f"merge   -> {args.merge_out}")
    print(f"deferred-> {args.deferred_out}")

    if args.apply:
        added = apply_merge(args.our, ours, proposed)
        print(f"\nAPPLIED: appended {added:,} records to {args.our}")
    else:
        print("\nDry run — re-run with --apply to write FR.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
