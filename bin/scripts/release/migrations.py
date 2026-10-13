#!/usr/bin/env python3
"""Release migration files for a data release (v5 plan; decisions_3_final.md).

Compares contributions/ at two git refs and writes, for consumers:
  removed_ids.jsonl / removed_ids.csv  every id that left the data, with its reviewed outcome and targets
  changed_fields.jsonl                 every changed field of a surviving record (translations per language key)
  release_manifest.json                refs, counts per table and field, and SHA-256 of each file above
It fails, writing nothing, when a removed id has no reviewed event in the ledger, a target does not exist in the new
snapshot, a redirect is claimed for anything but a proved same-place merge, or a retired id is in use again.

Usage:
  python3 bin/scripts/release/migrations.py --from v4.0 --to HEAD --ledger migrations/events.jsonl --out build/migrations
"""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TABLES = {'countries': 'contributions/countries/countries.json', 'states': 'contributions/states/states.json',
          'counties': 'contributions/counties', 'cities': 'contributions/cities', 'postcodes': 'contributions/postcodes'}
OUTCOMES = {'merged_same_entity', 'administrative_seat', 'moved_dataset', 'territorial_successor', 'split_into',
            'namespace_replaced', 'invalid_record', 'no_successor'}
NO_TARGET = {'namespace_replaced', 'invalid_record', 'no_successor'}   # outcomes whose targets are empty
IGNORED = {'created_at', 'updated_at', 'flag'}   # managed by MySQL; not a change consumers act on


class MigrationError(Exception):
    """A removal or reference the release cannot explain."""


def git(repo, *args):
    """Output of a git command in the repo; raises with git's message on failure."""
    r = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if r.returncode:
        raise MigrationError(f"git {' '.join(args)}: {r.stderr.decode().strip()}")
    return r.stdout


def snapshot(repo, ref):
    """Every record of every table at a ref, keyed by (table, id); records without an id are skipped."""
    out = {}
    for table, path in TABLES.items():
        if path.endswith('.json'):
            files = [path]
        else:
            listing = git(repo, 'ls-tree', '--name-only', ref, path + '/').decode().split()
            files = [f for f in listing if f.endswith('.json')]
        for f in files:
            for row in json.loads(git(repo, 'show', f'{ref}:{f}')):
                if row.get('id') is not None:
                    out[(table, int(row['id']))] = row
    return out


def load_ledger(path):
    """Reviewed events keyed by (table, id); a key twice is an error."""
    events = {}
    for n, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        e = json.loads(line)
        key = (e['old_table'], int(e['old_id']))
        if key in events:
            raise MigrationError(f'ledger line {n}: {key} appears twice')
        events[key] = e
    return events


def field_changes(before, after):
    """(field, before, after) for each changed field; translations compared per language as translations.<lang>."""
    out = []
    for k in sorted((set(before) | set(after)) - IGNORED):
        b, a = before.get(k, None), after.get(k, None)
        if k == 'translations' and isinstance(b or {}, dict) and isinstance(a or {}, dict):
            for lang in sorted(set(b or {}) | set(a or {})):
                if (b or {}).get(lang) != (a or {}).get(lang):
                    out.append((f'translations.{lang}', (b or {}).get(lang), (a or {}).get(lang)))
        elif b != a or (k in before) != (k in after):
            out.append((k, b, a))
    return out


def check(old, new, events):
    """Errors for removals the ledger does not explain, bad targets, false redirects and reused ids."""
    errors = []
    for key in sorted(set(old) - set(new)):
        e = events.get(key)
        if e is None:
            errors.append(f'{key[0]} {key[1]} was removed but has no ledger event')
            continue
        if e.get('review_status') != 'reviewed' or e.get('outcome') not in OUTCOMES:
            errors.append(f"{key[0]} {key[1]}: event not reviewed or outcome {e.get('outcome')!r} unknown")
        targets = e.get('targets') or []
        if e.get('outcome') in NO_TARGET and targets:
            errors.append(f"{key[0]} {key[1]}: outcome {e['outcome']} must have no targets")
        if e.get('outcome') not in NO_TARGET and not targets:
            errors.append(f"{key[0]} {key[1]}: outcome {e.get('outcome')} needs at least one target")
        for t in targets:
            if (t['table'], int(t['id'])) not in new:
                errors.append(f"{key[0]} {key[1]}: target {t['table']} {t['id']} does not exist in the new snapshot")
        if e.get('automatic_redirect') and e.get('outcome') != 'merged_same_entity':
            errors.append(f"{key[0]} {key[1]}: automatic redirect is allowed only for merged_same_entity")
    for key in sorted(events):
        if key in new and key not in old:
            errors.append(f'{key[0]} {key[1]} is a retired id and is in use again')
    return errors


