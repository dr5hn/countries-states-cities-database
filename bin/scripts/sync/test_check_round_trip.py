"""Tests for the round-trip gate (check_round_trip.py). No database or git needed.
Run with the sync's other tests: python3 -m unittest discover bin/scripts/sync"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from check_round_trip import compare, main

ROW = {'id': 1, 'name': 'A', 'state_id': 5, 'latitude': '1.00000000'}
NEW = {'name': 'Smara', 'state_id': None, 'state_code': None}


class CompareTest(unittest.TestCase):
    """compare() on one file's rows."""

    def assertProblem(self, expected, before, after):
        """Assert one of the problems contains the expected text."""
        problems = compare('f.json', before, after)
        self.assertTrue(any(expected in p for p in problems), f'{expected!r} not in {problems}')

    def test_unchanged_and_new_ids_pass(self):
        """Same rows pass; managed fields may differ; an id-less row may come back with its new id."""
        self.assertEqual(compare('f.json', [ROW, NEW], [dict(ROW, flag=1, updated_at='x'), dict(NEW, id=7)]), [])

    def test_changed_idless_payload(self):
        """A row imported without an id must come back as it was, not as some other row with a new id."""
        self.assertProblem('did not come back as imported', [NEW], [{'id': 7, 'name': 'DIFFERENT', 'state_id': 1457,
                                                                      'state_code': None}])
        self.assertProblem('did not come back as imported', [NEW, NEW], [dict(NEW, id=7)])   # one of two lost
        self.assertProblem('match no imported row', [ROW], [ROW, dict(NEW, id=7)])           # a row appeared

    def test_duplicate_and_invalid_ids(self):
        """Repeated or invalid ids are refused instead of collapsing in a dictionary."""
        self.assertProblem('appears more than once', [ROW, dict(ROW, name='B')], [ROW, dict(ROW, name='B')])
        self.assertProblem('appears more than once', [ROW], [ROW, ROW])
        self.assertProblem('not a positive integer', [dict(ROW, id=True)], [dict(ROW, id=True)])
        self.assertProblem('not a positive integer', [ROW], [dict(ROW, id='1')])
        self.assertProblem('is not an object', [ROW, 3], [ROW])
        self.assertProblem('not an array', {'id': 1}, [ROW])

    def test_missing_row_and_typed_values(self):
        """A missing row fails, and 1, 1.0, true and "1" are different values."""
        self.assertProblem('missing after the round trip', [ROW], [])
        for value in (5.0, True, '5', None):
            self.assertProblem('changed in the round trip', [ROW], [dict(ROW, state_id=value)])
        self.assertProblem('changed in the round trip', [ROW], [{k: v for k, v in ROW.items() if k != 'latitude'}])
        self.assertProblem('have no id after the round trip', [NEW], [NEW])


class MainTest(unittest.TestCase):
    """main() with a snapshot folder: the file sets must match and each file is compared."""

    def setUp(self):
        """contributions/ and a snapshot of it in a temporary folder."""
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        for root in ('contributions', 'snapshot'):
            Path(root, 'cities').mkdir(parents=True)
            Path(root, 'cities', 'EH.json').write_text(json.dumps([NEW]))
        Path('contributions/cities/EH.json').write_text(json.dumps([dict(NEW, id=7)]))

    def run_main(self):
        """Exit status of the gate against the snapshot."""
        with contextlib.redirect_stdout(io.StringIO()):
            return main(['--snapshot', 'snapshot'])

    def test_matching_files_pass(self):
        """The fixture's new row came back with an id: pass."""
        self.assertEqual(self.run_main(), 0)

    def test_unexpected_missing_and_changed_files(self):
        """An extra file, a missing file and a changed payload each fail."""
        Path('contributions/cities/XX.json').write_text('[]')
        self.assertEqual(self.run_main(), 1)
        Path('contributions/cities/XX.json').unlink()
        Path('snapshot/cities/YY.json').write_text('[]')
        self.assertEqual(self.run_main(), 1)
        Path('snapshot/cities/YY.json').unlink()
        Path('contributions/cities/EH.json').write_text(json.dumps([dict(NEW, id=7, name='Other')]))
        self.assertEqual(self.run_main(), 1)

    def test_missing_snapshot(self):
        """A snapshot folder that does not exist is an error, not an empty pass."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--snapshot', 'nowhere']), 1)


if __name__ == '__main__':
    unittest.main()
