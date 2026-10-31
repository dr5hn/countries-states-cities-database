"""Tests for counties linked to several regions (v5, decision B6): the reference check (city_states.check_counties)
and its use by the importer and the sync. Run with the sync's other tests: python3 -m unittest discover bin/scripts/sync"""
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from city_states import check_counties

COUNTRIES = [{'id': 158, 'iso2': 'NZ'}, {'id': 233, 'iso2': 'US'}]
STATES = [{'id': 4060, 'country_id': 158, 'country_code': 'NZ', 'iso2': 'MWT'},
          {'id': 4061, 'country_id': 158, 'country_code': 'NZ', 'iso2': 'WKO'},
          {'id': 1457, 'country_id': 233, 'country_code': 'US', 'iso2': 'LA'}]
PAIRS = [{'state_id': 4060, 'state_code': 'MWT'}, {'state_id': 4061, 'state_code': 'WKO'}]


def county(**k):
    """A county of two regions (shape 2), overridden by k."""
    return {'id': 9, 'name': 'Waitomo District', 'country_id': 158, 'country_code': 'NZ', 'state_id': None,
            'state_code': None, 'states': PAIRS, **k}


ONE_REGION = county(id=8, name='Far North District', state_id=4061, state_code='WKO', states=None)


def city(**k):
    """A Waikato city linked to county 9, overridden by k."""
    return {'id': 1, 'name': 'Te Kuiti', 'country_id': 158, 'country_code': 'NZ', 'state_id': 4061, 'state_code': 'WKO',
            'county_id': 9, **k}


class CheckCountiesTest(unittest.TestCase):
    """Both county shapes, every refusal, and the city membership rule."""

    def problems(self, counties, cities=()):
        """The errors for these counties and cities."""
        return check_counties(COUNTRIES, STATES, list(counties), list(cities))

    def assertProblem(self, expected, counties=(), cities=()):
        """Assert one of the errors contains the expected text."""
        errors = self.problems(counties, cities)
        self.assertTrue(any(expected in e for e in errors), f'{expected!r} not in {errors}')

    def test_both_shapes_pass(self):
        """A one-region county, a county of two regions and cities in either pass; an omitted states key is shape 1."""
        no_key = {k: v for k, v in ONE_REGION.items() if k != 'states'}
        self.assertEqual(self.problems([county(), ONE_REGION, no_key | {'id': 7}],
                                       [city(), city(id=2, state_id=4060, state_code='MWT'), city(id=3, county_id=8)]), [])

    def test_county_refusals(self):
        """Half pairs, a list beside a state, no state at all, short or repeated lists, bad entries and other countries."""
        cases = {
            'state_id and state_code must both be set or both be null': county(state_code='WKO'),
            'has a state, so it cannot also list states': county(state_id=4061, state_code='WKO'),
            'no state: list its regions in states': county(states=None),
            'two or more distinct regions': county(states=[PAIRS[0]]),
            'two or more distinct regions ': county(states=[PAIRS[0], PAIRS[0]]),
            'each entry of states needs only state_id and state_code': county(states=[PAIRS[0], {'state_id': 4061}]),
            'states entry: state_code \'XX\' does not match state 4061': county(states=[PAIRS[0], {'state_id': 4061, 'state_code': 'XX'}]),
            'states entry: state 1457 belongs to country US, not NZ': county(states=[PAIRS[0], {'state_id': 1457, 'state_code': 'LA'}]),
            'states entry: state_id 99 does not exist': county(states=[PAIRS[0], {'state_id': 99, 'state_code': 'ZZ'}]),
            'states entry: state_id True is not a positive integer': county(states=[PAIRS[0], {'state_id': True, 'state_code': 'WKO'}]),
            'needs an explicit id': county(id=None),
            'states must be a list': county(states={'state_id': 4060}),
            'do not name one known country': county(country_id=999),
            'state 1457 belongs to country US, not NZ': ONE_REGION | {'state_id': 1457, 'state_code': 'LA'},
            'state_code \'XX\' does not match state 4061': ONE_REGION | {'state_code': 'XX'},
        }
        for expected, record in cases.items():
            self.assertProblem(expected.strip(), counties=[record])

    def test_city_membership(self):
        """A linked city's state must be its county's state or one of its regions; the county must exist."""
        self.assertProblem("city 1 Te Kuiti: state 1457 is not one of county 9's regions",
                           [county()], [city(country_id=233, country_code='US', state_id=1457, state_code='LA')])
        self.assertProblem("city 1 Te Kuiti: state 4060 is not county 8's state (4061)", [ONE_REGION],
                           [city(county_id=8, state_id=4060, state_code='MWT')])
        self.assertProblem('city 1 Te Kuiti: county_id 77 does not exist', [county()], [city(county_id=77)])
        self.assertProblem('county 9 Again: id is duplicated', [county(), county(name='Again')])


