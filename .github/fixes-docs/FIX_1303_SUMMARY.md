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
| 2b | not started | Wire counties into MySQL and the export formats |

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
  successors when Alaska is completed. The counties dataset is not exported yet, so this does not reach
  consumers in the meantime.
- **Phase 2b**: counties are a validated contribution dataset but don't yet reach MySQL or any export
  (needs a `counties` table + migration, import/sync scripts, the export commands, `export.yml`).

## Rollback

Revert the commit.
