"""Tests for check_county_states_exports.py on small generated-looking files: it passes only when every format exists,
carries the county's state pair explicitly empty and lists the same two or more regions, and no other county lost
its state. Needs pyyaml, pandas and pyarrow (installed in CI).
Run: python3 -m unittest discover -s bin/db/tests -p 'test_*.py'"""
import csv
import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_county_states_exports import main

CHECKER = str(Path(__file__).with_name('check_county_states_exports.py'))
REGIONS = [{'state_id': 4060, 'state_code': 'MWT'}, {'state_id': 4061, 'state_code': 'WKO'}]
WAITOMO = {'id': 9, 'name': 'Waitomo District', 'state_id': None, 'state_code': None, 'states': REGIONS, 'country_id': 158}
NORTH = {'id': 1, 'name': 'Far North District', 'state_id': 4059, 'state_code': 'NTL', 'states': None, 'country_id': 158}
XML_WAITOMO = ('<county><id>9</id><state_id/><state_code/><states><state_id>4060</state_id><state_code>MWT</state_code></states>'
               '<states><state_id>4061</state_id><state_code>WKO</state_code></states></county>')


def write_exports(root, json_waitomo=None, xml_waitomo=XML_WAITOMO, relation=None, mongo_waitomo=None, toon_states=None):
    """A complete, correct set of exports for one county of several regions (9) and one county with its state."""
    for d in ('json', 'csv', 'plist', 'xml', 'yml', 'mongodb', 'parquet', 'toon', 'sqlserver'):
        Path(root, d).mkdir()
    waitomo = json_waitomo or WAITOMO
    Path(root, 'json/counties.json').write_text(json.dumps([waitomo, NORTH]))
    flat = lambda r: {k: '' if v is None else str(v) for k, v in r.items() if k != 'states'}
    relation = REGIONS if relation is None else relation
    for name, rows in (('counties', [flat(WAITOMO), flat(NORTH)]),
                       ('county_states', [{'county_id': '9', 'state_id': str(r['state_id']), 'state_code': r['state_code']} for r in relation])):
        with open(Path(root, f'csv/{name}.csv'), 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ['county_id', 'state_id', 'state_code'])
            w.writeheader()
            w.writerows(rows)
        Path(root, f'plist/{name}.plist').write_bytes(plistlib.dumps(rows))
    Path(root, 'xml/counties.xml').write_text(f'<counties>{xml_waitomo}<county><id>1</id><state_id>4059</state_id><states/></county></counties>')
    import yaml
    Path(root, 'yml/counties.yml').write_text(yaml.safe_dump({'counties': [WAITOMO, NORTH]}))
    mongo = mongo_waitomo or {**{k: v for k, v in WAITOMO.items() if k != 'id'}, '_id': 9}
    Path(root, 'mongodb/counties.json').write_text(json.dumps([mongo, {'_id': 1, 'state_id': 4059, 'states': None, 'state': {'$id': 4059}}]))
    parquet_frame().to_parquet(Path(root, 'parquet/counties.parquet'))
    cell = json.dumps(REGIONS if toon_states is None else toon_states, separators=(',', ':')).replace('"', '\\"')
    Path(root, 'toon/counties.toon').write_text('[2]{id,name,state_id,state_code,states,country_id}:\n'
                                                f'  9,Waitomo District,null,null,"{cell}",158\n  1,Far North District,4059,NTL,null,158')
    Path(root, 'sqlserver/county_states.sql').write_text('INSERT INTO world.county_states (county_id, state_id) VALUES\n'
                                                         + ',\n'.join(f"(9, {r['state_id']})" for r in relation) + ';\n')


def parquet_frame():
    """The Parquet counties table: the county of several regions and one county with its state."""
    import pandas as pd
    return pd.DataFrame({'id': [9, 1], 'state_id': pd.array([None, 4059], dtype='Int64'), 'state_code': [None, 'NTL'],
                         'states': [json.dumps(REGIONS), None]})


class CheckerTest(unittest.TestCase):
    """One passing set, then each kind of omission must be reported."""

    def problems(self, change=lambda root: None, **kw):
        """Problems found after writing the exports and applying change."""
        with tempfile.TemporaryDirectory() as root:
            write_exports(root, **kw)
            change(root)
            return main(9, root)

    def assertProblem(self, expected, **kw):
        """Assert one of the problems contains the expected text."""
        found = self.problems(**kw)
        self.assertTrue(any(expected in p for p in found), f'{expected!r} not in {found}')

    def test_complete_exports_pass(self):
        """The correct set has no problems."""
        self.assertEqual(self.problems(), [])

    def test_missing_files(self):
        """Each missing artifact is a problem."""
        for rel in ('json/counties.json', 'csv/county_states.csv', 'plist/county_states.plist', 'xml/counties.xml',
                    'yml/counties.yml', 'mongodb/counties.json', 'parquet/counties.parquet', 'toon/counties.toon',
                    'sqlserver/county_states.sql'):
            self.assertProblem(f'{rel}: not generated', change=lambda root, rel=rel: Path(root, rel).unlink())

    def test_regions_must_match_everywhere(self):
        """One region fewer in any listing is a problem; a single region is not a county of several regions."""
        self.assertProblem('json/counties.json: county 9 needs a null state pair and two or more regions',
                           json_waitomo={**WAITOMO, 'states': REGIONS[:1]})
        self.assertProblem('csv/county_states.csv: regions differ', relation=REGIONS[:1])
        self.assertProblem('xml/counties.xml: regions differ', xml_waitomo=XML_WAITOMO.replace(
            '<states><state_id>4061</state_id><state_code>WKO</state_code></states>', ''))
        self.assertProblem('toon/counties.toon: regions differ', toon_states=REGIONS[:1])

    def test_state_pair_must_be_empty(self):
        """A county of several regions that still carries a state, or a Mongo state reference, is a problem."""
        self.assertProblem('json/counties.json: county 9 needs a null state pair', json_waitomo={**WAITOMO, 'state_id': 4060})
        self.assertProblem('xml/counties.xml: state elements are missing or not empty',
                           xml_waitomo=XML_WAITOMO.replace('<state_id/>', '<state_id>4060</state_id>'))
        self.assertProblem('mongodb/counties.json', mongo_waitomo={**{k: v for k, v in WAITOMO.items() if k != 'id'}, '_id': 9,
                                                                   'state': {'$ref': 'states', '$id': 4060}})

    def test_other_counties_keep_their_state(self):
        """A one-state county that lost its state in Parquet is a problem."""
        def drop(root):
            """Null the state of county 1 in the Parquet table."""
            df = parquet_frame()
            df.loc[1, 'state_id'] = None
            df.to_parquet(Path(root, 'parquet/counties.parquet'))
        self.assertProblem('parquet: another county lost its state', change=drop)

    def test_command_exit_code(self):
        """The command exits 1 when a problem is found and 0 when none is."""
        with tempfile.TemporaryDirectory() as root:
            write_exports(root)
            ok = subprocess.run([sys.executable, CHECKER, '9'], cwd=root, capture_output=True, text=True)
            Path(root, 'csv/county_states.csv').unlink()
            bad = subprocess.run([sys.executable, CHECKER, '9'], cwd=root, capture_output=True, text=True)
        self.assertEqual((ok.returncode, bad.returncode), (0, 1), ok.stdout + ok.stderr + bad.stdout)


if __name__ == '__main__':
    unittest.main()
