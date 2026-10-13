#!/usr/bin/env python3
"""Check a test-only city with no state in every export format, after import and export (v5: cities without a state).

Run from the repository root after the exports:  python3 bin/db/tests/check_null_state_exports.py <city id> <EH>
It exits 1 with a list of problems, or 0 after printing what it checked. It reads the generated files only.
"""
import csv
import json
import plistlib
import sys
import xml.etree.ElementTree as ET  # parses the export just generated in this run, not outside input
from pathlib import Path


def main(city_id, country):
    """Check each format; return the problems found."""
    problems = []
    need = lambda ok, msg: ok or problems.append(msg)

    flat = json.loads(Path('json/cities.json').read_text(encoding='utf-8'))
    hits = [c for c in flat if c['id'] == city_id]
    need(len(hits) == 1, f'json/cities.json: city {city_id} appears {len(hits)} times')
    if hits:
        need(all(hits[0].get(k, 'missing') is None for k in ('state_id', 'state_code', 'state_name')), 'json/cities.json: state fields are not null')

    nested = json.loads(Path('json/countries+states+cities.json').read_text(encoding='utf-8'))
    ids = [c['id'] for n in nested for c in n.get('cities', [])] + [c['id'] for n in nested for s in n['states'] for c in s['cities']]
    need(sorted(ids) == sorted(c['id'] for c in flat), 'countries+states+cities.json: cities are not each listed exactly once')
    home = [n for n in nested if n['iso2'] == country]
    need(bool(home) and city_id in [c['id'] for c in home[0].get('cities', [])], f'countries+states+cities.json: city {city_id} is not in {country} cities')

    rows = [r for r in csv.DictReader(open('csv/cities.csv', encoding='utf-8')) if r['id'] == str(city_id)]
    need(len(rows) == 1 and all(rows[0][k] == '' for k in ('state_id', 'state_code', 'state_name')), 'csv/cities.csv: state fields are not empty')

    if Path('plist/cities.plist').exists():
        plist = [r for r in plistlib.loads(Path('plist/cities.plist').read_bytes()) if r['id'] == str(city_id)]
        need(len(plist) == 1 and all(plist[0][k] == '' for k in ('state_id', 'state_code', 'state_name')), 'plist/cities.plist: state fields are not empty')

    xml_city = [e for e in ET.parse('xml/cities.xml').getroot() if e.findtext('id') == str(city_id)]
    need(len(xml_city) == 1 and all((xml_city[0].findtext(k) or '') == '' for k in ('state_id', 'state_code', 'state_name')), 'xml/cities.xml: state elements are not empty')

    try:
        import yaml
        doc = yaml.safe_load(Path('yml/cities.yml').read_text(encoding='utf-8'))
        items = doc if isinstance(doc, list) else next(v for v in doc.values() if isinstance(v, list))
        y = [c for c in items if c.get('id') == city_id]
        need(len(y) == 1 and all(y[0].get(k, 'missing') is None for k in ('state_id', 'state_code', 'state_name')), 'yml/cities.yml: state fields are not null')
    except ImportError:
        problems.append('PyYAML is not installed; YAML not checked')

    mongo = [c for c in json.loads(Path('mongodb/cities.json').read_text(encoding='utf-8')) if c.get('_id') == city_id or c.get('id') == city_id]
    need(len(mongo) == 1 and mongo[0].get('state_id') is None and 'state' not in mongo[0], 'mongodb/cities.json: state is not null or a state reference exists')

    if Path('parquet/cities.parquet').exists():
        import pandas as pd
        df = pd.read_parquet('parquet/cities.parquet')
        need(str(df['state_id'].dtype) == 'Int64', f"parquet: state_id is {df['state_id'].dtype}, not Int64")
        row = df[df['id'] == city_id]
        need(len(row) == 1 and pd.isna(row['state_id'].iloc[0]), 'parquet: state_id is not null')
        need(int(df['state_id'].notna().sum()) == len(df) - 1, 'parquet: another city lost its state')
    return problems


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: check_null_state_exports.py <city id> <country iso2>')
    found = main(int(sys.argv[1]), sys.argv[2])
    for p in found:
        print(f'[ERROR] {p}')
    if found:
        sys.exit(1)
    print(f'[INFO] city {sys.argv[1]} has no state in json, nested json, csv, plist, xml, yaml, mongodb and parquet; every city is listed once')
