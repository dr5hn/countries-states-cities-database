"""Tests for the release migration checks and files (migrations.py)."""
import json
import tempfile
import unittest
from pathlib import Path

from migrations import build, check, field_changes, write

OLD = {('cities', 1): {'id': 1, 'name': 'Unit row', 'type': 'city'},
       ('cities', 2): {'id': 2, 'name': 'Seat', 'type': 'city', 'translations': {'de': 'Sitz', 'fr': 'Siège'}},
       ('cities', 3): {'id': 3, 'name': 'Twin'},
       ('cities', 4): {'id': 4, 'name': 'Twin'}}
NEW = {('cities', 2): {'id': 2, 'name': 'Seat', 'type': 'town', 'translations': {'de': 'Sitz', 'es': 'Sede'}},
       ('cities', 3): {'id': 3, 'name': 'Twin'},
       ('counties', 9): {'id': 9, 'name': 'The unit'}}
EVENTS = {('cities', 1): {'old_table': 'cities', 'old_id': 1, 'outcome': 'moved_dataset', 'review_status': 'reviewed',
                          'automatic_redirect': False, 'targets': [{'table': 'counties', 'id': 9, 'relation': 'moved_dataset'},
                                                                   {'table': 'cities', 'id': 2, 'relation': 'administrative_seat'}]},
          ('cities', 4): {'old_table': 'cities', 'old_id': 4, 'outcome': 'merged_same_entity', 'review_status': 'reviewed',
                          'automatic_redirect': True, 'targets': [{'table': 'cities', 'id': 3, 'relation': 'merged_same_entity'}]}}


class CheckTest(unittest.TestCase):
    """Every removal must be explained by a reviewed event with real targets."""

    def test_explained_removals_pass(self):
        """Two removals, each with a reviewed event and existing targets."""
        self.assertEqual(check(OLD, NEW, EVENTS), [])

    def test_missing_event_fails(self):
        """A removal with no event is reported."""
        events = {k: v for k, v in EVENTS.items() if k != ('cities', 4)}
        self.assertIn('cities 4 was removed but has no ledger event', check(OLD, NEW, events))

    def test_unreviewed_event_fails(self):
        """A held event (outcome null) is not enough."""
        events = {**EVENTS, ('cities', 4): dict(EVENTS[('cities', 4)], outcome=None, review_status='held')}
        self.assertTrue(any('not reviewed' in e for e in check(OLD, NEW, events)))

    def test_missing_target_fails(self):
        """A target that does not exist in the new snapshot is reported."""
        events = {**EVENTS, ('cities', 4): dict(EVENTS[('cities', 4)], targets=[{'table': 'cities', 'id': 99, 'relation': 'x'}])}
        self.assertTrue(any('target cities 99 does not exist' in e for e in check(OLD, NEW, events)))

    def test_redirect_only_for_same_place(self):
        """A redirect on a unit-to-seat relation is refused."""
        events = {**EVENTS, ('cities', 1): dict(EVENTS[('cities', 1)], automatic_redirect=True)}
        self.assertTrue(any('automatic redirect' in e for e in check(OLD, NEW, events)))

    def test_no_target_outcomes_have_no_targets(self):
        """namespace_replaced with a target, and moved_dataset without one, are both refused."""
        events = {**EVENTS, ('cities', 1): dict(EVENTS[('cities', 1)], outcome='namespace_replaced')}
        self.assertTrue(any('must have no targets' in e for e in check(OLD, NEW, events)))
        events = {**EVENTS, ('cities', 1): dict(EVENTS[('cities', 1)], targets=[])}
        self.assertTrue(any('needs at least one target' in e for e in check(OLD, NEW, events)))

    def test_reused_id_fails(self):
        """A retired id that is in use again is reported."""
        new = {**NEW, ('cities', 4): {'id': 4, 'name': 'Something else'}}
        old = {k: v for k, v in OLD.items() if k != ('cities', 4)}
        self.assertTrue(any('retired id' in e for e in check(old, new, EVENTS)))


class BuildTest(unittest.TestCase):
    """Release files are complete and deterministic."""

    def test_field_changes_per_language(self):
        """Translations compare per language key; managed timestamps are ignored."""
        got = field_changes({'type': 'city', 'translations': {'de': 'A', 'fr': 'B'}, 'updated_at': 1},
                            {'type': 'town', 'translations': {'de': 'A', 'es': 'C'}, 'updated_at': 2})
        self.assertEqual(got, [('translations.es', None, 'C'), ('translations.fr', 'B', None), ('type', 'city', 'town')])

    def test_csv_has_one_row_per_relation(self):
        """The unit row gives two CSV rows (county and seat); the merge gives one."""
        removed, rows, changed, per_table, counts = build(OLD, NEW, EVENTS)
        self.assertEqual([r[0:2] + r[5:8] for r in rows],
                         [['cities', 1, 'counties', 9, 'moved_dataset'], ['cities', 1, 'cities', 2, 'administrative_seat'],
                          ['cities', 4, 'cities', 3, 'merged_same_entity']])
        self.assertEqual(per_table['cities'], {'removed': 2, 'added': 0, 'changed': 1})
        self.assertEqual(per_table['counties']['added'], 1)
        self.assertEqual(counts, {'cities.translations': 2, 'cities.type': 1})

    def test_files_are_deterministic(self):
        """The same inputs give byte-identical files."""
        sums = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as d:
                sums.append(write(Path(d), *build(OLD, NEW, EVENTS), {'schema_version': 1}))
        self.assertEqual(sums[0], sums[1])
        with tempfile.TemporaryDirectory() as d:
            write(Path(d), *build(OLD, NEW, EVENTS), {'schema_version': 1})
            manifest = json.loads((Path(d) / 'release_manifest.json').read_text())
            self.assertEqual(set(manifest['files']), {'removed_ids.jsonl', 'removed_ids.csv', 'changed_fields.jsonl'})


if __name__ == '__main__':
    unittest.main()
