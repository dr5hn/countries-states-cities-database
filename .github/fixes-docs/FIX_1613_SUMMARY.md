# Fix Summary: Add city "Au" (Fischen im Allgäu, Bavaria, Germany)

## Issue Reference
**Original Issue:** [#1613](https://github.com/dr5hn/countries-states-cities-database/issues/1613) — new City (Submitted via CSC Manager change request #49)

## Executive Summary

Added the village of **Au**, part of the municipality of Fischen im Allgäu in Bavaria, Germany — not present in the dataset. Note this dataset already contains a *different* place also named "Au" (id `23720`, in Baden-Württemberg, ~90km away) — confirmed via Wikidata that the requested record is a distinct place, not a duplicate.

## Changes Made

Added to `contributions/cities/DE.json` (inserted alphabetically, between the existing "Au" id `23720` and "Au am Rhein" id `23721`):

```json
{
  "name": "Au",
  "state_id": 3009,
  "state_code": "BY",
  "country_id": 82,
  "country_code": "DE",
  "type": "city",
  "level": null,
  "parent_id": null,
  "latitude": "47.46258000",
  "longitude": "10.28342000",
  "native": "Au",
  "population": 154,
  "timezone": "Europe/Berlin",
  "wikiDataId": "Q131301662"
}
```

`id` omitted (auto-assigned on import). `type` normalized to lowercase `city` — the issue's CSC Manager submission said `City`, but this dataset's own convention for `DE.json` is exclusively lowercase (`city`/`adm2`/`adm3`/`adm4`/etc.; zero existing records use capitalized `City`).

## Deliberately omitted: `translations`

No `translations` object was added — following the precedent set in [FIX_1610_SUMMARY.md](./FIX_1610_SUMMARY.md) (Cuba municipalities), machine-generating transliterations into 19 other languages for a place this small, without an authoritative source, risks introducing wrong data. Omitting the field entirely is valid per this dataset's schema (`translations` is optional for cities).

## Verification
- Wikidata `Q131301662`: label "Au", description "village in the municipality of Fischen im Allgäu, Germany", `P17` Germany, `P131` Fischen im Allgäu, `P625` ≈ 47°27'45.29"N 10°17'0.31"E (47.46258, 10.28342) — matches the submitted coordinates exactly.
- Confirmed `state_id 3009` / `state_code BY` = Bavaria and `country_id 82` = Germany against `contributions/states/states.json` and `contributions/countries/countries.json`.
- Confirmed the existing `"name": "Au"` record already in `DE.json` (id `23720`) is a different place (Baden-Württemberg, lat/lon 47.95/7.83333) — not a duplicate of this addition.
- JSON validated after edit.

## Files Changed
- `contributions/cities/DE.json` — add 1 city record.