def build(old, new, events):
    """The release files' content: removed events, CSV rows, changed fields and counts."""
    removed = [events[k] | {'old_table': k[0], 'old_id': k[1]} for k in sorted(set(old) - set(new))]
    rows = []
    for e in removed:
        base = [e['old_table'], e['old_id'], old[(e['old_table'], e['old_id'])].get('name') or old[(e['old_table'], e['old_id'])].get('code'),
                e['outcome'], 'yes' if e.get('automatic_redirect') else 'no']
        rows += [base + [t['table'], t['id'], t['relation']] for t in e.get('targets') or []] or [base + ['', '', '']]
    changed, counts = [], {}
    for key in sorted(set(old) & set(new)):
        for f, b, a in field_changes(old[key], new[key]):
            changed.append({'table': key[0], 'id': key[1], 'field': f, 'before': b, 'after': a})
            counts[f'{key[0]}.{f.split(".")[0]}'] = counts.get(f'{key[0]}.{f.split(".")[0]}', 0) + 1
    per_table = {t: {'removed': sum(1 for k in set(old) - set(new) if k[0] == t),
                     'added': sum(1 for k in set(new) - set(old) if k[0] == t),
                     'changed': len({(c['table'], c['id']) for c in changed if c['table'] == t})} for t in TABLES}
    return removed, rows, changed, per_table, dict(sorted(counts.items()))


def write(out, removed, rows, changed, per_table, field_counts, meta):
    """Write the four files deterministically and return their SHA-256s."""
    out.mkdir(parents=True, exist_ok=True)
    dump = lambda items: ''.join(json.dumps(i, ensure_ascii=False, sort_keys=True) + '\n' for i in items)
    (out / 'removed_ids.jsonl').write_text(dump(removed), encoding='utf-8')
    with open(out / 'removed_ids.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['table', 'old_id', 'name', 'outcome', 'automatic_redirect', 'target_table', 'target_id', 'relation'])
        w.writerows(rows)
    (out / 'changed_fields.jsonl').write_text(dump(changed), encoding='utf-8')
    sums = {n: hashlib.sha256((out / n).read_bytes()).hexdigest() for n in ('removed_ids.jsonl', 'removed_ids.csv', 'changed_fields.jsonl')}
    manifest = meta | {'tables': per_table, 'changed_field_counts': field_counts, 'files': sums}
    (out / 'release_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return sums


def main(argv=None):
    """Compare the two refs, check every removal against the ledger, write the release files."""
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--from', dest='frm', required=True, help='git ref of the previous published release')
    p.add_argument('--to', required=True, help='git ref of this release')
    p.add_argument('--ledger', required=True, help='reviewed events, one JSON object per line')
    p.add_argument('--out', required=True, help='folder for the release files')
    p.add_argument('--repo', default='.', help='repository path (default: current folder)')
    a = p.parse_args(argv)
    try:
        refs = {r: git(a.repo, 'rev-parse', r).decode().strip() for r in (a.frm, a.to)}
        old, new, events = snapshot(a.repo, a.frm), snapshot(a.repo, a.to), load_ledger(a.ledger)
        errors = check(old, new, events)
        if errors:
            raise MigrationError(f'{len(errors)} problem(s):\n  ' + '\n  '.join(errors[:50]))
        removed, rows, changed, per_table, counts = build(old, new, events)
        sums = write(Path(a.out), removed, rows, changed, per_table, counts,
                     {'schema_version': 1, 'from': {'ref': a.frm, 'sha': refs[a.frm]}, 'to': {'ref': a.to, 'sha': refs[a.to]}})
    except (MigrationError, OSError, json.JSONDecodeError, KeyError) as e:
        print(f'[ERROR] {e}', file=sys.stderr)
        return 1
    print(f"[INFO] {sum(t['removed'] for t in per_table.values())} removed, {len(changed)} field changes; files: {', '.join(sums)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
