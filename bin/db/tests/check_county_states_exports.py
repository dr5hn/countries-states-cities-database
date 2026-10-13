#!/usr/bin/env python3
"""Check a county of several regions in every export format, after import and export (v5, decision B6).

Run from the repository root after the exports:  python3 bin/db/tests/check_county_states_exports.py <county id>
The county must have a null state pair and the same two or more regions in every format: the states list in JSON,
YAML, XML, MongoDB, Parquet and TOON, the county_states rows in CSV, PLIST and SQL Server. No other county may lose its
state. It exits 1 with a list of problems, or 0 after printing what it checked. It reads the generated files only.
"""
import csv
import json
import plistlib
import re
import sys
import xml.etree.ElementTree as ET  # parses the export just generated in this run, not outside input
from pathlib import Path

from check_null_state_exports import _read, _records, _yaml

PAIR = ('state_id', 'state_code')


def _regions(listed):
    """A states list as sorted (state_id, state_code) tuples, or None when it is not a list of pairs."""
    if not isinstance(listed, list) or not all(isinstance(r, dict) for r in listed):
        return None
    return sorted((int(r.get('state_id')), r.get('state_code')) for r in listed)


def _csv_rows(path):
    """Rows of a CSV export."""
    with open(path, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def main(county_id, root='.'):
    """Check each format under root; return the problems found."""
    problems = []
    need = lambda ok, msg: ok or problems.append(msg)

    counties = _read(root, 'json/counties.json', _records, problems)
    if counties is None:
        return problems
    hits = [c for c in counties if c.get('id') == county_id]
    regions = _regions(hits[0].get('states')) if len(hits) == 1 else None
    if len(hits) != 1 or any(k not in hits[0] or hits[0][k] is not None for k in PAIR) or not regions or len(regions) < 2:
        problems.append(f'json/counties.json: county {county_id} needs a null state pair and two or more regions')
        return problems
    several = {c['id'] for c in counties if c.get('states')}
    need(all(c.get('state_id') is not None for c in counties if c['id'] not in several),
         'json/counties.json: a county without regions has no state')

    def relation_check(rel, rows):
        """The county's rows in a county_states listing equal its regions."""
        mine = sorted((int(r['state_id']), r['state_code']) for r in rows if str(r.get('county_id')) == str(county_id))
        need(mine == regions, f'{rel}: regions differ ({mine} != {regions})')

    for fmt, parse in (('csv', _csv_rows), ('plist', lambda p: plistlib.loads(p.read_bytes()))):
        flat = _read(root, f'{fmt}/counties.{fmt}', parse, problems)
        if flat is not None:
            row = [r for r in flat if r.get('id') == str(county_id)]
            need(len(row) == 1 and all(row[0].get(k) == '' for k in PAIR), f'{fmt}/counties.{fmt}: state fields are not empty')
        rows = _read(root, f'{fmt}/county_states.{fmt}', parse, problems)
        if rows is not None:
            relation_check(f'{fmt}/county_states.{fmt}', rows)

    xml = _read(root, 'xml/counties.xml', lambda p: ET.parse(p).getroot(), problems)
    if xml is not None:
        el = [e for e in xml if e.findtext('id') == str(county_id)]
        need(len(el) == 1 and all(el[0].findtext(k) == '' for k in PAIR), 'xml/counties.xml: state elements are missing or not empty')
        if len(el) == 1:
            mine = sorted((int(s.findtext('state_id')), s.findtext('state_code')) for s in el[0].findall('states'))
            need(mine == regions, f'xml/counties.xml: regions differ ({mine} != {regions})')

    for rel, parse, key in (('yml/counties.yml', _yaml, 'id'), ('mongodb/counties.json', _records, '_id')):
        rows = _read(root, rel, parse, problems)
        if rows is not None:
            row = [c for c in rows if c.get(key) == county_id]
            ok = len(row) == 1 and all(k in row[0] and row[0][k] is None for k in PAIR) and _regions(row[0].get('states')) == regions
            need(ok and 'state' not in row[0], f'{rel}: state pair not null, regions differ, or a state reference exists')

    def parquet(path):
        """The counties table of the Parquet export."""
        import pandas as pd
        return pd.read_parquet(path)
    df = _read(root, 'parquet/counties.parquet', parquet, problems)
    if df is not None:
        missing = sorted({'id', 'states', *PAIR} - set(df.columns))
        need(not missing, f"parquet: a column is missing ({', '.join(missing)})")
        if not missing:
            need(str(df['state_id'].dtype) == 'Int64', f"parquet: state_id is {df['state_id'].dtype}, not Int64")
            row = df[df['id'] == county_id]
            need(len(row) == 1 and all(row[k].isna().iloc[0] for k in PAIR)
                 and _regions(json.loads(row['states'].iloc[0])) == regions, 'parquet: state pair not null or regions differ')
            need(int(df['state_id'].notna().sum()) == len(df) - len(several), 'parquet: another county lost its state')

    toon = _read(root, 'toon/counties.toon', lambda p: p.read_text(encoding='utf-8').splitlines(), problems)
    if toon is not None:
        row = [line for line in toon if line.startswith(f'  {county_id},')]
        cell = re.search(r'"(\[.*\])"', row[0]) if len(row) == 1 else None
        listed = json.loads(cell.group(1).replace('\\"', '"')) if cell else None
        need(len(row) == 1 and ',null,null,' in row[0], 'toon/counties.toon: state pair is not null')
        need(_regions(listed) == regions, f'toon/counties.toon: regions differ ({_regions(listed)} != {regions})')

    sql = _read(root, 'sqlserver/county_states.sql', lambda p: p.read_text(encoding='utf-8'), problems)
    if sql is not None:
        mine = sorted(int(s) for s in re.findall(rf'\({county_id}, (\d+)\)', sql))
        need(mine == [r[0] for r in regions], f'sqlserver/county_states.sql: regions differ ({mine})')
    return problems


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: check_county_states_exports.py <county id>')
    found = main(int(sys.argv[1]))
    for p in found:
        print(f'[ERROR] {p}')
    if found:
        sys.exit(1)
    print(f'[INFO] county {sys.argv[1]} has no state and the same regions in json, csv, plist, xml, yaml, mongodb, parquet, '
          'toon and sqlserver; every other county keeps its state')
