/**
 * Diff Analysis (Ideas 6, 12, 13)
 * Analyses PR changes to determine:
 * - Entity types changed (auto-label: data:cities, data:states, data:countries)
 * - Operations (additions, modifications, deletions)
 * - Record counts (flag large contributions > 500)
 * - Critical changes (deletions in states/countries)
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const { getEntityType, parseJsonFile, listChangedFiles, gitFilePatch } = require('./utils');

async function run() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = github.getOctokit(token);
  const { pull_request: pr } = github.context.payload;

  if (!pr) {
    core.setFailed('This script must run on a pull_request event.');
    return;
  }

  // Get changed files
  const files = await listChangedFiles(octokit, github.context, pr);

  const labels = new Set();
  const operations = { added: 0, modified: 0, removed: 0 };
  const entityTypes = new Set();
  let isCritical = false;
  let criticalReasons = [];
  let totalRecords = 0;

  for (const file of files) {
    const filePath = file.filename;
    const entityType = getEntityType(filePath);

    if (!filePath.startsWith('contributions/') || !filePath.endsWith('.json')) continue;

    if (entityType) {
      entityTypes.add(entityType);
      labels.add(`data:${entityType}`);
    }

    // Track operations
    switch (file.status) {
      case 'added':
        operations.added++;
        break;
      case 'modified':
        operations.modified++;
        break;
      case 'removed':
        operations.removed++;

        // Idea 6: Critical PR detection for state/country deletions
        if (entityType === 'states' || entityType === 'countries') {
          isCritical = true;
          criticalReasons.push(
            `Deletion of ${entityType} file: ${filePath}`
          );
        }
        break;
    }

    // Count records in added/modified files
    if (file.status !== 'removed') {
      const fullPath = path.join(process.cwd(), filePath);
      if (fs.existsSync(fullPath)) {
        const { data } = parseJsonFile(fullPath);
        if (data) {
          const records = Array.isArray(data) ? data : [data];
          totalRecords += records.length;
        }
      }
    }

    // Check for record deletions within modified files (patch analysis)
    // Only flag as critical when actual records are removed (name field deleted
    // without a corresponding addition), not simple field edits
    if (file.status === 'modified' && (entityType === 'states' || entityType === 'countries')) {
      // The API leaves out the patch of a large diff, and a listing read from git has none: read it from git, and
      // treat a diff that cannot be read as a possible deletion rather than skip the check.
      let patch = file.patch;
      if (patch === undefined) {
        try {
          patch = gitFilePatch(filePath);
        } catch (err) {
          isCritical = true;
          criticalReasons.push(`Could not read the diff of ${filePath} (${err.message.split('\n')[0]}); check it for removed records by hand`);
          patch = '';
        }
      }
      const patchLines = patch.split('\n');
      const deletedNames = new Set();
      const addedNames = new Set();

      for (const line of patchLines) {
        const nameMatch = line.match(/"name"\s*:\s*"([^"]+)"/);
        if (nameMatch) {
          if (line.startsWith('-') && !line.startsWith('---')) {
            deletedNames.add(nameMatch[1]);
          } else if (line.startsWith('+') && !line.startsWith('+++')) {
            addedNames.add(nameMatch[1]);
          }
        }
      }

      // Only flag names that were deleted without a corresponding addition
      const actuallyRemoved = [...deletedNames].filter((name) => !addedNames.has(name));
      if (actuallyRemoved.length > 0) {
        isCritical = true;
        criticalReasons.push(
          `Record deletions detected in ${entityType} file: ${filePath} (${actuallyRemoved.length} record(s) removed: ${actuallyRemoved.slice(0, 5).join(', ')})`
        );
      }
    }
  }

  // Idea 6: Critical labelling
  if (isCritical) {
    labels.add('critical');
    labels.add('requires-maintainer-approval');
  }

  // Idea 12: Large contribution flagging
  if (totalRecords > 500) {
    labels.add('large-contribution');
  }

  // Apply labels
  const labelsArray = Array.from(labels);
  if (labelsArray.length > 0) {
    try {
      await octokit.rest.issues.addLabels({
        owner: github.context.repo.owner,
        repo: github.context.repo.repo,
        issue_number: pr.number,
        labels: labelsArray,
      });
      core.info(`Labels applied: ${labelsArray.join(', ')}`);
    } catch (err) {
      core.warning(`Could not apply labels: ${err.message}`);
    }
  }

  // Outputs
  core.setOutput('labels', JSON.stringify(labelsArray));
  core.setOutput('is_critical', isCritical.toString());
  core.setOutput('critical_reasons', JSON.stringify(criticalReasons));
  core.setOutput('total_records', totalRecords.toString());
  core.setOutput('is_large', (totalRecords > 500).toString());
  core.setOutput('operations', JSON.stringify(operations));
  core.setOutput('entity_types', JSON.stringify(Array.from(entityTypes)));

  // Log summary
  core.info(`Entity types: ${Array.from(entityTypes).join(', ') || 'none'}`);
  core.info(`Operations: +${operations.added} ~${operations.modified} -${operations.removed}`);
  core.info(`Total records: ${totalRecords}`);
  core.info(`Critical: ${isCritical}`);
  if (isCritical) {
    for (const reason of criticalReasons) core.warning(`CRITICAL: ${reason}`);
  }
}

run().catch((err) => core.setFailed(err.message));
