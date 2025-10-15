# Countries States Cities — AI agent guide

This repository is a data-first export pipeline for a global geographical dataset. The canonical SQL dump is `sql/world.sql` (authoritative), and contributors typically edit `contributions/` (JSON). Export and sync tooling lives under `bin/` (PHP console + Python scripts).

Keep this short — focus on what an automated agent needs to be productive.

Quick overview
- Source (contributor-facing): `contributions/` (cities/*.json, states/states.json, countries/countries.json)
- Canonical SQL: `sql/world.sql` (used to seed MySQL for exports)
- Export tooling: `bin/` (PHP console + `bin/Commands/*.php`) + Python sync scripts (`bin/scripts/sync/`)

Primary workflows
- JSON-first (recommended):
  1. Edit `contributions/` JSON files (omit `id` for new records).
  2. Commit & push — GitHub Actions imports JSON → MySQL and runs PHP exports.

- SQL-first (maintainers / advanced):
  1. Modify MySQL directly (or import `sql/world.sql`).
  2. Run `python3 bin/scripts/sync/sync_mysql_to_json.py` to sync MySQL → `contributions/` JSON.
  3. Commit the JSON changes.

Key local commands
- Install PHP deps:
  cd bin && composer install --no-interaction --prefer-dist

- Seed MySQL locally:
  sudo systemctl start mysql.service
  mysql -uroot -proot -e "CREATE DATABASE world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
  mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql

- Run exports (from `bin/`):
  php console export:json
  php console export:csv
  php console export:xml
  php console export:yaml
  php console export:mongodb

Important files (inspect first)
- `bin/console` — CLI entrypoint; registers `bin/Commands/*` and sets memory limits.
- `bin/Commands/*.php` — Export command classes (one-per-format). Use `ExportJson.php` as the minimal example.
- `bin/scripts/sync/import_json_to_mysql.py` and `bin/scripts/sync/sync_mysql_to_json.py` — JSON ↔ MySQL sync scripts.
- `bin/config/app.yaml` — DB credentials used by scripts and console.
- `sql/world.sql` — canonical dataset (large single-file dump).

Integration & conversions
- PostgreSQL migration: `nmig/` (see `nmig.config.json`) — clone `https://github.com/AnatolyUss/nmig.git`, `npm install`, build and run.
- SQLite/DuckDB: `pip install mysql-to-sqlite3 duckdb` then `mysql2sqlite -d world -u root --mysql-password root -f sqlite/world.sqlite3`.

Validation & expectations
- There are no unit tests; validate via exports and SQL counts.
- Quick checks:
  mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"  # expected ~151k
  mysql -uroot -proot -e "SELECT COUNT(*) FROM world.cities WHERE country_code = 'US';"  # expected ~19k

Agent rules — do this
- Prefer editing `contributions/` JSON files for data updates.
- Use `bin/config/app.yaml` to change DB credentials for local testing.
- If you change schema or fields, run the appropriate sync/import script and validate locally before committing.
- When adding export features, follow the `bin/Commands/Export*.php` pattern (one command per output format).
- **ALWAYS document fixes and PRs** in `.github/fixes-docs/`:
  - Create **only ONE markdown file per Issue/PR** (e.g., `FIX_<issue_number>_SUMMARY.md` or `<TOPIC>_SUMMARY.md`)
  - The single file should contain:
    - Issue reference and executive summary
    - Countries/entities addressed
    - Changes made (before/after counts, examples)
    - Validation steps and results
    - Code examples, data samples, and validation commands
  - Follow existing format in `.github/fixes-docs/` directory
  - Do NOT create multiple separate files for the same issue/PR

Agent rules — do NOT do this
- Do NOT commit generated export files (`json/`, `csv/`, `yml/`, `xml/`, `sqlite/`, `duckdb/`, `mongodb/`, `sqlite/`, `sqlserver/`, `psql/` dumps).
- Do NOT run exports or commit generated artifacts unless explicitly requested.
- Do NOT edit `sql/world.sql` casually — prefer JSON-first workflow or validate fully when using SQL-first.

Quick tips
- New JSON records should omit `id` (MySQL AUTO_INCREMENT assigns it during import).
- Import scripts can detect new fields and add columns, but always validate schema changes manually.
- Use `ExportJson.php` as the reference implementation when adding new commands.

If something is unclear, open a small PR describing the change and include export validation counts; ask maintainers before making large schema changes.

-- End of agent guide --
