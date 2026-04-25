/**
 * Shared utility functions for CSC automation scripts.
 * Used across all validation and analysis scripts.
 */

const fs = require('fs');
const path = require('path');

// Fields that are auto-managed and must NOT be present in contributions
const AUTO_MANAGED_FIELDS = ['id', 'created_at', 'updated_at', 'flag'];

// Schema definitions derived from schema.sql
const SCHEMA = {
  cities: {
    required: ['name', 'state_id', 'state_code', 'country_id', 'country_code', 'latitude', 'longitude'],
    optional: ['state_name', 'country_name', 'wikiDataId', 'timezone'],
    rules: {
      name: { type: 'string', maxLength: 255, nonEmpty: true },
      state_id: { type: 'integer', positive: true },
      state_code: { type: 'string', maxLength: 255, nonEmpty: true },
      country_id: { type: 'integer', positive: true },
      country_code: { type: 'string', exactLength: 2 },
      latitude: { type: 'coordinate', min: -90, max: 90 },
      longitude: { type: 'coordinate', min: -180, max: 180 },
      wikiDataId: { type: 'string', pattern: /^Q\d+$/ },
    },
  },
  states: {
    required: ['name', 'country_id', 'country_code'],
    optional: ['fips_code', 'iso2', 'type', 'level', 'parent_id', 'native', 'latitude', 'longitude', 'country_name', 'state_code', 'wikiDataId'],
    rules: {
      name: { type: 'string', maxLength: 255, nonEmpty: true },
      country_id: { type: 'integer', positive: true },
      country_code: { type: 'string', exactLength: 2 },
      iso2: { type: 'string', maxLength: 255 },
      type: { type: 'string', maxLength: 191 },
      latitude: { type: 'coordinate', min: -90, max: 90 },
      longitude: { type: 'coordinate', min: -180, max: 180 },
      wikiDataId: { type: 'string', pattern: /^Q\d+$/ },
    },
  },
  countries: {
    required: ['name'],
    optional: [
      'iso3', 'numeric_code', 'iso2', 'phonecode', 'capital', 'currency',
      'currency_name', 'currency_symbol', 'tld', 'native', 'region',
      'region_id', 'subregion', 'subregion_id', 'nationality', 'timezones',
      'translations', 'latitude', 'longitude', 'emoji', 'emojiU', 'wikiDataId',
    ],
    rules: {
      name: { type: 'string', maxLength: 100, nonEmpty: true },
      iso2: { type: 'string', exactLength: 2 },
      iso3: { type: 'string', exactLength: 3 },
      numeric_code: { type: 'string', exactLength: 3 },
      latitude: { type: 'coordinate', min: -90, max: 90 },
      longitude: { type: 'coordinate', min: -180, max: 180 },
      wikiDataId: { type: 'string', pattern: /^Q\d+$/ },
    },
  },
  postcodes: {
    required: ['code', 'country_id', 'country_code'],
    optional: [
      'state_id', 'state_code', 'city_id', 'locality_name', 'type',
      'latitude', 'longitude', 'source', 'wikiDataId',
    ],
    rules: {
      code: { type: 'string', maxLength: 20, nonEmpty: true },
      country_id: { type: 'integer', positive: true },
      country_code: { type: 'string', exactLength: 2 },
      state_id: { type: 'integer', positive: true },
      state_code: { type: 'string', maxLength: 255 },
      city_id: { type: 'integer', positive: true },
      locality_name: { type: 'string', maxLength: 255 },
      type: { type: 'string', maxLength: 32 },
      latitude: { type: 'coordinate', min: -90, max: 90 },
      longitude: { type: 'coordinate', min: -180, max: 180 },
      source: { type: 'string', maxLength: 64 },
      wikiDataId: { type: 'string', pattern: /^Q\d+$/ },
    },
  },
};

/**
 * Determine entity type from file path.
 * @param {string} filePath - Path to the changed file
 * @returns {string|null} - 'cities', 'states', 'countries', or null
 */
function getEntityType(filePath) {
  const normalized = filePath.toLowerCase();
  if (normalized.includes('postcodes')) return 'postcodes';
  if (normalized.includes('cities')) return 'cities';
  if (normalized.includes('states')) return 'states';
  if (normalized.includes('countries')) return 'countries';
  return null;
}

/**
 * Parse JSON file safely with error reporting.
 * @param {string} filePath - Path to the JSON file
 * @returns {{ data: any, error: string|null }}
 */
function parseJsonFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    // Check for BOM
    const cleanContent = content.replace(/^\uFEFF/, '');
    const data = JSON.parse(cleanContent);
    return { data, error: null };
  } catch (err) {
    return { data: null, error: `Invalid JSON: ${err.message}` };
  }
}

/**
 * Validate a single field value against its schema rule.
 * @param {string} fieldName - Name of the field
 * @param {any} value - Value to validate
 * @param {object} rule - Validation rule from SCHEMA
 * @returns {string|null} - Error message or null if valid
 */
