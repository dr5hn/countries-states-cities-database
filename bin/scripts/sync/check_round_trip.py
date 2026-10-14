#!/usr/bin/env python3
"""Compare contributions/ after the MySQL round trip (import, then sync) with the version that was imported.

Rows that had an id must come back with the same fields and values (MySQL's created_at, updated_at and flag aside;
typed comparison, so 1, 1.0 and true differ). Rows imported without an id must come back, field for field, as the rows
with newly assigned ids, and only they may gain one. The set of JSON files must match too. Any other difference fails,
so a lossy import or sync stops the export.

The expected side is a commit (--ref, default HEAD) or a copy of contributions/ taken just before the import
(--snapshot DIR), which also covers files that are not committed, such as a test fixture.

Usage (repository root, after the sync):  python3 bin/scripts/sync/check_round_trip.py [--ref HEAD | --snapshot DIR]
"""
import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

MANAGED = {'created_at', 'updated_at', 'flag'}


def canon(row, drop=()):
    """Typed, key-order independent text of a row without the fields MySQL manages (and any in drop)."""
    return json.dumps({k: v for k, v in row.items() if k not in MANAGED and k not in drop}, ensure_ascii=False,
                      sort_keys=True)


def keyed(path, rows, side, problems):
    """Rows by id and the rows without one, refusing non-object rows and ids that are invalid or repeated."""
    by_id, idless = {}, []
    if not isinstance(rows, list):
        problems.append(f'{path}: {side} is not an array of records')
        return by_id, idless
    for n, r in enumerate(rows):
        i = r.get('id') if isinstance(r, dict) else None
        if not isinstance(r, dict):
            problems.append(f'{path}: {side} row {n} is not an object')
        elif i is None:
            idless.append(r)
        elif type(i) is not int or i <= 0:
            problems.append(f'{path}: {side} row {n} has id {i!r}, not a positive integer')
        elif i in by_id:
            problems.append(f'{path}: {side} id {i} appears more than once')
        else:
            by_id[i] = r
    return by_id, idless


def compare(path, before, after):
    """Problems for one file: rows that had an id and changed or went missing, and new-id rows that do not match the
    imported id-less rows one for one."""
    problems = []
    old, old_idless = keyed(path, before, 'imported', problems)
    new, new_idless = keyed(path, after, 'round-trip', problems)
    if new_idless:
        problems.append(f'{path}: {len(new_idless)} rows have no id after the round trip')
    for i in sorted(old):
        if i not in new:
            problems.append(f'{path}: id {i} is missing after the round trip')
        elif canon(old[i]) != canon(new[i]):
            problems.append(f'{path}: id {i} changed in the round trip')
    # the id-less rows and the rows that gained an id must be the same payloads, as many times each
    wanted = collections.Counter(canon(r, {'id'}) for r in old_idless)
    got = collections.Counter(canon(new[i], {'id'}) for i in new.keys() - old.keys())
    if wanted != got:
        problems.append(f'{path}: {sum((wanted - got).values())} rows imported without an id did not come back as '
                        f'imported; {sum((got - wanted).values())} rows with new ids match no imported row')
    return problems


def expected_files(ref, snapshot):
    """The imported JSON files: {path from the repository root: function returning their bytes}."""
    if snapshot:
        root = Path(snapshot)
        if not root.is_dir():
            raise FileNotFoundError(f'snapshot folder {snapshot} does not exist')
        return {f'contributions/{p.relative_to(root).as_posix()}': p.read_bytes for p in sorted(root.rglob('*.json'))}
    paths = subprocess.run(['git', 'ls-tree', '-r', '--name-only', ref, '--', 'contributions/'], capture_output=True,
                           text=True, check=True).stdout.split()
    return {x: (lambda x=x: subprocess.run(['git', 'show', f'{ref}:{x}'], capture_output=True, check=True).stdout)
            for x in paths if x.endswith('.json')}


def main(argv=None):
    """Compare every imported contributions JSON file with its round-trip copy; exit 1 listing the problems."""
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    g = p.add_mutually_exclusive_group()
    g.add_argument('--ref', default='HEAD', help='commit that was imported (default HEAD)')
    g.add_argument('--snapshot', help='copy of contributions/ taken just before the import')
    a = p.parse_args(argv)
    source = a.snapshot or a.ref
    try:
        expected = expected_files(a.ref, a.snapshot)
    except (OSError, subprocess.CalledProcessError) as e:
        print(f'[ERROR] cannot read the imported files from {source}: {e}')
        return 1
    actual = {q.as_posix() for q in Path('contributions').rglob('*.json')}
    problems = [f'{x}: not among the imported files' for x in sorted(actual - expected.keys())]
    problems += [f'{x}: missing after the round trip' for x in sorted(expected.keys() - actual)]
    for path in sorted(expected.keys() & actual):
        try:
            before = json.loads(expected[path]())
            after = json.loads(Path(path).read_text(encoding='utf-8'))
        except (OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as e:
            problems.append(f'{path}: cannot be read: {e}')
            continue
        problems += compare(path, before, after)
    for x in problems[:100]:
        print(f'[ERROR] {x}')
    if problems:
        print(f'[ERROR] {len(problems)} round-trip differences; the import or sync lost or changed data. Compare the '
              f'files above with {source}.')
        return 1
    print(f'[INFO] round trip: all {len(expected)} contributions JSON files match {source}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
