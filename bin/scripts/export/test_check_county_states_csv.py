"""Tests for check_county_states_csv.py: the CSV companion must list exactly the regions of json/counties.json."""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK = str(Path(__file__).with_name('check_county_states_csv.py'))
COUNTIES = [{'id': 9, 'state_id': None, 'state_code': None, 'states': [{'state_id': 4060, 'state_code': 'MWT'}, {'state_id': 4061, 'state_code': 'WKO'}]},
            {'id': 1, 'state_id': 4059, 'state_code': 'NTL', 'states': None}]


def run(rows, counties=COUNTIES):
    """Run the check in a folder holding these CSV rows and counties; return the completed process."""
    with tempfile.TemporaryDirectory() as root:
        Path(root, 'json').mkdir()
        Path(root, 'csv').mkdir()
        Path(root, 'json/counties.json').write_text(json.dumps(counties))
        with open(Path(root, 'csv/county_states.csv'), 'w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh)
            w.writerow(['county_id', 'state_id', 'state_code'])
            w.writerows(rows)
        return subprocess.run([sys.executable, CHECK], cwd=root, capture_output=True, text=True)


class CheckCountyStatesCsvTest(unittest.TestCase):
    """Equal lists pass; a missing, extra or changed row fails with exit 1."""

    def test_equal_lists_pass(self):
        """Both regions of county 9, in any order, pass."""
        self.assertEqual(run([[9, 4061, 'WKO'], [9, 4060, 'MWT']]).returncode, 0)

    def test_differences_fail(self):
        """One region fewer, one extra, or a wrong code fails."""
        for rows in ([[9, 4060, 'MWT']], [[9, 4060, 'MWT'], [9, 4061, 'WKO'], [1, 4059, 'NTL']], [[9, 4060, 'MWT'], [9, 4061, 'XX']]):
            self.assertEqual(run(rows).returncode, 1, rows)


if __name__ == '__main__':
    unittest.main()
