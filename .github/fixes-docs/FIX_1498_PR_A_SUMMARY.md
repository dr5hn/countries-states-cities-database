# FIX #1498 — Spain: drop admin-level placeholders from cities (PR-A of 2)

**Issue:** [#1498 — Bug ES: GetCity returns province-level admin entries as cities](https://github.com/dr5hn/countries-states-cities-database/issues/1498)
**Scope:** Drop 22 placeholder rows from `contributions/cities/ES.json`.
**Sibling PR:** PR-B retags ~6,920 mistyped admin-level rows (currently `type` in `adm1`/`adm2`/`adm3`) to `type='city'`. PR-B closes #1498.
**Date:** 2026-05-04

## Problem

The reporter flagged that `GetCity(country=ES, state=Madrid)` returns "Provincia de Madrid" as a city, with the same pattern across other Spanish provinces, plus a cross-province leak ("Provincia de Alicante" inside Valencia's city list). These are admin-level placeholder rows, not municipalities.

Spain's `states.json` already lists the 50 provinces as proper states, so the "Provincia de X" pseudo-cities are duplicate concepts and can be dropped without re-parenting any other data.

## Drops (22 rows)

### 21 "Provincia de X" / "Província de X" placeholders

| id | name | state_code | type |
|----|------|-----------|------|
| 36362 | Provincia de Alicante | V | city |
| 36364 | Provincia de Burgos | LE | adm2 |
| 36365 | Provincia de Cantabria | S | adm3 |
| 36373 | Provincia de Huesca | HU | adm3 |
| 36375 | Provincia de La Rioja | LO | adm3 |
| 36376 | Provincia de Las Palmas | GC | city |
| 36377 | Provincia de León | LE | adm3 |
| 36379 | Provincia de Madrid | M | section |
| 36381 | Provincia de Navarra | NA | adm1 |
| 36383 | Provincia de Palencia | LE | adm3 |
| 36385 | Provincia de Salamanca | LE | adm3 |
| 36386 | Provincia de Santa Cruz de Tenerife | GC | city |
| 36387 | Provincia de Segovia | LE | adm3 |
| 36389 | Provincia de Soria | LE | adm3 |
| 36390 | Provincia de Teruel | HU | adm3 |
| 36391 | Provincia de Valladolid | LE | city |
| 36392 | Provincia de Zamora | LE | adm3 |
| 36393 | Provincia de Zaragoza | HU | adm3 |
| 36394 | Provincia de Ávila | LE | adm3 |
| 36396 | Província de Castelló | V | adm3 |
| 36400 | Província de València | V | city |

The state_code values are themselves messy (e.g. "Provincia de Burgos" sits under `LE`/León, "Provincia de Zaragoza" under `HU`/Huesca) — further evidence these rows are stub data, not curated municipality records.

### 1 cross-state Alicante stub

| id | name | state_code | reason |
|----|------|-----------|--------|
| 32244 | Alicante | V (Valencia) | Wrong province; missing Valencian endonym |

The canonical Alicante row is **id 152158** (`Alicante/Alacant`, state_code `A`) under the Alicante province. Row 32244 is a legacy duplicate from when Valencia community was the parent of three provinces, and its `state_code='V'` is what the issue reporter flagged as the cross-province leak.

## Counts

| | Before | After |
|---|--:|--:|
| `ES.json` rows | 8,427 | 8,405 |
| Rows named `Provincia *` / `Província *` | 21 | 0 |
| Rows where `state_code='V'` and name='Alicante' | 1 | 0 |

## Implementation

`bin/scripts/fixes/spain_drop_provincia_placeholders.py` — explicit id allowlist + name/state verification per id. Refuses to touch rows in the allowlist if their name/state has shifted from what was audited. Idempotent: a second run on cleaned data writes nothing and exits 0.

## Validation (mirrors `.github/scripts/validate-*`)

- Schema: 0 errors. All rows still have name/state_id/state_code/country_id/country_code/lat/lon. country_code/country_id consistent (ES/207).
- Cross-reference: 0 errors. Every `state_id` resolves to an ES state and `state_code` matches the resolved state's `iso2`.
- Coordinates: 127 rows out of `country-bounds.json` ES box (down from 129 on master — the drop reduced OOB by 2). The 127 remaining are all Canary Islands (state_codes `TF`, `GC`) — pre-existing, same pattern as IT/Lampedusa noted in #1395.
- Duplicate scan (same name + ≤5km): 45 pairs, **unchanged from master**.
- `python3 -m json.tool` parses cleanly; `normalize_json.py` is a no-op.

## Scope

- Touches **only** the 22 placeholder rows.
- Does **not** modify `states.json` or `countries.json`.
- Does **not** close #1498. PR-B (the type-field retag of ~6,920 mistyped rows) is the closing PR.
