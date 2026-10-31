#!/usr/bin/env python3
"""Check counties of several regions in every export format, after import and export (v5, decision B6).

Run from the repository root after the exports:  python3 bin/db/tests/check_county_states_exports.py <county id>
The expectations come from the source of truth, as the importer reads it: contributions/counties/*.json (each county's
id, own state pair, and regions) and contributions/states/states.json (a region's code is its state's iso2, as the
export joins it). The given county must have a null state pair and two or more distinct regions there. Every county,
that one and all others, must then have the same state pair and the same regions in every format, json/counties.json
included: the states list in JSON, YAML, XML, MongoDB, Parquet and TOON (read with the reference reader), the
county_states rows in CSV, PLIST and SQL Server, and the state columns of each counties file, SQL Server's included.
So a wrong ExportJson, which every derived format would repeat, still fails. Counts are never used in place of
equality. Exits 1 with the problems, or 0 after printing what it checked.

Each file is read by a strict loader before anything is compared, and a structural fault fails the whole file: a
repeated key, header or column; a wrong envelope or root (a null root fails the file, it is never skipped); stray
XML or property-list content; CSV quoting a lenient reader would repair; non-canonical TOON numbers; invalid UTF-8;
a Parquet column stored with the wrong physical type. Ids must be positive integers of the format's own integer type
(or canonical integer text in text formats) and nulls must use the format's own null encoding.

SQL Server: this is not a general SQL validator. It accepts exactly the statements this repository's exporter
(bin/Commands/ExportSqlServer.php) writes for world.counties and world.county_states, in the exporter's order: the
DROP and CREATE scaffold (CREATE checked declaration by declaration, none empty), counties' constraint and identity
switches around the inserts (naming the parent constraint CREATE declares), and INSERT statements of at most 1,000
rows (SQL Server's limit; the exporter writes 900) into declared columns, parsed completely (one value per column,
exact separators, nothing left over). Column names written [x] or "x" are the same column as x. Comments are removed
first, so a commented-out insert adds no rows. Any other statement is refused, not interpreted.

Scope: the checker guards the exporters' own output against regressions: a wrong, missing, repeated or reordered
value, record or statement. It is not a hardened parser for arbitrary hand-edited files; it fails closed on the
malformations an exporter bug could plausibly produce, and on the malformations reviews have reported.
"""
import csv
import io
import json
import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET  # parses the export just generated in this run, not outside input
from collections import Counter
from pathlib import Path

from check_null_state_exports import _read

TOON_READER_DIR = Path(__file__).resolve().parents[2] / 'scripts' / 'export'   # where CI installs @toon-format/toon
TOON_DECODE = ("const { decode } = await import('@toon-format/toon'); const fs = await import('node:fs'); "
               "const text = new TextDecoder('utf-8', { fatal: true }).decode(fs.readFileSync(process.argv[1])); "
               "process.stdout.write(JSON.stringify(decode(text)))")

MISSING, INVALID, BAD = '(missing)', '(invalid list)', '(invalid value)'   # never equal to a real id, code, pair or list
POSITIVE_INT_TEXT = re.compile(r'[1-9][0-9]*')
SAFE_INT = 2 ** 53 - 1   # the largest integer the JavaScript TOON reader keeps exact
SQL_NUMBER = re.compile(r'-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?')
# The CREATE TABLE declarations ExportSqlServer.php writes: all of county_states', and the compared ones of counties
COUNTY_STATES_DDL = {'county_id INT NOT NULL', 'state_id INT NOT NULL',
                     'CONSTRAINT PK_county_states PRIMARY KEY (county_id, state_id)',
                     'CONSTRAINT FK_county_states_counties FOREIGN KEY (county_id) REFERENCES world.counties(id) ON DELETE CASCADE',
                     'CONSTRAINT FK_county_states_states FOREIGN KEY (state_id) REFERENCES world.states(id)'}
COUNTIES_DDL = {'id INT IDENTITY(1,1) PRIMARY KEY', 'state_id INT NULL', 'state_code NVARCHAR(255) NULL',
                'CONSTRAINT FK_counties_parent FOREIGN KEY (parent_id) REFERENCES world.counties(id)',   # the switches name it
                'CONSTRAINT FK_counties_states FOREIGN KEY (state_id) REFERENCES world.states(id)',
                'CONSTRAINT CK_counties_state_pair CHECK ((state_id IS NULL AND state_code IS NULL) OR '
                '(state_id IS NOT NULL AND state_code IS NOT NULL))'}
