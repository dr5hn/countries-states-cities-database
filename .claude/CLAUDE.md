# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A comprehensive geographical database (153k+ cities, 5k+ states, 250 countries) available in 9 formats. This is a **data repository** focused on data integrity and multi-format exports. Licensed under ODbL-1.0.

## Architecture: Two-Phase Build System

Data flows between JSON (version control) and MySQL (canonical state):

```
contributions/     →  [Python Import]  →  MySQL  →  [PHP Export]  →  json/, csv/, xml/, yml/, sql/
  ├── cities/*.json                       world        (Symfony Console)    sqlite/, mongodb/, etc.
  ├── states.json                       (canonical)
  └── countries.json
```

**Phase 1: Python Import** (`bin/scripts/sync/import_json_to_mysql.py`)
- Reads `contributions/` JSON files
- Dynamic schema detection (auto-adds new columns to MySQL)
- IDs auto-assigned by MySQL AUTO_INCREMENT
- Handles 209+ country-specific city files

**Phase 2: PHP Export** (`bin/Commands/Export*.php`)
- Symfony Console commands (one per format)
- Reads directly from MySQL via SELECT queries
- Memory limit: unlimited
- Auto-discovered by `bin/console` application

## Data Contribution Workflows

### Workflow 1: JSON-First (Contributors)
```bash
# 1. Edit contributions/cities/US.json (omit 'id' for new records)
# 2. Push changes
# 3. GitHub Actions auto-runs:
python3 bin/scripts/sync/import_json_to_mysql.py  # JSON → MySQL (IDs assigned)
cd bin && php console export:json                  # MySQL → all formats
```

### Workflow 2: SQL-First (Maintainers)
```bash
mysql -uroot -proot world  # Make changes
python3 bin/scripts/sync/sync_mysql_to_json.py  # Sync MySQL → JSON
git add contributions/ && git commit             # Commit JSON changes
```

### Optional: Auto-Normalize JSON
```bash
python3 bin/scripts/sync/normalize_json.py contributions/cities/US.json
```

## Common Development Commands

### Initial Setup
```bash
cd bin
composer install --no-interaction --prefer-dist
```

### Database Setup
```bash
sudo systemctl start mysql.service
mysql -uroot -proot -e "CREATE DATABASE world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"
```

### Import & Export (Local Testing)
```bash
python3 bin/scripts/sync/import_json_to_mysql.py

cd bin
php console export:json         # 4 seconds
php console export:csv          # 1 second
php console export:xml          # 9 seconds
php console export:yaml         # 17 seconds
php console export:sql-server   # 3 seconds
php console export:mongodb      # 1 second

python3 bin/scripts/sync/sync_mysql_to_json.py
```

### Database Migration (Optional)
```bash
# PostgreSQL
cd nmig && npm install && npm run build
cp ../nmig.config.json config/config.json && npm start

# SQLite
pip install mysql-to-sqlite3
mysql2sqlite -d world --mysql-password root -u root -f sqlite/world.sqlite3
```

## Key Architecture Patterns

### PHP Console Application (`bin/console`)
- Symfony Console Application extending `Application`
- Auto-discovers commands in `bin/Commands/` via DirectoryIterator
- Sets `memory_limit = -1` for large dataset exports
- Registers Phinx migration commands (migrate, seed, etc.)

### Dynamic Schema Detection (`import_json_to_mysql.py`)
1. Compares JSON fields vs MySQL `SHOW COLUMNS`
2. Infers MySQL types from JSON values (smart type detection)
3. Executes `ALTER TABLE` for missing columns
4. Bidirectional schema evolution supported

### Export Command Pattern (`bin/Commands/Export*.php`)
1. Extend `Command`, set `$defaultName` (e.g., `export:csv`)
2. Read from MySQL via `Config::getConfig()->getDB()`
3. Transform data to target format
4. Write to corresponding directory (csv/, xml/, etc.)
Use `ExportJson.php` as reference for new export commands.

### Export Distribution: GitHub Releases (not git)
Large compressed exports (`.gz`) are **uploaded to GitHub Releases**, not committed to git. This keeps repo clone size manageable. The export workflow:
1. Generates all formats in the Actions runner
2. Compresses large files with `gzip -9`
3. Creates a tagged Release (`export-YYYYMMDD`) with all `.gz` assets
4. Creates a PR containing only small files (schema, individual table exports)

Downstream projects (csc-export-tool, countrystatecity npm/pypi packages) download `.gz` from `https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/<filename>`.

## GitHub Actions Automation

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `export.yml` | Manual / changes to `bin/Commands/Export**` | Full export pipeline, uploads to Releases + PR |
| `pr-validator.yml` | PR touching `contributions/` | Schema validation, cross-refs, coordinates, duplicates, auto-labels |
| `auto-changelog.yml` | PR merged to master | Appends one-liner to `CHANGELOG.md` via PR |
| `triage-repository.yml` | Manual (workflow_dispatch) | Batch triage all open issues/PRs, label, warn stale, send digest |
| `stale-cleanup.yml` | Weekly (Sunday) | Warn PRs inactive 21+ days, close at 30+ |
| `weekly-digest.yml` | Weekly (Monday 9am IST) | Slack summary of repo status |
| `issue-autoassign.yml` | Issue labelled `auto-fix`/`copilot` | Assign to Copilot coding agent |
| `setup-labels.yml` | Manual (one-time) | Create all 20 required labels |

