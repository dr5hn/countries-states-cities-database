# Changelog Generator Scripts

Automated system for generating changelogs from `contributions/` folder changes.

## 📁 Scripts

### Core Generator
- **`changelog_generator.py`** - Main CLI entry point
  - Usage: `python3 bin/scripts/changelog/changelog_generator.py [OPTIONS]`
  - Orchestrates the entire changelog generation process

### Analyzers
- **`json_analyzer.py`** - Analyzes JSON diffs from contributions/
  - Detects additions, updates, and deletions
  - Matches objects by ID and name

- **`git_parser.py`** - Extracts git commit history
  - Tracks changes in contributions/ folder
  - Returns file diffs for each changed file

### Processors
- **`changelog_writer.py`** - Generates JSON changelog files
  - Creates per-country files
  - Generates global changelog and statistics
  - Writes minified JSON

- **`deduplicator.py`** - Prevents duplicate entries
  - Hashes changes to detect duplicates
  - Maintains seen set across commits

- **`archiver.py`** - Manages retention and archiving
  - Applies 24-month retention policy
  - Archives old changes by year

### Utilities
- **`utils.py`** - Shared helper functions
  - Configuration loading
  - Date formatting
  - JSON operations

### Legacy
- **`sql_analyzer.py`** - SQL diff analyzer (deprecated)
  - Previously used for world.sql tracking
  - Kept for reference

## 🚀 Usage

```bash
# Generate changelogs
python3 bin/scripts/changelog/changelog_generator.py

# With options
python3 bin/scripts/changelog/changelog_generator.py \
  --retention-months 6 \
  --since 2025-10-01 \
  --show-sizes

# Dry run
python3 bin/scripts/changelog/changelog_generator.py --dry-run
```

## 📝 Configuration

Edit `config/changelog.json`:
```json
{
  "target_paths": [
    "contributions/cities/",
    "contributions/states/states.json",
    "contributions/countries/countries.json"
  ],
  "retention_months": 24,
  "minify_json": true
}
```

## 📦 Dependencies

Install from `requirements-changelog.txt`:
```bash
pip install -r bin/scripts/changelog/requirements-changelog.txt
```

## 🔄 Automation

GitHub Actions workflow (`.github/workflows/generate-changelog.yml`):
- Triggers on changes to `contributions/**`
- Generates changelogs
- Creates PR in changelog repository

## 📖 Documentation

See project root for full documentation:
- `.github/agent-docs/CHANGELOG_SYSTEM.md` - Complete documentation
