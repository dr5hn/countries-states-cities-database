#!/usr/bin/env python3
"""Check counties of several regions in every export format, after import and export (v5, decision B6).

Run from the repository root after the exports:  python3 bin/db/tests/check_county_states_exports.py <county id>
json/counties.json is the authority. The given county must have a null state pair and two or more distinct regions
there. Every county, that one and all others, must then have the same state pair and the same regions in every other
format: the states list in YAML, XML, MongoDB, Parquet and TOON (read with the reference reader), the county_states
rows in CSV, PLIST and SQL Server, and the state columns of each counties file, SQL Server's included. Counts are
never used in place of equality. Exits 1 with the problems, or 0 after printing what it checked.
"""
import csv
from collections import Counter
import json
import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET  # parses the export just generated in this run, not outside input
from pathlib import Path

from check_null_state_exports import _read, _records, _yaml

TOON_READER_DIR = Path(__file__).resolve().parents[2] / 'scripts' / 'export'   # where CI installs @toon-format/toon
TOON_DECODE = ("const { decode } = await import('@toon-format/toon'); const fs = await import('node:fs'); "
               "process.stdout.write(JSON.stringify(decode(fs.readFileSync(process.argv[1], 'utf8'))))")


MISSING, INVALID, BAD = '(missing)', '(invalid list)', '(invalid value)'   # never equal to a real id, code, pair or list
POSITIVE_INT_TEXT = re.compile(r'[1-9][0-9]*')


def _native_id(v):
    """An id from a typed format (JSON, YAML, MongoDB, TOON, Parquet): a positive int, never a boolean or a fraction;
    anything else is BAD."""
    return v if type(v) is int and v > 0 else BAD


def _text_id(v, nullable=True):
    """An id from a text cell (CSV, PLIST, XML, SQL): '' is the null encoding when nullable, canonical positive integer
    text is the id; a missing cell (None, a short CSV row) or any other text is BAD, never null."""
    if v == '' and nullable:
        return None
    return int(v) if isinstance(v, str) and POSITIVE_INT_TEXT.fullmatch(v) else BAD


def _text_code(v):
    """A state code from a text cell: '' is null; a missing cell (None) is BAD."""
    return None if v == '' else v if isinstance(v, str) else BAD


def _regions(listed):
    """A states list as a sorted tuple of (state_id, state_code), or None when it is not a list of exact pairs with
    integer-typed positive ids and non-empty codes (no coercion: 4060.75, "4060" and true are not 4060)."""
    if not isinstance(listed, list) or not all(
            isinstance(r, dict) and set(r) == {'state_id', 'state_code'} and _native_id(r['state_id']) is not BAD
            and isinstance(r['state_code'], str) and r['state_code'] for r in listed):
        return None
    return tuple(sorted((r['state_id'], r['state_code']) for r in listed))


def _xml_regions(county):
    """An XML county's list: MISSING without a states element, None for one empty <states/>, the regions when every
    states element holds exactly one leaf state_id (positive integer text) and one leaf state_code and nothing else,
    INVALID for anything else."""
    listed = county.findall('states')
    if not listed:
        return MISSING
    blank = lambda t: not (t or '').strip()
    if len(listed) == 1 and len(listed[0]) == 0 and blank(listed[0].text):
        return None
    pairs = []
    for el in listed:
        children = list(el)
        if not blank(el.text) or sorted(c.tag for c in children) != ['state_code', 'state_id'] \
                or any(len(c) or not blank(c.tail) for c in children):
            return INVALID
        sid_text, code = _xml_leaf(el, 'state_id'), _xml_leaf(el, 'state_code')
        sid = BAD if sid_text in (MISSING, BAD) else _text_id(sid_text, nullable=False)
        if sid is BAD or code in (MISSING, BAD) or not code:
            return INVALID
        pairs.append({'state_id': sid, 'state_code': code})
    return _list_value(pairs)


def _list_value(listed):
    """What a format holds for one county's list: None for no list, the regions tuple, or INVALID."""
    if listed is None:
        return None
    regions = _regions(listed)
    return INVALID if regions is None else regions


