"""Auto-assigned ids never reuse an id the ledger retired or reserved (migrations/events.jsonl, reserved_ids.jsonl)."""
import json
import os
import tempfile
import unittest
from unittest.mock import Mock

from import_json_to_mysql import JSONToMySQLImporter, retired_id_floor


def write_lines(path, rows):
    """Write rows as JSON lines; a str row is written as is (to test malformed lines)."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(r if isinstance(r, str) else json.dumps(r) for r in rows) + '\n')


class RetiredIdFloorTest(unittest.TestCase):
    """retired_id_floor() reads the ledger files without a database."""

    def setUp(self):
        """A scratch migrations folder per test."""
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        """Remove the scratch folder."""
        self.tmp.cleanup()

    def test_no_ledger_means_no_floor(self):
        """Today's master: an empty events.jsonl and no reserved list."""
        write_lines(os.path.join(self.dir, 'events.jsonl'), [])
        self.assertEqual(retired_id_floor(self.dir), {})

    def test_removals_and_reservations_set_the_floor(self):
        """The highest removed or reserved id per table; identity and restoration events retire nothing."""
        write_lines(os.path.join(self.dir, 'events.jsonl'), [
            {'old_table': 'cities', 'old_id': 166400, 'event_commit': 'a'},                      # removal by default
            {'event_type': 'removal', 'old_table': 'cities', 'old_id': 12, 'event_commit': 'b'},
            {'event_type': 'identity', 'table': 'cities', 'id': 999999, 'event_commit': 'c'},
            {'event_type': 'restoration', 'table': 'states', 'id': 888888, 'event_commit': 'd'},
        ])
        write_lines(os.path.join(self.dir, 'reserved_ids.jsonl'), [
            {'table': 'postcodes', 'id': 900000}, {'table': 'cities', 'id': 166350}, ''])
        self.assertEqual(retired_id_floor(self.dir), {'cities': 166400, 'postcodes': 900000})

    def test_batch_rows_set_floor(self):
        """Every batch row contributes its id, alongside ordinary removals and reserved ids."""
        write_lines(os.path.join(self.dir, 'events.jsonl'), [
            {'old_table': 'cities', 'old_id': 7},
            {'event_type': 'removal_batch', 'old_table': 'postcodes',
             'rows': [{'old_id': 900001}, {'old_id': 900099}, {'old_id': 900002}]},
            {'event_type': 'removal_batch', 'old_table': 'cities', 'rows': [{'old_id': 8}]}])
        write_lines(os.path.join(self.dir, 'reserved_ids.jsonl'), [{'table': 'cities', 'id': 9}])
        self.assertEqual(retired_id_floor(self.dir), {'postcodes': 900099, 'cities': 9})
        for rows in ([], None, [None], [{'old_id': True}], [{'old_id': '12'}]):
            write_lines(os.path.join(self.dir, 'events.jsonl'), [
                {'event_type': 'removal_batch', 'old_table': 'postcodes', 'rows': rows}])
            with self.subTest(rows=rows), self.assertRaisesRegex(SystemExit, 'row [01]'):
                retired_id_floor(self.dir)

    def test_malformed_lines_stop_the_import(self):
        """Not JSON, not an object, no positive integer id, or an unknown event type: the import stops instead of guessing."""
        for bad in ('{not json', '[1, 2]', json.dumps({'old_table': 'cities', 'old_id': '7'}),
                    json.dumps({'old_table': 'cities', 'old_id': True}), json.dumps({'old_id': 7}),
                    json.dumps({'event_type': 'retirement', 'old_table': 'cities', 'old_id': 7})):
            write_lines(os.path.join(self.dir, 'events.jsonl'), [bad])
            with self.assertRaises(SystemExit, msg=bad):
                retired_id_floor(self.dir)


class AutoIncrementTest(unittest.TestCase):
    """_batch_insert_records() raises AUTO_INCREMENT above the floor only for rows without ids."""

    def importer(self, floor):
        """An importer with a recording cursor and no database."""
        imp = JSONToMySQLImporter.__new__(JSONToMySQLImporter)
        imp.cursor, imp.conn, imp.id_floor = Mock(), Mock(), floor
        imp.prepare_value = lambda value, col: value
        return imp

    def test_rows_without_ids_start_above_the_floor(self):
        """The ALTER runs before the inserts."""
        imp = self.importer({'cities': 166400})
        imp._batch_insert_records('cities', [{'name': 'A'}], ['name'])
        imp.cursor.execute.assert_called_once_with('ALTER TABLE cities AUTO_INCREMENT = 166401')
        self.assertEqual(imp.cursor.method_calls[0][0], 'execute')

    def test_rows_with_ids_or_tables_without_a_floor_are_untouched(self):
        """Explicit ids keep their numbers; a table the ledger never retired from needs no ALTER."""
        imp = self.importer({'cities': 166400})
        imp._batch_insert_records('cities', [{'id': 5, 'name': 'A'}], ['id', 'name'])
        imp._batch_insert_records('states', [{'name': 'B'}], ['name'])
        imp.cursor.execute.assert_not_called()


if __name__ == '__main__':
    unittest.main()
