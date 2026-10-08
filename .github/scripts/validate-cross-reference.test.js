'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { loadCounties, validateCountyReference } = require('./validate-cross-reference');
const { validateRecord } = require('./utils');

const city = {
  name: 'Test city', state_id: 1457, state_code: 'LA',
  country_id: 233, country_code: 'US', latitude: '30.0', longitude: '-92.0',
};
const county = { id: 1, name: 'Acadia', state_id: 1457, country_id: 233, country_code: 'US' };
const counties = new Map([[county.id, county]]);

test('city county_id is optional and nullable', () => {
  for (const record of [city, { ...city, county_id: null }]) {
    assert.deepEqual(validateCountyReference(record, counties), []);
    assert.deepEqual(validateRecord(record, 'cities', 0), { errors: [], warnings: [] });
  }
});

test('accepts a positive county ID in the same state and country', () => {
  const record = { ...city, county_id: 1 };
  assert.deepEqual(validateCountyReference(record, counties), []);
  assert.deepEqual(validateRecord(record, 'cities', 0), { errors: [], warnings: [] });
});

test('rejects nonpositive, fractional, string and boolean county IDs', () => {
  for (const county_id of [0, -1, 1.5, '1', true]) {
    assert.match(validateCountyReference({ ...city, county_id }, counties)[0], /positive integer/);
  }
});

test('rejects a county missing from contributions', () => {
  assert.match(validateCountyReference({ ...city, county_id: 99 }, counties)[0], /does not exist/);
});

test('rejects a county in another state', () => {
  assert.match(validateCountyReference({ ...city, county_id: 1, state_id: 1427 }, counties)[0], /state_id/);
});

test('rejects mismatching country ID or code', () => {
  for (const record of [{ ...city, country_id: 75 }, { ...city, country_code: 'FR' }]) {
    assert.match(validateCountyReference({ ...record, county_id: 1 }, counties)[0], /country/);
  }
});

test('loads county contributions across countries and skips unassigned IDs', () => {
  // Keep all test files under this worktree and restore cwd even on failure.
  const previous = process.cwd();
  const root = fs.mkdtempSync(path.join(__dirname, '.county-test-'));
  try {
    process.chdir(root);
    assert.equal(loadCounties().size, 0);
    fs.mkdirSync('contributions/counties', { recursive: true });
    fs.writeFileSync('contributions/counties/US.json', JSON.stringify([county, { name: 'New county' }]));
    fs.writeFileSync('contributions/counties/FR.json', JSON.stringify([{ ...county, id: 2, country_code: 'FR' }]));
    assert.equal(loadCounties().size, 2);
    fs.writeFileSync('contributions/counties/FR.json', JSON.stringify([county]));
    assert.throws(loadCounties, /Duplicate county id/);
    fs.writeFileSync('contributions/counties/FR.json', '{');
    assert.throws(loadCounties, /Cannot load counties/);
  } finally {
    process.chdir(previous);
    fs.rmSync(root, { recursive: true });
  }
});
