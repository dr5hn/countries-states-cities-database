# Fix Summary: Russian name of Georgia (country)

## Issue Reference
**Original Issue:** [#1626](https://github.com/dr5hn/countries-states-cities-database/issues/1626) — Update the Russian name of Georgia

## Executive Summary

`contributions/countries/countries.json`'s Russian translation for the country **Georgia** (`iso2: GE`, `id: 81`) was `"Джорджия"` — a phonetic transliteration of the English name that is actually the standard Russian name for the **US state** of Georgia, not the country. The correct Russian name for the country is `"Грузия"` (Gruzia), the name used across all Slavic-speaking countries and the standard Russian designation.

## Changes Made

`contributions/countries/countries.json`, Georgia's `translations.ru` field:

| Field | Before | After |
|-------|--------|-------|
| `translations.ru` | `Джорджия` | `Грузия` |

## Verification

- Confirmed `Грузия` is the standard Russian country name (used by all Slavic-language countries, per RFE/RL and Britannica coverage of Georgia's own 2018 request that *other* languages drop the Russian-derived "Gruzia" form in favor of "Georgia" — Russian itself retained `Грузия`).
- Georgia's own `translations.uk` (Ukrainian) field already reads `Грузія` — the cognate Slavic form — making the prior `ru` value inconsistent with the dataset's own neighboring entry.
- No other fields, records, or files touched.

## Files Changed
- `contributions/countries/countries.json` — correct one field (`translations.ru`) on one record.
