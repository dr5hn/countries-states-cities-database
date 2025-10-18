# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

A comprehensive geographical database (151k+ cities, 5k+ states, 250 countries) available in 9 formats. This is a **data repository** focused on data integrity and multi-format exports.

## Architecture: Two-Phase Build System

The repository uses a **bidirectional workflow** where data flows between JSON (version control) and MySQL (canonical state):

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
- Memory limit: unlimited (handles 151k+ records)
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
# Pre-assign IDs before committing (connects to MySQL for next ID)
python3 bin/scripts/sync/normalize_json.py contributions/cities/US.json
```

## Common Development Commands

### Initial Setup
```bash
cd bin
composer install --no-interaction --prefer-dist  # PHP dependencies (Symfony Console, etc.)
```

### Database Setup
```bash
# Start MySQL
sudo systemctl start mysql.service

# Create database
mysql -uroot -proot -e "CREATE DATABASE world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Import canonical SQL dump
mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql

# Validate
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"  # Should be ~151,024
```

### Import & Export (Local Testing)
```bash
# Import JSON to MySQL (from contributions/)
python3 bin/scripts/sync/import_json_to_mysql.py

# Export MySQL to all formats
cd bin
php console export:json         # 4 seconds
php console export:csv          # 1 second
php console export:xml          # 9 seconds
php console export:yaml         # 17 seconds
php console export:sql-server   # 3 seconds
php console export:mongodb      # 1 second

# Sync MySQL back to JSON (validation or SQL-first workflow)
python3 bin/scripts/sync/sync_mysql_to_json.py
```

### Database Migration (Optional)
```bash
# PostgreSQL
cd nmig
npm install && npm run build
cp ../nmig.config.json config/config.json
npm start

# SQLite
pip install mysql-to-sqlite3
mysql2sqlite -d world --mysql-password root -u root -f sqlite/world.sqlite3

# DuckDB (reference only, not supported)
pip install duckdb
python3 bin/scripts/export/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db
```

## Key Architecture Patterns

### PHP Console Application (`bin/console`)
- Symfony Console Application extending `Application`
- Auto-discovers commands in `bin/Commands/` via DirectoryIterator
- Sets `memory_limit = -1` for large dataset exports
- Registers Phinx migration commands (migrate, seed, etc.)
- Each export = independent Command class

### Dynamic Schema Detection (`import_json_to_mysql.py`)
```python
# Auto-detects new columns in JSON and adds to MySQL
new_columns = self.detect_new_columns(table_name, json_data)
if new_columns:
    self.add_columns_to_table(table_name, new_columns)  # ALTER TABLE
```

**How it works:**
1. Compares JSON fields vs MySQL SHOW COLUMNS
2. Infers MySQL types from JSON values (smart type detection)
3. Executes ALTER TABLE for missing columns
4. Bidirectional schema evolution supported

### Export Command Pattern (`bin/Commands/Export*.php`)
```php
class ExportJson extends Command {
    protected static $defaultName = 'export:json';

    protected function execute(InputInterface $input, OutputInterface $output): int {
        $db = Config::getConfig()->getDB();  // MySQL connection
        $result = $db->query("SELECT * FROM cities ORDER BY name");
        // Build arrays, write to json/ directory
        $this->filesystem->dumpFile($rootDir . '/json/cities.json', ...);
    }
}
```

**Pattern for new exports:**
1. Extend `Command`, set `$defaultName` (e.g., `export:csv`)
2. Read from MySQL via `Config::getConfig()->getDB()`
3. Transform data to target format
4. Write to corresponding directory (csv/, xml/, etc.)

### GitHub Actions Workflow (`.github/workflows/export.yml`)
**Auto-runs on:**
- Manual trigger (workflow_dispatch)
- Changes to `bin/Commands/Export**`

**Steps:**
1. Setup: MySQL, PostgreSQL, MongoDB
2. Create database + run schema migrations
3. Import: `import_json_to_mysql.py` (JSON → MySQL)
4. Validation: `sync_mysql_to_json.py` (MySQL → JSON round-trip)
5. Exports: All formats via PHP console commands
6. Compress: Large files (.gz for cities.json, world.sql, etc.)
7. Pull Request: Auto-created with all exports

## File Organization

```
contributions/          # Source of truth (edit these)
├── cities/            # 209+ country files (US.json, IN.json, etc.)
├── states/states.json
└── countries/countries.json

bin/
├── console            # Symfony Console app (CLI entrypoint)
├── Commands/          # Export*.php classes (auto-discovered)
├── config/
│   ├── app.yaml       # DB credentials for scripts
│   └── phinx.yaml     # Migration config
└── scripts/
    ├── sync/          # Python: JSON ↔ MySQL bidirectional sync
    └── export/        # Python: Format conversions (SQLite, DuckDB)

sql/world.sql          # Canonical MySQL dump (auto-generated)
```

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

**Local MySQL commands (no password):**
```bash
mysql -uroot world                          # Connect to database
mysql -uroot -e "USE world; SHOW TABLES;"  # Run queries
```

## Important Rules

**DO:**
- Edit `contributions/` JSON only (source of truth)
- Omit `id` for new records (auto-assigned)
- Run `normalize_json.py` to pre-assign IDs (optional)
- Document fixes in `.github/fixes-docs/FIX_<issue_number>_SUMMARY.md` (ONE file per issue)
- When adding states + cities: run JSON→MySQL→JSON between tasks for ID assignment
- Use `ExportJson.php` as reference for new export commands

**DO NOT:**
- Edit auto-generated dirs: `json/`, `csv/`, `xml/`, `yml/`, `sql/`, etc.
- Commit large exports without explicit request
- Edit `sql/world.sql` directly (prefer JSON-first workflow)
- Add `flag`, `created_at`, `updated_at` manually (MySQL manages these)
- Run exports locally without cleaning up afterward

## Performance Expectations

- MySQL import: ~3 seconds (151k+ records)
- JSON export: ~4 seconds
- CSV export: ~1 second
- XML export: ~9 seconds
- YAML export: ~17 seconds
- DuckDB conversion: ~8 minutes (set 20+ min timeout)
- GitHub Actions: 10-15 minutes (full pipeline)

## Validation Queries

```sql
-- Data integrity check
SELECT 'Cities', COUNT(*) FROM cities UNION
SELECT 'States', COUNT(*) FROM states UNION
SELECT 'Countries', COUNT(*) FROM countries;

-- Sample validation
SELECT COUNT(*) FROM cities WHERE country_code = 'US';  -- ~19,824
```

## Common Issues

- **Composer hangs**: Use `--no-interaction --prefer-dist`
- **MySQL connection failed**: `sudo systemctl start mysql.service`
- **DuckDB timeout**: Takes 8+ minutes, set timeout to 20+ minutes
- **Export files missing**: Run exports from `bin/` directory
- **Round-trip validation fails**: Check for schema mismatches between JSON and MySQL

## Timezone Management

**Tools (Keep these):**
- `bin/scripts/analysis/timezone_summary.py` - Generate timezone analysis reports
- `bin/scripts/fixes/timezone_mappings.json` - Geographic timezone reference data
- `.github/fixes-docs/TIMEZONE_FIX_SUMMARY.md` - Documentation of fixes applied (2025-10-18)

**Completed Fixes (2025-10-18):**
- Fixed 81 states across 9 countries (US, CA, RU, BR, MX, AU, AR, ID, KZ, CN)
- Improved timezone utilization from 240 to 299 unique timezones
- All changes validated against country timezone definitions

**Generate Timezone Reports:**
```bash
python3 bin/scripts/analysis/timezone_summary.py  # Full analysis report
```
