"""Tests for check_null_state_exports.py on small generated-looking files: it passes only when every format exists and
carries the city's state fields explicitly empty. Needs pyyaml, pandas and pyarrow (installed in CI).
Run: python3 -m unittest discover -s bin/db/tests -p 'test_*.py'"""
import csv
import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_null_state_exports import main

CHECKER = str(Path(__file__).with_name('check_null_state_exports.py'))

EH = {'id': 9, 'name': 'Test', 'state_id': None, 'state_code': None, 'state_name': None, 'country_id': 244}
US = {'id': 1, 'name': 'Other', 'state_id': 5, 'state_code': 'LA', 'state_name': 'L', 'country_id': 233}
XML_EH = '<city><id>9</id><state_id/><state_code/><state_name/></city>'


def write_exports(root, xml_eh=XML_EH, mongo_eh=None):
    """A complete, correct set of exports for one stateless city (9, EH) and one normal city."""
    for d in ('json', 'csv', 'plist', 'xml', 'yml', 'mongodb', 'parquet'):
        Path(root, d).mkdir()
    Path(root, 'json/cities.json').write_text(json.dumps([EH, US]))
    Path(root, 'json/countries+states+cities.json').write_text(json.dumps([
        {'iso2': 'EH', 'states': [], 'cities': [{'id': 9}]},
        {'iso2': 'US', 'states': [{'cities': [{'id': 1}]}], 'cities': []}]))
    blank = lambda r: {k: '' if v is None else str(v) for k, v in r.items()}
    with open(Path(root, 'csv/cities.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(EH))
        w.writeheader()
        w.writerows([blank(EH), blank(US)])
    Path(root, 'plist/cities.plist').write_bytes(plistlib.dumps([blank(EH), blank(US)]))
    Path(root, 'xml/cities.xml').write_text(f'<cities>{xml_eh}<city><id>1</id><state_id>5</state_id></city></cities>')
    import yaml
    Path(root, 'yml/cities.yml').write_text(yaml.safe_dump({'cities': [EH, US]}))
    mongo = mongo_eh or {**{k: v for k, v in EH.items() if k != 'id'}, '_id': 9}
    Path(root, 'mongodb/cities.json').write_text(json.dumps([mongo, {'_id': 1, 'state_id': 5, 'state': {'$id': 5}}]))
    import pandas as pd
    parquet_frame().to_parquet(Path(root, 'parquet/cities.parquet'))


def parquet_frame():
    """The Parquet cities table: the stateless city and one normal city, with all three state columns."""
    import pandas as pd
    return pd.DataFrame({'id': [9, 1], 'state_id': pd.array([None, 5], dtype='Int64'), 'state_code': [None, 'LA'],
                         'state_name': [None, 'L']})


class CheckerTest(unittest.TestCase):
    """One passing set, then each kind of omission must be reported."""

    def problems(self, change=lambda root: None, **kw):
        """Problems found after writing the exports and applying change."""
        with tempfile.TemporaryDirectory() as root:
            write_exports(root, **kw)
            change(root)
            return main(9, 'EH', root)

    def assertProblem(self, expected, **kw):
        """Assert one of the problems contains the expected text."""
        found = self.problems(**kw)
        self.assertTrue(any(expected in p for p in found), f'{expected!r} not in {found}')

    def test_complete_exports_pass(self):
        """The correct set has no problems."""
        self.assertEqual(self.problems(), [])

    def test_missing_files(self):
        """Each missing artifact is a problem, PLIST and Parquet included."""
        for rel in ('plist/cities.plist', 'parquet/cities.parquet', 'xml/cities.xml', 'mongodb/cities.json'):
            self.assertProblem(f'{rel}: not generated', change=lambda root, rel=rel: Path(root, rel).unlink())

    def test_missing_xml_elements(self):
        """An XML city without its state elements fails; empty elements are what passes."""
        self.assertProblem('xml/cities.xml: state elements are missing', xml_eh='<city><id>9</id></city>')

    def test_mongo_keys_and_reference(self):
        """Mongo must carry the state keys as explicit nulls and no state reference."""
        self.assertProblem('mongodb/cities.json', mongo_eh={'_id': 9})
        self.assertProblem('mongodb/cities.json', mongo_eh={**{k: v for k, v in EH.items() if k != 'id'}, '_id': 9,
                                                            'state': {'$ref': 'states', '$id': 5}})

    def test_flat_json_key_missing(self):
        """A missing state key in the flat JSON is not the same as null."""
        def drop(root):
            """Remove state_name from the stateless city."""
            Path(root, 'json/cities.json').write_text(json.dumps([{k: v for k, v in EH.items() if k != 'state_name'}, US]))
        self.assertProblem('json/cities.json: state fields are not null', change=drop)

    def test_json_null_document(self):
        """A JSON export that is the literal null is a problem, and the command exits 1."""
        for rel in ('json/cities.json', 'json/countries+states+cities.json', 'mongodb/cities.json'):
            null = lambda root, rel=rel: Path(root, rel).write_text('null')
            self.assertProblem(f'{rel}: cannot be read', change=null)
            with tempfile.TemporaryDirectory() as root:
                write_exports(root)
                null(root)
                run = subprocess.run([sys.executable, CHECKER, '9', 'EH'], cwd=root, capture_output=True, text=True)
                self.assertEqual(run.returncode, 1, f'{rel}: {run.stdout}{run.stderr}')

    def test_json_root_must_hold_records(self):
        """An object root, or a row that is not an object, is a problem."""
        for text in ('{"cities": []}', '[9, 1]'):
            self.assertProblem('json/cities.json: cannot be read',
                               change=lambda root, text=text: Path(root, 'json/cities.json').write_text(text))

    def test_parquet_state_fields(self):
        """Each Parquet state column must exist and be null for the stateless city."""
        def rewrite(edit):
            """A change that rewrites the Parquet table after applying edit to it."""
            def change(root):
                """Apply the edit and write the table back."""
                df = parquet_frame()
                edit(df)
                df.to_parquet(Path(root, 'parquet/cities.parquet'))
            return change
        for col, value in (('state_id', 5), ('state_code', 'LA'), ('state_name', 'Louisiana')):
            self.assertProblem('parquet: a state column is missing',
                               change=rewrite(lambda df, col=col: df.drop(columns=[col], inplace=True)))
            self.assertProblem('parquet: state fields are not null',
                               change=rewrite(lambda df, col=col, value=value: df.loc.__setitem__((0, col), value)))


if __name__ == '__main__':
    unittest.main()
