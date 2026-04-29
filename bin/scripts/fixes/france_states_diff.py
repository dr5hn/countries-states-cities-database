#!/usr/bin/env python3
"""
Diff French state-level metadata in `contributions/states/states.json` against
the authoritative data.gouv.fr feeds (departements + regions).

Purpose
-------
Issue #1352 asks us to polish French department/region metadata. The
authoritative reference is the open INSEE-derived feeds published by
data.gouv.fr:

  - departements.min.json : 101 entries (96 metropolitan + 5 overseas DROM)
  - regions.min.json      : 18 entries (13 metropolitan + 5 overseas DROM)

This script compares those feeds against the FR records in our repo and reports
deltas worth a maintainer's attention:

  * Type / classification (e.g. is "Corse" classified as a region?)
  * Native (French) names that differ from data.gouv.fr's `nom`
  * Records that exist in our repo but not in the feed (likely overseas
    collectivities and territories the feeds don't enumerate)
  * Records in the feed that are missing from our repo

Usage
-----
    python3 bin/scripts/fixes/france_states_diff.py \
        --departements /tmp/fr1352/departements.min.json \
        --regions /tmp/fr1352/regions.min.json

Defaults to /tmp/fr1352/ if --departements / --regions are omitted.

Notes
-----
- Repo `name` is English; `native` is French. data.gouv.fr only reports French.
  The script therefore compares data.gouv.fr `nom` against repo `native`,
  NOT against `name`. Native diffs are advisory; English `name` is left alone.
- data.gouv.fr region codes (e.g. "94" = Corse, "11" = Île-de-France) are NOT
  the same as ISO 3166-2 codes; the repo's `iso2` for regions stores the
  alphabetic ISO sub-codes (ARA, BFC, …) for metro regions and the INSEE region
  code for overseas regions (971…976). The script keeps these code spaces
  separate.

This script is read-only. It does not mutate states.json.
"""

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
STATES_FILE = REPO_ROOT / "contributions" / "states" / "states.json"

# Map data.gouv.fr region `code` → repo `iso2` for metropolitan regions.
# Source: ISO 3166-2:FR (3-letter codes after FR-) cross-referenced with
# INSEE region numbers.
REGION_CODE_TO_ISO2_METRO: Dict[str, str] = {
    "11": "IDF",   # Île-de-France
    "24": "CVL",   # Centre-Val de Loire
    "27": "BFC",   # Bourgogne-Franche-Comté
    "28": "NOR",   # Normandie
    "32": "HDF",   # Hauts-de-France
    "44": "GES",   # Grand Est
    "52": "PDL",   # Pays de la Loire
    "53": "BRE",   # Bretagne
    "75": "NAQ",   # Nouvelle-Aquitaine
    "76": "OCC",   # Occitanie
    "84": "ARA",   # Auvergne-Rhône-Alpes
    "93": "PAC",   # Provence-Alpes-Côte d'Azur
    "94": "20R",   # Corse (sole region with numeric ISO sub-code)
}

# Map data.gouv.fr region `code` → repo `iso2` for overseas regions.
# data.gouv.fr uses 01..06; repo uses the INSEE department codes 971..976.
REGION_CODE_TO_ISO2_OVERSEAS: Dict[str, str] = {
    "01": "971",   # Guadeloupe
    "02": "972",   # Martinique
    "03": "973",   # Guyane / French Guiana
    "04": "974",   # La Réunion
    "06": "976",   # Mayotte
}


def load_json(path: Path) -> list:
    """Load a JSON file from disk; raises FileNotFoundError if missing."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def normalize(s: Optional[str]) -> str:
    """
    Normalize a string for fuzzy comparison: NFC, lowercased, hyphens and
    spaces collapsed, curly apostrophes folded to straight. Used to flag
    typographical drift while still printing the raw values.
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("-", " ")
    s = " ".join(s.split())
    return s.casefold()


