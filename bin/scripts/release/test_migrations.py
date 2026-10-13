"""Tests for the release migration generator (migrations.py), on scratch git repositories."""
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

import migrations as m
from migrations import MigrationError, event_errors, field_changes, generate, row_hash

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
            'automatic_redirect': auto, 'review_status': 'reviewed', 'evidence': [{'note': 'test'}],
            'review': {'reason': 'test', 'reviewer': 'test'}, **extra}


def target(table, i, relation):
    """One event target."""
    return {'table': table, 'id': i, 'relation': relation}


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
        self.reserved = self.dir / 'reserved.jsonl'
        self.reserved.write_text('')
        self.meta = self.dir / 'meta.json'
        self.meta.write_text(json.dumps({'data_version': '5.0.0', 'contract_version': '5', 'policy_version': '1',
                                         'data_schema_version': '5', 'notices': ['NOTICE']}))

    def gen(self, frm, to, events, out='out'):
        """Run generate() with these ledger events; returns (content, out path)."""
        ledger = self.dir / 'events.jsonl'
        ledger.write_text(''.join(json.dumps(e) + '\n' for e in events))
        content, _ = generate(self.repo.root, frm, to, ledger, self.reserved, self.meta, self.dir / out)
        return content, self.dir / out

    def refused(self, frm, to, events, pattern):
        """Assert generate() refuses with a message matching the pattern and writes nothing."""
        with self.assertRaisesRegex(MigrationError, pattern):
            self.gen(frm, to, events, out='refused')
        self.assertFalse((self.dir / 'refused').exists())


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
                        'short commit': self.base(event_commit='abc'), 'bad before': self.base(before=city(2, 'Other')),
                        'float id': self.base(old_id=2.0), 'bool id': self.base(old_id=True)}.items():
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
        self.assertEqual(per_table['cities'], {'from_total': 2, 'to_total': 2, 'removed': 1, 'added': 1, 'changed_records': 1,
                                               'removal_events': 1, 'created_and_removed_in_interval': 0})
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
        c1 = self.repo.commit({CITY: [city(1, 'Seat town'), city(2, 'Two')]})
        ev = {'schema_version': 1, 'event_type': 'identity', 'table': 'cities', 'id': 1, 'event_commit': c1,
              'before_row_sha256': row_hash(city(1, 'Regency')), 'outcome': 'repurposed',
              'targets': [target('cities', 2, 'prior_identity')], 'automatic_redirect': False,
              'review_status': 'reviewed', 'evidence': [{'note': 'test'}], 'review': {'reason': 'test', 'reviewer': 'test'}}
        (_, _, _, identity, *_), out = self.gen(c0, c1, [ev])
        self.assertEqual((identity[0]['before']['name'], identity[0]['after']['name']), ('Regency', 'Seat town'))
        c2 = self.repo.commit({'contributions/cities/YY.json': []})
        self.refused(c0, c2, [dict(ev, event_commit=c2)], 'did not change there')

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


if __name__ == '__main__':
    unittest.main()
