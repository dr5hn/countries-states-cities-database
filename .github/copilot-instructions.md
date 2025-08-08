# Countries States Cities Database

This repository contains a comprehensive geographical database of countries, states, and cities worldwide. The database is available in multiple formats (JSON, CSV, XML, YAML, MySQL, PostgreSQL, SQLite, DuckDB, SQL Server, MongoDB) and is automatically exported using PHP-based CLI tools.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

- **CRITICAL**: MySQL database setup and import:
  - `sudo systemctl start mysql.service` -- MySQL service startup: 2 seconds
  - `mysql -uroot -proot -e "CREATE DATABASE world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"` -- Database creation: < 1 second
  - `mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql` -- Import data: 3 seconds, NEVER CANCEL
  - **Database contains**: 6 regions, 22 subregions, 250 countries, 5,134 states, 151,901 cities

- **Install PHP dependencies**:
  - `cd bin && composer install --no-interaction --prefer-dist` -- Dependency installation: 30-60 seconds, NEVER CANCEL
  - MySQL root password is `root`

- **Export commands** (all run from `bin/` directory):
  - `php console export:json` -- JSON export: 4 seconds, NEVER CANCEL
  - `php console export:csv` -- CSV export: 1 second, NEVER CANCEL 
  - `php console export:xml` -- XML export: 9 seconds, NEVER CANCEL
  - `php console export:yaml` -- YAML export: 17 seconds, NEVER CANCEL
  - `php console export:sql-server` -- SQL Server export: 3 seconds, NEVER CANCEL
  - `php console export:mongodb` -- MongoDB export: 1 second, NEVER CANCEL

- **PostgreSQL migration** (optional):
  - `sudo systemctl start postgresql.service` -- PostgreSQL startup: 2 seconds
  - `sudo -u postgres psql -c "CREATE DATABASE world;" && sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"` -- Setup: 1 second
  - `git clone https://github.com/AnatolyUss/nmig.git nmig` if nmig directory is empty -- Clone: 10 seconds, NEVER CANCEL
  - `cd nmig && npm install` -- Install dependencies: 30 seconds, NEVER CANCEL. Set timeout to 60+ minutes.
  - `npm run build` -- Build nmig: 3 seconds, NEVER CANCEL
  - `cp ../nmig.config.json config/config.json && npm start` -- Migration: 4 seconds, NEVER CANCEL

- **SQLite/DuckDB exports**:
  - Install: `pip install mysql-to-sqlite3 duckdb` -- Installation: 30 seconds, NEVER CANCEL
  - `mysql2sqlite -d world --mysql-password root -u root -f sqlite/world.sqlite3` -- SQLite export: 1 second, NEVER CANCEL
  - `python3 bin/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db` -- DuckDB export: 8 minutes, NEVER CANCEL. Set timeout to 20+ minutes.

## Validation

- **Database validation**: Always verify database imports with `mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"` -- Expected: 151,901 cities
- **Export validation**: Check file creation in respective directories (json/, csv/, xml/, yml/, sqlserver/, mongodb/, sqlite/, duckdb/)
- **Sample queries**: Test with `mysql -uroot -proot -e "SELECT COUNT(*) FROM world.cities WHERE country_code = 'US';"` -- Expected: ~19,824 US cities
- **ALWAYS run complete export workflows** to validate changes don't break data integrity
- No unit tests exist - this is a data repository validated through export processes

## Common Tasks

The following are outputs from frequently run commands. Reference them instead of viewing, searching, or running bash commands to save time.

### Repository structure
```
.
├── .github/           # GitHub Actions workflows and documentation  
├── bin/              # PHP CLI export tools and dependencies
├── csv/              # CSV export outputs
├── docs/             # Static demo website files
├── duckdb/           # DuckDB database files  
├── json/             # JSON export outputs
├── mongodb/          # MongoDB export outputs
├── nmig/             # MySQL to PostgreSQL migration tool (git submodule)
├── psql/             # PostgreSQL export outputs
├── sql/              # Source SQL files (world.sql is main 21MB dataset)
├── sqlite/           # SQLite database files
├── sqlserver/        # SQL Server export outputs
├── xml/              # XML export outputs
├── yml/              # YAML export outputs
├── README.md         # Main documentation
└── nmig.config.json  # Database migration configuration
```

### Main console commands
```bash
cd bin && php console list
Available commands:
  export:json        # Export all data to JSON format
  export:csv         # Export all data to CSV format  
  export:xml         # Export all data to XML format
  export:yaml        # Export all data to YAML format
  export:sql-server  # Export all data to SQL Server format
  export:mongodb     # Export all data to MongoDB format
  export:csc-npm     # Export data for NPM package format
  export:plist       # Export data to Apple Property List format
  manage:migrate     # Run database migrations
  manage:status      # Show migration status
  seed:run          # Run database seeders
```

