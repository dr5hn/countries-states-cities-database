/**
 * Cross-Reference Validation (Idea 9)
 * Verifies that state_id and country_id actually exist in the repo data,
 * and that state_code/country_code match the referenced records.
 */

const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const { getEntityType, parseJsonFile, listChangedFiles, countyShapeErrors } = require('./utils');

// Lazy per-country cities loader — cities live in contributions/cities/{ISO2}.json
const cityCache = new Map();
function loadCitiesForCountry(iso2) {
  if (!iso2) return null;
  const cc = iso2.toUpperCase();
  if (cityCache.has(cc)) return cityCache.get(cc);
  const filePath = path.join(process.cwd(), 'contributions', 'cities', `${cc}.json`);
  if (!fs.existsSync(filePath)) {
    cityCache.set(cc, null);
    return null;
  }
  try {
    const cities = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    cityCache.set(cc, cities);
    return cities;
  } catch {
    cityCache.set(cc, null);
    return null;
  }
}

/** Load county IDs from canonical country contribution files, never stale exports. */
function loadCounties() {
  const dir = path.join(process.cwd(), 'contributions', 'counties');
  const byId = new Map();
  if (!fs.existsSync(dir)) return byId;
  for (const file of fs.readdirSync(dir).filter(f => /^[A-Z]{2}\.json$/.test(f)).sort()) {
    const { data, error } = parseJsonFile(path.join(dir, file));
    if (error || !Array.isArray(data)) throw new Error(`Cannot load counties/${file}: ${error || 'expected an array'}`);
    for (const county of data) {
      if (county.id != null) {
        if (byId.has(Number(county.id))) throw new Error(`Duplicate county id ${county.id}`);
        byId.set(Number(county.id), county);
      }
    }
  }
  return byId;
}

/** Canonical countries or states: a missing, malformed, non-array or duplicate-id file fails, never falls back to exports. */
function loadCanonical(entity) {
  const file = path.join(process.cwd(), 'contributions', entity, `${entity}.json`);
  const { data, error } = fs.existsSync(file) ? parseJsonFile(file) : { error: 'missing' };
  if (error || !Array.isArray(data)) throw new Error(`Cannot load contributions/${entity}/${entity}.json: ${error || 'expected an array'}`);
  const ids = new Set();
  for (const r of data) {
    if (ids.has(Number(r.id))) throw new Error(`Duplicate ${entity} id ${r.id}`);
    ids.add(Number(r.id));
  }
  return data;
}

/** Check the reference inventory itself: a wrong country or state record must not decide which countries have states. */
function checkInventory(countries, states) {
  const problems = [];
  const byId = new Map();
  const codes = new Set();
  for (const c of countries) {
    if (!c || !Number.isInteger(c.id) || c.id <= 0 || typeof c.iso2 !== 'string' || !/^[A-Z]{2}$/.test(c.iso2)) {
      problems.push(`country ${JSON.stringify(c && c.id)} needs a positive integer id and a two-letter iso2`);
    } else if (codes.has(c.iso2)) {
      problems.push(`country iso2 ${c.iso2} is duplicated`);
    } else {
      byId.set(c.id, c);
      codes.add(c.iso2);
    }
  }
  for (const s of states) {
    const country = s && byId.get(s.country_id);
    if (!s || !Number.isInteger(s.id) || s.id <= 0) problems.push(`state ${JSON.stringify(s && s.id)} needs a positive integer id`);
    else if (!country) problems.push(`state ${s.id}: country_id ${JSON.stringify(s.country_id)} is not a known country`);
    else if (s.country_code !== country.iso2) problems.push(`state ${s.id}: country_code ${JSON.stringify(s.country_code)} is not ${country.iso2}`);
    else if (typeof s.iso2 !== 'string' || !s.iso2) problems.push(`state ${s.id} has no state code (iso2)`);
  }
  if (problems.length) throw new Error(`Invalid reference data: ${problems.slice(0, 10).join('; ')}`);
}