function validateField(fieldName, value, rule) {
  if (!rule) return null;

  if (rule.type === 'string') {
    if (typeof value !== 'string') return `"${fieldName}" must be a string, got ${typeof value}`;
    if (rule.nonEmpty && value.trim().length === 0) return `"${fieldName}" must not be empty`;
    if (rule.exactLength && value.length !== rule.exactLength) {
      return `"${fieldName}" must be exactly ${rule.exactLength} characters, got ${value.length} ("${value}")`;
    }
    if (rule.maxLength && value.length > rule.maxLength) {
      return `"${fieldName}" exceeds max length of ${rule.maxLength} characters`;
    }
    if (rule.pattern && !rule.pattern.test(value)) {
      return `"${fieldName}" format is invalid ("${value}")`;
    }
  }

  if (rule.type === 'integer') {
    const num = Number(value);
    if (!Number.isInteger(num)) return `"${fieldName}" must be an integer, got "${value}"`;
    if (rule.positive && num <= 0) return `"${fieldName}" must be positive, got ${num}`;
  }

  if (rule.type === 'coordinate') {
    const num = parseFloat(value);
    if (isNaN(num)) return `"${fieldName}" must be a number, got "${value}"`;
    if (num < rule.min || num > rule.max) {
      return `"${fieldName}" must be between ${rule.min} and ${rule.max}, got ${num}`;
    }
  }

  return null;
}

/**
 * Validate a single record against its entity schema.
 * @param {object} record - The data record to validate
 * @param {string} entityType - 'cities', 'states', or 'countries'
 * @param {number} index - Record index for error reporting
 * @returns {{ errors: string[], warnings: string[] }}
 */
function validateRecord(record, entityType, index) {
  const schema = SCHEMA[entityType];
  if (!schema) return { errors: [`Unknown entity type: ${entityType}`], warnings: [] };

  const errors = [];
  const warnings = [];
  const label = record.name || record.code;
  const prefix = `Record ${index + 1}${label ? ` ("${label}")` : ''}`;

  // Check for auto-managed fields that should NOT be present
  for (const field of AUTO_MANAGED_FIELDS) {
    if (field in record) {
      errors.push(`${prefix}: "${field}" must not be included (auto-managed)`);
    }
  }

  // Check required fields
  for (const field of schema.required) {
    if (!(field in record) || record[field] === null || record[field] === undefined) {
      errors.push(`${prefix}: missing required field "${field}"`);
    } else {
      const rule = schema.rules[field];
      if (rule) {
        const fieldError = validateField(field, record[field], rule);
        if (fieldError) errors.push(`${prefix}: ${fieldError}`);
      }
    }
  }

  // Validate optional fields that are present
  for (const field of schema.optional) {
    if (field in record && record[field] !== null && record[field] !== undefined) {
      const rule = schema.rules[field];
      if (rule) {
        const fieldError = validateField(field, record[field], rule);
        if (fieldError) warnings.push(`${prefix}: ${fieldError}`);
      }
    }
  }

  // Check for unknown fields
  const allKnown = [...schema.required, ...schema.optional, ...AUTO_MANAGED_FIELDS];
  for (const field of Object.keys(record)) {
    if (!allKnown.includes(field)) {
      warnings.push(`${prefix}: unknown field "${field}"`);
    }
  }

  return { errors, warnings };
}

/**
 * Calculate Haversine distance between two coordinates in km.
 * @param {number} lat1 - Latitude of point 1
 * @param {number} lon1 - Longitude of point 1
 * @param {number} lat2 - Latitude of point 2
 * @param {number} lon2 - Longitude of point 2
 * @returns {number} - Distance in kilometres
 */
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Calculate Levenshtein distance between two strings.
 * @param {string} a - First string
 * @param {string} b - Second string
 * @returns {number} - Edit distance
 */
