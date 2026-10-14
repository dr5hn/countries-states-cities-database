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