/** Every canonical city across country files, by id (loaded once, only when a parent link needs checking). */
let allCities = null;
function loadAllCities() {
  if (allCities) return allCities;
  allCities = new Map();
  const dir = path.join(process.cwd(), 'contributions', 'cities');
  for (const file of fs.readdirSync(dir).filter(f => /^[A-Z]{2}\.json$/.test(f)).sort()) {
    const { data, error } = parseJsonFile(path.join(dir, file));
    if (error || !Array.isArray(data)) throw new Error(`Cannot load cities/${file}: ${error || 'expected an array'}`);
    for (const c of data) {
      if (c.id == null) continue;   // a new city gets its id on import
      if (!Number.isInteger(c.id) || c.id <= 0) throw new Error(`cities/${file}: id ${JSON.stringify(c.id)} is not a positive integer`);
      if (allCities.has(c.id)) throw new Error(`city id ${c.id} is in both ${allCities.get(c.id).__file} and cities/${file}`);
      allCities.set(c.id, Object.defineProperty({ ...c }, '__file', { value: `cities/${file}` }));
    }
  }
  return allCities;
}

/**
 * Why an indexed city cannot be trusted as a parent, or null: its country id and code must name one country, it must sit
 * in that country's file, and its state pair must name a state of that country by its iso2 (both null only when the
 * country has no states). ref holds countryById, stateById and countriesWithStates from the checked inventory.
 */
function parentRecordProblem(p, ref) {
  const country = Number.isInteger(p.country_id) ? ref.countryById.get(p.country_id) : undefined;
  if (!country || p.country_code !== country.iso2) {
    return `its country_id ${JSON.stringify(p.country_id)} and country_code ${JSON.stringify(p.country_code)} do not name one country`;
  }
  if (p.__file !== `cities/${country.iso2}.json`) return `it is filed in ${p.__file}, not cities/${country.iso2}.json`;
  if (p.state_id === null && p.state_code === null) {
    return ref.countriesWithStates.has(country.id) ? `it has no state, but ${country.iso2} has states` : null;
  }
  const state = Number.isInteger(p.state_id) ? ref.stateById.get(p.state_id) : undefined;
  if (!state || Number(state.country_id) !== country.id || p.state_code !== state.iso2) {
    return `its state_id ${JSON.stringify(p.state_id)} and state_code ${JSON.stringify(p.state_code)} do not name a state of ${country.iso2}`;
  }
  return null;
}

/** A city's parent must exist, be a valid record itself, not be the city, share its country and state (null state
 * included) and not loop. */
function validateCityParent(record, cities, ref) {
  if (record.parent_id == null) return [];
  if (!Number.isInteger(record.parent_id) || record.parent_id <= 0) return ['parent_id must be a positive integer'];
  if (record.id != null && record.parent_id === Number(record.id)) return ['parent_id points to the city itself'];
  const parent = cities.get(record.parent_id);
  if (!parent) return [`parent_id ${record.parent_id} does not exist in contributions/cities`];
  const bad = parentRecordProblem(parent, ref);
  if (bad) return [`parent_id ${record.parent_id} cannot be checked: ${bad}`];
  const errors = [];
  if (parent.country_id !== record.country_id || parent.country_code !== record.country_code) {
    errors.push(`parent_id ${record.parent_id} is in country ${parent.country_code} (${parent.country_id}), not ${record.country_code} (${record.country_id})`);
  }
  if ((parent.state_id ?? null) !== (record.state_id ?? null)) {
    errors.push(`parent_id ${record.parent_id} is in state ${parent.state_id ?? 'none'}, not ${record.state_id ?? 'none'}`);
  }
  const seen = new Set([Number(record.id)]);
  for (let p = parent; p && p.parent_id != null; p = cities.get(p.parent_id)) {
    if (seen.has(Number(p.id))) { errors.push(`parent_id ${record.parent_id} leads to a loop`); break; }
    seen.add(Number(p.id));
  }
  return errors;
}

