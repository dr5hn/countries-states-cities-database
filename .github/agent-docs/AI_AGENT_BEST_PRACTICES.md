# AI Agent Best Practices for Countries States Cities Database

## 📋 Overview

This guide provides AI agents (GitHub Copilot, Claude Code, etc.) with best practices for working with this geographical database. Following these practices ensures data quality, consistency, and completeness.

## 🎯 Core Principles

### 1. Always Enrich Data Completely

When adding or updating ANY geographical entity (city, state, country), **ALWAYS** include:

#### ✅ Required Fields
- `name` - Official name
- `country_code` - ISO 2-letter code
- `country_id` - Foreign key reference
- `latitude` - Decimal degrees (string format)
- `longitude` - Decimal degrees (string format)

#### ✅ Highly Recommended Fields
- **`timezone`** - IANA timezone identifier (e.g., "America/New_York", "Europe/Paris")
- **`translations`** - Object with language codes as keys (at least 5-10 major languages)
- **`wikiDataId`** - Wikidata identifier (e.g., "Q60" for New York City)
- **`native`** - Native language name (if different from English)

#### ✅ Additional Fields (when available)
- For states: `iso2`, `type`, `population`
- For cities: `state_id`, `state_code`

### 2. Automatic Enrichment Workflow

**CRITICAL**: Never skip timezone and translations. Use these automated tools:

```bash
# Step 1: Add your data to contributions/ (without timezone/translations)
# Step 2: Run timezone enrichment
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/US.json \
    --type city

# Step 3: Run translation enrichment
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/US.json \
    --type city \
    --limit 10  # Remove --limit for all records

# Step 4: Validate with Wikipedia
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "New York City" \
    --type city \
    --country US \
    --output validation_report.json
```

### 3. Data Quality Checklist

Before committing ANY changes, verify:

- [ ] All new records have `timezone` field
- [ ] All new records have `translations` object (even if empty)
- [ ] All coordinates are in decimal format (not DMS)
- [ ] All foreign keys (`country_id`, `state_id`) are valid
- [ ] WikiData IDs are verified (check https://www.wikidata.org/)
- [ ] Names match official sources (Wikipedia, government sites)
- [ ] No duplicate entries
- [ ] JSON is valid (no syntax errors)

## 🛠️ Available Tools

### Validation Tools

#### 1. Wikipedia Validator
Validates names, coordinates, and fetches WikiData IDs.

```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Paris" \
    --type city \
    --country FR \
    --language fr \
    --output paris_report.json
```

**When to use:**
- Verifying city/state/country names
- Getting coordinates for new entries
- Finding WikiData IDs
- Cross-referencing data accuracy

#### 2. Timezone Enricher
Automatically adds IANA timezone based on coordinates.

```bash
# For a city file
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/DE.json \
    --type city

# For states (specific country)
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code DE

# Force update existing timezones
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/FR.json \
    --type city \
    --force-update
```

**When to use:**
- Adding new cities without timezone
- Updating incorrect timezones
- Bulk timezone enrichment for a country
- **ALWAYS** run this after adding new entries

#### 3. Translation Enricher
Fetches translations from Wikipedia in 18+ languages.

```bash
# Add translations for all cities in a file
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/JP.json \
    --type city

# Test with limited records first
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/CN.json \
    --type city \
    --limit 10

# Specific languages only
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code FR \
    --languages fr de es it

# Force update existing translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/ES.json \
    --type city \
    --force-update
```

**When to use:**
- Adding new entries
- Enriching existing entries without translations
- **ALWAYS** run this for major cities/states
- Before finalizing any PR

**Supported languages:**
Arabic (ar), Bengali (bn), German (de), Spanish (es), French (fr), Hindi (hi), Indonesian (id), Italian (it), Japanese (ja), Korean (ko), Dutch (nl), Polish (pl), Portuguese (pt), Russian (ru), Turkish (tr), Ukrainian (uk), Vietnamese (vi), Chinese (zh)

## 📚 Required Reading for AI Agents

### Before Starting Any Task

**MUST READ** these documents in this order:

1. **`.github/copilot-instructions.md`** - General workflow and rules
2. **`.github/agent-docs/README.md`** - Tool overview
3. **`.github/agent-docs/AI_AGENT_BEST_PRACTICES.md`** - This file
4. **`.github/fixes-docs/*.md`** - Review at least 2-3 examples to understand:
   - Documentation format
   - Validation steps
   - Common patterns
   - How to cite sources

### Example Documentation to Study

**Excellent examples** from `.github/fixes-docs/`:

- `AFGHANISTAN_MISSING_WARDAK_PROVINCE.md` - Shows proper state + cities addition with timezone and translations
- `FIX_1019_SUMMARY.md` - Shows comprehensive fix documentation
- `POLAND_CITIES_FIX.md` - Shows data cleanup methodology

**Key takeaways from these examples:**
- ✅ Always include WikiData IDs
- ✅ Always include timezone information
- ✅ Always include native names
- ✅ Include before/after counts
- ✅ List all validation steps performed
- ✅ Cite Wikipedia/WikiData sources

## 🔄 Complete Workflow for Common Tasks

### Task 1: Adding a New City

```bash
# 1. Research the city
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Munich" \
    --type city \
    --country DE \
    --output munich_report.json

# Review output for:
# - Official name
# - Coordinates
# - WikiData ID

# 2. Add city to contributions/cities/DE.json (without id, timezone, translations)
{
  "name": "Munich",
  "state_id": 3006,
  "state_code": "BY",
  "country_id": 82,
  "country_code": "DE",
  "latitude": "48.13512690",
  "longitude": "11.58197940",
  "native": "München",
  "wikiDataId": "Q1726"
}

# 3. Enrich with timezone
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/DE.json \
    --type city

# 4. Enrich with translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/DE.json \
    --type city \
    --limit 1  # Just the new city for testing

# 5. Verify the result in DE.json
# Should now have timezone and translations fields

# 6. Import to MySQL to get ID assigned
python3 bin/scripts/sync/import_json_to_mysql.py

# 7. Sync back to get the ID
python3 bin/scripts/sync/sync_mysql_to_json.py

# 8. Commit with proper documentation
```

### Task 2: Adding a New State + Cities

```bash
# 1. Add state to contributions/states/states.json
{
  "name": "New Province",
  "country_id": 123,
  "country_code": "XX",
  "iso2": "NP",
  "latitude": "12.34567890",
  "longitude": "56.78901234",
  "native": "Native Name"
}

# 2. Enrich state with timezone
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code XX

# 3. Enrich state with translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code XX

# 4. Import to MySQL to assign state ID
python3 bin/scripts/sync/import_json_to_mysql.py
python3 bin/scripts/sync/sync_mysql_to_json.py

# 5. Note the state_id from states.json

# 6. Add cities to contributions/cities/XX.json
# Use the state_id from step 5

# 7. Enrich cities with timezone and translations
python3 bin/scripts/validation/timezone_enricher.py --file contributions/cities/XX.json --type city
python3 bin/scripts/validation/translation_enricher.py --file contributions/cities/XX.json --type city

# 8. Final import and sync
python3 bin/scripts/sync/import_json_to_mysql.py
python3 bin/scripts/sync/sync_mysql_to_json.py
```

### Task 3: Fixing Missing Timezones (Batch)

```bash
# For a specific country's cities
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/FR.json \
    --type city

# For a specific country's states
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code FR

# Commit the changes
```

### Task 4: Adding Missing Translations (Batch)

```bash
# For major cities only (test first with --limit)
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/IT.json \
    --type city \
    --limit 50  # Top 50 cities

# Review results, then run for all
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/IT.json \
    --type city

# Commit the changes
```

## 📝 Documentation Requirements

### For EVERY Fix/Addition

Create **ONE** markdown file in `.github/fixes-docs/`:

**Naming:** `FIX_<issue_number>_SUMMARY.md` or `<TOPIC>_<ACTION>.md`

**Required sections:**

```markdown
# [Title of Fix]

## Issue Reference
**Title:** [Link to GitHub issue if applicable]
**Problem:** Brief description

## Countries/Regions Addressed
- Country 1
- Country 2

## Changes Made

### [Section for each change]
- Before count: X
- After count: Y
- Fields added: timezone, translations, wikiDataId

## Validation Steps

### 1. Validation Step Name
```bash
# Command used
command here
```
Expected result: ...
Actual result: ...

### 2. Another Validation Step
...

## Data Samples

### State Entry
```json
{
  "id": 123,
  "name": "State Name",
  "timezone": "Asia/Kabul",
  "translations": {
    "ar": "النسخة العربية",
    "de": "Deutsche Version"
  },
  "wikiDataId": "Q12345"
}
```

## References
- Wikipedia: [link]
- WikiData: [link]
- ISO standard: [link if applicable]

## Impact
- API changes (if any)
- Breaking changes (if any)
- Data quality improvements
```

## 🚫 Common Mistakes to Avoid

### ❌ DON'T

1. **Skip timezone enrichment** - Always run `timezone_enricher.py`
2. **Skip translation enrichment** - Always run `translation_enricher.py` for major cities/states
3. **Add entries without WikiData IDs** - Verify on wikidata.org
4. **Use DMS coordinates** - Always use decimal degrees
5. **Leave translations field empty for major cities** - At minimum, add 5-10 languages
6. **Forget to sync between JSON and MySQL** - Always run both import and sync commands
7. **Skip validation** - Always validate with Wikipedia
8. **Commit without documentation** - One markdown file per fix in `.github/fixes-docs/`
9. **Hardcode IDs** - Let MySQL AUTO_INCREMENT assign them
10. **Forget rate limiting** - Tools handle this automatically, but don't run them in tight loops

### ✅ DO

1. **Always enrich data** - Use all three tools: validator, timezone enricher, translation enricher
2. **Validate foreign keys** - Check that state_id and country_id exist
3. **Use proper workflow** - JSON → import → sync → commit
4. **Document everything** - One markdown file per issue in fixes-docs
5. **Test with limits first** - Use `--limit 10` when testing translation enricher
6. **Check for duplicates** - Before adding, search for existing entries
7. **Follow examples** - Study fixes-docs for patterns
8. **Cite sources** - Include Wikipedia and WikiData links
9. **Verify ISO codes** - Check against official ISO standards
10. **Run validation** - Before and after changes

## 🎓 Learning Resources

### For Understanding the Database

- `.claude/CLAUDE.md` - Complete technical documentation
- `.github/copilot-instructions.md` - Workflow and rules
- `contributions/README.md` - Field reference and examples

### For Understanding Data Quality

- `.github/fixes-docs/` - Real examples of proper fixes
- Study at least 3-5 examples before starting your task

### For Tool Usage

- `bin/scripts/validation/README.md` - Validation tools guide
- `.github/agent-docs/WIKIPEDIA_API_DOCS.md` - API reference
- `.github/agent-docs/README.md` - Tool overview

## 🔍 Quality Metrics

### Excellent Data Entry (Target)

```json
{
  "id": 12345,
  "name": "Paris",
  "state_id": 4796,
  "state_code": "11",
  "country_id": 75,
  "country_code": "FR",
  "latitude": "48.85661400",
  "longitude": "2.35222190",
  "native": "Paris",
  "timezone": "Europe/Paris",
  "translations": {
    "ar": "باريس",
    "de": "Paris",
    "es": "París",
    "fr": "Paris",
    "hi": "पैरिस",
    "it": "Parigi",
    "ja": "パリ",
    "ko": "파리",
    "pt": "Paris",
    "ru": "Париж",
    "zh": "巴黎"
  },
  "wikiDataId": "Q90"
}
```

**What makes this excellent:**
- ✅ Has timezone (Europe/Paris)
- ✅ Has 11 translations covering major languages
- ✅ Has WikiData ID (Q90)
- ✅ Has native name
- ✅ Coordinates in decimal format
- ✅ All foreign keys present

### Poor Data Entry (Avoid)

```json
{
  "name": "Some City",
  "country_code": "XX",
  "latitude": "12.34",
  "longitude": "56.78"
}
```

**What's wrong:**
- ❌ No timezone
- ❌ No translations
- ❌ No WikiData ID
- ❌ No native name
- ❌ Missing state_id, country_id
- ❌ Incomplete coordinates

## 🎯 Success Criteria

Before marking a task as complete, ensure:

1. ✅ All new/updated entries have timezone
2. ✅ All new/updated entries have translations (at least 5-10 languages for major cities)
3. ✅ All WikiData IDs verified
4. ✅ All coordinates validated against Wikipedia
5. ✅ JSON files pass validation (valid syntax)
6. ✅ MySQL import/sync completed successfully
7. ✅ Documentation created in `.github/fixes-docs/`
8. ✅ All validation steps documented
9. ✅ Sources cited (Wikipedia, WikiData, etc.)
10. ✅ Before/after counts provided

## 📞 Questions?

- Check `.github/copilot-instructions.md` first
- Review examples in `.github/fixes-docs/`
- See tool documentation in `bin/scripts/validation/README.md`
- Consult `.claude/CLAUDE.md` for technical details