# The exporter's statement order per file (bin/Commands/ExportSqlServer.php execute())
SQL_MAX_ROWS = 1000   # rows one INSERT ... VALUES may carry in SQL Server (error 10738); the exporter writes 900
SQL_ORDER = {'counties': re.compile(r'drop create nocheck identity_on( insert)* identity_off check'),
             'county_states': re.compile(r'drop create( insert)*')}


# --- values -------------------------------------------------------------------------------------------------------

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


def _typed_id(v):
    """A nullable id from a typed format: null, or a positive int (never a boolean or a fraction)."""
    return None if v is None else _native_id(v)


def _typed_code(v):
    """A nullable state code from a typed format: null, or a non-empty string."""
    return None if v is None else v if isinstance(v, str) and v else BAD


def _regions(listed):
    """A states list as a sorted tuple of (state_id, state_code), or None when it is not a list of exact pairs with
    integer-typed positive ids and non-empty codes (no coercion: 4060.75, "4060" and true are not 4060)."""
    if not isinstance(listed, list) or not all(
            isinstance(r, dict) and set(r) == {'state_id', 'state_code'} and _native_id(r['state_id']) is not BAD
            and isinstance(r['state_code'], str) and r['state_code'] for r in listed):
        return None
    return tuple(sorted((r['state_id'], r['state_code']) for r in listed))


def _list_value(listed):
    """What a format holds for one county's list: None for no list, the regions tuple, or INVALID."""
    if listed is None:
        return None
    regions = _regions(listed)
    return INVALID if regions is None else regions


def _flat_row_ok(row):
    """Whether a CSV or PLIST row is whole: no surplus-cell key and no missing (None) cell anywhere."""
    return None not in row and all(v is not None for v in row.values())


def _blank(text):
    """Whether XML text or a tail is only whitespace (indentation)."""
    return not (text or '').strip()


# --- strict loaders: each returns records or raises, so _read reports the whole file ---------------------------------

def _utf8(path):
    """The file's text; invalid UTF-8 is an error, never replaced."""
    return Path(path).read_bytes().decode('utf-8')


def _no_duplicates(pairs):
    """A JSON object from its pairs; a repeated key is an error, not an overwrite."""
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f'duplicate key {key!r}')
        out[key] = value
    return out


def _reject_constant(name):
    """NaN and Infinity are not JSON."""
    raise ValueError(f'non-standard JSON constant {name}')


def _json(text):
    """Strict JSON: no repeated key in any object, no NaN or Infinity."""
    return json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)


def _record_list(doc, what):
    """doc as a list of record dicts; null, another root or a non-object row is an error."""
    if not isinstance(doc, list) or not all(isinstance(r, dict) for r in doc):
        raise ValueError(f'{what}: expected an array of records, got {type(doc).__name__}')
    return doc


def _load_json(path):
    """A JSON array of records (json/counties.json, mongodb/counties.json)."""
    return _record_list(_json(_utf8(path)), 'JSON')


def _load_yaml(path):
    """The exporter's YAML envelope {county: [records]}, with no repeated mapping key at any depth."""
    import yaml

    class Strict(getattr(yaml, 'CSafeLoader', yaml.SafeLoader)):
        """The safe loader, refusing a repeated mapping key instead of keeping the last value."""

        def construct_mapping(self, node, deep=False):
            """Check the keys of one mapping, then build it."""
            seen = set()
            for key_node, _ in node.value:
                key = self.construct_object(key_node, deep=True)
                if key in seen:
                    raise ValueError(f'YAML: duplicate key {key!r} at line {key_node.start_mark.line + 1}')
                seen.add(key)
            return super().construct_mapping(node, deep)

    doc = yaml.load(_utf8(path), Loader=Strict)
    if not isinstance(doc, dict) or list(doc) != ['county']:
        raise ValueError(f'YAML: expected the envelope {{county: [...]}}, got '
                         f'{list(doc) if isinstance(doc, dict) else type(doc).__name__}')
    return _record_list(doc['county'], 'YAML county')


