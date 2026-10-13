#!/usr/bin/env python3
"""Release migration files for a data release (v5 plan section C; decisions_3_final.md, decisions_4_final.md).

Walks the first-parent history of contributions/ between two pinned commits and writes, for consumers:
  removed_ids.jsonl / removed_ids.csv  every id that left the data in the interval (ids created and removed in between
                                       included), with its reviewed event and the targets that stand for it at --to
  added_ids.jsonl                      every id present at --to and not at --from
  identity_changes.jsonl               reviewed identity decisions on ids that kept their number at the time
  changed_fields.jsonl                 every changed field of a record present at both ends, typed, with presence flags
  release_manifest.json                release versions, both commits, totals and counts that reconcile, file SHA-256s
It writes nothing and exits 1 when a removal has no reviewed event at the commit where it happened, an event's parent
commit, path or before-row hash is wrong, a target is wrong or missing at that commit, a redirect is not a reviewed
same-entity merge, a repurposed id still denotes the other entity at --to, an id is missing, malformed or duplicated,
or a retired or reserved id is in use. An output failure keeps the earlier output.

Usage:
  python3 bin/scripts/release/migrations.py --from <published snapshot sha> --to <candidate sha> \\
    --ledger migrations/events.jsonl --reserved migrations/reserved_ids.jsonl --meta release_meta.json --out build/migrations
"""
import argparse
import bisect
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

TABLES = {'countries': 'contributions/countries/countries.json', 'states': 'contributions/states/states.json',
          'counties': 'contributions/counties', 'cities': 'contributions/cities', 'postcodes': 'contributions/postcodes'}
SINGULAR = {'countries': 'country', 'states': 'state', 'counties': 'county', 'cities': 'city', 'postcodes': 'postcode'}
# Left out of changed_fields by policy: bookkeeping columns. The importer keeps the values a file gives and fills
# missing ones; they never describe the place itself.
MANAGED = {'created_at', 'updated_at', 'flag'}
# outcome -> (relations allowed, relation required, fewest distinct targets, most or None)
REMOVAL_OUTCOMES = {
    'merged_same_entity': ({'merged_same_entity'}, 'merged_same_entity', 1, 1),
    'administrative_seat': ({'administrative_seat', 'moved_dataset'}, 'administrative_seat', 1, None),
    'moved_dataset': ({'moved_dataset'}, 'moved_dataset', 1, None),
    'territorial_successor': ({'territorial_successor'}, 'territorial_successor', 1, None),
    'split_into': ({'split_into'}, 'split_into', 2, None),
    'namespace_replaced': (set(), None, 0, 0), 'invalid_record': (set(), None, 0, 0), 'no_successor': (set(), None, 0, 0),
}
IDENTITY_OUTCOMES = {   # decisions_4_final.md
    'classification': (set(), None, 0, 0),                       # the same entity; its category or depth was corrected
    'dual_role': ({'moved_dataset'}, None, 0, None),             # the row stands for a place and its unit; the unit's record
    'repurpose': ({'prior_identity'}, 'prior_identity', 1, None),  # the number came to denote another entity; the earlier one
    'unresolved': (set(), None, 0, 0),                           # what the row first denoted is not established
}
SHA1, SHA256 = re.compile(r'[0-9a-f]{40}'), re.compile(r'[0-9a-f]{64}')
META_KEYS = ('data_version', 'contract_version', 'policy_version', 'data_schema_version')
FORMAT_VERSION = 2
MISSING = object()


class MigrationError(Exception):
    """An input, removal, reference or id the release cannot explain."""


class OutputError(Exception):
    """The release files could not be written; the earlier output, if any, was kept."""


def _reject_constant(name):
    """json parse hook: NaN and Infinity are not JSON."""
    raise ValueError(f'{name} is not a JSON number')


def _finite_float(text):
    """json parse hook: a number too large for a float is refused, not turned into Infinity."""
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f'{text} is out of range')
    return value


def strict_json(text, where):
    """Parse standard JSON only (no NaN, Infinity or overflowing numbers), naming the input on failure."""
    try:
        return json.loads(text, parse_constant=_reject_constant, parse_float=_finite_float)
    except ValueError as err:
        raise MigrationError(f'{where}: invalid JSON: {err}') from err


def positive_id(v):
    """True for a JSON integer above zero (booleans and fractions are not ids)."""
    return type(v) is int and v > 0


def canon(v):
    """Canonical JSON text of a value: typed (1, 1.0 and true differ) and key-order independent."""
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def row_hash(row):
    """SHA-256 of a row's canonical JSON, as recorded in before_row_sha256."""
    return hashlib.sha256(canon(row).encode('utf-8')).hexdigest()


