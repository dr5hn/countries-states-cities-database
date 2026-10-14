"""Tests for check_county_states_exports.py on small generated-looking files: it passes only when every format exists,
the target county has a null state pair and the same two or more distinct regions everywhere, and every other county
keeps its own state pair. Each false pass review_county_regions reproduced is a regression here. Needs pyyaml, pandas,
pyarrow, and Node with @toon-format/toon installed in bin/scripts/export (as in CI).
Run: python3 -m unittest discover -s bin/db/tests -p 'test_*.py'"""
import copy
import csv
import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts' / 'export'))
from json_to_toon import json_to_toon  # noqa: E402  the real converter writes the TOON fixture

from check_county_states_exports import main  # noqa: E402

CHECKER = str(Path(__file__).with_name('check_county_states_exports.py'))
REGIONS = [{'state_id': 4060, 'state_code': 'MWT'}, {'state_id': 4061, 'state_code': 'WKO'}]
COUNTIES = [{'id': 9, 'name': 'Waitomo District', 'state_id': None, 'state_code': None, 'states': REGIONS, 'country_id': 158},
            {'id': 1, 'name': 'Far North District', 'state_id': 4059, 'state_code': 'NTL', 'states': None, 'country_id': 158}]


def flat(r):
    """A county as CSV and PLIST write it: strings, empty for null, no list."""
    return {k: '' if v is None else str(v) for k, v in r.items() if k != 'states'}


def sql_value(v):
    """A value as the SQL Server export writes it."""
    return 'NULL' if v is None else f"N'{v}'" if isinstance(v, str) else str(v)


def write_exports(root, counties=None, edit=None):
    """A complete set of exports from these counties; edit(fmt, rows) may change the rows one format receives."""
    base = counties or COUNTIES
    rows = lambda fmt: (edit(fmt, copy.deepcopy(base)) if edit else None) or copy.deepcopy(base)
    for d in ('json', 'csv', 'plist', 'xml', 'yml', 'mongodb', 'parquet', 'toon', 'sqlserver'):
        Path(root, d).mkdir()
    Path(root, 'json/counties.json').write_text(json.dumps(rows('json')))
    for fmt, dump in (('csv', None), ('plist', plistlib.dumps)):
        counties_rows, relation = [flat(r) for r in rows(fmt)], [
            {'county_id': str(r['id']), 'state_id': str(s['state_id']), 'state_code': s['state_code']} for r in rows(fmt) for s in r['states'] or []]
        for name, data, fields in (('counties', counties_rows, list(counties_rows[0])), ('county_states', relation, ['county_id', 'state_id', 'state_code'])):
            if fmt == 'csv':
                with open(Path(root, f'csv/{name}.csv'), 'w', newline='', encoding='utf-8') as fh:
                    w = csv.DictWriter(fh, fieldnames=fields)
                    w.writeheader()
                    w.writerows(data)
            else:
                Path(root, f'plist/{name}.plist').write_bytes(dump(data))
    xml = ''.join('<county>' + f"<id>{r['id']}</id>" + ''.join(f'<{k}/>' if r[k] is None else f'<{k}>{r[k]}</{k}>' for k in ('state_id', 'state_code'))
                  + (''.join(f"<states><state_id>{s['state_id']}</state_id><state_code>{s['state_code']}</state_code></states>" for s in r['states'])
                     if r['states'] else '<states/>') + '</county>' for r in rows('xml'))
    Path(root, 'xml/counties.xml').write_text(f'<counties>{xml}</counties>')
    import yaml
    Path(root, 'yml/counties.yml').write_text(yaml.safe_dump({'counties': rows('yml')}))
    mongo = [{**{k: v for k, v in r.items() if k != 'id'}, '_id': r['id'], **({'state': {'$ref': 'states', '$id': r['state_id']}} if r['state_id'] else {})}
             for r in rows('mongodb')]
    Path(root, 'mongodb/counties.json').write_text(json.dumps(mongo))
    import pandas as pd
    pq = rows('parquet')
    pd.DataFrame({'id': [r['id'] for r in pq], 'state_id': pd.array([r['state_id'] for r in pq], dtype='Int64'),
                  'state_code': [r['state_code'] for r in pq],
                  'states': [json.dumps(r['states']) if r['states'] else None for r in pq]}).to_parquet(Path(root, 'parquet/counties.parquet'))
    Path(root, 'toon/counties.toon').write_text(json_to_toon(json.dumps(rows('toon'))))
    sq = rows('sqlserver')
    cols = list(sq[0])
    cols.remove('states')
    Path(root, 'sqlserver/counties.sql').write_text(
        'CREATE TABLE world.counties (\n    id INT IDENTITY(1,1) PRIMARY KEY,\n    state_id INT NULL\n);\n\n'
        f"INSERT INTO world.counties ({', '.join(cols)}) VALUES\n"
        + ',\n'.join('(' + ', '.join(sql_value(r[c]) for c in cols) + ')' for r in sq) + ';\n')
    pairs = [(r['id'], s['state_id']) for r in sq for s in r['states'] or []]
    Path(root, 'sqlserver/county_states.sql').write_text(
        'CREATE TABLE world.county_states (\n    county_id INT NOT NULL,\n    state_id INT NOT NULL,\n'
        '    CONSTRAINT PK_county_states PRIMARY KEY (county_id, state_id),\n'
        '    CONSTRAINT FK_county_states_counties FOREIGN KEY (county_id) REFERENCES world.counties(id) ON DELETE CASCADE,\n'
        '    CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)\n);\n\n'
        'INSERT INTO world.county_states (county_id, state_id) VALUES\n' + ',\n'.join(f'({a}, {b})' for a, b in pairs) + ';\n')