def _csv_lexical(text):
    """Refuse CSV that a lenient reader would repair: a quote inside an unquoted cell, text after a closing quote, or a
    quoted cell still open at the end. Doubled quotes inside a quoted cell and embedded newlines stay legal."""
    start, plain, quoted, closing = range(4)
    state, line = start, 1
    for ch in text:
        if state == start:
            state = quoted if ch == '"' else start if ch in ',\r\n' else plain
        elif state == plain:
            if ch == '"':
                raise ValueError(f'CSV line {line}: a quote inside an unquoted cell')
            if ch in ',\r\n':
                state = start
        elif state == quoted:
            if ch == '"':
                state = closing
        elif ch == '"':
            state = quoted   # a doubled quote inside a quoted cell
        elif ch in ',\r\n':
            state = start
        else:
            raise ValueError(f'CSV line {line}: text after a closing quote')
        if ch == '\n':
            line += 1
    if state == quoted:
        raise ValueError('CSV: a quoted cell is not closed')


def _load_csv(path):
    """Rows of a CSV export as dicts by header name, after the lexical check, read with strict=True. Header names must
    be unique. A row with fewer or more cells than the header is kept but marked with a None key (as csv.DictReader
    marks surplus cells), so _flat_row_ok() refuses it before any field is read."""
    text = _utf8(path)
    _csv_lexical(text)
    rows = list(csv.reader(io.StringIO(text, newline=''), strict=True))
    if not rows:
        raise ValueError('CSV: no header')
    header = rows[0]
    repeated = sorted(name for name, n in Counter(header).items() if n > 1)
    if repeated:
        raise ValueError(f'CSV: repeated column {repeated}')
    out = []
    for row in rows[1:]:
        d = dict(zip(header, row))
        if len(row) != len(header):
            d[None] = f'{len(row)} cells for {len(header)} columns'
        out.append(d)
    return out


class _NoDuplicateDict(dict):
    """A property-list dict that refuses a repeated key instead of keeping the last value."""

    def __setitem__(self, key, value):
        """Set a key once."""
        if key in self:
            raise ValueError(f'PLIST: duplicate key {key!r}')
        super().__setitem__(key, value)


def _plist_xml_grammar(data):
    """The exporter's XML property list: one <plist> holding exactly one <array> of <dict>s whose children alternate
    <key> and <string> leaves. Any other element, attribute (but plist's version), nested tag or non-whitespace text is
    an error, so plistlib never gets to drop it."""
    root = ET.fromstring(data)
    if root.tag != 'plist' or set(root.attrib) - {'version'} or not _blank(root.text) or len(root) != 1:
        raise ValueError('PLIST: expected <plist> holding one <array>')
    array = root[0]
    if array.tag != 'array' or array.attrib or not _blank(array.text) or not _blank(array.tail):
        raise ValueError('PLIST: expected one <array> of records')
    for record in array:
        if record.tag != 'dict' or record.attrib or not _blank(record.text) or not _blank(record.tail):
            raise ValueError(f'PLIST: <{record.tag}> where a record <dict> belongs')
        children = list(record)
        if len(children) % 2:
            raise ValueError('PLIST: a record has a key without a value')
        for i, child in enumerate(children):
            want = 'key' if i % 2 == 0 else 'string'
            if child.tag != want or len(child) or child.attrib or not _blank(child.tail):
                raise ValueError(f'PLIST: <{child.tag}> where a leaf <{want}> belongs')


def _load_plist(path):
    """A property list of records: XML (grammar-checked first) or binary, with no repeated key."""
    data = Path(path).read_bytes()
    if data.startswith(b'bplist00'):
        doc = plistlib.loads(data, fmt=plistlib.FMT_BINARY, dict_type=_NoDuplicateDict)
    else:
        _plist_xml_grammar(data)
        doc = plistlib.loads(data, fmt=plistlib.FMT_XML, dict_type=_NoDuplicateDict)
    return _record_list(doc, 'PLIST')


def _load_xml(path):
    """The county elements of the XML export: root <counties> holding only <county> records, without attributes and
    with only whitespace between elements, down to each county's own fields."""
    root = ET.parse(path).getroot()
    if root.tag != 'counties' or root.attrib or not _blank(root.text):
        raise ValueError(f'XML: expected the root <counties>, got <{root.tag}>')
    for county in root:
        if county.tag != 'county' or county.attrib or not _blank(county.text) or not _blank(county.tail):
            raise ValueError(f'XML: <{county.tag}> where a <county> record belongs, or text or attributes on it')
        for field in county:
            if not _blank(field.tail):
                raise ValueError(f'XML: text after <{field.tag}> in a county')
    return list(root)


