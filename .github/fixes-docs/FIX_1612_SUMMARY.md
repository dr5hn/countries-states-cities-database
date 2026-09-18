# Fix Summary: Add cities "Bensersiel" and "Burhave" (Lower Saxony, Germany)

## Issue Reference
**Original Issue:** [#1612](https://github.com/dr5hn/countries-states-cities-database/issues/1612) — Bensersiel (Submitted via CSC Manager change request #48)

## Executive Summary

Added two coastal East Frisia settlements in Lower Saxony, Germany, neither previously present in the dataset:

- **Bensersiel** — a borough of the town of Esens, on the North Sea coast.
- **Burhave** — a locality/seaside resort in the Butjadingen municipality.

## Changes Made

Added to `contributions/cities/DE.json` (each inserted alphabetically at its correct position):

```json
{
  "name": "Bensersiel",
  "state_id": 3008,
  "state_code": "NI",
  "country_id": 82,
  "country_code": "DE",
  "type": "city",
  "level": null,
  "parent_id": null,
  "latitude": "53.67296700",
  "longitude": "7.57633300",
  "native": "Bensersiel",
  "population": 231,
  "timezone": "Europe/Berlin",
  "wikiDataId": "Q370757"
}
```

```json
{
  "name": "Burhave",
  "state_id": 3008,
  "state_code": "NI",
  "country_id": 82,
  "country_code": "DE",
  "type": "city",
  "level": null,
  "parent_id": null,
  "latitude": "53.57440000",
  "longitude": "8.36250000",
  "native": "Burhave",
  "population": 2069,
  "timezone": "Europe/Berlin",
  "wikiDataId": "Q1016278"
}
```

`id` omitted on both (auto-assigned on import). `type` normalized to lowercase `city`, matching this dataset's convention (the CSC Manager submission used capitalized `City`; `DE.json` uses lowercase exclusively — see also [FIX_1613_SUMMARY.md](./FIX_1613_SUMMARY.md)).

## Deliberately omitted: `translations`

No `translations` object was added for either record, following the same precedent as [FIX_1610_SUMMARY.md](./FIX_1610_SUMMARY.md) and [FIX_1613_SUMMARY.md](./FIX_1613_SUMMARY.md) — omitting is valid per schema, and machine-generating 19-language transliterations without a source risks introducing wrong data.

## Verification
- Wikidata `Q370757` (Bensersiel): "Borough from the city of Esens", `P17` Germany, `P625` 53°40'23"N 7°34'35"E — matches submitted coordinates exactly; population (231) matches.
- Wikidata `Q1016278` (Burhave): "human settlement in Germany", `P131` Butjadingen, `P625` 53°34'27.8"N 8°21'45.0"E — matches submitted coordinates exactly.
- Confirmed neither name existed anywhere in `DE.json` prior to this change (`grep` returned no matches).
- Confirmed `state_id 3008` / `state_code NI` = Lower Saxony and `country_id 82` = Germany against `contributions/states/states.json` and `contributions/countries/countries.json`.
- JSON validated after edit.

## Files Changed
- `contributions/cities/DE.json` — add 2 city records.