### PR Validation Pipeline (`.github/scripts/`)
Runs on every PR touching `contributions/`. Node.js scripts using `@actions/core` and `@actions/github`:

1. **`validate-pr-format.js`** — Description, source URL, issue linkage checks
2. **`analyse-diff.js`** — Auto-labels entity types, detects critical changes (record deletions in states/countries)
3. **`validate-schema.js`** — JSON lint + field validation against schema rules in `utils.js`
4. **`validate-cross-reference.js`** — FK integrity: state_id, country_id exist and codes match
5. **`validate-coordinates.js`** — Coordinates within parent country's bounding box (`.github/data/country-bounds.json`)
6. **`detect-duplicates.js`** — Fuzzy name (Levenshtein ≤ 2) + coordinate proximity (< 5km)
7. **`check-source-urls.js`** — HTTP HEAD check on source URLs in PR description

Shared utilities in `utils.js`: schema definitions, `loadRepoData()` (tries `contributions/` first), `haversineDistance()`, `levenshteinDistance()`.

## Data Schema Essentials

### Cities (Most Common)
- `id` - OMIT for new records (MySQL AUTO_INCREMENT)
- `name`, `state_id`, `state_code`, `country_id`, `country_code`, `latitude`, `longitude` - REQUIRED
- `timezone` (IANA), `wikiDataId` - Optional
- `created_at`, `updated_at`, `flag` - OMIT (auto-managed by MySQL)

### Finding Foreign Keys
```bash
grep -A 5 '"name": "California"' contributions/states/states.json  # state_id
grep -A 5 '"name": "United States"' contributions/countries/countries.json  # country_id
```

## Configuration

**Database credentials:**
- Scripts: `bin/config/app.yaml`
- PHP exports: `Config::getConfig()->getDB()` reads from app.yaml
- Default: `root:root@localhost/world`
- **Local Environment**: MySQL runs without password (`root:@localhost/world`)

**Override for GitHub Actions:**
```bash
python3 bin/scripts/sync/import_json_to_mysql.py --host $DB_HOST --user $DB_USER --password $DB_PASSWORD
```

**Secrets used by workflows:**
- `GITHUB_TOKEN` — Auto-provided, used by PR validator, changelog, triage
- `SLACK_WEBHOOK_URL` — Optional, for Slack notifications across all workflows

## Important Rules

**DO:**
- Edit `contributions/` JSON only (source of truth)
- Omit `id` for new records (auto-assigned)
- Run `normalize_json.py` to pre-assign IDs (optional)
- Document fixes in `.github/fixes-docs/FIX_<issue_number>_SUMMARY.md` (ONE file per issue)
- When adding states + cities: run JSON→MySQL→JSON between tasks for ID assignment
- For overseas / dual-ISO territories (e.g. FR overseas, US territories, CN SARs), see [MULTI_LEVEL_TERRITORIES.md](../MULTI_LEVEL_TERRITORIES.md) before changing country/state records

**DO NOT:**
- Edit auto-generated dirs: `json/`, `csv/`, `xml/`, `yml/`, `sql/`, etc.
- Commit `.gz` exports or large generated files (they go to GitHub Releases)
- Edit `sql/world.sql` directly (prefer JSON-first workflow)
- Add `flag`, `created_at`, `updated_at` manually (MySQL manages these)

## Performance Expectations

- MySQL import: ~3 seconds
- JSON export: ~4 seconds
- CSV export: ~1 second
- XML export: ~9 seconds
- YAML export: ~17 seconds
- DuckDB conversion: ~8 minutes (set 20+ min timeout)
- GitHub Actions full export: 10-15 minutes

## Validation Queries

```sql
SELECT 'Cities', COUNT(*) FROM cities UNION
SELECT 'States', COUNT(*) FROM states UNION
SELECT 'Countries', COUNT(*) FROM countries;

SELECT COUNT(*) FROM cities WHERE country_code = 'US';  -- ~19,824
```

## Common Issues

- **Composer hangs**: Use `--no-interaction --prefer-dist`
- **MySQL connection failed**: `sudo systemctl start mysql.service`
- **DuckDB timeout**: Takes 8+ minutes, set timeout to 20+ minutes
- **Export files missing**: Run exports from `bin/` directory
- **Round-trip validation fails**: Check for schema mismatches between JSON and MySQL

## Timezone Management

**Tools:**
- `bin/scripts/analysis/timezone_summary.py` - Generate timezone analysis reports
- `bin/scripts/fixes/timezone_mappings.json` - Geographic timezone reference data
- `.github/fixes-docs/TIMEZONE_FIX_SUMMARY.md` - Documentation of fixes applied (2025-10-18)

**Generate Reports:**
```bash
python3 bin/scripts/analysis/timezone_summary.py
```
