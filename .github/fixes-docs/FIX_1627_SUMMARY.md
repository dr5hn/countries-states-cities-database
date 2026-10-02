# FIX #1627 — `translations_capital` / `translations_currency_name` columns (foundation only)

**Issue:** [#1627 — Translation for country capitals and currency names](https://github.com/dr5hn/countries-states-cities-database/issues/1627)
**Scope:** New optional columns on the existing `countries` table.
**Date:** 2026-09-18

## What this PR includes (foundation only)

Following the same "foundation first, data later" shape as the `postcodes` table rollout ([FIX_1039_POSTCODES_TABLE.md](./FIX_1039_POSTCODES_TABLE.md)):

- Phinx migration: `bin/db/migrations/20260918000000_add_capital_currency_translations_to_countries.php` — idempotent (`hasColumn` guard, matching `20240708093950_add_languages_in_country.php`'s style), adds both columns as `text`, positioned after `translations`.
- Manual mirror in `bin/db/schema.sql` — `countries` table gains `translations_capital` and `translations_currency_name`, same `text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci` type as the existing `translations` column, so reviewers can read the schema without running Phinx.
- Validator support: both field names added to `SCHEMA.countries.optional` in `.github/scripts/utils.js`, so `validate-schema.js` doesn't flag them as unknown fields once contributors start adding data.

Both new columns store the same shape as the existing `translations` field — a JSON object keyed by language code, e.g. `{"fr": "...", "de": "...", ...}` — just for the country's capital name and currency name respectively, instead of the country name.

## Why `text`, not a hand-picked type

Checked `import_json_to_mysql.py`'s dynamic column-type inference (`infer_column_type`) before choosing a type: it has a hardcoded allowlist mapping `translations` (exact field name) to `TEXT`, which these new field names wouldn't match — but it also has a fallback rule (`isinstance(sample, dict) → TEXT`) that any dict-valued field hits regardless of name. Since both new fields hold JSON objects, they'd land on `TEXT` either way; the manual migration/schema.sql mirror keeps this explicit rather than relying on the fallback to fire correctly when the first real data lands.

## What this PR does NOT include (deliberate)

1. **Translation data** — no country record has these fields populated yet. The issue reporter explicitly offered to do the translation work ("I'm ready to start translating if you can tell me how to do it"); populating ~250 countries × ~19 languages × 2 fields is exactly that follow-up work, not something to fabricate here. All 250 countries already have non-empty `translations`, so the likely target is similar full coverage — but that's a large, source-dependent task (capital-city-name and currency-name translations need per-language verification, not guessing) that belongs to whoever's actually doing the sourcing.
2. **Export command updates** — correcting an inaccurate claim caught by Pullfrog's review: `bin/Commands/Export*.php` do query `countries` with `SELECT *`, but they then build each export record **field-by-field** (e.g. `ExportJson.php:65-93`: `$countriesArray[$m]['translations'] = $row['translations'] !== null ? json_decode($row['translations'], true) : null;`, repeated per known column). New, unlisted columns are **silently dropped from every export**, not passed through as raw/escaped strings as originally stated here. `ExportSqlServer.php` additionally has a hardcoded `CREATE TABLE` DDL (e.g. line 83, `translations NVARCHAR(MAX)`) that has no entry at all for the two new columns — that export would need its DDL updated too, not just a field-copy line. Wiring all of this — explicit field assignment + `json_decode` across every export format (JSON, CSV, XML, YAML, SQL, SQLite, SQL Server, MongoDB, Parquet) plus the SQL Server DDL — is mechanical but touches every export command file. Deferred to a follow-up PR, same reasoning the postcodes rollout used.
3. **`sync_mysql_to_json.py` reverse-sync changes** — correcting another inaccurate claim: this script **does** need a change, not "no evidence it needs changes" as originally stated here. Line 89 hardcodes which text columns get JSON-parsed on the way back out: `elif col in ['timezones', 'translations'] and isinstance(value, str):`. Without adding `translations_capital`/`translations_currency_name` to that allowlist, reverse-sync would write them into `contributions/countries/countries.json` as escaped JSON strings instead of nested objects, breaking the "same shape as `translations`" contract this PR's data model depends on. Deferred to the same follow-up PR as the export command wiring.

## Rollout Plan (Suggested)

| PR | Scope | Notes |
|----|-------|-------|
| **This PR** | Schema + validator support only | 0 data |
| Next | Export command wiring (`json_decode` for both fields, all 9 formats) | Mechanical, needs real data to verify against |
| Then | Translation data, country by country or in bulk | Community contribution — reporter offered; needs a verifiable per-language source per field (not guessed) |

## Rollback

```sql
ALTER TABLE `countries` DROP COLUMN `translations_capital`, DROP COLUMN `translations_currency_name`;
```

No existing columns are modified; rollback is clean. The Phinx migration is a `change()` method without an explicit `down()` — same convention as `20260425000000_create_postcodes_table.php` — so rollback is via the manual `ALTER TABLE` above, consistent with that precedent.

## Files Changed
- `bin/db/migrations/20260918000000_add_capital_currency_translations_to_countries.php` — new migration.
- `bin/db/schema.sql` — add 2 columns to `countries` table definition.
- `.github/scripts/utils.js` — add 2 field names to `SCHEMA.countries.optional`.
