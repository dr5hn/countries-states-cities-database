"""Tests for the release migration generator (migrations.py), on scratch git repositories."""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

import importlib.util

# Loaded from this folder by path: the repository's top-level migrations/ folder would shadow `import migrations`
# when the tests run from the repository root.
_spec = importlib.util.spec_from_file_location('release_migrations', Path(__file__).resolve().with_name('migrations.py'))
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
MigrationError, event_errors, field_changes, generate, row_hash = (m.MigrationError, m.event_errors, m.field_changes,
                                                                   m.generate, m.row_hash)

CITY = 'contributions/cities/XX.json'


def city(i, name, **extra):
    """A minimal city row."""
    return {'id': i, 'name': name, 'country_code': 'XX', 'state_code': 'AA', **extra}


class Repo:
    """A scratch git repository whose commits replace whole contributions files."""

    def __init__(self, root):
        """Create the repository with a countries and a states file."""
        self.root = Path(root) / 'repo'
        self.root.mkdir()
        self.run('init', '-q', '-b', 'main')
        self.run('config', 'user.email', 't@example.invalid')
        self.run('config', 'user.name', 'test')
        self.files = {}

    def run(self, *args):
        """Run git in the repository and return its output."""
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, changes, message='change'):
        """Write (path -> rows) or delete (path -> None) files, commit, and return the SHA."""
        for path, rows in changes.items():
            p = self.root / path
            if rows is None:
                p.unlink()
                self.files.pop(path, None)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps(rows), encoding='utf-8')
                self.files[path] = rows
        self.run('add', '-A')
        self.run('commit', '-q', '--allow-empty', '-m', message)
        return self.run('rev-parse', 'HEAD')


def removal(table, i, commit, parent, path, row, outcome, targets, auto=False, **extra):
    """A reviewed removal event as the ledger stores it."""
    return {'schema_version': 1, 'old_table': table, 'old_id': i, 'event_commit': commit, 'before_commit': parent,
            'before_path': path, 'before_row_sha256': row_hash(row), 'outcome': outcome, 'targets': targets,
            'automatic_redirect': auto, 'review_status': 'reviewed', 'evidence': [{'url': 'https://example.invalid/test'}],
            'review': {'reason': 'test', 'reviewer': 'test'}, **extra}


def restoration(table, i, commit, retired_commit, retired, restored, same):
    """A reviewed restoration event as the ledger stores it."""
    return {'schema_version': 1, 'event_type': 'restoration', 'table': table, 'id': i, 'event_commit': commit,
            'retirement_commit': retired_commit, 'retired_row_sha256': row_hash(retired), 'restored_row_sha256': row_hash(restored),
            'same_identity': same, 'review_status': 'reviewed', 'evidence': [{'url': 'https://example.invalid/test'}],
            'review': {'reason': 'test', 'reviewer': 'test'}}


def target(table, i, relation):
    """One event target."""
    return {'table': table, 'id': i, 'relation': relation}


def identity_event(i, commit, before_row, outcome, targets, table='cities'):
    """A reviewed identity event as the ledger stores it."""
    return {'schema_version': 1, 'event_type': 'identity', 'table': table, 'id': i, 'event_commit': commit,
            'before_row_sha256': row_hash(before_row), 'outcome': outcome, 'targets': targets, 'automatic_redirect': False,
            'review_status': 'reviewed', 'evidence': [{'url': 'https://example.invalid/test'}], 'review': {'reason': 'test', 'reviewer': 'test'}}


class Case(unittest.TestCase):
    """Scratch repository, inputs and a generate() helper."""

    def setUp(self):
        """A repository with one country and one state, plus empty inputs."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.repo = Repo(self.dir)
        self.base_files = {'contributions/countries/countries.json': [{'id': 1, 'name': 'X', 'iso2': 'XX'}],
                           'contributions/states/states.json': [{'id': 1, 'name': 'A', 'iso2': 'AA', 'country_code': 'XX'}]}
        (self.dir / 'unresolved_baseline.jsonl').write_text('')
        self.reserved = self.dir / 'reserved.jsonl'
        self.reserved.write_text('')
        self.meta = self.dir / 'meta.json'
        self.meta.write_text(json.dumps({'data_version': '5.0.0', 'contract_version': '5', 'policy_version': '1',
                                         'data_schema_version': '5', 'notices': ['NOTICE']}))

    def gen(self, frm, to, events, out='out', **kwargs):
        """Run generate() with these ledger events; returns (content, out path)."""
        ledger = self.dir / 'events.jsonl'
        ledger.write_text(''.join(json.dumps(e) + '\n' for e in events))
        content, _ = generate(self.repo.root, frm, to, ledger, self.reserved, self.meta, self.dir / out, **kwargs)
        return content, self.dir / out

    def refused(self, frm, to, events, pattern):
        """Assert generate() refuses with a message matching the pattern and writes nothing."""
        with self.assertRaisesRegex(MigrationError, pattern):
            self.gen(frm, to, events, out='refused')
        self.assertFalse((self.dir / 'refused').exists())


def pr_event(event, number):
    """Replace a fixture's commit key with a PR number, as a data PR would do."""
    return {**{k: v for k, v in event.items() if k != 'event_commit'}, 'event_pr': number}