### Database connection details
- **MySQL**: host=127.0.0.1, port=3306, user=root, password=root, database=world
- **PostgreSQL**: host=127.0.0.1, port=5432, user=postgres, password=postgres, database=world
- **Character set**: utf8mb4 for proper international character support

### Key file locations
- **Source data**: `sql/world.sql` (21MB, contains all geographical data)
- **PHP config**: `bin/config/app.yaml` (database connection settings)
- **Migration config**: `nmig.config.json` (MySQL to PostgreSQL settings)
- **Export outputs**: `json/`, `csv/`, `xml/`, `yml/`, `sqlserver/`, `mongodb/`, `sqlite/`, `duckdb/`

### Record counts
- **Regions**: 6 (Africa, Americas, Asia, Europe, Oceania, Polar)
- **Subregions**: 22 (Eastern Africa, Western Europe, etc.)
- **Countries**: 250 (all UN recognized countries plus territories)
- **States**: 5,134 (provinces, states, territories within countries)
- **Cities**: 151,901 (major cities and towns worldwide)

### Required system packages
- **PHP**: 8.1+ with composer
- **MySQL**: 8.0+ for data storage and querying
- **Node.js**: 20+ for nmig migration tool
- **Python**: 3.8+ for SQLite/DuckDB conversion scripts
- **PostgreSQL**: 12+ (optional, for PostgreSQL exports)

### GitHub Actions workflow
- **Trigger**: Manual workflow_dispatch or changes to `bin/Commands/Export**`
- **Services**: MySQL, PostgreSQL, MongoDB automatically configured
- **Export process**: Creates all formats automatically and opens PR
- **Runtime**: Complete workflow takes 10-15 minutes, NEVER CANCEL

### Performance expectations
- **MySQL import**: 3 seconds for 151k+ records
- **JSON export**: 4 seconds for all tables  
- **CSV export**: 1 second for all tables
- **XML export**: 9 seconds for all tables
- **YAML export**: 17 seconds for all tables
- **PostgreSQL migration**: 4 seconds for full database
- **SQLite export**: 1 second for full database
- **DuckDB export**: 8 minutes for full database, NEVER CANCEL
- **MongoDB export**: 1 second for JSON files

### Common validation queries
```sql
-- Verify data integrity
SELECT 'Regions', COUNT(*) FROM regions UNION
SELECT 'Countries', COUNT(*) FROM countries UNION  
SELECT 'States', COUNT(*) FROM states UNION
SELECT 'Cities', COUNT(*) FROM cities;

-- Sample data checks
SELECT COUNT(*) FROM cities WHERE country_code = 'US';  -- ~19,824
SELECT name FROM countries WHERE iso2 = 'US';          -- United States
SELECT COUNT(*) FROM states WHERE country_code = 'CA'; -- Canadian provinces
```

### Troubleshooting
- **MySQL connection failed**: Ensure service started with `sudo systemctl start mysql.service`
- **Composer hangs on GitHub**: Use `--no-interaction --prefer-dist` flags to avoid token prompts
- **nmig directory empty**: Run `git clone https://github.com/AnatolyUss/nmig.git nmig` to populate
- **DuckDB timeout**: This export takes 8+ minutes, always set timeout to 20+ minutes
- **Export files missing**: Run exports from `bin/` directory, check target directories exist
- **Memory issues with large exports**: PHP memory limit set to unlimited in console script

### Data modification workflow
1. **Edit source**: Update `sql/world.sql` for data changes
2. **Reimport database**: `mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql`
3. **Run exports**: Execute all `php console export:*` commands from `bin/` directory  
4. **Validate outputs**: Check file sizes and record counts in export directories
5. **Test queries**: Run validation queries to ensure data integrity

### Contributing data updates
- **Primary method**: Use web tool at https://manager.countrystatecity.in/ for submissions
- **Manual method**: Edit `sql/world.sql` directly and create pull request
- **Table structure**: See `.github/CONTRIBUTING.md` for column specifications
- **Data sources**: Use WikiData, Wikipedia, or other legitimate geographical sources

### Important notes for agents
- **Large export files**: MongoDB JSON files and DuckDB databases can be 50MB+ and should not be committed
- **Build artifacts**: Export files are automatically generated and excluded via .gitignore
- **GitHub Actions**: Use the automated export workflow for generating all formats rather than manual commits
- **Development focus**: This is a data repository - focus on data integrity and export functionality, not code architecture