function levenshteinDistance(a, b) {
  const matrix = [];
  const aLower = a.toLowerCase();
  const bLower = b.toLowerCase();

  for (let i = 0; i <= bLower.length; i++) matrix[i] = [i];
  for (let j = 0; j <= aLower.length; j++) matrix[0][j] = j;

  for (let i = 1; i <= bLower.length; i++) {
    for (let j = 1; j <= aLower.length; j++) {
      if (bLower.charAt(i - 1) === aLower.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[bLower.length][aLower.length];
}

/**
 * Load a JSON data file from the repository.
 * Tries multiple common paths.
 * @param {string} entityType - 'cities', 'states', or 'countries'
 * @returns {Array|null}
 */
function loadRepoData(entityType) {
  const possiblePaths = [
    path.join(process.cwd(), 'contributions', entityType, `${entityType}.json`),
    path.join(process.cwd(), `json`, `${entityType}.json`),
    path.join(process.cwd(), `${entityType}.json`),
    path.join(process.cwd(), `data`, `${entityType}.json`),
  ];

  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      try {
        return JSON.parse(fs.readFileSync(p, 'utf8'));
      } catch {
        continue;
      }
    }
  }

  return null;
}

/**
 * Format a validation report as a GitHub markdown comment.
 * @param {object} results - Validation results object
 * @returns {string} - Formatted markdown
 */
function formatReport(results) {
  const {
    prFormat = {},
    schemaValidation = {},
    crossReference = {},
    coordinateBounds = {},
    duplicateCheck = {},
    sourceUrls = {},
    labels = [],
    summary = {},
  } = results;

  let report = '## CSC Validation Report\n\n';

  // PR Format
  if (Object.keys(prFormat).length > 0) {
    report += '### PR Format\n';
    for (const [check, result] of Object.entries(prFormat)) {
      const icon = result.pass ? ':white_check_mark:' : ':x:';
      report += `- ${icon} ${result.label}\n`;
    }
    report += '\n';
  }

  // Labels
  if (labels.length > 0) {
    report += `### Labels Applied\n`;
    report += labels.map((l) => `\`${l}\``).join(', ') + '\n\n';
  }

  // Schema Validation
  if (schemaValidation.errors?.length > 0 || schemaValidation.warnings?.length > 0) {
    const errorCount = schemaValidation.errors?.length || 0;
    const warnCount = schemaValidation.warnings?.length || 0;
    report += `### Schema Validation (${errorCount} errors, ${warnCount} warnings)\n`;

    if (schemaValidation.errors?.length > 0) {
      report += '\n**Errors (blocking):**\n';
      for (const err of schemaValidation.errors.slice(0, 20)) {
        report += `- :x: ${err}\n`;
      }
      if (schemaValidation.errors.length > 20) {
        report += `- ... and ${schemaValidation.errors.length - 20} more errors\n`;
      }
    }

    if (schemaValidation.warnings?.length > 0) {
      report += '\n**Warnings:**\n';
      for (const warn of schemaValidation.warnings.slice(0, 10)) {
        report += `- :warning: ${warn}\n`;
      }
      if (schemaValidation.warnings.length > 10) {
        report += `- ... and ${schemaValidation.warnings.length - 10} more warnings\n`;
      }
    }
    report += '\n';
  } else if (schemaValidation.recordCount > 0) {
    report += `### Schema Validation\n`;
    report += `:white_check_mark: All ${schemaValidation.recordCount} records passed validation\n\n`;
  }

  // Cross-Reference
  if (crossReference.errors?.length > 0 || crossReference.valid > 0) {
    report += '### Cross-Reference Validation\n';
    if (crossReference.valid > 0) {
      report += `:white_check_mark: ${crossReference.valid} references verified\n`;
    }
    if (crossReference.errors?.length > 0) {
      for (const err of crossReference.errors.slice(0, 10)) {
        report += `- :x: ${err}\n`;
      }
    }
    report += '\n';
  }

  // Coordinate Bounds
  if (coordinateBounds.warnings?.length > 0) {
    report += '### Geo-Bounds Check\n';
    for (const warn of coordinateBounds.warnings.slice(0, 10)) {
      report += `- :warning: ${warn}\n`;
    }
    report += '\n';
  } else if (coordinateBounds.checked > 0) {
    report += `### Geo-Bounds Check\n`;
    report += `:white_check_mark: All ${coordinateBounds.checked} coordinates within expected country bounds\n\n`;
  }

  // Duplicate Check
  if (duplicateCheck.warnings?.length > 0) {
    report += '### Duplicate Detection\n';
    for (const warn of duplicateCheck.warnings.slice(0, 10)) {
      report += `- :warning: ${warn}\n`;
    }
    report += '\n';
  } else if (duplicateCheck.checked > 0) {
    report += `### Duplicate Detection\n`;
    report += `:white_check_mark: No duplicates found among ${duplicateCheck.checked} records\n\n`;
  }

  // Source URLs
  if (sourceUrls.errors?.length > 0 || sourceUrls.valid > 0) {
    report += '### Source URL Verification\n';
    if (sourceUrls.valid > 0) {
      report += `:white_check_mark: ${sourceUrls.valid} source URL(s) accessible\n`;
    }
    if (sourceUrls.errors?.length > 0) {
      for (const err of sourceUrls.errors) {
        report += `- :warning: ${err}\n`;
      }
    }
    report += '\n';
  }

  // Summary
  report += '---\n';
  const totalErrors = summary.errors || 0;
  const totalWarnings = summary.warnings || 0;

  if (totalErrors === 0 && totalWarnings === 0) {
    report += ':white_check_mark: **All checks passed** | Status: Ready for review\n';
  } else if (totalErrors === 0) {
    report += `:white_check_mark: **0 errors, ${totalWarnings} warning(s)** | Status: Ready for review (with warnings)\n`;
  } else {
    report += `:x: **${totalErrors} error(s), ${totalWarnings} warning(s)** | Status: Changes required\n`;
  }

  return report;
}

module.exports = {
  AUTO_MANAGED_FIELDS,
  SCHEMA,
  getEntityType,
  parseJsonFile,
  validateField,
  validateRecord,
  haversineDistance,
  levenshteinDistance,
  loadRepoData,
  formatReport,
};
