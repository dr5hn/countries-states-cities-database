# Changelog System Documentation

## Overview

The Changelog System automatically tracks all changes to the `world.sql` database by analyzing git commit history and generating per-country JSON changelog files, deployed to a GitHub Pages website.

## Architecture

### Components

1. **Python Scripts** (`scripts/changelog/`)
   - `git_parser.py` - Extracts commits from git history
   - `sql_analyzer.py` - Parses SQL diffs to extract changes
   - `changelog_writer.py` - Generates minified JSON files
   - `deduplicator.py` - Prevents duplicate entries
   - `archiver.py` - Manages retention and archives
   - `changelog_generator.py` - Main CLI orchestrator
   - `utils.py` - Shared utilities

2. **GitHub Pages Site** (`site/`)
   - Interactive web interface at changelog.countrystatecity.in
   - Country browser with search
   - Timeline view
   - Statistics dashboard

3. **Automation** (`.github/workflows/generate-changelog.yml`)
   - Triggers on changes to `sql/world.sql`
   - Generates changelogs
   - Deploys to `changelogs-data` orphan branch
   - Publishes to GitHub Pages

## 🔄 Automation Flow

```
Developer edits contributions/cities/NG.json
  ↓
Adds new city to JSON array
  ↓
Git commit & push
  ↓
GitHub Action triggers
  ↓
JSON Analyzer detects addition
  ↓
Generates changelog entry with action: "add"
  ↓
Creates PR in changelog repo
  ↓
Merge & deploy to changelog.countrystatecity.in
```

## Data Flow

```
git commits → git_parser → sql_analyzer → deduplicator → changelog_writer → JSON files
                                                              ↓
                                                         archiver
                                                              ↓
                                            changelogs-data branch → GitHub Pages
```

## Configuration

### `config/changelog.json`

```json
{
  "retention_months": 24,
  "minify_json": true,
  "archive_enabled": true,
  "archive_by_year": true,
  "compact_field_names": false,
  "max_global_recent_changes": 100,
  "max_changes_per_file": 1000,
  "exclude_fields": ["author_email"],
  "output_dir": "changelogs",
  "target_file": "sql/world.sql",
  "archive_branch": "changelogs-data",
  "github_pages_enabled": true
}
```

### Configuration Options

- **retention_months**: Number of months to keep in main files (default: 24)
- **minify_json**: Remove whitespace from JSON (default: true)
- **archive_enabled**: Enable archiving old changes (default: true)
- **archive_by_year**: Group archives by year (default: true)
- **compact_field_names**: Use abbreviated field names (default: false)
- **max_global_recent_changes**: Max changes in global changelog (default: 100)
- **max_changes_per_file**: Split large files if exceeded (default: 1000)
- **exclude_fields**: Fields to exclude from output

## Usage

### Local Generation

```bash
# Install dependencies
pip install -r bin/scripts/changelog/requirements-changelog.txt

# Generate changelogs (dry run)
python3 bin/scripts/changelog/changelog_generator.py --dry-run

# Generate with full history
python3 bin/scripts/changelog/changelog_generator.py

# Generate for specific country
python3 bin/scripts/changelog/changelog_generator.py --country US

# Generate with custom retention
python3 bin/scripts/changelog/changelog_generator.py --retention-months 12

# Generate since specific date
python3 bin/scripts/changelog/changelog_generator.py --since 2025-01-01

# Show file sizes
python3 bin/scripts/changelog/changelog_generator.py --show-sizes
```

### CLI Options

```
--config PATH           Configuration file (default: config/changelog.json)
--repo-path PATH        Git repository path (default: .)
--output-dir PATH       Output directory override
--country CODE          Generate for specific country only
--since DATE            Process commits since date (YYYY-MM-DD)
--retention-months N    Retention period override
--full                  Process full git history
--no-archive            Disable archiving
--minify/--prettify     JSON minification override
--dry-run               Preview without writing files
--show-sizes            Display file sizes after generation
```

## Output Structure

```
changelogs/
├── countries/              # Per-country changelogs
│   ├── US.json            # United States (minified)
│   ├── IN.json            # India
│   └── ...
├── archives/              # Archived changes (older than retention)
│   ├── 2023/
│   │   ├── US.json
│   │   └── ...
│   ├── 2024/
│   └── index.json         # Archive index
├── global-changelog.json  # Recent 100 changes
├── stats.json             # Statistics
└── README.md              # Auto-generated docs
```

## JSON Schema

### Per-Country Changelog

```json
{
  "version": "1.0.0",
  "country_code": "US",
  "country_name": "United States",
  "last_updated": "2025-10-26T12:34:56Z",
  "total_changes": 145,
  "changes": [
    {
      "id": "c7f3a92b",
      "timestamp": "2025-10-15T09:23:11Z",
      "commit_sha": "c7f3a92b4e8d9f2a1c5b6e7d8a9f0b1c2d3e4f5a",
      "author": "John Doe",
      "action": "add",
      "entity_type": "city",
      "entity": {
        "id": 12345,
        "name": "Springfield",
        "state_code": "IL",
        "country_code": "US",
        "latitude": 39.7817,
        "longitude": -89.6501
      },
      "changes": {
        "added": {
          "name": "Springfield",
          "state_id": 14,
          "latitude": 39.7817,
          "longitude": -89.6501
        }
      },
      "message": "Add Springfield, Illinois"
    }
  ]
}
```