class PREventsTest(Case):
    """PR keys resolve once, before the existing history and identity gates."""

    def setup_removal(self, message='Remove twin (#42)'):
        """A removed city and its PR-keyed reviewed event."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Twin')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]}, message)
        ev = pr_event(removal('cities', 2, c1, c0, CITY, city(2, 'Twin'), 'merged_same_entity',
                              [target('cities', 1, 'merged_same_entity')], auto=True), 42)
        return c0, c1, ev

    def test_schema_requires_a_valid_key(self):
        """PR keys are positive JSON integers; explicit SHA keys keep the old metadata behavior."""
        _, _, ev = self.setup_removal()
        self.assertEqual(event_errors(ev, 'test'), [])
        for bad in (True, False, 0, -1, 42.0, '42', None, [], {}):
            with self.subTest(pr=bad):
                self.assertTrue(event_errors(dict(ev, event_pr=bad), 'test'))
        self.assertEqual(event_errors(dict(ev, event_commit='a' * 40), 'test'), [])
        self.assertTrue(event_errors(dict(ev, event_commit=None), 'test'))
        self.assertTrue(event_errors({k: v for k, v in ev.items() if k != 'event_pr'}, 'test'))

    def test_subject_resolution_and_published_sha(self):
        """A historical PR resolves by its subject suffix, before --from too, and publishes its full SHA."""
        c0, c1, ev = self.setup_removal()
        c2 = self.repo.commit({}, 'next release')
        content, out = self.gen(c0, c2, [ev])
        self.assertEqual(content[0][0]['event_commit'], c1)
        self.assertEqual(json.loads((out / 'removed_ids.jsonl').read_text())['event_commit'], c1)
        self.assertEqual(content[1][0][-1], c1)
        self.assertEqual(content[0][0]['event_pr'], 42)
        self.assertNotIn('event_commit', ev)
        self.refused(c1, c2, [dict(ev, before_row_sha256='0' * 64)], 'before_row_sha256')
        content, _ = self.gen(c1, c2, [ev], out='step')
        self.assertEqual(content[0], [])

    def test_no_match_requires_exact_suffix_on_release_line(self):
        """Body mentions, embedded suffixes, other PRs and side-branch commits cannot bind an event."""
        for message in ('Remove (#42) trailing', 'Remove (#420)', 'Remove\n\nDetails (#42)', 'Remove (#042)'):
            with self.subTest(message=message):
                c0, c1, ev = self.setup_removal(message)
                self.refused(c0, c1, [ev], 'event_pr 42 matches 0 first-parent commits')
        self.repo.run('checkout', '-q', '-b', 'side')
        side = self.repo.commit({}, 'Only a side branch (#42)')
        self.refused(c0, c1, [ev], 'matches 0')
        self.repo.run('checkout', '-q', 'main')
        self.repo.run('merge', '--no-ff', '-m', 'Merge side branch', side)
        head = self.repo.run('rev-parse', 'HEAD')
        self.refused(c0, head, [ev], 'matches 0')

    def test_multiple_matches_are_refused(self):
        """Two matching subjects on the first-parent line are ambiguous, including one before --from."""
        c0, c1, ev = self.setup_removal()
        c2 = self.repo.commit({}, 'Another subject (#42)')
        self.refused(c0, c2, [ev], 'event_pr 42 matches 2 first-parent commits')
        self.refused(c1, c2, [ev], 'matches 2')

    def test_mixed_keys_and_duplicate_resolved_key(self):
        """SHA and PR events can coexist; two keys resolving to the same event are still duplicates."""
        c0, c1, ev = self.setup_removal()
        c2 = self.repo.commit({CITY: []}, 'Remove final city (#43)')
        old = removal('cities', 1, c2, c1, CITY, city(1, 'One'), 'no_successor', [])
        content, _ = self.gen(c0, c2, [ev, old])
        self.assertEqual([e['event_commit'] for e in content[0]], [c1, c2])
        self.refused(c0, c1, [ev, {**{k: v for k, v in ev.items() if k != 'event_pr'}, 'event_commit': c1}],
                     'appears twice')

    def test_explicit_commit_keeps_legacy_pr_metadata(self):
        """Existing SHAs are authoritative even with PR metadata or a matching pending PR option."""
        c0, c1, ev = self.setup_removal('Legacy SHA event')
        c2 = self.repo.commit({}, 'Preview')
        for pr in (42, None, 'legacy metadata'):
            legacy = dict(ev, event_commit=c1, event_pr=pr)
            content, _ = self.gen(c0, c2, [legacy], pending_pr=42)
            self.assertEqual(content[0][0]['event_commit'], c1)
            self.assertEqual(content[0][0]['event_pr'], pr)

    def test_resolved_removal_keeps_all_guards(self):
        """PR resolution preserves the before-parent/path/hash, target and review gates."""
        c0, c1, ev = self.setup_removal()
        for changes, pattern in (({'before_commit': c1}, 'event before'),
                                 ({'before_path': 'contributions/cities/YY.json'}, 'event before'),
                                 ({'before_row_sha256': '0' * 64}, 'before_row_sha256'),
                                 ({'targets': [target('cities', 9, 'merged_same_entity')]}, 'target cities 9'),
                                 ({'review_status': 'held'}, 'held, not reviewed')):
            with self.subTest(changes=changes):
                self.refused(c0, c1, [dict(ev, **changes)], pattern)

    def test_pending_pr_binds_merge_preview_only_for_own_events(self):
        """The preview's first parent is the base; only this PR overrides subject lookup, with output SHA retained."""
        c0, c1, ev = self.setup_removal()
        self.repo.run('checkout', '-q', '-b', 'pr')
        self.repo.commit({CITY: []}, 'Remove one city')
        self.repo.run('checkout', '-q', 'main')
        self.repo.run('merge', '--no-ff', '-m', 'Merge preview', 'pr')
        preview = self.repo.run('rev-parse', 'HEAD')
        pending = pr_event(removal('cities', 1, preview, c1, CITY, city(1, 'One'), 'no_successor', []), 43)
        self.refused(c0, preview, [ev, pending], 'event_pr 43 matches 0')
        content, _ = self.gen(c0, preview, [ev, pending], pending_pr=43)
        self.assertEqual([e['event_commit'] for e in content[0]], [c1, preview])
        self.assertEqual(content[0][1]['before_commit'], c1)
        with self.assertRaisesRegex(MigrationError, 'no ledger event'):
            self.gen(c0, preview, [ev], pending_pr=43)
        with self.assertRaisesRegex(MigrationError, 'event_pr 44 matches 0'):
            self.gen(c0, preview, [ev, pending, dict(pending, event_pr=44)], pending_pr=43)

    def test_pending_pr_overrides_subject_and_validates_input(self):
        """Pending mode deliberately binds --to even if that PR subject exists; invalid numbers are refused."""
        c0, c1, ev = self.setup_removal()
        c2 = self.repo.commit({}, 'Preview (#42)')
        with self.assertRaisesRegex(MigrationError, 'no ledger event|no such removal'):
            self.gen(c0, c2, [ev], pending_pr=42)
        for bad in (0, -1, True, '42', 42.0):
            with self.subTest(pending_pr=bad), self.assertRaisesRegex(MigrationError, 'pending_pr must be a positive integer'):
                self.gen(c0, c1, [ev], pending_pr=bad)

    def test_pending_pr_cli(self):
        """The CLI passes pending PR mode through and rejects a non-positive number without output."""
        c0, c1, ev = self.setup_removal('Preview')
        ledger = self.dir / 'events.jsonl'
        ledger.write_text(json.dumps(ev) + '\n')
        args = ['--from', c0, '--to', c1, '--ledger', str(ledger), '--reserved', str(self.reserved),
                '--meta', str(self.meta), '--repo', str(self.repo.root), '--out', str(self.dir / 'cli')]
        self.assertEqual(m.main(args + ['--pending-pr', '42']), 0)
        with redirect_stderr(io.StringIO()):
            self.assertEqual(m.main(args + ['--pending-pr', '0']), 1)

    def test_repurpose_keyed_by_pr_still_needs_retirement(self):
        """A PR-keyed repurpose must retire the reused id with its replacement, also for step releases."""
        old, later = city(2, 'Unit'), city(2, 'Town')
        county = 'contributions/counties/XX.json'
        c0 = self.repo.commit({**self.base_files, CITY: [old], county: []})
        c1 = self.repo.commit({CITY: [later], county: [{'id': 9, 'name': 'Unit'}]}, 'Reclassify (#42)')
        rep = pr_event(identity_event(2, c1, old, 'repurpose', [target('counties', 9, 'prior_identity')]), 42)
        self.refused(c0, c1, [rep], 'still denotes the other entity')
        c2 = self.repo.commit({CITY: [city(3, 'Town')]}, 'Retire reused id (#43)')
        retire = pr_event(removal('cities', 2, c2, c1, CITY, later, 'merged_same_entity',
                                 [target('cities', 3, 'merged_same_entity')], retires_repurpose={
                                     'identity_event_commit': c1, 'replacement': {'table': 'cities', 'id': 3},
                                     'replacement_kind': 'fresh'}), 43)
        for frm in (c0, c1):
            content, out = self.gen(frm, c2, [rep, retire])
            self.assertEqual(content[3][0]['event_commit'], c1)
            self.assertEqual(content[3][0]['remediation']['event_commit'], c2)
            self.assertEqual(content[0][0]['later_entity_targets'][0]['id'], 3)
            self.assertEqual(json.loads((out / 'identity_changes.jsonl').read_text())['event_commit'], c1)
        self.refused(c0, c2, [rep, {k: v for k, v in retire.items() if k != 'retires_repurpose'}], 'needs retires_repurpose')

    def test_restoration_keyed_by_pr_and_pending_pr(self):
        """A PR-keyed restoration binds the same stable identity and publishes the resolved restoration SHA."""
        old = city(2, 'Two', wikiDataId='Q2')
        c0 = self.repo.commit({**self.base_files, CITY: [old]})
        c1 = self.repo.commit({CITY: []}, 'Retire (#41)')
        c2 = self.repo.commit({CITY: [old]}, 'Restore (#42)')
        retire = pr_event(removal('cities', 2, c1, c0, CITY, old, 'no_successor', []), 41)
        back = pr_event(restoration('cities', 2, c2, c1, old, old, {'wikiDataId': 'Q2'}), 42)
        for pending in (None, 42):
            content, _ = self.gen(c1, c2, [retire, back], pending_pr=pending)
            self.assertEqual(content[2][0]['restored']['event_commit'], c2)
        self.refused(c0, c2, [retire, dict(back, same_identity={'wikiDataId': 'Q9'})], 'wikiDataId is not')
        self.refused(c0, c2, [retire, dict(back, restored_row_sha256='0' * 64)], 'restored_row_sha256')
        self.refused(c0, c2, [retire], 'retired or reserved')

    def test_baseline_conflict_after_pr_resolution(self):
        """Resolving a PR cannot evade the conflict with the immutable baseline at the same commit."""
        row = city(1, 'One')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({}, 'Review (#42)')
        baseline = {'schema_version': 1, 'table': 'cities', 'id': 1, 'baseline_commit': c1,
                    'row_sha256': row_hash(row), 'outcome': 'unresolved', 'reason': 'test', 'decision_round': 'test',
                    'review_status': 'reviewed', 'review': {'reason': 'test', 'reviewer': 'test'},
                    'evidence': [{'url': 'https://example.invalid/test'}]}
        (self.dir / 'unresolved_baseline.jsonl').write_text(json.dumps(baseline) + '\n')
        ev = pr_event(dict(identity_event(1, c1, row, 'classification', []), decision_only=True,
                           after_row_sha256=row_hash(row)), 42)
        self.refused(c0, c1, [ev], 'baseline conflicts')


