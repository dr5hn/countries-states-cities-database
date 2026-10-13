#!/usr/bin/env python3
"""Check a test-only city with no state in every export format, after import and export (v5: cities without a state).

Run from the repository root after the exports:  python3 bin/db/tests/check_null_state_exports.py <city id> <EH>
It exits 1 with a list of problems, or 0 after printing what it checked. It reads the generated files only. Every file
below must exist, and each must carry the city's state fields explicitly empty (a missing field is a problem).
"""
import csv
import json
import plistlib
import sys
import xml.etree.ElementTree as ET  # parses the export just generated in this run, not outside input
from pathlib import Path

STATE = ('state_id', 'state_code', 'state_name')


def _read(root, rel, parse, problems):
    """Parse one generated file, or record that it is missing or unreadable and return None."""
    path = Path(root, rel)
    if not path.is_file():
        problems.append(f'{rel}: not generated')
        return None
    try:
        return parse(path)
    except Exception as e:   # any parse failure is a failed check, reported with the file
        problems.append(f'{rel}: cannot be read: {e}')
        return None


def _records(path):
    """The JSON array of record objects in a generated file; null, an object root or a non-object row is a ValueError."""
    doc = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(doc, list) or not all(isinstance(r, dict) for r in doc):
        raise ValueError('not a JSON array of objects')
    return doc


def _yaml(path):
    """The list of cities in the YAML export."""
    import yaml
    loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)   # the C loader when built: minutes faster on all cities
    doc = yaml.load(path.read_text(encoding='utf-8'), Loader=loader)
    return doc if isinstance(doc, list) else next(v for v in doc.values() if isinstance(v, list))


def main(city_id, country, root='.'):
    """Check each format under root; return the problems found."""
    problems = []
    need = lambda ok, msg: ok or problems.append(msg)

    flat = _read(root, 'json/cities.json', _records, problems)
    if flat is not None:
        hits = [c for c in flat if c.get('id') == city_id]
        need(len(hits) == 1, f'json/cities.json: city {city_id} appears {len(hits)} times')
        need(len(hits) == 1 and all(k in hits[0] and hits[0][k] is None for k in STATE), 'json/cities.json: state fields are not null')

    nested = _read(root, 'json/countries+states+cities.json', _records, problems)
    if nested is not None and flat is not None:
        ids = [c['id'] for n in nested for c in n.get('cities', [])] + [c['id'] for n in nested for s in n['states'] for c in s['cities']]
        need(sorted(ids) == sorted(c['id'] for c in flat), 'countries+states+cities.json: cities are not each listed exactly once')
        home = [n for n in nested if n['iso2'] == country]
        need(bool(home) and city_id in [c['id'] for c in home[0].get('cities', [])], f'countries+states+cities.json: city {city_id} is not in {country} cities')

    rows = _read(root, 'csv/cities.csv', lambda p: list(csv.DictReader(open(p, encoding='utf-8'))), problems)
    if rows is not None:
        rows = [r for r in rows if r.get('id') == str(city_id)]
        need(len(rows) == 1 and all(rows[0].get(k) == '' for k in STATE), 'csv/cities.csv: state fields are not empty')

    plist = _read(root, 'plist/cities.plist', lambda p: plistlib.loads(p.read_bytes()), problems)
    if plist is not None:
        plist = [r for r in plist if r.get('id') == str(city_id)]
        need(len(plist) == 1 and all(plist[0].get(k) == '' for k in STATE), 'plist/cities.plist: state fields are not empty')

    xml = _read(root, 'xml/cities.xml', lambda p: ET.parse(p).getroot(), problems)
    if xml is not None:
        xml = [e for e in xml if e.findtext('id') == str(city_id)]
        # findtext gives None for a missing element and '' for an empty one: only an element that exists and is empty passes
        need(len(xml) == 1 and all(xml[0].findtext(k) == '' for k in STATE), 'xml/cities.xml: state elements are missing or not empty')

    y = _read(root, 'yml/cities.yml', _yaml, problems)
    if y is not None:
        y = [c for c in y if c.get('id') == city_id]
        need(len(y) == 1 and all(k in y[0] and y[0][k] is None for k in STATE), 'yml/cities.yml: state fields are not null')

    mongo = _read(root, 'mongodb/cities.json', _records, problems)
    if mongo is not None:
        mongo = [c for c in mongo if c.get('_id') == city_id]
        need(len(mongo) == 1 and all(k in mongo[0] and mongo[0][k] is None for k in STATE) and 'state' not in mongo[0],
             'mongodb/cities.json: state fields are not explicitly null, or a state reference exists')

    def parquet(path):
        """The cities table of the Parquet export."""
        import pandas as pd
        return pd.read_parquet(path)
    df = _read(root, 'parquet/cities.parquet', parquet, problems)
    if df is not None:
        missing = sorted({'id', *STATE} - set(df.columns))
        need(not missing, f"parquet: a state column is missing ({', '.join(missing)})")
        if not missing:
            need(str(df['state_id'].dtype) == 'Int64', f"parquet: state_id is {df['state_id'].dtype}, not Int64")
            row = df[df['id'] == city_id]
            need(len(row) == 1 and all(row[k].isna().iloc[0] for k in STATE), 'parquet: state fields are not null')
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
