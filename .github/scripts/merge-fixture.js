/** Test fixture: a scratch git repository shaped like the checkout of a pull_request (a merge commit). */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const STATES = 'contributions/states/states.json';

/** Pretty-printed JSON, one field per line, as the repository stores it. */
function pretty(rows) {
  return `${JSON.stringify(rows, null, 2)}\n`;
}

/**
 * A scratch repository whose HEAD merges a PR branch into a base that moved on, as actions/checkout leaves a
 * pull_request. The PR rewrites the states file (`before` on the base, `after` at `afterPath` in the PR), deletes
 * one postcode file and adds another. Returns { dir, head } with the PR's head commit.
 */
function mergeRepo({
  before = pretty([{ id: 1, name: 'Kept' }, { id: 2, name: 'Gone' }]),
  after = pretty([{ id: 1, name: 'Kept' }]),
  afterPath = STATES,
} = {}) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'csc-merge-'));
  const git = (...args) => execFileSync('git', args, { cwd: dir, encoding: 'utf8' });
  const write = (name, text) => {
    fs.mkdirSync(path.join(dir, path.dirname(name)), { recursive: true });
    fs.writeFileSync(path.join(dir, name), text);
  };
  git('init', '-q', '-b', 'main');
  git('config', 'user.email', 't@example.invalid');
  git('config', 'user.name', 'test');
  write(STATES, before);
  write('contributions/postcodes/XX.json', '[]\n');
  git('add', '-A'); git('commit', '-q', '-m', 'base');
  git('checkout', '-q', '-b', 'pr');
  if (afterPath !== STATES) git('mv', STATES, afterPath);
  write(afterPath, after);
  fs.rmSync(path.join(dir, 'contributions/postcodes/XX.json'));
  write('contributions/postcodes/YY.json', '[]\n');
  git('add', '-A'); git('commit', '-q', '-m', 'pr');
  const head = git('rev-parse', 'HEAD').trim();
  git('checkout', '-q', 'main');
  write('README.md', 'base moved on\n');
  git('add', '-A'); git('commit', '-q', '-m', 'base moves');
  git('merge', '-q', '--no-ff', '-m', 'merge', 'pr');
  return { dir, head };
}

/** Run fn with the working directory set to dir. */
async function inDir(dir, fn) {
  const back = process.cwd();
  process.chdir(dir);
  try { return await fn(); } finally { process.chdir(back); }
}

module.exports = { mergeRepo, inDir, pretty, STATES };
