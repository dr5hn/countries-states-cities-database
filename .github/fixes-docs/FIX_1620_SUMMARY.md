# Fix Summary: Mumbai neighbourhoods listed as cities

## Issue Reference
**Original Issue:** [#1620](https://github.com/dr5hn/countries-states-cities-database/issues/1620) — City List Includes Sub-localities/Neighborhoods as Cities

## Problem

For India → Maharashtra, the city list mixed Mumbai's neighbourhoods (Andheri, Borivali, Bandra, Colaba…)
in with real cities. Worse, 12 of them — and **Mumbai itself** — were typed `adm1` (the level used for
states), so consumers filtering on `type` could not separate them.

## Approach

Retype rather than delete. Removing records would break the `id`s that downstream apps and the
`postcodes.city_id` foreign key already reference. Instead this follows two conventions the dataset
already uses:

- `type: "section"` — the established type for sub-city areas (5,300+ records across AU, US, NL, CH, DE…).
- `parent_id` → the parent city's `id` — already used by 2,721 Chinese records, all of which resolve to a
  valid city.

Consumers can now drop neighbourhoods with `type != "section"`, or roll them up to their city via
`parent_id`.

## Changes (44 records in `contributions/cities/IN.json`, none added or removed)

| Change | Count | Records |
|---|---|---|
| Neighbourhood of Mumbai → `section`, `parent_id` 133024 | 36 | Andheri, Ballard Estate, Bandra, Bhandup, Borivali, Breach Candy, Byculla, Chembur, Chinchpokli, Colaba, Dharavi, Fort, Ghatkopar, Girgaon, Gorai, Jogeshwari, Juhu, Mahim, Malabar Hill, Malad, Mankhurd, Matunga, Mazagaon, Mulund, Nariman Point, Parel, Powai, Prabhadevi, Sewri, Sion Mumbai, Tardeo, Trombay, Vikhroli, Vile Parle, Wadala, Worli |
| Neighbourhood of Navi Mumbai → `section`, `parent_id` 133186 | 5 | Airoli, Artist Village, Kopar Khairane, Mahape, Vashi |
| Mumbai: `adm1` → `city` | 1 | Mumbai (133024) |
| Navi Mumbai: `section` → `city` | 1 | Navi Mumbai (133186) — a separate municipal corporation, not a part of Mumbai |
| District listed as a city → `adm2`, QID corrected | 1 | "Mumbai Suburban" carried `Q2341660` (Mumbai **City** district); corrected to `Q2085374` (Mumbai Suburban district) |

## How records were classified

Each Maharashtra record within 45 km of Mumbai was classified by walking its Wikidata
`P131` (located in the administrative territorial entity) chain up to Mumbai, Mumbai City district,
Mumbai Suburban district or Navi Mumbai. Every result was then reviewed by hand, because Wikidata's own
`P131` is wrong or too coarse for several of these:

- **Vashi, Airoli, Mahape** — Wikidata places them in Mumbai, but they lie east of Thane Creek and are
  Navi Mumbai nodes (longitude ≈ 73.00–73.03 vs Mumbai's ≈ 72.8–72.95).
- **Powai, Gorai** — Wikidata skips straight to "Maharashtra"; both are inside Mumbai city limits.

## Deliberately left unchanged

- **Kharghar, Kalamboli** — CIDCO-planned as part of Navi Mumbai but administered by the Panvel
  Municipal Corporation, so their parent city is ambiguous.
- **Thane-side and Raigad towns** (Thane, Kalyan, Dombivli, Bhiwandi, Ulhasnagar, Panvel, Uran, Virar…)
  — separate cities, correctly typed `city`.

## Related problems found (not fixed here)

- **Kalundri** (MH) carries `Q2281643`, which is *Kalpi* in Jalaun district, Uttar Pradesh.
- **Amarnath** and **Ambernath** (MH) share `Q584008` (Ambernath) — likely a duplicate record.

## Verification

| Check | Result |
|---|---|
| Records before → after | 4,198 → 4,198 |
| Lines changed | 172 (`type` 88, `parent_id` 82, `wikiDataId` 2) — no other field touched |
| Every target matched by name + expected QID before editing | 44 / 44 |
| All new `parent_id` values resolve to a Maharashtra city | 2 / 2 (Mumbai, Navi Mumbai) |

## Rollback

Revert the commit. No `id`s change, so no dependent data needs repair.
