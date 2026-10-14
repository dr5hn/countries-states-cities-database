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
  restoring parent references after all counties exist. All county files are preflighted before reset;
  unreadable, malformed and non-array files stop the import. Only absent county tables/directories are skipped.
- Reverse sync includes counties in schema dumps, preserves the county files' field/newline style, and does not
  add null county links to city contributions. Source-only state/country names survive round trips.
  The existing US file gains IDs 1–3,081 only; no city links are set.
- Added counties to the 12 published formats: JSON, CSV (including translations), XML, YAML, MongoDB, SQL Server,
  GeoJSON, TOON, Parquet, MySQL, PostgreSQL and SQLite. Flat/nested city JSON includes `county_id`; other
  converters carry it through. The workflow exports, compresses and uploads county assets and includes county
  counts; like states, the small county files are also committed by the export PR. The local PLIST and DuckDB
  helpers (not part of the workflow) also read counties; DuckDB remaps county/city/parent references in
  global-ID mode.
- Added the Prisma County model and optional City relation, with counties seeded before cities and parents
  linked after insert. County translations use nullable text to avoid adding another pre-existing Json/Text
  validation error. Older releases without `counties.json` are accepted.
- Cross-reference validation loads county contribution files and rejects nonexistent county IDs or links
  across states/countries. County IDs are optional positive integers; county records also receive state and
  country reference checks. County edits/removals also check existing city links and county parents;
  parents must exist and children with parents must have explicit IDs. ID-only county records are canonical.

### Verification (scratch databases only)

The review-fix checks below ran against `3ace9708` plus these fixes. France's 333 county records were
loaded from `origin/master:contributions/counties/FR.json` for testing only and are not part of the commits.

| Check | Result |
| --- | --- |
| Full importer on `world_phase2b_fix` (utf8mb4) | 6 regions; 22 subregions; 250 countries; 5,317 states; 3,414 counties (3,081 US + 333 FR); 153,744 cities; 844,248 postcodes |
| County and city MySQL → contributions round trip | US byte-identical; every FR source value preserved with IDs 3,082–3,414; source-only `state_name`/`country_name` preserved; all 223 city files byte-identical |
| PHP JSON export with isolated scratch config/output | All 3,414 counties and 153,744 cities exported; flat cities include `county_id` |
| Malformed, non-array and unreadable county-file CLI fixtures | Exit 1 before reset/truncate; counts in all seven populated scratch tables unchanged |
| Phinx upgrade/rollback and `SHOW COLUMNS` comparison | All 20 county column definitions match `schema.sql`, including types, nullability, keys, defaults and extra attributes |
| `.github/scripts`: `npm test` | 36/36 pass, including county-only edits/removals, hierarchy, real canonical US records and README refresh |
| Python: `python -m unittest discover -s bin/scripts/sync -p test_counties.py` | 8/8 pass: preflight safety, optional missing sources, database errors and source-only field round trips |
| Each of the seven review findings | Regression test fails on the original implementation and passes with the fix |

Generated exports and the temporary FR contribution are excluded from the commits. `world_phase2b_fix`
was dropped after verification. The main checkout, its config, and MySQL `world` are untouched.

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

## v5.0.0: counties of several regions; New Zealand's seven cross-region councils (decision B6)

### Problem
Seven of New Zealand's district councils lie in two or more regions (ISO 3166-2 states): Waitomo, Taupō, Rotorua,
Stratford, Rangitikei, Tararua and Waitaki. A county had exactly one `state_id`, so these councils were held out of the
54 territorial-authority counties (#2006): filing one under its seat's region would have put land of other regions
under the wrong state. Decision B6 (decisions_2_final.md, owner decision of 13 Oct 2026) keeps each as one county
linked to every region it lies in, in v5.0.0.

### Fix
- **Schema (held for v5.0.0, stacked on #2016):** a county has either its own state, or `state_id` and `state_code`
  both null and its regions in `states` (two or more). MySQL stores the list in `county_states (county_id, state_id)`
  with both foreign keys; migration `20261015000000_county_states` adds it and makes the county state pair nullable
  with a both-or-neither check. The importer, sync, validators, Prisma seed and every export format carry the list
  (bin/README.md has the format table); a city linked to such a county keeps its own state, which must be one of the
  county's.
- **Data:** seven counties, ids 14023-14029, `administrative district` / `district council`, level 2, each with its
  own Wikidata area item and that item's own P625 point (CC0), rounded to the schema's eight decimals (half-even; only
  Waitomo's 175.18333333333 loses digits). Sixteen region links from Stats NZ's Meshblock Higher Geographies 2026 land
  concordance. Six towns linked to their council: Taupo and Turangi (Taupō), Rotorua (Rotorua), Stratford
  (Stratford), Bulls (Rangitikei), Oamaru (Waitaki). Names follow the official Stats NZ register except Taupō, where
  the council and the area item use the macron; Rangitikei keeps the official spelling (LINZ declined the macron on
  3 December 2024); Rotorua District stays the area's name beside the council's "Rotorua Lakes Council" brand. No
  record is removed and no other value changes. Stratford's stored town point is 965 m outside its own urban area;
  it is flagged for a later point review, and both points lie in the same council and region, so the link stands.

### Sources
- Wikidata (CC0): the seven area items and their P625 statements, each pinned to a revision; point ledger in
  `.github/fixes-docs/ledgers/NZ_cross_region_councils_points.csv`.
- Stats NZ Geographic Data Service, Meshblock Higher Geographies 2026 and Urban Rural / Territorial Authority 2026
  (CC BY 4.0): region membership of each council and each linked town (concordance only; no geometry copied).
- Research: Codex nz_regions_1 (all 149 New Zealand city rows and 54 county rows audited; 0 held).

### Rollback
In this order (reverting the code first would remove the migration that the rollback needs):
1. **Data:** restore `contributions/counties/NZ.json` and `contributions/cities/NZ.json` as they were before this PR
   and reimport with this PR's importer, or delete counties 14023-14029 and the six `county_id` links (their sixteen
   `county_states` rows go with the counties).
2. **Schema:** with this PR's migration file still present, run `cd bin && php console manage:rollback -t
   20261014000000`. It is refused while a county has no state or a region row exists; afterwards `manage:status` shows
   20261015000000 down and the `county_states` table is gone.
3. **Code:** revert the rest of the PR.
