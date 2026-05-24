/**
 * Schema Validation (Ideas 2 & 15)
 * Parses changed JSON files in contributions/ against schema.sql requirements.
 * Validates JSON syntax, formatting, required fields, and field formats.
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const { getEntityType, parseJsonFile, validateRecord, AUTO_MANAGED_FIELDS } = require('./utils');

async function run() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = github.getOctokit(token);
  const { pull_request: pr } = github.context.payload;

  if (!pr) {
    core.setFailed('This script must run on a pull_request event.');
    return;
  }

  // Get changed files
  const { data: files } = await octokit.rest.pulls.listFiles({
    owner: github.context.repo.owner,
    repo: github.context.repo.repo,
    pull_number: pr.number,
    per_page: 300,
  });

  const contributionFiles = files.filter(
    (f) =>
      f.filename.startsWith('contributions/') &&
      f.filename.endsWith('.json') &&
      f.status !== 'removed'
  );

  if (contributionFiles.length === 0) {
    core.info('No contribution JSON files changed.');
    core.setOutput('errors', JSON.stringify([]));
    core.setOutput('warnings', JSON.stringify([]));
    core.setOutput('record_count', '0');
    core.setOutput('has_errors', 'false');
    return;
  }

  const allErrors = [];
  const allWarnings = [];
  let totalRecords = 0;

  for (const file of contributionFiles) {
    const filePath = file.filename;
    const entityType = getEntityType(filePath);

    if (!entityType) {
      allWarnings.push(`Cannot determine entity type for: ${filePath}`);
      continue;
    }

    core.info(`Validating: ${filePath} (${entityType})`);

    // Check file exists locally (checkout required in workflow)
    const fullPath = path.join(process.cwd(), filePath);
    if (!fs.existsSync(fullPath)) {
      allErrors.push(`File not found: ${filePath}`);
      continue;
    }

    // JSON syntax validation (Idea 15)
    const { data, error } = parseJsonFile(fullPath);
    if (error) {
      allErrors.push(`${filePath}: ${error}`);
      continue;
    }

    // Ensure data is an array or single object
    const records = Array.isArray(data) ? data : [data];
    totalRecords += records.length;

    // Validate each record against schema (Idea 2)
    for (let i = 0; i < records.length; i++) {
      const record = records[i];

      if (typeof record !== 'object' || record === null) {
        allErrors.push(`${filePath}: Record ${i + 1} is not a valid object`);
        continue;
      }

      const { errors, warnings } = validateRecord(record, entityType, i);
      allErrors.push(...errors.map((e) => `${filePath}: ${e}`));
      allWarnings.push(...warnings.map((w) => `${filePath}: ${w}`));
    }

    // JSON formatting check (consistent 2-space indent)
    try {
      const raw = fs.readFileSync(fullPath, 'utf8');
      const formatted = JSON.stringify(data, null, 2) + '\n';

      // Check for BOM
      if (raw.charCodeAt(0) === 0xfeff) {
        allWarnings.push(`${filePath}: Contains BOM character (byte order mark)`);
      }

      // Check for trailing whitespace on lines
      const lines = raw.split('\n');
      for (let i = 0; i < lines.length; i++) {
        if (lines[i] !== lines[i].trimEnd() && lines[i].trim().length > 0) {
          allWarnings.push(`${filePath}: Line ${i + 1} has trailing whitespace`);
          break; // Only report once per file
        }
      }
    } catch {
      // Non-critical formatting check
    }
  }

  const hasErrors = allErrors.length > 0;

  // Outputs are passed to the report step via environment variables, which
  // have a hard size limit. A whole-file edit can legitimately surface
  // thousands of entries (e.g. auto-managed-field warnings on every existing
  // row), so cap each list before emitting to avoid "Maximum object size
  // exceeded". has_errors is computed from the full, uncapped count above.
  const MAX_REPORTED = 50;
  const capList = (list) =>
    list.length <= MAX_REPORTED
      ? list
      : [...list.slice(0, MAX_REPORTED), `...and ${list.length - MAX_REPORTED} more`];

  core.setOutput('errors', JSON.stringify(capList(allErrors)));
  core.setOutput('warnings', JSON.stringify(capList(allWarnings)));
  core.setOutput('record_count', totalRecords.toString());
  core.setOutput('has_errors', hasErrors.toString());

  // Log results
  core.info(`\nValidation complete: ${totalRecords} records across ${contributionFiles.length} files`);
  core.info(`Errors: ${allErrors.length}, Warnings: ${allWarnings.length}`);

  for (const err of allErrors) core.error(err);
  for (const warn of allWarnings) core.warning(warn);
}

run().catch((err) => core.setFailed(err.message));
