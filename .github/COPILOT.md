# GitHub Copilot Workspace Instructions

This document provides guidance for GitHub Copilot when working with data contributions in this repository.

## Quick Reference for Data Contributions

When adding or modifying geographical data (regions, subregions, countries, states, or cities), follow this workflow:

### 1. Edit JSON Files

**Location**: `contributions/` directory
- Regions: `contributions/regions/regions.json`
- Subregions: `contributions/subregions/subregions.json`
- Countries: `contributions/countries/countries.json`
- States: `contributions/states/states.json`
- Cities: `contributions/cities/<COUNTRY_CODE>.json` (e.g., `US.json`, `IN.json`)

### 2. Field Guidelines

**For NEW records** (without existing ID):
```json
{
  "name": "New York",
  "state_id": 1452,
  "state_code": "NY",
  "country_id": 233,
  "country_code": "US",
  "latitude": "40.71277530",
  "longitude": "-74.00597280"
}
```

**OMIT these fields** - they are auto-managed:
- `id` - Auto-assigned by MySQL AUTO_INCREMENT
- `created_at` - Auto-filled by MySQL (default: `2014-01-01 06:31:01` for cities, NULL for others)
- `updated_at` - Auto-filled by MySQL (default: `CURRENT_TIMESTAMP`)
- `flag` - Auto-filled by MySQL (default: `1`)

**For EXISTING records** (with ID):
```json
{
  "id": 123,
  "name": "Updated City Name",
  "state_id": 1452,
  ...
}
```

Keep the `id` field unchanged when updating existing records.

### 3. Auto-Normalize JSON (Optional but Recommended)

After editing JSON files, run the normalizer to auto-assign IDs and timestamps:

```bash
# Normalize a single file
python3 bin/scripts/sync/normalize_json.py contributions/cities/US.json

# Normalize multiple files
python3 bin/scripts/sync/normalize_json.py contributions/cities/*.json

# Normalize states
python3 bin/scripts/sync/normalize_json.py contributions/states/states.json
```

**What the normalizer does**:
1. Connects to MySQL to get the next available ID
2. Auto-assigns sequential IDs to records without `id`
3. Adds `created_at` timestamp (ISO 8601 format) if missing
4. Adds `updated_at` timestamp (ISO 8601 format) if missing
5. Updates JSON file in place

### 4. Verify Changes

```bash
# Review what changed
git diff contributions/

# Test import locally (optional)
python3 bin/scripts/sync/import_json_to_mysql.py
```

### 5. Commit and Push

```bash
git add contributions/
git commit -m "feat: add new cities to US"
git push
```

GitHub Actions will automatically:
1. Import JSON to MySQL (IDs auto-assigned if not present)
2. Export all formats (JSON, CSV, XML, YAML, SQL, etc.)
3. Create a pull request with the exports

## Common Tasks for Copilot

### Task: Add New Cities

1. **Find the country file**: `contributions/cities/<COUNTRY_CODE>.json`
2. **Add new city objects** at the end of the array
3. **Required fields**:
   - `name` (string)
   - `state_id` (integer) - look up in `contributions/states/states.json`
   - `state_code` (string) - look up in `contributions/states/states.json`
   - `country_id` (integer) - look up in `contributions/countries/countries.json`
   - `country_code` (string, 2 chars) - look up in `contributions/countries/countries.json`
   - `latitude` (string, decimal format)
   - `longitude` (string, decimal format)
4. **Optional fields**:
   - `native` (native name)
   - `timezone` (IANA timezone, e.g., "America/New_York")
   - `wikiDataId` (WikiData identifier)
5. **Run normalizer** (optional): `python3 bin/scripts/sync/normalize_json.py contributions/cities/<COUNTRY_CODE>.json`

### Task: Add New States

1. **Edit**: `contributions/states/states.json`
2. **Required fields**:
   - `name` (string)
   - `country_id` (integer) - look up in `contributions/countries/countries.json`
   - `country_code` (string, 2 chars)
