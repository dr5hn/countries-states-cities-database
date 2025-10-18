# Agent Documentation Index

📚 **Complete guide for AI agents working with this geographical database.**

## 🚀 Quick Start (Read in This Order)

### For ALL AI Agents (GitHub Copilot, Claude Code, etc.)

1. **⭐ START HERE:** `AI_AGENT_BEST_PRACTICES.md`
   - Complete workflows for all common tasks
   - **CRITICAL:** Timezone and translation enrichment requirements
   - Tool usage examples with real commands
   - Quality checklist and success criteria
   - Common mistakes to avoid
   - **READ THIS FIRST - IT WILL SAVE YOU HOURS!**

2. **Study Examples:** `../fixes-docs/*.md`
   - Review at least 2-3 fix documentation examples
   - See: `AFGHANISTAN_MISSING_WARDAK_PROVINCE.md` for excellent example
   - Learn the pattern: problem → solution → validation → documentation

3. **Workflow Guide:** `../copilot-instructions.md`
   - JSON-first workflow
   - Database operations
   - Export commands
   - Schema reference

4. **Tool Reference:** This page (INDEX.md)
   - Overview of all available tools
   - When to use each tool

5. **Technical Deep Dive:** `../../.claude/CLAUDE.md`
   - Architecture details
   - Two-phase build system
   - Performance expectations

## 📁 Files in This Directory

### AI_AGENT_BEST_PRACTICES.md ⭐
**The single most important file for AI agents.**

**What it contains:**
- ✅ **Mandatory enrichment workflow** - Never skip timezone and translations!
- ✅ **Complete task workflows** - Step-by-step for adding cities, states, countries
- ✅ **Tool usage examples** - Real commands you can copy-paste
- ✅ **Quality standards** - What "excellent" vs "poor" data looks like
- ✅ **Documentation requirements** - How to document your changes
- ✅ **Common mistakes** - What NOT to do

**When to read:** Before starting ANY task

### WIKIPEDIA_API_DOCS.md
**HTTP API reference for Wikipedia (fallback method).**

**What it contains:**
- Raw Wikipedia API endpoint examples
- Query parameters and response formats
- Example URLs for articles, searches, images
- Useful when Wikipedia-API package isn't available

**When to use:**
- As reference for understanding Wikipedia API
- Fallback if Wikipedia-API Python package fails
- Understanding coordinate extraction from API responses

### WIKIPEDIA_MCP.md
**Model Context Protocol server documentation (LOCAL DEV ONLY).**

**What it contains:**
- Wikipedia MCP server features and installation
- Configuration for Claude Desktop
- Multi-language support
- Tool and resource documentation

**When to use:**
- ❌ **NOT for GitHub Copilot agents** (MCP not available in CI/CD)
- ✅ For local development with Claude Desktop
- ✅ As reference for MCP capabilities

**Important:** This is reference only for GitHub Actions/Copilot agents!

## 🛠️ Available Tools

### Validation & Enrichment Tools

Located in: `bin/scripts/validation/`

#### 1. Wikipedia Validator (`wikipedia_validator.py`)
**Validates geographical data against Wikipedia.**

```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Paris" \
    --type city \
    --country FR \
    --language fr \
    --output validation_report.json
```

**Use for:**
- Verifying city/state/country names
- Getting accurate coordinates
- Finding WikiData IDs
- Cross-referencing data accuracy

**Dependencies:** Wikipedia-API

#### 2. Timezone Enricher (`timezone_enricher.py`)
**Automatically adds IANA timezone based on coordinates.**

```bash
# For cities in a specific country
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/DE.json \
    --type city

# For states of a specific country
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code DE
```

**Use for:**
- Adding timezone to new entries
- Fixing incorrect timezones
- Bulk timezone enrichment
- **ALWAYS run after adding new entries!**

**Dependencies:** timezonefinder

#### 3. Translation Enricher (`translation_enricher.py`)
**Fetches translations from Wikipedia in 18+ languages.**

```bash
# Add translations (test with --limit first)
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/FR.json \
    --type city \
    --limit 10

# Then run for all
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/FR.json \
    --type city
```

**Use for:**
- Adding translations to new entries
- Enriching existing entries
- **ALWAYS run for major cities/states!**

**Supported languages:**
Arabic (ar), Bengali (bn), German (de), Spanish (es), French (fr), Hindi (hi), Indonesian (id), Italian (it), Japanese (ja), Korean (ko), Dutch (nl), Polish (pl), Portuguese (pt), Russian (ru), Turkish (tr), Ukrainian (uk), Vietnamese (vi), Chinese (zh)

**Dependencies:** Wikipedia-API

### Tool Dependencies

All tools are **pre-installed in GitHub Actions**:

```bash
# Installed automatically by copilot-setup-steps.yml
pip install Wikipedia-API timezonefinder mysql-connector-python
```

For local development:
```bash
cd bin/scripts/validation
pip install -r requirements.txt
```

## 🎯 Mandatory Workflow for AI Agents

### When Adding/Updating ANY Data

**ALWAYS follow this sequence:**

```bash
# 1. Add data to contributions/ JSON files (without id, timezone, translations)

# 2. Enrich with timezone
python3 bin/scripts/validation/timezone_enricher.py \
    --file contributions/cities/XX.json \
    --type city

# 3. Enrich with translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/XX.json \
    --type city

# 4. Validate with Wikipedia
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "City Name" \
    --type city \
    --country XX

# 5. Import to MySQL (assigns IDs)
python3 bin/scripts/sync/import_json_to_mysql.py

# 6. Sync back to JSON (updates IDs)
python3 bin/scripts/sync/sync_mysql_to_json.py

# 7. Create documentation in .github/fixes-docs/

# 8. Commit changes
```

