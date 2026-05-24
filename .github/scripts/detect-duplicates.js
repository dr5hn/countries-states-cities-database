/**
 * Duplicate Detection (Idea 7)
 * Checks if city/state being added already exists in the database.
 * Uses fuzzy name matching (Levenshtein <= 2) and coordinate proximity (< 5km).
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const {
  getEntityType,
  parseJsonFile,
  loadRepoData,
  haversineDistance,
  levenshteinDistance,
} = require('./utils');

const NAME_DISTANCE_THRESHOLD = 2;
const COORDINATE_DISTANCE_KM = 5;

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

  const warnings = [];
  let checked = 0;

  for (const file of contributionFiles) {
    const filePath = file.filename;
    const entityType = getEntityType(filePath);
    const fullPath = path.join(process.cwd(), filePath);

    if (!entityType || !fs.existsSync(fullPath)) continue;

    // Load existing data for comparison
    // For cities, load the country-specific file from contributions/ instead of
    // the full cities.json (153k+ records) to avoid memory and performance issues
    let existingData = null;
    if (entityType === 'cities') {
      const countryCode = path.basename(filePath, '.json').toUpperCase();
      const countryFilePath = path.join(process.cwd(), 'contributions', 'cities', `${countryCode}.json`);
      if (fs.existsSync(countryFilePath)) {
        const { data: countryData } = parseJsonFile(countryFilePath);
        existingData = countryData;
      }
    } else {
      existingData = loadRepoData(entityType);
    }
    if (!existingData || existingData.length === 0) {
      core.info(`No existing ${entityType} data found for duplicate check.`);
      continue;
    }

    const { data, error } = parseJsonFile(fullPath);
    if (error || !data) continue;

    const records = Array.isArray(data) ? data : [data];

    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      if (!record.name) continue;

      checked++;
      const prefix = `Record ${i + 1} ("${record.name}")`;

      // Filter existing records to same state/country for efficiency
      let candidates = existingData;
      if (entityType === 'cities' && record.state_id) {
        candidates = existingData.filter(
          (e) => Number(e.state_id) === Number(record.state_id)
        );
      } else if (entityType === 'states' && record.country_id) {
        candidates = existingData.filter(
          (e) => Number(e.country_id) === Number(record.country_id)
        );
      }

      for (const existing of candidates) {
        if (!existing.name) continue;

        // Fuzzy name match
        const nameDist = levenshteinDistance(record.name, existing.name);
        const isNameMatch = nameDist <= NAME_DISTANCE_THRESHOLD;
        const isExactMatch = nameDist === 0;

        // Coordinate proximity check (for cities/states with coords)
        let isCloseProximity = false;
        let distanceKm = null;
        if (
          record.latitude && record.longitude &&
          existing.latitude && existing.longitude
        ) {
          distanceKm = haversineDistance(
            parseFloat(record.latitude),
            parseFloat(record.longitude),
            parseFloat(existing.latitude),
            parseFloat(existing.longitude)
          );
          isCloseProximity = distanceKm < COORDINATE_DISTANCE_KM;
        }

        // Report potential duplicates
        if (isExactMatch && isCloseProximity) {
          warnings.push(
            `${filePath}: ${prefix} appears to be a duplicate of existing "${existing.name}" ` +
            `(id: ${existing.id}, distance: ${distanceKm.toFixed(1)}km)`
          );
        } else if (isExactMatch) {
          // Exact name match but different coordinates
          const distStr = distanceKm !== null ? `, ${distanceKm.toFixed(1)}km apart` : '';
          warnings.push(
            `${filePath}: ${prefix} has the same name as existing "${existing.name}" ` +
            `(id: ${existing.id}${distStr}) - verify this is not a duplicate`
          );
        } else if (isNameMatch && isCloseProximity) {
          warnings.push(
            `${filePath}: ${prefix} is similar to existing "${existing.name}" ` +
            `(id: ${existing.id}, name distance: ${nameDist}, ${distanceKm.toFixed(1)}km apart)`
          );
        }
      }
    }
  }

  // Cap the emitted list — it is passed to the report step via an environment
  // variable with a hard size limit, and dense localities can produce
  // thousands of fuzzy-match warnings. Emit the true total separately.
  core.setOutput('warnings', JSON.stringify(warnings.slice(0, 50)));
  core.setOutput('warning_count', warnings.length.toString());
  core.setOutput('checked', checked.toString());

  core.info(`Duplicate check: ${checked} records checked, ${warnings.length} potential duplicates`);
  for (const warn of warnings) core.warning(warn);
}

run().catch((err) => core.setFailed(err.message));
