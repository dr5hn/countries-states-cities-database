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


STATES = [{'id': 4059, 'name': 'Northland', 'country_id': 158, 'country_code': 'NZ', 'iso2': 'NTL'},
          {'id': 4060, 'name': 'Manawatu-Whanganui', 'country_id': 158, 'country_code': 'NZ', 'iso2': 'MWT'},
          {'id': 4061, 'name': 'Waikato', 'country_id': 158, 'country_code': 'NZ', 'iso2': 'WKO'}]


def write_contributions(root, counties):
    """The source of truth the checker derives its expectations from: contributions/counties/NZ.json in the
    contributions form (states only on a county of several regions) and contributions/states/states.json."""
    Path(root, 'contributions/counties').mkdir(parents=True, exist_ok=True)
    Path(root, 'contributions/states').mkdir(parents=True, exist_ok=True)
    source = [{k: v for k, v in c.items() if k != 'states' or v is not None} for c in counties]
    Path(root, 'contributions/counties/NZ.json').write_text(json.dumps(source))
    Path(root, 'contributions/states/states.json').write_text(json.dumps(STATES))


def write_exports(root, counties=None, edit=None, source=None):
    """A complete set of exports from these counties, and the contributions they come from (source, by default the
    same counties); edit(fmt, rows) may change the rows one format receives."""
    base = counties or COUNTIES
    write_contributions(root, source or base)
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
    Path(root, 'yml/counties.yml').write_text(yaml.safe_dump({'county': rows('yml')}))   # the exporter's singular envelope
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
    # the scaffold, DDL declarations and statement order ExportSqlServer.php writes (other county columns left out)
    Path(root, 'sqlserver/counties.sql').write_text(
        '-- Table: counties\n\n'
        "IF OBJECT_ID('world.counties', 'U') IS NOT NULL DROP TABLE world.counties;\n"
        'CREATE TABLE world.counties (\n    id INT IDENTITY(1,1) PRIMARY KEY,\n    name NVARCHAR(255) NOT NULL,\n'
        '    state_id INT NULL,\n    state_code NVARCHAR(255) NULL,\n    country_id INT NOT NULL,\n    parent_id INT NULL,\n'
        '    -- SQL Server forbids cascading self-references (error 1785). Clear child links before deletion.\n'
        '    CONSTRAINT FK_counties_parent FOREIGN KEY (parent_id) REFERENCES world.counties(id),\n'
        '    CONSTRAINT FK_counties_states FOREIGN KEY (state_id) REFERENCES world.states(id),\n'
        '    CONSTRAINT CK_counties_state_pair CHECK ((state_id IS NULL AND state_code IS NULL) OR (state_id IS NOT NULL AND state_code IS NOT NULL))\n);\n\n'
        'ALTER TABLE world.counties NOCHECK CONSTRAINT FK_counties_parent;\n\n'
        'SET IDENTITY_INSERT world.counties ON;\n\n'
        # batches of 900 rows, as the exporter chunks them (SQL Server takes at most 1,000 per INSERT)
        + ''.join(f"INSERT INTO world.counties ({', '.join(cols)}) VALUES\n"
                  + ',\n'.join('(' + ', '.join(sql_value(r[c]) for c in cols) + ')' for r in sq[i:i + 900]) + ';\n\n'
                  for i in range(0, len(sq), 900))
        + 'SET IDENTITY_INSERT world.counties OFF;\n\n'
        'ALTER TABLE world.counties WITH CHECK CHECK CONSTRAINT FK_counties_parent;\n\n')
    pairs = [(r['id'], s['state_id']) for r in sq for s in r['states'] or []]
    Path(root, 'sqlserver/county_states.sql').write_text(
        '-- Table: county_states\n\n'
        "IF OBJECT_ID('world.county_states', 'U') IS NOT NULL DROP TABLE world.county_states;\n"
        'CREATE TABLE world.county_states (\n    county_id INT NOT NULL,\n    state_id INT NOT NULL,\n'
        '    CONSTRAINT PK_county_states PRIMARY KEY (county_id, state_id),\n'
        '    CONSTRAINT FK_county_states_counties FOREIGN KEY (county_id) REFERENCES world.counties(id) ON DELETE CASCADE,\n'
        '    CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)\n);\n\n'
        'INSERT INTO world.county_states (county_id, state_id) VALUES\n' + ',\n'.join(f'({a}, {b})' for a, b in pairs) + ';\n\n')


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
        self.assertProblem('json/counties.json: county 1',
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
        self.assertProblem('contributions/counties/NZ.json: county 9 has a null state pair, so it needs two or more distinct regions', counties=twice)

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
        self.assertProblem('contributions/counties/NZ.json: county 10', counties=COUNTIES + [repeated])
        self.assertProblem('contributions/counties/NZ.json: county 2 needs its own complete state pair and no states list',
                           counties=COUNTIES + [{**COUNTIES[1], 'id': 2, 'states': REGIONS}])
        self.assertProblem('contributions/counties/NZ.json: county id 1 is duplicated', counties=COUNTIES + [COUNTIES[1]])

    def test_sql_server_relation_ddl(self):
        """The county_states table needs its composite key and both foreign keys."""
        def strip(root):
            """Remove the foreign key to states from the generated DDL."""
            p = Path(root, 'sqlserver/county_states.sql')
            p.write_text(p.read_text().replace('    CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)\n', ''))
        self.assertProblem('sqlserver/county_states.sql: cannot be read: SQL: CREATE TABLE world.county_states has an empty declaration', change=strip)

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
            change(doc['county'])
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


class StructureRegressionTest(FormatAuditRegressionTest):
    """Codex review_county_regions_4: a CSV row must be exactly as wide as its header, and every XML scalar the checker
    reads must be exactly one leaf element. The review's cases, then one generic test per rule."""

    test_positive_fixture_passes = test_every_audited_mutation_is_refused = None   # inherited helpers only

    def csv_rows(self, root):
        """The raw rows of csv/counties.csv, header first."""
        with open(root / 'csv/counties.csv', newline='', encoding='utf-8') as fh:
            return list(csv.reader(fh))

    def write_csv(self, root, rows):
        """Write raw rows back to csv/counties.csv."""
        with open(root / 'csv/counties.csv', 'w', newline='', encoding='utf-8') as fh:
            csv.writer(fh).writerows(rows)

    def test_review_cases(self):
        """A trailing cell dropped after the state cells (target and normal county); a nested or a conflicting
        duplicate XML id, state_id or state_code on the target county."""
        import xml.etree.ElementTree as ET

        def drop_last(index):
            """Drop the last cell of one data row."""
            def change(root):
                """Rewrite the CSV with one row a cell short."""
                rows = self.csv_rows(root)
                rows[index] = rows[index][:-1]
                self.write_csv(root, rows)
            return change
        for index in (1, 2):
            self.assertNotEqual(self.problems(drop_last(index)), [], f'row {index}')
        for tag in ('id', 'state_id', 'state_code'):
            def nested(root, tag=tag):
                """Give the target's field a child element."""
                self.xml_case(root, lambda tree: tree[0].find(tag).append(ET.fromstring('<broken>999</broken>')))

            def duplicate(root, tag=tag):
                """Add a conflicting second field to the target."""
                self.xml_case(root, lambda tree: tree[0].append(ET.fromstring(f'<{tag}>999</{tag}>')))
            self.assertNotEqual(self.problems(nested), [], f'nested {tag}')
            self.assertNotEqual(self.problems(duplicate), [], f'duplicate {tag}')

    def test_csv_row_short_or_long_at_any_position(self):
        """Removing or inserting one cell at any position of any data row is refused."""
        with tempfile.TemporaryDirectory() as d:
            write_exports(Path(d))
            rows = self.csv_rows(Path(d))
        width = len(rows[0])
        for index in range(1, len(rows)):
            for pos in range(width + 1):
                for kind in ('short', 'long'):
                    if kind == 'short' and pos == width:
                        continue

                    def change(root, index=index, pos=pos, kind=kind):
                        """One row one cell short or long at pos."""
                        rows = self.csv_rows(root)
                        row = rows[index]
                        rows[index] = row[:pos] + row[pos + 1:] if kind == 'short' else row[:pos] + ['x'] + row[pos:]
                        self.write_csv(root, rows)
                    with self.subTest(row=index, pos=pos, kind=kind):
                        self.assertNotEqual(self.problems(change), [])

    def test_xml_field_duplicated_or_nested_anywhere(self):
        """Every XML scalar the checker reads, on every county and in every region, refuses a duplicate copy (same text
        or another) and a nested child."""
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as d:
            write_exports(Path(d))
            tree = ET.parse(Path(d) / 'xml/counties.xml').getroot()
        targets = []
        for ci, county in enumerate(tree):
            for tag in ('id', 'state_id', 'state_code'):
                targets.append((ci, None, tag))
            for si, el in enumerate(county.findall('states')):
                for tag in ('state_id', 'state_code'):
                    if el.find(tag) is not None:
                        targets.append((ci, si, tag))
        self.assertGreaterEqual(len(targets), 10)
        for ci, si, tag in targets:
            for kind in ('duplicate-same', 'duplicate-other', 'nested'):
                def change(root, ci=ci, si=si, tag=tag, kind=kind):
                    """Mutate one XML scalar field."""
                    def alter(tree):
                        """Duplicate or nest the field."""
                        parent = tree[ci] if si is None else tree[ci].findall('states')[si]
                        field = parent.find(tag)
                        if kind == 'nested':
                            field.append(ET.fromstring('<broken>999</broken>'))
                        else:
                            twin = ET.fromstring(f'<{tag}>{field.text or "" if kind == "duplicate-same" else "999"}</{tag}>')
                            parent.insert(list(parent).index(field) + 1, twin)
                    self.xml_case(root, alter)
                with self.subTest(county=ci, region=si, field=tag, kind=kind):
                    self.assertNotEqual(self.problems(change), [])


class Round5RegressionTest(unittest.TestCase):
    """Codex review_county_regions_5's systematic audit (structure-audit.py, structure-supplement.py,
    final-parser-probes.py): 69 false passes in eight classes, plus its refusal and compatibility controls. Every
    'refuse' case must report a problem, every 'pass' case none."""

    @staticmethod
    def run_case(change, counties=None):
        """Problems after writing the fixture (or one built from counties) and applying change(root)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_exports(root, counties=counties)
            change(root)
            return main(9, root)

    @staticmethod
    def text(rel, old, new):
        """A change replacing one exact fragment of a text export."""
        def change(root):
            """Replace the fragment."""
            p = root / rel
            data = p.read_text()
            assert old in data, (rel, old)
            p.write_text(data.replace(old, new, 1))
        return change

    @staticmethod
    def append(rel, extra):
        """A change appending text to an export."""
        return lambda root: (root / rel).write_text((root / rel).read_text() + extra)

    @staticmethod
    def xml(change):
        """A change to the XML tree."""
        import xml.etree.ElementTree as ET

        def apply(root):
            """Parse, change, write back."""
            p = root / 'xml/counties.xml'
            tree = ET.parse(p)
            change(tree.getroot())
            tree.write(p, encoding='unicode')
        return apply

    @staticmethod
    def mongo(change):
        """A change to the MongoDB rows."""
        def apply(root):
            """Load, change, write back."""
            p = root / 'mongodb/counties.json'
            rows = json.loads(p.read_text())
            change(rows)
            p.write_text(json.dumps(rows))
        return apply

    @staticmethod
    def parquet_frame(change):
        """A change to the Parquet table through pandas."""
        def apply(root):
            """Load, change, write back."""
            import pandas as pd
            p = root / 'parquet/counties.parquet'
            df = pd.read_parquet(p)
            change(df)
            df.to_parquet(p)
        return apply

    @staticmethod
    def parquet_state_id(array):
        """A change storing state_id with another physical type, keeping the pandas metadata."""
        def apply(root):
            """Replace the physical state_id column."""
            import pyarrow.parquet as pq
            p = root / 'parquet/counties.parquet'
            old = pq.read_table(p)
            pq.write_table(old.set_column(old.column_names.index('state_id'), 'state_id', array()), p)
        return apply

    @staticmethod
    def toon_rows(change):
        """A change rewriting the TOON export from changed fixture rows."""
        def apply(root):
            """Convert the changed rows."""
            rows = copy.deepcopy(COUNTIES)
            change(rows)
            (root / 'toon/counties.toon').write_text(json_to_toon(json.dumps(rows)))
        return apply

    def cases(self):
        """(name, change, expected) for every audited mutation and control."""
        import pyarrow as pa
        import xml.etree.ElementTree as ET
        T, A = self.text, self.append
        out = [('positive', lambda r: None, 'pass')]
        # 1. repeated keys, headers and columns
        for rel, key, good, bad in (('json/counties.json', 'id', '9', '999'), ('json/counties.json', 'state_id', 'null', '999'),
                                    ('mongodb/counties.json', '_id', '9', '999'), ('mongodb/counties.json', 'state_id', 'null', '999')):
            out.append((f'{rel}_duplicate_{key}', T(rel, f'"{key}": {good}', f'"{key}": {bad}, "{key}": {good}'), 'refuse'))
        for rel in ('json/counties.json', 'mongodb/counties.json'):
            out.append((f'{rel}_duplicate_region_key', T(rel, '"state_id": 4060', '"state_id": 999, "state_id": 4060'), 'refuse'))
        out.append(('yaml_duplicate_own_key', T('yml/counties.yml', '  state_id: 4059', '  state_id: 999\n  state_id: 4059'), 'refuse'))
        out.append(('yaml_duplicate_region_key', T('yml/counties.yml', '    state_id: 4060', '    state_id: 999\n    state_id: 4060'), 'refuse'))
        for table in ('counties', 'county_states'):
            out.append((f'plist_{table}_duplicate_key', T(f'plist/{table}.plist', '<key>state_id</key>',
                                                           '<key>state_id</key><string>999</string><key>state_id</key>'), 'refuse'))

            def dup_csv(root, table=table):
                """Prepend a second state_id column with contradictory cells."""
                p = root / f'csv/{table}.csv'
                with p.open(newline='') as fh:
                    rows = list(csv.reader(fh))
                with p.open('w', newline='') as fh:
                    csv.writer(fh).writerows([['state_id'] + rows[0]] + [['999'] + row for row in rows[1:]])
            out.append((f'csv_{table}_duplicate_header', dup_csv, 'refuse'))

            def dup_sql(root, table=table):
                """Add a repeated SQL column with one conflicting value per row."""
                import re
                p = root / f'sqlserver/{table}.sql'
                data = p.read_text().replace(f'INSERT INTO world.{table} (', f'INSERT INTO world.{table} (state_id, ', 1)
                start = data.index(' VALUES\n') + len(' VALUES\n')
                p.write_text(data[:start] + re.sub(r'(?m)^\(', '(999, ', data[start:]))
            out.append((f'sql_{table}_duplicate_column', dup_sql, 'refuse'))
        out.append(('toon_duplicate_header', T('toon/counties.toon', '{id,', '{id,id,'), 'refuse'))
        dup_text = json.dumps(REGIONS).replace('"state_id": 4060', '"state_id": 999, "state_id": 4060')
        out.append(('parquet_duplicate_embedded_json_key', self.parquet_frame(lambda df: df.__setitem__('states', [dup_text, None])), 'refuse'))
        out.append(('toon_duplicate_embedded_json_key', self.toon_rows(lambda rows: rows[0].update(states=dup_text)), 'refuse'))

        def aliased(root):
            """Two physical columns that pandas metadata names id."""
            import pandas as pd
            import pyarrow.parquet as pq
            p = root / 'parquet/counties.parquet'
            df = pd.read_parquet(p)
            df.insert(0, 'bad_id', [999, 999])
            table = pa.Table.from_pandas(df, preserve_index=False)
            meta = dict(table.schema.metadata)
            pandas_meta = json.loads(meta[b'pandas'])
            pandas_meta['columns'][0]['name'] = 'id'
            meta[b'pandas'] = json.dumps(pandas_meta).encode()
            pq.write_table(table.replace_schema_metadata(meta), p)
        out.append(('parquet_aliased_duplicate_id', aliased, 'refuse'))
        # 2. envelopes and roots
        out += [('xml_wrong_root', self.xml(lambda t: setattr(t, 'tag', 'cities')), 'refuse'),
                ('xml_wrong_record_tag', self.xml(lambda t: setattr(t[0], 'tag', 'city')), 'refuse'),
                ('yaml_wrong_wrapper', T('yml/counties.yml', 'county:', 'cities:'), 'refuse'),
                ('yaml_ignored_extra_records', T('yml/counties.yml', 'county:', 'ignored:\n- id: 999\n  state_id: 999\n  state_code: BAD\n  states: null\ncounty:'), 'refuse'),
                ('yaml_ignored_trailing_records', A('yml/counties.yml', '\nextra:\n- id: 999\n  state_id: 999\n  state_code: BAD\n  states: null\n'), 'refuse'),
                ('toon_null_root', lambda r: (r / 'toon/counties.toon').write_text('null'), 'refuse'),
                ('toon_empty_root', lambda r: (r / 'toon/counties.toon').write_text(''), 'refuse')]
        for table in ('counties', 'county_states'):
            rel = f'plist/{table}.plist'
            out += [(f'plist_{table}_wrong_wrapper', lambda r, rel=rel: (T(rel, '<plist version="1.0">', '<wrong version="1.0">')(r), T(rel, '</plist>', '</wrong>')(r)), 'refuse'),
                    (f'plist_{table}_ignored_root', T(rel, '<array>', '<array><dict><key>id</key><string>999</string></dict></array><array>'), 'refuse'),
                    (f'plist_{table}_null_root', lambda r, rel=rel: (r / rel).write_bytes(plistlib.dumps(None, fmt=plistlib.FMT_BINARY)), 'refuse'),
                    (f'plist_{table}_empty_xml_root', lambda r, rel=rel: (r / rel).write_bytes(b'<?xml version="1.0"?><plist version="1.0"/>'), 'refuse'),
                    (f'plist_{table}_trailing_data', lambda r, rel=rel: (r / rel).write_bytes((r / rel).read_bytes() + b'junk'), 'refuse'),
                    # 3. a nested tag hiding contradictory text inside a property-list string
                    (f'plist_{table}_nested_scalar', T(rel, '<string>4059</string>' if table == 'counties' else '<string>4060</string>',
                                                      '<string>999<unknown/>' + ('4059' if table == 'counties' else '4060') + '</string>'), 'refuse')]

            def binary(root, rel=rel):
                """The same records as a binary property list (valid)."""
                (root / rel).write_bytes(plistlib.dumps(plistlib.loads((root / rel).read_bytes()), fmt=plistlib.FMT_BINARY))
            out.append((f'plist_{table}_binary_valid', binary, 'pass'))
        with tempfile.TemporaryDirectory() as d:
            write_exports(Path(d))
            for table in ('counties', 'county_states'):
                rows = plistlib.loads((Path(d) / f'plist/{table}.plist').read_bytes())
                for ri, row in enumerate(rows):
                    for key in row:
                        def null_cell(root, table=table, rows=rows, ri=ri, key=key):
                            """A binary property list with one None cell."""
                            changed = copy.deepcopy(rows)
                            changed[ri][key] = None
                            (root / f'plist/{table}.plist').write_bytes(plistlib.dumps(changed, fmt=plistlib.FMT_BINARY))
                        out.append((f'plist_{table}_{ri}_{key}_None', null_cell, 'refuse'))
        # 3. XML attributes and mixed content
        out += [('xml_county_mixed_text', self.xml(lambda t: setattr(t[0], 'text', 'broken')), 'refuse'),
                ('xml_scalar_mixed_tail', self.xml(lambda t: setattr(t[0].find('state_id'), 'tail', '999')), 'refuse'),
                ('xml_region_element_mixed_tail', self.xml(lambda t: setattr(t[0].find('states'), 'tail', '999')), 'refuse'),
                ('xml_scalar_nil_attribute', self.xml(lambda t: t[1].find('state_id').set('{http://www.w3.org/2001/XMLSchema-instance}nil', 'true')), 'refuse'),
                ('xml_empty_states_attribute', self.xml(lambda t: t[1].find('states').set('state_id', '999')), 'refuse')]
        # 8. the JSON authority's states key
        out.append(('json_missing_normal_states', T('json/counties.json', '"states": null, ', ''), 'refuse'))
        # 4. CSV quoting
        out += [('csv_unclosed_quote_relation', T('csv/county_states.csv', '4061,WKO\n', '4061,"WKO'), 'refuse'),
                ('csv_junk_after_empty_quote', T('csv/county_states.csv', '4061,WKO', '4061,""WKO'), 'refuse')]
        # 5. SQL Server: only the exporter's statements, rows consumed completely
        for table, extra in (('counties', "INSERT INTO world.counties (id, state_id, state_code) VALUES (999, 4059, N'NTL');\n"),
                             ('county_states', 'INSERT INTO world.county_states (county_id, state_id) VALUES (9, 999);\n')):
            rel = f'sqlserver/{table}.sql'
            out += [(f'sql_{table}_ignored_extra_insert', A(rel, extra), 'refuse'),
                    (f'sql_{table}_commented_insert', T(rel, 'INSERT INTO world.', '/* INSERT INTO world.'), 'refuse'),
                    (f'sql_{table}_ignored_broken_row', T(rel, ' VALUES\n', ' VALUES\nBROKEN ROW,\n'), 'refuse')]

            def balanced(root, rel=rel):
                """Wrap every insert in a closed block comment."""
                p = root / rel
                before, rest = p.read_text().split('INSERT INTO', 1)
                p.write_text(before + '/* INSERT INTO' + rest + '*/\n')
            out.append((f'sql_{table}_balanced_commented_insert', balanced, 'refuse'))
        out += [('sql_counties_post_update', A('sqlserver/counties.sql', 'UPDATE world.counties SET state_id=999 WHERE id=1;\n'), 'refuse'),
                ('sql_relation_post_delete', A('sqlserver/county_states.sql', 'DELETE FROM world.county_states;\n'), 'refuse'),
                ('sql_relation_missing_row_separator', T('sqlserver/county_states.sql', '(9, 4060),\n', '(9, 4060)\n'), 'refuse'),
                ('sql_relation_extra_value_separator', T('sqlserver/county_states.sql', '(9, 4060)', '(9,, 4060)'), 'refuse'),
                ('sql_counties_missing_value_separator', T('sqlserver/counties.sql', "4059, N'NTL'", "4059 N'NTL'"), 'refuse'),
                ('sql_relation_disabled_constraint', T('sqlserver/county_states.sql',
                                                        '    CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)',
                                                        '    -- CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)'), 'refuse'),
                ('sql_no_county_table', T('sqlserver/counties.sql', 'CREATE TABLE world.counties', 'CREATE TABLE world.wrong_table'), 'refuse')]
        # 6. MongoDB state references
        out += [('mongo_wrong_reference_collection', self.mongo(lambda rows: rows[1]['state'].update({'$ref': 'countries'})), 'refuse'),
                ('mongo_missing_reference_collection', self.mongo(lambda rows: rows[1]['state'].pop('$ref')), 'refuse'),
                ('mongo_float_reference_id', self.mongo(lambda rows: rows[1]['state'].update({'$id': 4059.0})), 'refuse')]
        for i, val in enumerate([False, [], '', {}, {'$ref': 'states', '$id': None}, {'$ref': 'states'}]):
            out.append((f'mongo_null_pair_reference_{i}', self.mongo(lambda rows, val=val: rows[0].update(state=val)), 'refuse'))
        for value in (True, 4059.0, '4059', 0, -1, None):
            out.append((f'mongo_own_type_{value!r}', self.mongo(lambda rows, value=value: rows[1].update(state_id=value)), 'refuse'))
        # 7. no conversion before validation: TOON numbers and bytes, Parquet storage
        out += [('toon_fraction_rounded_county_id', T('toon/counties.toon', '  9,', '  9.0000000000000001,'), 'refuse'),
                ('toon_fraction_rounded_state_id', T('toon/counties.toon', ',4059,', ',4059.0000000000001,'), 'refuse'),
                ('toon_invalid_utf8', lambda r: (r / 'toon/counties.toon').write_bytes((r / 'toon/counties.toon').read_bytes().replace(b'Waitomo', b'Waitom\xff')), 'refuse'),
                ('parquet_physical_float_4059.0', self.parquet_state_id(lambda: pa.array([None, 4059.0], type=pa.float64())), 'refuse'),
                ('parquet_physical_float_4059.75', self.parquet_state_id(lambda: pa.array([None, 4059.75], type=pa.float64())), 'refuse'),
                ('parquet_nan_null_laundering', self.parquet_state_id(lambda: pa.array([float('nan'), 4059.0], type=pa.float64(), from_pandas=False)), 'refuse'),
                ('parquet_physical_string_id', self.parquet_state_id(lambda: pa.array([None, '4059'], type=pa.string())), 'refuse'),
                ('parquet_trailing_bytes', lambda r: (r / 'parquet/counties.parquet').write_bytes((r / 'parquet/counties.parquet').read_bytes() + b'junk'), 'refuse')]
        for raw in ('[]', '{}', '"bad"', 'null', '[{"state_id": 4060.5, "state_code": "MWT"}]'):
            out.append((f'parquet_bad_list_{raw}', self.parquet_frame(lambda df, raw=raw: df.__setitem__('states', [raw, None])), 'refuse'))
            out.append((f'toon_bad_list_{raw}', self.toon_rows(lambda rows, raw=raw: rows[0].update(states=raw)), 'refuse'))
        # malformed files and invalid UTF-8 anywhere
        for rel in ('json/counties.json', 'csv/counties.csv', 'csv/county_states.csv', 'plist/counties.plist', 'plist/county_states.plist',
                    'xml/counties.xml', 'yml/counties.yml', 'mongodb/counties.json', 'parquet/counties.parquet', 'toon/counties.toon',
                    'sqlserver/counties.sql', 'sqlserver/county_states.sql'):
            out.append((f'malformed_{rel}', lambda r, rel=rel: (r / rel).write_bytes(b'\xffbroken'), 'refuse'))
        for rel, old, new in (('json/counties.json', b'Waitomo', b'Waitom\xff'), ('mongodb/counties.json', b'Waitomo', b'Waitom\xff'),
                              ('yml/counties.yml', b'Waitomo', b'Waitom\xff'), ('csv/counties.csv', b'Waitomo', b'Waitom\xff'),
                              ('xml/counties.xml', b'NTL', b'N\xffL'), ('sqlserver/counties.sql', b'Waitomo', b'Waitom\xff')):
            out.append((f'invalid_utf8_{rel}', lambda r, rel=rel, old=old, new=new: (r / rel).write_bytes((r / rel).read_bytes().replace(old, new)), 'refuse'))
        out += [('yaml_multi_document', A('yml/counties.yml', '\n---\ncounty: []\n'), 'refuse'),
                ('json_trailing_document', A('json/counties.json', '\n[]'), 'refuse'),
                ('toon_trailing_document', A('toon/counties.toon', '\nextra: 999'), 'refuse')]
        # every CSV row one cell short or long, in both files
        with tempfile.TemporaryDirectory() as d:
            write_exports(Path(d))
            for table in ('counties', 'county_states'):
                with (Path(d) / f'csv/{table}.csv').open(newline='') as fh:
                    original = list(csv.reader(fh))
                for ri in range(1, len(original)):
                    for pos in range(len(original[0]) + 1):
                        for kind in ('remove', 'insert'):
                            if kind == 'remove' and pos == len(original[0]):
                                continue

                            def cell(root, table=table, original=original, ri=ri, pos=pos, kind=kind):
                                """One row one cell short or long."""
                                rows = copy.deepcopy(original)
                                rows[ri].pop(pos) if kind == 'remove' else rows[ri].insert(pos, 'x')
                                with (root / f'csv/{table}.csv').open('w', newline='') as fh:
                                    csv.writer(fh).writerows(rows)
                            out.append((f'csv_{table}_{ri}_{pos}_{kind}', cell, 'refuse'))
        # compatibility controls: order, indentation, column order, binary property lists
        for table in ('counties', 'county_states'):
            def reorder(root, table=table):
                """Reverse records and columns together."""
                p = root / f'csv/{table}.csv'
                with p.open(newline='') as fh:
                    rows = list(csv.reader(fh))
                with p.open('w', newline='') as fh:
                    csv.writer(fh).writerows([list(reversed(rows[0]))] + [list(reversed(row)) for row in reversed(rows[1:])])
            out.append((f'csv_{table}_ordering', reorder, 'pass'))
        out.append(('xml_indented', self.xml(lambda t: ET.indent(t)), 'pass'))

        def reverse_json(rel):
            """Reverse counties and the target's regions in a JSON export."""
            def apply(root):
                """Load, reverse, write."""
                rows = json.loads((root / rel).read_text())
                rows[0]['states'].reverse()
                rows.reverse()
                (root / rel).write_text(json.dumps(rows))
            return apply

        def reverse_yaml(root):
            """Reverse counties and regions in YAML."""
            import yaml
            doc = yaml.safe_load((root / 'yml/counties.yml').read_text())
            doc['county'][0]['states'].reverse()
            doc['county'].reverse()
            (root / 'yml/counties.yml').write_text(yaml.safe_dump(doc))

        def reverse_xml(t):
            """Reverse counties and the target's regions in XML."""
            states = t[0].findall('states')
            for s in states:
                t[0].remove(s)
            for s in reversed(states):
                t[0].append(s)
            t[:] = list(reversed(list(t)))

        def reverse_parquet(root):
            """Reverse rows and the target's regions in Parquet."""
            import pandas as pd
            p = root / 'parquet/counties.parquet'
            df = pd.read_parquet(p)
            df.loc[0, 'states'] = json.dumps(list(reversed(REGIONS)))
            df.iloc[::-1].to_parquet(p)

        def reverse_toon(rows):
            """Reverse rows and regions for TOON."""
            rows[0]['states'].reverse()
            rows.reverse()
        out += [('json_ordering', reverse_json('json/counties.json'), 'pass'), ('mongodb_ordering', reverse_json('mongodb/counties.json'), 'pass'),
                ('yml_ordering', reverse_yaml, 'pass'), ('xml_ordering', self.xml(reverse_xml), 'pass'),
                ('parquet_ordering', reverse_parquet, 'pass'), ('toon_ordering', self.toon_rows(reverse_toon), 'pass')]
        return out

    def test_every_case(self):
        """Every refuse case reports a problem; every pass case none."""
        cases = self.cases()
        self.assertGreater(len(cases), 170)
        for name, change, expected in cases:
            with self.subTest(name):
                found = self.run_case(change)
                if expected == 'pass':
                    self.assertEqual(found, [], name)
                else:
                    self.assertNotEqual(found, [], name)

    def test_rebuilt_fixtures(self):
        """A valid U+FFFD code corrupted to an invalid byte only in TOON, and a code with a quote left unquoted only in
        CSV, are refused; both untouched fixtures pass."""
        for code, rel, old, new in (('�', 'toon/counties.toon', '�'.encode(), b'\xff'),
                                    ('N"TL', 'csv/counties.csv', b'"N""TL"', b'N"TL')):
            counties = copy.deepcopy(COUNTIES)
            counties[1]['state_code'] = code
            with self.subTest(code=code):
                self.assertEqual(self.run_case(lambda r: None, counties), [])
                self.assertNotEqual(self.run_case(lambda r, rel=rel, old=old, new=new: (r / rel).write_bytes(
                    (r / rel).read_bytes().replace(old, new)), counties), [])



class Round6RegressionTest(Round5RegressionTest):
    """Codex review_county_regions_6: SQL identifier aliases, the exporter's SQL scaffold order and exact DDL, TOON
    header spellings, and the text "null" against a real null in every format."""

    test_every_case = test_rebuilt_fixtures = None   # inherited helpers only

    def round6_cases(self):
        """(name, change, expected) for the round-6 mutations and their controls."""
        T, A = self.text, self.append
        out = [('positive', lambda r: None, 'pass')]
        # 1. a column named twice under another spelling
        for table, first in (('counties', '(9, '), ('county_states', '(9, ')):
            for alias in ('[state_id]', '"state_id"', 'STATE_ID'):
                def aliased(root, table=table, alias=alias):
                    """Prepend an aliased state_id column with a contradictory value in every row."""
                    import re
                    p = root / f'sqlserver/{table}.sql'
                    data = p.read_text().replace(f'INSERT INTO world.{table} (', f'INSERT INTO world.{table} ({alias}, ', 1)
                    start = data.index(' VALUES\n') + len(' VALUES\n')
                    end = data.index(';', start)
                    p.write_text(data[:start] + re.sub(r'(?m)^\(', '(999, ', data[start:end]) + data[end:])
                out.append((f'sql_{table}_duplicate_alias_{alias}', aliased, 'refuse'))
        # 2. the exporter's statements, in its order, with its exact declarations
        counties, relation = 'sqlserver/counties.sql', 'sqlserver/county_states.sql'
        out += [('sql_counties_trailing_drop', A(counties, "IF OBJECT_ID('world.counties', 'U') IS NOT NULL DROP TABLE world.counties;\n"), 'refuse'),
                ('sql_county_states_trailing_drop', A(relation, "IF OBJECT_ID('world.county_states', 'U') IS NOT NULL DROP TABLE world.county_states;\n"), 'refuse'),
                ('sql_counties_identity_on_missing', T(counties, 'SET IDENTITY_INSERT world.counties ON;', ''), 'refuse'),
                ('sql_counties_identity_off_missing', T(counties, 'SET IDENTITY_INSERT world.counties OFF;', ''), 'refuse'),
                ('sql_counties_parent_switch_missing', T(counties, 'ALTER TABLE world.counties NOCHECK CONSTRAINT FK_counties_parent;', ''), 'refuse'),
                ('sql_county_states_identity_switch', T(relation, 'INSERT INTO', 'SET IDENTITY_INSERT world.county_states ON;\nINSERT INTO'), 'refuse'),
                ('sql_counties_create_unconsumed_text', T(counties, ')\n);\n\nALTER', ')\n) BROKEN TEXT;\n\nALTER'), 'refuse'),
                ('sql_county_states_create_unconsumed_text', T(relation, 'world.states(id)\n);', 'world.states(id)\n) BROKEN TEXT;'), 'refuse'),
                ('sql_county_states_quoted_foreign_key', T(relation, '    CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)\n',
                                                          "    note NVARCHAR(255) DEFAULT N'FOREIGN KEY (state_id) REFERENCES world.states(id)'\n"), 'refuse'),
                ('sql_counties_state_id_not_null', T(counties, 'state_id INT NULL', 'state_id INT NOT NULL'), 'refuse'),
                ('sql_counties_pair_check_dropped', T(counties, ',\n    CONSTRAINT CK_counties_state_pair', ',\n    -- CONSTRAINT CK_counties_state_pair'), 'refuse')]
        for table in ('counties', 'county_states'):
            def before_create(root, table=table):
                """Move the insert statement before the DROP and CREATE."""
                p = root / f'sqlserver/{table}.sql'
                data = p.read_text()
                start = data.index(f'INSERT INTO world.{table}')
                end = data.index(';', start) + 2
                insert = data[start:end]
                data = data[:start] + data[end:]
                at = data.index('IF OBJECT_ID')
                p.write_text(data[:at] + insert + data[at:])
            out.append((f'sql_{table}_insert_before_create', before_create, 'refuse'))
        # 3. TOON header names, quoted or spaced, before the raw-number gate
        out += [('toon_quoted_header_id_control', T('toon/counties.toon', '{id,', '{"id",'), 'pass'),
                ('toon_quoted_header_state_id_control', T('toon/counties.toon', ',state_id,', ',"state_id",'), 'pass'),
                ('toon_quoted_header_id_rounded', lambda r: (T('toon/counties.toon', '{id,', '{"id",')(r), T('toon/counties.toon', '  9,', '  9.0000000000000001,')(r)), 'refuse'),
                ('toon_quoted_header_state_id_rounded', lambda r: (T('toon/counties.toon', ',state_id,', ',"state_id",')(r), T('toon/counties.toon', ',4059,', ',4059.0000000000001,')(r)), 'refuse'),
                ('toon_spaced_header_id_rounded', lambda r: (T('toon/counties.toon', '{id,', '{ id,')(r), T('toon/counties.toon', '  9,', '  9.0000000000000001,')(r)), 'refuse'),
                ('toon_spaced_header_state_id_rounded', lambda r: (T('toon/counties.toon', ',state_id,', ', state_id,')(r), T('toon/counties.toon', ',4059,', ',4059.0000000000001,')(r)), 'refuse'),
                ('toon_missing_state_id_header', T('toon/counties.toon', ',state_id,', ',stateid,'), 'refuse')]
        # 4. the text "null" is never a null, in any format
        out += [('json_states_text_null', T('json/counties.json', '"states": null', '"states": "null"'), 'refuse'),
                ('mongodb_state_id_text_null', T('mongodb/counties.json', '"state_id": null', '"state_id": "null"'), 'refuse'),
                ('mongodb_states_text_null', T('mongodb/counties.json', '"states": null', '"states": "null"'), 'refuse'),
                ('yml_state_id_text_null', T('yml/counties.yml', '  state_id: null', "  state_id: 'null'"), 'refuse'),
                ('yml_states_text_null', T('yml/counties.yml', '  states: null', "  states: 'null'"), 'refuse'),
                ('xml_state_id_text_null', self.xml(lambda t: setattr(t[0].find('state_id'), 'text', 'null')), 'refuse'),
                ('xml_state_code_text_null', self.xml(lambda t: setattr(t[0].find('state_code'), 'text', 'null')), 'refuse'),
                ('csv_state_id_text_null', T('csv/counties.csv', '9,Waitomo District,,', '9,Waitomo District,null,'), 'refuse'),
                ('plist_state_id_text_null', T('plist/counties.plist', '<key>state_id</key>\n\t\t<string></string>', '<key>state_id</key>\n\t\t<string>null</string>'), 'refuse'),
                ('sql_state_id_text_null', T(counties, 'NULL, NULL', "N'null', NULL"), 'refuse'),
                ('sql_state_code_text_null', T(counties, 'NULL, NULL', "NULL, N'null'"), 'refuse'),
                ('parquet_states_text_null', self.parquet_frame(lambda df: df.__setitem__('states', [df.loc[0, 'states'], 'null'])), 'refuse'),
                ('parquet_state_code_text_null', self.parquet_frame(lambda df: df.__setitem__('state_code', ['null', df.loc[1, 'state_code']])), 'refuse'),
                ('toon_states_text_null', self.toon_rows(lambda rows: rows[1].update(states='null')), 'refuse'),
                ('toon_state_id_text_null', T('toon/counties.toon', '  9,Waitomo District,null,', '  9,Waitomo District,"null",'), 'refuse')]
        return out

    def test_round6_cases(self):
        """Every refuse case reports a problem; every pass case none."""
        for name, change, expected in self.round6_cases():
            with self.subTest(name):
                found = self.run_case(change)
                if expected == 'pass':
                    self.assertEqual(found, [], name)
                else:
                    self.assertNotEqual(found, [], name)



class Round7RegressionTest(Round5RegressionTest):
    """Codex review_county_regions_7: SQL produced by plausible exporter-source changes (undeclared INSERT columns, a
    constraint switch without its constraint, an empty declaration, an INSERT over SQL Server's 1,000 rows), and a
    wrong ExportJson that every derived format repeats: the checker's expectations come from contributions/, not from
    json/counties.json."""

    test_every_case = test_rebuilt_fixtures = None   # inherited helpers only

    @staticmethod
    def many(n):
        """COUNTIES plus n one-state counties, ids 100 upwards."""
        return COUNTIES + [{'id': 100 + i, 'name': f'County {i}', 'state_id': 4059, 'state_code': 'NTL', 'states': None,
                            'country_id': 158} for i in range(n)]

    def run_with(self, change, counties=None, source=None):
        """Problems after writing exports (from counties) and contributions (from source) and applying change."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_exports(root, counties=counties, source=source)
            change(root)
            return main(9, root)

    def test_sql_from_exporter_source_changes(self):
        """Each emitted consequence of an exporter-source change is refused; the unchanged files pass."""
        T = self.text
        counties = 'sqlserver/counties.sql'
        self.assertEqual(self.run_with(lambda r: None), [])

        def undeclared_states(root):
            """array_intersect dropped: the JSON-only states field becomes an INSERT column."""
            import re
            p = root / counties
            data = p.read_text().replace('INSERT INTO world.counties (', 'INSERT INTO world.counties (states, ', 1)
            start = data.index(' VALUES\n') + len(' VALUES\n')
            end = data.index(';', start)
            p.write_text(data[:start] + re.sub(r'(?m)^\(', "(N'x', ", data[start:end]) + data[end:])
        for name, change in (
                ('sql_undeclared_states', undeclared_states),
                ('sql_missing_parent_constraint', T(counties, '    CONSTRAINT FK_counties_parent FOREIGN KEY (parent_id) REFERENCES world.counties(id),\n', '')),
                ('sql_internal_double_create_comma', T(counties, 'REFERENCES world.counties(id),', 'REFERENCES world.counties(id),,')),
                ('sql_relation_trailing_create_comma', T('sqlserver/county_states.sql', 'REFERENCES world.states(id)\n);', 'REFERENCES world.states(id),\n);'))):
            with self.subTest(name):
                self.assertNotEqual(self.run_with(change), [], name)

    def test_insert_batches_at_most_1000_rows(self):
        """1,001 counties in batches of 900 and 101 pass; the same rows in one INSERT of 1,001 are refused."""
        counties = self.many(999)
        self.assertEqual(len(counties), 1001)
        self.assertEqual(self.run_with(lambda r: None, counties=counties), [])

        def one_batch(root):
            """Join the two batches into one statement."""
            p = root / 'sqlserver/counties.sql'
            data = p.read_text()
            first = data.index('INSERT INTO world.counties')
            second = data.index('INSERT INTO world.counties', first + 1)
            values_start = data.index(' VALUES\n', second) + len(' VALUES\n')
            joined = data[:data.rindex(';', first, second)] + ',\n' + data[values_start:]
            p.write_text(joined)
        self.assertNotEqual(self.run_with(one_batch, counties=counties), [])

    def test_expectations_come_from_contributions(self):
        """An ExportJson that drops the one-state counties, or writes full ISO codes as region codes, is repeated by
        every derived format; comparing with contributions/ refuses both. Unchanged exports pass."""
        missing_own = [c for c in COUNTIES if c['state_id'] is None]
        self.assertNotEqual(self.run_with(lambda r: None, counties=missing_own, source=COUNTIES), [])
        iso = copy.deepcopy(COUNTIES)
        iso[0]['states'] = [{'state_id': s['state_id'], 'state_code': 'NZ-' + s['state_code']} for s in REGIONS]
        found = self.run_with(lambda r: None, counties=iso, source=COUNTIES)
        self.assertTrue(any(p.startswith('json/counties.json') for p in found), found)
        self.assertTrue(any(p.startswith('csv/county_states.csv') for p in found), found)

    def test_contributions_must_be_well_formed(self):
        """A county without an id, a repeated id, or a region code that is not its state's iso2 in contributions/ is
        reported, not used as an expectation."""
        for name, change in (
                ('no id', lambda c: c[1].pop('id')),
                ('repeated id', lambda c: c.append(dict(c[1]))),
                ('region code not iso2', lambda c: c[0]['states'][0].update(state_code='XX'))):
            source = copy.deepcopy(COUNTIES)
            change(source)
            with self.subTest(name):
                found = self.run_with(lambda r: None, source=source)
                self.assertTrue(any(p.startswith('contributions/') for p in found), found)