def fr_states(states: Iterable[dict]) -> List[dict]:
    """Filter the master states list down to FR records."""
    return [s for s in states if s.get("country_code") == "FR"]


def report_delta(label: str, code: str, field: str, repo_val, feed_val) -> None:
    """Print a single discrepancy line in a consistent format."""
    print(f"  [{label}] {code:6} {field:9} repo={repo_val!r:40} feed={feed_val!r}")


def diff_departements(repo_fr: List[dict], feed: List[dict]) -> Tuple[int, int]:
    """
    Diff department-level metadata.

    Returns (delta_count, missing_in_repo_count).
    """
    print("\n=== Departments (101 expected from data.gouv.fr) ===")
    print(f"  feed: {len(feed)}  repo (type=metropolitan department + overseas region): see below\n")

    repo_by_iso2: Dict[str, dict] = {s["iso2"]: s for s in repo_fr if s.get("iso2")}
    deltas = 0
    missing = 0

    for entry in feed:
        code = entry["code"]
        nom = entry["nom"]
        repo = repo_by_iso2.get(code)
        if repo is None:
            print(f"  [MISSING] code={code} nom={nom!r} not in repo iso2 index")
            missing += 1
            continue

        # Native check
        if normalize(repo.get("native")) != normalize(nom):
            report_delta("NATIVE", code, "native", repo.get("native"), nom)
            deltas += 1

        # Sanity: name should NOT equal feed nom verbatim if it's supposed to
        # be English. Flag department records where name and native differ
        # from the feed (these are usually fine — most dept names are
        # identical in English and French — but worth eyeballing).
        # Skip: too noisy. We only flag native diffs.

    return deltas, missing


def diff_regions(repo_fr: List[dict], feed: List[dict]) -> Tuple[int, int]:
    """
    Diff region-level metadata.

    Reports:
      * Native-name drift vs data.gouv.fr `nom`.
      * Type/classification: Corse should be `metropolitan region` per
        data.gouv.fr; other entries should already match.
      * Records in the feed missing from our repo.
    """
    print("\n=== Regions (18 expected from data.gouv.fr: 13 metro + 5 overseas) ===")
    print(f"  feed: {len(feed)}\n")

    repo_by_iso2: Dict[str, dict] = {s["iso2"]: s for s in repo_fr if s.get("iso2")}

    deltas = 0
    missing = 0
    metro_codes = set(REGION_CODE_TO_ISO2_METRO)
    overseas_codes = set(REGION_CODE_TO_ISO2_OVERSEAS)

    for entry in feed:
        code = entry["code"]
        nom = entry["nom"]

        if code in metro_codes:
            iso2 = REGION_CODE_TO_ISO2_METRO[code]
            expected_type = "metropolitan region"
        elif code in overseas_codes:
            iso2 = REGION_CODE_TO_ISO2_OVERSEAS[code]
            expected_type = "overseas region"
        else:
            print(f"  [UNKNOWN-CODE] feed code={code} nom={nom!r} not mapped")
            continue

        repo = repo_by_iso2.get(iso2)
        if repo is None:
            print(f"  [MISSING] feed code={code} → expected iso2={iso2} ({nom!r}) not found")
            missing += 1
            continue

        if repo.get("type") != expected_type:
            report_delta("TYPE", iso2, "type", repo.get("type"), expected_type)
            deltas += 1

        if normalize(repo.get("native")) != normalize(nom):
            report_delta("NATIVE", iso2, "native", repo.get("native"), nom)
            deltas += 1

    return deltas, missing


