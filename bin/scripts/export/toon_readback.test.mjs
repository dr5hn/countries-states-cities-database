// Reads the converter's real output back with the reference TOON reader and checks every value's type.
// Run: npm install --no-save @toon-format/toon@4.4.0 && node --test bin/scripts/export/toon_readback.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { decode } from '@toon-format/toon';

const converterDir = process.env.TOON_CONVERTER_DIR || path.dirname(fileURLToPath(import.meta.url));

/** TOON text the Python converter writes for these rows. */
function convert(rows) {
  const code = 'import sys; sys.path.insert(0, sys.argv[1]); from json_to_toon import json_to_toon; print(json_to_toon(sys.stdin.read()))';
  return execFileSync('python3', ['-c', code, converterDir], { input: JSON.stringify(rows), encoding: 'utf8' }).trimEnd();
}

test('a stateless city, a normal city, literal-looking strings and booleans read back exactly', () => {
  const rows = [
    { id: 1, name: 'Smara', state_id: null, state_code: null, note: 'null', flag: true },
    { id: 2, name: 'Baton Rouge', state_id: 1457, state_code: 'LA', note: 'true', flag: false },
  ];
  assert.deepEqual(decode(convert(rows)), rows);
});

test("a county's list of regions reads back as the same JSON text", () => {
  const states = [{ state_id: 4060, state_code: 'MWT' }, { state_id: 4061, state_code: 'WKO' }];
  const [row] = decode(convert([{ id: 9, state_id: null, states }]));
  assert.equal(row.state_id, null);
  assert.deepEqual(JSON.parse(row.states), states);
});

test('strings that look like numbers, colons, brackets and backslashes read back as the same strings', () => {
  const rows = [{ id: 4213, state_id: 2062, state_code: '1', latitude: '-38.86700000', code: '01', a: 'x:y', b: '[x]', c: '#1', d: 'a\\b', e: '' }];
  assert.deepEqual(decode(convert(rows)), rows);
});

test('every string is quoted exactly as the reference encoder quotes it (Unicode digits stay bare)', async () => {
  const { encode } = await import('@toon-format/toon');
  const strings = ['١', '१२', '１', '١.٢', '1', '01', '-38.86700000', '1e3', 'x:y', '[x]', '#1', 'a\\b', 'say "hi"', '', 'null',
    ' lead', 'tab\there', 'Taupō District', 'Ōamaru', 'São Paulo', '-', 'k=v|k2=v2'];
  for (const s of strings) {
    const rows = [{ id: 1, v: s }];
    const ours = convert(rows).split('\n')[1];
    const reference = encode(rows).split('\n')[1];
    assert.equal(ours, reference, JSON.stringify(s));
  }
});
