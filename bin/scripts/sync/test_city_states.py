"""Tests for the reference checks (city_states.py) and their use before the import resets tables or the sync writes
files (v5: cities without a state). Run with the sync's other tests: python3 -m unittest discover bin/scripts/sync"""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from city_states import check_references

COUNTRIES = [{'id': 233, 'iso2': 'US'}, {'id': 244, 'iso2': 'EH'}]
STATES = [{'id': 1457, 'country_id': 233, 'country_code': 'US', 'iso2': 'LA'}]


def city(**k):
    """A Western Sahara city with no state, overridden by k."""
    return {'id': 1, 'name': 'X', 'country_id': 244, 'country_code': 'EH', 'state_id': None, 'state_code': None, **k}


US_CITY = city(id=2, country_id=233, country_code='US', state_id=1457, state_code='LA')


class CheckReferencesTest(unittest.TestCase):
    """Every rule, with one valid case for each kind of city."""

    def test_valid_cities_pass(self):
        """A stateless city of a country with no states and a normal city both pass."""
        self.assertEqual(check_references(COUNTRIES, STATES, [city(), US_CITY]), [])

    def assertProblem(self, expected, countries=COUNTRIES, states=STATES, cities=()):
        """Assert one of the errors contains the expected text."""
        errors = check_references(countries, states, list(cities))
        self.assertTrue(any(expected in e for e in errors), f'{expected!r} not in {errors}')

    def test_city_rejections(self):
        """Missing keys, half pairs, wrong types, unknown states, other countries, wrong codes and countries."""
        cases = {
            'required': {k: v for k, v in city().items() if k != 'state_code'},
            'no state, but country US has states': city(country_id=233, country_code='US'),
            'both be set or both be null': city(state_code='LA'),
            'not a positive integer': city(country_id=233, country_code='US', state_id='1457', state_code='LA'),
            'does not exist': city(country_id=233, country_code='US', state_id=99, state_code='LA'),
            'belongs to country US, not EH': city(state_id=1457, state_code='LA'),
            'does not match state': city(country_id=233, country_code='US', state_id=1457, state_code='XX'),
            'do not name one known country': city(country_id=999999),
        }
        for expected, record in cases.items():
            self.assertProblem(expected, cities=[record])
        self.assertProblem('do not name one known country', cities=[city(country_code='US')])
        self.assertProblem('not a positive integer', cities=[city(country_id=233, country_code='US', state_id=True, state_code='LA')])

    def test_inventory_rejections(self):
        """A wrong country or state inventory is refused instead of being used to decide who has states."""
        self.assertProblem('id or iso2 is duplicated', countries=COUNTRIES + [{'id': 245, 'iso2': 'US'}])
        self.assertProblem('two-letter iso2', countries=COUNTRIES + [{'id': 246, 'iso2': 'usa'}])
        self.assertProblem('id is duplicated', states=STATES + [dict(STATES[0], iso2='LB')])
        self.assertProblem('is not a known country', states=[{'id': 1457, 'iso2': 'LA', 'country_code': 'US'}],
                           cities=[city(country_id=233, country_code='US')])
        self.assertProblem("country_code 'EH' is not US", states=[dict(STATES[0], country_code='EH')])
        self.assertProblem('has no state code', states=[dict(STATES[0], iso2=None)])


def mysql_available():
    """Whether the importer's database driver is installed (it is in CI)."""
    try:
        import mysql.connector  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(mysql_available(), 'mysql-connector-python is not installed')