def is_str(v, *allowed):
    """A string, and one of the allowed values when any are given (checked before any set or dict lookup)."""
    return isinstance(v, str) and (not allowed or v in allowed[0])


def relation_table_ok(relation, old_table, table):
    """Whether a target table fits its relation: same-entity, successor and split stay in the table; a seat is a city."""
    if relation in ('merged_same_entity', 'territorial_successor', 'split_into'):
        return table == old_table
    if relation == 'administrative_seat':
        return table == 'cities'
    if relation == 'moved_dataset':
        return table != old_table
    return relation == 'prior_identity'


def evidence_ok(item):
    """A usable evidence object: a research manifest with its SHA-256, or a source URL."""
    return isinstance(item, dict) and (
        (is_str(item.get('manifest')) and bool(item['manifest']) and is_str(item.get('sha256')) and bool(SHA256.fullmatch(item['sha256'])))
        or (is_str(item.get('url')) and item['url'].startswith(('https://', 'http://'))))


def event_errors(e, where):
    """Schema errors of one ledger event, a removal (the default) or an identity event; empty when valid."""
    if not isinstance(e, dict):
        return [f'{where}: not a JSON object']
    errs = []

    def need(ok, msg):
        if not ok:
            errs.append(f'{where}: {msg}')

    kind = e.get('event_type', 'removal')
    need(type(e.get('schema_version')) is int and e['schema_version'] == 1, 'schema_version must be the integer 1')
    need(is_str(kind, ('removal', 'identity')), f'event_type {kind!r} is not removal or identity')
    tkey, ikey = ('old_table', 'old_id') if kind == 'removal' else ('table', 'id')
    need(is_str(e.get(tkey), TABLES), f'{tkey} {e.get(tkey)!r} is not a known table')
    need(positive_id(e.get(ikey)), f'{ikey} must be a positive integer')
    need(is_str(e.get('event_commit')) and bool(SHA1.fullmatch(e['event_commit'])), 'event_commit must be a full commit SHA')
    need(is_str(e.get('before_row_sha256')) and bool(SHA256.fullmatch(e['before_row_sha256'])), 'before_row_sha256 must be a SHA-256')
    if 'before' in e:
        need(isinstance(e['before'], dict) and row_hash(e['before']) == e.get('before_row_sha256'), 'before does not hash to before_row_sha256')
    if kind == 'removal':
        need(is_str(e.get('before_commit')) and bool(SHA1.fullmatch(e['before_commit'])), 'before_commit must be a full commit SHA')
        need(is_str(e.get('before_path')) and e['before_path'].startswith('contributions/'), 'before_path must be a contributions/ path')
    need(is_str(e.get('review_status'), ('reviewed', 'held')), 'review_status must be reviewed or held')
    if e.get('review_status') != 'reviewed' or errs:
        return errs   # a held event is a placeholder: it fails the gate wherever it applies
    review = e.get('review')
    need(isinstance(review, dict) and all(is_str(review.get(k)) and review[k].strip() for k in ('reason', 'reviewer')),
         'a reviewed event needs review.reason and review.reviewer')
    need(isinstance(e.get('evidence'), list) and len(e['evidence']) > 0 and all(evidence_ok(x) for x in e['evidence']),
         'a reviewed event needs evidence: objects with a manifest and its sha256, or a source url')
    need(type(e.get('automatic_redirect')) is bool, 'automatic_redirect must be true or false')
    rules = REMOVAL_OUTCOMES if kind == 'removal' else IDENTITY_OUTCOMES
    outcome, targets = e.get('outcome'), e.get('targets')
    if not is_str(outcome, rules) or not isinstance(targets, list):
        return errs + [f'{where}: outcome {outcome!r} unknown for a {kind} event, or targets not a list (use [] for none)']
    allowed, required, fewest, most = rules[outcome]
    keys = set()
    for t in targets:
        ok = (isinstance(t, dict) and is_str(t.get('table'), TABLES) and positive_id(t.get('id'))
              and is_str(t.get('relation'), allowed) and relation_table_ok(t['relation'], e[tkey], t['table']))
        need(ok, f'target {t!r} needs a known table, a positive integer id and a relation that {outcome} allows for that table')
        if ok:
            keys.add((t['table'], t['id']))
    need(len(keys) == len(targets) or errs, 'targets repeat')
    need((e[tkey], e[ikey]) not in keys, 'an event cannot target its own record')
    need(fewest <= len(keys) and (most is None or len(keys) <= most), f'{outcome} needs {fewest} to {most or "any"} distinct targets')
    need(required is None or any(isinstance(t, dict) and t.get('relation') == required for t in targets), f'{outcome} needs a {required} target')
    need(not e.get('automatic_redirect') or (kind == 'removal' and outcome == 'merged_same_entity'),
         'automatic_redirect is allowed only for a reviewed merged_same_entity removal')
    return errs