def report_typography(repo_fr: List[dict], regs_feed: List[dict]) -> None:
    """
    Surface region/department records where the *normalized* native string
    matches the feed but the *raw* string differs (curly vs straight quotes,
    hyphens vs spaces, etc.). These are advisory: the repo and feed disagree
    only on typography, and which form is canonical is a maintainer call.
    """
    print("\n=== Typographical-only native diffs (advisory) ===")
    metro = REGION_CODE_TO_ISO2_METRO
    overseas = REGION_CODE_TO_ISO2_OVERSEAS
    repo_by_iso2 = {s["iso2"]: s for s in repo_fr if s.get("iso2")}
    flagged = 0
    for entry in regs_feed:
        iso2 = metro.get(entry["code"]) or overseas.get(entry["code"])
        if not iso2:
            continue
        repo = repo_by_iso2.get(iso2)
        if not repo:
            continue
        repo_native = repo.get("native") or ""
        feed_nom = entry["nom"]
        if repo_native == feed_nom:
            continue
        if normalize(repo_native) != normalize(feed_nom):
            continue  # already reported as a real delta
        print(f"  [TYPO]   {iso2:6} repo={repo_native!r:40} feed={feed_nom!r}")
        flagged += 1
    if flagged == 0:
        print("  (none)")


def report_coverage(repo_fr: List[dict]) -> None:
    """
    Coverage stats for fields data.gouv.fr does not provide (fips_code,
    iso3166_2, latitude, longitude). Useful to surface gaps even though
    they cannot be filled from these feeds alone.
    """
    print("\n=== Coverage of fields not in data.gouv.fr feeds ===")
    fields = ("fips_code", "iso3166_2", "latitude", "longitude", "wikiDataId", "timezone")
    total = len(repo_fr)
    for f in fields:
        filled = sum(1 for s in repo_fr if s.get(f) not in (None, ""))
        print(f"  {f:12} filled: {filled:3}/{total}")


def report_extras(repo_fr: List[dict]) -> None:
    """
    List FR repo records that are *not* covered by either feed: overseas
    collectivities, dependencies, special-status metropolitan collectivities,
    and the overseas territory (TF). Listed as advisory; the feeds do not
    cover these.
    """
    feed_covered_types = {"metropolitan department", "metropolitan region", "overseas region"}
    extras = [s for s in repo_fr if s.get("type") not in feed_covered_types]
    if not extras:
        return
    print("\n=== Repo records NOT covered by data.gouv.fr feeds (advisory only) ===")
    print("  These are intentionally outside the metropolitan/DROM scope of the feeds.\n")
    for s in sorted(extras, key=lambda x: (x.get("type", ""), x.get("iso2", ""))):
        print(
            f"  [EXTRA] {s.get('iso2',''):6} type={s.get('type',''):50}"
            f" name={s.get('name',''):35} native={s.get('native','')}"
        )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--departements",
        type=Path,
        default=Path("/tmp/fr1352/departements.min.json"),
        help="Path to departements.min.json from data.gouv.fr",
    )
    parser.add_argument(
        "--regions",
        type=Path,
        default=Path("/tmp/fr1352/regions.min.json"),
        help="Path to regions.min.json from data.gouv.fr",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point. Returns 0 if no fatal errors occurred."""
    args = parse_args()

    for path in (args.departements, args.regions, STATES_FILE):
        if not path.exists():
            print(f"ERROR: required file missing: {path}", file=sys.stderr)
            return 2

    deps_feed = load_json(args.departements)
    regs_feed = load_json(args.regions)
    states = load_json(STATES_FILE)
    repo_fr = fr_states(states)

    print(f"FR repo records: {len(repo_fr)}")
    print(f"Departements feed: {len(deps_feed)}")
    print(f"Regions feed:      {len(regs_feed)}")

    dep_deltas, dep_missing = diff_departements(repo_fr, deps_feed)
    reg_deltas, reg_missing = diff_regions(repo_fr, regs_feed)
    report_typography(repo_fr, regs_feed)
    report_coverage(repo_fr)
    report_extras(repo_fr)

    print("\n=== Summary ===")
    print(f"  Department deltas (native): {dep_deltas}")
    print(f"  Department missing in repo: {dep_missing}")
    print(f"  Region deltas (native+type): {reg_deltas}")
    print(f"  Region missing in repo:      {reg_missing}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
