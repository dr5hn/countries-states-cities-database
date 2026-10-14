"""Parquet read-back of integer columns with nulls (v5: a city's state_id can be null). Needs pandas and pyarrow."""
import os
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from json_to_parquet import typed_frame


def read_back(rows):
    """Write rows the way export_table does and read the table back."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, 'cities.parquet')
        pq.write_table(pa.Table.from_pandas(typed_frame(rows), preserve_index=False), path)
        return pq.read_table(path)


class ParquetIntegerTest(unittest.TestCase):
    """Mixed and all-null integer columns stay int64 with real nulls."""

    def test_mixed_state_ids(self):
        """A null state next to real ones reads back as null, the others as integers."""
        t = read_back([{'id': 1, 'state_id': None, 'state_code': None}, {'id': 2, 'state_id': 1457, 'state_code': 'LA'}])
        self.assertEqual(t.schema.field('state_id').type, pa.int64())
        self.assertEqual(t.column('state_id').to_pylist(), [None, 1457])
        self.assertEqual(t.column('state_code').to_pylist(), [None, 'LA'])

    def test_all_null_state_ids(self):
        """A column with only nulls is still int64, not float or null-typed."""
        t = read_back([{'id': 1, 'state_id': None}, {'id': 2, 'state_id': None}])
        self.assertEqual(t.schema.field('state_id').type, pa.int64())
        self.assertEqual(t.column('state_id').to_pylist(), [None, None])

    def test_fraction_refused(self):
        """A non-integer value in an integer column stops the export."""
        with self.assertRaises(ValueError):
            typed_frame([{'id': 1, 'state_id': 1.5}])


if __name__ == '__main__':
    unittest.main()
