# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## State points outside their own territory

### How they were found
Without state borders to test against, the check uses each state's own cities: the area they cover (the 5th–95th
percentile of their latitudes and longitudes, widened by a quarter, at least 0.3°). **54 state points lie outside
their own cities' area.** Most are large regions whose geographic centre is far from where people live (Quebec,
Saudi regions) or states already fixed in #1646. A state is fixed here only when its own Wikidata item — the
record's `wikiDataId`, checked to be that state by label and description — has a point **inside** that area.

### Fix
**20 states** take their Wikidata item's coordinate (33 with the second pass below). Only `latitude` and `longitude` change.

| id | State | Stored point was | Wikidata |
|---|---|---|---|
| 4691 | Donetska (UA) | near Kyiv | Q2012050 |
| 4668 | Zhytomyrska (UA) | near Kyiv | Q40637 |
| 4681 | Khmelnytska (UA) | near Kyiv | Q171331 |
| 4669 | Vinnytska (UA) | near Kyiv | Q166709 |
| 4680 | Cherkaska (UA) | Donetsk Oblast | Q161808 |
| 4678 | Chernivetska (UA) | near Lviv | Q168856 |
| 3567 | Harju (EE) | at sea off Hiiumaa | Q180200 |
| 2654 | Comoé (CI) | Lagunes district | Q16629374 |
| 4959 | Bono (GH) | Bono East | Q64685186 |
| 4961 | Oti (GH) | Eastern Region | Q48804004 |
| 1911 | Altai Krai (RU) | Altai Republic | Q5942 |
| 3470 | Hidalgo (MX) | Nuevo León / Tamaulipas border | Q80903 |
| 396 | Central (UG) | Northern Region | Q429685 |
| 1397 | Chiriquí Province (PA) | Panama City | Q739651 |
| 2878 | Meta (CO) | Casanare–Vichada border | Q238629 |
| 2826 | La Araucanía (CL) | Los Lagos | Q2176 |
| 4983 | Charente (FR) | Charente-Maritime | Q3266 |
| 5054 | Vienne (FR) | the town of Vienne, Isère | Q12804 |
| 1009 | Innlandet (NO) | Møre og Romsdal coast | Q56404886 |
| 1341 | Aurora (PH) | Isabela | Q13730 |

### Second pass, with corrected state IDs
#1662 corrects 277 state Wikidata IDs. Comparing every state's point with its corrected item's point finds 13 more
states whose point lies among another state's cities (or outside the country) while the Wikidata point lies among
their own. Those take the Wikidata point too; for Loire, Mureș and Line Islands this uses the ID as corrected in #1662.

| id | State | Stored point was | Wikidata |
|---|---|---|---|
| 1832 | Line (KI) | Betio, Gilbert Islands (3,290 km away) | Q31866835 |
| 5010 | Loire (FR) | Maine-et-Loire (the Pays de la Loire region's point) | Q12569 |
| 4692 | Chernihivska (UA) | Kyiv | Q167874 |
| 1530 | Denmark (DK) | Funen (Southern Denmark) | Q26073 |
| 4915 | Mureș (RO) | Alba County | Q190711 |
| 3568 | Lääne (EE) | Järva County | Q189968 |
| 1210 | Puntarenas (CR) | at sea off Quepos | Q502170 |
| 370 | Western (UG) | near Masaka (Central Region) | Q2559188 |
| 260 | Western (RW) | in Uganda, north of Rwanda | Q737354 |
| 524 | Khojali (AZ) | Lankaran | Q330790 |
| 553 | Agdash (AZ) | near Gədəbəy | Q275784 |
| 3727 | Moravica (RS) | Pčinja district, by the Kosovo border | Q915380 |
| 3555 | Hiiu (EE) | near Tallinn (Harju) | Q1466462 |

### Left for follow-up
- *Loire*, *Denmark* (Capital Region) and *Mureș* are fixed in the second pass above.
- *Newfoundland and Labrador* (CA): the Wikidata point is outside the cities' area too; to check.
- The Danish state is still named *Denmark*; it is the Capital Region (Region Hovedstaden).

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/states/states.json` — coordinates on 33 states
