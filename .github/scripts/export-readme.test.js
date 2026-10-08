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
