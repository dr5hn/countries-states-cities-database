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
same-entity merge, a repurposed id still denotes the other entity at --to or is retired without naming the other
entity's replacement, an id is missing, malformed or duplicated, or a retired or reserved id is in use without a
reviewed restoration of the same entity. Events before --from get the same checks. An output failure keeps the
earlier output.

Usage:
  python3 bin/scripts/release/migrations.py --from <published snapshot sha> --to <candidate sha> \\
    --ledger migrations/events.jsonl --reserved migrations/reserved_ids.jsonl --meta release_meta.json --out build/migrations
"""
import argparse
import bisect
import csv
import functools
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

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
EVENT_TYPES = ('removal', 'identity', 'restoration')
REPLACEMENT_KINDS = ('fresh', 'existing')   # the other entity of a repurposed id: a never-used id, or a proved existing one
STABLE_IDS = ('wikiDataId', 'iso3166_2', 'iso3')   # identifiers of the entity itself; a restoration binds at least one
EXPANSION_LIMIT = 1_000_000   # target paths visited from one record; real chains are short, branching ones can multiply
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
    """A usable evidence object: {"manifest": <non-blank path>, "sha256": <its SHA-256>}, or {"url": <http(s) URL with a
    host>}. Only the shape is checked; sources are never fetched."""
    if not isinstance(item, dict):
        return False
    if is_str(item.get('manifest')) and item['manifest'].strip():
        return is_str(item.get('sha256')) and bool(SHA256.fullmatch(item['sha256']))
    url = item.get('url')
    if not is_str(url) or any(ch.isspace() for ch in url):
        return False
    try:
        parts = urlsplit(url)
        return parts.scheme in ('https', 'http') and bool(parts.hostname)
    except ValueError:
        return False


def key_ok(t):
    """A {"table", "id"} object naming a known table and a positive integer id."""
    return isinstance(t, dict) and is_str(t.get('table'), TABLES) and positive_id(t.get('id'))


def event_errors(e, where):
    """Schema errors of one ledger event: a removal (the default), an identity event or a restoration; empty when valid."""
    if not isinstance(e, dict):
        return [f'{where}: not a JSON object']
    errs = []

    def need(ok, msg):
        if not ok:
            errs.append(f'{where}: {msg}')

    kind = e.get('event_type', 'removal')
    sha1 = lambda k: is_str(e.get(k)) and bool(SHA1.fullmatch(e[k]))
    sha256 = lambda k: is_str(e.get(k)) and bool(SHA256.fullmatch(e[k]))
    need(type(e.get('schema_version')) is int and e['schema_version'] == 1, 'schema_version must be the integer 1')
    if not is_str(kind, EVENT_TYPES):
        return errs + [f'{where}: event_type {kind!r} is not one of {", ".join(EVENT_TYPES)}']
    tkey, ikey = ('old_table', 'old_id') if kind == 'removal' else ('table', 'id')
    need(is_str(e.get(tkey), TABLES), f'{tkey} {e.get(tkey)!r} is not a known table')
    need(positive_id(e.get(ikey)), f'{ikey} must be a positive integer')
    need(sha1('event_commit'), 'event_commit must be a full commit SHA')
    if kind == 'restoration':
        need(sha1('retirement_commit'), 'retirement_commit must be a full commit SHA')
        need(sha256('retired_row_sha256') and sha256('restored_row_sha256'), 'retired_row_sha256 and restored_row_sha256 must be SHA-256s')
        same = e.get('same_identity')
        need(isinstance(same, dict) and any(k in STABLE_IDS for k in same) and all(
            k not in MANAGED | {'id'} and ((is_str(v) and v.strip()) or positive_id(v)) for k, v in same.items()),
            f'same_identity must bind at least one of {", ".join(STABLE_IDS)}, each field (not id or managed fields) '
            'mapped to the nonblank string or integer both rows hold')
    else:
        need(sha256('before_row_sha256'), 'before_row_sha256 must be a SHA-256')
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
         'a reviewed event needs evidence: objects with a manifest and its sha256, or an http(s) url with a host')
    if 'prior_entity' in e:
        need(kind == 'identity' and e.get('outcome') == 'repurpose', 'prior_entity is only for a repurpose identity')
    if kind == 'restoration':
        return errs
    need(type(e.get('automatic_redirect')) is bool, 'automatic_redirect must be true or false')
    rules = REMOVAL_OUTCOMES if kind == 'removal' else IDENTITY_OUTCOMES
    outcome, targets = e.get('outcome'), e.get('targets')
    if not is_str(outcome, rules) or not isinstance(targets, list):
        return errs + [f'{where}: outcome {outcome!r} unknown for a {kind} event, or targets not a list (use [] for none)']
    allowed, required, fewest, most = rules[outcome]
    if 'prior_entity' in e:
        prior = e['prior_entity']
        no_record = kind == 'identity' and outcome == 'repurpose' and not targets
        need(no_record, 'prior_entity is allowed only on a repurpose identity with targets []')
        need(isinstance(prior, dict) and is_str(prior.get('status'), ('ended', 'unrecorded'))
             and is_str(prior.get('reason')) and bool(prior['reason'].strip())
             and isinstance(prior.get('evidence'), list) and bool(prior['evidence'])
             and all(evidence_ok(x) for x in prior['evidence']),
             'prior_entity needs status ended or unrecorded, a nonblank reason and usable evidence')
        if isinstance(prior, dict) and 'recorded_later' in prior:
            later = prior['recorded_later']
            need(prior.get('status') == 'unrecorded' and isinstance(later, dict)
                 and is_str(later.get('event_commit')) and bool(SHA1.fullmatch(later['event_commit']))
                 and key_ok(later.get('target')) and (later['target']['table'], later['target']['id']) != (e[tkey], e[ikey])
                 and is_str(later.get('row_sha256')) and bool(SHA256.fullmatch(later['row_sha256'])),
                 'recorded_later needs an unrecorded prior entity, event_commit, a different target and row_sha256')
        if no_record:
            required, fewest = None, 0
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
    if 'retires_repurpose' in e:
        fix = e['retires_repurpose']
        ok = (kind == 'removal' and isinstance(fix, dict) and is_str(fix.get('identity_event_commit'))
              and bool(SHA1.fullmatch(fix['identity_event_commit'])) and key_ok(fix.get('replacement'))
              and is_str(fix.get('replacement_kind'), REPLACEMENT_KINDS))
        need(ok, 'retires_repurpose needs identity_event_commit, replacement {table, id} and replacement_kind fresh or existing')
        if ok:
            need((fix['replacement']['table'], fix['replacement']['id']) in keys, 'the replacement must be one of the targets')
            need(e.get('automatic_redirect') is False, 'the removal that retires a repurposed id cannot redirect automatically')
    return errs


def read_utf8(path, what):
    """A file's text; bytes that are not UTF-8 are refused with the file named."""
    try:
        return Path(path).read_bytes().decode('utf-8')
    except UnicodeDecodeError as err:
        raise MigrationError(f'{what} {path}: not UTF-8 ({err.reason} at byte {err.start})') from err