### Field Definitions

- **version**: Schema version
- **country_code**: ISO 2-letter country code
- **country_name**: Full country name
- **last_updated**: ISO 8601 timestamp of generation
- **total_changes**: Number of changes in file
- **changes**: Array of change objects
  - **id**: Short change identifier (8-char SHA)
  - **timestamp**: When change was committed
  - **commit_sha**: Full git commit SHA
  - **author**: Commit author name
  - **action**: `add`, `update`, or `delete`
  - **entity_type**: `city`, `state`, or `country`
  - **entity**: Current entity data
  - **changes**: Specific modifications
  - **message**: Commit message

## GitHub Pages Website

### Deployment

The website is automatically deployed to the `changelogs-data` orphan branch and hosted at `https://changelog.countrystatecity.in`.

### Features

1. **Home Page** (`index.html`)
   - Overview and statistics
   - Quick access links

2. **Browse Page** (`browse.html`)
   - Search countries
   - Filter by action/entity type
   - View detailed changes

3. **Timeline** (`timeline.html`)
   - Recent 100 changes
   - Chronological view
   - Relative timestamps

4. **Statistics** (`stats.html`)
   - Overall summary
   - Top countries by changes
   - Action/entity distribution

### API Access

All data is available as JSON:

```javascript
// Fetch country changelog
const response = await fetch(
  'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/changelogs-data/changelogs/countries/US.json'
);
const data = await response.json();

// Fetch global changelog
const global = await fetch(
  'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/changelogs-data/changelogs/global-changelog.json'
);

// Fetch statistics
const stats = await fetch(
  'https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/changelogs-data/changelogs/stats.json'
);
```

## Retention & Archiving

### Retention Policy

- **Active**: Last 24 months in main changelog files
- **Archived**: Older changes moved to `archives/YYYY/` directories
- **Configurable**: Adjust retention period via config

### Archive Process

1. Changes older than retention period are identified
2. Grouped by year
3. Written to year-specific directories
4. Index file created for navigation
5. Main files contain only recent changes

### Storage Strategy

- Main changelog files in `changelogs-data` branch
- Keeps main branch clean (no large data files)
- GitHub Pages serves static JSON files
- Optional: Use GitHub Releases for large archives

## Automation

### GitHub Actions Workflow

Triggers:
- Push to `master` branch (when `sql/world.sql` changes)
- Manual workflow dispatch

Steps:
1. Checkout with full history
2. Install Python dependencies
3. Run changelog generator
4. Create/update `changelogs-data` orphan branch
5. Copy changelog files + website
6. Deploy to GitHub Pages
7. Report summary

### Manual Trigger

```bash
# Via GitHub UI
Actions → Generate Data Changelogs → Run workflow

# Via GitHub CLI
gh workflow run generate-changelog.yml
```

## Troubleshooting

### No Changes Generated

- Verify `sql/world.sql` has commits
- Check git history: `git log -- sql/world.sql`
- Run with `--dry-run` to see what would be generated

### Large File Sizes

- Reduce `retention_months`
- Enable archiving
- Use `compact_field_names: true`

### Missing Countries

- Check if country_code is present in entity data
- Verify SQL table column mappings
- Review `sql_analyzer.py` column definitions

### Workflow Failures

- Check Python dependency installation
- Verify git fetch depth is 0 (full history)
- Review workflow logs for specific errors

## Development

### Adding New Features

1. **New Export Format**: Extend `changelog_writer.py`
2. **Additional Filters**: Update SQL analyzer patterns
3. **UI Enhancements**: Modify site HTML/CSS/JS
4. **New Statistics**: Add to stats generation

### Testing

```bash
# Dry run to test logic
python3 scripts/changelog/changelog_generator.py --dry-run

# Test specific commit range
python3 scripts/changelog/changelog_generator.py --since 2025-10-01

# Test single country
python3 scripts/changelog/changelog_generator.py --country US

# Preview output
python3 scripts/changelog/changelog_generator.py --prettify
```

### Code Structure

- **Modular**: Each script has single responsibility
- **Type Hints**: Python type annotations throughout
- **Error Handling**: Comprehensive try/catch blocks
- **Logging**: Click-based progress indicators
- **Configuration**: Centralized in JSON file

## Performance

### Optimization Techniques

1. **Minified JSON**: ~27% size reduction
2. **Rolling Window**: 24-month retention
3. **Deduplication**: Prevents duplicate entries
4. **Streaming**: Processes commits incrementally
5. **Caching**: Reuses parsed data

### Benchmarks

- **Commits**: 403 commits processed in ~5 seconds
- **Changes**: 150K+ changes extracted in ~10 seconds
- **JSON Generation**: 244 country files in ~2 seconds
- **Total Runtime**: ~20 seconds for full history

## Future Enhancements

- [ ] GraphQL API for querying changes
- [ ] Email notifications for specific countries
- [ ] RSS feeds for changes
- [ ] Data visualization charts
- [ ] Export to CSV/Excel
- [ ] Change comparison tool
- [ ] Bulk download of archives

## Support

For issues or questions:
- GitHub Issues: https://github.com/dr5hn/countries-states-cities-database/issues
- Website: https://changelog.countrystatecity.in
