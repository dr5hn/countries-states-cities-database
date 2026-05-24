/**
 * Coordinate Sanity Check (Idea 8)
 * Validates that coordinates fall within the parent country's bounding box.
 * Uses a static country-bounds.json file with 50km tolerance for border cities.
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const { getEntityType, parseJsonFile } = require('./utils');

// Buffer distance in degrees (roughly 50km at equator)
const BUFFER_DEGREES = 0.45;

async function run() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = github.getOctokit(token);
  const { pull_request: pr } = github.context.payload;

  if (!pr) {
    core.setFailed('This script must run on a pull_request event.');
    return;
  }

  // Load country bounds
  const boundsPath = path.join(__dirname, '..', 'data', 'country-bounds.json');
  let countryBounds = {};
  if (fs.existsSync(boundsPath)) {
    try {
      countryBounds = JSON.parse(fs.readFileSync(boundsPath, 'utf8'));
    } catch {
      core.warning('Could not parse country-bounds.json');
    }
  } else {
    core.warning('country-bounds.json not found. Skipping coordinate bounds check.');
    core.setOutput('warnings', JSON.stringify([]));
    core.setOutput('warning_count', '0');
    core.setOutput('checked', '0');
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

    if (!entityType || entityType === 'countries' || !fs.existsSync(fullPath)) continue;

    const { data, error } = parseJsonFile(fullPath);
    if (error || !data) continue;

    const records = Array.isArray(data) ? data : [data];

    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      const lat = parseFloat(record.latitude);
      const lon = parseFloat(record.longitude);
      const countryCode = (record.country_code || '').toUpperCase();

      if (isNaN(lat) || isNaN(lon) || !countryCode) continue;

      const bounds = countryBounds[countryCode];
      if (!bounds) {
        // No bounds data for this country, skip
        continue;
      }

      checked++;

      const { minLat, maxLat, minLon, maxLon } = bounds;

      // Check with buffer tolerance
      if (
        lat < minLat - BUFFER_DEGREES ||
        lat > maxLat + BUFFER_DEGREES ||
        lon < minLon - BUFFER_DEGREES ||
        lon > maxLon + BUFFER_DEGREES
      ) {
        const prefix = `Record ${i + 1}${record.name ? ` ("${record.name}")` : ''}`;
        warnings.push(
          `${filePath}: ${prefix}: coordinates (${lat}, ${lon}) fall outside ${countryCode} bounds ` +
          `[${minLat}, ${maxLat}] x [${minLon}, ${maxLon}] (with ${BUFFER_DEGREES}deg tolerance)`
        );
      }
    }
  }

  // Cap the emitted list (env-var size limit in the report step); emit the
  // true total separately.
  core.setOutput('warnings', JSON.stringify(warnings.slice(0, 50)));
  core.setOutput('warning_count', warnings.length.toString());
  core.setOutput('checked', checked.toString());

  core.info(`Coordinate bounds: ${checked} checked, ${warnings.length} warnings`);
  for (const warn of warnings) core.warning(warn);
}

run().catch((err) => core.setFailed(err.message));
