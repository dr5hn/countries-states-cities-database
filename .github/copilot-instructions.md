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

## Data Validation with Wikipedia

### Wikipedia API Integration

When validating or enriching geographical data, use the Wikipedia API directly (see `.github/agent-docs/WIKIPEDIA_API_DOCS.md` for examples).

**Common validation tasks:**
1. **Verify city/state/country names**: Search Wikipedia to confirm official names and spellings
2. **Extract coordinates**: Get latitude/longitude from Wikipedia articles
3. **Find timezone information**: Extract IANA timezone identifiers from infoboxes
4. **Validate population data**: Cross-reference with Wikipedia demographic data
5. **Check administrative divisions**: Verify state/province relationships

**Example API calls:**

```bash
# Get article for a city (e.g., Belgrade)
curl "https://en.wikipedia.org/w/api.php?action=query&titles=Belgrade&prop=extracts|pageimages|coordinates|info&inprop=url&redirects=&format=json&origin=*"

# Search for a location
curl "https://en.wikipedia.org/w/api.php?action=query&list=search&prop=info&inprop=url&utf8=&format=json&srlimit=20&srsearch=New%20York%20City"

# Get coordinates for a location
curl "https://en.wikipedia.org/w/api.php?action=query&titles=Paris&prop=coordinates&format=json"
```

**Best practices:**
- Always include `&origin=*` to avoid CORS issues when testing in browser
- Use `redirects=` parameter to follow article redirects automatically
- Capitalize multi-word search terms (e.g., "New York" not "new york")
- Extract data from the JSON response and validate against existing database records
- For batch operations, respect Wikipedia's rate limits (add delays between requests)

**Python example using Wikipedia-API package (recommended):**

```python
import wikipediaapi

# Initialize Wikipedia client
wiki = wikipediaapi.Wikipedia(
    user_agent='countries-states-cities-database/1.0',
    language='en'
)

def validate_city_with_wikipedia(city_name, country_code=None):
    """Validate city data against Wikipedia"""
    # Try different title formats
    titles_to_try = [
        city_name,
        f"{city_name}, {country_code}" if country_code else None,
        f"{city_name} (city)"
    ]

    for title in filter(None, titles_to_try):
        page = wiki.page(title)
        if page.exists():
            return {
                "title": page.title,
                "url": page.fullurl,
                "summary": page.summary[:300],
                "coordinates": page.coordinates if hasattr(page, 'coordinates') else None,
                "categories": list(page.categories.keys())[:10]
            }

    return {"status": "not_found"}

# Or use the built-in validator script:
# python3 bin/scripts/validation/wikipedia_validator.py --entity "Paris" --type city --country FR
```

**Important notes:**
- Wikipedia API documentation: https://www.mediawiki.org/wiki/API:Main_page
- Use different language Wikipedias for region-specific data (e.g., `de.wikipedia.org` for German cities)
- Always cite Wikipedia as a source in fix documentation (`.github/fixes-docs/`)
- MCP servers (like `wikipedia-mcp`) are NOT available in GitHub Actions - use direct HTTP API calls

## 🎯 CRITICAL: Data Enrichment Requirements

### Timezone and Translation Fields are MANDATORY

**NEVER skip adding timezone and translations!** These fields are critical for data quality.

#### Automatic Enrichment Tools

**ALWAYS run these tools after adding or updating ANY data:**

```bash
# 1. Import to MySQL (assigns IDs)
python3 bin/scripts/sync/import_json_to_mysql.py

# 2. Add timezone to ALL entries (MySQL-based, very fast)
python3 bin/scripts/validation/add_timezones.py --table both

# 3. Sync back to JSON (updates timezone in JSON files)
python3 bin/scripts/sync/sync_mysql_to_json.py

# 4. Add translations from Wikipedia (18+ languages, FREE!)
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/US.json \
    --type city \
    --limit 10  # Remove --limit for all records

# 5. Import again (updates translations in MySQL)
python3 bin/scripts/sync/import_json_to_mysql.py

# 6. Final sync
python3 bin/scripts/sync/sync_mysql_to_json.py

# 7. Validate with Wikipedia
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "New York City" \
    --type city \
    --country US
```