class EventSchemaTest(unittest.TestCase):
    """Event shape and outcome rules, before any history is read."""

    def base(self, **kw):
        """A valid merge event, with fields overridden."""
        e = removal('cities', 2, 'a' * 40, 'b' * 40, CITY, city(2, 'Twin'), 'merged_same_entity',
                    [target('cities', 1, 'merged_same_entity')], auto=True)
        e.update(kw)
        return e

    def test_valid_events_pass(self):
        """A merge redirect, a seat with its county, and a reviewed no-successor retirement are valid."""
        self.assertEqual(event_errors(self.base(), 'e'), [])
        seat = self.base(outcome='administrative_seat', automatic_redirect=False,
                         targets=[target('cities', 1, 'administrative_seat'), target('counties', 9, 'moved_dataset')])
        self.assertEqual(event_errors(seat, 'e'), [])
        self.assertEqual(event_errors(self.base(outcome='no_successor', automatic_redirect=False, targets=[]), 'e'), [])

    def test_unsafe_redirects_and_targets_are_refused(self):
        """Wrong-table merge, seat labelled merge, two merge targets, one-target split, no relation, null targets."""
        cases = {
            'merge into another table': self.base(targets=[target('counties', 1, 'merged_same_entity')]),
            'seat relation on a merge': self.base(targets=[target('cities', 1, 'administrative_seat')]),
            'two merge targets': self.base(targets=[target('cities', 1, 'merged_same_entity'), target('cities', 3, 'merged_same_entity')]),
            'one-target split': self.base(outcome='split_into', automatic_redirect=False, targets=[target('cities', 1, 'split_into')]),
            'target without relation': self.base(targets=[{'table': 'cities', 'id': 1}]),
            'boolean target id': self.base(targets=[target('cities', True, 'merged_same_entity')]),
            'redirect on a seat': self.base(outcome='administrative_seat', targets=[target('cities', 1, 'administrative_seat')]),
            'null targets': self.base(outcome='no_successor', automatic_redirect=False, targets=None),
            'string redirect flag': self.base(automatic_redirect='yes'),
        }
        for name, e in cases.items():
            self.assertTrue(event_errors(e, 'e'), name)

    def test_provenance_is_required(self):
        """Missing reason, evidence, commit SHAs or a before row that does not hash are refused."""
        for name, e in {'no reason': self.base(review={'reviewer': 'x'}), 'no evidence': self.base(evidence=[]),
                        'null evidence': self.base(evidence=[None]), 'empty evidence': self.base(evidence=[{}]),
                        'boolean schema version': self.base(schema_version=True), 'list table': self.base(old_table=['cities']),
                        'dict outcome': self.base(outcome={'a': 1}), 'self target': self.base(targets=[target('cities', 2, 'merged_same_entity')]),
                        'short commit': self.base(event_commit='abc'), 'bad before': self.base(before=city(2, 'Other')),
                        'float id': self.base(old_id=2.0), 'bool id': self.base(old_id=True),
                        'url without host': self.base(evidence=[{'url': 'http://'}]),
                        'blank manifest': self.base(evidence=[{'manifest': ' ', 'sha256': '0' * 64}]),
                        'url with spaces': self.base(evidence=[{'url': 'https://example.invalid/a b'}])}.items():
            self.assertTrue(event_errors(e, 'e'), name)
        self.assertEqual(event_errors(self.base(evidence=[{'manifest': 'research/x.json', 'sha256': '0' * 64}]), 'e'), [])

    def test_retiring_a_repurpose_is_declared_in_full(self):
        """retires_repurpose needs its fields, a replacement among the targets, and no automatic redirect."""
        fix = {'identity_event_commit': 'c' * 40, 'replacement': {'table': 'cities', 'id': 1}, 'replacement_kind': 'fresh'}
        ok = self.base(automatic_redirect=False, retires_repurpose=fix)
        self.assertEqual(event_errors(ok, 'e'), [])
        for name, e in {'redirect': self.base(retires_repurpose=fix),
                        'replacement not a target': self.base(automatic_redirect=False, retires_repurpose={**fix, 'replacement': {'table': 'cities', 'id': 7}}),
                        'no successor': self.base(outcome='no_successor', automatic_redirect=False, targets=[], retires_repurpose=fix),
                        'bad kind': self.base(automatic_redirect=False, retires_repurpose={**fix, 'replacement_kind': 'any'})}.items():
            self.assertTrue(event_errors(e, 'e'), name)


class FieldChangesTest(unittest.TestCase):
    """Typed, presence-aware field deltas."""

    def test_presence_and_types(self):
        """Missing and null differ both ways, per translation key and for the container; 1 and true differ."""
        d = field_changes({'a': None, 'n': 1, 'translations': {'de': 'X'}, 'updated_at': 1},
                          {'b': None, 'n': True, 'translations': {'de': 'X', 'fr': None}, 'updated_at': 2})
        self.assertEqual([(x['field'], x['before_present'], x['after_present']) for x in d],
                         [('a', True, False), ('b', False, True), ('n', True, True), ('translations.fr', False, True)])
        self.assertEqual(field_changes({'translations': {}}, {'translations': None})[0]['field'], 'translations')
        self.assertEqual(field_changes({'x': 1}, {'x': 1.0})[0]['after'], 1.0)