def _xml_leaf(parent, tag):
    """The text of exactly one leaf element <tag> under parent ('' when empty): MISSING when absent, BAD when repeated,
    nested or carrying attributes (such as xsi:nil). Every XML scalar the checker reads goes through here."""
    found = parent.findall(tag)
    if not found:
        return MISSING
    if len(found) > 1 or len(found[0]) or found[0].attrib:
        return BAD
    return found[0].text or ''


def _xml_regions(county):
    """An XML county's list: MISSING without a states element, None for one empty <states/> without attributes, the
    regions when every states element holds exactly one leaf state_id (positive integer text) and one leaf state_code
    and nothing else, INVALID for anything else."""
    listed = county.findall('states')
    if not listed:
        return MISSING
    if any(el.attrib for el in listed):
        return INVALID
    if len(listed) == 1 and len(listed[0]) == 0 and _blank(listed[0].text):
        return None
    pairs = []
    for el in listed:
        children = list(el)
        if not _blank(el.text) or sorted(c.tag for c in children) != ['state_code', 'state_id'] \
                or any(not _blank(c.tail) for c in children):
            return INVALID
        sid_text, code = _xml_leaf(el, 'state_id'), _xml_leaf(el, 'state_code')
        sid = BAD if sid_text in (MISSING, BAD) else _text_id(sid_text, nullable=False)
        if sid is BAD or code in (MISSING, BAD) or not code:
            return INVALID
        pairs.append({'state_id': sid, 'state_code': code})
    return _list_value(pairs)


def _toon_cells(row):
    """The raw cells of one tabular TOON row, split on commas outside quoted cells (backslash escapes inside)."""
    cells, cell, quoted, escaped = [], [], False, False
    for ch in row:
        if quoted:
            cell.append(ch)
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
            cell.append(ch)
        elif ch == ',':
            cells.append(''.join(cell))
            cell = []
        else:
            cell.append(ch)
    cells.append(''.join(cell))
    return cells


def _load_toon(path):
    """The rows of a TOON export. Before the reference reader (@toon-format/toon under Node, which decodes the whole
    document with fatal UTF-8) turns numbers into JavaScript numbers, the raw id and state_id cells must be canonical
    positive integers within JavaScript's exact range (state_id may be the literal null), so 9.0000000000000001 is
    never rounded into 9."""
    text = _utf8(path)
    lines = text.split('\n')
    header = re.fullmatch(r'\[(\d+)\]\{([^}]*)\}:', lines[0])
    if header is None:
        raise ValueError('TOON: expected a table of records, [N]{fields}:')
    fields = []
    for name in _toon_cells(header.group(2)):   # quoted or bare, around spaces: decoded as the reference reader does
        name = name.strip()
        fields.append(json.loads(name) if name.startswith('"') else name)
    for name in ('id', 'state_id'):
        if fields.count(name) != 1:
            raise ValueError(f'TOON: the header names {name} {fields.count(name)} times')
    for n, line in enumerate(lines[1:], 2):
        cells = _toon_cells(line[2:]) if line.startswith('  ') else None
        if cells is None or len(cells) != len(fields):
            continue   # the reference reader refuses a malformed row
        raw = dict(zip(fields, cells))
        for field, nullable in (('id', False), ('state_id', True)):
            value = raw[field].strip()
            if nullable and value == 'null':
                continue
            if not POSITIVE_INT_TEXT.fullmatch(value) or int(value) > SAFE_INT:
                raise ValueError(f'TOON line {n}: {field} {value!r} is not a canonical positive integer')
    run = subprocess.run(['node', '--input-type=module', '-e', TOON_DECODE, str(Path(path).resolve())], cwd=TOON_READER_DIR,
                         capture_output=True, text=True, timeout=600)
    if run.returncode != 0:
        raise ValueError(f'the TOON reference reader failed: {run.stderr.strip()[-300:]}')
    return _record_list(json.loads(run.stdout), 'TOON')