/** Check that a city's optional county belongs to its declared state (or lists it, v5) and country. */
function validateCountyReference(record, counties) {
  if (record.county_id == null) return [];
  if (!Number.isInteger(record.county_id) || record.county_id <= 0) {
    return ['county_id must be a positive integer'];
  }
  const county = counties.get(record.county_id);
  if (!county) return [`county_id ${record.county_id} does not exist in contributions/counties`];
  const errors = [];
  if (county.state_id == null && Array.isArray(county.states)) {
    // a county of several regions (v5): the city's state must be one of them
    const ids = county.states.map((s) => Number(s && s.state_id));
    if (!ids.includes(Number(record.state_id))) {
      errors.push(`county_id ${record.county_id} lists states ${ids.join(', ')}, not ${record.state_id}`);
    }
  } else if (Number(county.state_id) !== Number(record.state_id)) {
    errors.push(`county_id ${record.county_id} belongs to state_id ${county.state_id}, not ${record.state_id}`);
  }
  if (Number(county.country_id) !== Number(record.country_id) ||
      county.country_code !== record.country_code) {
    errors.push(`county_id ${record.county_id} belongs to country ${county.country_code} (${county.country_id}), not ${record.country_code} (${record.country_id})`);
  }
  return errors;
}

async function run() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = github.getOctokit(token);
  const { pull_request: pr } = github.context.payload;

  if (!pr) {
    core.setFailed('This script must run on a pull_request event.');
    return;
  }

  // Load reference data
  // Canonical reference data only; a missing or malformed file fails the run (never a silent skip or stale export)
  const countries = loadCanonical('countries');
  const states = loadCanonical('states');
  checkInventory(countries, states);
  const counties = loadCounties();

  if (!countries) {
    core.warning('Could not load countries.json for cross-reference. Skipping.');
    core.setOutput('errors', JSON.stringify([]));
    core.setOutput('error_count', '0');
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
  const countriesWithStates = new Set(states.map((s) => Number(s.country_id)));
  const ref = { countryById, stateById, countriesWithStates };

  // Get changed files
  const files = await listChangedFiles(octokit, github.context, pr);

  const contributionFiles = files.filter(
    (f) =>
      f.filename.startsWith('contributions/') &&
      f.filename.endsWith('.json') &&
      f.status !== 'removed'
  );

  // County edits/removals can break unchanged cities and county children.
  // County, state or country edits/removals can break unchanged cities (county links, null-state eligibility).
  if (files.some(f => /^contributions\/(counties|states|countries)\//.test(f.filename) && f.filename.endsWith('.json'))) {
    const included = new Set(contributionFiles.map(f => f.filename));
    for (const entity of ['cities', 'counties']) {
      const dir = path.join(process.cwd(), 'contributions', entity);
      if (!fs.existsSync(dir)) continue;
      for (const name of fs.readdirSync(dir).filter(f => /^[A-Z]{2}\.json$/.test(f)).sort()) {
        const filename = `contributions/${entity}/${name}`;
        if (!included.has(filename)) contributionFiles.push({ filename });
      }
    }
  }

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

      if (entityType === 'cities' && record.parent_id != null) {
        errors.push(...validateCityParent(record, loadAllCities(), ref).map(error => `${prefix}: ${error}`));
      }

      if (entityType === 'cities') {
        const countyErrors = validateCountyReference(record, counties);
        errors.push(...countyErrors.map(error => `${prefix}: ${error}`));
        if (record.county_id != null && countyErrors.length === 0) validCount++;
      }

      // Every scanned county, changed or not, gets the whole shape check (v5, decision B6)
      if (entityType === 'counties') errors.push(...countyShapeErrors(record, prefix));

      // A county of several regions (v5): each listed region is a state of the county's country, by its own code
      if (entityType === 'counties' && Array.isArray(record.states)) {
        for (const entry of record.states) {
          const id = entry && entry.state_id;
          const state = stateById.get(Number(id));
          if (!state) {
            errors.push(`${prefix}: states entry ${id} does not exist`);
          } else if (Number(state.country_id) !== Number(record.country_id)) {
            errors.push(`${prefix}: states entry ${id} ("${state.name}") belongs to country_id ${state.country_id}, not ${record.country_id}`);
          } else if (entry.state_code !== state.iso2) {
            errors.push(`${prefix}: states entry ${id}: state_code ${JSON.stringify(entry.state_code)} does not match (expected "${state.iso2}")`);
          } else {
            validCount++;
          }
        }
      }

      if (entityType === 'counties' && record.parent_id != null) {
        if (record.id == null) {
          errors.push(`${prefix}: counties with parent_id must have an explicit id`);
        }
        if (!Number.isInteger(record.parent_id) || record.parent_id <= 0) {
          errors.push(`${prefix}: parent_id must be a positive integer`);
        } else if (!counties.has(record.parent_id)) {
          errors.push(`${prefix}: parent_id ${record.parent_id} does not exist in contributions/counties`);
        }
      }

      if (entityType === 'cities' || entityType === 'counties') {
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

        // A city with no state (v5): allowed only when its country has no states at all (e.g. Western Sahara), so a
        // missing state is never a shortcut for an unresolved one
        if (entityType === 'cities' && record.state_id === null && states) {
          if (countriesWithStates.has(Number(record.country_id))) {
            errors.push(`${prefix}: state_id is null but country ${record.country_code} has states; set the state`);
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
            // The code must be the state's own iso2, always (canonical states have no separate state_code)
            if (record.state_code !== state.iso2) {
              errors.push(
                `${prefix}: state_code ${JSON.stringify(record.state_code)} does not match state_id ${record.state_id} (expected "${state.iso2}")`
              );
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

        // Validate city_id exists if provided (optional FK)
        if (record.city_id != null && record.country_id) {
          const country = countryById.get(Number(record.country_id));
          if (country && country.iso2) {
            const cities = loadCitiesForCountry(country.iso2);
            if (cities) {
              const city = cities.find((c) => Number(c.id) === Number(record.city_id));
              if (!city) {
                errors.push(
                  `${prefix}: city_id ${record.city_id} does not exist in cities/${country.iso2}.json`
                );
              } else {
                validCount++;
                if (Number(city.country_id) !== Number(record.country_id)) {
                  errors.push(
                    `${prefix}: city_id ${record.city_id} ("${city.name}") belongs to country_id ${city.country_id}, not ${record.country_id}`
                  );
                }
                if (record.state_id != null && Number(city.state_id) !== Number(record.state_id)) {
                  errors.push(
                    `${prefix}: city_id ${record.city_id} ("${city.name}") belongs to state_id ${city.state_id}, not declared state_id ${record.state_id}`
                  );
                }
              }
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

  // Cap the emitted list (env-var size limit in the report step); emit the
  // true total separately. has_errors reflects the full count.
  core.setOutput('errors', JSON.stringify(errors.slice(0, 50)));
  core.setOutput('error_count', errors.length.toString());
  core.setOutput('valid', validCount.toString());
  core.setOutput('has_errors', (errors.length > 0).toString());

  core.info(`Cross-reference: ${validCount} valid, ${errors.length} errors`);
  for (const err of errors) core.error(err);
}

/** Run the check; a failure that stops it is reported as one error, so the report can never read "All checks passed". */
async function main() {
  try {
    await run();
  } catch (err) {
    core.setOutput('errors', JSON.stringify([`The cross-reference check could not run: ${err.message}`]));
    core.setOutput('error_count', '1');
    core.setOutput('valid', '0');
    core.setOutput('has_errors', 'true');
    core.setFailed(err.message);
  }
}

if (require.main === module) main();

module.exports = { loadCounties, validateCountyReference, validateCityParent, parentRecordProblem, loadCanonical, checkInventory };