def read_jsonl(path, what):
    """Objects of a JSON Lines file, with the line number of any malformed line."""
    out = []
    for n, line in enumerate(read_utf8(path, what).splitlines(), 1):
        if line.strip():
            out.append((n, strict_json(line, f'{what} {path} line {n}')))
    return out


def load_ledger(path):
    """Removal, identity and restoration events, each keyed by (table, id, event_commit); any schema error or repeated
    key fails."""
    index, errors = {kind: {} for kind in EVENT_TYPES}, []
    for n, e in read_jsonl(path, 'ledger'):
        errs = event_errors(e, f'ledger line {n}')
        if errs:
            errors += errs
            continue
        kind = e.get('event_type', 'removal')
        key = (e['old_table'], e['old_id'], e['event_commit']) if kind == 'removal' else (e['table'], e['id'], e['event_commit'])
        if key in index[kind]:
            errors.append(f'ledger line {n}: {kind} of {key[0]} {key[1]} at {key[2][:12]} appears twice')
        index[kind][key] = e
    if errors:
        raise MigrationError(f'{len(errors)} ledger problem(s):\n  ' + '\n  '.join(errors[:50]))
    return index['removal'], index['identity'], index['restoration']


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
    meta = strict_json(read_utf8(path, 'release metadata'), f'release metadata {path}')
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


