# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Mexican cities filed under the wrong state (second pass)

### How they were found
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames place with
the same name (or an alternate name) within 3 km and **exactly the record's population**. For 167 MX records that
entry lies in another state; 129 of them are already moved by #1647 and #1652. Of the other 38:

| Result | Records |
|---|---:|
| Wikidata (the same-named item's "located in" chain) agrees with GeoNames | **26** |
| GeoNames says Hidalgo, but the Wikidata items carry INEGI codes of Hueypoxtla, México (GeoNames recently moved points in that area across the border) | **2** |
| Wikidata says the filed state is right: the sources disagree, left alone | 5 |
| Wikidata has no same-named place nearby, or contains it in several states | 5 |

22 of the 26 had been held back in #1652 because the filed state also has a place of that name; the exact
population match with the GeoNames entry in the new state shows which place the record is. The other 4, and the 2
Hueypoxtla records, were not in that pass.

### Fix
**28 cities** move. Only `state_id` and `state_code` change. Two of them, *El Porvenir* (142453) and *San José del Valle* (142848),
lie in Bahía de Banderas, whose zone is `America/Bahia_Banderas`; their `timezone` is corrected with the
time-zone fixes (#1667).

| id | City | Move | Population | Evidence |
|---|---|---|---:|---|
| 68090 | Adolfo López Mateos | MOR → MEX | 1,316 | GeoNames population match + Wikidata agree |
| 68671 | Buenavista | MOR → MEX | 1,291 | GeoNames population match + Wikidata agree |
| 69467 | Contepec | MEX → MIC | 4,184 | GeoNames population match + Wikidata agree |
| 69721 | Dos Ríos | MOR → MEX | 4,249 | GeoNames population match + Wikidata agree |
| 69871 | El Carmen | MOR → MEX | 1,238 | Wikidata Q61248206, INEGI 150360002 (Hueypoxtla, México); population = Hueypoxtla municipal plan |
| 70276 | Emiliano Zapata | CHP → TAB | 20,030 | GeoNames population match + Wikidata agree |
| 70510 | Galeana | MEX → MIC | 2,962 | GeoNames population match + Wikidata agree |
| 70960 | Jacona de Plancarte | MEX → MIC | 53,860 | GeoNames population match + Wikidata agree |
| 71199 | La Cantera | MEX → MIC | 4,024 | GeoNames population match + Wikidata agree |
| 71301 | La Gloria | PUE → VER | 2,510 | GeoNames population match + Wikidata agree |
| 71335 | La Junta | VER → OAX | 1,014 | GeoNames population match + Wikidata agree |
| 71793 | Los Corazones | CHP → OAX | 1,104 | GeoNames population match + Wikidata agree |
| 71807 | Los Hucuares | MEX → MIC | 1,144 | GeoNames population match + Wikidata agree |
| 71823 | Los Nogales | MEX → MIC | 1,360 | GeoNames population match + Wikidata agree |
| 71842 | Los Remedios | MEX → MIC | 1,854 | GeoNames population match + Wikidata agree |
| 72140 | Milpillas | SON → CHH | 1,025 | GeoNames population match + Wikidata agree |
| 72802 | Plan de Iguala | VER → SLP | 1,596 | GeoNames population match + Wikidata agree |
| 72809 | Playa Azul | MEX → MIC | 3,139 | GeoNames population match + Wikidata agree |
| 72868 | Potreros | MEX → GUA | 1,547 | GeoNames population match + Wikidata agree |
| 73210 | Salazar | MOR → MEX | 1,515 | GeoNames population match + Wikidata agree |
| 73606 | San Francisco Zacacalco | MOR → MEX | 7,420 | Wikidata Q6118775, INEGI 150360008 (Hueypoxtla, México) |
| 74151 | San Miguel | MOR → MEX | 2,754 | GeoNames population match + Wikidata agree |
| 74373 | San Pedro Tarímbaro | MEX → MIC | 1,353 | GeoNames population match + Wikidata agree |
| 74599 | Santa Clara | GUA → MIC | 2,633 | GeoNames population match + Wikidata agree |
| 75023 | Santo Tomás | MEX → MIC | 1,386 | GeoNames population match + Wikidata agree |
| 75431 | Tepetongo | MEX → MIC | 1,426 | GeoNames population match + Wikidata agree |
| 142453 | El Porvenir | JAL → NAY | 6,046 | GeoNames population match + Wikidata agree |
| 142848 | San José del Valle | JAL → NAY | 22,541 | GeoNames population match + Wikidata agree |

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/MX.json` — `state_id` and `state_code` on 28 records
