/**
 * Cross-Reference Validation (Idea 9)
 * Verifies that state_id and country_id actually exist in the repo data,
 * and that state_code/country_code match the referenced records.
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const { getEntityType, parseJsonFile, loadRepoData } = require('./utils');

async function run() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = github.getOctokit(token);
  const { pull_request: pr } = github.context.payload;

  if (!pr) {
    core.setFailed('This script must run on a pull_request event.');
    return;
  }

  // Load reference data
  const countries = loadRepoData('countries');
  const states = loadRepoData('states');

  if (!countries) {
    core.warning('Could not load countries.json for cross-reference. Skipping.');
    core.setOutput('errors', JSON.stringify([]));
    core.setOutput('valid', '0');
    core.setOutput('has_errors', 'false');
    return;
  }

  // Build lookup maps
  const countryById = new Map();
  const countryByCode = new Map();
  if (countries) {
    for (const c of countries) {
      countryById.set(Number(c.id), c);
      if (c.iso2) countryByCode.set(c.iso2.toUpperCase(), c);
    }
  }

  const stateById = new Map();
  if (states) {
    for (const s of states) {
      stateById.set(Number(s.id), s);
    }
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

  const errors = [];
  let validCount = 0;

  for (const file of contributionFiles) {
    const filePath = file.filename;
    const entityType = getEntityType(filePath);
    const fullPath = path.join(process.cwd(), filePath);

    if (!entityType || !fs.existsSync(fullPath)) continue;

    const { data, error } = parseJsonFile(fullPath);
    if (error || !data) continue;

    const records = Array.isArray(data) ? data : [data];

    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      const label = record.name || record.code;
      const prefix = `${filePath}: Record ${i + 1}${label ? ` ("${label}")` : ''}`;

      if (entityType === 'cities') {
        // Validate country_id exists
        if (record.country_id) {
          const country = countryById.get(Number(record.country_id));
          if (!country) {
            errors.push(`${prefix}: country_id ${record.country_id} does not exist`);
          } else {
            validCount++;
            // Validate country_code matches
            if (record.country_code && country.iso2) {
              if (record.country_code.toUpperCase() !== country.iso2.toUpperCase()) {
                errors.push(
                  `${prefix}: country_code "${record.country_code}" does not match country_id ${record.country_id} (expected "${country.iso2}")`
                );
              }
            }
          }
        }

        // Validate state_id exists
        if (record.state_id && states) {
          const state = stateById.get(Number(record.state_id));
          if (!state) {
            errors.push(`${prefix}: state_id ${record.state_id} does not exist`);
          } else {
            validCount++;
            // Validate state belongs to the specified country
            if (record.country_id && Number(state.country_id) !== Number(record.country_id)) {
              errors.push(
                `${prefix}: state_id ${record.state_id} ("${state.name}") belongs to country_id ${state.country_id}, not ${record.country_id}`
              );
            }
            // Validate state_code matches
            if (record.state_code && state.state_code) {
              if (record.state_code !== state.state_code && record.state_code !== state.iso2) {
                errors.push(
                  `${prefix}: state_code "${record.state_code}" does not match state_id ${record.state_id} (expected "${state.state_code || state.iso2}")`
                );
              }
            }
          }
        }
      }

      if (entityType === 'states') {
        // Validate country_id exists
        if (record.country_id) {
          const country = countryById.get(Number(record.country_id));
          if (!country) {
            errors.push(`${prefix}: country_id ${record.country_id} does not exist`);
          } else {
            validCount++;
            // Validate country_code matches
            if (record.country_code && country.iso2) {
              if (record.country_code.toUpperCase() !== country.iso2.toUpperCase()) {
                errors.push(
                  `${prefix}: country_code "${record.country_code}" does not match country_id ${record.country_id} (expected "${country.iso2}")`
                );
              }
            }
          }
        }
      }

      if (entityType === 'postcodes') {
        // Validate country_id exists (required FK)
        if (record.country_id) {
          const country = countryById.get(Number(record.country_id));
          if (!country) {
            errors.push(`${prefix}: country_id ${record.country_id} does not exist`);
          } else {
            validCount++;
            if (record.country_code && country.iso2) {
              if (record.country_code.toUpperCase() !== country.iso2.toUpperCase()) {
                errors.push(
                  `${prefix}: country_code "${record.country_code}" does not match country_id ${record.country_id} (expected "${country.iso2}")`
                );
              }
            }
          }
        }

        // Validate state_id exists if provided (optional FK)
        if (record.state_id != null && states) {
          const state = stateById.get(Number(record.state_id));
          if (!state) {
            errors.push(`${prefix}: state_id ${record.state_id} does not exist`);
          } else {
            validCount++;
            if (record.country_id && Number(state.country_id) !== Number(record.country_id)) {
              errors.push(
                `${prefix}: state_id ${record.state_id} ("${state.name}") belongs to country_id ${state.country_id}, not ${record.country_id}`
              );
            }
          }
        }

        // Validate postcode format against country regex if defined
        if (record.code && record.country_id) {
          const country = countryById.get(Number(record.country_id));
          if (country && country.postal_code_regex) {
            try {
              const re = new RegExp(country.postal_code_regex);
              if (!re.test(record.code)) {
                errors.push(
                  `${prefix}: code "${record.code}" does not match postal_code_regex "${country.postal_code_regex}" of ${country.iso2}`
                );
              }
            } catch (e) {
              // Invalid regex on the country side — skip silently rather than blocking PR
            }
          }
        }
      }
    }
  }

  core.setOutput('errors', JSON.stringify(errors));
  core.setOutput('valid', validCount.toString());
  core.setOutput('has_errors', (errors.length > 0).toString());

  core.info(`Cross-reference: ${validCount} valid, ${errors.length} errors`);
  for (const err of errors) core.error(err);
}

run().catch((err) => core.setFailed(err.message));
