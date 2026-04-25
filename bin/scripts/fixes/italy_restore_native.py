#!/usr/bin/env python3
"""Restore the `native` field for Italian cities corrupted by past machine
translation runs (e.g. `Pero` → native `Ma`, `Postal` → native `Postale`,
`Petit Fenis` → native `Chiede un fieno`).

Strategy:
  1. Build a normalised lookup of ISTAT comune Italian names (and bilingual
     alternatives) -> the canonical Italian denomination, reusing the same
     normalisation as italy_remap_cities.py.
  2. For each city: if `name` matches an ISTAT entry (so we know `name` is the
     authoritative Italian form), and `native` differs from `name`, replace
     `native` with `name`.  Cities whose `name` is not an ISTAT comune (mostly
     frazioni) are left untouched — we have no ground truth to second-guess
     them.

Idempotent.  Only the `native` field is mutated.

Usage:
    python3 bin/scripts/fixes/italy_restore_native.py [--dry-run] [--report path]
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
ISTAT_CSV = REPO_ROOT / "bin/scripts/fixes/data/istat-elenco-comuni-italiani.csv"
CITIES_JSON = REPO_ROOT / "contributions/cities/IT.json"


def normalise_name(value: str) -> str:
    """Same fold used by italy_remap_cities.py: lowercased, NFD-stripped diacritics,
    apostrophe-collapsed, single-spaced, alphanumeric+apostrophe+hyphen+slash only."""
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


def load_istat_index() -> Dict[str, str]:
    """Map normalised key -> canonical ISTAT Italian denomination."""
    index: Dict[str, str] = {}
    with ISTAT_CSV.open("r", encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        for row in reader:
            ita = row["Denominazione in italiano"].strip()
            alt = row["Denominazione altra lingua"].strip()
            full = row["Denominazione (Italiana e straniera)"].strip()
            if not ita:
                continue
            for source in (ita, alt, full):
                for key in expand_keys(source):
                    # Don't overwrite an Italian-name key with a bilingual alt key.
                    index.setdefault(key, ita)
    return index


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args(argv)

    index = load_istat_index()
    cities = json.loads(CITIES_JSON.read_text(encoding="utf-8"))

    examples: List[dict] = []
    examples_kept: List[dict] = []
    changed = 0
    skipped_no_istat = 0
    already_correct = 0
    by_first_letter: Counter = Counter()

    for city in cities:
        name = city.get("name") or ""
        native = city.get("native")
        if not name:
            continue
        keys = expand_keys(name)
        canonical: Optional[str] = None
        for k in keys:
            if k in index:
                canonical = index[k]
                break
        if canonical is None:
            skipped_no_istat += 1
            continue
        # We know `name` is the canonical Italian form (it matched ISTAT).
        # Replace `native` with `name` when they differ.
        if native == name:
            already_correct += 1
            continue
        previous = native
        city["native"] = name
        changed += 1
        by_first_letter[name[:1].upper()] += 1
        if len(examples) < 25:
            examples.append({"id": city.get("id"), "name": name, "from": previous, "to": name})

    print(f"Total cities: {len(cities)}")
    print(f"  unchanged (no ISTAT match for name): {skipped_no_istat}")
    print(f"  unchanged (native already == name):  {already_correct}")
    print(f"  native restored:                     {changed}")
    print()
    print("Top 25 corrupted samples (before -> after):")
    for ex in examples:
        print(f"  id={ex['id']:7} {ex['name']!r:35} native: {ex['from']!r:25} -> {ex['to']!r}")
    print()
    print("Distribution by first letter:")
    for letter, count in by_first_letter.most_common():
        print(f"  {letter or '?':2} {count}")

    if args.report:
        args.report.write_text(
            json.dumps(
                {
                    "totals": {
                        "input": len(cities),
                        "skipped_no_istat": skipped_no_istat,
                        "already_correct": already_correct,
                        "changed": changed,
                    },
                    "by_first_letter": dict(by_first_letter),
                    "examples": examples,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    if args.dry_run:
        print("\n--dry-run: IT.json not modified.")
        return 0

    text = json.dumps(cities, ensure_ascii=False, indent=2)
    CITIES_JSON.write_text(text, encoding="utf-8")
    print(f"\nWrote {len(cities)} cities to {CITIES_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
