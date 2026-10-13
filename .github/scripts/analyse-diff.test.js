/** analyse-diff.js: removed state/country records found by id, on lists GitHub refuses, and incomplete analysis. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { mergeRepo, inDir, pretty, STATES } = require('./merge-fixture');

const REFUSED = new Error('Sorry, this diff is taking too long to generate.');

/**
 * Run the real analyse-diff.js in dir with GitHub and core stubs. `files` is what the API lists (both the direct call
 * and the paginated one serve it); REFUSED makes both fail, as GitHub does on a very large diff.
 */
async function analyse(dir, head, files) {
  const outputs = {};
  const listFiles = async () => { if (files === REFUSED) throw REFUSED; return { data: files }; };
  const fakeGithub = {
    getOctokit: () => ({
      paginate: async (fn, params) => (await fn(params)).data,
      rest: { pulls: { listFiles }, issues: { addLabels: async () => {} } },
    }),
    context: { payload: { pull_request: { number: 1, head: { sha: head } } }, repo: { owner: 'fixture', repo: 'fixture' } },
  };
  const fakeCore = {
    setOutput: (key, value) => { outputs[key] = value; },
    info() {}, warning() {}, setFailed(message) { throw new Error(message); },
  };
  const code = fs.readFileSync(path.join(__dirname, 'analyse-diff.js'), 'utf8');
  const sandbox = {
    require: (key) => key === '@actions/github' ? fakeGithub : key === '@actions/core' ? fakeCore :
      key === './utils' ? require('./utils') : require(key),
    process, console, module: { exports: {} },
  };
  await inDir(dir, () => vm.runInNewContext(code, sandbox));
  return outputs;
}

test('a state removed in a PR GitHub cannot list is flagged critical by its id', async () => {
  const { dir, head } = mergeRepo();
  const out = await analyse(dir, head, REFUSED);
  assert.equal(out.is_critical, 'true');
  assert.match(out.critical_reasons, /Record deletions detected in states file.*removed: id 2/);
  assert.equal(out.analysis_incomplete, 'false');
  assert.deepEqual(JSON.parse(out.operations), { added: 1, modified: 1, removed: 1 });
});

test('a removal in compact JSON, one line for every record, is still found', async () => {
  const { dir, head } = mergeRepo({ before: '[{"id": 1, "name": "Kept"}, {"id": 2, "name": "Gone"}]\n', after: '[{"id": 1, "name": "Kept"}]\n' });
  const out = await analyse(dir, head, REFUSED);
  assert.match(out.critical_reasons, /removed: id 2/);
});

test('a record replaced by another with the same name but a new id is a removal', async () => {
  const { dir, head } = mergeRepo({ after: pretty([{ id: 1, name: 'Kept' }, { id: 3, name: 'Gone' }]) });
  const out = await analyse(dir, head, REFUSED);
  assert.match(out.critical_reasons, /removed: id 2/);
});

test('a renamed states file that loses a record is compared with its old path', async () => {
  const moved = 'contributions/states/states-moved.json';
  const { dir, head } = mergeRepo({ afterPath: moved });
  const out = await analyse(dir, head, [{ filename: moved, status: 'renamed', previous_filename: STATES }]);
  assert.equal(out.is_critical, 'true');
  assert.match(out.critical_reasons, /states-moved.json.*removed: id 2/);
});

test('an edit that keeps every record is not critical', async () => {
  const { dir, head } = mergeRepo({ after: pretty([{ id: 1, name: 'Kept' }, { id: 2, name: 'Renamed' }]) });
  const out = await analyse(dir, head, [{ filename: STATES, status: 'modified' }]);
  assert.equal(out.is_critical, 'false');
  assert.equal(out.analysis_incomplete, 'false');
});

test('a states file that cannot be compared makes the analysis incomplete', async () => {
  const { dir } = mergeRepo();
  const out = await analyse(dir, '0'.repeat(40), [{ filename: STATES, status: 'modified' }]);
  assert.equal(out.analysis_incomplete, 'true');
  assert.match(out.incomplete_reasons, /Could not compare the records of contributions\/states\/states.json/);
});

for (const [label, moved] of [['out of contributions', 'archive/regions.json'], ['to a non-JSON name', 'contributions/states/states.txt'],
  ['into another entity folder', 'contributions/cities/XX.json']]) {
  test(`a states file renamed ${label} is a deleted states file`, async () => {
    const { dir, head } = mergeRepo({ afterPath: moved, after: pretty([{ id: 1, name: 'Kept' }, { id: 2, name: 'Gone' }]) });
    const out = await analyse(dir, head, [{ filename: moved, status: 'renamed', previous_filename: STATES }]);
    assert.equal(out.is_critical, 'true', label);
    assert.match(out.critical_reasons, new RegExp(`Deletion of states file: contributions/states/states.json \\(moved to ${moved.replace('.', '\\.')}\\)`));
  });
}

test('a base record without an id cannot be compared, so the analysis is incomplete', async () => {
  const { dir, head } = mergeRepo({ before: pretty([{ name: 'Kept' }, { name: 'Gone' }]), after: pretty([{ name: 'Kept' }]) });
  const out = await analyse(dir, head, REFUSED);
  assert.equal(out.analysis_incomplete, 'true');
  assert.match(out.incomplete_reasons, /row 0 has no positive integer id/);
});

test('a new record without an id in the PR is an addition, and a removal beside it is still found', async () => {
  const { dir, head } = mergeRepo({ after: pretty([{ id: 1, name: 'Kept' }, { name: 'New' }]) });
  const out = await analyse(dir, head, REFUSED);
  assert.equal(out.analysis_incomplete, 'false');
  assert.match(out.critical_reasons, /removed: id 2/);
});

for (const status of ['changed', 'unchanged', 'some-future-status']) {
  test(`a states file listed as "${status}" is still compared, so a removal cannot slip past`, async () => {
    const { dir, head } = mergeRepo();
    const out = await analyse(dir, head, [{ filename: STATES, status }]);
    assert.equal(out.is_critical, 'true', status);
    assert.match(out.critical_reasons, /removed: id 2/);
  });
}
