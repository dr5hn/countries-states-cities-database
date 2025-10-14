# Claude AI Agent Instructions — Countries States Cities Database

This repository maintains a global geographical dataset with countries, states/regions, and cities. You are working with a data-first pipeline where JSON files in `contributions/` are the source of truth, synced with MySQL and exported to multiple formats.

## Core Principles

1. **JSON-first workflow**: Edit `contributions/` JSON files for data changes
2. **Validate thoroughly**: Check counts, structure, and exports before committing
3. **Document everything**: All fixes and PRs must be documented in `.github/fixes-docs/`

## Quick Reference

### Repository Structure
- `contributions/` — Source JSON files (cities/*.json, states/states.json, countries/countries.json)
- `sql/world.sql` — Canonical MySQL dump
- `bin/` — PHP console + export commands (`bin/Commands/*.php`)
- `bin/scripts/sync/` — Python scripts for JSON ↔ MySQL synchronization
- `.github/fixes-docs/` — **Required documentation for all fixes and PRs**

### Key Commands

```bash
# Install PHP dependencies
cd bin && composer install --no-interaction --prefer-dist

# Seed MySQL locally
sudo systemctl start mysql.service
mysql -uroot -proot -e "CREATE DATABASE world CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -uroot -proot --default-character-set=utf8mb4 world < sql/world.sql

# Run exports (from bin/)
php console export:json
php console export:csv
php console export:xml
php console export:yaml

# Sync MySQL ↔ JSON
python3 bin/scripts/sync/import_json_to_mysql.py
python3 bin/scripts/sync/sync_mysql_to_json.py
```

### Data Validation

```bash
# Quick count checks
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities;"  # ~151k
mysql -uroot -proot -e "SELECT COUNT(*) FROM world.cities WHERE country_code = 'US';"  # ~19k

# Validate JSON structure
python3 -m json.tool contributions/cities/US.json > /dev/null && echo "Valid JSON"

# Check for duplicate IDs or empty fields
grep -o '"id":[^,]*' contributions/cities/US.json | sort | uniq -d
```

## Mandatory Documentation Protocol

**Every fix, PR, or significant change MUST be documented in `.github/fixes-docs/`.**

### Documentation Requirements

When you make changes:

1. **Create a Summary File** (mandatory)
   - Name: `FIX_<issue_number>_SUMMARY.md` or `<FEATURE_NAME>_SUMMARY.md`
   - Include:
     - Issue/PR reference
     - Executive summary
     - Countries/entities affected
     - Changes made (before/after with counts)
     - Examples of changed data
     - Validation results with commands

2. **Create Detailed Documentation** (for complex changes)
   - Name: `<COUNTRY_CODE>_<ISSUE_TYPE>.md` or similar
   - Include:
     - Detailed analysis
     - Step-by-step changes
     - Data samples (before/after)
     - Code snippets if applicable

### Documentation Template

```markdown
# Fix Summary: [Title]

## Issue Reference
**Original Issue:** [Issue link or description]

## Executive Summary
[Brief overview of what was fixed]

### Entities Addressed
1. **🇺🇸 Country Name** - [Status]
2. ...

---

## Changes Made

### Country Name 🇺🇸

**Problem:** [Description]

**Solution:** [What was done]

**Details:**
- **Before:** [counts/examples]
- **After:** [counts/examples]
- **Method:** [How it was fixed]

**Validation:**
- ✅ [Validation check 1]
- ✅ [Validation check 2]
- ...

## SQL/Code Examples
\```sql
-- Example validation query
SELECT COUNT(*) FROM cities WHERE country_code = 'US';
\```

## Files Changed
- `contributions/cities/US.json`
- ...
```

### Example Documentation

See existing files in `.github/fixes-docs/`:
- `FIX_1019_SUMMARY.md` — Comprehensive fix summary with multiple countries
- `POLAND_CITIES_FIX.md` — Detailed analysis of Poland administrative units issue
- `UK_CITIES_RESTRUCTURE.md` — Step-by-step UK data restructuring

## Do This ✅

1. **Edit `contributions/` JSON files** for data changes
2. **Omit `id` field** when adding new records (MySQL AUTO_INCREMENT handles it)
3. **Run sync scripts** after schema changes: `python3 bin/scripts/sync/import_json_to_mysql.py`
4. **Validate exports** locally before committing
5. **Document in `.github/fixes-docs/`** — this is MANDATORY
6. **Include before/after counts** in documentation
7. **Add validation commands** that others can run
8. **Use emojis** for country flags in documentation for clarity

## Do NOT Do ❌

1. **Do NOT skip documentation** — every PR needs `.github/fixes-docs/` entries
2. **Do NOT commit export artifacts** (`json/`, `csv/`, `yml/`, `xml/`, `sqlite/`, etc.)
3. **Do NOT edit `sql/world.sql` directly** — use JSON-first workflow
4. **Do NOT run exports** unless explicitly requested
5. **Do NOT guess** — validate with actual database queries and exports
6. **Do NOT make schema changes** without thorough testing and documentation

## Workflow for Fixes

### Standard Fix Workflow

1. **Analyze the issue**
   - Identify affected countries/entities
   - Gather current data counts
   - Understand the correct hierarchy

2. **Make changes**
   - Edit `contributions/` JSON files
   - Follow existing structure and patterns
   - Preserve valid `id` fields for existing records

3. **Validate locally**
   - Import to MySQL: `python3 bin/scripts/sync/import_json_to_mysql.py`
   - Check counts: `SELECT COUNT(*) FROM cities WHERE country_code = 'XX';`
   - Run sample exports: `php console export:json`

4. **Document thoroughly**
   - Create `FIX_<number>_SUMMARY.md` in `.github/fixes-docs/`
   - Include all validation results
   - Add before/after examples
   - List all affected files

5. **Commit and push**
   - Commit JSON changes
   - Commit documentation in `.github/fixes-docs/`
   - Push to feature branch
   - Documentation must be included in the PR

### Example Fix Process

```bash
# 1. Make changes to JSON
vim contributions/cities/PL.json

# 2. Validate JSON syntax
python3 -m json.tool contributions/cities/PL.json > /dev/null

# 3. Import to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py

# 4. Validate in database
mysql -uroot -proot -e "SELECT COUNT(*) FROM world.cities WHERE country_code = 'PL';"

# 5. Create documentation
vim .github/fixes-docs/FIX_1019_SUMMARY.md

# 6. Commit with both changes
git add contributions/cities/PL.json .github/fixes-docs/FIX_1019_SUMMARY.md
git commit -m "fix: Remove 314 powiats from Poland cities (Issue #1019)"
```

## Data Hierarchy

Understand the correct structure:

```
Regions (continents)
└── Subregions (geographical areas)
    └── Countries
        └── States/Provinces/Voivodeships (first-level subdivisions)
            └── Cities (municipalities, towns, villages)
```

**Not in database:**
- Counties (powiats, districts) — these are NOT in the cities table
- Administrative units below state level (unless they are actual cities)

## Important Notes

- **Cities table**: Should contain only municipalities, towns, villages — not administrative units
- **States table**: First-level subdivisions only (states, provinces, voivodeships)
- **New records**: Omit `id` field — it's auto-assigned during MySQL import
- **Character encoding**: Use UTF-8 (utf8mb4) for all text data
- **Validation**: Always include `SELECT COUNT(*)` queries in documentation

## Getting Help

- Check existing docs in `.github/fixes-docs/` for patterns
- Review `bin/Commands/ExportJson.php` for export logic
- Test changes locally before committing
- Include validation steps in PR documentation

---

**Remember: Documentation in `.github/fixes-docs/` is not optional — it's a required part of every PR.**
