/** Test fixture: a scratch git repository shaped like the checkout of a pull_request (a merge commit). */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

/** A scratch repository whose HEAD merges a PR branch into the base, as actions/checkout leaves a pull_request. */
function mergeRepo() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'csc-merge-'));
  const git = (...args) => execFileSync('git', args, { cwd: dir, encoding: 'utf8' });
  const write = (name, text) => {
    fs.mkdirSync(path.join(dir, path.dirname(name)), { recursive: true });
    fs.writeFileSync(path.join(dir, name), text);
  };
  git('init', '-q', '-b', 'main');
  git('config', 'user.email', 't@example.invalid');
  git('config', 'user.name', 'test');
  const states = (rows) => `${JSON.stringify(rows, null, 2)}\n`;   // pretty-printed, one field per line, as in the repo
  write('contributions/states/states.json', states([{ id: 1, name: 'Kept' }, { id: 2, name: 'Gone' }]));
  write('contributions/postcodes/XX.json', '[]\n');
  git('add', '-A'); git('commit', '-q', '-m', 'base');
  git('checkout', '-q', '-b', 'pr');
  write('contributions/states/states.json', states([{ id: 1, name: 'Kept' }]));
  fs.rmSync(path.join(dir, 'contributions/postcodes/XX.json'));
  write('contributions/postcodes/YY.json', '[]\n');
  git('add', '-A'); git('commit', '-q', '-m', 'pr');
  git('checkout', '-q', 'main');
  write('README.md', 'base moved on\n');
  git('add', '-A'); git('commit', '-q', '-m', 'base moves');
  git('merge', '-q', '--no-ff', '-m', 'merge', 'pr');
  return dir;
}

/** Run fn with the working directory set to dir. */
async function inDir(dir, fn) {
  const back = process.cwd();
  process.chdir(dir);
  try { return await fn(); } finally { process.chdir(back); }
}

module.exports = { mergeRepo, inDir };
