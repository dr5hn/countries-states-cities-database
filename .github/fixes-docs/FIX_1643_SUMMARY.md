# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## States geocoded outside their territory

### Problem
Twenty records in `contributions/states/states.json` carried coordinates outside their own territory, most of them on another continent — they had been
geocoded by name without a country filter (e.g. Fiji's *Ba* landed on Ba in Oklahoma, *Central* on Los Angeles):

| id | State | Country | Was at |
|---|---|---|---|
| 1367 | Central | IL | Paraguay |
| 1917 | Ba | FJ | Oklahoma, US |
| 1920 | Rewa | FJ | South Carolina, US |
| 1923 | Western | FJ | New York State, US |
| 1926 | Ra | FJ | Kansas, US |
| 1929 | Central | FJ | Los Angeles, US |
| 1930 | Bua | FJ | Wisconsin, US |
| 1932 | Eastern | FJ | San Diego, US |
| 1933 | Lau | FJ | Texas, US |
| 1983 | Western | ZM | Sri Lanka |
| 2281 | South | LB | South Carolina, US |
| 2629 | Montagnes | CI | Liberia |
| 2632 | Lacs | CI | Ontario, Canada |
| 2644 | Denguélé | CI | Quebec, Canada |
| 2717 | Norte | GW | Philippines |
| 3306 | Dakhla-Oued Ed-Dahab (EH) | MA | Atlantic Ocean |
| 3436 | Western | IS | England |
| 4649 | North East | SG | Penang, Malaysia |
| 4652 | South West | SG | Penang, Malaysia |
| 4887 | Sai Kung | HK | Guangxi, China |

### Fix
Each state takes the coordinate (P625) of its own Wikidata item — the `wikiDataId` already on the record. Before
writing, each item was checked to be that state (label and description, e.g. Q797434 "province of Fiji") and its
point to fall inside the country's bounds. Only `latitude` and `longitude` change; timezones were already correct.

### Verification
- All 20 new points fall inside their country's bounding box (with the remote-territory boxes from the
  coordinate-validator fix, which Fiji's Lau and Eastern divisions need: they straddle the 180° meridian).
- The same states were the only state records flagged outside their country by the repo-wide bounds check.

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/states/states.json` — coordinates on 20 states