def mysql_available():
    """Whether the importer's database driver is installed (it is in CI)."""
    try:
        import mysql.connector  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(mysql_available(), 'mysql-connector-python is not installed')
class ImporterCountyTest(unittest.TestCase):
    """The importer checks counties before any reset, needs the migration for several regions, and writes the
    relation rows from the list, never as a column."""

    def setUp(self):
        """Contribution files in a temporary folder and an importer with a stub cursor."""
        from import_json_to_mysql import JSONToMySQLImporter
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        for path, rows in {'countries/countries.json': COUNTRIES, 'states/states.json': STATES,
                           'cities/NZ.json': [city()], 'counties/NZ.json': [county(), ONE_REGION]}.items():
            Path('contributions', path).parent.mkdir(parents=True, exist_ok=True)
            Path('contributions', path).write_text(json.dumps(rows))
        self.importer = JSONToMySQLImporter.__new__(JSONToMySQLImporter)
        self.importer.cursor, self.importer.conn = Mock(), Mock()

    def preflight(self, migrated=True, counties_table=True, columns=('state_id', 'state_code')):
        """Run the county preflight with the database reporting the migration as applied or not, the counties table
        present or not, and which state columns SHOW COLUMNS returns."""
        last = {}
        self.importer.cursor.execute.side_effect = lambda sql, *a: last.update(sql=sql)

        def fetchone():
            """Answer SHOW TABLES for counties and county_states."""
            if "'counties'" in last['sql']:
                return {'t': 'counties'} if counties_table else None
            return {'t': 'county_states'} if migrated else None
        self.importer.cursor.fetchone.side_effect = fetchone
        self.importer.cursor.fetchall.return_value = [{'Field': c, 'Null': 'YES' if migrated else 'NO'} for c in columns]
        with contextlib.redirect_stdout(io.StringIO()):
            return self.importer.preflight_counties()

    def test_preflight(self):
        """Valid counties load; a broken county or city link refuses; several regions need migration 20261015000000."""
        self.assertEqual(len(self.preflight()), 2)
        with self.assertRaisesRegex(ValueError, 'run migration 20261015000000'):
            self.preflight(migrated=False)
        Path('contributions/counties/NZ.json').write_text(json.dumps([ONE_REGION]))
        Path('contributions/cities/NZ.json').write_text(json.dumps([city(county_id=8)]))
        self.assertEqual(len(self.preflight(migrated=False)), 1)   # one region each: no migration needed
        Path('contributions/counties/NZ.json').write_text(json.dumps([county(states=[PAIRS[0]])]))
        with self.assertRaisesRegex(ValueError, 'county reference problems'):
            self.preflight()

    def test_older_database_without_counties_refuses_several_regions(self):
        """With no counties table, a county of several regions refuses before any reset; one-state counties still skip,
        and an unreadable file is still skipped as before."""
        with self.assertRaisesRegex(ValueError, 'run migration 20261015000000'):
            self.preflight(counties_table=False)
        Path('contributions/counties/NZ.json').write_text(json.dumps([ONE_REGION]))
        Path('contributions/cities/NZ.json').write_text(json.dumps([city(county_id=8)]))
        self.assertEqual(self.preflight(counties_table=False), [])
        Path('contributions/counties/ZZ.json').write_text('{')
        self.assertEqual(self.preflight(counties_table=False), [])

    def test_both_state_columns_must_be_reported(self):
        """A column query that does not return both state columns is not proof of the migration."""
        with self.assertRaisesRegex(ValueError, 'run migration 20261015000000'):
            self.preflight(columns=('state_id',))

    def test_relation_rows_not_a_column(self):
        """states never becomes a column; each listed region becomes one county_states row after the counties."""
        rows = [county(), ONE_REGION]
        self.assertNotIn('states', self.importer_new_columns(rows))
        executed = []
        self.importer.cursor.execute.side_effect = lambda sql, *a: executed.append(sql)
        self.importer.cursor.executemany.side_effect = lambda sql, values: executed.append((sql, list(values)))
        self.importer.get_table_columns = lambda table: {c: 'x' for c in ('id', 'name', 'state_id', 'state_code', 'country_id',
                                                                           'country_code', 'parent_id')}
        self.importer.detect_new_columns = lambda table, data: {}
        with contextlib.redirect_stdout(io.StringIO()):
            self.importer.import_counties(rows)
        inserts = [x for x in executed if isinstance(x, tuple)]
        self.assertTrue(all('`states`' not in sql for sql, _ in inserts))
        relation = [values for sql, values in inserts if 'INTO county_states' in sql]
        self.assertEqual(relation, [[(9, 4060), (9, 4061)]])

    def importer_new_columns(self, rows):
        """Columns the importer would add for these county records to a table that has only an id."""
        from import_json_to_mysql import JSONToMySQLImporter
        importer = JSONToMySQLImporter.__new__(JSONToMySQLImporter)
        importer.get_table_columns = lambda table: {'id': 'int'}
        return importer.detect_new_columns('counties', rows)


