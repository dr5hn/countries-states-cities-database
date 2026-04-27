# France Cities Remap to Departments

## Issue Reference
- **GitHub Issue:** [#1352](https://github.com/dr5hn/countries-states-cities-database/issues/1352) — France data: cities misclassified at region level instead of department.
- **Sibling PRs:** #1394 (PR-A diff vs upstream), #1393 (PR-B), #1392 (PR-C), #1400 (PR-D). None of those remap existing cities; this PR (PR-E) does.
- **Reference fix:** #1395 — the Italy region→province remap this PR mirrors.
- **Date:** 2026-04-27

## Executive Summary
Reassigned **8,727 of 10,079 French cities** from the 12 metropolitan regions plus the Corsica collectivity (`20R`) to the correct INSEE department-level entity (one of 95 metropolitan departments, plus `2A`, `2B`, `75C`).

Before this fix, endpoints like `GET /v1/countries/FR/states/03/cities` returned `[]` because Allier (department `03`) had **0 cities** — all of its communes sat under the parent region `ARA`. After this fix, Allier holds **59 cities** (Vichy, Moulins, Montluçon, Cusset, Yzeure, etc.). The same was true for every other department whose region was the holding bucket.

| State_code level | Cities (before) | Cities (after) |
|------------------|----------------:|---------------:|
| Metropolitan region (ARA, IDF, NOR, PDL, NAQ, BRE, OCC, GES, CVL, BFC, HDF, PAC) | 8,699 | 0 |
| Corsica collectivity (`20R`) | 28 | 0 |
| Metropolitan department (01–95, `2A`, `2B`, `75C`) | 1,351 | 10,078 |
| Other (overseas: NC, etc.) | 1 | 1 |

## Mapping source

The authoritative mapping is the official `geo.api.gouv.fr` commune dataset:

- **Source:** `https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,codeRegion,centre,population&format=json`
- **Snapshot bundled at:** `bin/scripts/fixes/data/geo-api-gouv-communes.json`
- **Licence:** [Licence Ouverte v2.0 (Etalab)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/), compatible with this repo's ODbL-1.0.
- **Records:** 34,969 communes × 6 fields (nom, code INSEE, codeDepartement, codeRegion, centre, population).

The join uses **INSEE commune name + coordinates**. Each upstream record carries its `codeDepartement` (the 2-character INSEE department code: `01`–`95`, `2A`, `2B`, `971`–`989`), which maps 1:1 to our `state.iso2` for every metropolitan department, with a single override:

| INSEE department | Our state.iso2 | Notes |
|------------------|----------------|-------|
| `75`             | `75C`          | Paris is stored as the collectivity-level `75C`, not bare `75`. |
| `69`             | `69`           | All dept-69 communes go to Rhône. Métropole de Lyon (`69M`) cannot be inferred from `codeDepartement` and is left untouched (none of our region-coded rows currently belong to `69M` anyway). |
| All others       | identical      | `01` → `01`, `2A` → `2A`, `2B` → `2B`, … |

## Implementation

`bin/scripts/fixes/france_cities_remap.py` performs the remap. Resolution order per city:

1. **Name match in current region** — the city's `name` is normalised (NFKD-folded, ASCII-stripped, lowercased, ligatures `œ`/`æ` expanded, `lès`/`les`/`lez` collapsed, non-letters removed — same helper as PR #1394) and looked up against an index of every commune name. When multiple matches exist, candidates whose `codeRegion` corresponds to the city's current region are preferred. With one such candidate, take it; with several, pick the one closest by haversine distance.
2. **Name match in any region** — if no candidate sits in the current region, pick the globally-closest namesake — but only when its distance is within 25 km. Far-away namesakes (some at 600+ km) are deliberately rejected because the current region is itself wrong, so "closest" can land on a totally unrelated commune. These rejections fall through to (3).
3. **k-NN proximity vote** — for cities still unresolved, rank all communes by haversine distance, take the 5 nearest (capped at 25 km), and use an inverse-distance-weighted vote on `codeDepartement`. Mirrors the Italy pass; more robust at department borders than picking the single nearest commune.

The script is **dependency-free Python**, **idempotent** (re-running on the post-remap file produces 0 changes), and writes a structured JSON report to `bin/scripts/fixes/france_cities_remap.report.json`.

Only `state_id` and `state_code` are mutated. `name`, `native`, `latitude`, `longitude`, `wikiDataId`, `translations`, `population`, `timezone`, and every other field on every city record are preserved verbatim.

## Counts

```
input                10079
in_scope              8727  cities in source-set state codes (12 regions + 20R)
skipped_out_of_scope  1352  already at dept level (52, 55, 48, 2A, 2B), or NC

by_resolution:
  name_unique         7441  single name match anywhere
  name_region          418  one in-region candidate among multiple
  name_region_multi    181  multiple in-region candidates -> closest by coord
  name_other_region      0  (cascade fix: every cross-region match was either
                              within 25km or fell through to k-NN)
  proximity_knn        687  resolved by 5-NN weighted vote within 25 km

changed              8727  state_id and state_code rewritten
unchanged               0
unmapped                0  every in-scope record reached a final assignment
```

The proximity-pass distance distribution is healthy:

| Distance bucket | Count |
|-----------------|------:|
| 0 – 1 km        | 118  |
| 1 – 3 km        | 381  |
| 3 – 5 km        | 128  |
| 5 – 10 km       | 34   |
| 10 – 25 km      | 0    |

Furthest proximity match: 8.56 km (`Le Pin-en-Mauges` → dept 49 Maine-et-Loire, a former commune merged into Beaupréau-en-Mauges in 2015).

## Spot-checks

| City | Before | After |
|------|--------|-------|
| Vichy | state_code=`ARA` (region) | state_code=`03` (Allier) |
| Lyon | state_code=`ARA` | state_code=`69` (Rhône) |
| Marseille | state_code=`PAC` | state_code=`13` (Bouches-du-Rhône) |
| Paris | state_code=`IDF` | state_code=`75C` (Paris collectivity) |
| Bordeaux | state_code=`NAQ` | state_code=`33` (Gironde) |
| Strasbourg | state_code=`GES` | state_code=`67` (Bas-Rhin) |
| Nice | state_code=`PAC` | state_code=`06` (Alpes-Maritimes) |
| Lille | state_code=`HDF` | state_code=`59` (Nord) |
| Bastia | state_code=`20R` | state_code=`2B` (Haute-Corse) |
| Ajaccio | state_code=`20R` | state_code=`2A` (Corse-du-Sud) |

## Customer scenario verified
`GET /v1/countries/FR/states/03/cities` now returns **59 cities** (was `[]`), unblocking the Kevin / Allier customer report referenced in the issue.

## Edge cases & known limitations

### Métropole de Lyon (`69M`)
The geo.api.gouv.fr dataset does not distinguish Métropole de Lyon (`69M`) communes from the rest of department 69 — every dept-69 record carries `codeDepartement: "69"`. As a result, all 142 dept-69 communes in this remap go to state `69` (Rhône), including communes administratively part of Métropole de Lyon (Lyon, Villeurbanne, etc.). This matches the pre-remap state for these cities (which sat under `ARA` and could not have been further specialised either). Splitting Métropole de Lyon out of Rhône is left as a follow-up.

### Out-of-scope rows
1,352 rows are skipped (left unchanged):
- 1,351 already at department level (`52`=428, `55`=500, `48`=141, `2B`=8, `2A`=99 plus minor groupings before the remap).
- 1 record for Nouvelle-Calédonie (`NC`), which is overseas (out of scope per task framing).

### Frazione-style merged communes
~660 cities map via the proximity pass because their names no longer correspond to a separate INSEE commune (e.g. `Le Pin-en-Mauges`, `Aigueblanche`, `Aillant-sur-Tholon` — all merged into other communes by INSEE in the past decade but still present in our `FR.json` as historical records). The 5-NN vote bounded at 25 km picks their administrative successor's department. The PR-A diagnostic report's `extra_in_csc` list (643 entries) covers a similar surface and can drive a separate clean-up PR if maintainers want to drop the historical names.

### Unmapped count
`0`. Every in-scope row reached a final assignment. No record was deleted.

## Validation
Run locally before commit:
- `python3 bin/scripts/fixes/france_cities_remap.py --dry-run` — confirms idempotency (`in_scope=0` after applying).
- `python3 bin/scripts/sync/normalize_json.py contributions/cities/FR.json` — no-op (no missing IDs/timestamps; remap only touches state_id/state_code).
- Cross-reference walk: every (`state_id`, `state_code`) in the post-remap file resolves to a real states.json row whose `country_id` matches and whose `iso2` equals `state_code`.
- Coordinate bounds: 0 metropolitan rows fall outside `country-bounds.json`'s FR box.
- (name, state_id) duplicates inside FR: 0.

## Files

- `bin/scripts/fixes/france_cities_remap.py` — the remap script (offline, idempotent).
- `bin/scripts/fixes/data/geo-api-gouv-communes.json` — bundled INSEE commune snapshot used by the script.
- `bin/scripts/fixes/france_cities_remap.report.json` — structured run report.
- `contributions/cities/FR.json` — 10,079 records, only `state_id` and `state_code` mutated.