def _authority_errors(counties):
    """Every county of json/counties.json must be well formed: a unique positive integer id, both state keys, and either
    its own complete state pair with no list, or two explicit nulls and two or more distinct regions."""
    errors, seen = [], set()
    for c in counties:
        cid = c.get('id')
        if type(cid) is not int or cid <= 0:
            errors.append(f'json/counties.json: county id {cid!r} is not a positive integer')
            continue
        if cid in seen:
            errors.append(f'json/counties.json: county id {cid} is duplicated')
        seen.add(cid)
        if 'state_id' not in c or 'state_code' not in c:
            errors.append(f'json/counties.json: county {cid} lacks a state key')
        elif c['state_id'] is not None or c['state_code'] is not None:
            if c['state_id'] is None or c['state_code'] is None:
                errors.append(f'json/counties.json: county {cid} has no regions but not a full state pair')
            elif _native_id(c['state_id']) is BAD or not isinstance(c['state_code'], str) or not c['state_code']:
                errors.append(f'json/counties.json: county {cid} has an invalid state pair')
            elif c.get('states') is not None:
                errors.append(f'json/counties.json: county {cid} has a state and a states list')
        else:
            regions = _regions(c.get('states'))
            if not regions or len(regions) < 2 or len({sid for sid, _ in regions}) != len(regions) \
                    or any(sid <= 0 or not isinstance(code, str) or not code for sid, code in regions):
                errors.append(f'json/counties.json: county {cid} has a null state pair, so it needs two or more distinct regions')
    return errors


def _csv_rows(path):
    """Rows of a CSV export as dicts by header name. A row with fewer or more cells than the header is kept but marked
    with a None key (as csv.DictReader marks surplus cells), so _flat_row_ok() refuses it before any field is read."""
    with open(path, encoding='utf-8', newline='') as fh:
        rows = list(csv.reader(fh))
    header, out = rows[0] if rows else [], []
    for row in rows[1:]:
        d = dict(zip(header, row))
        if len(row) != len(header):
            d[None] = f'{len(row)} cells for {len(header)} columns'
        out.append(d)
    return out


def _flat_row_ok(row):
    """Whether a CSV or PLIST row is whole: no surplus-cell key and no missing (None) cell anywhere."""
    return None not in row and all(v is not None for v in row.values())


def _xml_leaf(parent, tag):
    """The text of exactly one leaf element <tag> under parent ('' when empty): MISSING when absent, BAD when repeated or
    when it has child elements. Every XML scalar the checker reads goes through here."""
    found = parent.findall(tag)
    if not found:
        return MISSING
    if len(found) > 1 or len(found[0]):
        return BAD
    return found[0].text or ''


def _toon(path):
    """The rows of a TOON export, decoded by the reference reader (@toon-format/toon) under Node."""
    run = subprocess.run(['node', '--input-type=module', '-e', TOON_DECODE, str(Path(path).resolve())], cwd=TOON_READER_DIR,
                         capture_output=True, text=True, timeout=600)
    if run.returncode != 0:
        raise ValueError(f'the TOON reference reader failed: {run.stderr.strip()[-300:]}')
    return json.loads(run.stdout)


class SqlText(str):
    """A quoted SQL Server literal (N'...'), kept apart from bare tokens such as 4059 or NULL."""


def _sql_id(v, nullable=True):
    """An id from a SQL Server VALUES row: NULL is null when nullable; a bare positive integer is the id; quoted text
    or anything else is BAD."""
    if v is None:
        return None if nullable else BAD
    return BAD if isinstance(v, SqlText) else _text_id(v, nullable=False)


def _sql_code(v):
    """A state code from a SQL Server VALUES row: NULL is null, non-empty quoted text is the code, anything else BAD."""
    return None if v is None else str(v) if isinstance(v, SqlText) and v else BAD


def _typed_id(v):
    """A nullable id from a typed format: null, or a positive int (never a boolean or a fraction)."""
    return None if v is None else _native_id(v)


def _typed_code(v):
    """A nullable state code from a typed format: null, or a non-empty string."""
    return None if v is None else v if isinstance(v, str) and v else BAD


def _sql_values(row):
    """The values of one SQL Server VALUES row, '(1, N'a,b', NULL)', as Python values (None for NULL)."""
    out, i, n = [], 0, len(row)
    while i < n:
        if row[i] in ' ,':
            i += 1
        elif row.startswith("N'", i) or row[i] == "'":
            i += 2 if row[i] == 'N' else 1
            buf = []
            while True:
                if row[i] == "'" and row[i + 1:i + 2] == "'":
                    buf.append("'")
                    i += 2
                elif row[i] == "'":
                    i += 1
                    break
                else:
                    buf.append(row[i])
                    i += 1
            out.append(SqlText(''.join(buf)))
        else:
            j = i
            while j < n and row[j] != ',':
                j += 1
            token = row[i:j].strip()
            out.append(None if token == 'NULL' else token)
            i = j
    return out