def top_level(repo):
    """The repository's top folder. git resolves pathspecs such as contributions/ from the working folder, so every
    read runs from the top: a --repo inside the repository would otherwise list no files and write empty releases."""
    return git(repo, 'rev-parse', '--show-toplevel').decode().strip()


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
    try:
        text = git(repo, 'show', f'{sha}:{path}').decode('utf-8')
    except UnicodeDecodeError as err:
        raise MigrationError(f'{path} at {sha[:12]}: not UTF-8 ({err.reason} at byte {err.start})') from err
    rows = strict_json(text, f'{path} at {sha[:12]}')
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


def snapshot(repo, sha, table=None):
    """The namespace at a commit, of one table or all. Rows without an id yet are kept as pending: history may have them."""
    s = State()
    for t, path in files_of(repo, sha):
        if table in (None, t):
            s.put(t, path, *parse_file(repo, sha, path, strict=False), sha)
    return s


@functools.lru_cache(maxsize=4)
def table_rows(repo, sha, table):
    """The rows of one table at a commit, read once per (commit, table) for restorations; callers must not change them."""
    return snapshot(repo, sha, table).rows


def idless(state):
    """Rows still without an id, named by file, row and the commit that last wrote the file."""
    return [f'{p} row {n} (since {sha[:12]})' for p, (sha, rows) in sorted(state.pending.items()) for n in rows]


def retired_row(repo, commit, key, later):
    """The row of key removed at commit, which must come before later on later's first-parent line. The key's whole
    table is read on both sides, so a copy left in another file is seen, and a duplicate id is refused."""
    if commit == later or commit not in first_parent_line(repo, later):
        raise MigrationError(f'retirement_commit {commit[:12]} is not earlier on the first-parent line')
    then = table_rows(repo, git(repo, 'rev-parse', f'{commit}^1').decode().strip(), key[0])
    if key not in then or key in table_rows(repo, commit, key[0]):
        raise MigrationError(f'{key[0]} {key[1]} was not removed at retirement_commit {commit[:12]}')
    return then[key]


def walk(repo, base, frm, to, on_commit, progress=None):
    """Apply each first-parent commit after base, up to --to, to the namespace at base, calling
    on_commit(index, sha, parent, removed, added, before, state) after each. base is --from, or an earlier commit on its
    first-parent line when earlier events must be checked. Returns the rows at --from and the final state; every row
    must have its id at --from and at --to."""
    lines = git(repo, 'rev-list', '--first-parent', '--reverse', '--parents', f'{base}..{to}').decode().split('\n')
    commits = [ln.split() for ln in lines if ln.strip()]
    state, start = snapshot(repo, base), None

    def at_from():
        """The rows at --from, which must all have their ids."""
        left = idless(state)
        if left:
            raise MigrationError(f'{len(left)} rows have no id at --from {frm[:12]}: ' + '; '.join(left[:20]))
        return dict(state.rows)

    if base == frm:
        start = at_from()
    parent = base
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
        if c == frm:
            start = at_from()
        if progress and (i % 25 == 0 or i == len(commits)):
            progress(f'{i}/{len(commits)} commits')
    if parent != to or start is None:
        raise MigrationError(f'--to {to[:12]} does not descend from --from {frm[:12]} on its first-parent line')
    left = idless(state)
    if left:
        raise MigrationError(f'{len(left)} rows have no id at --to; allocate ids in the source before generating: ' + '; '.join(left[:20]))
    return start, state


