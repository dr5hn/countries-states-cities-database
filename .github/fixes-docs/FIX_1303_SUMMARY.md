# Fix Summary: US counties returned as cities

## Issue Reference
**Original Issue:** [#1303](https://github.com/dr5hn/countries-states-cities-database/issues/1303) — Counties should be returned separately from cities

## Background

About 30% of `contributions/cities/US.json` (19,788 rows) were county-level admin units, not cities.
The fix is being done in phases:

| Phase | PR | What |
|---|---|---|
| 1 | [#1561](https://github.com/dr5hn/countries-states-cities-database/pull/1561) | Retyped mis-classified settlements to `city` |
| 2a | [#1569](https://github.com/dr5hn/countries-states-cities-database/pull/1569) | Moved 3,057 `county`/`parish` rows to a new `contributions/counties/US.json` |
| 2a (Alaska) | this PR | Moved the Alaska county-equivalents that 2a missed |
| 2b | this implementation | Counties table, city links, import/sync, all export formats |

## This change: Alaska county-equivalents

Phase 2a selected rows by `type`. Alaska's county-equivalents — boroughs and census areas — had been
stored as `type: "city"`, so none were moved and the counties dataset had **no Alaska rows at all**.

`bin/scripts/fixes/relocate_us_counties.py` now also moves Alaska rows whose name marks them as a
borough or census area, with `type: "borough"` or `type: "census area"` (siblings of `county` and
`parish`).

**Moved (24):**
- **Boroughs (16):** Aleutians East, Bristol Bay, Denali, Fairbanks North Star, Haines, Kenai Peninsula,
  Ketchikan Gateway, Kodiak Island, Lake and Peninsula, Matanuska-Susitna, North Slope, Northwest Arctic,
  Petersburg — plus the consolidated Anchorage Municipality, City and Borough of Wrangell, and Sitka City
  and Borough.
- **Census areas (8):** Aleutians West, Bethel, Dillingham, Hoonah-Angoon, Nome, Southeast Fairbanks,
  Yukon-Koyukuk, and Valdez-Cordova (see below).

### Rule for consolidated city-boroughs

A consolidated government is both a city and a county-equivalent. The rule applied:

- **The city also has its own row → the consolidated row moves to counties.** Anchorage Municipality
  (separate `Anchorage` row), City and Borough of Wrangell (separate `Wrangell` row), and Sitka City and
  Borough (it even shared `Q79804` with the `Sitka` row — a duplicate).
- **The consolidated row is the place's only row → it stays a city.** Juneau, Skagway and Yakutat.

This matches phase 2a, where consolidated city-counties that exist only as a city row (San Francisco,
Denver…) stayed cities. Whether every consolidated city-county should *also* get a counties row is a
phase 2b decision.

No US postcode references any moved row, so no `city_id` links break.

## Script fixes

Two latent problems in the relocation script were fixed so it is safe to re-run:

- It **overwrote** `counties/US.json` with only the newly found rows. A second run would have deleted
  every existing county. It now appends and skips rows already present.
- It always added a trailing newline to both files, producing a spurious diff on `cities/US.json`.
  It now keeps each file's existing style.

## Verification

| Check | Result |
|---|---|
| `cities/US.json` rows | 16,731 → 16,707 (whole-record removals only) |
| `counties/US.json` rows | 3,057 → 3,081 (append only; existing rows unchanged) |
| Alaska rows in counties | 0 → 24 (16 borough, 8 census area) |
| Postcodes referencing a moved row | 0 |
| Second run | "Nothing to relocate" — idempotent |

## Still to do

Alaska has 30 current county-equivalents (19 boroughs, 11 census areas). After this change:

| Status | Units |
|---|---|
| In counties | 16 boroughs + 7 census areas |
| Only as the city's own row (stays a city by the rule above) | Juneau, Skagway, Yakutat |
| Absent from both datasets | Chugach, Copper River, Kusilvak and Prince of Wales-Hyder census areas |

- **Valdez-Cordova Census Area was dissolved on 2019-01-02** and replaced by Chugach and Copper River
  (Wikidata Q508618). It is moved here because it is not a city, but it should be replaced by its two
  successors when Alaska is completed. This historical row is now exported and still needs a separate data correction.
- **City links and API support**: phase 2b supplies nullable `county_id` infrastructure; matching cities to
  counties and exposing counties through the API remain separate work.

## Phase 2b: MySQL, exports and nullable city links

### What changed

- Added the reversible `20261008000000_create_counties_table.php` migration and schema mirror: county IDs,
  state/country FKs, county hierarchy, coordinates, names, population, timezone, translations, timestamps and flag.
  Cities gain a nullable `county_id` FK with `ON DELETE SET NULL`; the schema mirror also includes `type_local`
  for states and cities. County parents use `ON DELETE SET NULL` in MySQL.
- Full-import reset clears postcodes, cities, counties, states, countries, subregions and regions in that order.
  Import runs counties after states and before cities, inserting explicit IDs before auto-assigned IDs and
  restoring parent references after all counties exist. Missing county tables/directories are supported.
- Reverse sync includes counties in schema dumps, preserves the county files' field/newline style, and does not
  add null county links to city contributions. The existing US file gains IDs 1–3,081 only; no city links are set.
- Added counties to JSON, CSV (including translations), XML, YAML, MongoDB, SQL Server, PLIST, GeoJSON, TOON,
  Parquet, MySQL, PostgreSQL, SQLite and DuckDB. Flat/nested city JSON includes `county_id`; other converters
  carry it through. The workflow exports, compresses and uploads county assets, includes county counts, and
  runs PLIST and DuckDB helpers. DuckDB remaps county/city/parent references in global-ID mode; native dataframe insertion speeds up full exports, with a transaction fallback when pandas is unavailable.
- Added the Prisma County model and optional City relation, with counties seeded before cities and parents
  linked after insert. County translations use nullable text to avoid adding another pre-existing Json/Text
  validation error. Older releases without `counties.json` are accepted.
- Cross-reference validation loads county contribution files and rejects nonexistent county IDs or links
  across states/countries. County IDs are optional positive integers; county records also receive state and
  country reference checks.

### Verification (scratch databases only)

| Check | Result |
| --- | --- |
| Load schema and run full importer on `world_phase2b` (utf8mb4) | 3,081 counties; 153,744 cities; 844,248 postcodes |
| Full MySQL → contributions sync | County IDs added with every existing value unchanged; all 223 city files byte-identical |
| PHP exporters with in-memory scratch database config | JSON, CSV, XML, YAML, MongoDB, SQL Server and PLIST succeeded |
| County dataset in all 14 formats | 3,081 records; SQL Server/MySQL SQL generated and inspected |
| PostgreSQL | NMIG migrated all seven tables and FKs; county `pg_dump` verified |
| SQLite and DuckDB | Standalone county and combined database exports contain 3,081 counties |
| IDs, hierarchy and FK fixture | Mixed explicit/auto IDs, forward parents, missing directory and deletion nullification passed |
| Phinx upgrade/rollback against master schema | County table and city column created, then actually removed |
| Legacy master schema/data with no county table; empty/missing county JSON | Import and exporters succeed |
| `.github/scripts`: `npm ci`, `npm test` | 26/26 pass |
| Prisma validate vs `origin/master` | Six pre-existing errors in both; no increase |

Generated exports are build artifacts; incidental regenerated reference files are excluded from these commits.
Both scratch databases are dropped after verification. The main checkout, its config, and MySQL `world` are untouched.

SQL Server uses a noncascading parent FK because its cascade rules reject self-reference cycles
([error 1785](https://learn.microsoft.com/en-us/sql/relational-databases/errors-events/mssqlserver-1785-database-engine-error)).
Clients of that format must clear child counties' `parent_id` before deleting a parent. Its city county FK still
uses `ON DELETE SET NULL`. County parent constraints are validated after insertion to allow forward references.
SQL Server and MongoDB were verified as generated exports; no native servers were used for those two formats.

### Rollback

Back up county contribution files (including their assigned IDs) and any populated city links before rolling back.
Run Phinx rollback for this migration: it removes the city FK/column before dropping counties. Revert the phase 2b
commits to restore the source/schema/export paths. Contribution JSON remains available for a later reimport; the
migration rollback removes county rows and city links from MySQL. The earlier phase 2a data moves are independent.