def _sql_inserts(text, table):
    """Every row inserted into world.<table>, as dicts by column name (values as text, None for NULL)."""
    rows = []
    for m in re.finditer(rf'INSERT INTO world\.{table} \(([^)]*)\) VALUES\n(.*?);\n', text, re.S):
        cols = [c.strip() for c in m.group(1).split(',')]
        for line in m.group(2).split('\n'):
            line = line.strip().rstrip(',')
            if line.startswith('(') and line.endswith(')'):
                values = _sql_values(line[1:-1])
                if len(values) != len(cols):
                    raise ValueError(f'a {table} row has {len(values)} values for {len(cols)} columns')
                rows.append(dict(zip(cols, values)))
    return rows


def main(county_id, root='.'):
    """Check each format under root against json/counties.json; return the problems found."""
    problems = []
    need = lambda ok, msg: ok or problems.append(msg)

    counties = _read(root, 'json/counties.json', _records, problems)
    if counties is None:
        return problems
    authority = _authority_errors(counties)
    problems += authority
    if authority:
        return problems
    truth = {c['id']: ((c['state_id'], c['state_code']), _list_value(c.get('states'))) for c in counties}
    pair, regions = truth.get(county_id, ((0, 0), None))
    if pair != (None, None) or not regions:
        problems.append(f'json/counties.json: county {county_id} needs a null state pair and two or more distinct regions')
        return problems
    triples = sorted((cid, sid, code) for cid, (_, listed) in truth.items() if listed for sid, code in listed)

    def compare(where, rows, with_regions=True):
        """rows: (county id, state pair, regions) per record of one format. Every county must appear once, the id sets
        must be equal, and each county's pair (and regions) must equal the authority's."""
        got, dup = {}, set()
        for cid, got_pair, got_regions in rows:
            if cid in got:
                dup.add(cid)
            got[cid] = (got_pair, got_regions)
        for cid in sorted(dup, key=str)[:1]:
            problems.append(f'{where}: county {cid} appears {sum(1 for r in rows if r[0] == cid)} times')
        if set(got) != set(truth):
            extra, missing = sorted(set(got) - set(truth), key=str), sorted(set(truth) - set(got), key=str)
            problems.append(f'{where}: counties differ from json/counties.json (extra {extra[:3]}, missing {missing[:3]})')
        wrong = [cid for cid in truth if cid in got and (got[cid][0] != truth[cid][0] or (with_regions and got[cid][1] != truth[cid][1]))]
        if wrong:
            cid = wrong[0]
            problems.append(f'{where}: county {cid} has {got[cid][0]} and regions {got[cid][1]}, expected {truth[cid][0]} and '
                            f'{truth[cid][1]}' + (f' ({len(wrong)} counties differ)' if len(wrong) > 1 else ''))

    def keyed_pair(row, to_id, to_code):
        """A record's state pair through this format's parsers, or MISSING when either key is absent."""
        if 'state_id' not in row or 'state_code' not in row:
            return MISSING
        return (to_id(row['state_id']), to_code(row['state_code']))

    for fmt, parse in (('csv', _csv_rows), ('plist', lambda p: plistlib.loads(p.read_bytes()))):
        rows = _read(root, f'{fmt}/counties.{fmt}', parse, problems)
        if rows is not None:
            # a short CSV row gives None cells and a long one a None key: neither is the empty null encoding
            # a row with a missing or surplus cell is refused whole, before any of its fields is read
            compare(f'{fmt}/counties.{fmt}', [(_text_id(r.get('id'), nullable=False) if _flat_row_ok(r) else BAD,
                                               keyed_pair(r, _text_id, _text_code) if _flat_row_ok(r) else BAD, None) for r in rows],
                    with_regions=False)
        rel = _read(root, f'{fmt}/county_states.{fmt}', parse, problems)
        if rel is not None:
            got = Counter((_text_id(r.get('county_id'), nullable=False), _text_id(r.get('state_id'), nullable=False),
                           _text_code(r.get('state_code'))) if _flat_row_ok(r) else (BAD, BAD, BAD) for r in rel)
            need(got == Counter(triples), f'{fmt}/county_states.{fmt}: regions differ from json/counties.json')

    xml = _read(root, 'xml/counties.xml', lambda p: ET.parse(p).getroot(), problems)
    if xml is not None:
        rows = []
        for e in xml:
            cid, sid, code = (_xml_leaf(e, tag) for tag in ('id', 'state_id', 'state_code'))
            pair = MISSING if MISSING in (sid, code) else BAD if BAD in (sid, code) else (_text_id(sid), _text_code(code))
            rows.append((BAD if cid in (MISSING, BAD) else _text_id(cid, nullable=False), pair, _xml_regions(e)))
        compare('xml/counties.xml', rows)

    for rel, parse, key in (('yml/counties.yml', _yaml, 'id'), ('mongodb/counties.json', _records, '_id')):
        rows = _read(root, rel, parse, problems)
        if rows is not None:
            compare(rel, [(_native_id(r.get(key)), keyed_pair(r, _typed_id, _typed_code),
                           _list_value(r['states']) if 'states' in r else MISSING) for r in rows])
            if key == '_id':
                refs = {r.get('_id'): (r.get('state') or {}).get('$id') for r in rows}
                wrong = [cid for cid, ((sid, _), _) in truth.items() if refs.get(cid) != sid]
                need(not wrong, f'mongodb/counties.json: county {wrong[0]} has state reference {refs.get(wrong[0])}, expected {truth[wrong[0]][0][0]}' if wrong else '')

    def parquet(path):
        """The counties table of the Parquet export."""
        import pandas as pd
        return pd.read_parquet(path)

    def json_text(value):
        """A list stored as JSON text (Parquet, TOON): None for null, the regions, or INVALID."""
        if value is None:
            return None
        if not isinstance(value, str):
            return INVALID
        try:
            return _list_value(json.loads(value))
        except ValueError:
            return INVALID

    df = _read(root, 'parquet/counties.parquet', parquet, problems)
    if df is not None:
        missing = sorted({'id', 'state_id', 'state_code', 'states'} - set(df.columns))
        need(not missing, f"parquet: a column is missing ({', '.join(missing)})")
        if not missing:
            need(str(df['state_id'].dtype) == 'Int64', f"parquet: state_id is {df['state_id'].dtype}, not Int64")
            cols = df[['id', 'state_id', 'state_code', 'states']]
            rows = cols.astype(object).where(cols.notna(), None).to_dict('records')
            compare('parquet', [(_native_id(r['id']), (_typed_id(r['state_id']), _typed_code(r['state_code'])), json_text(r['states']))
                                for r in rows])

    toon = _read(root, 'toon/counties.toon', _toon, problems)
    if toon is not None:
        compare('toon/counties.toon', [(_native_id(r.get('id')), keyed_pair(r, _typed_id, _typed_code),
                                        json_text(r['states']) if 'states' in r else MISSING) for r in toon])

    sql = _read(root, 'sqlserver/counties.sql', lambda p: _sql_inserts(p.read_text(encoding='utf-8'), 'counties'), problems)
    if sql is not None:
        compare('sqlserver/counties.sql', [(_sql_id(r.get('id'), nullable=False), keyed_pair(r, _sql_id, _sql_code), None) for r in sql],
                with_regions=False)
    text = _read(root, 'sqlserver/county_states.sql', lambda p: p.read_text(encoding='utf-8'), problems)
    if text is not None:
        ddl = ('PRIMARY KEY (county_id, state_id)', 'FOREIGN KEY (county_id) REFERENCES world.counties(id) ON DELETE CASCADE',
               'FOREIGN KEY (state_id) REFERENCES world.states(id)')
        need(all(d in text for d in ddl), 'sqlserver/county_states.sql: the table needs its composite key and both foreign keys')
        got = Counter((_sql_id(r['county_id'], nullable=False), _sql_id(r['state_id'], nullable=False))
                      for r in _sql_inserts(text, 'county_states'))
        need(got == Counter((c, s) for c, s, _ in triples), 'sqlserver/county_states.sql: regions differ from json/counties.json')
    return problems


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: check_county_states_exports.py <county id>')
    found = main(int(sys.argv[1]))
    for p in found:
        print(f'[ERROR] {p}')
    if found:
        sys.exit(1)
    print(f'[INFO] county {sys.argv[1]} has no state and its regions, and every county its own state pair and regions, in json, '
          'csv, plist, xml, yaml, mongodb, parquet, toon and sqlserver')
