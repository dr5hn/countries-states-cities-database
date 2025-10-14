# Python Scripts

Organized collection of Python scripts for data processing, synchronization, and export.

## Directory Structure

```
scripts/
├── sync/        # Bidirectional MySQL ↔ JSON synchronization
├── export/      # Export to various formats
└── README.md    # This file
```

## Utility Scripts (`utility/`)

### add_timezones.py ⭐ NEW
**Add timezone data to cities and states using latitude/longitude coordinates**

```bash
# Add timezones to both cities and states (default)
python3 scripts/utility/add_timezones.py

# Add timezones only to cities
python3 scripts/utility/add_timezones.py --table cities

# Add timezones only to states
python3 scripts/utility/add_timezones.py --table states

# Custom database credentials
python3 scripts/utility/add_timezones.py --host localhost --user root --password root

# Test with limited records
python3 scripts/utility/add_timezones.py --limit 100 --dry-run
```

**Features**:
- Uses `timezonefinder` library to map lat/lng → IANA timezone
- **Supports both cities and states tables**
- **Filters out `Etc/GMT*` timezones** (not proper location-based IANA timezones)
- Processes records in batches for efficiency (default: 1000 per batch)
- Updates only records without timezone data (timezone IS NULL)
- Supports dry-run mode for testing
- Transaction-safe with batch commits

**Use case**: Populate timezone data for new cities based on coordinates

**Requirements**: `pip install timezonefinder mysql-connector-python`

**Important**: The script automatically filters out generic `Etc/GMT±N` timezones returned by TimezoneFinder for oceanic locations, ensuring only proper IANA timezones are used. See `TIMEZONE_GUIDE.md` for details.

### validate_timezones.py ⭐ NEW
**Validate timezone data quality across countries, states, and cities**

```bash
# Run validation check
python3 scripts/utility/validate_timezones.py

# Check cities too (requires MySQL)
python3 scripts/utility/validate_timezones.py --check-cities

# Generate SQL fixes for problematic states
python3 scripts/utility/validate_timezones.py --fix-states
```

**Features**:
- Checks for `Etc/` timezones in states
- Validates state timezones exist in countries
- Detects invalid or deprecated IANA timezones
- Optional city timezone validation (MySQL required)
- Generates SQL fix statements

**Use case**: Data quality auditing and validation before releases

### sync_mysql_to_json.py ⭐ NEW
**MySQL → JSON synchronization with dynamic schema detection**

```bash
python3 scripts/sync/sync_mysql_to_json.py

# With custom credentials
python3 scripts/sync/sync_mysql_to_json.py --host localhost --user root --password root
```

**Features**:
- Auto-detects ALL columns from MySQL schema (no hardcoded fields)
- Syncs to `contributions/cities/<COUNTRY_CODE>.json`
- Preserves IDs and handles NULL values
- Adapts to schema changes automatically
- Perfect for local development workflow

**Use case**: Edit MySQL locally → Sync to JSON → Commit

### import_json_to_mysql.py ⭐ NEW
**JSON → MySQL import with automatic schema updates**

```bash
# Local development
python3 scripts/sync/import_json_to_mysql.py

# GitHub Actions (custom credentials)
python3 scripts/sync/import_json_to_mysql.py --host $DB_HOST --user $DB_USER --password $DB_PASSWORD
```

**Features**:
- Auto-detects new columns in JSON
- Adds missing columns to MySQL schema automatically
- Intelligent type inference (VARCHAR, INT, DECIMAL, TEXT, etc.)
- Batch inserts for performance (1000 records/batch)
- Transaction safety with rollback on error
- CI/CD ready

**Use case**: Add column to JSON → Import → MySQL schema updates automatically


## Export Scripts (`export/`)

### export_plist.py
Exports data to Apple Property List (.plist) format.

```bash
python3 scripts/export/export_plist.py
```

**Output**: `plist/` directory with .plist files

### import_duckdb.py
Converts MySQL/SQLite database to DuckDB format.

```bash
python3 scripts/export/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db
```

**Note**: Takes ~8 minutes, use 20+ minute timeout

## Requirements

Install Python dependencies:

```bash
pip install mysql-connector-python timezonefinder duckdb
```

## Common Workflows

### Workflow 1: JSON-First (Contributors via GitHub Actions)
```bash
# 1. Edit JSON
vim contributions/cities/US.json

# 2. Commit & Push
git add contributions/
git commit -m "feat: add new cities"
git push

# 3. GitHub Actions automatically:
#    - Runs import_json_to_mysql.py (contributions → MySQL, IDs auto-assigned)
#    - Runs php console export:json (MySQL → json/ directory)
#    - Creates PR with all exports
```

### Workflow 2: SQL-First (Maintainers)
```bash
# 1. Edit MySQL
mysql -uroot -proot world
# ... make changes ...

# 2. Sync MySQL → JSON
python3 scripts/sync/sync_mysql_to_json.py

# 3. Review & commit
git diff ../../contributions/
git add ../../contributions/
git commit -m "feat: update database"
```

### Workflow 3: Schema Evolution
**Adding new column to existing data:**

```bash
# If column added in MySQL:
python3 scripts/sync/sync_mysql_to_json.py  # Auto-detects new column

# If column added in JSON:
python3 scripts/sync/import_json_to_mysql.py  # Auto-adds column to MySQL
```

## Script Execution from Project Root

All scripts can be run from project root:

```bash
# Sync scripts
python3 bin/scripts/sync/sync_mysql_to_json.py         # MySQL → contributions/
python3 bin/scripts/sync/import_json_to_mysql.py       # contributions/ → MySQL

# Export scripts
python3 bin/scripts/export/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db
```

## Development Guidelines

1. **All scripts must**:
   - Include shebang: `#!/usr/bin/env python3`
   - Have docstring explaining purpose
   - Use type hints where applicable
   - Handle errors gracefully
   - Print progress/status messages

2. **File organization**:
   - `sync/`: Bidirectional database synchronization
   - `export/`: Format conversion and export

3. **Dynamic schema support**:
   - NEVER hardcode field lists
   - Always detect columns dynamically
   - Use `SHOW COLUMNS` for MySQL introspection
   - Infer types from sample data for JSON

4. **Error handling**:
   - Use try/except blocks
   - Provide clear error messages
   - Exit with non-zero code on failure
   - Clean up resources (close DB connections)
