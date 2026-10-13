/**
 * PR Format Validation (Ideas 1 & 5)
 * Checks: description present, source documentation linked,
 * justification included, issue linkage for data changes.
 */

const core = require('@actions/core');
const github = require('@actions/github');
const { listChangedFiles } = require('./utils');

async function run() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = github.getOctokit(token);
  const { pull_request: pr } = github.context.payload;

  if (!pr) {
    core.setFailed('This script must run on a pull_request event.');
    return;
  }

  const results = {
    description: { pass: false, label: 'Description provided' },
    source: { pass: false, label: 'Data source linked' },
    issueLinked: { pass: false, label: 'Issue linked (recommended for data changes)' },
    justification: { pass: false, label: 'Justification / context provided' },
  };

  const body = pr.body || '';
  const title = pr.title || '';

  // 1. Check description is present and not just the default template
  const defaultTemplateMarkers = [
    '<!-- Describe what this PR does -->',
    'No description provided',
  ];
  const hasDescription =
    body.trim().length > 30 &&
    !defaultTemplateMarkers.some((marker) => body.trim() === marker);
  results.description.pass = hasDescription;

  // 2. Check for data source documentation
  const sourcePatterns = [
    /source:\s*.+/i,
    /https?:\/\/\S+/i,
    /data\s*source/i,
    /official\s*(source|website|portal)/i,
    /geonames/i,
    /wikipedia/i,
    /government|\.gov/i,
  ];
  results.source.pass = sourcePatterns.some((p) => p.test(body));

  // 3. Check for issue linkage
  const issuePatterns = [
    /closes?\s*#\d+/i,
    /fixes?\s*#\d+/i,
    /resolves?\s*#\d+/i,
    /related\s*(to)?\s*#\d+/i,
    /#\d+/,
  ];
  results.issueLinked.pass = issuePatterns.some((p) => p.test(body)) || issuePatterns.some((p) => p.test(title));

  // 4. Check for justification / context
  const justificationPatterns = [
    /justification/i,
    /reason/i,
    /because/i,
    /this\s*(pr|change|update)/i,
    /adding|updating|correcting|fixing|removing/i,
    /incorrect|wrong|missing|outdated/i,
  ];
  results.justification.pass =
    justificationPatterns.some((p) => p.test(body)) || body.trim().length > 100;

  // 5. Determine if this is a data PR (changes to contributions/)
  const files = await listChangedFiles(octokit, github.context, pr);

  const isDataPR = files.some((f) => f.filename.startsWith('contributions/'));

  // For data PRs without issue linkage AND vague description, this is critical
  const needsClarification =
    isDataPR && !results.issueLinked.pass && !results.description.pass;

  // Output results
  core.setOutput('results', JSON.stringify(results));
  core.setOutput('is_data_pr', isDataPR.toString());
  core.setOutput('needs_clarification', needsClarification.toString());
  const hasErrors = !results.description.pass || (isDataPR && !results.source.pass);
  core.setOutput(
    'has_errors',
    hasErrors.toString()
  );

  // Log
  for (const [key, val] of Object.entries(results)) {
    const icon = val.pass ? 'PASS' : 'FAIL';
    core.info(`[${icon}] ${val.label}`);
  }

  if (needsClarification) {
    core.warning(
      'Data PR without linked issue or clear description - clarification needed.'
    );
  }
}

run().catch((err) => core.setFailed(err.message));
