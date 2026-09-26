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
| 2a (Alaska) | this PR | Moved the Alaska boroughs that 2a missed |
| 2b | not started | Wire counties into MySQL and the export formats |

## This change: Alaska boroughs

Phase 2a selected rows by `type`. Alaska's boroughs (its county-equivalents) had been stored as
`type: "city"`, so none were moved and the counties dataset had **no Alaska rows at all**.

`bin/scripts/fixes/relocate_us_counties.py` now also selects Alaska rows whose name ends in " Borough",
and moves them with `type: "borough"` (a sibling of `county` and `parish`).

**Moved (14):** Aleutians East, Bristol Bay, Denali, Fairbanks North Star, Haines, Kenai Peninsula,
Ketchikan Gateway, Kodiak Island, Lake and Peninsula, Matanuska-Susitna, North Slope, Northwest Arctic
and Petersburg boroughs, plus **Sitka City and Borough**.

**Consolidated "City and Borough" governments** are both a city and a county-equivalent. Phase 2a
kept consolidated city-counties (San Francisco, Denver…) as cities, so the rule here is:

- **Sitka City and Borough** moves: it shared `Q79804` with a separate `Sitka` city row, so it was a
  duplicate and the city stays represented.
- **Yakutat City and Borough** stays: it is Yakutat's only row, and moving it would remove the town.

No US postcode references any of the moved rows, so no `city_id` links break.

## Script fixes

Two latent problems in the relocation script were fixed so it is safe to re-run:

- It **overwrote** `counties/US.json` with only the newly found rows. A second run would have deleted
  every existing county. It now appends and skips rows already present.
- It always added a trailing newline to both files, producing a spurious diff on `cities/US.json`.
  It now keeps each file's existing style.

## Verification

| Check | Result |
|---|---|
| `cities/US.json` rows | 16,731 → 16,717 (whole-record removals only) |
| `counties/US.json` rows | 3,057 → 3,071 (append only; existing rows unchanged) |
| Alaska rows in counties | 0 → 14 |
| Second run | "Nothing to relocate" — idempotent |

## Still to do

- **Phase 2b**: counties are a validated contribution dataset but don't yet reach MySQL or any export
  (needs a `counties` table + migration, import/sync scripts, the export commands, `export.yml`).
- **Completing Alaska**: 16 county-equivalents were never in the dataset at all — Anchorage, Juneau,
  Skagway, Wrangell and Yakutat (as boroughs) and the 11 census areas of the Unorganized Borough.

## Rollback

Revert the commit.
