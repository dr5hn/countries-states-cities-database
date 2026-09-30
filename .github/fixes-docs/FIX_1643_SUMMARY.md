# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## States with a broken parent link

### How they were found
A scan of `states.json` checked every `parent_id`: it must name an existing state of the same country, other than
the state itself. Found by the independent review of #1657, then confirmed by the scan:

| Problem | States |
|---|---:|
| Tuscan provinces whose parent is Udine (1764, a province in Friuli-Venezia Giulia) instead of Tuscany (1664) | 8 |
| Spanish provinces that are their own parent | 3 |

Asturias, Cantabria and La Rioja are single-province autonomous communities. Their province records (1160, 1170, 1171)
point to themselves; the community records (5701–5703) were added later and never linked. Every other Spanish
province points to its community.

### Fix
Only `parent_id` changes, on 11 states.

| id | State | Country | parent_id was | Now |
|---|---|---|---|---|
| (8) | Pisa, Pistoia, Prato, Siena, Livorno, Lucca, Massa and Carrara, Grosseto | IT | 1764 Udine | 1664 Tuscany |
| 1160 | Asturias (province) | ES | 1160 (itself) | 5701 Asturias, Principality of |
| 1170 | Cantabria (province) | ES | 1170 (itself) | 5702 Cantabria |
| 1171 | La Rioja (province) | ES | 1171 (itself) | 5703 La Rioja |

### Also found (not changed here)
The same scan finds 166 states whose `level` is not below their parent's: provinces at level 1 under level-1 regions
in Morocco (58), Burkina Faso (45) and Belgium (10); Guinea's prefectures and regions both at level 2 (29); Fiji's
provinces at level 1 under level-2 divisions (14); two Guinea-Bissau regions at level 1 under a province. Spanish
provinces are level 1 and their communities have no level. Changing levels could alter what API users get when they
filter by level, so it waits for a decision in #1643.

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/states/states.json` — `parent_id` on 11 states
