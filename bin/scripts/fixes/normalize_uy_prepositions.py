#!/usr/bin/env python3
"""Normalise Spanish prepositions/articles in Uruguay city names.

Spanish toponymy lowercases interior prepositions and articles
(``de``, ``del``, ``la``, ``las``, ``los``, ``el``, ``y``) — e.g.
``Paso De Los Toros`` -> ``Paso de los Toros``. Many UY city ``name``
values were imported title-cased, capitalising every token.

Rules
-----
* Only the listed connectors are touched; every other token is left as-is.
* A connector is lowercased only when it is *interior* — not the first
  token of the name, and not the first token of a segment that follows a
  separator (``-``/``/``). This keeps names like ``San Rafael - El Placer``
  and ``Pinares - Las Delicias`` correct.
* ``A`` is deliberately excluded: it collides with middle initials
  (``Capitan J A Artigas``). The single genuine-preposition case
  (``Palo A Pique``) is handled explicitly below.
* Idempotent — safe to re-run.

Usage
-----
    python3 bin/scripts/fixes/normalize_uy_prepositions.py --dry-run
    python3 bin/scripts/fixes/normalize_uy_prepositions.py
"""

import argparse
import json
import sys
from pathlib import Path

FILE = Path("contributions/cities/UY.json")

CONNECTORS = {"De", "Del", "La", "Las", "Los", "El", "Y"}
SEPARATORS = {"-", "/", "–"}

# Explicit one-offs that the generic rule cannot resolve safely.
EXPLICIT = {
    "Palo A Pique": "Palo a Pique",  # "a" is the preposition, not an initial
}


def normalize(name: str) -> str:
    """Lowercase interior Spanish connectors in a place name."""
    if name in EXPLICIT:
        return EXPLICIT[name]

    tokens = name.split(" ")
    segment_start = True  # first token of the name or of a post-separator segment
    out = []
    for tok in tokens:
        if tok in SEPARATORS:
            out.append(tok)
            segment_start = True
            continue
        if not segment_start and tok in CONNECTORS:
            out.append(tok.lower())
        else:
            out.append(tok)
        segment_start = False
    return " ".join(out)


def main() -> int:
    """Apply (or preview) the normalisation across UY.json."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without writing")
    args = parser.parse_args()

    if not FILE.exists():
        print(f"ERROR: {FILE} not found (run from repo root)", file=sys.stderr)
        return 1

    records = json.loads(FILE.read_text(encoding="utf-8"))
    changes = []
    for r in records:
        old = r.get("name", "")
        new = normalize(old)
        if new != old:
            changes.append((old, new))
            r["name"] = new

    print(f"{FILE}: {len(records)} rows, {len(changes)} name(s) normalised")
    for old, new in changes:
        print(f"  {old!r}  ->  {new!r}")

    if args.dry_run:
        print("\n(dry run — no changes written)")
        return 0

    FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