class HistoryTest(Case):
    """Removals joined to the commit where they happened, with targets checked there."""

    def test_merge_addition_and_files(self):
        """A reviewed merge and an addition give every file; counts reconcile; runs are byte-identical."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Twin')]})
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town'), city(3, 'Three')]})
        ev = removal('cities', 2, c1, c0, CITY, city(2, 'Twin'), 'merged_same_entity', [target('cities', 1, 'merged_same_entity')], auto=True)
        (removed, rows, added, _, changed, per_table, counts), out = self.gen(c0, c1, [ev])
        self.assertEqual(removed[0]['current_targets'], [{'table': 'cities', 'id': 1, 'relations': ['merged_same_entity'], 'automatic_redirect': True}])
        self.assertEqual([(a['id'], a['added_commit']) for a in added], [(3, c1)])
        self.assertEqual(changed, [{'table': 'cities', 'id': 1, 'field': 'type', 'before': None, 'after': 'town', 'before_present': False, 'after_present': True}])
        self.assertEqual(per_table['cities'], {'from_total': 2, 'to_total': 2, 'removed': 1, 'added': 1, 'restored': 0, 'changed_records': 1,
                                               'removal_events': 1, 'identity_events': 0, 'created_and_removed_in_interval': 0})
        header = (out / 'removed_ids.csv').read_text().splitlines()[0].split(',')
        self.assertEqual(header[:9], ['record', 'old_id', 'name', 'country_code', 'state_code', 'outcome', 'new_table', 'new_id', 'source'])
        self.assertEqual(rows[0][:8], ['city', 2, 'Twin', 'XX', 'AA', 'merged_same_entity', 'cities', 1])
        manifest = json.loads((out / 'release_manifest.json').read_text())
        self.assertEqual((manifest['from']['sha'], manifest['to']['sha'], manifest['release']['data_version']), (c0, c1, '5.0.0'))
        first = {p.name: p.read_bytes() for p in out.iterdir()}
        _, out2 = self.gen(c0, c1, [ev], out='out2')
        self.assertEqual(first, {p.name: p.read_bytes() for p in out2.iterdir()})

    def test_event_must_match_the_removal(self):
        """No event, an event at another commit, or a wrong before-row hash is refused, writing nothing."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One')], 'contributions/cities/YY.json': []})
        self.refused(c0, c2, [], 'no ledger event')
        args = ('cities', 2)
        wrong_commit = removal(*args, c2, c1, CITY, city(2, 'Two'), 'no_successor', [])
        self.refused(c0, c2, [wrong_commit], 'no ledger event|no such removal')
        wrong_hash = removal(*args, c1, c0, CITY, city(2, 'Two'), 'no_successor', [])
        wrong_hash['before_row_sha256'] = '0' * 64
        self.refused(c0, c2, [wrong_hash], 'before_row_sha256')

    def test_target_checked_at_the_event_commit_and_chains_followed(self):
        """A to B, then B to C a commit later: valid, and B's old id resolves to C; the redirect needs both hops."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'A'), city(2, 'B')]})
        c1 = self.repo.commit({CITY: [city(2, 'B'), city(3, 'C')]})
        c2 = self.repo.commit({CITY: [city(3, 'C')]})
        e1 = removal('cities', 1, c1, c0, CITY, city(1, 'A'), 'merged_same_entity', [target('cities', 2, 'merged_same_entity')], auto=True)
        e2 = removal('cities', 2, c2, c1, CITY, city(2, 'B'), 'merged_same_entity', [target('cities', 3, 'merged_same_entity')], auto=False)
        (removed, *_), _ = self.gen(c0, c2, [e1, e2])
        self.assertEqual(removed[0]['current_targets'], [{'table': 'cities', 'id': 3, 'relations': ['merged_same_entity'] * 2, 'automatic_redirect': False}])
        missing = removal('cities', 1, c1, c0, CITY, city(1, 'A'), 'merged_same_entity', [target('cities', 9, 'merged_same_entity')])
        self.refused(c0, c2, [missing, e2], 'target cities 9 does not exist after that commit')

    def test_created_and_removed_between_releases(self):
        """An id created and removed inside the interval needs a reviewed event and is emitted, though absent at both ends."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        c1 = self.repo.commit({CITY: [city(1, 'One'), city(5, 'Brief')]})
        c2 = self.repo.commit({CITY: [city(1, 'One')]})
        ev = removal('cities', 5, c2, c1, CITY, city(5, 'Brief'), 'invalid_record', [])
        self.refused(c0, c2, [dict(ev, review_status='held')], 'held, not reviewed')
        (removed, _, added, _, _, per_table, _), _ = self.gen(c0, c2, [ev])
        self.assertEqual((removed[0]['old_id'], removed[0]['present_at_from'], added), (5, False, []))
        self.assertEqual(per_table['cities']['created_and_removed_in_interval'], 1)

    def test_ids_never_return(self):
        """A removed id added back, a reserved id present at --from, and a reserved id added are all refused."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One'), city(2, 'Someone else')]})
        ev = removal('cities', 2, c1, c0, CITY, city(2, 'Two'), 'no_successor', [])
        self.refused(c0, c2, [ev], 'retired or reserved id and is in use again')
        self.reserved.write_text(json.dumps({'table': 'cities', 'id': 1}) + '\n')
        self.refused(c0, c1, [ev], 'cities 1 is retired or reserved but present at --from')
        self.reserved.write_text(json.dumps({'table': 'cities', 'id': 7}) + '\n')
        c3 = self.repo.commit({CITY: [city(1, 'One'), city(2, 'Someone else'), city(7, 'Seven')]})
        self.refused(c2, c3, [], 'cities 7 is a retired or reserved id')

    def test_events_outside_the_interval(self):
        """A later release's event does not block an earlier interval; an earlier one keeps its id retired."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town'), city(2, 'Two')]})
        c2 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        later = removal('cities', 2, c2, c1, CITY, city(2, 'Two'), 'no_successor', [])
        self.gen(c0, c1, [later])
        c3 = self.repo.commit({CITY: [city(1, 'One', type='town'), city(2, 'Back')]})
        self.refused(c2, c3, [later], 'retired or reserved id')

    def test_ids_must_be_final_unique_and_integers(self):
        """An id-less row at --to, a duplicate across files and a boolean id are refused; an id-less row in between is fine."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        c1 = self.repo.commit({CITY: [city(1, 'One'), {'name': 'New'}]})
        self.refused(c0, c1, [], 'rows have no id at --to')
        c2 = self.repo.commit({CITY: [city(1, 'One'), city(4, 'New')]})
        (_, _, added, *_), _ = self.gen(c0, c2, [])
        self.assertEqual([a['id'] for a in added], [4])
        c3 = self.repo.commit({'contributions/cities/YY.json': [city(4, 'Copy')]})
        self.refused(c2, c3, [], 'cities id 4 is duplicated')
        self.repo.commit({'contributions/cities/YY.json': None})
        c5 = self.repo.commit({CITY: [city(1, 'One'), city(True, 'Bool')]})
        self.refused(c5, c5, [], 'is not a positive integer')

    def test_fixed_files_may_appear(self):
        """A countries file absent at --from counts as an empty table, so its rows are additions."""
        c0 = self.repo.commit({CITY: [city(1, 'One')]})
        c1 = self.repo.commit(self.base_files)
        (_, _, added, *_), _ = self.gen(c0, c1, [])
        self.assertEqual(sorted((a['table'], a['id']) for a in added), [('countries', 1), ('states', 1)])

    def test_identity_event(self):
        """A reviewed identity event is emitted where the record changed and kept its id; elsewhere it is refused."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'Regency'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'Regency', type='municipality'), city(2, 'Two')]})
        ev = identity_event(1, c1, city(1, 'Regency'), 'classification', [])
        (_, _, _, identity, *_), out = self.gen(c0, c1, [ev])
        self.assertEqual((identity[0]['before'].get('type'), identity[0]['after']['type']), (None, 'municipality'))
        c2 = self.repo.commit({'contributions/cities/YY.json': []})
        self.refused(c0, c2, [dict(ev, event_commit=c2)], 'did not change there')

    def repurpose_history(self):
        """City 1 merges into city 2; city 2 then comes to denote a town (the regency stays county 9); city 2 retires and
        the town gets fresh city 3. Returns the commits and the merge, repurpose and retirement events."""
        counties = 'contributions/counties/XX.json'
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'A'), city(2, 'B Regency')], counties: [{'id': 9, 'name': 'B Regency'}]})
        c1 = self.repo.commit({CITY: [city(2, 'B Regency')]})
        c2 = self.repo.commit({CITY: [city(2, 'B Town')]})
        c3 = self.repo.commit({CITY: [city(3, 'B Town')]})
        merge = removal('cities', 1, c1, c0, CITY, city(1, 'A'), 'merged_same_entity', [target('cities', 2, 'merged_same_entity')], auto=True)
        repurpose = identity_event(2, c2, city(2, 'B Regency'), 'repurpose', [target('counties', 9, 'prior_identity')])
        fix = {'identity_event_commit': c2, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'}
        retire = removal('cities', 2, c3, c2, CITY, city(2, 'B Town'), 'merged_same_entity',
                         [target('cities', 3, 'merged_same_entity')], retires_repurpose=fix)
        return (c0, c1, c2, c3), (merge, repurpose, retire)

    def test_repurpose_needs_remediation_and_maps_to_the_earlier_identity(self):
        """A repurposed id may not remain at --to, nor disappear without naming the other entity's replacement. Once
        retired, the id and an earlier merge into it map to the entity the number first denoted, never automatically;
        the town's fresh id is listed apart. Both placements of the repurpose give the same mapping."""
        (c0, c1, c2, c3), (merge, repurpose, retire) = self.repurpose_history()
        self.refused(c0, c2, [merge, repurpose], 'still denotes the other entity')
        bare = {k: v for k, v in retire.items() if k != 'retires_repurpose'}
        self.refused(c0, c3, [merge, repurpose, bare], 'needs retires_repurpose')
        regency = [{'table': 'counties', 'id': 9, 'relations': ['prior_identity'], 'automatic_redirect': False}]
        town = [{'table': 'cities', 'id': 3, 'relations': ['merged_same_entity'], 'automatic_redirect': False}]
        for frm in (c0, c2):
            (removed, rows, _, identity, *_), _ = self.gen(frm, c3, [merge, repurpose, retire], out=f'out-{frm[:6]}')
            own = [r for r in removed if r['old_id'] == 2][0]
            self.assertEqual((own['current_targets'], own['later_entity_targets'], own['repurposed_at']), (regency, town, c2))
            self.assertEqual(identity[0]['remediation']['replacement'], {'table': 'cities', 'id': 3})
            self.assertEqual(identity[0]['event_before_from'], frm == c2)
            self.assertNotIn('yes', [r[10] for r in rows])
            self.assertIn(['cities', 3, 'later_entity>merged_same_entity'], [[r[6], r[7], r[9]] for r in rows])
        (removed, *_), _ = self.gen(c0, c3, [merge, repurpose, retire])
        self.assertEqual(removed[0]['current_targets'], [{'table': 'counties', 'id': 9, 'relations': ['merged_same_entity', 'prior_identity'],
                                                         'automatic_redirect': False}])

    def test_no_record_repurpose_schema(self):
        """Empty mappings need their own explicit, evidenced declaration; existing target rules remain strict."""
        prior = {'status': 'unrecorded', 'reason': 'No separate original record at conversion',
                 'evidence': [{'url': 'https://example.invalid/inventory'}]}
        event = identity_event(2, 'a' * 40, city(2, 'Old'), 'repurpose', [])
        self.assertTrue(event_errors(event, 'test'))
        self.assertFalse(event_errors(dict(event, prior_entity=prior), 'test'))
        for bad in (None, [], {}, {**prior, 'status': 'unknown'}, {**prior, 'status': []},
                    {**prior, 'reason': ' '}, {**prior, 'evidence': []},
                    {**prior, 'evidence': [{'url': 'file:///tmp/source'}]}):
            with self.subTest(prior=bad):
                self.assertTrue(event_errors(dict(event, prior_entity=bad), 'test'))
        for bad in (dict(event, prior_entity=prior, targets=[target('counties', 9, 'prior_identity')]),
                    dict(event, prior_entity=prior, outcome='classification'),
                    dict(event, prior_entity=prior, automatic_redirect=True),
                    dict(event, prior_entity=prior, review={}),
                    dict(event, prior_entity=prior, evidence=[]),
                    removal('cities', 2, 'a' * 40, 'b' * 40, CITY, city(2, 'Old'),
                            'no_successor', [], prior_entity=prior),
                    dict(restoration('cities', 2, 'a' * 40, 'b' * 40, city(2, 'Old'), city(2, 'Old'),
                                     {'wikiDataId': 'Q1'}), prior_entity=prior)):
            with self.subTest(event=bad):
                self.assertTrue(event_errors(bad, 'test'))

    def test_no_record_repurpose_still_needs_complete_remediation(self):
        """Both statuses keep all history, hash, replacement and retirement gates and never redirect."""
        (c0, c1, c2, c3), (merge, original, retire) = self.repurpose_history()
        for status in ('ended', 'unrecorded'):
            prior = {'status': status, 'reason': 'Reviewed absence of a separate original record',
                     'evidence': [{'url': 'https://example.invalid/inventory'}]}
            rep = dict(original, targets=[], prior_entity=prior)
            self.refused(c0, c2, [merge, rep], 'still denotes the other entity')
            self.refused(c0, c3, [merge, rep, {k: v for k, v in retire.items() if k != 'retires_repurpose'}],
                         'needs retires_repurpose')
            self.refused(c0, c3, [merge, dict(rep, before_row_sha256='0' * 64), retire], 'identity before_row_sha256')
            self.refused(c0, c3, [merge, rep, dict(retire, retires_repurpose={**retire['retires_repurpose'],
                         'replacement_kind': 'existing'})], 'first appears at this commit')
            for frm in (c0, c2):
                (removed, rows, _, identity, *_), _ = self.gen(frm, c3, [merge, rep, retire],
                                                              out=f'no-record-{status}-{frm[:6]}')
                own = next(r for r in removed if r['old_id'] == 2)
                self.assertEqual(own['current_targets'], [])
                self.assertEqual(own['prior_entity'], prior)
                self.assertEqual(identity[0]['prior_entity'], prior)
                self.assertEqual(identity[0]['current_targets'], [])
                self.assertEqual(own['later_entity_targets'][0]['id'], 3)
                self.assertFalse(own['later_entity_targets'][0]['automatic_redirect'])
                self.assertEqual(identity[0]['event_before_from'], frm == c2)
                self.assertNotIn('yes', [r[10] for r in rows])
                if frm == c0:
                    terminal = next(r for r in removed if r['old_id'] == 1)['current_targets'][0]
                    self.assertEqual(terminal['end'], status)
                    self.assertEqual(terminal['prior_entity'], prior)
                    self.assertIsNone(terminal['id'])
                    self.assertFalse(terminal['automatic_redirect'])
        self.refused(c0, c3, [merge, dict(original, targets=[target('counties', 999, 'prior_identity')]), retire],
                     'identity target counties 999')

    def test_recorded_later_schema(self):
        """Delayed representation is only for unrecorded entities and binds an exact different key, commit and row."""
        later = {'event_commit': 'b' * 40, 'target': {'table': 'counties', 'id': 9}, 'row_sha256': 'c' * 64}
        prior = {'status': 'unrecorded', 'reason': 'Original unit first represented later',
                 'evidence': [{'url': 'https://example.invalid/proof'}], 'recorded_later': later}
        event = dict(identity_event(2, 'a' * 40, city(2, 'Unit'), 'repurpose', []), prior_entity=prior)
        self.assertFalse(event_errors(event, 'test'))
        for bad in (None, {}, {**later, 'event_commit': 'bad'}, {**later, 'row_sha256': False},
                    {**later, 'target': {'table': 'cities', 'id': 2}}, {**later, 'target': {'table': 'cities', 'id': True}}):
            with self.subTest(later=bad):
                self.assertTrue(event_errors(dict(event, prior_entity={**prior, 'recorded_later': bad}), 'test'))
        self.assertTrue(event_errors(dict(event, prior_entity={**prior, 'status': 'ended'}), 'test'))

    def test_recorded_later_is_temporal_hash_checked_and_follows_later_events(self):
        """A prior entity can gain representation later; future mappings wait, and bad timing/rows are refused."""
        counties = 'contributions/counties/XX.json'
        original, town, unit = city(2, 'Unit'), city(2, 'Town'), {'id': 9, 'name': 'Unit'}
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'A'), original], counties: []})
        c1 = self.repo.commit({CITY: [original]})
        c2 = self.repo.commit({CITY: [town]})
        c3 = self.repo.commit({CITY: [city(3, 'Town')]})
        c4 = self.repo.commit({counties: [unit]})
        c5 = self.repo.commit({counties: [{'id': 10, 'name': 'Unit'}]})
        c6 = self.repo.commit({})
        merge = removal('cities', 1, c1, c0, CITY, city(1, 'A'), 'merged_same_entity',
                        [target('cities', 2, 'merged_same_entity')], auto=True)
        later = {'event_commit': c4, 'target': {'table': 'counties', 'id': 9}, 'row_sha256': row_hash(unit)}
        prior = {'status': 'unrecorded', 'reason': 'Unit not independently recorded until later',
                 'evidence': [{'url': 'https://example.invalid/proof'}], 'recorded_later': later}
        rep = dict(identity_event(2, c2, original, 'repurpose', []), prior_entity=prior)
        retire = removal('cities', 2, c3, c2, CITY, town, 'merged_same_entity',
                         [target('cities', 3, 'merged_same_entity')], retires_repurpose={
                             'identity_event_commit': c2, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'})
        move = removal('counties', 9, c5, c4, counties, unit, 'merged_same_entity',
                       [target('counties', 10, 'merged_same_entity')], auto=True)
        events = [merge, rep, retire, move]
        (removed, _, _, identity, *_), _ = self.gen(c0, c3, events, out='before-recorded')
        self.assertEqual(identity[0]['current_targets'], [])
        self.assertEqual(removed[0]['current_targets'][0]['end'], 'unrecorded')
        for frm in (c0, c2, c4):
            (removed, _, _, identity, *_), _ = self.gen(frm, c5, events, out=f'after-recorded-{frm[:6]}')
            own = next(r for r in removed if r['old_table'] == 'cities' and r['old_id'] == 2) if frm != c4 else None
            if own:
                self.assertEqual(own['current_targets'][0]['id'], 10)
                self.assertFalse(own['current_targets'][0]['automatic_redirect'])
                self.assertEqual(own['prior_entity'], prior)
            if identity:
                self.assertEqual(identity[0]['current_targets'][0]['id'], 10)
        for update, pattern in (({'row_sha256': '0' * 64}, 'row_sha256 does not match'),
                                ({'target': {'table': 'counties', 'id': 99}}, 'target missing'),
                                ({'event_commit': c0}, 'must follow its identity event'),
                                ({'event_commit': c1}, 'must follow its identity event'),
                                ({'event_commit': c2}, 'must follow its identity event'),
                                ({'event_commit': 'f' * 40}, 'not on the release line'),
                                ({'event_commit': c6, 'target': {'table': 'counties', 'id': 10},
                                  'row_sha256': row_hash({'id': 10, 'name': 'Unit'})}, 'target did not change')):
            bad = dict(rep, prior_entity={**prior, 'recorded_later': {**later, **update}})
            self.refused(c0, c6, [merge, bad, retire, move], pattern)

    def test_fresh_replacement_must_be_new(self):
        """A 'fresh' replacement that existed before the repurpose is refused; declared 'existing' it is accepted."""
        counties = 'contributions/counties/XX.json'
        c0 = self.repo.commit({**self.base_files, CITY: [city(2, 'B Regency'), city(3, 'B Town')], counties: [{'id': 9, 'name': 'B Regency'}]})
        c1 = self.repo.commit({CITY: [city(2, 'B Town'), city(3, 'B Town')]})
        c2 = self.repo.commit({CITY: [city(3, 'B Town')]})
        repurpose = identity_event(2, c1, city(2, 'B Regency'), 'repurpose', [target('counties', 9, 'prior_identity')])
        fix = {'identity_event_commit': c1, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'}
        retire = removal('cities', 2, c2, c1, CITY, city(2, 'B Town'), 'merged_same_entity', [target('cities', 3, 'merged_same_entity')],
                         retires_repurpose=fix)
        self.refused(c0, c2, [repurpose, retire], 'must first appear after the repurpose')
        self.gen(c0, c2, [repurpose, dict(retire, retires_repurpose={**fix, 'replacement_kind': 'existing'})])

    def test_restored_replacement_is_not_fresh(self):
        """An id retired and restored before the repurpose was used before: 'fresh' is refused, 'existing' accepted."""
        counties = 'contributions/counties/XX.json'
        three = city(3, 'B Town', wikiDataId='Q3')
        c0 = self.repo.commit({**self.base_files, CITY: [city(2, 'B Regency'), three], counties: [{'id': 9, 'name': 'B Regency'}]})
        c1 = self.repo.commit({CITY: [city(2, 'B Regency')]})
        c2 = self.repo.commit({CITY: [city(2, 'B Town')]})
        c3 = self.repo.commit({CITY: [city(2, 'B Town'), three]})
        c4 = self.repo.commit({CITY: [three]})
        events = [removal('cities', 3, c1, c0, CITY, three, 'no_successor', []),
                  identity_event(2, c2, city(2, 'B Regency'), 'repurpose', [target('counties', 9, 'prior_identity')]),
                  restoration('cities', 3, c3, c1, three, three, {'wikiDataId': 'Q3'})]
        fix = {'identity_event_commit': c2, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'}
        retire = removal('cities', 2, c4, c3, CITY, city(2, 'B Town'), 'merged_same_entity', [target('cities', 3, 'merged_same_entity')],
                         retires_repurpose=fix)
        self.refused(c0, c4, events + [retire], 'must first appear after the repurpose')
        self.gen(c0, c4, events + [dict(retire, retires_repurpose={**fix, 'replacement_kind': 'existing'})])

    def test_second_repurpose_needs_the_first_remediated(self):
        """An id repurposed twice before the first repurpose is remediated is refused, wherever the events fall."""
        counties = 'contributions/counties/XX.json'
        c0 = self.repo.commit({**self.base_files, CITY: [city(2, 'A')], counties: [{'id': 8, 'name': 'B'}, {'id': 9, 'name': 'A'}]})
        c1 = self.repo.commit({CITY: [city(2, 'B')]})
        c2 = self.repo.commit({CITY: [city(2, 'C')]})
        c3 = self.repo.commit({CITY: [city(3, 'C')]})
        fix = {'identity_event_commit': c2, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'}
        events = [identity_event(2, c1, city(2, 'A'), 'repurpose', [target('counties', 9, 'prior_identity')]),
                  identity_event(2, c2, city(2, 'B'), 'repurpose', [target('counties', 8, 'prior_identity')]),
                  removal('cities', 2, c3, c2, CITY, city(2, 'C'), 'merged_same_entity', [target('cities', 3, 'merged_same_entity')],
                          retires_repurpose=fix)]
        for frm in (c0, c2):
            self.refused(frm, c3, events, 'repurposed again')

    def test_events_off_the_release_line_are_refused(self):
        """An event on a branch that never joined the release line is refused, not ignored."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        self.repo.run('checkout', '-q', '-b', 'side')
        s1 = self.repo.commit({CITY: [city(1, 'One')]})
        self.repo.run('checkout', '-q', 'main')
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town'), city(2, 'Two')]})
        held = dict(removal('cities', 2, s1, c0, CITY, city(2, 'Two'), 'no_successor', []), review_status='held')
        self.refused(c0, c1, [held], 'not on the release line')

    def test_earlier_events_are_checked_against_history(self):
        """An earlier removal that did not happen, or whose before row does not match, is refused."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        good = removal('cities', 2, c1, c0, CITY, city(2, 'Two'), 'no_successor', [])
        self.gen(c1, c2, [good])
        self.refused(c1, c2, [dict(good, before_row_sha256='0' * 64)], 'before_row_sha256 does not match')
        self.refused(c1, c2, [removal('cities', 1, c1, c0, CITY, city(1, 'One'), 'no_successor', [])], 'no such removal')

    def test_earlier_events_get_the_same_checks(self):
        """Before --from, a missing target, a held removal or identity event, a held event for a removal that never
        happened, and a duplicate id in the history are refused, as they would be inside the interval."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        c3 = self.repo.commit({CITY: [city(1, 'One', type='village')]})
        missing = removal('cities', 2, c1, c0, CITY, city(2, 'Two'), 'merged_same_entity', [target('cities', 999, 'merged_same_entity')])
        self.refused(c2, c3, [missing], 'target cities 999 does not exist')
        held = dict(removal('cities', 2, c1, c0, CITY, city(2, 'Two'), 'no_successor', []), review_status='held')
        self.refused(c2, c3, [held], 'held, not reviewed')
        ghost = dict(removal('cities', 7, c1, c0, CITY, city(7, 'Ghost'), 'no_successor', []), review_status='held')
        self.refused(c2, c3, [ghost], 'no such removal')
        dual = identity_event(1, c2, city(1, 'One'), 'dual_role', [target('counties', 999, 'moved_dataset')])
        self.refused(c2, c3, [dual], 'identity target counties 999 does not exist')
        self.refused(c2, c3, [dict(identity_event(1, c2, city(1, 'One'), 'classification', []), review_status='held')], 'identity event is held')
        d0 = self.repo.commit({CITY: [city(1, 'One'), city(5, 'Five'), city(5, 'Five again')]})
        d1 = self.repo.commit({CITY: [city(1, 'One')]})
        d2 = self.repo.commit({CITY: [city(1, 'One', type='city')]})
        twice = removal('cities', 5, d1, d0, CITY, city(5, 'Five again'), 'no_successor', [])
        self.refused(d1, d2, [twice], 'cities id 5 is duplicated')

    def test_restoration_brings_back_the_same_entity(self):
        """A retired id may return only with a reviewed restoration bound to its retirement and the same identity;
        it is then an addition marked restored, accepted at a later --from, and unreviewed returns still fail."""
        old, new = city(2, 'Two', wikiDataId='Q2'), city(2, 'Two', wikiDataId='Q2', type='town')
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), old]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One'), new]})
        c3 = self.repo.commit({CITY: [city(1, 'One'), city(2, 'Two', wikiDataId='Q2', type='village')]})
        retire = removal('cities', 2, c1, c0, CITY, old, 'no_successor', [])
        back = restoration('cities', 2, c2, c1, old, new, {'wikiDataId': 'Q2'})
        self.refused(c1, c2, [retire], 'in use again')
        (_, _, added, *_), _ = self.gen(c1, c2, [retire, back])
        self.assertEqual(added[0]['restored'], {'event_commit': c2, 'retirement_commit': c1})
        (removed, _, added, _, _, per_table, _), _ = self.gen(c0, c2, [retire, back])
        self.assertEqual((removed[0]['present_at_to'], removed[0]['restored_at'], added), (True, c2, []))
        self.gen(c2, c3, [retire, back])
        self.reserved.write_text(json.dumps({'table': 'cities', 'id': 2}) + '\n')
        self.gen(c1, c2, [back])
        self.refused(c1, c2, [restoration('cities', 2, c2, c1, old, new, {'wikiDataId': 'Q9'})], 'wikiDataId is not')
        self.refused(c1, c2, [dict(back, restored_row_sha256='0' * 64)], 'restored_row_sha256 does not match')
        self.refused(c1, c2, [dict(back, retirement_commit=c2)], 'not earlier on the first-parent line')

    def test_restoration_cannot_undo_a_repurpose_retirement(self):
        """The row removed to remediate a repurpose is the later entity: restoring it under the old id is refused,
        wherever the restoration falls."""
        counties = 'contributions/counties/XX.json'
        a, b = city(2, 'A', wikiDataId='Q2'), city(2, 'B', wikiDataId='Q3')
        c0 = self.repo.commit({**self.base_files, CITY: [a], counties: [{'id': 9, 'name': 'A'}]})
        c1 = self.repo.commit({CITY: [b]})
        c2 = self.repo.commit({CITY: [city(3, 'B', wikiDataId='Q3')]})
        c3 = self.repo.commit({CITY: [b, city(3, 'B', wikiDataId='Q3')]})
        c4 = self.repo.commit({CITY: [b, city(3, 'B', wikiDataId='Q3', type='town')]})
        fix = {'identity_event_commit': c1, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'}
        events = [identity_event(2, c1, a, 'repurpose', [target('counties', 9, 'prior_identity')]),
                  removal('cities', 2, c2, c1, CITY, b, 'merged_same_entity', [target('cities', 3, 'merged_same_entity')],
                          retires_repurpose=fix),
                  restoration('cities', 2, c3, c2, b, b, {'wikiDataId': 'Q3'})]
        for frm in (c0, c3):
            self.refused(frm, c4, events, 'cannot restore the later entity')

    def test_restoration_must_name_the_latest_retirement(self):
        """A restoration bound to an older retirement of the id is refused once the id has left again since."""
        counties = 'contributions/counties/XX.json'
        a, b = city(2, 'A', wikiDataId='Q2'), city(2, 'B', wikiDataId='Q3')
        c0 = self.repo.commit({**self.base_files, CITY: [a], counties: [{'id': 9, 'name': 'A'}]})
        c1 = self.repo.commit({CITY: []})
        c2 = self.repo.commit({CITY: [a]})
        c3 = self.repo.commit({CITY: [b]})
        c4 = self.repo.commit({CITY: [city(3, 'B', wikiDataId='Q3')]})
        c5 = self.repo.commit({CITY: [a, city(3, 'B', wikiDataId='Q3')]})
        fix = {'identity_event_commit': c3, 'replacement': {'table': 'cities', 'id': 3}, 'replacement_kind': 'fresh'}
        events = [removal('cities', 2, c1, c0, CITY, a, 'no_successor', []),
                  restoration('cities', 2, c2, c1, a, a, {'wikiDataId': 'Q2'}),
                  identity_event(2, c3, a, 'repurpose', [target('counties', 9, 'prior_identity')]),
                  removal('cities', 2, c4, c3, CITY, b, 'merged_same_entity', [target('cities', 3, 'merged_same_entity')],
                          retires_repurpose=fix),
                  restoration('cities', 2, c5, c1, a, a, {'wikiDataId': 'Q2'})]
        self.refused(c0, c5, events, 'is not the latest disappearance')

    def test_restored_id_that_leaves_again_needs_a_new_restoration(self):
        """After a reviewed restoration, a later disappearance retires the id again, even before --from without a
        ledger event, so an unreviewed return is refused."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two', wikiDataId='Q2')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One'), city(2, 'Two', wikiDataId='Q2')]})
        c3 = self.repo.commit({CITY: [city(1, 'One')]})
        c4 = self.repo.commit({CITY: [city(1, 'One'), city(2, 'Else', wikiDataId='Q3')]})
        c5 = self.repo.commit({CITY: [city(1, 'One', type='town'), city(2, 'Else', wikiDataId='Q3')]})
        events = [removal('cities', 2, c1, c0, CITY, city(2, 'Two', wikiDataId='Q2'), 'no_successor', []),
                  restoration('cities', 2, c2, c1, city(2, 'Two', wikiDataId='Q2'), city(2, 'Two', wikiDataId='Q2'), {'wikiDataId': 'Q2'})]
        self.refused(c4, c5, events, 'in use again')

    def test_restoration_needs_a_matching_stable_identifier(self):
        """same_identity must bind a stable identifier; a shared country is not enough, and a conflicting identifier
        held by both rows refuses the restoration."""
        schema = restoration('cities', 2, 'a' * 40, 'b' * 40, city(2, 'Two'), city(2, 'Two'), {'country_code': 'XX'})
        self.assertTrue(event_errors(schema, 'e'))
        self.assertTrue(event_errors(dict(schema, same_identity={'wikiDataId': ' '}), 'e'))
        old, new = city(2, 'Two', wikiDataId='Q2', iso3166_2='XX-2'), city(2, 'Other', wikiDataId='Q99', iso3166_2='XX-2')
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), old]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One'), new]})
        events = [removal('cities', 2, c1, c0, CITY, old, 'no_successor', []),
                  restoration('cities', 2, c2, c1, old, new, {'iso3166_2': 'XX-2'})]
        self.refused(c0, c2, events, 'wikiDataId differs')

    def test_unreviewed_return_before_from_is_refused(self):
        """An id retired by a reviewed event that returns without a restoration is refused even when it leaves again
        before --from."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two', wikiDataId='Q2')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({CITY: [city(1, 'One'), city(2, 'Else', wikiDataId='Q99')]})
        c3 = self.repo.commit({CITY: [city(1, 'One')]})
        c4 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        events = [removal('cities', 2, c1, c0, CITY, city(2, 'Two', wikiDataId='Q2'), 'no_successor', []),
                  removal('cities', 2, c3, c2, CITY, city(2, 'Else', wikiDataId='Q99'), 'no_successor', [])]
        for frm in (c0, c3):
            self.refused(frm, c4, events, 'in use again')

    def test_restoration_retirement_is_read_over_the_whole_table(self):
        """A retirement that deleted one copy of an id still present in another file is not a retirement."""
        other, old = 'contributions/cities/YY.json', city(2, 'Two', wikiDataId='Q2')
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), old], other: [old]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        c2 = self.repo.commit({other: []})
        c3 = self.repo.commit({CITY: [city(1, 'One'), old]})
        self.refused(c2, c3, [restoration('cities', 2, c3, c1, old, old, {'wikiDataId': 'Q2'})], 'cities id 2 is duplicated')

    def test_restoration_resumes_target_resolution(self):
        """A merge into an id that later retires and is restored maps to the restored id, never automatically; a
        second retirement ends the path again."""
        two = city(2, 'Two', wikiDataId='Q2')
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), two]})
        c1 = self.repo.commit({CITY: [two]})
        c2 = self.repo.commit({CITY: []})
        c3 = self.repo.commit({CITY: [two]})
        c4 = self.repo.commit({CITY: []})
        events = [removal('cities', 1, c1, c0, CITY, city(1, 'One'), 'merged_same_entity', [target('cities', 2, 'merged_same_entity')], auto=True),
                  removal('cities', 2, c2, c1, CITY, two, 'no_successor', []),
                  restoration('cities', 2, c3, c2, two, two, {'wikiDataId': 'Q2'})]
        (removed, rows, *_), _ = self.gen(c0, c3, events)
        back = {'table': 'cities', 'id': 2, 'automatic_redirect': False}
        self.assertEqual([r['current_targets'] for r in removed], [[{**back, 'relations': ['merged_same_entity', 'restored']}],
                                                                   [{**back, 'relations': ['restored']}]])
        self.assertEqual([(r[1], r[7], r[9], r[10]) for r in rows], [(1, 2, 'merged_same_entity>restored', 'no'), (2, 2, 'restored', 'no')])
        again = removal('cities', 2, c4, c3, CITY, two, 'no_successor', [])
        (removed, *_), _ = self.gen(c0, c4, events + [again], out='out2')
        self.assertEqual(removed[0]['current_targets'], [{'table': None, 'id': None, 'end': 'no_successor',
                                                          'relations': ['merged_same_entity', 'restored'], 'automatic_redirect': False}])

    def test_runs_from_a_subdirectory(self):
        """--repo may name any folder inside the repository: pathspecs resolve from its top level, so a run from a
        subdirectory reads the same files instead of an empty tree."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        events = [removal('cities', 2, c1, c0, CITY, city(2, 'Two'), 'no_successor', [])]
        ledger = self.dir / 'events.jsonl'
        ledger.write_text(''.join(json.dumps(e) + '\n' for e in events))
        (removed, _, _, _, changed, per_table, _), _ = generate(self.repo.root / 'contributions' / 'cities', c0, c1, ledger,
                                                                self.reserved, self.meta, self.dir / 'sub')
        self.assertEqual(([r['old_id'] for r in removed], len(changed), per_table['cities']['from_total']), ([2], 1, 2))

    def test_reads_use_the_resolved_sha(self):
        """After resolving --to once, no git read uses the movable branch name."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        self.repo.commit({CITY: [city(1, 'One', type='town')]})
        self.repo.run('branch', 'moving')
        calls, real = [], m.git
        m.git = lambda repo, *args: calls.append(args) or real(repo, *args)
        try:
            self.gen(c0, 'moving', [])
        finally:
            m.git = real
        self.assertEqual([a for a in calls if any('moving' in str(x) for x in a)], [('rev-parse', '--verify', '--quiet', 'moving^{commit}')])

    def test_future_event_when_to_is_the_root(self):
        """A later release's event is ignored when --to is the root commit, with or without it."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One'), city(2, 'Two')]})
        c1 = self.repo.commit({CITY: [city(1, 'One')]})
        later = dict(removal('cities', 2, c1, c0, CITY, city(2, 'Two'), 'no_successor', []), review_status='held')
        self.gen(c0, c0, [later])
        self.gen(c0, c0, [], out='out2')

    def test_held_identity_with_malformed_prior_entity(self):
        """A held identity event's prior_entity is never read: a malformed one waits harmlessly in a later release and,
        inside the interval, the event is refused as held rather than crashing the walk."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        for n, bad in enumerate((None, [], 'ended', {'recorded_later': 'x'}, {'recorded_later': {'event_commit': 7}})):
            held = dict(identity_event(1, c1, city(1, 'One'), 'repurpose', []), review_status='held', prior_entity=bad)
            self.gen(c0, c0, [held], out=f'held{n}')
            self.refused(c0, c1, [held], 'identity event is held')

    def cli(self, ledger, meta=None):
        """Run the command line on the scratch repository; returns (exit code, stderr)."""
        err = io.StringIO()
        with redirect_stderr(err):
            code = m.main(['--from', 'HEAD', '--to', 'HEAD', '--ledger', str(ledger), '--reserved', str(self.reserved),
                           '--meta', str(meta or self.meta), '--out', str(self.dir / 'cli'), '--repo', str(self.repo.root)])
        return code, err.getvalue()

    def test_cli_names_inputs_that_are_not_utf8(self):
        """A bad byte in the ledger, the release metadata or a source file exits 1 naming the input, with no traceback."""
        self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        bad = self.dir / 'bad.jsonl'
        bad.write_bytes(b'{"x": "\xff"}\n')
        self.assertEqual(self.cli(bad)[0], 1)
        self.assertIn('not UTF-8', self.cli(bad)[1])
        empty, meta = self.dir / 'empty.jsonl', self.dir / 'bad_meta.json'
        empty.write_text('')
        meta.write_bytes(b'{"data_version": "\xff"}')
        self.assertIn('release metadata', self.cli(empty, meta)[1])
        (self.repo.root / CITY).write_bytes(b'[{"id": 1, "name": "\xff"}]')
        self.repo.run('add', '-A'); self.repo.run('commit', '-q', '-m', 'bad byte')
        code, err = self.cli(empty)
        self.assertEqual(code, 1)
        self.assertIn(f'{CITY} at', err)
        self.assertNotIn('Traceback', err)

    def test_cli_refuses_a_malformed_ledger(self):
        """A target without a relation makes the command exit 1 with a readable message."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        ledger = self.dir / 'bad.jsonl'
        ledger.write_text(json.dumps({**removal('cities', 2, c0, c0, CITY, city(2, 'X'), 'merged_same_entity', []),
                                      'targets': [{'table': 'cities', 'id': 1}]}) + '\n')
        err = io.StringIO()
        with redirect_stderr(err):
            code = m.main(['--from', c0, '--to', c0, '--ledger', str(ledger), '--reserved', str(self.reserved),
                           '--meta', str(self.meta), '--out', str(self.dir / 'cli'), '--repo', str(self.repo.root)])
        self.assertEqual(code, 1)
        self.assertIn('ledger line 1', err.getvalue())
        self.assertFalse((self.dir / 'cli').exists())


