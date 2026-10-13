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


if __name__ == '__main__':
    unittest.main()