3. **Optional fields**:
   - `fips_code`, `iso2`, `iso3166_2`
   - `type` (e.g., "state", "province", "territory")
   - `level`, `parent_id`
   - `native`, `latitude`, `longitude`
   - `timezone`, `wikiDataId`, `population`
4. **Run normalizer** (optional): `python3 bin/scripts/sync/normalize_json.py contributions/states/states.json`

### Task: Update Existing Records

1. **Find the record** by searching for its `id` or `name`
2. **Keep the `id` field** unchanged
3. **Modify** only the fields that need updating
4. **Commit** with descriptive message: `fix: correct timezone for New York`

## Important Rules

1. **NEVER** edit files in these directories (they are auto-generated):
   - `json/`
   - `csv/`
   - `xml/`
   - `yml/`
   - `sql/`
   - `sqlite/`
   - `duckdb/`
   - `sqlserver/`
   - `mongodb/`
   - `psql/`

2. **ALWAYS** edit files in `contributions/` directory only

3. **DO NOT** manually assign IDs unless you know the next available ID
   - Let MySQL AUTO_INCREMENT handle it, or
   - Use the `normalize_json.py` script

4. **DO NOT** add `flag`, `created_at`, or `updated_at` fields
   - MySQL handles these automatically with DEFAULT values

5. **VERIFY** foreign key relationships:
   - Cities must reference valid `state_id` and `country_id`
   - States must reference valid `country_id`
   - Countries must reference valid `region_id` and `subregion_id` (if applicable)

## Schema Reference

### Cities Schema
```json
{
  "id": 123,                    // OMIT for new records (auto-assigned)
  "name": "City Name",          // REQUIRED
  "state_id": 456,              // REQUIRED (FK to states)
  "state_code": "CA",           // REQUIRED
  "country_id": 789,            // REQUIRED (FK to countries)
  "country_code": "US",         // REQUIRED (2 chars)
  "latitude": "34.05223000",    // REQUIRED (string decimal)
  "longitude": "-118.24368000", // REQUIRED (string decimal)
  "native": "Native Name",      // optional
  "timezone": "America/Los_Angeles", // optional (IANA format)
  "translations": {...},        // optional (JSON object)
  "wikiDataId": "Q65",          // optional
  "created_at": "2024-10-16T12:00:00", // OMIT (auto-managed)
  "updated_at": "2024-10-16T12:00:00", // OMIT (auto-managed)
  "flag": 1                     // OMIT (auto-managed)
}
```

### States Schema
```json
{
  "id": 123,                    // OMIT for new records
  "name": "California",         // REQUIRED
  "country_id": 233,            // REQUIRED (FK to countries)
  "country_code": "US",         // REQUIRED
  "fips_code": "06",            // optional
  "iso2": "CA",                 // optional
  "iso3166_2": "US-CA",         // optional
  "type": "state",              // optional
  "level": 1,                   // optional
  "parent_id": null,            // optional
  "native": "California",       // optional
  "latitude": "36.77826100",    // optional
  "longitude": "-119.41793240", // optional
  "timezone": "America/Los_Angeles", // optional
  "translations": {...},        // optional
  "wikiDataId": "Q99",          // optional
  "population": "39538223",     // optional (string)
  "created_at": null,           // OMIT (auto-managed)
  "updated_at": "2024-10-16T12:00:00", // OMIT (auto-managed)
  "flag": 1                     // OMIT (auto-managed)
}
```

## Finding Reference IDs

To find the correct `state_id`, `country_id`, or other foreign keys:

```bash
# Find state ID
grep -A 5 '"name": "California"' contributions/states/states.json

# Find country ID
grep -A 5 '"name": "United States"' contributions/countries/countries.json

# Find all states for a country
jq '.[] | select(.country_code == "US") | {id, name}' contributions/states/states.json
```

## Testing Locally

Before pushing, you can test the import:

```bash
# Start MySQL (if not running)
sudo systemctl start mysql.service

# Import to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py

# Verify import
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"

# Run exports (optional)
cd bin
php console export:json
```

## Questions?

- Check `.claude/CLAUDE.md` for detailed repository documentation
- Review `bin/scripts/sync/README.md` for script documentation (if exists)
- See `bin/README.md` for export command documentation