class Gate:
    """Checks each commit's removals, additions and events against the ledger. Before --from it checks the events,
    and an id a reviewed removal retired may not return unless a reviewed restoration brings it back; inside the
    interval every removal also needs its event, and the same holds for reserved ids. Keeps a timeline of removal,
    identity and restoration events per key for target resolution."""

    def __init__(self, removals, identities, restorations=None, reserved=(), interval=(), repo=None):
        """Events keyed (table, id, commit), ids reserved at --from, the interval's commits and the repository."""
        self.removals, self.identities, self.restorations = removals, identities, restorations or {}
        self.reserved, self.retired, self.interval, self.repo = frozenset(reserved), set(), set(interval), repo
        self.errors, self.used, self.events, self.identity = [], set(), [], []
        self.added_at, self.restored, self.repurposed, self.remediated = {}, {}, {}, {}
        self.first_seen, self.removed_ever = {}, set()   # first addition in the walk, and every id the walk saw removed
        self.prior_records = {}   # identity key -> (later representation index, target) validated against that commit
        self.latest_removal = {}   # key -> the commit of its latest disappearance in the walk
        self.timeline = defaultdict(list)   # key -> [(commit index, kind, event)] in history order
        self.at = defaultdict(list)         # commit -> [(kind, key, event)] for identity and restoration events
        for kind, events in (('identity', identities), ('restoration', self.restorations)):
            for key, e in events.items():
                self.at[key[2]].append((kind, key, e))
                later = recorded_later_of(e)
                if later:
                    self.at[later['event_commit']].append(('prior_representation', key, e))

    def __call__(self, i, c, parent, removed, added, before, state):
        """Check one commit after it has been applied to the namespace."""
        inside, err = c in self.interval, self.errors.append
        restored_here = set()
        for kind, key, e in self.at.get(c, []):
            if kind == 'restoration' and self.restoration_ok(i, c, key, e, added, state):
                restored_here.add(key[:2])
        for k in added:
            if (k in self.retired or (inside and k in self.reserved)) and k not in restored_here:
                err(f'{k[0]} {k[1]} is a retired or reserved id and is in use again at {c[:12]}')
            self.added_at[k] = (i, c)
            self.first_seen.setdefault(k, (i, c))
        for k in removed:
            self.removed_ever.add(k)
            self.latest_removal[k] = c
            e = self.removals.get((k[0], k[1], c))
            if inside or e is not None or k in self.restored:   # a restored id that leaves again needs a new restoration
                self.retired.add(k)
            if e is None:
                if inside or k in self.repurposed:
                    err(f'{k[0]} {k[1]} was removed at {c[:12]} but has no ledger event for that commit')
                self.repurposed.pop(k, None)
                continue
            self.used.add((k[0], k[1], c))
            if e['review_status'] != 'reviewed':
                err(f'{k[0]} {k[1]} at {c[:12]}: the event is {e["review_status"]}, not reviewed')
                continue
            path, row = before[k]
            if e['before_commit'] != parent or e['before_path'] != path:
                err(f'{k[0]} {k[1]} at {c[:12]}: event before {e["before_commit"][:12]} {e["before_path"]}, actual {parent[:12]} {path}')
            if row_hash(row) != e['before_row_sha256']:
                err(f'{k[0]} {k[1]} at {c[:12]}: before_row_sha256 does not match the removed row')
            for t in e['targets']:
                if (t['table'], t['id']) not in state.rows:
                    err(f'{k[0]} {k[1]} at {c[:12]}: target {t["table"]} {t["id"]} does not exist after that commit')
            self.retirement_ok(i, c, k, e)
            self.events.append((k, c, e, row, inside))
            self.timeline[k].append((i, 'removal', e))
        for kind, key, e in self.at.get(c, []):
            if kind != 'identity':
                continue
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
                if e['outcome'] == 'repurpose':
                    if k in self.repurposed:
                        err(f'{k[0]} {k[1]} at {c[:12]}: repurposed again while the repurpose at {self.repurposed[k][1][:12]} is '
                            'not remediated; retire the id with retires_repurpose first')
                    self.repurposed.setdefault(k, (i, c, e))
                self.identity.append((k, c, e, before[k][1], state.rows[k], inside))
                self.timeline[k].append((i, 'identity', e))

        for kind, key, e in self.at.get(c, []):
            if kind != 'prior_representation':
                continue
            self.used.add((kind,) + key)
            later = e['prior_entity']['recorded_later']
            t = later['target']
            row = state.rows.get((t['table'], t['id']))
            if c == e['event_commit'] or ('identity',) + key not in self.used:
                err(f'{key[0]} {key[1]}: recorded_later must follow its identity event on the release line')
            elif row is None or row_hash(row) != later['row_sha256']:
                err(f'{key[0]} {key[1]}: recorded_later target missing or row_sha256 does not match at {c[:12]}')
            elif (t['table'], t['id']) not in added and ((t['table'], t['id']) not in before
                    or canon(before[(t['table'], t['id'])][1]) == canon(row)):
                err(f'{key[0]} {key[1]}: recorded_later target did not change at {c[:12]}')
            else:
                self.prior_records[key] = (i, dict(t, relation='prior_identity'))

    def retirement_ok(self, i, c, k, e):
        """The removal of a repurposed id must say it retires that repurpose and name the replacement id of the entity
        the number came to denote: a fresh id first added after the repurpose and never reserved, or an existing id
        that was already there before this commit. A fresh id is first added after the repurpose, was never removed in
        the walk and is not reserved. Its earlier identity is the repurpose's prior_identity."""
        rp, fix, err = self.repurposed.pop(k, None), e.get('retires_repurpose'), self.errors.append
        where = f'{k[0]} {k[1]} at {c[:12]}'
        if rp is None:
            if fix is not None:
                err(f'{where}: retires_repurpose, but no reviewed repurpose of this id comes before it')
            return
        ri, rc, rep = rp
        if fix is None:
            err(f'{where}: removes an id repurposed at {rc[:12]}; the event needs retires_repurpose naming that repurpose '
                'and the replacement id of the entity the number came to denote')
            return
        rkey = (fix['replacement']['table'], fix['replacement']['id'])
        first = self.first_seen.get(rkey)
        if fix['identity_event_commit'] != rc:
            err(f'{where}: retires_repurpose names {fix["identity_event_commit"][:12]}, but the repurpose is at {rc[:12]}')
        elif fix['replacement_kind'] == 'fresh' and not (first and first[0] > ri and rkey not in self.reserved
                                                         and rkey not in self.removed_ever):
            err(f'{where}: the fresh replacement {rkey[0]} {rkey[1]} must first appear after the repurpose, never have been '
                'removed and never be reserved; declare an id used before existing')
        elif fix['replacement_kind'] == 'existing' and first and first[0] >= i:
            err(f'{where}: the existing replacement {rkey[0]} {rkey[1]} first appears at this commit; declare it fresh')
        else:
            self.remediated[(k, c)] = (ri, rc, rep, e)

    def restoration_ok(self, i, c, key, e, added, state):
        """A reviewed restoration brings a retired id back for the same entity: the id returns at this commit with the
        reviewed row, it was removed at retirement_commit (earlier on this line, and its latest disappearance in the walk)
        with the reviewed row, both rows hold the same_identity values, and no stable identifier both rows hold differs.
        A removal that remediated a repurpose took away the later entity, so it cannot be restored. Marks the event
        used; returns whether it holds."""
        k, err, where = key[:2], self.errors.append, f'{key[0]} {key[1]} at {c[:12]}'
        self.used.add(('restoration',) + key)
        if e['review_status'] != 'reviewed':
            err(f'{where}: the restoration event is {e["review_status"]}, not reviewed')
            return False
        if k not in added:
            err(f'{where}: restoration event, but the id does not return at that commit')
            return False
        try:
            old = retired_row(self.repo, e['retirement_commit'], k, c)
        except MigrationError as x:
            err(f'{where}: {x}')
            return False
        if (k, e['retirement_commit']) in self.remediated:
            err(f'{where}: cannot restore the later entity under an id retired to remediate a repurpose at '
                f'{e["retirement_commit"][:12]}')
            return False
        if k in self.latest_removal and self.latest_removal[k] != e['retirement_commit']:
            err(f'{where}: retirement_commit {e["retirement_commit"][:12]} is not the latest disappearance '
                f'{self.latest_removal[k][:12]} observed in the walk')
            return False
        new, problems = state.rows[k], []
        if row_hash(new) != e['restored_row_sha256']:
            problems.append('restored_row_sha256 does not match the returned row')
        if row_hash(old) != e['retired_row_sha256']:
            problems.append('retired_row_sha256 does not match the row removed at retirement_commit')
        problems += [f'{f} is not {v!r} in both the retired and the restored row'
                     for f, v in sorted(e['same_identity'].items()) if canon(old.get(f)) != canon(v) or canon(new.get(f)) != canon(v)]
        problems += [f'{f} differs between the retired and the restored row ({old[f]!r}, {new[f]!r})' for f in STABLE_IDS
                     if old.get(f) not in (None, '') and new.get(f) not in (None, '') and canon(old[f]) != canon(new[f])]
        for p in problems:
            err(f'{where}: {p}')
        if problems:
            return False
        self.retired.discard(k)
        self.restored[k] = (i, c, e)
        self.timeline[k].append((i, 'restoration', e))
        return True

    def next_event(self, key, after):
        """The first event on a key at a commit later than the given index, or None."""
        events = self.timeline.get(key, [])
        n = bisect.bisect_right([x[0] for x in events], after)
        return events[n] if n < len(events) else None


