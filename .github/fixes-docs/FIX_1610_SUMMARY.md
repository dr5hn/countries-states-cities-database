# Fix Summary: Cuba — incomplete Havana municipalities

## Issue Reference
**Original Issue:** [#1610](https://github.com/dr5hn/countries-states-cities-database/issues/1610) — Cuba Habana City incomplete

## Executive Summary

Havana is divided into **15 municipalities** (*municipios*). The dataset contained only **10** of
them, so 5 were missing entirely — including **La Lisa**, which the reporter named.

## Changes Made

Added the 5 missing municipalities to `contributions/cities/CU.json` under `state_id` 272 (Havana):

| Municipality | wikiDataId | Latitude | Longitude | Population |
|--------------|-----------|----------|-----------|------------|
| Playa | Q2066897 | 23.09416700 | -82.44888900 | 178,601 |
| Plaza de la Revolución | Q2099152 | 23.12444400 | -82.38611100 | 139,135 |
| Marianao | Q2553350 | 23.08333300 | -82.43333300 | 134,057 |
| La Lisa | Q3648399 | 23.02472200 | -82.46305600 | 147,415 |
| Cotorro | Q3646457 | 23.02611100 | -82.24750000 | 83,115 |

## On "Miramar"

The reporter also mentioned *Miramar*. Miramar is **not** a municipality — it is a neighbourhood
(*consejo popular*) within the **Playa** municipality, which this PR adds. Havana's 15 municipalities
are subdivided into 105 *consejos populares*; adding those is a separate, much larger scope decision
and is deliberately not attempted here.

## Verification

Each municipality was resolved on Wikidata and verified before use — the entity had to be in Cuba
(`P17` = Q241) and located in a Havana entity (`P131`). All five entities' own English descriptions
read "municipality of Havana".

| Check | Result |
|-------|--------|
| Wikidata entities verified as Havana municipalities | 5 / 5 |
| Duplicate name in `CU.json` | 0 |
| Duplicate `wikiDataId` in `CU.json` | 0 |
| Official Havana municipalities now covered | **15 / 15** |
| Records before → after | 187 → 192 (+5) |

`type` is set to `section`, matching the dominant convention for existing Havana municipality records
in this dataset. Translations are intentionally omitted rather than machine-generated.

## Files Changed
- `contributions/cities/CU.json` — add 5 municipality records.
