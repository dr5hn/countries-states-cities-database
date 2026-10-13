#!/usr/bin/env python3
"""Compare contributions/ after the MySQL round trip (import, then sync) with the committed version.

Rows that had an id must come back with the same fields and values (MySQL's created_at, updated_at and flag aside;
typed comparison, so 1, 1.0 and true differ). Rows committed without an id may come back with a new id, and only
they may. Any other difference fails, so a lossy import or sync stops the export.

Usage (repository root, after the sync):  python3 bin/scripts/sync/check_round_trip.py [--ref HEAD]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

MANAGED = {'created_at', 'updated_at', 'flag'}


def canon(row):
    """Typed, key-order independent text of a row without the fields MySQL manages."""
    return json.dumps({k: v for k, v in row.items() if k not in MANAGED}, ensure_ascii=False, sort_keys=True)


def compare(path, before, after):
    """Problems for one file: changed or missing rows that had an id, and new ids beyond the id-less rows."""
    problems = []
    old = {r['id']: r for r in before if r.get('id') is not None}
    new = {r['id']: r for r in after if r.get('id') is not None}
    idless = sum(1 for r in before if r.get('id') is None)
    for i in sorted(old):
        if i not in new:
            problems.append(f'{path}: id {i} is missing after the round trip')
        elif canon(old[i]) != canon(new[i]):
            problems.append(f'{path}: id {i} changed in the round trip')
    if len(new) - len(old.keys() & new.keys()) != idless:
        problems.append(f'{path}: {len(new) - len(old.keys() & new.keys())} new ids for {idless} rows committed without one')
    if len(after) != len(before):
        problems.append(f'{path}: {len(before)} rows committed, {len(after)} after the round trip')
    return problems


def main(argv=None):
    """Compare every committed contributions JSON file; exit 1 listing the problems."""
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--ref', default='HEAD', help='commit to compare with (default HEAD)')
    a = p.parse_args(argv)
    paths = subprocess.run(['git', 'ls-tree', '-r', '--name-only', a.ref, '--', 'contributions/'], capture_output=True,
                           text=True, check=True).stdout.split()
    problems = []
    for path in (x for x in paths if x.endswith('.json')):
        before = json.loads(subprocess.run(['git', 'show', f'{a.ref}:{path}'], capture_output=True, check=True).stdout)
        if not Path(path).exists():
            problems.append(f'{path}: missing after the round trip')
            continue
        problems += compare(path, before, json.loads(Path(path).read_text(encoding='utf-8')))
    for x in problems[:100]:
        print(f'[ERROR] {x}')
    if problems:
        print(f'[ERROR] {len(problems)} round-trip differences; the import or sync lost or changed data. Compare the files above with {a.ref}.')
        return 1
    print(f'[INFO] round trip: all {len(paths)} contributions files match {a.ref}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