def _load_parquet(path):
    """The compared columns of the Parquet counties table, read from their physical Arrow storage (never through
    pandas' metadata-driven casts): unique column names, physical and as pandas would name them; integer storage for
    id and state_id; string storage (or null storage when every value is null) for state_code and states."""
    import pyarrow.parquet as pq
    import pyarrow.types as pat
    table = pq.read_table(path)
    names = table.column_names
    if len(set(names)) != len(names):
        raise ValueError(f'Parquet: repeated column in {names}')
    meta = table.schema.metadata or {}
    if b'pandas' in meta:
        columns = json.loads(meta[b'pandas']).get('columns', [])
        named = [c.get('name') for c in columns if isinstance(c.get('name'), str)]
        aliased = [c for c in columns if isinstance(c.get('name'), str) and c.get('name') != c.get('field_name')]
        if len(set(named)) != len(named) or aliased:
            raise ValueError('Parquet: pandas metadata gives two columns one name, or renames a column')
    text = lambda t: pat.is_string(t) or pat.is_large_string(t) or pat.is_null(t)   # an all-null text column may be null-typed
    wanted = {'id': pat.is_integer, 'state_id': pat.is_integer, 'state_code': text, 'states': text}
    missing = sorted(set(wanted) - set(names))
    if missing:
        raise ValueError(f"Parquet: a column is missing ({', '.join(missing)})")
    for name, ok in wanted.items():
        if not ok(table.schema.field(name).type):
            raise ValueError(f'Parquet: {name} is stored as {table.schema.field(name).type}')
    columns = {name: table.column(name).to_pylist() for name in wanted}
    return [dict(zip(wanted, values)) for values in zip(*columns.values())]


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


def _sql_statements(text):
    """The comment-free statements of a SQL Server script, split on semicolons outside quoted literals. An unterminated
    comment or literal, or text after the last semicolon, is an error."""
    out, cur, i, n = [], [], 0, len(text)
    while i < n:
        if text.startswith('--', i):
            j = text.find('\n', i)
            i = n if j < 0 else j
        elif text.startswith('/*', i):
            j = text.find('*/', i + 2)
            if j < 0:
                raise ValueError('SQL: a block comment is not closed')
            cur.append(' ')
            i = j + 2
        elif text[i] == "'":
            j = i + 1
            while True:
                if j >= n:
                    raise ValueError('SQL: a quoted literal is not closed')
                if text.startswith("''", j):
                    j += 2
                elif text[j] == "'":
                    break
                else:
                    j += 1
            cur.append(text[i:j + 1])
            i = j + 1
        elif text[i] == ';':
            out.append(''.join(cur).strip())
            cur = []
            i += 1
        else:
            cur.append(text[i])
            i += 1
    if ''.join(cur).strip():
        raise ValueError(f"SQL: text after the last statement: {''.join(cur).strip()[:60]!r}")
    return [s for s in out if s]


def _sql_rows(values, ncols):
    """Every row of an INSERT's VALUES list, consumed completely: '(v, v),\\n(v, v)', each value NULL, N'text' or a
    number, exactly ncols per row, commas between values and between rows, nothing left over."""
    rows, i, n = [], 0, len(values)

    def skip(i):
        """Past whitespace."""
        while i < n and values[i] in ' \t\r\n':
            i += 1
        return i

    i = skip(0)
    while True:
        if i >= n or values[i] != '(':
            raise ValueError(f'SQL: expected a row at {values[i:i + 30]!r}')
        i += 1
        row = []
        while True:
            i = skip(i)
            if values.startswith('NULL', i):
                row.append(None)
                i += 4
            elif values.startswith("N'", i):
                j = i + 2
                while True:
                    if j >= n:
                        raise ValueError('SQL: a quoted value is not closed')
                    if values.startswith("''", j):
                        j += 2
                    elif values[j] == "'":
                        break
                    else:
                        j += 1
                row.append(SqlText(values[i + 2:j].replace("''", "'")))
                i = j + 1
            else:
                m = SQL_NUMBER.match(values, i)
                if not m:
                    raise ValueError(f'SQL: expected a value at {values[i:i + 30]!r}')
                row.append(m.group())
                i = m.end()
            i = skip(i)
            if i < n and values[i] == ',':
                i += 1
                continue
            if i < n and values[i] == ')':
                i += 1
                break
            raise ValueError(f'SQL: expected , or ) at {values[i:i + 30]!r}')
        if len(row) != ncols:
            raise ValueError(f'SQL: a row has {len(row)} values for {ncols} columns')
        rows.append(row)
        i = skip(i)
        if i >= n:
            return rows
        if values[i] != ',':
            raise ValueError(f'SQL: expected , between rows at {values[i:i + 30]!r}')
        i = skip(i + 1)


