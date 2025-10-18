# Countries States Cities — GitHub Copilot Guide

This repository is a comprehensive geographical database with a bidirectional JSON ↔ MySQL workflow. Contributors edit `contributions/` JSON files, and exports are generated via PHP console commands from MySQL.

## Quick Overview

- **Source**: `contributions/` (cities/*.json, states/states.json, countries/countries.json)
- **Canonical SQL**: `sql/world.sql` (151k+ cities, 5k+ states, 250 countries)
- **Export tooling**: `bin/` (PHP console + Python sync scripts)

## Primary Workflows

### JSON-First (Recommended for Contributors)

1. Edit `contributions/` JSON files (omit `id` for new records)
2. Commit & push — GitHub Actions imports JSON → MySQL and runs exports

### SQL-First (Maintainers Only)

1. Modify MySQL directly or import `sql/world.sql`
2. Run `python3 bin/scripts/sync/sync_mysql_to_json.py` to sync MySQL → JSON
3. Commit the JSON changes

## Adding/Editing Data

### Location of JSON Files

- Regions: `contributions/regions/regions.json`
- Subregions: `contributions/subregions/subregions.json`
- Countries: `contributions/countries/countries.json`
- States: `contributions/states/states.json`
- Cities: `contributions/cities/<COUNTRY_CODE>.json` (e.g., `US.json`, `IN.json`)

### Field Guidelines

**For NEW records** (omit `id`):
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

**OMIT these fields** - auto-managed by MySQL:
- `id` - Auto-assigned by AUTO_INCREMENT
- `created_at` - Auto-filled by MySQL
- `updated_at` - Auto-filled by MySQL
- `flag` - Auto-filled by MySQL (default: 1)

**For EXISTING records** (keep `id` unchanged):
```json
{
  "id": 123,
  "name": "Updated City Name",
  "state_id": 1452,
  ...
}
```

### Auto-Normalize JSON (Optional)

After editing JSON files, you can run the normalizer to auto-assign IDs and timestamps:

```bash
# Normalize a single file
python3 bin/scripts/sync/normalize_json.py contributions/cities/US.json

# Normalize multiple files
python3 bin/scripts/sync/normalize_json.py contributions/cities/*.json

# Normalize states
python3 bin/scripts/sync/normalize_json.py contributions/states/states.json
```

**What it does**:
1. Connects to MySQL to get the next available ID
2. Auto-assigns sequential IDs to records without `id`
3. Adds `created_at` and `updated_at` timestamps (ISO 8601 format)
4. Updates JSON file in place

## Common Tasks

### Add New Cities

1. Find the country file: `contributions/cities/<COUNTRY_CODE>.json`
2. Add new city objects at the end of the array
3. **Required fields**:
   - `name` (string)
   - `state_id` (integer) - look up in `contributions/states/states.json`
   - `state_code` (string)
   - `country_id` (integer) - look up in `contributions/countries/countries.json`
   - `country_code` (string, 2 chars)
   - `latitude` (string, decimal format)
   - `longitude` (string, decimal format)
4. **Optional fields**:
   - `native`, `timezone`, `wikiDataId`
5. Run normalizer (optional): `python3 bin/scripts/sync/normalize_json.py contributions/cities/<COUNTRY_CODE>.json`

### Add New States

1. Edit: `contributions/states/states.json`
2. **Required fields**: `name`, `country_id`, `country_code`
3. **Optional fields**: `fips_code`, `iso2`, `type`, `latitude`, `longitude`, `timezone`, `wikiDataId`
4. Run normalizer (optional): `python3 bin/scripts/sync/normalize_json.py contributions/states/states.json`

### Update Existing Records

1. Find the record by searching for its `id` or `name`
2. Keep the `id` field unchanged
3. Modify only the fields that need updating
4. Commit with descriptive message: `fix: correct timezone for New York`

## Schema Reference

### Cities Schema
```json
{
  "id": 123,                    // OMIT for new records
  "name": "City Name",          // REQUIRED
  "state_id": 456,              // REQUIRED (FK to states)
  "state_code": "CA",           // REQUIRED
  "country_id": 789,            // REQUIRED (FK to countries)
  "country_code": "US",         // REQUIRED (2 chars)
  "latitude": "34.05223000",    // REQUIRED (string decimal)
  "longitude": "-118.24368000", // REQUIRED (string decimal)
  "native": "Native Name",      // optional
  "timezone": "America/Los_Angeles", // optional (IANA format)
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
  "type": "state",              // optional
  "latitude": "36.77826100",    // optional
  "longitude": "-119.41793240", // optional
  "timezone": "America/Los_Angeles", // optional
  "wikiDataId": "Q99",          // optional
  "population": "39538223",     // optional (string)
  "created_at": null,           // OMIT (auto-managed)
  "updated_at": "2024-10-16T12:00:00", // OMIT (auto-managed)
  "flag": 1                     // OMIT (auto-managed)
}
```

## Finding Reference IDs

```bash
# Find state ID
grep -A 5 '"name": "California"' contributions/states/states.json

# Find country ID
grep -A 5 '"name": "United States"' contributions/countries/countries.json

# Find all states for a country
jq '.[] | select(.country_code == "US") | {id, name}' contributions/states/states.json
```

## Local Development Commands

### Initial Setup
```bash
# Install PHP dependencies
cd bin
composer install --no-interaction --prefer-dist
```

### Database Operations (MySQL)
```bash
# Start MySQL
sudo systemctl start mysql.service

# Create database
mysql -uroot -proot -e "CREATE DATABASE world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import SQL dump
mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql

# Validate import
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"  # Expected ~151,024
```

### Export Commands (reads from MySQL)
```bash
cd bin
php console export:json      # 4 seconds
php console export:csv       # 1 second
php console export:xml       # 9 seconds
php console export:yaml      # 17 seconds
php console export:sql-server # 3 seconds
php console export:mongodb   # 1 second
```

### Testing Locally
```bash
# Import JSON to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py

# Verify import
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"

# Run exports (optional)
cd bin
php console export:json
```

## Important Rules

### DO THIS
- Edit `contributions/` JSON files for data updates
- Use `bin/config/app.yaml` for DB credentials
- Run sync/import scripts after schema changes
- Follow `bin/Commands/Export*.php` pattern for new export formats
- **ALWAYS document fixes** in `.github/fixes-docs/`:
  - Create **ONE** markdown file per issue: `FIX_<issue_number>_SUMMARY.md`
  - Include: issue reference, countries addressed, changes made, validation steps
  - Follow existing format in `.github/fixes-docs/`
- If adding new state and cities, run json→mysql and mysql→json commands between tasks

### DO NOT DO THIS
- Edit auto-generated directories: `json/`, `csv/`, `xml/`, `yml/`, `sql/`, `sqlite/`, `mongodb/`, `sqlserver/`, `psql/`
- Commit generated export files unless explicitly requested
- Run exports or commit artifacts without permission
- Edit `sql/world.sql` casually (prefer JSON-first workflow)
- Manually assign IDs (use MySQL AUTO_INCREMENT or normalize_json.py)
- Add `flag`, `created_at`, or `updated_at` fields manually

### Verify Foreign Keys
- Cities must reference valid `state_id` and `country_id`
- States must reference valid `country_id`
- Countries must reference valid `region_id` and `subregion_id` (if applicable)

## Key Files

- `bin/console` — CLI entrypoint; registers commands, sets memory limits
- `bin/Commands/*.php` — Export command classes (one per format)
- `bin/scripts/sync/import_json_to_mysql.py` — JSON → MySQL
- `bin/scripts/sync/sync_mysql_to_json.py` — MySQL → JSON
- `bin/scripts/sync/normalize_json.py` — Auto-assign IDs and timestamps
- `bin/config/app.yaml` — DB credentials
- `sql/world.sql` — Canonical dataset

## Validation & Performance

### Quick Validation
```sql
-- Verify data integrity
SELECT 'Regions', COUNT(*) FROM regions UNION
SELECT 'Countries', COUNT(*) FROM countries UNION
SELECT 'States', COUNT(*) FROM states UNION
SELECT 'Cities', COUNT(*) FROM cities;

-- Sample checks
SELECT COUNT(*) FROM cities WHERE country_code = 'US';  # ~19,824
SELECT name FROM countries WHERE iso2 = 'US';           # United States
```

### Performance Expectations
- Python build: ~1-2 seconds
- MySQL import: ~3 seconds (151k+ records)
- JSON export: ~4 seconds
- CSV export: ~1 second
- XML export: ~9 seconds
- YAML export: ~17 seconds

## Integration & Conversions

### PostgreSQL Migration
```bash
# Clone nmig (Git submodule)
git clone https://github.com/AnatolyUss/nmig.git nmig
cd nmig
npm install
npm run build
cp ../nmig.config.json config/config.json
npm start
```

### SQLite
```bash
pip install mysql-to-sqlite3

# Convert to SQLite
mysql2sqlite -d world --mysql-password root -u root -f sqlite/world.sqlite3
```

## Tips

- New JSON records should omit `id` (MySQL AUTO_INCREMENT assigns it)
- Import scripts can detect new fields and add columns
- Use `ExportJson.php` as reference for new export commands
- For complex changes, open a PR with export validation counts
- Always verify schema changes manually

## Questions?

- Check `.claude/CLAUDE.md` for detailed documentation
- Review `bin/README.md` for export command documentation
- See `bin/scripts/sync/README.md` for script documentation (if exists)
- Use [CSC Update Tool](https://manager.countrystatecity.in/) for non-technical contributions
- Reference WikiData, Wikipedia, or official sources for data accuracy
