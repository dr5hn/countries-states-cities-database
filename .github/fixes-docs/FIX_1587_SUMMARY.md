# Fix Summary: Iranian city native names machine-translated

## Issue Reference
**Original Issue:** [#1587](https://github.com/dr5hn/countries-states-cities-database/issues/1587) — native names are incorrectly machine-translated

## Executive Summary

204 Iranian city records in `contributions/cities/IR.json` had `native` values that were **machine
translations of the English name** rather than the correct Persian place name. Examples:

| id | name | before (`native`) | meaning of garbage | after (`native`) |
|----|------|-------------------|--------------------|------------------|
| 135121 | Saveh | صرفه جویی کردن | "to economize" | ساوه |
| 134774 | Semnan | نیمان | (nonsense) | سمنان |
| 135140 | Yazd | نوشتن | "to write" | یزد |
| 135142 | Zanjan | زنگ | "bell" | زنجان |
| 135125 | Tabriz | خوشی | "pleasure" | تبریز |

## Changes Made

- **File:** `contributions/cities/IR.json`
- **Records updated:** 204 (only the `native` field changed on each)
- **Source of corrections:** issue #1587 (reporter-supplied, Persian Wikipedia)

## Integrity Verification

Each correction was matched to its record by primary-key `id`, then guarded by an English-name check
before applying:

| Check | Result |
|-------|--------|
| Correction rows in issue (deduped) | 204 unique ids |
| `id` found in `IR.json` | 204 / 204 |
| Record `name` matches issue's English name | 204 / 204 |
| Record's existing `native` matched issue's "current" value | 204 / 204 |
| Name mismatches / not-found (skipped) | 0 |

The exact match across all four checks confirms the corrections target the intended records. Diff is
204 insertions / 204 deletions, all on `native` lines; JSON re-validated at 1847 records.