def resolve_targets(gate, final, targets, index, auto):
    """Follow targets forward in history to what stands for them at --to, without recursion. A removal passes to its
    targets; a repurpose passes to the entity the number used to denote (prior_identity), never redirecting
    automatically; an unresolved identity keeps the key but ends any automatic redirect. A removal followed by a
    restoration of the same id continues at that id (relation restored), never automatically. A path that ends in a
    removal with no successor is reported with that outcome. Every step moves to a strictly later event, so each path
    ends; identical results are listed once. Branching histories can multiply paths, so more than EXPANSION_LIMIT steps
    from one record is an error."""
    out, seen, steps = [], set(), 0
    stack = [(t, index, [t['relation']], auto) for t in reversed(targets)]

    def emit(item):
        """Add one resolved target unless the same one is already listed."""
        if canon(item) not in seen:
            seen.add(canon(item))
            out.append(item)

    while stack:
        steps += 1
        if steps > EXPANSION_LIMIT:
            raise MigrationError(f'the target paths from {canon(targets)[:200]} take more than {EXPANSION_LIMIT:,} steps; '
                                 'check the ledger for an unintended fan-out of split events')
        t, at, relations, redirect = stack.pop()
        key = (t['table'], t['id'])
        nxt = gate.next_event(key, at)
        if nxt is None:
            if key in final:
                emit({'table': key[0], 'id': key[1], 'relations': relations, 'automatic_redirect': redirect})
            continue
        i, kind, e = nxt
        if kind == 'removal':
            back = gate.next_event(key, i)
            if back and back[1] == 'restoration' and back[2]['retirement_commit'] == e['event_commit']:   # same entity back
                stack.append((t, back[0], relations + ['restored'], False))
                continue
            if not e['targets']:
                emit({'table': None, 'id': None, 'end': e['outcome'], 'relations': relations, 'automatic_redirect': False})
            for t2 in reversed(e['targets']):
                stack.append((t2, i, relations + [t2['relation']], redirect and e['automatic_redirect']))
        elif kind == 'restoration':
            stack.append((t, i, relations, False))
        elif e['outcome'] == 'repurpose':
            if not e['targets']:
                later = gate.prior_records.get((e['table'], e['id'], e['event_commit']))
                if later:
                    stack.append((later[1], later[0], relations + ['prior_identity'], False))
                else:
                    emit({'table': None, 'id': None, 'end': e['prior_entity']['status'], 'prior_entity': e['prior_entity'],
                          'relations': relations + ['prior_identity'], 'automatic_redirect': False})
            for t2 in reversed(e['targets']):
                stack.append((t2, i, relations + ['prior_identity'], False))
        else:
            stack.append((t, i, relations, redirect and e['outcome'] != 'unresolved'))
    return out