def _sql_name(name):
    """A column name as SQL Server resolves it: [x] and "x" are x, and names are compared without case."""
    name = name.strip()
    if len(name) > 1 and (name[0], name[-1]) in (('[', ']'), ('"', '"')):
        name = name[1:-1]
    return name.lower()


def _sql_declarations(create, table):
    """The declarations of a whitespace-normalised 'CREATE TABLE world.<table> (...)', split on commas outside
    parentheses and quoted literals. Text after the closing parenthesis, or a column or constraint declared twice, is
    an error."""
    body = create[len(f'CREATE TABLE world.{table} ('):]
    decls, cur, depth, i = [], [], 1, 0
    while i < len(body):
        ch = body[i]
        if ch == "'":
            j = i + 1
            while j < len(body) and not (body[j] == "'" and not body.startswith("''", j)):
                j += 2 if body.startswith("''", j) else 1
            cur.append(body[i:j + 1])
            i = j + 1
            continue
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                decls.append(''.join(cur).strip())
                if body[i + 1:].strip():
                    raise ValueError(f'SQL: text after CREATE TABLE world.{table} (...): {body[i + 1:].strip()[:40]!r}')
                break
        elif ch == ',' and depth == 1:
            decls.append(''.join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(ch)
        i += 1
    else:
        raise ValueError(f'SQL: CREATE TABLE world.{table} is not closed')
    if '' in decls:
        raise ValueError(f'SQL: CREATE TABLE world.{table} has an empty declaration (two commas, or one before the closing parenthesis)')
    names = [d.split()[1] if d.startswith('CONSTRAINT ') else d.split()[0] for d in decls]
    if len(set(map(_sql_name, names))) != len(names):
        raise ValueError(f'SQL: a column or constraint of world.{table} is declared twice')
    return set(decls)


def _load_sql(path, table):
    """The rows a SQL Server export inserts into world.<table>, and its CREATE TABLE declarations. Only the statements the
    exporter writes for that table, in its order, are accepted (see the module docstring); anything else is an error."""
    norm = lambda s: re.sub(r'\s+', ' ', s).strip()
    kinds_of = {f"IF OBJECT_ID('world.{table}', 'U') IS NOT NULL DROP TABLE world.{table}": 'drop',
                f'SET IDENTITY_INSERT world.{table} ON': 'identity_on', f'SET IDENTITY_INSERT world.{table} OFF': 'identity_off',
                f'ALTER TABLE world.{table} NOCHECK CONSTRAINT FK_{table}_parent': 'nocheck',
                f'ALTER TABLE world.{table} WITH CHECK CHECK CONSTRAINT FK_{table}_parent': 'check'}
    insert = re.compile(rf'INSERT\s+INTO\s+world\.{table}\s*\(([^)]*)\)\s*VALUES\s(.*)\Z', re.S)
    kinds, decls, rows, inserted = [], None, [], set()
    for statement in _sql_statements(_utf8(path)):
        n = norm(statement)
        if n in kinds_of:
            kinds.append(kinds_of[n])
            continue
        if n.startswith(f'CREATE TABLE world.{table} ('):
            kinds.append('create')
            decls = _sql_declarations(n, table)
            continue
        m = insert.match(statement)
        if not m:
            raise ValueError(f'SQL: a statement the exporter does not write: {n[:80]!r}')
        kinds.append('insert')
        columns = [_sql_name(c) for c in m.group(1).split(',')]
        if len(set(columns)) != len(columns):
            raise ValueError(f'SQL: a column is named twice in {m.group(1).strip()[:80]!r}')
        batch = _sql_rows(m.group(2), len(columns))
        if len(batch) > SQL_MAX_ROWS:
            raise ValueError(f'SQL: one INSERT carries {len(batch)} rows; SQL Server takes at most {SQL_MAX_ROWS}')
        inserted |= set(columns)
        rows += [dict(zip(columns, values)) for values in batch]
    if not SQL_ORDER[table].fullmatch(' '.join(kinds)):
        raise ValueError(f"SQL: statements {' '.join(kinds)!r} are not the exporter's order for world.{table}")
    declared = {_sql_name(d.split()[0]) for d in decls if not d.startswith('CONSTRAINT ')}
    undeclared = sorted(inserted - declared)
    if undeclared:
        raise ValueError(f'SQL: INSERT into world.{table} names columns CREATE does not declare: {undeclared}')
    constraints = {_sql_name(d.split()[1]) for d in decls if d.startswith('CONSTRAINT ')}
    if {'nocheck', 'check'} & set(kinds) and _sql_name(f'FK_{table}_parent') not in constraints:
        raise ValueError(f'SQL: the constraint switches name FK_{table}_parent, which CREATE does not declare')
    return rows, decls


# --- the source of truth ------------------------------------------------------------------------------------------

def _expected(root):
    """(expectations, problems) from contributions/ as the importer reads it: county id -> ((state_id, state_code),
    regions or None). A county of several regions has a null pair and two or more distinct regions, each listed with
    its state's iso2 from states.json (the code the export joins); every other county has its own complete pair and no
    list. A county without a positive integer id (run the import and sync first), a repeated id, or another shape is
    reported, never used as an expectation."""
    problems, truth = [], {}
    try:
        states = _record_list(_json(_utf8(Path(root, 'contributions/states/states.json'))), 'states.json')
        files = sorted(Path(root, 'contributions/counties').glob('*.json'))
    except (OSError, ValueError) as e:
        return {}, [f'contributions/states/states.json: cannot be read: {e}']
    iso2 = {s.get('id'): s.get('iso2') for s in states}
    if not files:
        problems.append('contributions/counties: no county files')
    for f in files:
        rel = f'contributions/counties/{f.name}'
        try:
            counties = _record_list(_json(_utf8(f)), rel)
        except (OSError, ValueError) as e:
            problems.append(f'{rel}: cannot be read: {e}')
            continue
        for c in counties:
            cid = c.get('id')
            if type(cid) is not int or cid <= 0:
                problems.append(f'{rel}: county {c.get("name")!r} has no positive integer id; run the import and sync first')
                continue
            if cid in truth:
                problems.append(f'{rel}: county id {cid} is duplicated')
                continue
            if 'state_id' not in c or 'state_code' not in c:
                problems.append(f'{rel}: county {cid} lacks state_id or state_code')
                continue
            sid, code, listed = c['state_id'], c['state_code'], c.get('states')
            if sid is not None or code is not None:
                if _native_id(sid) is BAD or not isinstance(code, str) or not code or listed is not None:
                    problems.append(f'{rel}: county {cid} needs its own complete state pair and no states list')
                    continue
                truth[cid] = ((sid, code), None)
                continue
            regions = _regions(listed)
            if not regions or len(regions) < 2 or len({r for r, _ in regions}) != len(regions):
                problems.append(f'{rel}: county {cid} has a null state pair, so it needs two or more distinct regions')
                continue
            if any(iso2.get(r) != rcode for r, rcode in regions):
                problems.append(f"{rel}: county {cid} lists a region whose code is not its state's iso2 in states.json")
                continue
            truth[cid] = ((None, None), regions)
    return truth, problems


def main(county_id, root='.'):
    """Check each format under root against json/counties.json; return the problems found."""
    problems = []
    need = lambda ok, msg: ok or problems.append(msg)

    truth, source = _expected(root)
    problems += source
    if source:
        return problems
    pair, regions = truth.get(county_id, ((0, 0), None))
    if pair != (None, None) or not regions:
        problems.append(f'contributions/counties: county {county_id} needs a null state pair and two or more distinct regions')
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

    # json/counties.json is one format among the others: it must carry states explicitly (null on a one-state county)
    exported = _read(root, 'json/counties.json', _load_json, problems)
    if exported is not None:
        compare('json/counties.json', [(_native_id(r.get('id')), keyed_pair(r, _typed_id, _typed_code),
                                        _list_value(r['states']) if 'states' in r else MISSING) for r in exported])

    for fmt, load in (('csv', _load_csv), ('plist', _load_plist)):
        rows = _read(root, f'{fmt}/counties.{fmt}', load, problems)
        if rows is not None:
            # a row with a missing or surplus cell is refused whole, before any of its fields is read
            compare(f'{fmt}/counties.{fmt}', [(_text_id(r.get('id'), nullable=False) if _flat_row_ok(r) else BAD,
                                               keyed_pair(r, _text_id, _text_code) if _flat_row_ok(r) else BAD, None) for r in rows],
                    with_regions=False)
        rel = _read(root, f'{fmt}/county_states.{fmt}', load, problems)
        if rel is not None:
            got = Counter((_text_id(r.get('county_id'), nullable=False), _text_id(r.get('state_id'), nullable=False),
                           _text_code(r.get('state_code'))) if _flat_row_ok(r) else (BAD, BAD, BAD) for r in rel)
            need(got == Counter(triples), f'{fmt}/county_states.{fmt}: regions differ from json/counties.json')

    xml = _read(root, 'xml/counties.xml', _load_xml, problems)
    if xml is not None:
        rows = []
        for e in xml:
            cid, sid, code = (_xml_leaf(e, tag) for tag in ('id', 'state_id', 'state_code'))
            pair = MISSING if MISSING in (sid, code) else BAD if BAD in (sid, code) else (_text_id(sid), _text_code(code))
            rows.append((BAD if cid in (MISSING, BAD) else _text_id(cid, nullable=False), pair, _xml_regions(e)))
        compare('xml/counties.xml', rows)

    yml = _read(root, 'yml/counties.yml', _load_yaml, problems)
    if yml is not None:
        compare('yml/counties.yml', [(_native_id(r.get('id')), keyed_pair(r, _typed_id, _typed_code),
                                      _list_value(r['states']) if 'states' in r else MISSING) for r in yml])

    mongo = _read(root, 'mongodb/counties.json', _load_json, problems)
    if mongo is not None:
        compare('mongodb/counties.json', [(_native_id(r.get('_id')), keyed_pair(r, _typed_id, _typed_code),
                                           _list_value(r['states']) if 'states' in r else MISSING) for r in mongo])
        # the state reference: absent without an own state, else exactly {"$ref": "states", "$id": <int state_id>}
        refs = {_native_id(r.get('_id')): r.get('state', MISSING) for r in mongo}
        wrong = [cid for cid, ((sid, _), _) in truth.items() if cid in refs and not (
            refs[cid] is MISSING if sid is None else
            isinstance(refs[cid], dict) and set(refs[cid]) == {'$ref', '$id'} and refs[cid]['$ref'] == 'states'
            and type(refs[cid]['$id']) is int and refs[cid]['$id'] == sid)]
        need(not wrong, f'mongodb/counties.json: county {wrong[0]} has state reference {refs[wrong[0]]!r}, expected '
             f'{"none" if truth[wrong[0]][0][0] is None else {"$ref": "states", "$id": truth[wrong[0]][0][0]}}' if wrong else '')

    def json_text(value):
        """A list stored as JSON text (Parquet, TOON): None for null, the regions, or INVALID (repeated keys included)."""
        if value is None:
            return None
        if not isinstance(value, str):
            return INVALID
        try:
            decoded = _json(value)
        except ValueError:
            return INVALID
        return _list_value(decoded) if isinstance(decoded, list) else INVALID   # the text "null" is not a null list

    parquet = _read(root, 'parquet/counties.parquet', _load_parquet, problems)
    if parquet is not None:
        compare('parquet', [(_native_id(r['id']), (_typed_id(r['state_id']), _typed_code(r['state_code'])), json_text(r['states']))
                            for r in parquet])

    toon = _read(root, 'toon/counties.toon', _load_toon, problems)
    if toon is not None:
        compare('toon/counties.toon', [(_native_id(r.get('id')), keyed_pair(r, _typed_id, _typed_code),
                                        json_text(r['states']) if 'states' in r else MISSING) for r in toon])

    sql = _read(root, 'sqlserver/counties.sql', lambda p: _load_sql(p, 'counties'), problems)
    if sql is not None:
        rows, ddl = sql
        need(COUNTIES_DDL <= ddl, 'sqlserver/counties.sql: the counties table lacks its id key, nullable state pair, state key or pair check')
        compare('sqlserver/counties.sql', [(_sql_id(r.get('id'), nullable=False), keyed_pair(r, _sql_id, _sql_code), None) for r in rows],
                with_regions=False)
    rel = _read(root, 'sqlserver/county_states.sql', lambda p: _load_sql(p, 'county_states'), problems)
    if rel is not None:
        rows, ddl = rel
        need(ddl == COUNTY_STATES_DDL, 'sqlserver/county_states.sql: the table is not the exporter\'s (two columns, composite key, both foreign keys)')
        got = Counter((_sql_id(r.get('county_id'), nullable=False), _sql_id(r.get('state_id'), nullable=False)) for r in rows)
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