**These tools are PRE-INSTALLED in GitHub Actions.** No excuses for skipping them!

#### What Each Tool Does

1. **`add_timezones.py`** - Automatically determines IANA timezone from coordinates
   - Uses timezonefinder library (already included in script)
   - Works directly with MySQL (VERY FAST - 1000+ cities/minute)
   - Batch processing with dry-run mode for testing
   - Handles both cities AND states in one command

2. **`translation_enricher.py`** - Fetches translations from Wikipedia (FREE!)
   - Supports 18+ major languages (ar, de, es, fr, hi, it, ja, ko, pt, ru, zh, etc.)
   - Uses Wikipedia language links (no API costs!)
   - Rate-limited to respect API usage
   - Authentic translations (actual Wikipedia article titles)

3. **`wikipedia_validator.py`** - Validates data accuracy
   - Verifies names and coordinates
   - Fetches WikiData IDs
   - Cross-references with authoritative sources

#### Quality Requirements

**Minimum acceptable data quality:**

```json
{
  "name": "Paris",
  "country_id": 75,
  "country_code": "FR",
  "state_id": 4796,
  "state_code": "11",
  "latitude": "48.85661400",
  "longitude": "2.35222190",
  "timezone": "Europe/Paris",           // ← REQUIRED
  "translations": {                     // ← REQUIRED (at least 5-10 languages)
    "ar": "باريس",
    "de": "Paris",
    "es": "París",
    "fr": "Paris",
    "ja": "パリ"
  },
  "wikiDataId": "Q90",                 // ← HIGHLY RECOMMENDED
  "native": "Paris"                    // ← RECOMMENDED
}
```

**If you submit data without timezone and translations, it will be REJECTED.**

## 📚 Required Documentation Reading

### Before Starting ANY Task

**MUST READ in this order:**

1. **`.github/agent-docs/AI_AGENT_BEST_PRACTICES.md`** ⭐ START HERE
   - Complete workflow for all common tasks
   - Tool usage examples
   - Quality checklist
   - Common mistakes to avoid

2. **`.github/agent-docs/README.md`**
   - Overview of all available tools
   - When to use each tool
   - GitHub Actions vs local development

3. **`.github/fixes-docs/`** - Review at least 2-3 examples
   - `AFGHANISTAN_MISSING_WARDAK_PROVINCE.md` - Excellent example of proper state + cities addition
   - `FIX_1019_SUMMARY.md` - Comprehensive fix documentation
   - Study the pattern: problem → solution → validation → documentation

4. **This file** (`.github/copilot-instructions.md`)
   - General rules and workflows

5. **`.claude/CLAUDE.md`**
   - Deep technical details
   - Architecture overview

### Available Documentation

**Agent Guides** (`.github/agent-docs/`):
- `AI_AGENT_BEST_PRACTICES.md` - **START HERE** - Complete best practices guide
- `README.md` - Tool overview
- `WIKIPEDIA_API_DOCS.md` - API reference (fallback)
- `WIKIPEDIA_MCP.md` - MCP reference (local dev only)

**Fix Examples** (`.github/fixes-docs/`):
- Study existing fixes to understand:
  - Documentation format
  - Validation methodology
  - How to cite sources
  - Before/after metrics

**Technical Docs**:
- `.claude/CLAUDE.md` - Architecture and workflows
- `bin/README.md` - Export commands
- `bin/scripts/validation/README.md` - Validation tools
- `contributions/README.md` - Field reference

## Questions?

- **First:** Check `.github/agent-docs/AI_AGENT_BEST_PRACTICES.md` (answers 90% of questions)
- **Second:** Review examples in `.github/fixes-docs/`
- **Third:** Check `.claude/CLAUDE.md` for detailed documentation
- Review `bin/README.md` for export command documentation
- See `bin/scripts/validation/README.md` for validation tools
- Use [CSC Update Tool](https://manager.countrystatecity.in/) for non-technical contributions
- Reference WikiData, Wikipedia, or official sources for data accuracy
