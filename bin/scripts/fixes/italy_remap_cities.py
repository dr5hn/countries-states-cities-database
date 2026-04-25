#!/usr/bin/env python3
"""Remap Italian cities to their correct metropolitan-city / province / free-consortium
state, replacing the legacy region parenthood reported in issue #1349.

Sources:
  - ISTAT "Elenco dei comuni italiani" (semicolon-separated CSV, ISO-8859-1 / Latin-1).
    Bundled at bin/scripts/fixes/data/istat-elenco-comuni-italiani.csv.
    Re-fetch with --refresh-istat to grab the latest revision from istat.it.
  - contributions/states/states.json (canonical state list, 126 IT entities).
  - contributions/cities/IT.json (9947 city records to be remapped).

Mapping rules:
  1. ISTAT lists every comune with its Sigla automobilistica (2-letter province code).
     This sigla matches our state.iso2 for province-level entities (metro cities,
     provinces, free consortia, autonomous provinces, decentralised regional entities).
  2. Sigla "AO" has no province-level entity in our DB; cities map up to the
     autonomous region "Aosta Valley" (id=1716, iso2="23").
  3. For comuni with multiple namesakes across provinces, region-aware tie-breaking
     uses the city's pre-existing state_id (which is its current region).
  4. Cities whose name does not match any ISTAT comune fall back to coordinate-based
     nearest-neighbour inheritance from the closest name-matched city. Distance is
     bounded so far-flung records become "unmapped" rather than mis-assigned.

Output:
  - Rewrites contributions/cities/IT.json in place (state_id and state_code only).
  - Prints a per-sigla remap summary plus unmapped / possible-duplicate listings.
  - Optionally writes a JSON report to --report PATH for the fix-doc author.

Usage:
    python3 bin/scripts/fixes/italy_remap_cities.py [--dry-run] [--report path.json]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
import unicodedata
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
ISTAT_CSV = REPO_ROOT / "bin/scripts/fixes/data/istat-elenco-comuni-italiani.csv"
ISTAT_URL = "https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv"
STATES_JSON = REPO_ROOT / "contributions/states/states.json"
CITIES_JSON = REPO_ROOT / "contributions/cities/IT.json"

# Sigle that have no province-level state — comuni fall back to the autonomous region.
SIGLA_FALLBACK = {
    "AO": (1716, "23"),  # Valle d'Aosta -> autonomous region "Aosta Valley"
}

# English-only city names that map to a single Italian comune.  Without these
# aliases, proximity has to guess and frequently picks a neighbouring province
# (e.g. "Venice" in our data has no ISTAT-name match, so its frazioni Mestre /
# Giudecca / Campalto used to snap to Treviso via nearest-neighbour).
ENGLISH_TO_ITALIAN_ALIASES: Dict[str, str] = {
    "venice": "venezia",
    "florence": "firenze",
    "naples": "napoli",
    "turin": "torino",
    "milan": "milano",
    "genoa": "genova",
    "rome": "roma",
    "padua": "padova",
    "mantua": "mantova",
    "syracuse": "siracusa",
}

# Maximum proximity-fallback distance in km. Cities further than this from any
# name-matched comune are reported as unmapped instead of guessed.
PROXIMITY_LIMIT_KM = 25.0

# Number of nearest comuni to inspect during the proximity pass — a majority
# vote across the cluster is more robust at province borders than picking the
# single nearest neighbour (which mis-maps frazioni near a border, e.g. Mestre
# ending up in Treviso because Mogliano Veneto sits 3km closer than Venice).
PROXIMITY_K = 5


def normalise_name(value: str) -> str:
    """Fold an Italian comune name to a canonical comparison key.

    Lowercases, strips diacritics, normalises apostrophe variants and whitespace,
    and removes punctuation other than apostrophes and hyphens.
    """
    if not value:
        return ""
    text = unicodedata.normalize("NFD", value)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower()
    text = re.sub(r"[’‘`´]", "'", text)
    text = re.sub(r"[^a-z0-9' \-/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def expand_keys(value: str) -> List[str]:
    """Return all comparison keys derived from a name, including bilingual splits.

    ISTAT bilingual comuni use "Italian/AltLang" (e.g. "Bolzano/Bozen"); we register
    the joined form, each side, and the apostrophe-elided "Sant'X" -> "sant x" form.
    """
    base = normalise_name(value)
    if not base:
        return []
    keys = {base}
    if "/" in base:
        for part in base.split("/"):
            part = part.strip()
            if part:
                keys.add(part)
    keys.add(base.replace("'", " ").replace("  ", " ").strip())
    keys.add(base.replace("'", ""))
    return [k for k in keys if k]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres between two WGS84 points."""
    R = 6371.0088
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def safe_float(value) -> Optional[float]:
    """Parse a numeric string from JSON, tolerating None / blank."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_istat_if_missing(refresh: bool) -> None:
    """Download the ISTAT CSV if it's missing or --refresh-istat is set."""
    if ISTAT_CSV.exists() and not refresh:
        return
    ISTAT_CSV.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading ISTAT comune list -> {ISTAT_CSV} ...", file=sys.stderr)
    urllib.request.urlretrieve(ISTAT_URL, ISTAT_CSV)


