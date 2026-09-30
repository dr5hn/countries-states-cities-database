# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## French cities filed under the wrong department

### How they were found
Re-matching France's Wikidata IDs (#1641, #1642) placed 45 records, by name and coordinates, on a commune in
another department. Each was checked on Wikidata: the item with the record's name within 2 km of its point,
followed up its "located in" (P131) chain. CSC's France has both regions and departments as states, so the new
state is the containing one **of the same type as the filed state** (the department), and it must equal the INSEE
department of the matched commune.

Where the filed department also has a commune of that name, population decides: the record moves only if its
population is within 1.5× of the matched commune's and not of the namesake's. *Évry*, filed under Yonne with
51,900 people, is Évry in Essonne, not the village in Yonne.

| Result | Records |
|---|---:|
| Move (namesake ruled out by population in 20 of them) | **30** |
| Held: Wikidata does not lead to a single department (communes merged into new ones, mostly in Maine-et-Loire) | 12 |
| Held: population close to both the matched commune and the namesake (Chirac, Coise, Courteilles) | 3 |

### Fix
**30 cities** move to their department. Only `state_id` and `state_code` change; all keep `Europe/Paris`.

| id | City | Was filed under | Now | Wikidata | Namesake in old dept. |
|---|---|---|---|---|---|
| 39302 | Albens | Haute-Savoie (74) | Savoie (73) | Q2274264, Q528122 |  |
| 39859 | Beaumont | Corrèze (19) | Vienne (86) | Q1356025 | yes |
| 40011 | Bienville | Oise (60) | Haute-Marne (52) | Q109413700, Q1100865 | yes |
| 40192 | Bourg-de-Thizy | Loire (42) | Rhône (69) | Q1364098 |  |
| 41061 | Cloyes-sur-le-Loir | Loir-et-Cher (41) | Eure-et-Loir (28) | Q3096255, Q472001 |  |
| 41156 | Contres | Cher (18) | Loir-et-Cher (41) | Q730148 | yes |
| 41262 | Cours-la-Ville | Loire (42) | Rhône (69) | Q1617140 |  |
| 41516 | Domfront | Oise (60) | Orne (61) | Q1290284, Q3096379 | yes |
| 41548 | Douchy | Aisne (02) | Loiret (45) | Q249609 | yes |
| 41925 | Fougerolles | Indre (36) | Haute-Saône (70) | Q3096462, Q922794 | yes |
| 41947 | Francheville | Orne (61) | Eure (27) | Q1008333 | yes |
| 43334 | Le Vigan | Gard (30) | Lot (46) | Q1383446 | yes |
| 43756 | Malesherbes | Seine-et-Marne (77) | Loiret (45) | Q2615431, Q838311 |  |
| 43836 | Margon | Hérault (34) | Eure-et-Loir (28) | Q388824 | yes |
| 44066 | Mezel | Alpes-de-Haute-Provence (04) | Puy-de-Dôme (63) | Q608101 | yes |
| 44244 | Montgaillard | Aude (11) | Ariège (09) | Q925331 | yes |
| 44481 | Méréville | Meurthe-et-Moselle (54) | Essonne (91) | Q123498082, Q257045 | yes |
| 44853 | Parigny | Loire (42) | Manche (50) | Q1062309, Q49360014 |  |
| 44955 | Pierrefitte-sur-Seine | Val-d'Oise (95) | Seine-Saint-Denis (93) | Q1543301, Q253939 |  |
| 45552 | Rocquencourt | Oise (60) | Yvelines (78) | Q1418760 | yes |
| 45571 | Romagny | Haut-Rhin (68) | Manche (50) | Q49364067, Q771946 | yes |
| 45963 | Saint-Genix-sur-Guiers | Isère (38) | Savoie (73) | Q591760 |  |
| 46392 | Saint-Pardoux | Puy-de-Dôme (63) | Deux-Sèvres (79) | Q49366176, Q948006 | yes |
| 46722 | Sainte-Radegonde | Vienne (86) | Deux-Sèvres (79) | Q1631611, Q49366698 | yes |
| 46750 | Salignac | Alpes-de-Haute-Provence (04) | Gironde (33) | Q384743, Q49366760 | yes |
| 47491 | Vallières | Aube (10) | Haute-Savoie (74) | Q750996 | yes |
| 47526 | Vassy | Orne (61) | Calvados (14) | Q845014 |  |
| 47857 | Vire | Saône-et-Loire (71) | Calvados (14) | Q1997656, Q220684 | yes |
| 48054 | Écuelles | Saône-et-Loire (71) | Seine-et-Marne (77) | Q274816 | yes |
| 48125 | Évry | Yonne (89) | Essonne (91) | Q192393, Q2612260 | yes |

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/FR.json` — `state_id` and `state_code` on 30 records