def read_jsonl(path, what):
    """Objects of a JSON Lines file, with the line number of any malformed line."""
    out = []
    for n, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            out.append((n, strict_json(line, f'{what} {path} line {n}')))
    return out


def load_ledger(path):
    """Removal and identity events keyed by (table, id, event_commit); any schema error or repeated key fails."""
    removals, identities, errors = {}, {}, []
    for n, e in read_jsonl(path, 'ledger'):
        errs = event_errors(e, f'ledger line {n}')
        if errs:
            errors += errs
            continue
        removal = e.get('event_type', 'removal') == 'removal'
        key = (e['old_table'], e['old_id'], e['event_commit']) if removal else (e['table'], e['id'], e['event_commit'])
        index = removals if removal else identities
        if key in index:
            errors.append(f'ledger line {n}: {key[0]} {key[1]} at {key[2][:12]} appears twice')
        index[key] = e
    if errors:
        raise MigrationError(f'{len(errors)} ledger problem(s):\n  ' + '\n  '.join(errors[:50]))
    return removals, identities


def load_reserved(path):
    """Namespace-qualified ids that left the data before this interval and may never return: {"table", "id"} per line."""
    out = set()
    for n, r in read_jsonl(path, 'reserved ids'):
        if not (isinstance(r, dict) and is_str(r.get('table'), TABLES) and positive_id(r.get('id'))):
            raise MigrationError(f'reserved ids {path} line {n}: needs a known table and a positive integer id')
        out.add((r['table'], r['id']))
    return out


def load_meta(path):
    """Release metadata: the four version strings and a non-empty list of notices (paths or URLs)."""
    meta = strict_json(Path(path).read_text(encoding='utf-8'), f'release metadata {path}')
    bad = [k for k in META_KEYS if not (isinstance(meta, dict) and is_str(meta.get(k)) and meta[k].strip())]
    if bad or not (isinstance(meta.get('notices'), list) and meta['notices'] and all(is_str(x) and x for x in meta['notices'])):
        raise MigrationError(f'release metadata {path}: needs non-empty {", ".join(META_KEYS)} and a list of notices (missing or bad: {bad})')
    return meta


