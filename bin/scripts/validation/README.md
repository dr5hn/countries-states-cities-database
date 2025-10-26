# Validation Scripts

This directory contains scripts for validating and analyzing the timezone data quality in the countries-states-cities database.

## Scripts Overview

### 1. `validate_timezones.py` - Data Quality Validation

Validates the quality and correctness of timezone data in the database.

**Purpose:**
- Check for problematic `Etc/GMT*` timezones in states
- Verify state timezones exist in country definitions
- Validate against IANA timezone identifiers
- Check cities for timezone issues (with MySQL)

**Usage:**
```bash
# Basic validation
python3 bin/scripts/validation/validate_timezones.py

# Generate SQL fixes for problematic states
python3 bin/scripts/validation/validate_timezones.py --fix-states

# Also check cities (requires MySQL connection)
python3 bin/scripts/validation/validate_timezones.py --check-cities
```

**What it checks:**
- ✅ No `Etc/GMT*` timezones in states
- ✅ All state timezones exist in country definitions
- ✅ All timezones are valid IANA identifiers
- ✅ Optional: Cities timezone quality

**Expected output:**
```
✅ No timezone issues found!
   All timezones are properly formatted IANA identifiers
```

---

### 2. `analyze_missing_timezones.py` - IANA Coverage Analysis

Compares our timezone coverage against the complete IANA timezone database.

**Purpose:**
- Identify missing IANA timezones
- Categorize missing timezones (legacy, territories, recent additions)
- Assess population and coverage impact
- Generate recommendations

**Usage:**
```bash
# Run analysis
python3 bin/scripts/validation/analyze_missing_timezones.py

# Generate supplementary timezone JSON (not implemented yet)
python3 bin/scripts/validation/analyze_missing_timezones.py --generate-supplementary
```

**What it analyzes:**
- Total IANA timezone coverage percentage
- Missing Antarctica timezones
- Missing dependent territory timezones
- Legacy timezone aliases
- Recent IANA additions/renames
- Population impact assessment

**Expected output:**
```
Coverage: 97.9% (423/432 IANA common timezones)
Missing: 21 (4.9%)
- 14 legacy aliases (US/*, Canada/*)
- 2 recent additions (Kyiv, Ciudad_Juarez)
- 3 small territories
- 2 generic (GMT, UTC)
```

---

### 3. `add_timezones.py` - Automatic Timezone Population

Automatically adds IANA timezones to cities and states based on their coordinates.

**Purpose:**
- Fill missing timezone fields for cities/states
- Use coordinates to determine proper IANA timezone
- Filter out problematic `Etc/GMT*` timezones
- Batch process large datasets

**Usage:**
```bash
# Dry run (no changes) for cities
python3 bin/scripts/validation/add_timezones.py --table cities --limit 100 --dry-run

# Dry run for states
python3 bin/scripts/validation/add_timezones.py --table states --limit 100 --dry-run

# Process both cities and states
python3 bin/scripts/validation/add_timezones.py --table both

# Force update existing timezones
python3 bin/scripts/validation/add_timezones.py --table cities --force-update
```

**Requirements:**
- MySQL connection configured
- timezonefinder library installed
- Coordinates (latitude/longitude) present in records

**Note:** This script filters out `Etc/GMT*` timezones as they are not proper location-based timezones.

---

### 4. `wikipedia_validator.py` - Wikipedia Data Validation

Validates geographical data against Wikipedia and retrieves WikiData IDs.

**Purpose:**
- Verify city/state/country names
- Fetch official coordinates
- Retrieve WikiData identifiers
- Cross-reference population data
- Validate timezone information

**Usage:**
```bash
# Validate a city
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Paris" \
    --type city \
    --country FR \
    --output paris_report.json

# Validate a state
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "California" \
    --type state \
    --country US

# Use specific language Wikipedia
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "München" \
    --type city \
    --country DE \
    --language de
```

**What it retrieves:**
- Official names and alternate names
- Coordinates (latitude/longitude)
- WikiData ID
- Population data
- Timezone information
- Summary and categories

---

### 5. `translation_enricher.py` - Multilingual Translation Enrichment

Fetches translations for cities/states/countries from Wikipedia in multiple languages.

**Purpose:**
- Add translations in 18+ languages
- Fetch authentic Wikipedia article titles
- Support batch processing
- Rate-limited API calls

**Usage:**
```bash
# Add translations for cities (test with limit first)
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/FR.json \
    --type city \
    --limit 10

# Process all cities in a file
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/DE.json \
    --type city

# Specific languages only
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code JP \
    --languages ja ko zh

# Force update existing translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/ES.json \
    --type city \
    --force-update
```

**Supported languages:**
Arabic (ar), Bengali (bn), German (de), Spanish (es), French (fr), Hindi (hi), Indonesian (id), Italian (it), Japanese (ja), Korean (ko), Dutch (nl), Polish (pl), Portuguese (pt), Russian (ru), Turkish (tr), Ukrainian (uk), Vietnamese (vi), Chinese (zh)

---

## Related Analysis Scripts

### `bin/scripts/analysis/timezone_summary.py`

Generates comprehensive timezone distribution statistics.

**Usage:**
```bash
python3 bin/scripts/analysis/timezone_summary.py
```

**What it reports:**
- Overall timezone statistics
- Country-by-country breakdown
- Top 20 most used timezones
- Countries with multiple timezones
- Timezone mismatch detection

---

## Common Workflows

### Validate Timezone Data Quality

```bash
# Run all validation checks
python3 bin/scripts/validation/validate_timezones.py
python3 bin/scripts/validation/analyze_missing_timezones.py
python3 bin/scripts/analysis/timezone_summary.py
```

### Add Missing Timezones to Cities

```bash
# 1. Test with dry-run first
python3 bin/scripts/validation/add_timezones.py --table cities --limit 100 --dry-run

# 2. Process all cities
python3 bin/scripts/validation/add_timezones.py --table cities

# 3. Sync back to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py
```

### Enrich City Data Completely

```bash
# 1. Add timezone
python3 bin/scripts/validation/add_timezones.py --table cities

# 2. Add translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/US.json \
    --type city \
    --limit 50

# 3. Validate with Wikipedia
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "New York City" \
    --type city \
    --country US

# 4. Sync to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py
```

---

## Requirements

Install required Python packages:

```bash
pip install -r bin/scripts/validation/requirements.txt
```

Required packages:
- `pytz` - IANA timezone validation
- `timezonefinder` - Coordinate to timezone lookup
- `wikipediaapi` - Wikipedia API client
- `mysql-connector-python` - MySQL database access

---

## Documentation

For detailed information about timezone handling:
- [Timezone Guide](../../.github/agent-docs/TIMEZONE_GUIDE.md)
- [Timezone Coverage Validation](../../.github/fixes-docs/TIMEZONE_COVERAGE_VALIDATION.md)
- [AI Agent Best Practices](../../.github/agent-docs/AI_AGENT_BEST_PRACTICES.md)

---

## Validation Status

Current database validation results:

| Check | Status |
|-------|--------|
| Etc/GMT timezones in states | ✅ None found |
| State timezones in countries | ✅ All present |
| IANA timezone validity | ✅ All valid |
| State timezone coverage | ✅ 100% (5,070/5,070) |
| Country timezone coverage | ✅ 100% (250/250) |
| IANA coverage | ✅ 97.9% (423/432) |

**Last validated:** October 18, 2025

See [TIMEZONE_COVERAGE_VALIDATION.md](../../.github/fixes-docs/TIMEZONE_COVERAGE_VALIDATION.md) for detailed analysis.