class RobustnessTest(Case):
    """Malformed numbers, deep chains, write failures and diagnostics."""

    def test_nan_in_source_is_refused(self):
        """NaN is not JSON: a source file holding it is refused before anything is written."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        (self.repo.root / CITY).write_text('[{"id": 1, "name": "One", "country_code": "XX", "state_code": "AA", "population": NaN}]')
        self.repo.run('add', '-A'); self.repo.run('commit', '-q', '-m', 'nan')
        self.refused(c0, self.repo.run('rev-parse', 'HEAD'), [], 'invalid JSON')

    def test_branching_chain_is_not_a_cycle(self):
        """Seven levels in which two units are each split into the same next two resolve to those two, listed once."""
        gate = m.Gate({}, {})
        for level in range(7):
            for unit in (2 * level + 1, 2 * level + 2):
                gate.timeline[('cities', unit)].append((level + 1, 'removal', {
                    'outcome': 'split_into', 'automatic_redirect': False,
                    'targets': [target('cities', 2 * level + 3, 'split_into'), target('cities', 2 * level + 4, 'split_into')]}))
        got = m.resolve_targets(gate, {('cities', 15): {}, ('cities', 16): {}}, [target('cities', 1, 'split_into')], 0, False)
        self.assertEqual(sorted(x['id'] for x in got), [15, 16])

    def test_long_chain_without_recursion(self):
        """A valid chain longer than Python's recursion limit resolves."""
        gate = m.Gate({}, {}, set())
        n = sys.getrecursionlimit() + 500
        for i in range(1, n):
            gate.timeline[('cities', i)].append((i, 'removal', {'targets': [target('cities', i + 1, 'merged_same_entity')], 'automatic_redirect': True, 'outcome': 'merged_same_entity'}))
        got = m.resolve_targets(gate, {('cities', n): {}}, [target('cities', 1, 'merged_same_entity')], 0, True)
        self.assertEqual((got[0]['id'], len(got[0]['relations']), got[0]['automatic_redirect']), (n, n, True))

    def test_write_failure_keeps_the_earlier_output(self):
        """When the files cannot be written, the earlier complete output stays and the error says where it is."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        _, out = self.gen(c0, c1, [])
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        with mock.patch.object(m.csv, 'writer', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(m.OutputError, 'last complete output is in'):
                self.gen(c0, c1, [])
        self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, before)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir() if p.name.startswith('.out')), [])

    def test_restart_after_an_interrupted_swap(self):
        """A run stopped between the two renames left the last output in .out.previous; the next run puts it back
        first, so a failure then still leaves it in place, and a good run replaces it."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        c1 = self.repo.commit({CITY: [city(1, 'One', type='town')]})
        _, out = self.gen(c0, c1, [])
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        out.rename(self.dir / '.out.previous')
        with mock.patch.object(m.csv, 'writer', side_effect=OSError('disk full')):
            with self.assertRaises(m.OutputError):
                self.gen(c0, c1, [])
        self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, before)
        out.rename(self.dir / '.out.previous')
        self.gen(c0, c1, [])
        self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()}, before)
        self.assertFalse((self.dir / '.out.previous').exists())

    def test_idless_rows_are_located(self):
        """Rows still without an id at --to are named by file and row."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'One')]})
        c1 = self.repo.commit({'contributions/cities/YY.json': [{'name': 'New'}]})
        self.refused(c0, c1, [], 'contributions/cities/YY.json row 0')


class BaselineTest(Case):
    """Snapshot disclosures and later decisions work even when no scalar changes."""

    def baseline(self, commit, row, **changes):
        """Write one reviewed unresolved snapshot; return its input object."""
        entry = {'schema_version': 1, 'table': 'cities', 'id': row['id'], 'baseline_commit': commit,
                 'row_sha256': row_hash(row), 'outcome': 'unresolved', 'reason': 'original scope unproved',
                 'decision_round': '4c', 'review_status': 'reviewed',
                 'review': {'reviewer': 'test', 'reason': 'reviewed legacy hold'},
                 'evidence': [{'url': 'https://example.invalid/decision'}], **changes}
        (self.dir / 'unresolved_baseline.jsonl').write_text(json.dumps(entry) + '\n')
        return entry

    def test_unchanged_legacy_row_is_published(self):
        """A row identical to --from still gets a baseline identity and reconciled output hashes/counts."""
        row = city(1, 'Legacy')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({})
        self.baseline(c1, row)
        content, out = self.gen(c0, c1, [])
        self.assertEqual(content[4], [])
        e, = content[3]
        self.assertTrue(e['baseline'])
        self.assertEqual((e['before'], e['after'], e['present_at_to']), (row, row, True))
        manifest = json.loads((out / 'release_manifest.json').read_text())
        self.assertEqual(manifest['tables']['cities']['identity_events'], 1)
        self.assertEqual(manifest['migration_format_version'], 3)
        self.assertEqual(manifest['unresolved_baseline']['keys'], 1)
        self.assertEqual(manifest['files']['identity_changes.jsonl'], m.hashlib.sha256((out / 'identity_changes.jsonl').read_bytes()).hexdigest())

    def test_baseline_validation_refuses_bad_inputs(self):
        """Bad keys, empty provenance, wrong guards, duplicates and mixed anchors cannot be published."""
        row = city(1, 'Legacy')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({})
        for changes in ({'id': True}, {'reason': ' '}, {'decision_round': ''}, {'evidence': []},
                        {'review_status': 'held'}, {'outcome': 'classification'}, {'row_sha256': 'bad'}):
            with self.subTest(changes=changes):
                self.baseline(c1, row, **changes)
                self.refused(c0, c1, [], 'unresolved baseline')
        for changes in ({'row_sha256': '0' * 64}, {'id': 9}):
            self.baseline(c1, row, **changes)
            self.refused(c0, c1, [], 'baseline row missing or row_sha256')
        e = self.baseline(c1, row)
        path = self.dir / 'unresolved_baseline.jsonl'
        for second in (e, {**e, 'id': 2, 'baseline_commit': c0}):
            path.write_text(json.dumps(e) + '\n' + json.dumps(second) + '\n')
            self.refused(c0, c1, [], 'duplicate key or mixed')

    def test_merge_into_baseline_key_is_not_automatic(self):
        """A merge made after the baseline into a key it lists never redirects automatically, cumulative or step."""
        one, twin = city(1, 'One'), city(2, 'Twin')
        c0 = self.repo.commit({**self.base_files, CITY: [one, twin]})
        c1 = self.repo.commit({}, 'baseline')
        c2 = self.repo.commit({CITY: [one]})
        self.baseline(c1, one)
        ev = removal('cities', 2, c2, c1, CITY, twin, 'merged_same_entity', [target('cities', 1, 'merged_same_entity')], auto=True)
        for frm, out in ((c0, 'cumulative'), (c1, 'step')):
            content, _ = self.gen(frm, c2, [ev], out=out)
            self.assertEqual(content[0][0]['current_targets'],
                             [{'table': 'cities', 'id': 1, 'relations': ['merged_same_entity'], 'automatic_redirect': False}])

    def test_merge_redirect_follows_latest_identity_decision(self):
        """A key classified before the merge redirects automatically; reopened as unresolved before it, it does not."""
        one, twin = city(1, 'One'), city(2, 'Twin')
        c0 = self.repo.commit({**self.base_files, CITY: [one, twin]})
        c1 = self.repo.commit({}, 'baseline')
        c2 = self.repo.commit({}, 'classified')
        c3 = self.repo.commit({}, 'reopened')
        c4 = self.repo.commit({CITY: [one]})
        self.baseline(c1, one)
        review = lambda c, outcome: dict(identity_event(1, c, one, outcome, []), decision_only=True, after_row_sha256=row_hash(one))
        merge = removal('cities', 2, c4, c3, CITY, twin, 'merged_same_entity', [target('cities', 1, 'merged_same_entity')], auto=True)
        content, _ = self.gen(c0, c4, [review(c2, 'classification'), merge], out='classified')
        self.assertTrue(content[0][0]['current_targets'][0]['automatic_redirect'])
        for frm, out in ((c0, 'reopened'), (c3, 'reopened_step')):
            content, _ = self.gen(frm, c4, [review(c2, 'classification'), review(c3, 'unresolved'), merge], out=out)
            self.assertFalse(content[0][0]['current_targets'][0]['automatic_redirect'])

    def test_missing_inventory_fails_closed(self):
        """Accidentally omitting the baseline file cannot produce an apparently complete release."""
        c0 = self.repo.commit({**self.base_files, CITY: [city(1, 'Legacy')]})
        (self.dir / 'unresolved_baseline.jsonl').unlink()
        with self.assertRaises(FileNotFoundError):
            self.gen(c0, c0, [])

    def test_future_and_off_line_snapshots(self):
        """A later snapshot waits; an unrelated commit or invented SHA is rejected."""
        row = city(1, 'Legacy')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({})
        self.baseline(c1, row)
        content, _ = self.gen(c0, c0, [])
        self.assertEqual(content[3], [])
        self.baseline('f' * 40, row)
        self.refused(c0, c1, [], 'not on the release line')
        self.repo.run('checkout', '-q', '-b', 'side', c0)
        side = self.repo.commit({}, 'side')
        self.baseline(side, row)
        self.refused(c0, c1, [], 'not on the release line')

    def test_root_and_step_intervals_validate_without_repeating(self):
        """An anchor at the root or exactly --from is checked but is not repeated in a later step file."""
        row = city(1, 'Legacy')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({})
        self.baseline(c0, row)
        content, _ = self.gen(c0, c1, [])
        self.assertEqual(content[3], [])
        self.baseline(c0, row, row_sha256='0' * 64)
        self.refused(c0, c1, [], 'row_sha256')

    def test_later_review_without_data_edit_resolves_in_order(self):
        """A guarded decision on an unchanged row follows the baseline; a step carries only the new decision."""
        row = city(1, 'Legacy')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({})
        c2 = self.repo.commit({}, 'identity review')
        self.baseline(c1, row)
        ev = dict(identity_event(1, c2, row, 'classification', []), decision_only=True, after_row_sha256=row_hash(row))
        content, _ = self.gen(c0, c2, [ev])
        self.assertEqual([e['outcome'] for e in content[3]], ['unresolved', 'classification'])
        content, _ = self.gen(c1, c2, [ev], out='step')
        self.assertEqual([e['outcome'] for e in content[3]], ['classification'])
        self.refused(c0, c2, [dict(ev, after_row_sha256='0' * 64)], 'after_row_sha256')
        self.refused(c0, c2, [identity_event(1, c2, row, 'classification', [])], 'did not change there')
        for changes in ({'decision_only': 'true'}, {'decision_only': False}, {'outcome': 'repurpose'},
                        {'after_row_sha256': None}):
            self.assertTrue(event_errors({**ev, **changes}, 'e'))

    def test_later_removal_clears_active_hold(self):
        """A cumulative file preserves the historical disclosure, while the reviewed removal retires the key."""
        row = city(1, 'Legacy')
        c0 = self.repo.commit({**self.base_files, CITY: [row]})
        c1 = self.repo.commit({})
        c2 = self.repo.commit({CITY: []})
        self.baseline(c1, row)
        ev = removal('cities', 1, c2, c1, CITY, row, 'no_successor', [])
        content, _ = self.gen(c0, c2, [ev])
        self.assertFalse(content[3][0]['present_at_to'])
        self.assertEqual(content[0][0]['old_id'], 1)
        self.baseline(c2, row)
        self.refused(c0, c2, [ev], 'baseline row missing')

    def test_repurpose_and_same_commit_conflicts_are_refused(self):
        """A known transfer cannot be masked by an unresolved snapshot, nor can two decisions share its position."""
        old, later = city(1, 'Old'), city(1, 'Other')
        c0 = self.repo.commit({**self.base_files, CITY: [old]})
        c1 = self.repo.commit({CITY: [later]})
        ev = dict(identity_event(1, c1, old, 'repurpose', []), prior_entity={
            'status': 'unrecorded', 'reason': 'separate original', 'evidence': [{'url': 'https://example.invalid/original'}]})
        self.baseline(c1, later)
        self.refused(c0, c1, [ev], 'baseline key was repurposed')
        self.refused(c0, c1, [identity_event(1, c1, old, 'classification', [])], 'baseline conflicts')


if __name__ == '__main__':
    unittest.main()