def prior_targets(gate, final, event, index):
    """Resolve the original entity from its historical targets or its evidenced later representation."""
    later = gate.prior_records.get((event['table'], event['id'], event['event_commit']))
    targets, at = ([later[1]], later[0]) if later else (event['targets'], index)
    return resolve_targets(gate, final, targets, at, False)


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
    """The release files' content: removed events, CSV rows, added ids, identity events, changed fields and counts.
    The removal that retires a repurposed id maps the id to its earlier identity (current_targets) and lists the
    entity the number came to denote separately (later_entity_targets); neither redirects automatically. An id the
    same entity got back later maps to itself from that restoration on."""
    final = state.rows
    removed = []
    for k, c, e, row, inside in gate.events:
        if not inside:
            continue
        entry = {**e, 'before': row, 'present_at_from': k in start, 'present_at_to': k in final}
        back, fix = gate.next_event(k, order[c]), gate.remediated.get((k, c))
        if fix:
            ri, rc, rep, _ = fix
            entry.update(repurposed_at=rc, current_targets=prior_targets(gate, final, rep, ri),
                         later_entity_targets=resolve_targets(gate, final, e['targets'], order[c], False))
            if 'prior_entity' in rep:
                entry['prior_entity'] = rep['prior_entity']
        elif back and back[1] == 'restoration' and back[2]['retirement_commit'] == c:   # the same entity came back later
            entry.update(restored_at=back[2]['event_commit'], current_targets=resolve_targets(
                gate, final, [{'table': k[0], 'id': k[1], 'relation': 'restored'}], back[0], False))
        else:
            entry['current_targets'] = resolve_targets(gate, final, e['targets'], order[c], e['automatic_redirect'])
        removed.append(entry)
    retirement_of = {(k, fix[1]): (c, fix[3]) for (k, c), fix in gate.remediated.items()}
    identity = []
    for k, c, e, before, after, inside in gate.identity:
        fix = retirement_of.get((k, c))
        if not inside and not (fix and fix[0] in gate.interval):
            continue   # an earlier decision is listed again only when its id is retired in this interval
        remediation = None
        if fix:
            rc, r = fix
            remediation = {'event_commit': rc, 'outcome': r['outcome'], 'replacement': r['retires_repurpose']['replacement'],
                           'replacement_kind': r['retires_repurpose']['replacement_kind'],
                           'later_entity_targets': resolve_targets(gate, final, r['targets'], order[rc], False)}
        identity.append({**e, 'before': before, 'after': after, 'event_before_from': not inside, 'present_at_to': k in final,
                         'remediation': remediation, 'current_targets': prior_targets(gate, final, e, order[c])})
    rows = []
    for r in removed:
        b, t = r['before'], r['old_table']
        base = [SINGULAR[t], r['old_id'], label(b), b.get('country_code', b.get('iso2') if t == 'countries' else '') or '',
                b.get('state_code', b.get('iso2') if t == 'states' else '') or '', r['outcome']]
        line = lambda ct, relation, auto: (base + [ct.get('table') or '', ct.get('id') or '', r.get('event_pr_url') or '',
                                                   relation, 'yes' if auto else 'no', r['event_commit']])
        rows += [line(ct, '>'.join(ct['relations']), ct['automatic_redirect']) for ct in r['current_targets']] or [line({}, '', False)]
        rows += [line(ct, '>'.join(['later_entity'] + ct['relations']), False) for ct in r.get('later_entity_targets', [])]
    added = []
    for k in sorted(final.keys() - start.keys()):
        a = {'table': k[0], 'id': k[1], 'name': label(final[k]), 'path': state.path[k], 'added_commit': gate.added_at[k][1]}
        if k in gate.restored:
            a['restored'] = {'event_commit': gate.restored[k][1], 'retirement_commit': gate.restored[k][2]['retirement_commit']}
        added.append(a)
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
                        'restored': sum(1 for a in added if a['table'] == t and 'restored' in a),
                        'changed_records': len({c['id'] for c in changed if c['table'] == t}),
                        'removal_events': sum(1 for r in removed if r['old_table'] == t),
                        'identity_events': sum(1 for x in identity if x['table'] == t),
                        'created_and_removed_in_interval': sum(1 for r in removed if r['old_table'] == t and not r['present_at_from'])}
    return removed, rows, added, identity, changed, per_table, dict(sorted(counts.items()))


