/** analyse-diff.js on pull requests whose diff GitHub will not produce. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const { mergeRepo, inDir } = require('./merge-fixture');

/** Run the real analyse-diff.js in dir with GitHub and core stubs; paginate is the stubbed file listing. */
async function analyse(dir, paginate) {
  const outputs = {};
  const fakeGithub = {
    getOctokit: () => ({ paginate, rest: { pulls: { listFiles() {} }, issues: { addLabels: async () => {} } } }),
    context: { payload: { pull_request: { number: 1 } }, repo: { owner: 'fixture', repo: 'fixture' } },
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

test('a state removed in a PR GitHub cannot diff is still flagged critical', async () => {
  const out = await analyse(mergeRepo(), async () => { throw new Error('Sorry, this diff is taking too long to generate.'); });
  assert.equal(out.is_critical, 'true');
  assert.match(out.critical_reasons, /Record deletions detected in states file.*Gone/);
  assert.deepEqual(JSON.parse(out.operations), { added: 1, modified: 1, removed: 1 });
});

test('a states diff that cannot be read at all is treated as a possible deletion', async () => {
  const empty = fs.mkdtempSync(path.join(os.tmpdir(), 'csc-nogit-'));
  const listed = async () => [{ filename: 'contributions/states/states.json', status: 'modified' }];
  const out = await analyse(empty, listed);
  assert.equal(out.is_critical, 'true');
  assert.match(out.critical_reasons, /Could not read the diff of contributions\/states\/states.json/);
});