def load_istat() -> Tuple[Dict[str, List[dict]], Dict[str, List[dict]], Dict[str, str]]:
    """Parse the ISTAT CSV.

    Returns:
        comune_index: normalised-name key -> list of records, populated from the
            primary Italian / alternative-language / full denominations.
        conjunction_index: secondary index keyed by each side of " e " / " ed "
            conjunctions (e.g. "Lampedusa e Linosa" produces "lampedusa" and
            "linosa"). Only consulted when the primary index misses, since
            "Massa" exists as its own comune as well as inside "Massa e Cozzile".
        sigla_to_region: sigla -> ISTAT region name (used for region tie-break).
    """
    comune_index: Dict[str, List[dict]] = defaultdict(list)
    conjunction_index: Dict[str, List[dict]] = defaultdict(list)
    sigla_to_region: Dict[str, str] = {}

    with ISTAT_CSV.open("r", encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        for row in reader:
            sigla = row["Sigla automobilistica"].strip()
            ita = row["Denominazione in italiano"].strip()
            alt = row["Denominazione altra lingua"].strip()
            full = row["Denominazione (Italiana e straniera)"].strip()
            region = row["Denominazione Regione"].strip()
            ut_name = row[
                "Denominazione dell'Unità territoriale sovracomunale \n(valida a fini statistici)"
            ].strip()
            tip = row["Tipologia di Unità territoriale sovracomunale "].strip()
            cat = row["Codice Catastale del comune"].strip()

            if not sigla:
                continue
            sigla_to_region[sigla] = region

            record = {
                "sigla": sigla,
                "italian_name": ita,
                "alt_name": alt,
                "full_name": full,
                "region_it": region,
                "ut_name": ut_name,
                "tipologia": tip,
                "codice_catastale": cat,
            }

            keys = set()
            for source in (ita, alt, full):
                keys.update(expand_keys(source))
            for key in keys:
                comune_index[key].append(record)

            for source in (ita, alt, full):
                norm = normalise_name(source)
                for sep in (" e ", " ed "):
                    if sep in f" {norm} ":
                        for part in norm.split(sep):
                            part = part.strip()
                            if part and len(part) >= 4:
                                conjunction_index[part].append(record)

    return comune_index, conjunction_index, sigla_to_region


def build_state_lookups(
    states: List[dict],
) -> Tuple[Dict[str, dict], Dict[int, dict], Dict[str, int], Dict[int, int]]:
    """Build IT-state lookups by iso2, by id, by region name (Italian), and a
    state_id -> region_id walk-up (province/metro -> parent region)."""
    iso2_to_state: Dict[str, dict] = {}
    id_to_state: Dict[int, dict] = {}
    region_name_to_id: Dict[str, int] = {}

    # ISTAT region name -> our state name (region or autonomous region).
    region_name_pairs = {
        "Piemonte": "Piedmont",
        "Valle d'Aosta/Vallée d'Aoste": "Aosta Valley",
        "Lombardia": "Lombardy",
        "Trentino-Alto Adige/Südtirol": "Trentino-South Tyrol",
        "Veneto": "Veneto",
        "Friuli-Venezia Giulia": "Friuli–Venezia Giulia",
        "Liguria": "Liguria",
        "Emilia-Romagna": "Emilia-Romagna",
        "Toscana": "Tuscany",
        "Umbria": "Umbria",
        "Marche": "Marche",
        "Lazio": "Lazio",
        "Abruzzo": "Abruzzo",
        "Molise": "Molise",
        "Campania": "Campania",
        "Puglia": "Apulia",
        "Basilicata": "Basilicata",
        "Calabria": "Calabria",
        "Sicilia": "Sicily",
        "Sardegna": "Sardinia",
    }
    name_to_state: Dict[str, dict] = {}

    for state in states:
        if state.get("country_code") != "IT":
            continue
        id_to_state[state["id"]] = state
        if state["type"] in ("region", "autonomous region"):
            name_to_state[state["name"]] = state
        else:
            iso2_to_state[state["iso2"]] = state

    for istat_name, our_name in region_name_pairs.items():
        state = name_to_state.get(our_name)
        if not state:
            raise RuntimeError(
                f"Region not found for ISTAT name {istat_name!r} (expected our name {our_name!r})"
            )
        region_name_to_id[istat_name] = state["id"]

    # Build state_id -> region_id by walking parent_id up to a region/autonomous region.
    state_to_region: Dict[int, int] = {}
    for state in states:
        if state.get("country_code") != "IT":
            continue
        cursor = state
        seen: set = set()
        while cursor and cursor["id"] not in seen:
            seen.add(cursor["id"])
            if cursor["type"] in ("region", "autonomous region"):
                state_to_region[state["id"]] = cursor["id"]
                break
            parent = cursor.get("parent_id")
            cursor = id_to_state.get(parent) if parent else None

    return iso2_to_state, id_to_state, region_name_to_id, state_to_region


def candidate_for_city(
    city: dict,
    comune_index: Dict[str, List[dict]],
    conjunction_index: Dict[str, List[dict]],
    sigla_to_region: Dict[str, str],
    region_name_to_id: Dict[str, int],
    state_to_region: Dict[int, int],
) -> Tuple[Optional[dict], str]:
    """Pick the best ISTAT comune for a city.

    A name-only match is rejected when the candidate's ISTAT region differs from
    the city's current region — otherwise frazioni named "San Lorenzo" in
    Lombardy would all snap to the single ISTAT "San Lorenzo" in Calabria.
    Rejected candidates fall through to the proximity pass.

    Returns:
        (record, reason). reason is one of:
            'name_unique'      - one ISTAT match in the same region.
            'name_region'      - multiple ISTAT matches, one in the same region.
            'name_ambiguous'   - one or more ISTAT matches, none in the same
                                 region; treated as no_match by the caller.
            'name_conjunction' - matched via " e "-conjunction half + region.
            'no_match'         - the name produced no ISTAT match.
    """
    city_name = city.get("name", "")
    keys = set(expand_keys(city_name))
    # Honour English -> Italian aliases for the major ISO-named metro cities.
    for k in list(keys):
        alias = ENGLISH_TO_ITALIAN_ALIASES.get(k)
        if alias:
            keys.add(alias)
    seen_id: set = set()
    candidates: List[dict] = []
    for key in keys:
        for rec in comune_index.get(key, []):
            ident = (rec["sigla"], rec["italian_name"], rec["codice_catastale"])
            if ident in seen_id:
                continue
            seen_id.add(ident)
            candidates.append(rec)

    current_region_id = state_to_region.get(city.get("state_id"))

    def in_current_region(rec: dict) -> bool:
        return region_name_to_id.get(rec["region_it"]) == current_region_id

    if candidates:
        region_filtered = [rec for rec in candidates if in_current_region(rec)]
        if len(region_filtered) == 1 and len(candidates) == 1:
            return region_filtered[0], "name_unique"
        if len(region_filtered) >= 1:
            return region_filtered[0], "name_region"
        # All candidates are in a different region: don't trust the name match.
        return None, "name_ambiguous"

    # Conjunction fallback: only accept if the half-match lies in the same region.
    seen_id.clear()
    conj_candidates: List[dict] = []
    for key in keys:
        for rec in conjunction_index.get(key, []):
            ident = (rec["sigla"], rec["italian_name"], rec["codice_catastale"])
            if ident in seen_id:
                continue
            seen_id.add(ident)
            conj_candidates.append(rec)
    if conj_candidates:
        region_filtered = [rec for rec in conj_candidates if in_current_region(rec)]
        if len(region_filtered) >= 1:
            return region_filtered[0], "name_conjunction"

    return None, "no_match"


def resolve_state_for_sigla(
    sigla: str, iso2_to_state: Dict[str, dict]
) -> Optional[Tuple[int, str]]:
    """Map an ISTAT sigla to (state_id, state_code) per the rules at top of file."""
    if sigla in iso2_to_state:
        state = iso2_to_state[sigla]
        return state["id"], state["iso2"]
    if sigla in SIGLA_FALLBACK:
        return SIGLA_FALLBACK[sigla]
    return None


def remap_cities(
    cities: List[dict],
    comune_index: Dict[str, List[dict]],
    conjunction_index: Dict[str, List[dict]],
    sigla_to_region: Dict[str, str],
    iso2_to_state: Dict[str, dict],
    id_to_state: Dict[int, dict],
    region_name_to_id: Dict[str, int],
    state_to_region: Dict[int, int],
) -> dict:
    """Run the two-pass remap. Returns a structured report; mutates cities in place."""
    matched_pairs: List[Tuple[float, float, str]] = []  # (lat, lon, sigla) for proximity pass
    pending_proximity: List[dict] = []
    unmapped: List[dict] = []

    name_unique = name_region = name_ambig = name_conj = no_match = 0
    changed = unchanged = 0
    sigla_distribution: Counter = Counter()
    sigla_changes: Counter = Counter()
    comune_to_cities: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
    annotations: List[dict] = []

    for city in cities:
        record, reason = candidate_for_city(
            city,
            comune_index,
            conjunction_index,
            sigla_to_region,
            region_name_to_id,
            state_to_region,
        )
        if reason == "name_unique":
            name_unique += 1
        elif reason == "name_region":
            name_region += 1
        elif reason == "name_ambiguous":
            name_ambig += 1
        elif reason == "name_conjunction":
            name_conj += 1
        else:
            no_match += 1

        if record is None:
            pending_proximity.append(city)
            continue

        sigla = record["sigla"]
        target = resolve_state_for_sigla(sigla, iso2_to_state)
        if target is None:
            unmapped.append({"id": city["id"], "name": city["name"], "reason": f"unknown_sigla:{sigla}"})
            continue

        target_id, target_code = target
        comune_to_cities[(sigla, record["italian_name"])].append(
            {"id": city["id"], "name": city["name"], "lat": city.get("latitude"), "lon": city.get("longitude")}
        )
        if city["state_id"] != target_id or city["state_code"] != target_code:
            previous = (city["state_id"], city["state_code"])
            city["state_id"] = target_id
            city["state_code"] = target_code
            changed += 1
            sigla_changes[sigla] += 1
            annotations.append(
                {
                    "id": city["id"],
                    "name": city["name"],
                    "from_state_id": previous[0],
                    "from_state_code": previous[1],
                    "to_state_id": target_id,
                    "to_state_code": target_code,
                    "via": reason,
                    "comune": record["italian_name"],
                }
            )
        else:
            unchanged += 1
        sigla_distribution[sigla] += 1

        lat = safe_float(city.get("latitude"))
        lon = safe_float(city.get("longitude"))
        if lat is not None and lon is not None:
            matched_pairs.append((lat, lon, sigla))

    # Pass 2: coordinate fallback for cities with no name match.
    proximity_changed = 0
    proximity_skipped = 0
    for city in pending_proximity:
        lat = safe_float(city.get("latitude"))
        lon = safe_float(city.get("longitude"))
        if lat is None or lon is None or not matched_pairs:
            unmapped.append({"id": city["id"], "name": city["name"], "reason": "no_match_no_coords"})
            proximity_skipped += 1
            continue

        # k-nearest-neighbour majority vote, weighted by inverse distance.
        scored = sorted(
            (
                (haversine_km(lat, lon, mlat, mlon), msigla)
                for mlat, mlon, msigla in matched_pairs
            ),
            key=lambda x: x[0],
        )[:PROXIMITY_K]
        nearest_dist = scored[0][0] if scored else float("inf")
        if nearest_dist > PROXIMITY_LIMIT_KM:
            unmapped.append(
                {"id": city["id"], "name": city["name"], "reason": f"too_far:{nearest_dist:.1f}km"}
            )
            proximity_skipped += 1
            continue
        votes: Counter = Counter()
        for d, sig in scored:
            votes[sig] += 1.0 / max(d, 0.1)
        best_sigla = votes.most_common(1)[0][0]
        target = resolve_state_for_sigla(best_sigla, iso2_to_state)
        if target is None:
            unmapped.append({"id": city["id"], "name": city["name"], "reason": f"unknown_sigla:{best_sigla}"})
            proximity_skipped += 1
            continue
        target_id, target_code = target
        if city["state_id"] != target_id or city["state_code"] != target_code:
            previous = (city["state_id"], city["state_code"])
            city["state_id"] = target_id
            city["state_code"] = target_code
            changed += 1
            proximity_changed += 1
            sigla_distribution[best_sigla] += 1
            sigla_changes[best_sigla] += 1
            annotations.append(
                {
                    "id": city["id"],
                    "name": city["name"],
                    "from_state_id": previous[0],
                    "from_state_code": previous[1],
                    "to_state_id": target_id,
                    "to_state_code": target_code,
                    "via": f"proximity_knn:{nearest_dist:.1f}km",
                    "comune": None,
                }
            )
        else:
            unchanged += 1
            sigla_distribution[best_sigla] += 1

    duplicates = [
        {
            "sigla": sigla,
            "comune": comune,
            "cities": records,
        }
        for (sigla, comune), records in comune_to_cities.items()
        if len(records) > 1
    ]
    duplicates.sort(key=lambda d: (-len(d["cities"]), d["sigla"], d["comune"]))

    return {
        "totals": {
            "input": len(cities),
            "name_unique": name_unique,
            "name_region": name_region,
            "name_ambiguous": name_ambig,
            "name_conjunction": name_conj,
            "no_match": no_match,
            "proximity_assigned": proximity_changed,
            "proximity_skipped_or_far": proximity_skipped,
            "changed": changed,
            "unchanged": unchanged,
            "unmapped": len(unmapped),
        },
        "by_sigla": dict(sigla_distribution.most_common()),
        "changes_by_sigla": dict(sigla_changes.most_common()),
        "unmapped": unmapped,
        "possible_duplicates": duplicates,
        "annotations_sample": annotations[:50],
    }


def write_cities_normalised(cities: List[dict]) -> None:
    """Write IT.json in repo's standard JSON shape (2-space indent, no trailing newline)."""
    text = json.dumps(cities, ensure_ascii=False, indent=2)
    CITIES_JSON.write_text(text, encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print report without writing IT.json.",
    )
    parser.add_argument(
        "--refresh-istat",
        action="store_true",
        help="Re-download the ISTAT comune CSV before running.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Write the full structured report as JSON to this path.",
    )
    args = parser.parse_args(argv)

    fetch_istat_if_missing(args.refresh_istat)

    states = json.loads(STATES_JSON.read_text(encoding="utf-8"))
    iso2_to_state, id_to_state, region_name_to_id, state_to_region = build_state_lookups(states)
    comune_index, conjunction_index, sigla_to_region = load_istat()
    cities = json.loads(CITIES_JSON.read_text(encoding="utf-8"))

    report = remap_cities(
        cities,
        comune_index,
        conjunction_index,
        sigla_to_region,
        iso2_to_state,
        id_to_state,
        region_name_to_id,
        state_to_region,
    )

    print("=" * 70)
    print("Italy city remap (issue #1349) report")
    print("=" * 70)
    for k, v in report["totals"].items():
        print(f"  {k:32} {v}")
    print()
    print(f"Distribution after remap (top 25 of {len(report['by_sigla'])}):")
    for sigla, count in list(report["by_sigla"].items())[:25]:
        state = iso2_to_state.get(sigla)
        label = f"{state['name']} ({state['type']})" if state else SIGLA_FALLBACK.get(sigla, ('?','?'))
        print(f"  {sigla:4} {count:5}  {label}")
    print()
    print(f"Possible duplicates (>=2 cities to one comune): {len(report['possible_duplicates'])}")
    for entry in report["possible_duplicates"][:15]:
        names = ", ".join(c["name"] for c in entry["cities"])
        print(f"  [{entry['sigla']}] {entry['comune']}: {names}")
    print()
    print(f"Unmapped: {len(report['unmapped'])}")
    for entry in report["unmapped"][:20]:
        print(f"  id={entry['id']:7}  {entry['name']:40}  reason={entry['reason']}")

    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nFull report written to {args.report}")

    if args.dry_run:
        print("\n--dry-run: IT.json NOT modified.")
        return 0

    write_cities_normalised(cities)
    print(f"\nWrote {len(cities)} cities to {CITIES_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
