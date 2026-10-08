"""Regression tests for county import safety and contribution round trips."""

import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import mysql.connector
import import_json_to_mysql as importer_module
from import_json_to_mysql import JSONToMySQLImporter
from sync_mysql_to_json import MySQLToJSONSync


class CountySyncTests(unittest.TestCase):
    """Exercise production import/sync methods without changing a database."""

    def setUp(self):
        """Create isolated contribution files and a read-only database stub."""
        self.previous = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        self.file = Path('contributions/counties/US.json')
        self.file.parent.mkdir(parents=True)
        self.county = dict(id=1, name='Acadia', state_id=1457, state_code='LA',
                           country_id=233, country_code='US', latitude='30.00000000',
                           longitude='-92.00000000')
        self.file.write_text(json.dumps([self.county]))
        self.importer = JSONToMySQLImporter.__new__(JSONToMySQLImporter)
        self.importer.cursor = Mock()
        self.importer.cursor.fetchone.return_value = {'table': 'counties'}
        self.importer.conn = Mock()
        self.importer.get_table_columns = Mock(return_value={key: '' for key in self.county})
        self.importer.detect_new_columns = Mock(return_value={})
        self.importer._batch_insert_records = Mock(return_value=1)
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def assert_main_stops_before_reset(self):
        """Run CLI orchestration and assert no reset or import occurs."""
        with patch.object(importer_module, 'JSONToMySQLImporter', return_value=self.importer), \
             patch.object(importer_module, '__file__', str(Path.cwd() / 'bin/scripts/sync/import_json_to_mysql.py')), \
             patch('sys.argv', ['import_json_to_mysql.py']), \
             patch.object(self.importer, 'reset_tables') as reset, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as failure:
                importer_module.main()
            self.assertEqual(failure.exception.code, 1)
            reset.assert_not_called()
            self.importer._batch_insert_records.assert_not_called()
            self.assertFalse(any('TRUNCATE' in call.args[0] for call in self.importer.cursor.execute.call_args_list))

    def test_malformed_file_stops_full_import_before_reset(self):
        """A later malformed file must not erase a previously imported snapshot."""
        Path('contributions/counties/ZZ.json').write_text('{')
        self.assert_main_stops_before_reset()

    def test_non_array_file_stops_full_import_before_reset(self):
        """A JSON object is not a valid county dataset."""
        Path('contributions/counties/ZZ.json').write_text('{}')
        self.assert_main_stops_before_reset()

    def test_unreadable_file_stops_full_import_before_reset(self):
        """A read failure is fatal, even with another valid file present."""
        real_open = open

        def unreadable(file, *args, **kwargs):
            """Simulate a permission failure independently of the test user's UID."""
            if str(file).endswith('US.json'):
                raise PermissionError('Unreadable county fixture')
            return real_open(file, *args, **kwargs)

        with patch('builtins.open', side_effect=unreadable):
            self.assert_main_stops_before_reset()

    def test_unreadable_directory_is_not_treated_as_absent(self):
        """Directory permission errors must stop the full import too."""
        real_stat = os.stat

        def unreadable(path, *args, **kwargs):
            """Simulate an inaccessible county directory without relying on chmod."""
            if str(path) == 'contributions/counties':
                raise PermissionError('Unreadable county directory')
            return real_stat(path, *args, **kwargs)

        with patch('os.stat', side_effect=unreadable):
            self.assert_main_stops_before_reset()

    def test_direct_import_preflights_every_file_before_truncate(self):
        """Calling the county importer directly must also protect stored data."""
        Path('contributions/counties/ZZ.json').write_text('{')
        with self.assertRaises(ValueError):
            self.importer.import_counties()
        self.assertFalse(any('TRUNCATE' in call.args[0] for call in self.importer.cursor.execute.call_args_list))

    def test_missing_directory_or_table_is_optional(self):
        """Absent optional sources remain supported."""
        self.file.unlink()
        self.file.parent.rmdir()
        self.assertEqual(self.importer.import_counties(), 0)
        self.file.parent.mkdir()
        self.file.write_text('{')
        self.importer.cursor.fetchone.return_value = None
        self.assertEqual(self.importer.import_counties(), 0)

    def test_table_check_error_is_not_an_absent_table(self):
        """Database errors must propagate rather than silently omit counties."""
        self.importer.cursor.execute.side_effect = mysql.connector.Error('Unavailable connection')
        with self.assertRaises(mysql.connector.Error):
            self.importer.import_counties()

    def test_import_sync_round_trip_preserves_non_database_fields(self):
        """Relationship names survive while database-backed values can change."""
        source = dict(self.county, state_name='Louisiana', country_name='United States')
        self.file.write_text(json.dumps([source], indent=2) + '\n')
        stored = []

        def insert(table, records, columns):
            """Retain only the columns the importer sends to MySQL."""
            stored.extend({key: record[key] for key in columns} for record in records)
            return len(records)

        self.importer._batch_insert_records.side_effect = insert
        self.assertEqual(self.importer.import_counties(), 1)
        self.assertNotIn('state_name', stored[0])
        stored[0]['latitude'] = '31.00000000'
        syncer = MySQLToJSONSync.__new__(MySQLToJSONSync)
        syncer.cursor = Mock()
        syncer.cursor.fetchone.return_value = {'table': 'counties'}
        syncer.cursor.fetchall.side_effect = [[{'country_code': 'US'}], stored]
        syncer.get_table_columns = Mock(return_value=list(self.county))
        self.assertEqual(syncer.sync_counties(), 1)
        self.assertEqual(json.loads(self.file.read_text()), [dict(source, latitude='31.00000000')])
        self.assertTrue(self.file.read_text().endswith('\n'))


if __name__ == '__main__':
    unittest.main()
