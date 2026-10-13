/**
 * Diff Analysis (Ideas 6, 12, 13)
 * Analyses PR changes to determine:
 * - Entity types changed (auto-label: data:cities, data:states, data:countries)
 * - Operations (additions, modifications, deletions)
 * - Record counts (flag large contributions > 500)
 * - Critical changes (deletions in states/countries)
 * - Whether the analysis is complete (analysis_incomplete): a states/countries file it could not compare
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const { getEntityType, parseJsonFile, listChangedFiles, baseJson } = require('./utils');

/** The persisted ids of a parsed states or countries file; throws when it is not an array of records with ids. */
function recordIds(data, where) {
  if (!Array.isArray(data)) throw new Error(`${where} is not an array of records`);
  const ids = data.map((r) => r && r.id).filter((id) => id !== undefined && id !== null);
  if (new Set(ids).size !== ids.length) throw new Error(`${where} repeats an id`);
  return new Set(ids);
}

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
  const incompleteReasons = [];
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
      case 'renamed':
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

    // Record deletions within a changed states or countries file: compare the persisted ids of the file on the merge
    // base with the merged file, so formatting, renames and duplicate names cannot hide a removed record. A file that
    // cannot be compared makes the analysis incomplete, which the report shows and the final step fails on.
    if ((file.status === 'modified' || file.status === 'renamed') && (entityType === 'states' || entityType === 'countries')) {
      try {
        const before = recordIds(baseJson(pr, file.previous_filename || filePath), `${filePath} on the base`);
        const { data, error } = parseJsonFile(path.join(process.cwd(), filePath));
        if (error || data === undefined) throw new Error(`${filePath} in the PR cannot be parsed`);
        const after = recordIds(data, `${filePath} in the PR`);
        const removed = [...before].filter((id) => !after.has(id));
        if (removed.length > 0) {
          isCritical = true;
          criticalReasons.push(
            `Record deletions detected in ${entityType} file: ${filePath} (${removed.length} record(s) removed: id ${removed.slice(0, 5).join(', ')})`
          );
        }
      } catch (err) {
        incompleteReasons.push(`Could not compare the records of ${filePath} with the base (${err.message.split('\n')[0]}); check it for removed records by hand`);
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
  core.setOutput('analysis_incomplete', (incompleteReasons.length > 0).toString());
  core.setOutput('incomplete_reasons', JSON.stringify(incompleteReasons));

  // Log summary
  core.info(`Entity types: ${Array.from(entityTypes).join(', ') || 'none'}`);
  core.info(`Operations: +${operations.added} ~${operations.modified} -${operations.removed}`);
  core.info(`Total records: ${totalRecords}`);
  core.info(`Critical: ${isCritical}`);
  if (isCritical) {
    for (const reason of criticalReasons) core.warning(`CRITICAL: ${reason}`);
  }
  for (const reason of incompleteReasons) core.warning(`INCOMPLETE: ${reason}`);
}

run().catch((err) => core.setFailed(err.message));