def git(repo, *args):
    """Output of a git command in the repo; raises with git's message on failure."""
    r = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if r.returncode:
        raise MigrationError(f"git {' '.join(args[:3])}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout


def resolve(repo, ref):
    """The commit SHA a ref names, resolved once; every later read uses the SHA, never the movable name."""
    if not ref or ref.startswith('-'):
        raise MigrationError(f'not a git ref: {ref!r}')
    return git(repo, 'rev-parse', '--verify', '--quiet', f'{ref}^{{commit}}').decode().strip()


def first_parent_line(repo, sha, stop=None):
    """Commits on sha's first-parent line, sha included, back to the root or to stop (excluded)."""
    return git(repo, 'rev-list', '--first-parent', sha, *([f'^{stop}'] if stop else [])).decode().split()


def table_of(path):
    """The table a contributions file belongs to, or None (README files, other folders)."""
    for table, p in TABLES.items():
        if p.endswith('.json'):
            if path == p:
                return table
        elif path.startswith(p + '/') and path.endswith('.json') and '/' not in path[len(p) + 1:]:
            return table
    return None


def parse_file(repo, sha, path, strict):
    """Keyed rows and the row numbers of id-less rows of one file at a commit; strict refuses id-less rows."""
    rows = strict_json(git(repo, 'show', f'{sha}:{path}').decode('utf-8'), f'{path} at {sha[:12]}')
    if not isinstance(rows, list) or not all(isinstance(r, dict) for r in rows):
        raise MigrationError(f'{path} at {sha[:12]}: expected an array of objects')
    keyed, pending = [], []
    for n, r in enumerate(rows):
        if r.get('id') is None:
            if strict:
                raise MigrationError(f'{path} row {n} at {sha[:12]}: no id; allocate ids in the source before generating')
            pending.append(n)
        elif not positive_id(r['id']):
            raise MigrationError(f'{path} row {n} at {sha[:12]}: id {r["id"]!r} is not a positive integer')
        else:
            keyed.append(r)
    return keyed, pending


def files_of(repo, sha):
    """Contributions files present at a commit, as sorted (table, path)."""
    listing = git(repo, 'ls-tree', '-r', '--name-only', '-z', sha, '--', 'contributions/').decode().split('\0')
    return sorted((table_of(p), p) for p in listing if p and table_of(p))


class State:
    """The keyed namespace at one commit: rows by (table, id), the file of each key, keys and id-less rows per file."""

    def __init__(self):
        """An empty namespace."""
        self.rows, self.path, self.by_path, self.pending = {}, {}, {}, {}

    def put(self, table, path, rows, pending, sha):
        """Add one file's rows; a key already in this or another file is a duplicate."""
        keys = set()
        for r in rows:
            k = (table, r['id'])
            if k in self.path or k in keys:
                raise MigrationError(f'{table} id {r["id"]} is duplicated: {self.path.get(k, path)} and {path} at {sha[:12]}')
            keys.add(k)
            self.rows[k], self.path[k] = r, path
        self.by_path[path] = keys
        self.pending[path] = (sha, pending)

    def drop(self, path):
        """Remove one file's rows; returns {key: (path, row)}."""
        self.pending.pop(path, None)
        return {k: (self.path.pop(k), self.rows.pop(k)) for k in self.by_path.pop(path, set())}


def snapshot(repo, sha):
    """The full namespace at a commit (strict: every row has a valid, unique id)."""
    s = State()
    for t, path in files_of(repo, sha):
        rows, _ = parse_file(repo, sha, path, strict=True)
        s.put(t, path, rows, [], sha)
    return s


def walk(repo, frm, to, on_commit, progress=None):
    """Apply each first-parent commit's contributions changes to the --from namespace, calling
    on_commit(index, sha, parent, removed, added, before, state) after each; returns the start rows and the final state."""
    lines = git(repo, 'rev-list', '--first-parent', '--reverse', '--parents', f'{frm}..{to}').decode().split('\n')
    commits = [ln.split() for ln in lines if ln.strip()]
    state = snapshot(repo, frm)
    start = dict(state.rows)
    parent = frm
    for i, (c, first_parent, *_) in enumerate(commits, 1):
        if first_parent != parent:
            raise MigrationError(f'--from {frm[:12]} is not on the first-parent history of --to {to[:12]}')
        raw = git(repo, 'diff', '--name-status', '--no-renames', '-z', parent, c, '--', 'contributions/').decode().split('\0')
        changed = [(s, p) for s, p in zip(raw[0::2], raw[1::2]) if table_of(p)]
        before = {}
        for _, p in changed:
            before.update(state.drop(p))
        new_keys = set()
        for status, p in changed:
            if status != 'D':
                state.put(table_of(p), p, *parse_file(repo, c, p, strict=False), c)
                new_keys |= state.by_path[p]
        on_commit(i, c, parent, sorted(before.keys() - new_keys), sorted(new_keys - before.keys()), before, state)
        parent = c
        if progress and (i % 25 == 0 or i == len(commits)):
            progress(f'{i}/{len(commits)} commits')
    if parent != to:
        raise MigrationError(f'--to {to[:12]} does not descend from --from {frm[:12]}')
    left = [f'{p} row {n} (since {sha[:12]})' for p, (sha, rows) in sorted(state.pending.items()) for n in rows]
    if left:
        raise MigrationError(f'{len(left)} rows have no id at --to; allocate ids in the source before generating: ' + '; '.join(left[:20]))
    return start, state


class Gate:
    """Checks each commit's removals, additions and identity events against the ledger and reserved ids, and keeps a
    timeline of every event per key for target resolution."""

    def __init__(self, removals, identities, retired):
        """Events in the interval, keyed (table, id, commit), and every id that may not appear again."""
        self.removals, self.identities, self.retired = removals, identities, set(retired)
        self.errors, self.used, self.events, self.identity, self.added_at = [], set(), [], [], {}
        self.timeline = defaultdict(list)   # key -> [(commit index, kind, event)] in history order
        self.identity_at = defaultdict(list)
        for key, e in identities.items():
            self.identity_at[key[2]].append((key, e))

    def __call__(self, i, c, parent, removed, added, before, state):
        """Check one commit after it has been applied to the namespace."""
        err = self.errors.append
        for k in added:
            if k in self.retired:
                err(f'{k[0]} {k[1]} is a retired or reserved id and is in use again at {c[:12]}')
            self.added_at[k] = c
        for k in removed:
            self.retired.add(k)
            path, row = before[k]
            e = self.removals.get((k[0], k[1], c))
            if e is None:
                err(f'{k[0]} {k[1]} was removed at {c[:12]} but has no ledger event for that commit')
                continue
            self.used.add((k[0], k[1], c))
            if e['review_status'] != 'reviewed':
                err(f'{k[0]} {k[1]} at {c[:12]}: the event is {e["review_status"]}, not reviewed')
                continue
            if e['before_commit'] != parent or e['before_path'] != path:
                err(f'{k[0]} {k[1]} at {c[:12]}: event before {e["before_commit"][:12]} {e["before_path"]}, actual {parent[:12]} {path}')
            if row_hash(row) != e['before_row_sha256']:
                err(f'{k[0]} {k[1]} at {c[:12]}: before_row_sha256 does not match the removed row')
            for t in e['targets']:
                if (t['table'], t['id']) not in state.rows:
                    err(f'{k[0]} {k[1]} at {c[:12]}: target {t["table"]} {t["id"]} does not exist after that commit')
            self.events.append((k, c, e, row))
            self.timeline[k].append((i, 'removal', e))
        for key, e in self.identity_at.get(c, []):
            k = key[:2]
            self.used.add(('identity',) + key)
            if e['review_status'] != 'reviewed':
                err(f'{k[0]} {k[1]} at {c[:12]}: the identity event is {e["review_status"]}, not reviewed')
            elif k not in before or k not in state.rows or canon(before[k][1]) == canon(state.rows[k]):
                err(f'{k[0]} {k[1]} at {c[:12]}: identity event, but the record did not change there while keeping its id')
            elif row_hash(before[k][1]) != e['before_row_sha256']:
                err(f'{k[0]} {k[1]} at {c[:12]}: identity before_row_sha256 does not match')
            else:
                for t in e['targets']:
                    if (t['table'], t['id']) not in state.rows:
                        err(f'{k[0]} {k[1]} at {c[:12]}: identity target {t["table"]} {t["id"]} does not exist after that commit')
                self.identity.append((k, c, e, before[k][1], state.rows[k]))
                self.timeline[k].append((i, 'identity', e))

    def next_event(self, key, after):
        """The first event on a key at a commit later than the given index, or None."""
        events = self.timeline.get(key, [])
        n = bisect.bisect_right([x[0] for x in events], after)
        return events[n] if n < len(events) else None


def resolve_targets(gate, final, targets, index, auto):
    """Follow targets forward in history to what stands for them at --to, without recursion. A removal passes to its
    targets; a repurpose passes to the entity the number used to denote (prior_identity), never redirecting
    automatically; an unresolved identity keeps the key but ends any automatic redirect. A path that ends in a
    removal with no successor is reported with that outcome."""
    out, stack, steps = [], [(t, index, [t['relation']], auto) for t in reversed(targets)], 0
    limit = 4 * (sum(len(v) for v in gate.timeline.values()) + len(targets)) + 16
    while stack:
        steps += 1
        if steps > limit:
            raise MigrationError('a target chain does not end; check the ledger for cycles')
        t, at, relations, redirect = stack.pop()
        key = (t['table'], t['id'])
        nxt = gate.next_event(key, at)
        if nxt is None:
            if key in final:
                out.append({'table': key[0], 'id': key[1], 'relations': relations, 'automatic_redirect': redirect})
            continue
        i, kind, e = nxt
        if kind == 'removal':
            if not e['targets']:
                out.append({'table': None, 'id': None, 'end': e['outcome'], 'relations': relations, 'automatic_redirect': False})
            for t2 in reversed(e['targets']):
                stack.append((t2, i, relations + [t2['relation']], redirect and e['automatic_redirect']))
        elif e['outcome'] == 'repurpose':
            for t2 in reversed(e['targets']):
                stack.append((t2, i, relations + ['prior_identity'], False))
        else:
            stack.append((t, i, relations, redirect and e['outcome'] != 'unresolved'))
    return out


def delta(field, b, a):
    """A one-item list describing a typed, presence-aware change of one field, or [] when equal."""
    if (b is MISSING) == (a is MISSING) and (b is MISSING or canon(b) == canon(a)):
        return []
    return [{'field': field, 'before': None if b is MISSING else b, 'after': None if a is MISSING else a,
             'before_present': b is not MISSING, 'after_present': a is not MISSING}]


def field_changes(before, after):
    """Changed public fields of one record; translations compared per language when both sides are objects."""
    out = []
    for k in sorted((before.keys() | after.keys()) - MANAGED):
        b, a = before.get(k, MISSING), after.get(k, MISSING)
        if k == 'translations' and isinstance(b, dict) and isinstance(a, dict):
            for lang in sorted(b.keys() | a.keys()):
                out += delta(f'translations.{lang}', b.get(lang, MISSING), a.get(lang, MISSING))
        else:
            out += delta(k, b, a)
    return out


def label(row):
    """A record's name, or its code for postcodes."""
    return row.get('name') or row.get('code') or ''


def build(start, state, gate, order):
    """The release files' content: removed events, CSV rows, added ids, identity events, changed fields and counts."""
    final = state.rows
    removed = []
    for k, c, e, row in gate.events:
        removed.append({**e, 'before': row, 'present_at_from': k in start, 'present_at_to': False,
                        'current_targets': resolve_targets(gate, final, e['targets'], order[c], e['automatic_redirect'])})
    identity = []
    for k, c, e, before, after in gate.identity:
        later = gate.next_event(k, order[c])
        while later and later[1] != 'removal':
            later = gate.next_event(k, later[0])
        remediation = None
        if later:
            r = later[2]
            remediation = {'event_commit': r['event_commit'], 'outcome': r['outcome'],
                           'current_targets': resolve_targets(gate, final, r['targets'], later[0], r['automatic_redirect'])}
        identity.append({**e, 'before': before, 'after': after, 'present_at_to': k in final, 'remediation': remediation,
                         'current_targets': resolve_targets(gate, final, e['targets'], order[c], False)})
    rows = []
    for r in removed:
        b, t = r['before'], r['old_table']
        base = [SINGULAR[t], r['old_id'], label(b), b.get('country_code', b.get('iso2') if t == 'countries' else '') or '',
                b.get('state_code', b.get('iso2') if t == 'states' else '') or '', r['outcome']]
        tail = [r.get('event_pr_url') or '']
        rows += [base + [ct['table'] or '', ct['id'] or ''] + tail + ['>'.join(ct['relations']), 'yes' if ct['automatic_redirect'] else 'no', r['event_commit']]
                 for ct in r['current_targets']] or [base + ['', ''] + tail + ['', 'no', r['event_commit']]]
    added = [{'table': k[0], 'id': k[1], 'name': label(final[k]), 'path': state.path[k], 'added_commit': gate.added_at.get(k)}
             for k in sorted(final.keys() - start.keys())]
    changed, counts = [], Counter()
    for k in sorted(start.keys() & final.keys()):
        if start[k] is final[k]:
            continue   # the file was never rewritten in the interval
        for d in field_changes(start[k], final[k]):
            changed.append({'table': k[0], 'id': k[1], **d})
            counts[f'{k[0]}.{d["field"]}'] += 1
    per_table = {}
    for t in TABLES:
        n_from, n_to = sum(1 for k in start if k[0] == t), sum(1 for k in final if k[0] == t)
        n_removed = sum(1 for k in start.keys() - final.keys() if k[0] == t)
        n_added = sum(1 for a in added if a['table'] == t)
        if n_from - n_removed + n_added != n_to:
            raise MigrationError(f'{t}: counts do not reconcile ({n_from} - {n_removed} + {n_added} != {n_to})')
        per_table[t] = {'from_total': n_from, 'to_total': n_to, 'removed': n_removed, 'added': n_added,
                        'changed_records': len({c['id'] for c in changed if c['table'] == t}),
                        'removal_events': sum(1 for r in removed if r['old_table'] == t),
                        'identity_events': sum(1 for x in identity if x['table'] == t),
                        'created_and_removed_in_interval': sum(1 for r in removed if r['old_table'] == t and not r['present_at_from'])}
    return removed, rows, added, identity, changed, per_table, dict(sorted(counts.items()))


CSV_HEADER = ['record', 'old_id', 'name', 'country_code', 'state_code', 'outcome', 'new_table', 'new_id', 'source',
              'relation', 'automatic_redirect', 'event_commit']   # v4.0's nine columns, then three appended
NAMES = ('removed_ids.jsonl', 'removed_ids.csv', 'added_ids.jsonl', 'identity_changes.jsonl', 'changed_fields.jsonl')


def write(out, removed, rows, added, identity, changed, per_table, field_counts, head):
    """Write the six files into a staging folder, then swap it in for the output folder; on any failure the earlier
    output stays as it was. Returns the SHA-256 of each data file."""
    out = Path(out)
    staging, previous = out.parent / f'.{out.name}.staging', out.parent / f'.{out.name}.previous'
    dump = lambda items: ''.join(json.dumps(i, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n' for i in items)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        for leftover in (staging, previous):
            if leftover.exists():
                shutil.rmtree(leftover)   # only this tool's own working folders, from an interrupted run
        staging.mkdir()
        (staging / 'removed_ids.jsonl').write_text(dump(removed), encoding='utf-8')
        with open(staging / 'removed_ids.csv', 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f, lineterminator='\n')
            w.writerow(CSV_HEADER)
            w.writerows(rows)
        (staging / 'added_ids.jsonl').write_text(dump(added), encoding='utf-8')
        (staging / 'identity_changes.jsonl').write_text(dump(identity), encoding='utf-8')
        (staging / 'changed_fields.jsonl').write_text(dump(changed), encoding='utf-8')
        sums = {n: hashlib.sha256((staging / n).read_bytes()).hexdigest() for n in NAMES}
        manifest = {**head, 'tables': per_table, 'changed_field_counts': field_counts, 'files': sums}
        (staging / 'release_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
        if out.exists():
            os.replace(out, previous)
        try:
            os.replace(staging, out)
        except OSError:
            if previous.exists() and not out.exists():
                os.replace(previous, out)
            raise
        if previous.exists():
            shutil.rmtree(previous)
        return sums
    except (OSError, ValueError) as err:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise OutputError(f'could not write {out}: {err}') from err


def place_commits(repo, frm, to, commits):
    """For each event commit: 'in' the interval, 'before' it or 'after' it on the release's first-parent line;
    anything else (a side branch, a divergent line, an unknown commit) is refused."""
    interval = set(first_parent_line(repo, to, frm))
    line_before = set(first_parent_line(repo, frm))
    place, off = {}, []
    for c in sorted(commits):
        if c in interval:
            place[c] = 'in'
        elif c in line_before:
            place[c] = 'before'
        else:
            r = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', f'{c}^{{commit}}'], capture_output=True)
            if r.returncode == 0 and to in first_parent_line(repo, c, to + '^'):
                place[c] = 'after'
            else:
                off.append(c)
    if off:
        raise MigrationError('event commits not on the release line (first-parent history of --to or a later release): '
                             + ', '.join(c[:12] for c in off))
    return interval, place


def verify_earlier(repo, removals, identities):
    """Check events before --from against history, commit by commit, reading only the files each commit changed (an id
    that leaves one file can only reappear in a file the same commit changed): a removal's parent, path and before-row
    hash must match and the id must be gone at its commit; an identity event's record must have changed there.
    Rows without an id yet, allowed in history, are skipped."""
    errors, by_commit = [], defaultdict(list)
    for key, e in list(removals.items()) + list(identities.items()):
        by_commit[key[2]].append((key, e))
    for c, items in sorted(by_commit.items()):
        parent = git(repo, 'rev-parse', f'{c}^1').decode().strip()
        raw = git(repo, 'diff', '--name-status', '--no-renames', '-z', parent, c, '--', 'contributions/').decode().split('\0')
        changed = [(s, p) for s, p in zip(raw[0::2], raw[1::2]) if table_of(p)]
        then, now = {}, {}
        for status, path in changed:
            if status != 'A':
                then.update({(table_of(path), r['id']): (path, r) for r in parse_file(repo, parent, path, strict=False)[0]})
            if status != 'D':
                now.update({(table_of(path), r['id']): (path, r) for r in parse_file(repo, c, path, strict=False)[0]})
        for key, e in items:
            k = key[:2]
            if e.get('event_type', 'removal') == 'removal':
                if e['before_commit'] != parent:
                    errors.append(f"{k[0]} {k[1]} at {c[:12]}: before_commit is not the commit's first parent")
                elif k not in then or then[k][0] != e['before_path'] or row_hash(then[k][1]) != e['before_row_sha256']:
                    errors.append(f'{k[0]} {k[1]} at {c[:12]}: the before row, path or hash does not match history')
                elif k in now:
                    errors.append(f'{k[0]} {k[1]} at {c[:12]}: the id was not removed at that commit')
            elif k not in then or k not in now or row_hash(then[k][1]) != e['before_row_sha256'] or canon(then[k][1]) == canon(now[k][1]):
                errors.append(f'{k[0]} {k[1]} at {c[:12]}: the identity event does not match history')
    return errors


def generate(repo, frm_ref, to_ref, ledger, reserved_path, meta_path, out, log=lambda m: None):
    """Validate the inputs, walk the history, check every event and write the files; raises MigrationError on any
    problem in the inputs or the history, OutputError when the files cannot be written."""
    removals, identities = load_ledger(ledger)
    reserved, meta = load_reserved(reserved_path), load_meta(meta_path)
    frm, to = resolve(repo, frm_ref), resolve(repo, to_ref)
    interval, place = place_commits(repo, frm, to, {k[2] for k in removals} | {k[2] for k in identities})
    earlier_r = {k: e for k, e in removals.items() if place[k[2]] == 'before'}
    earlier_i = {k: e for k, e in identities.items() if place[k[2]] == 'before'}
    log(f'checking {len(earlier_r)} earlier removal and {len(earlier_i)} earlier identity events against history')
    errors = verify_earlier(repo, {k: e for k, e in earlier_r.items() if e['review_status'] == 'reviewed'},
                            {k: e for k, e in earlier_i.items() if e['review_status'] == 'reviewed'})
    retired = set(reserved) | {k[:2] for k in earlier_r}
    repurposed = {k[:2]: k[2] for k, e in identities.items() if place[k[2]] in ('before', 'in') and e.get('outcome') == 'repurpose'}
    gate = Gate({k: e for k, e in removals.items() if place[k[2]] == 'in'}, {k: e for k, e in identities.items() if place[k[2]] == 'in'}, retired)
    order = {}
    log(f'walking {len(interval)} commits from {frm[:12]} to {to[:12]}')

    def on_commit(i, c, *rest):
        """Remember each commit's position, then run the gate on it."""
        order[c] = i
        gate(i, c, *rest)

    start, state = walk(repo, frm, to, on_commit, progress=log)
    errors += gate.errors + [f'{k[0]} {k[1]} is retired or reserved but present at --from' for k in sorted(retired & start.keys())]
    errors += [f'{k[0]} {k[1]}: event at {k[2][:12]}, but no such removal happened at that commit'
               for k in sorted(gate.removals.keys() - gate.used)]
    errors += [f'{k[0]} {k[1]}: identity event at {k[2][:12]} was not checked' for k in sorted(gate.identities) if ('identity',) + k not in gate.used]
    errors += [f'{k[0]} {k[1]} was repurposed at {c[:12]} and still denotes the other entity at --to; retire it with its earlier '
               f'identity and give that entity a fresh id' for k, c in sorted(repurposed.items()) if k in state.rows]
    if errors:
        raise MigrationError(f'{len(errors)} problem(s):\n  ' + '\n  '.join(errors[:50]) + ('\n  ...' if len(errors) > 50 else ''))
    content = build(start, state, gate, order)
    head = {'migration_format_version': FORMAT_VERSION, 'release': meta, 'from': {'ref': frm_ref, 'sha': frm},
            'to': {'ref': to_ref, 'sha': to}, 'first_parent_commits': len(interval), 'managed_fields_excluded': sorted(MANAGED)}
    return content, write(out, *content, head)


def main(argv=None):
    """Command line entry: exit 0 with the files written, or 1 with the problems and the earlier output kept."""
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--from', dest='frm', required=True, help='commit of the previous successful published snapshot')
    p.add_argument('--to', required=True, help='commit of this release candidate')
    p.add_argument('--ledger', required=True, help='reviewed events, one JSON object per line (migrations/events.jsonl)')
    p.add_argument('--reserved', required=True, help='ids retired before --from, {"table","id"} per line')
    p.add_argument('--meta', required=True, help='release metadata JSON: versions and notices')
    p.add_argument('--out', required=True, help='folder for the release files')
    p.add_argument('--repo', default='.', help='repository path with full history (default: current folder)')
    a = p.parse_args(argv)
    try:
        content, sums = generate(a.repo, a.frm, a.to, a.ledger, a.reserved, a.meta, a.out,
                                 log=lambda m: print(f'[INFO] {m}', file=sys.stderr))
    except MigrationError as err:
        print(f'[ERROR] {err}\nFix the ledger, reserved ids or source named above and run again; nothing was written.', file=sys.stderr)
        return 1
    except OutputError as err:
        print(f'[ERROR] {err}\nThe earlier output, if any, was kept; check the folder and free space, then run again.', file=sys.stderr)
        return 1
    except OSError as err:
        print(f'[ERROR] cannot read an input: {err}\nCheck the paths given; nothing was written.', file=sys.stderr)
        return 1
    removed, _, added, identity, changed, _, _ = content
    print(f'[INFO] {len(removed)} removal events, {len(added)} added, {len(identity)} identity events, '
          f'{len(changed)} field changes; files: {", ".join(sums)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
