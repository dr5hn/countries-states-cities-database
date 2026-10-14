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
    xml = ''.join('<county>' + f"<id>{r['id']}</id>" + ''.join(f'<{k}/>' if r[k] is None else f'<{k}>{r[k]}</{k}>' for k in ('state_id', 'state_code') if k in r)
                  + (''.join(f"<states><state_id>{s['state_id']}</state_id><state_code>{s['state_code']}</state_code></states>" for s in r['states'])
                     if r['states'] else '<states/>') + '</county>' for r in rows('xml'))
    Path(root, 'xml/counties.xml').write_text(f'<counties>{xml}</counties>')
    import yaml
    Path(root, 'yml/counties.yml').write_text(yaml.safe_dump({'counties': rows('yml')}))
    mongo = [{**{k: v for k, v in r.items() if k != 'id'}, '_id': r['id'], **({'state': {'$ref': 'states', '$id': r['state_id']}} if r.get('state_id') else {})}
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
        self.assertProblem('json/counties.json: county 9 has a null state pair, so it needs two or more distinct regions', counties=twice)

    def test_missing_pair_keys_are_not_null(self):
        """A target county without its state keys (YAML, MongoDB) or empty elements (XML) is a problem, not a null pair."""
        def drop(rows):
            """Remove the target county's pair keys."""
            del rows[0]['state_id'], rows[0]['state_code']
        for fmt, where in (('yml', 'yml/counties.yml'), ('mongodb', 'mongodb/counties.json'), ('xml', 'xml/counties.xml')):
            self.assertProblem(f'{where}: county 9', edit=target(fmt, drop))

    def test_invalid_list_is_not_no_list(self):
        """A malformed states list on a one-state county is a problem, not the expected absence of a list."""
        self.assertProblem('yml/counties.yml: county 1', edit=target('yml', lambda rows: rows[1].update(states=[{'state_id': 1}])))

    def test_extra_and_missing_counties(self):
        """A county that json/counties.json does not have, or one it has but a format lacks, is a problem."""
        extra = {'id': 99999, 'name': 'Extra', 'state_id': 4059, 'state_code': 'NTL', 'states': None, 'country_id': 158}
        self.assertProblem('csv/counties.csv: counties differ', edit=target('csv', lambda rows: rows.append(extra)))
        self.assertProblem('toon/counties.toon: counties differ', edit=target('toon', lambda rows: rows.pop()))
        self.assertProblem('xml/counties.xml: county 9 appears 2 times', edit=target('xml', lambda rows: rows.append(dict(rows[0]))))

    def test_every_county_of_several_regions_is_checked(self):
        """A second county of several regions with a repeated region fails, though the requested county 9 is valid."""
        repeated = {'id': 10, 'name': 'Twice', 'state_id': None, 'state_code': None, 'states': [REGIONS[0], REGIONS[0]], 'country_id': 158}
        self.assertProblem('json/counties.json: county 10', counties=COUNTIES + [repeated])
        self.assertProblem('json/counties.json: county 2 has a state and a states list',
                           counties=COUNTIES + [{**COUNTIES[1], 'id': 2, 'states': REGIONS}])
        self.assertProblem('json/counties.json: county id 1 is duplicated', counties=COUNTIES + [COUNTIES[1]])

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


class FormatAuditRegressionTest(unittest.TestCase):
    """Codex review_county_regions_3's audits as regressions: the 62-case format matrix
    (runs/review_county_regions_3/checker-format-audit.py), its nine scalar cases (checker-scalar-audit.py) and the
    short CSV row (checker-missing-cells-audit.py). Every mutation must be refused; the complete fixture must pass."""

    def problems(self, change):
        """Problems after writing the complete fixture and applying change(root)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_exports(root)
            change(root)
            return main(9, root)

    @staticmethod
    def xml_case(root, change):
        """Change the XML tree only."""
        import xml.etree.ElementTree as ET
        p = root / 'xml/counties.xml'
        tree = ET.parse(p)
        change(tree.getroot())
        tree.write(p, encoding='unicode')

    def xml_list(self, root, text, index):
        """Replace one county's XML states elements with literal XML."""
        import xml.etree.ElementTree as ET

        def change(tree):
            """Swap the states elements of county element index."""
            county = tree[index]
            for e in list(county.findall('states')):
                county.remove(e)
            for e in ET.fromstring('<new>' + text + '</new>'):
                county.append(e)
        self.xml_case(root, change)

    @staticmethod
    def structured(root, fmt, change):
        """Change YAML, MongoDB, JSON, TOON or Parquet rows in their exported representation."""
        import yaml
        import pandas as pd
        if fmt == 'yml':
            p = root / 'yml/counties.yml'
            doc = yaml.safe_load(p.read_text())
            change(doc['counties'])
            p.write_text(yaml.safe_dump(doc))
        elif fmt in ('json', 'mongodb'):
            p = root / f'{fmt}/counties.json'
            doc = json.loads(p.read_text())
            change(doc)
            p.write_text(json.dumps(doc))
        elif fmt == 'toon':
            doc = copy.deepcopy(COUNTIES)
            change(doc)
            (root / 'toon/counties.toon').write_text(json_to_toon(json.dumps(doc)))
        else:
            p = root / 'parquet/counties.parquet'
            df = pd.read_parquet(p)
            change(df)
            df.to_parquet(p)

    def identity_mutation(self, root, fmt, mutation):
        """missing_pair, missing_county, extra_county or duplicate_county in one format's own representation."""
        import pandas as pd
        key = '_id' if fmt == 'mongodb' else 'id'

        def rows_change(rows):
            """The mutation on a list of row dicts."""
            if mutation == 'missing_pair':
                rows[0].pop('state_id', None)
                rows[0].pop('state_code', None)
            elif mutation == 'missing_county':
                rows.pop()
            elif mutation == 'extra_county':
                rows.append({**rows[1], key: 99999})
            else:
                rows.append(copy.deepcopy(rows[0]))
        if fmt in ('yml', 'mongodb', 'toon'):
            self.structured(root, fmt, rows_change)
        elif fmt == 'xml':
            def alter(tree):
                """The mutation on the XML tree."""
                if mutation == 'missing_pair':
                    for k in ('state_id', 'state_code'):
                        tree[0].remove(tree[0].find(k))
                elif mutation == 'missing_county':
                    tree.remove(tree[-1])
                else:
                    e = copy.deepcopy(tree[1 if mutation == 'extra_county' else 0])
                    if mutation == 'extra_county':
                        e.find('id').text = '99999'
                    tree.append(e)
            self.xml_case(root, alter)
        elif fmt == 'parquet':
            p = root / 'parquet/counties.parquet'
            df = pd.read_parquet(p)
            if mutation == 'missing_pair':
                df = df.drop(columns=['state_id', 'state_code'])
            elif mutation == 'missing_county':
                df = df.iloc[:1]
            else:
                extra = df.iloc[[1 if mutation == 'extra_county' else 0]].copy()
                if mutation == 'extra_county':
                    extra.loc[:, 'id'] = 99999
                df = pd.concat([df, extra], ignore_index=True)
            df.to_parquet(p)
        elif fmt in ('csv', 'plist'):
            p = root / f'{fmt}/counties.{fmt}'
            rows = list(csv.DictReader(p.open())) if fmt == 'csv' else plistlib.loads(p.read_bytes())
            rows_change(rows)
            if fmt == 'plist':
                p.write_bytes(plistlib.dumps(rows))
            else:
                fields = list(rows[0])
                with p.open('w', newline='') as fh:
                    w = csv.DictWriter(fh, fieldnames=fields)
                    w.writeheader()
                    w.writerows([{k: v for k, v in r.items() if k in fields} for r in rows])
        else:
            p = root / 'sqlserver/counties.sql'
            text = p.read_text()
            if mutation == 'missing_pair':
                text = text.replace('state_id', 'unused_state_id').replace('state_code', 'unused_state_code')
            else:
                start = text.index(' VALUES\n') + len(' VALUES\n')
                end = text.index(';\n', start)
                lines = text[start:end].splitlines()
                if mutation == 'missing_county':
                    lines = lines[:1]
                else:
                    lines.append(lines[1 if mutation == 'extra_county' else 0].rstrip(','))
                if mutation == 'extra_county':
                    lines[-1] = lines[-1].replace('(1,', '(99999,', 1)
                text = text[:start] + ',\n'.join(line.rstrip(',') for line in lines) + text[end:]
            p.write_text(text)

    def cases(self):
        """Every (name, change) of the three audits."""
        out = []
        for name, text, index in (
                ('xml_normal_states_only_code', '<states><state_code>NTL</state_code></states>', 1),
                ('xml_normal_states_text', '<states>broken-list</states>', 1),
                ('xml_normal_states_unknown_child', '<states><oops>1</oops></states>', 1),
                ('xml_normal_states_two_empty', '<states/><states/>', 1),
                ('xml_target_states_missing_code', '<states><state_id>4060</state_id></states><states><state_id>4061</state_id><state_code>WKO</state_code></states>', 0),
                ('xml_target_states_extra_key', '<states><state_id>4060</state_id><state_code>MWT</state_code><extra>bad</extra></states><states><state_id>4061</state_id><state_code>WKO</state_code></states>', 0),
                ('xml_target_states_duplicate_child', '<states><state_id>4060</state_id><state_id>999</state_id><state_code>MWT</state_code></states><states><state_id>4061</state_id><state_code>WKO</state_code></states>', 0),
                ('xml_target_states_mixed_empty', '<states/><states><state_id>4060</state_id><state_code>MWT</state_code></states><states><state_id>4061</state_id><state_code>WKO</state_code></states>', 0),
                ('xml_normal_states_missing', '', 1)):
            out.append((name, lambda root, t=text, i=index: self.xml_list(root, t, i)))
        for fmt in ('csv', 'plist', 'xml', 'yml', 'mongodb', 'parquet', 'toon', 'sqlserver'):
            for mutation in ('missing_pair', 'missing_county', 'extra_county', 'duplicate_county'):
                out.append((f'{fmt}_{mutation}', lambda root, f=fmt, m=mutation: self.identity_mutation(root, f, m)))
        for fmt in ('yml', 'mongodb', 'toon', 'parquet'):
            for val in ([{'state_id': 1}], 'bad-list', [], {'state_id': 1}):
                def change(root, fmt=fmt, val=val):
                    """A malformed non-null states value on the one-state county."""
                    if fmt == 'parquet':
                        self.structured(root, fmt, lambda df: df.__setitem__('states', [df.loc[0, 'states'], json.dumps(val)]))
                    else:
                        self.structured(root, fmt, lambda rows: rows[1].update(states=val))
                out.append((f'{fmt}_invalid_states_{json.dumps(val)}', change))
        for fmt in ('csv', 'plist', 'xml', 'sqlserver'):
            def broken(root, fmt=fmt):
                """A null state id replaced by non-null text in one flat format."""
                if fmt == 'xml':
                    self.xml_case(root, lambda tree: setattr(tree[0].find('state_id'), 'text', 'broken'))
                elif fmt == 'plist':
                    p = root / 'plist/counties.plist'
                    rows = plistlib.loads(p.read_bytes())
                    rows[0]['state_id'] = 'broken'
                    p.write_bytes(plistlib.dumps(rows))
                elif fmt == 'csv':
                    p = root / 'csv/counties.csv'
                    rows = list(csv.DictReader(p.open()))
                    rows[0]['state_id'] = 'broken'
                    with p.open('w', newline='') as fh:
                        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                        w.writeheader()
                        w.writerows(rows)
                else:
                    p = root / 'sqlserver/counties.sql'
                    p.write_text(p.read_text().replace('NULL, NULL', "N'broken', NULL", 1))
            out.append((f'{fmt}_invalid_nonnull_state_id', broken))
        for fmt in ('yml', 'mongodb', 'toon'):
            key = '_id' if fmt == 'mongodb' else 'id'
            out.append((f'{fmt}_boolean_county_id', lambda root, f=fmt, k=key: self.structured(root, f, lambda rows: rows[1].update({k: True}))))
            out.append((f'{fmt}_fractional_region_id', lambda root, f=fmt: self.structured(root, f, lambda rows: rows[0]['states'][0].update(state_id=4060.75))))
        out.append(('parquet_fractional_county_id', lambda root: self.structured(root, 'parquet', lambda df: df.__setitem__('id', [9.0, 1.75]))))
        out.append(('json_authority_fractional_region_id', lambda root: self.structured(root, 'json', lambda rows: rows[0]['states'][0].update(state_id=4060.75))))
        out.append(('json_authority_string_region_id', lambda root: self.structured(root, 'json', lambda rows: rows[0]['states'][0].update(state_id='4060'))))

        def short_row(root):
            """The target county's CSV record cut to its first two cells (DictReader then gives None cells)."""
            p = root / 'csv/counties.csv'
            lines = p.read_text().splitlines()
            lines[1] = ','.join(lines[1].split(',')[:2])
            p.write_text('\n'.join(lines) + '\n')
        out.append(('csv_short_row', short_row))
        return out

    def test_positive_fixture_passes(self):
        """The complete fixture has no problems."""
        self.assertEqual(self.problems(lambda root: None), [])

    def test_every_audited_mutation_is_refused(self):
        """Each of the audits' mutations yields at least one problem and never raises."""
        cases = self.cases()
        self.assertEqual(len(cases), 71)   # 61 format-matrix mutations, 9 scalar cases, 1 short row, besides the positive
        for name, change in cases:
            with self.subTest(name):
                self.assertNotEqual(self.problems(change), [], name)