class ImporterTest(unittest.TestCase):
    """The importer refuses before resetting any table."""

    def setUp(self):
        """Contribution files in a temporary folder and an importer with a stub cursor."""
        from import_json_to_mysql import JSONToMySQLImporter
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        for path, rows in {'countries/countries.json': COUNTRIES, 'states/states.json': STATES}.items():
            Path('contributions', path).parent.mkdir(parents=True, exist_ok=True)
            Path('contributions', path).write_text(json.dumps(rows))
        Path('contributions/cities').mkdir()
        self.importer = JSONToMySQLImporter.__new__(JSONToMySQLImporter)
        self.importer.cursor = Mock()

    def preflight(self, cities, nullable='YES'):
        """Run the preflight on these cities with the state columns reported as nullable or not."""
        Path('contributions/cities/XX.json').write_text(json.dumps(cities))
        self.importer.cursor.fetchall.return_value = [{'Field': 'state_id', 'Null': nullable}, {'Field': 'state_code', 'Null': nullable}]
        with contextlib.redirect_stdout(io.StringIO()):
            self.importer.preflight_city_states()

    def test_preflight(self):
        """Valid data passes; a bad country or pair fails; a stateless city needs the migration's nullable columns."""
        self.preflight([city(), US_CITY])
        for bad in (city(country_id=999999), city(country_id=244, country_code='US'), city(state_code='LA')):
            with self.assertRaisesRegex(ValueError, 'reference problems'):
                self.preflight([bad])
        with self.assertRaisesRegex(ValueError, 'run migration 20261014000000'):
            self.preflight([city()], nullable='NO')
        self.preflight([US_CITY], nullable='NO')   # no stateless city: the migration is not needed

    def test_main_never_resets_after_a_failed_preflight(self):
        """The command stops with exit 1 and calls neither reset nor any import."""
        import import_json_to_mysql as module
        calls = []

        class Fake:
            """Records each importer step; the reference preflight fails."""

            def __init__(self, **_):
                """Accepts the connection arguments."""

            def __getattr__(self, name):
                """Every other step records its name and returns a count."""
                return lambda *a: calls.append(name) or 0

            def preflight_city_states(self):
                """Fails as a bad reference would."""
                calls.append('preflight_city_states')
                raise ValueError('1 reference problems')

        with patch.object(module, 'JSONToMySQLImporter', Fake), patch.object(sys, 'argv', ['import']), \
                patch.object(os, 'chdir'), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as stop:
                module.main()
        self.assertEqual(stop.exception.code, 1)
        self.assertNotIn('reset_tables', calls)
        self.assertFalse([c for c in calls if c.startswith('import_')])


@unittest.skipUnless(mysql_available(), 'mysql-connector-python is not installed')
class SyncTest(unittest.TestCase):
    """The sync writes the state keys, null included, and writes nothing when a pair is invalid."""

    def setUp(self):
        """A temporary folder and a sync with a stub cursor serving these rows."""
        from sync_mysql_to_json import MySQLToJSONSync
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        self.sync = MySQLToJSONSync.__new__(MySQLToJSONSync)
        self.sync.cursor = Mock()

    def run_sync(self, rows):
        """Serve the cities rows (grouped by country), countries and states, then sync."""
        columns = ['id', 'name', 'state_id', 'state_code', 'country_id', 'country_code']
        answers = {'SHOW COLUMNS': [{'Field': c} for c in columns], 'DISTINCT': [{'country_code': c} for c in sorted({r['country_code'] for r in rows})],
                   'FROM countries': COUNTRIES, 'FROM states': STATES}
        state = {}

        def execute(query, params=None):
            """Remember which rows the next fetchall returns."""
            key = next((k for k in answers if k in query), None)
            state['rows'] = answers[key] if key else [r for r in rows if r['country_code'] == params[0]]

        self.sync.cursor.execute.side_effect = execute
        self.sync.cursor.fetchall.side_effect = lambda: state['rows']
        with contextlib.redirect_stdout(io.StringIO()):
            return self.sync.sync_cities()

    def test_round_trip_and_refusal(self):
        """Null state keys are written; a US city with no state stops the sync before any file is written."""
        self.run_sync([city(), US_CITY])
        eh = json.loads(Path('contributions/cities/EH.json').read_text())
        self.assertEqual((eh[0]['state_id'], eh[0]['state_code']), (None, None))
        Path('contributions/cities/EH.json').unlink()
        Path('contributions/cities/US.json').unlink()
        with self.assertRaisesRegex(ValueError, 'no city file was written'):
            self.run_sync([city(), dict(US_CITY, state_id=None, state_code=None)])
        self.assertEqual(list(Path('contributions/cities').iterdir()), [])


if __name__ == '__main__':
    unittest.main()