CSV_HEADER = ['record', 'old_id', 'name', 'country_code', 'state_code', 'outcome', 'new_table', 'new_id', 'source',
              'relation', 'automatic_redirect', 'event_commit']   # v4.0's nine columns, then three appended
NAMES = ('removed_ids.jsonl', 'removed_ids.csv', 'added_ids.jsonl', 'identity_changes.jsonl', 'changed_fields.jsonl')


def write(out, removed, rows, added, identity, changed, per_table, field_counts, head):
    """Write the six files into a new staging folder, then swap it in for the output folder. The complete output is
    never deleted before its replacement is installed: a backup an interrupted run left in .<out>.previous is put back
    first, and the backup is removed only after the swap. Returns the SHA-256 of each data file."""
    out = Path(out)
    previous, staging = out.parent / f'.{out.name}.previous', None
    dump = lambda items: ''.join(json.dumps(i, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n' for i in items)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        if previous.exists() and not out.exists():
            os.replace(previous, out)   # an interrupted swap left the last complete output here
        staging = Path(tempfile.mkdtemp(prefix=f'.{out.name}.staging-', dir=out.parent))   # unique: never another run's
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
        if previous.exists():
            shutil.rmtree(previous)   # an older backup: the complete output is in out
        if out.exists():
            os.replace(out, previous)
        try:
            os.replace(staging, out)
        except OSError:
            if previous.exists() and not out.exists():
                os.replace(previous, out)
            raise
    except (OSError, ValueError) as err:
        if staging and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        kept = next((str(p) for p in (out, previous) if p.exists()), None)
        raise OutputError(f'could not write {out}: {err}' + (f'; the last complete output is in {kept}' if kept else '')) from err
    shutil.rmtree(previous, ignore_errors=True)   # a leftover is replaced by the next run, never read
    return sums


def on_line_after(repo, commit, to):
    """Whether commit is later than to on a line whose first parents pass through to (works when to is the root)."""
    line = first_parent_line(repo, commit, to)
    if not line:
        return False
    r = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', '--quiet', f'{line[-1]}^1'], capture_output=True)
    return r.returncode == 0 and r.stdout.decode().strip() == to


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
            if r.returncode == 0 and on_line_after(repo, c, to):
                place[c] = 'after'
            else:
                off.append(c)
    if off:
        raise MigrationError('event commits not on the release line (first-parent history of --to or a later release): '
                             + ', '.join(c[:12] for c in off))
    return interval, place


def recorded_later_of(e):
    """The recorded_later binding of a reviewed event, or None. Held placeholders are only checked for their core
    fields, so their prior_entity may be malformed and is never read."""
    prior = e.get('prior_entity') if e.get('review_status') == 'reviewed' else None
    later = prior.get('recorded_later') if isinstance(prior, dict) else None
    return later if isinstance(later, dict) and isinstance(later.get('event_commit'), str) else None


def generate(repo, frm_ref, to_ref, ledger, reserved_path, meta_path, out, log=lambda m: None):
    """Validate the inputs, walk the history, check every event and write the files; raises MigrationError on any
    problem in the inputs or the history, OutputError when the files cannot be written. Events before --from are
    checked by the same walk, which then starts at the first parent of the oldest of them."""
    removals, identities, restorations = load_ledger(ledger)
    reserved, meta = load_reserved(reserved_path), load_meta(meta_path)
    repo = top_level(repo)
    frm, to = resolve(repo, frm_ref), resolve(repo, to_ref)
    every = {k[2] for d in (removals, identities, restorations) for k in d}
    every.update(later['event_commit'] for e in identities.values() if (later := recorded_later_of(e)))
    interval, place = place_commits(repo, frm, to, every)
    applies = lambda d: {k: e for k, e in d.items() if place[k[2]] != 'after'}   # a later release's events wait for it
    for e in applies(identities).values():
        later = recorded_later_of(e)
        if later and not on_line_after(repo, later['event_commit'], e['event_commit']):
            raise MigrationError(f'{e["table"]} {e["id"]}: recorded_later must follow its identity event on the release line')
    base, earlier = frm, {c for c in every if place[c] == 'before'}
    if earlier:
        position = {c: n for n, c in enumerate(first_parent_line(repo, frm))}
        base = git(repo, 'rev-parse', f'{max(earlier, key=position.get)}^1').decode().strip()
        log(f'checking events at {len(earlier)} earlier commits by walking from {base[:12]}')
    gate = Gate(applies(removals), applies(identities), applies(restorations), reserved, interval, repo)
    order, retired_at_from = {}, set(reserved)   # replaced at --from when the walk starts earlier
    log(f'walking to {to[:12]}; {len(interval)} commits since --from {frm[:12]}')

    def on_commit(i, c, *rest):
        """Remember each commit's position, run the gate on it, and note what is retired at --from."""
        order[c] = i
        gate(i, c, *rest)
        if c == frm:
            retired_at_from.clear()
            retired_at_from.update(gate.retired | (gate.reserved - gate.restored.keys()))

    start, state = walk(repo, base, frm, to, on_commit, progress=log)
    errors = gate.errors + [f'{k[0]} {k[1]} is retired or reserved but present at --from' for k in sorted(retired_at_from & start.keys())]
    errors += [f'{k[0]} {k[1]}: event at {k[2][:12]}, but no such removal happened at that commit'
               for k in sorted(gate.removals.keys()) if k not in gate.used]
    errors += [f'{k[0]} {k[1]}: {kind} event at {k[2][:12]} was not checked; the record did not change at that commit'
               for kind, d in (('identity', gate.identities), ('restoration', gate.restorations))
               for k in sorted(d) if (kind,) + k not in gate.used]
    errors += [f'{k[0]} {k[1]}: recorded_later representation was not checked'
               for k, e in gate.identities.items() if (later := recorded_later_of(e))
               and place[later['event_commit']] != 'after'
               and ('prior_representation',) + k not in gate.used]
    errors += [f'{k[0]} {k[1]} was repurposed at {c[:12]} and still denotes the other entity at --to; retire it with its earlier '
               f'identity and give that entity a fresh or proved existing replacement id'
               for k, (_, c, _) in sorted(gate.repurposed.items()) if k in state.rows]
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
