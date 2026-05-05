# FIX #1498 — Spain: retag mistyped admin rows to type=city (PR-B of 2)

**Issue:** [#1498 — Bug ES: GetCity returns province-level admin entries as cities](https://github.com/dr5hn/countries-states-cities-database/issues/1498)
**Scope:** Bulk-retag 6,920 rows in `contributions/cities/ES.json` whose `type` is `adm1`/`adm2`/`adm3` to `type='city'`. Touches only the `type` field.
**Sibling PR:** PR-A (already merged / in review) dropped 22 admin-level placeholder rows.
**Closes:** #1498.
**Date:** 2026-05-04

## Problem

After PR-A removed the 22 admin-level placeholders, ES.json still carried 6,920 records whose `type` field was set to `adm1`, `adm2`, or `adm3` even though the rows themselves are real Spanish municipalities. Consuming apps that filter on `type='city'` (or sort city-vs-admin records) treat these as administrative regions and exclude them from city dropdowns — exactly the failure mode the reporter described.

## Spot-check (why these are real cities)

A 60-row random sample (20 of each adm type) gave:

- **adm1 (20 rows total in file):** every sample is a major Spanish city — Barcelona, Valencia, Sevilla, Zaragoza, Murcia, Pamplona, Valladolid, Las Palmas de Gran Canaria, Santiago de Compostela, Santander, Toledo, Mérida, Logroño, Vitoria-Gasteiz, Oviedo, Palma, etc.
- **adm2 (40 rows total):** every sample is a provincial capital or municipality — Córdoba, Málaga, Lleida, Girona, Soria, Segovia, Jaén, Lugo, Albacete, Guadalajara, Palencia, Zamora, Castelló de la Plana, Ciudad Real, Alicante/Alacant (id 152158, the canonical Alicante), etc.
- **adm3 (6,860 rows total):** every sample is a real Spanish municipality with coordinates and (mostly) population data.

Aggregate quality signals across the 6,920 candidates:

| Type | Count | Has wikiDataId | Has population > 0 | Has coords |
|------|------:|---------------:|-------------------:|-----------:|
| adm1 | 20    | 20/20          | 20/20              | 20/20      |
| adm2 | 40    | 39/40          | 38/40              | 40/40      |
| adm3 | 6,860 | 6,854/6,860    | 6,458/6,860        | 6,860/6,860 |

## Counts (post PR-A → post PR-B)

| Type | Before | After |
|------|--:|--:|
| city | 1,416 | **8,336** |
| section | 60 | 60 |
| adm3 | 6,860 | 0 |
| adm2 | 40 | 0 |
| adm1 | 20 | 0 |
| locality | 6 | 6 |
| historical_capital | 1 | 1 |
| capital | 1 | 1 |
| adm4 | 1 | 1 |
| **Total** | **8,405** | **8,405** |

(Note: the brief gave a back-of-envelope estimate of "6,936 to retag → 8,357 city". The actual numbers are 6,920 → 8,336, because 16 of the 22 rows PR-A dropped were themselves typed adm1/adm2/adm3.)

## Out of scope (deliberately not touched)

- **`type='section'` (60 rows):** mixed quality — some are real neighbourhoods of Barcelona/Madrid that should stay typed `section` (they're already correctly excluded from city dropdowns), some look like real towns. Needs row-by-row review, not bulk retag.
- **`type='locality'` (6 rows):** small, defensible category; left alone.
- **`type='capital'`, `type='historical_capital'`, `type='adm4'` (1 each):** not city-equivalents in this dataset's vocabulary. Left alone.

## Implementation

`bin/scripts/fixes/spain_retag_admin_types.py` — single-pass mutation, only touches the `type` field, only for ES rows whose current type is in `{adm1, adm2, adm3}`. Asserts row count is preserved and no admin-typed rows remain. Idempotent.

## Validation (mirrors `.github/scripts/validate-*`)

- Schema: 0 errors.
- Cross-reference: 0 errors. Every `state_id` resolves to an ES state and `state_code` matches the resolved state's `iso2`.
- Coordinate-bounds: 127 out-of-box (Canary Islands, `TF`/`GC` — pre-existing, identical to PR-A head).
- Same-name + ≤5km duplicate pairs: 45 — **identical to PR-A head**. The retag only changed the `type` field; coordinates and names are byte-for-byte unchanged.
- Diff inspection: 6,920 rows changed, every change is exactly one field (`type`), source value in `{adm1, adm2, adm3}`, target value `'city'`. Zero collateral changes.
- Idempotent re-run: 0 candidates remaining.

## Constraints honoured

- Touches **only** the `type` field of `country_code='ES'` rows.
- Does **not** touch `state_code`, `state_id`, coordinates, or any other field.
- Does **not** modify `states.json` or `countries.json`.
