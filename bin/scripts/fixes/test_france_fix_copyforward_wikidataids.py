#!/usr/bin/env python3
"""Tests for france_fix_copyforward_wikidataids.py. No network: the Wikidata lookups are stubbed.

    python3 -m unittest bin/scripts/fixes/test_france_fix_copyforward_wikidataids.py

TEST DATA ONLY: the records and Wikidata items below are a small hand-made fixture modelled on real FR.json
records (ids, names, departments, coordinates, populations). They live in a temp directory and are never
written to the repository.
"""
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name('france_fix_copyforward_wikidataids.py')
_spec = importlib.util.spec_from_file_location('france_fix_copyforward_wikidataids', SCRIPT)
fix = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fix)


def rec(id_, name, state_id, state_code, lat, lon, pop, qid, type_='city'):
    """One city record shaped like an FR.json record."""
    return {'id': id_, 'name': name, 'state_id': state_id, 'state_code': state_code, 'type': type_,
            'latitude': f'{lat:.8f}', 'longitude': f'{lon:.8f}', 'population': pop, 'wikiDataId': qid}


def item(insee, label, lon, lat):
    """One commune item as insee_items() returns it."""
    return {'insee': {insee: False}, 'labels': [label], 'p31': ['Q484170'], 'coords': [f'Point({lon} {lat})']}


# Abbaretz's Q1001990 was copied forward onto Abbeville and Abeilhan (a shared-QID group). Abilly holds its own
# ID outside the group. Saint-Julien is a REVIEWED record outside the group.
RECORDS = [
    rec(39234, 'Abbaretz', 5012, '44', 47.55314, -1.53200, 1627, 'Q1001990'),
    rec(39235, 'Abbeville', 5048, '80', 50.10521, 1.83547, 22406, 'Q1001990', 'adm3'),
    rec(39236, 'Abeilhan', 5002, '34', 43.44925, 3.29529, 1201, 'Q1001990'),
    rec(39237, 'Abilly', 5005, '37', 46.93333, 0.73333, 1158, 'Q1069923'),
    rec(46134, 'Saint-Julien', 5051, '83', 43.31334, 5.44935, 9939, 'Q765366', 'section'),
]
ITEMS = {
    'Q1001990': item('44001', 'Abbaretz', -1.531666666, 47.5525),
    'Q28520': item('80001', 'Abbeville', 1.835277777, 50.105277777),
    'Q200654': item('34001', 'Abeilhan', 3.294722222, 43.449722222),
    'Q1069923': item('37001', 'Abilly', 0.727777777, 46.941111111),
}


def dump(recs):
    """Serialise records the way FR.json is formatted."""
    return json.dumps(recs, ensure_ascii=False, indent=2) + '\n'


class FixScriptTest(unittest.TestCase):
    """Runs main() against the fixture in a temp directory."""

    def setUp(self):
        """Point the script at a temp FR.json, report and cache; stub the INSEE fetch; forbid network."""
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.fr, self.report = tmp / 'FR.json', tmp / 'report.json'
        self.fr.write_text(dump(RECORDS), encoding='utf-8')
        os.chmod(self.fr, 0o644)
        for name, value in (('REPO', tmp), ('FR_JSON', self.fr), ('REPORT', self.report), ('CACHE', tmp / 'cache'),
                            ('insee_items', lambda: ITEMS)):
            self.enterContext(mock.patch.object(fix, name, value))
        self.enterContext(mock.patch.object(fix, 'http_json', side_effect=AssertionError('network used in a test')))
        self.enterContext(mock.patch.object(sys, 'argv', ['france_fix_copyforward_wikidataids.py']))
        self.enterContext(mock.patch('builtins.print'))  # keep the script's log lines out of the test output

    def edit_during_planning(self, edit):
        """Make build_plan rewrite FR.json with edit(records) after planning, as another writer would."""
        real = fix.build_plan

        def planning(recs, items):
            """Plan, then let the other writer change the file before main() re-reads it."""
            result = real(recs, items)
            other = json.loads(self.fr.read_text(encoding='utf-8'))
            edit(other)
            self.fr.write_text(dump(other), encoding='utf-8')
            return result
        return mock.patch.object(fix, 'build_plan', planning)

    def qids(self):
        """{record id: wikiDataId} as FR.json now stands."""
        return {r.get('id'): r.get('wikiDataId') for r in json.loads(self.fr.read_text(encoding='utf-8'))}

    def test_applies_plan_and_rerun_changes_nothing(self):
        """The group is re-matched, the reviewed record outside it is fixed, and a rerun is a no-op."""
        fix.main()
        self.assertEqual(self.qids(), {39234: 'Q1001990', 39235: 'Q28520', 39236: 'Q200654',
                                       39237: 'Q1069923', 46134: 'Q3462652'})
        after = json.loads(self.fr.read_text(encoding='utf-8'))
        for old, new in zip(RECORDS, after):  # only wikiDataId changes
            self.assertEqual({k: v for k, v in old.items() if k != 'wikiDataId'},
                             {k: v for k, v in new.items() if k != 'wikiDataId'})
        summary = json.loads(self.report.read_text(encoding='utf-8'))['summary']
        self.assertEqual((summary['records_in_groups'], summary['reviewed_outside_groups'], summary['changed']), (3, 1, 3))
        self.assertEqual(stat.S_IMODE(self.fr.stat().st_mode), 0o644)  # the atomic replace keeps permissions
        self.assertEqual(sorted(p.name for p in self.fr.parent.iterdir()), ['FR.json', 'cache', 'report.json'])  # no temp files left

        fr_text, report_text = self.fr.read_text(encoding='utf-8'), self.report.read_text(encoding='utf-8')
        fix.main()
        self.assertEqual(self.fr.read_text(encoding='utf-8'), fr_text)
        self.assertEqual(self.report.read_text(encoding='utf-8'), report_text)

    def test_aborts_when_file_changes_during_planning(self):
        """Any edit while the lookups run aborts before anything is written, including edits to records outside
        the plan. Reviewer's case: Abilly (unplanned) takes Q28520 while Abbeville is being matched to Q28520;
        writing would leave Q28520 on two records."""
        new_record = rec(None, 'Abbeville-Saint-Lucien', 5021, '60', 49.51, 2.0, 400, 'Q28520')
        cases = {
            'unplanned record takes a planned QID': lambda recs: recs[3].update(wikiDataId='Q28520'),
            'unplanned record moves': lambda recs: recs[3].update(latitude='46.90000000'),
            'record added': lambda recs: recs.append(new_record),
            'record removed': lambda recs: recs.pop(3),
        }
        for label, edit in cases.items():
            with self.subTest(label):
                self.fr.write_text(dump(RECORDS), encoding='utf-8')
                self.report.unlink(missing_ok=True)
                with self.edit_during_planning(edit), self.assertRaises(SystemExit) as stop:
                    fix.main()
                self.assertIn('changed while planning', str(stop.exception))
                expected = json.loads(dump(RECORDS))
                edit(expected)
                self.assertEqual(json.loads(self.fr.read_text(encoding='utf-8')), expected)  # the other writer's file, untouched
                self.assertFalse(self.report.exists())
                self.assertLessEqual(list(self.qids().values()).count('Q28520'), 1)


if __name__ == '__main__':
    unittest.main()
