# Command Line Interface for World Database

This directory contains the command-line interface (CLI) tools for managing and exporting the World Database in various formats.

## Directory Structure

```
bin/
├── Commands/                    # PHP export command classes
├── Support/                     # Support classes (Config, Env)
├── config/                      # Configuration files (app.yaml, phinx.yaml)
├── db/                          # Database migrations
├── scripts/                     # Python scripts (organized by purpose)
│   ├── sync/                    # Bidirectional MySQL ↔ JSON sync
│   ├── export/                  # Format conversion and export
│   └── README.md                # Python scripts documentation
├── console                      # Main CLI entry point (PHP)
└── README.md                    # This file
```

## Available Commands

All commands can be executed from the `bin` directory using `php console [command]`

### Export Commands

1. **JSON Export**
   ```bash
   php console export:json
   ```
   Exports data in JSON format:
   - regions.json
   - subregions.json
   - countries.json
   - states.json
   - cities.json
   - countries+states.json
   - countries+cities.json
   - countries+states+cities.json

2. **CSV Export**
   ```bash
   php console export:csv
   ```
   Exports data in CSV format:
   - regions.csv
   - subregions.csv
   - countries.csv
   - states.csv
   - cities.csv

3. **XML Export**
   ```bash
   php console export:xml
   ```
   Exports data in XML format:
   - regions.xml
   - subregions.xml
   - countries.xml
   - states.xml
   - cities.xml

4. **YAML Export**
   ```bash
   php console export:yaml
   ```
   Exports data in YAML format:
   - regions.yml
   - subregions.yml
   - countries.yml
   - states.yml
   - cities.yml

5. **SQL Server Export**
   ```bash
   php console export:sql-server
   ```
   Exports data in SQL Server format with proper schema and data.

6. **NPM Package Export**
   ```bash
   php console export:csc-npm
   ```
   Exports data in NPM package format:
   - country.json
   - state.json
   - city.json

7. **PLIST Export**
   ```bash
   php console export:plist
   ```
   Exports data in Apple Property List format using Python script.

### Database Management Commands

```bash
php console manage:create     # Create a new migration
php console manage:migrate    # Run migrations
php console manage:rollback   # Rollback migrations
php console manage:status     # Show migration status
php console manage:breakpoint # Set/unset breakpoint
php console seed:create      # Create a new seeder
php console seed:run         # Run database seeds
```

### Python Scripts

Python scripts are organized in `scripts/` directory by purpose. See [scripts/README.md](scripts/README.md) for detailed documentation.

#### Sync Scripts (`scripts/sync/`)
```bash
# MySQL → JSON (dynamic schema detection)
python3 scripts/sync/sync_mysql_to_json.py

# JSON → MySQL (auto schema updates)
python3 scripts/sync/import_json_to_mysql.py [--host HOST --user USER --password PASS]
```

#### Export Scripts (`scripts/export/`)
```bash
# DuckDB export
python3 scripts/export/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db

# Apple PLIST export
python3 scripts/export/export_plist.py
```

**Requirements**: `pip install mysql-connector-python duckdb`

**📚 Full Python scripts documentation**: See [scripts/README.md](scripts/README.md)

## Bidirectional Workflow

The repository now supports **two contribution workflows**:

### Workflow 1: JSON-First (For Contributors via GitHub Actions)
```bash
# 1. Edit JSON files in contributions/
vim contributions/cities/US.json

# 2. Commit and push
git add contributions/
git commit -m "feat: add new cities"
git push

# 3. GitHub Actions automatically:
#    - Imports to MySQL (import_json_to_mysql.py) - IDs auto-assigned by MySQL
#    - Exports from MySQL (php console export:json, export:csv, etc.)
#    - Creates PR with all updated exports
```

### Workflow 2: SQL-First (For Maintainers)
```bash
# 1. Start MySQL and edit database directly
sudo systemctl start mysql.service
mysql -uroot -proot world
# ... make your changes ...

# 2. Sync MySQL back to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py

# 3. Review and commit
git diff
git add contributions/
git commit -m "feat: add new cities to database"

# 4. Push - GitHub Actions will handle exports
git push
```

### Schema Evolution Handling

When you add NEW columns to your database or JSON:

**If you added column in MySQL:**
1. Run `python3 bin/scripts/sync/sync_mysql_to_json.py` - it will auto-detect and include new columns
2. Commit the updated JSON files

**If you added column in JSON:**
1. Run `python3 bin/scripts/sync/import_json_to_mysql.py` - it will auto-detect and add new columns to MySQL
2. The schema is updated automatically with proper data types

Both scripts use **dynamic schema detection** - no need to manually update code when adding fields!

## Configuration

1. **Environment Setup**
   - Copy `.env.example` to `.env`
   - Set `APP_ENVIRONMENT` (production/development)

2. **Database Configuration**
   - Update `config/app.yaml` with MySQL credentials
   - Update `config/phinx.yaml` for migration settings

## Requirements

```json
{
    "require": {
        "php": ">=8.1",
        "symfony/console": "^7.0",
        "symfony/filesystem": "^7.0",
        "symfony/process": "^7.0",
        "symfony/yaml": "^7.0",
        "spatie/array-to-xml": "^3.3.0",
        "monolog/monolog": "^3.7",
        "vlucas/phpdotenv": "^5.6",
        "hassankhan/config": "^3.1",
        "robmorgan/phinx": "^0.16.1"
    }
}
```

## Development

### Adding New Commands

1. Create a new command class in `Commands/` directory
2. Extend `Symfony\Component\Console\Command\Command`
3. Implement required methods:
   - `configure()`: Set command name and description
   - `execute()`: Command logic
4. Register in `bin/console`

Example:
```php
<?php
namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;

class NewExportCommand extends Command
{
    protected static $defaultName = 'export:new-format';
    protected static $defaultDescription = 'Export data to new format';

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to a new format');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        // Implementation
        return Command::SUCCESS;
    }
}
```

### Best Practices

1. Use strict types and type declarations
2. Implement proper error handling
3. Use Symfony components (Filesystem, Process)
4. Follow PSR-12 coding standards
5. Add command descriptions and help text
6. Use SymfonyStyle for consistent output
7. Implement proper resource cleanup

## Error Handling

Commands implement comprehensive error handling for:
- File system operations
- Database connections
- Data parsing
- Process execution

Exit codes:
- `0`: Success
- `1`: General error
- `2`: Misuse of shell builtins