@unittest.skipUnless(mysql_available(), 'mysql-connector-python is not installed')
class SyncCountyTest(unittest.TestCase):
    """The sync rebuilds states from county_states, never from the old file, and refuses a broken county first."""

    def setUp(self):
        """A temporary folder and a sync with a stub cursor."""
        from sync_mysql_to_json import MySQLToJSONSync
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        self.sync = MySQLToJSONSync.__new__(MySQLToJSONSync)
        self.sync.cursor = Mock()

    def run_sync(self, rows, relation):
        """Serve these county rows and relation rows, then sync counties."""
        columns = ['id', 'name', 'state_id', 'state_code', 'country_id', 'country_code']
        answers = {'SHOW TABLES': [{'t': 'x'}], 'SHOW COLUMNS': [{'Field': c} for c in columns],
                   'DISTINCT': [{'country_code': 'NZ'}], 'FROM county_states': relation, 'FROM countries': COUNTRIES,
                   'FROM states': STATES, 'FROM cities': []}
        state = {}

        def execute(query, params=None):
            """Remember which rows the next fetch returns."""
            key = next((k for k in answers if k in query), None)
            state['rows'] = answers[key] if key else [dict(r) for r in rows]

        self.sync.cursor.execute.side_effect = execute
        self.sync.cursor.fetchall.side_effect = lambda: state['rows']
        self.sync.cursor.fetchone.side_effect = lambda: (state['rows'] or [None])[0]
        with contextlib.redirect_stdout(io.StringIO()):
            return self.sync.sync_counties()

    def test_states_from_the_relation(self):
        """The list comes from county_states in state order; a stale list in the old file is replaced or dropped."""
        Path('contributions/counties').mkdir(parents=True)
        stale = [county(states=[PAIRS[1], {'state_id': 4074, 'state_code': 'BOP'}]), ONE_REGION | {'states': PAIRS}]
        Path('contributions/counties/NZ.json').write_text(json.dumps(stale))
        db = [{k: v for k, v in r.items() if k != 'states'} for r in (county(), ONE_REGION)]
        self.run_sync(db, [{'county_id': 9, 'state_id': 4061}, {'county_id': 9, 'state_id': 4060}])
        out = {r['id']: r for r in json.loads(Path('contributions/counties/NZ.json').read_text())}
        self.assertEqual(out[9]['states'], PAIRS)
        self.assertNotIn('states', out[8])

    def test_broken_county_writes_nothing(self):
        """A county with no state and fewer than two relation rows stops the sync before any file is written."""
        db = [{k: v for k, v in county().items() if k != 'states'}]
        with self.assertRaisesRegex(ValueError, 'no county file was written'):
            self.run_sync(db, [{'county_id': 9, 'state_id': 4060}])
        self.assertFalse(Path('contributions/counties/NZ.json').exists())


if __name__ == '__main__':
    unittest.main()
