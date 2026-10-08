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

/** Run the real PR validator with local files and GitHub/core stubs. */
async function validateCountyEdit(records, status = 'modified') {
  const vm = require('node:vm');
  const previous = process.cwd();
  const root = fs.mkdtempSync(path.join(__dirname, '.county-test-'));
  const outputs = {};
  const code = fs.readFileSync(path.join(__dirname, 'validate-cross-reference.js'), 'utf8');
  try {
    for (const dir of ['counties', 'cities', 'countries', 'states']) {
      fs.mkdirSync(path.join(root, 'contributions', dir), { recursive: true });
    }
    const write = (file, data) => fs.writeFileSync(path.join(root, 'contributions', file), JSON.stringify(data));
    if (status !== 'removed') write('counties/US.json', records);
    write('cities/US.json', [{ ...city, county_id: 1 }]);
    write('countries/countries.json', [{ id: 233, iso2: 'US' }, { id: 75, iso2: 'FR' }]);
    write('states/states.json', [{ id: 1457, country_id: 233, state_code: 'LA' }, { id: 1427, country_id: 233, state_code: 'AL' }]);
    process.chdir(root);
    const fakeGithub = {
      getOctokit: () => ({ rest: { pulls: { listFiles: async () => ({ data: [
        { filename: 'contributions/counties/US.json', status },
      ] }) } } }),
      context: { payload: { pull_request: { number: 1 } }, repo: { owner: 'fixture', repo: 'fixture' } },
    };
    const fakeCore = {
      setOutput: (key, value) => { outputs[key] = value; },
      info() {}, error() {}, warning() {}, setFailed(message) { throw new Error(message); },
    };
    const sandbox = {
      require: (key) => key === '@actions/github' ? fakeGithub : key === '@actions/core' ? fakeCore :
        key === './utils' ? require('./utils') : require(key),
      process, module: { exports: {} },
    };
    await vm.runInNewContext(code + '\nrun()', sandbox);
    return JSON.parse(outputs.errors);
  } finally {
    process.chdir(previous);
    fs.rmSync(root, { recursive: true });
  }
}

test('county-only state edit checks unchanged city links', async () => {
  assert.match((await validateCountyEdit([{ ...county, state_id: 1427, state_code: 'AL' }])).join('\n'), /cities\/US.json.*belongs to state_id 1427/);
});

test('county-only country edit checks unchanged city links', async () => {
  assert.match((await validateCountyEdit([{ ...county, country_id: 75, country_code: 'FR' }])).join('\n'), /cities\/US.json.*belongs to country FR/);
});

test('county record removal checks unchanged city links', async () => {
  assert.match((await validateCountyEdit([])).join('\n'), /cities\/US.json.*county_id 1 does not exist/);
});

test('county file removal checks unchanged city links', async () => {
  assert.match((await validateCountyEdit([], 'removed')).join('\n'), /cities\/US.json.*county_id 1 does not exist/);
});

test('county parent_id must exist in county contributions', async () => {
  assert.match((await validateCountyEdit([{ ...county, parent_id: 999999 }])).join('\n'), /parent_id 999999 does not exist/);
});

test('county with parent_id requires an explicit id', async () => {
  assert.match((await validateCountyEdit([county, { ...county, id: undefined, parent_id: 1 }])).join('\n'), /parent_id.*explicit id/);
});

test('valid county parent and unchanged city links pass', async () => {
  assert.deepEqual(await validateCountyEdit([county, { ...county, id: 2, parent_id: 1 }]), []);
});