**⚠️ Skipping steps 2-3 (timezone and translations) is NOT ACCEPTABLE!**

## 📊 Data Quality Standards

### Excellent Entry (Target This)

```json
{
  "id": 12345,
  "name": "Munich",
  "state_id": 3006,
  "state_code": "BY",
  "country_id": 82,
  "country_code": "DE",
  "latitude": "48.13512690",
  "longitude": "11.58197940",
  "native": "München",
  "timezone": "Europe/Berlin",
  "translations": {
    "ar": "ميونخ",
    "de": "München",
    "es": "Múnich",
    "fr": "Munich",
    "hi": "म्यूनिख",
    "it": "Monaco di Baviera",
    "ja": "ミュンヘン",
    "ko": "뮌헨",
    "pt": "Munique",
    "ru": "Мюнхен",
    "zh": "慕尼黑"
  },
  "wikiDataId": "Q1726"
}
```

✅ Has timezone
✅ Has 11 translations
✅ Has WikiData ID
✅ Has native name

### Poor Entry (Avoid This)

```json
{
  "name": "Some City",
  "country_code": "XX",
  "latitude": "12.34",
  "longitude": "56.78"
}
```

❌ No timezone
❌ No translations
❌ No WikiData ID
❌ Missing foreign keys

## 📚 Complete Documentation Structure

```
.github/
├── agent-docs/                    # For AI agents
│   ├── INDEX.md                  # This file
│   ├── AI_AGENT_BEST_PRACTICES.md ⭐ START HERE
│   ├── WIKIPEDIA_API_DOCS.md     # API reference
│   └── WIKIPEDIA_MCP.md          # MCP reference (local dev)
│
├── fixes-docs/                    # Examples to study
│   ├── AFGHANISTAN_MISSING_WARDAK_PROVINCE.md
│   ├── FIX_1019_SUMMARY.md
│   └── ...
│
└── copilot-instructions.md       # Workflow guide

.claude/
└── CLAUDE.md                     # Technical deep dive

bin/
└── scripts/
    └── validation/
        ├── README.md              # Tool documentation
        ├── wikipedia_validator.py
        ├── timezone_enricher.py
        └── translation_enricher.py
```

## 🎓 Learning Path

### Beginner AI Agent

1. Read `AI_AGENT_BEST_PRACTICES.md` (30 minutes)
2. Study 2-3 examples in `fixes-docs/` (20 minutes)
3. Read `../copilot-instructions.md` (15 minutes)
4. Practice with a simple task (adding 1-2 cities)

### Experienced AI Agent

1. Skim `AI_AGENT_BEST_PRACTICES.md` for refresher
2. Jump to specific task workflow in best practices
3. Use tools as needed
4. Document following `fixes-docs/` patterns

## ⚠️ Common Pitfalls

1. **Skipping timezone/translation enrichment** → Tools are required, not optional!
2. **Not reading AI_AGENT_BEST_PRACTICES.md** → Will make mistakes that could be avoided
3. **Ignoring fixes-docs examples** → Will create poor documentation
4. **Hardcoding IDs** → Let MySQL AUTO_INCREMENT assign them
5. **Not validating with Wikipedia** → Data accuracy issues
6. **Committing without documentation** → Changes won't be accepted

## ✅ Success Checklist

Before completing any task:

- [ ] Read `AI_AGENT_BEST_PRACTICES.md`
- [ ] Ran `timezone_enricher.py` on new/updated data
- [ ] Ran `translation_enricher.py` on new/updated data
- [ ] Validated with `wikipedia_validator.py`
- [ ] All entries have WikiData IDs
- [ ] Created documentation in `fixes-docs/`
- [ ] Ran import → sync workflow
- [ ] JSON files are valid
- [ ] Cited sources (Wikipedia, WikiData)
- [ ] Provided before/after counts

## 🔗 Quick Links

### Most Important
- [AI Agent Best Practices](AI_AGENT_BEST_PRACTICES.md) ⭐
- [Copilot Instructions](../copilot-instructions.md)
- [Fix Documentation Examples](../fixes-docs/)

### Tool Documentation
- [Validation Tools README](../../bin/scripts/validation/README.md)
- [Wikipedia API Docs](WIKIPEDIA_API_DOCS.md)

### Technical Reference
- [Claude Documentation](../../.claude/CLAUDE.md)
- [Export Commands](../../bin/README.md)
- [Contributions Guide](../../contributions/README.md)

## 💡 Pro Tips

1. **Start small** - Test with `--limit 10` when using translation enricher
2. **Validate first** - Use wikipedia_validator before adding data
3. **Study examples** - The fixes-docs/ directory is your best teacher
4. **Use the tools** - They're faster and more accurate than manual work
5. **Document well** - Good documentation helps reviewers approve faster
6. **Follow patterns** - Don't reinvent the wheel, copy what works

## 📞 Still Have Questions?

1. Check `AI_AGENT_BEST_PRACTICES.md` - Answers 90% of questions
2. Review examples in `fixes-docs/` - See how others solved problems
3. Read tool READMEs in `bin/scripts/validation/` - Detailed usage examples
4. Consult `.claude/CLAUDE.md` - Deep technical details

**Remember:** The documentation exists to help you succeed. Use it! 🚀
