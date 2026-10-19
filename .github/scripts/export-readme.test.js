'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

test('export workflow refreshes county total in the current README format', () => {
  const root = path.resolve(__dirname, '../..');
  const original = fs.readFileSync(path.join(root, 'README.md'), 'utf8');
  const workflow = fs.readFileSync(path.join(root, '.github/workflows/export.yml'), 'utf8');
  const step = workflow.split('      - name: Update README.md\n')[1].split('\n      - name:')[0];
  const commands = step.split('        run: |\n')[1].replace(/^          /gm, '');
  const value = (label) => original.match(new RegExp(`${label} : (.*) <br>`))[1];
  const temp = fs.mkdtempSync(path.join(__dirname, '.readme-test-'));
  try {
    fs.writeFileSync(path.join(temp, 'README.md'), original);
    // BSD sed needs an explicit empty backup suffix; the workflow uses GNU sed.
    const script = commands.replaceAll('sed -i ', process.platform === 'darwin' ? "sed -i '' " : 'sed -i ');
    execFileSync('sh', ['-c', script], { cwd: temp, env: {
      ...process.env, county_count: '3414',
      region_count: value('Total Regions'), subregion_count: value('Total Sub Regions'),
      country_count: value('Total Countries'), state_count: value('Total States/Regions/Municipalities'),
      city_count: value('Total Cities/Towns/Districts'),
      postcode_count: value('Total Postcodes').split(' ')[0],
      postcode_country_count: value('Total Postcodes').match(/\(([0-9]+) countries\)/)[1],
      current_date: original.match(/Last Updated On: (.*)/)[1],
    } });
    const updated = fs.readFileSync(path.join(temp, 'README.md'), 'utf8');
    assert.match(updated, /\*\*3,414\*\* counties/);
    assert.equal(updated.replace('**3,414** counties', original.match(/\*\*[0-9,]+\*\* counties/)[0]), original);
  } finally {
    fs.rmSync(temp, { recursive: true });
  }
});

test('export workflow compresses, requires and checksums every county_states companion (v5)', () => {
  const root = path.resolve(__dirname, '../..');
  const workflow = fs.readFileSync(path.join(root, '.github/workflows/export.yml'), 'utf8');
  const step = (name) => workflow.split(`      - name: ${name}\n`)[1].split('\n      - name:')[0];
  const compress = step('Compress All Large Files');
  const required = step('Check every file a release carries');
  const packaged = step('Package the build with its checksums');
  for (const file of ['csv/county_states.csv', 'sql/county_states.sql', 'psql/county_states.sql', 'sqlite/county_states.sqlite3',
    'sqlserver/county_states.sql']) {
    assert.ok(compress.includes(` ${file} `) || compress.includes(` ${file};`), `${file} is not compressed`);
    assert.match(required, new RegExp(`^\\s+${file.replace(/[.+]/g, '\\$&')}\\.gz$`, 'm'), `${file}.gz is not required`);
    assert.match(packaged, new RegExp(`^\\s+${file.replace(/[.+]/g, '\\$&')}\\.gz$`, 'm'), `${file}.gz is not checksummed`);
  }
  assert.match(required, /check_county_states_csv\.py/, 'the CSV companion is not compared with json/counties.json');
});

test('the publish step expects exactly as many exports as the build checksums and the release gate require', () => {
  const root = path.resolve(__dirname, '../..');
  const workflow = fs.readFileSync(path.join(root, '.github/workflows/export.yml'), 'utf8');
  const step = (name) => workflow.split(`      - name: ${name}\n`)[1].split('\n      - name:')[0];
  const listed = (body, name) => body.split(`${name}=(\n`)[1].split('\n          )')[0].split(/\s+/).filter(Boolean);
  const built = listed(step('Package the build with its checksums'), 'files').filter((f) => f.endsWith('.gz') && f !== 'export-small-files.tar.gz');
  const required = listed(step('Check every file a release carries'), 'required');
  const placement = step('Verify and place the build');
  const counts = [...placement.matchAll(/-eq (\d+)\b|expected (\d+) exports/g)].map((m) => Number(m[1] || m[2]));
  assert.deepEqual([...required].sort(), [...built].sort(), 'the release gate and the checksum list name different exports');
  assert.ok(counts.length >= 2, 'the placement step has no expected export count');
  for (const n of counts) assert.equal(n, built.length, `the placement step expects ${n} exports; the build lists ${built.length}`);
});