def target(fmt_wanted, change):
    """An edit that applies change(rows) only to the rows of one format."""
    def edit(fmt, rows):
        """Change this format's rows, leave the others."""
        if fmt == fmt_wanted:
            change(rows)
            return rows
        return None
    return edit


class CheckerTest(unittest.TestCase):
    """One passing set, then each kind of omission or false pass must be reported."""

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
        """Each missing artifact is a problem, SQL Server's counties file included."""
        for rel in ('json/counties.json', 'csv/counties.csv', 'csv/county_states.csv', 'plist/counties.plist',
                    'plist/county_states.plist', 'xml/counties.xml', 'yml/counties.yml', 'mongodb/counties.json',
                    'parquet/counties.parquet', 'toon/counties.toon', 'sqlserver/counties.sql', 'sqlserver/county_states.sql'):
            self.assertProblem(f'{rel}: not generated', change=lambda root, rel=rel: Path(root, rel).unlink())

    def test_target_needs_a_null_pair_everywhere(self):
        """The target county with a state in any format is a problem, SQL Server and Mongo's reference included."""
        give_state = lambda rows: rows[0].update(state_id=4060, state_code='MWT')
        for fmt, where in (('sqlserver', 'sqlserver/counties.sql'), ('csv', 'csv/counties.csv'), ('xml', 'xml/counties.xml'),
                           ('toon', 'toon/counties.toon'), ('parquet', 'parquet'), ('mongodb', 'mongodb/counties.json')):
            self.assertProblem(f'{where}: county 9', edit=target(fmt, give_state))

    def test_every_other_county_keeps_its_pair(self):
        """A one-state county that loses its state or code in any format is a problem (no row counts)."""
        for fmt, key, where in (('csv', 'state_code', 'csv/counties.csv'), ('plist', 'state_id', 'plist/counties.plist'),
                                ('parquet', 'state_code', 'parquet'), ('yml', 'state_id', 'yml/counties.yml'),
                                ('toon', 'state_code', 'toon/counties.toon'), ('sqlserver', 'state_code', 'sqlserver/counties.sql')):
            self.assertProblem(f'{where}: county 1', edit=target(fmt, lambda rows, key=key: rows[1].update({key: None})))
        self.assertProblem('json/counties.json: county 1 has no regions but not a full state pair',
                           edit=target('json', lambda rows: rows[1].update(state_code=None)))

    def test_regions_must_match_everywhere(self):
        """One region fewer in any listing is a problem."""
        drop = lambda rows: rows[0].update(states=REGIONS[:1] + [{'state_id': 4062, 'state_code': 'OTA'}])
        for fmt, where in (('csv', 'csv/county_states.csv'), ('plist', 'plist/county_states.plist'), ('xml', 'xml/counties.xml'),
                           ('yml', 'yml/counties.yml'), ('mongodb', 'mongodb/counties.json'), ('parquet', 'parquet'),
                           ('toon', 'toon/counties.toon'), ('sqlserver', 'sqlserver/county_states.sql')):
            self.assertProblem(f'{where}', edit=target(fmt, drop))

    def test_regions_must_be_distinct(self):
        """The same region twice in every format is not a county of several regions."""
        twice = [{**COUNTIES[0], 'states': [REGIONS[0], REGIONS[0]]}, COUNTIES[1]]
        self.assertProblem('json/counties.json: county 9 needs a null state pair and two or more distinct regions', counties=twice)

    def test_sql_server_relation_ddl(self):
        """The county_states table needs its composite key and both foreign keys."""
        def strip(root):
            """Remove the foreign key to states from the generated DDL."""
            p = Path(root, 'sqlserver/county_states.sql')
            p.write_text(p.read_text().replace('    CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)\n', ''))
        self.assertProblem('sqlserver/county_states.sql: the table needs', change=strip)

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
