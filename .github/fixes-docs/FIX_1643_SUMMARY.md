# Fix Summary: Data-correctness audit (#1643)

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each,
newest last.

## Puerto Rico: municipalities geocoded to same-named places abroad

### Problem
Ten records of `contributions/cities/PR.json` (the 2022 batch, `id` 153xxx) carried the coordinates (nine of them also the
`wikiDataId`) of a same-named place elsewhere — they had been geocoded by name without a country filter:

| id | Record | Was at | Old `wikiDataId` |
|---|---|---|---|
| 153557 | Barceloneta | Barcelona, Spain | Q526438 |
| 153572 | Corozal | Corozal, Belize | Q451786 |
| 153574 | Dorado | New York State | Q8837 |
| 153576 | Florida | Florida, US state | Q812 |
| 153585 | Isabela | Isabela, Philippines | Q230864 |
| 153590 | Lares | Los Angeles area | Q504377 |
| 153591 | Las Marías | North Carolina | Q2485590 (already right) |
| 153609 | Río Grande | Coahuila, Mexico | Q160636 |
| 153611 | Salinas | Salinas, California | Q229252 |
| 153615 | San Sebastián | San Sebastián, Spain | Q10313 |

### Fix
PR.json has one record per municipality (its "states"), so each record takes its municipality's Wikidata item
("municipality of Puerto Rico", Q263639) — the ID and that item's coordinates:

| Record | `wikiDataId` | Coordinates |
|---|---|---|
| Barceloneta | Q2025087 | 18.45055556, -66.53861111 |
| Corozal | Q1884385 | 18.30416667, -66.32777778 |
| Dorado | Q2217567 | 18.45888889, -66.26777778 |
| Florida | Q2271950 | 18.37333333, -66.56000000 |
| Isabela | Q2307520 | 18.51305556, -67.07000000 |
| Lares | Q1026894 | 18.29500000, -66.87861111 |
| Las Marías | Q2485590 (unchanged) | 18.25138889, -66.99333333 |
| Río Grande | Q979996 | 18.38027778, -65.83138889 |
| Salinas | Q637330 | 18.01722222, -66.25361111 |
| San Sebastián | Q2413209 | 18.33722222, -66.99055556 |

*Lares* also carried the native name "Casas", picked up from the wrong match; it is now "Lares". Timezones were
already `America/Puerto_Rico`.

### Verification
- Eight of these municipality items are already the IDs of the same towns in `contributions/cities/US.json`
  (state PR).
- All 78 PR.json records now fall inside Puerto Rico's bounding box, and no `wikiDataId` is shared within the file.

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/PR.json` — coordinates on 10 records, `wikiDataId` on 9, native name on 1

## City coordinates pointing at the wrong place

### Problem
Sixteen cities had coordinates that do not belong to them:

- **15 French communes.** Their department (`state_code`) and census population identify the commune, but the
  stored point is elsewhere — found while re-matching France's Wikidata IDs (#1641, #1642), where the review
  confirmed each identity. *Saint-Leu* (Réunion, population 29,278) and *Saint-François* (Guadeloupe, 13,577)
  sat on same-named hamlets in mainland France; *Ballon* (Charente-Maritime, 823) on Ballon in the Sarthe;
  *Mareuil* (Charente, 359) on Mareuil in the Dordogne; *Doubs* and *Mayenne* on points near their departments'
  centres; the rest (Buxerolles, Charmes-la-Grande, Louplande, Puiseaux and five Corsican communes) 6–33 km off.
- **Chile's *Juan Fernández*** (the island commune, Q14454) sat in open ocean at −30.03, −82.05, 500 km north-west
  of the islands, with the Magallanes timezone.

### Fix
Each record takes the coordinate of its commune's Wikidata item. Timezones follow where the point moves to
another zone: *Saint-François* → `America/Guadeloupe`, *Saint-Leu* → `Indian/Reunion`, *Juan Fernández* →
`America/Santiago` (the islands keep mainland Chile time). Only `latitude`, `longitude` and those three
`timezone` values change.

| id | City | Now at | Wikidata |
|---|---|---|---|
| 39754 | Ballon (17) | 46.0569, −0.9522 | Q936602 |
| 40403 | Buxerolles (86) | 46.5975, 0.3492 | Q1359393 |
| 155677 | Charmes-la-Grande (52) | 48.3839, 4.9933 | Q729460 |
| 41547 | Doubs (25) | 46.9267, 6.3500 | Q382541 |
| 41994 | Furiani (2B) | 42.6567, 9.4331 | Q637279 |
| 42084 | Ghisonaccia (2B) | 42.0164, 9.4050 | Q637313 |
| 43606 | Louplande (72) | 47.9433, 0.0417 | Q943178 |
| 43650 | Lumio (2B) | 42.5783, 8.8333 | Q246410 |
| 43825 | Mareuil (16) | 45.7736, −0.1411 | Q520079 |
| 43969 | Mayenne (53) | 48.3031, −0.6136 | Q213513 |
| 44363 | Morosaglia (2B) | 42.4353, 9.3000 | Q270675 |
| 44732 | Oletta (2B) | 42.6325, 9.3556 | Q650588 |
| 45320 | Puiseaux (45) | 48.2053, 2.4711 | Q846273 |
| 45943 | Saint-François (971) | 16.2514, −61.2739 | Q608483 |
| 46192 | Saint-Leu (974) | −21.1664, 55.2869 | Q1649363 |
| 148461 | Juan Fernández (CL) | −33.6167, −78.8667 | Q14454 |

*Chef-Boutonne* was also flagged but is left alone: its stored point is by the town hall, and it is Wikidata's
point for the merged commune that lies 5.8 km off.

### Verification
- Each Wikidata item is the commune itself (INSEE code in the record's department; Q14454 "commune in Valparaíso
  Province, Chile", already the record's `wikiDataId`) and has one coordinate.
- The two overseas communes fall inside France's overseas bounds once the coordinate-validator fix (#1645) is in.

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/FR.json` — coordinates on 15 records, timezone on 2
- `contributions/cities/CL.json` — coordinates and timezone on 1 record

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

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/states/states.json` — coordinates on 20 states

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
| 3567 | Harju (EE) | on Hiiumaa (the village of Pühalepa-Harju) | Q180200 |
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
| 1530 | Denmark (DK) | at sea about 10 km north of Funen | Q26073 |
| 4915 | Mureș (RO) | Alba County | Q190711 |
| 3568 | Lääne (EE) | Jõgeva County (a farm named "Lääne" in Põltsamaa parish) | Q189968 |
| 1210 | Puntarenas (CR) | at sea off Quepos | Q502170 |
| 370 | Western (UG) | near Masaka (Central Region) | Q2559188 |
| 260 | Western (RW) | in Uganda, north of Rwanda | Q737354 |
| 524 | Khojali (AZ) | Lankaran | Q330790 |
| 553 | Agdash (AZ) | Kalbajar District | Q275784 |
| 3727 | Moravica (RS) | Pčinja district, by the Kosovo border | Q915380 |
| 3555 | Hiiu (EE) | near Tallinn (Harju) | Q1466462 |

### Left for follow-up
- *Loire*, *Denmark* (Capital Region) and *Mureș* are fixed in the second pass above.
- *Newfoundland and Labrador* (CA): the Wikidata point is outside the cities' area too; to check.
- The Danish state is still named *Denmark*; it is the Capital Region (Region Hovedstaden).
- Lääne and Harju had been geocoded to same-named places elsewhere (a farm, a village).

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/states/states.json` — coordinates on 33 states

## Puerto Rico: municipalities geocoded to same-named places abroad

### Problem
Ten records of `contributions/cities/PR.json` (the 2022 batch, `id` 153xxx) carried the coordinates (nine of them also the
`wikiDataId`) of a same-named place elsewhere — they had been geocoded by name without a country filter:

| id | Record | Was at | Old `wikiDataId` |
|---|---|---|---|
| 153557 | Barceloneta | Barcelona, Spain | Q526438 |
| 153572 | Corozal | Corozal, Belize | Q451786 |
| 153574 | Dorado | New York State | Q8837 |
| 153576 | Florida | Florida, US state | Q812 |
| 153585 | Isabela | Isabela, Philippines | Q230864 |
| 153590 | Lares | Los Angeles area | Q504377 |
| 153591 | Las Marías | North Carolina | Q2485590 (already right) |
| 153609 | Río Grande | Coahuila, Mexico | Q160636 |
| 153611 | Salinas | Salinas, California | Q229252 |
| 153615 | San Sebastián | San Sebastián, Spain | Q10313 |

### Fix
PR.json has one record per municipality (its "states"), so each record takes its municipality's Wikidata item
("municipality of Puerto Rico", Q263639) — the ID and that item's coordinates:

| Record | `wikiDataId` | Coordinates |
|---|---|---|
| Barceloneta | Q2025087 | 18.45055556, -66.53861111 |
| Corozal | Q1884385 | 18.30416667, -66.32777778 |
| Dorado | Q2217567 | 18.45888889, -66.26777778 |
| Florida | Q2271950 | 18.37333333, -66.56000000 |
| Isabela | Q2307520 | 18.51305556, -67.07000000 |
| Lares | Q1026894 | 18.29500000, -66.87861111 |
| Las Marías | Q2485590 (unchanged) | 18.25138889, -66.99333333 |
| Río Grande | Q979996 | 18.38027778, -65.83138889 |
| Salinas | Q637330 | 18.01722222, -66.25361111 |
| San Sebastián | Q2413209 | 18.33722222, -66.99055556 |

*Lares* also carried the native name "Casas", picked up from the wrong match; it is now "Lares". Timezones were
already `America/Puerto_Rico`.

### Verification
- Eight of these municipality items are already the IDs of the same towns in `contributions/cities/US.json`
  (state PR).
- All 78 PR.json records now fall inside Puerto Rico's bounding box, and no `wikiDataId` is shared within the file.

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/PR.json` — coordinates on 10 records, `wikiDataId` on 9, native name on 1

## City coordinates pointing at the wrong place

### Problem
Sixteen cities had coordinates that do not belong to them:

- **15 French communes.** Their department (`state_code`) and census population identify the commune, but the
  stored point is elsewhere — found while re-matching France's Wikidata IDs (#1641, #1642), where the review
  confirmed each identity. *Saint-Leu* (Réunion, population 29,278) and *Saint-François* (Guadeloupe, 13,577)
  sat on same-named hamlets in mainland France; *Ballon* (Charente-Maritime, 823) on Ballon in the Sarthe;
  *Mareuil* (Charente, 359) on Mareuil in the Dordogne; *Doubs* and *Mayenne* on points near their departments'
  centres; the rest (Buxerolles, Charmes-la-Grande, Louplande, Puiseaux and five Corsican communes) 6–33 km off.
- **Chile's *Juan Fernández*** (the island commune, Q14454) sat in open ocean at −30.03, −82.05, 500 km north-west
  of the islands, with the Magallanes timezone.

### Fix
Each record takes the coordinate of its commune's Wikidata item. Timezones follow where the point moves to
another zone: *Saint-François* → `America/Guadeloupe`, *Saint-Leu* → `Indian/Reunion`, *Juan Fernández* →
`America/Santiago` (the islands keep mainland Chile time). Only `latitude`, `longitude` and those three
`timezone` values change.

| id | City | Now at | Wikidata |
|---|---|---|---|
| 39754 | Ballon (17) | 46.0569, −0.9522 | Q936602 |
| 40403 | Buxerolles (86) | 46.5975, 0.3492 | Q1359393 |
| 155677 | Charmes-la-Grande (52) | 48.3839, 4.9933 | Q729460 |
| 41547 | Doubs (25) | 46.9267, 6.3500 | Q382541 |
| 41994 | Furiani (2B) | 42.6567, 9.4331 | Q637279 |
| 42084 | Ghisonaccia (2B) | 42.0164, 9.4050 | Q637313 |
| 43606 | Louplande (72) | 47.9433, 0.0417 | Q943178 |
| 43650 | Lumio (2B) | 42.5783, 8.8333 | Q246410 |
| 43825 | Mareuil (16) | 45.7736, −0.1411 | Q520079 |
| 43969 | Mayenne (53) | 48.3031, −0.6136 | Q213513 |
| 44363 | Morosaglia (2B) | 42.4353, 9.3000 | Q270675 |
| 44732 | Oletta (2B) | 42.6325, 9.3556 | Q650588 |
| 45320 | Puiseaux (45) | 48.2053, 2.4711 | Q846273 |
| 45943 | Saint-François (971) | 16.2514, −61.2739 | Q608483 |
| 46192 | Saint-Leu (974) | −21.1664, 55.2869 | Q1649363 |
| 148461 | Juan Fernández (CL) | −33.6167, −78.8667 | Q14454 |

*Chef-Boutonne* was also flagged but is left alone: its stored point is by the town hall, and it is Wikidata's
point for the merged commune that lies 5.8 km off.

### Verification
- Each Wikidata item is the commune itself (INSEE code in the record's department; Q14454 "commune in Valparaíso
  Province, Chile", already the record's `wikiDataId`) and has one coordinate.
- The two overseas communes fall inside France's overseas bounds once the coordinate-validator fix (#1645) is in.

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/FR.json` — coordinates on 15 records, timezone on 2
- `contributions/cities/CL.json` — coordinates and timezone on 1 record

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

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/states/states.json` — coordinates on 20 states

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
| 3567 | Harju (EE) | on Hiiumaa (the village of Pühalepa-Harju) | Q180200 |
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
| 1530 | Denmark (DK) | at sea about 10 km north of Funen | Q26073 |
| 4915 | Mureș (RO) | Alba County | Q190711 |
| 3568 | Lääne (EE) | Jõgeva County (a farm named "Lääne" in Põltsamaa parish) | Q189968 |
| 1210 | Puntarenas (CR) | at sea off Quepos | Q502170 |
| 370 | Western (UG) | near Masaka (Central Region) | Q2559188 |
| 260 | Western (RW) | in Uganda, north of Rwanda | Q737354 |
| 524 | Khojali (AZ) | Lankaran | Q330790 |
| 553 | Agdash (AZ) | Kalbajar District | Q275784 |
| 3727 | Moravica (RS) | Pčinja district, by the Kosovo border | Q915380 |
| 3555 | Hiiu (EE) | near Tallinn (Harju) | Q1466462 |

### Left for follow-up
- *Loire*, *Denmark* (Capital Region) and *Mureș* are fixed in the second pass above.
- *Newfoundland and Labrador* (CA): the Wikidata point is outside the cities' area too; to check.
- The Danish state is still named *Denmark*; it is the Capital Region (Region Hovedstaden).
- Lääne and Harju had been geocoded to same-named places elsewhere (a farm, a village).

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/states/states.json` — coordinates on 33 states

## States with a broken parent link

### How they were found
A scan of `states.json` checked every `parent_id`: it must name an existing state of the same country, other than
the state itself. Found by the independent review of #1657, then confirmed by the scan:

| Problem | States |
|---|---:|
| Tuscan provinces whose parent is Udine (1764, a province in Friuli-Venezia Giulia) instead of Tuscany (1664) | 8 |
| Spanish provinces that are their own parent | 3 |

Asturias, Cantabria and La Rioja are single-province autonomous communities. Their province records (1160, 1170, 1171)
point to themselves; the community records (5701–5703) were added later and never linked.

### Added after the independent review
The review checked every child state's parent against its Wikidata "located in" chain and ISO 3166-2 membership and
found four links that point to a real state of the right country, but the wrong one:

| id | State | parent was | Now |
|---|---|---|---|
| 3287 | Nouaceur (MA) | 4927 Rabat-Salé-Kénitra | 3303 Casablanca-Settat |
| 3302 | Chtouka-Aït Baha (MA) | 3303 Casablanca-Settat | 3295 Souss-Massa |
| 5039 | Haute-Saône (FR) | 4820 Grand-Est | 4825 Bourgogne-Franche-Comté |
| 5092 | Badajoz (ES) | 5325 Andalusia | 5333 Extremadura |

Left for a decision: Sulu (PH), whose parent is ARMM; the Supreme Court excluded Sulu from Bangsamoro in 2024.

### Fix
Only `parent_id` changes, on 15 states.

| id | State | Country | parent_id was | Now |
|---|---|---|---|---|
| (8) | Pisa, Pistoia, Prato, Siena, Livorno, Lucca, Massa and Carrara, Grosseto | IT | 1764 Udine | 1664 Tuscany |
| 1160 | Asturias (province) | ES | 1160 (itself) | 5701 Asturias, Principality of |
| 1170 | Cantabria (province) | ES | 1170 (itself) | 5702 Cantabria |
| 1171 | La Rioja (province) | ES | 1171 (itself) | 5703 La Rioja |

### Also found (not changed here)
The same scan finds 159 states (after this PR) whose `level` is not below their parent's: provinces at level 1 under level-1 regions
in Morocco (59), Burkina Faso (45) and Belgium (10); Guinea's prefectures and regions both at level 2 (29); Fiji's
provinces at level 1 under level-2 divisions (14); two Guinea-Bissau regions at level 1 under a province. Spanish
provinces are level 1 and their communities have no level. Changing levels could alter what API users get when they
filter by level, so it waits for a decision in #1643.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/states/states.json` — `parent_id` on 15 states

## Cities filed under the wrong state

### How they were found
A repo-wide check flagged every city whose ten nearest cities in the same country all lie in one other state,
none in its own: **305 candidates** in 56 countries. That neighbour test alone is not reliable, so each candidate
was checked in three steps:

1. **Wikidata.** Find the item with the record's name (label or alias, any language) within 2 km of the record,
   and follow its "located in" (P131) links up to the country's states, matched by each state's own
   `wikiDataId`. Result: **106 confirmed** (the place lies in the neighbours' state, not the filed one), **99 false
   alarms** (it lies in the filed state — mostly border towns) and **100 unresolved** (no same-named item nearby, or
   contained in neither).
2. **Guards** against a wrong *point* posing as a wrong *state*: set aside records whose filed state also
   contains a same-named place on Wikidata (56 — the record may be that place with bad coordinates), and records
   whose population disagrees with the matched item's by more than a factor of three (7); 58 records in all,
   as some failed both. The name search used
   exact labels, so it missed namesakes spelt differently or linked only to the country; four of the 44 have one
   (*Bon-Secours*: the commune Bonsecours in Seine-Maritime; *Ossé*: Osse in Doubs; *Panzhuang*: a town in Hebei;
   *Kozjak*: a village near Loznica). Each was checked by hand and the move holds: the record's type, population
   and coordinates match the place in the new state.
3. **Hand check** of the remaining 48, which rejected four: *Avellaneda* (a partido of Buenos Aires Province, not
   the city), *Bogotá D.C.* (its own capital district), *Nakhchivan* city (its own subdivision, separate from the
   autonomous republic) and *Piobesi Torinese* (a commune of Turin; the matched item is a stub with a wrong
   location).

### Fix
**44 cities** move to the state they are in. Only `state_id` and `state_code` change; coordinates, timezones and
IDs stay as they are.

| id | City | Country | Was filed under | Now | Wikidata evidence |
|---|---|---|---|---|---|
| 422 | Jrashen | AM | Yerevan (ER) | Ararat (AR) | Q2222156 |
| 555 | Vardadzor | AM | Yerevan (ER) | Gegharkunik (GR) | Q2636168 |
| 19724 | Jijiang | CN | Fujian (FJ) | Chongqing (CQ) | Q113481539 |
| 149171 | Fanzhuang | CN | Guizhou (GZ) | Tianjin (TJ) | Q28798456 |
| 149191 | Panzhuang | CN | Hebei (HE) | Tianjin (TJ) | Q13683271 |
| 149194 | Shangcang | CN | Zhejiang (ZJ) | Tianjin (TJ) | Q10867194 |
| 22042 | Kolossi | CY | Larnaca (Larnaka) (03) | Limassol (Leymasun) (02) | Q1584818, Q3353547 |
| 33090 | Cabezón | ES | León (LE) | Valladolid (VA) | Q24002822 |
| 33983 | El Burgo de Osma | ES | León (LE) | Soria (SO) | Q24015514, Q485129 |
| 34400 | Gamonal | ES | León (LE) | Burgos (BU) | Q133999496, Q3095047 |
| 34691 | Huerta del Rey | ES | León (LE) | Burgos (BU) | Q1645211, Q23999304 |
| 34848 | La Adrada | ES | León (LE) | Ávila (AV) | Q120172201, Q1606366 |
| 34850 | La Alberca | ES | León (LE) | Salamanca (SA) | Q1012961, Q24014011 |
| 34859 | La Bouza | ES | León (LE) | Salamanca (SA) | Q584647 |
| 34873 | La Fuente de San Esteban | ES | León (LE) | Salamanca (SA) | Q1637591, Q24014119 |
| 34889 | La Lastrilla | ES | León (LE) | Segovia (SG) | Q1919663, Q24014504 |
| 34901 | La Pedraja de Portillo | ES | León (LE) | Valladolid (VA) | Q1651735, Q24017004 |
| 38078 | Villagonzalo-Pedernales | ES | León (LE) | Burgos (BU) | Q129571445, Q23991996 |
| 40109 | Bon-Secours | FR | Seine-Maritime (76) | Bouches-du-Rhône (13) | Q2909806 |
| 44791 | Ossé | FR | Doubs (25) | Ille-et-Vilaine (35) | Q49359414, Q624139 |
| 53287 | Traganón | GR | Peloponnese (J) | West Greece (G) | Q1923665, Q21588630 |
| 154230 | Kalampaka | GR | Central Greece (H) | Thessaly (E) | Q15979847, Q940330 |
| 53647 | Samayac | GT | Quetzaltenango  (09) | Suchitepéquez  (10) | Q25175669, Q371216 |
| 147534 | Paras Rampur | IN | Uttar Pradesh (UP) | Punjab (PB) | Q7135859 |
| 147712 | Bijur | IN | Maharashtra (MH) | Karnataka (KA) | Q4907289 |
| 147778 | Kamatgi | IN | Maharashtra (MH) | Karnataka (KA) | Q6356167 |
| 63177 | Qīr Moāv | JO | Ma'an (MN) | Karak (KA) | Q27125240 |
| 64797 | Kapsowar | KE | Kilifi (14) | Elgeyo-Marakwet (05) | Q1009149 |
| 68680 | Buenavista de Benito Juárez | MX | Michoacán de Ocampo (MIC) | Puebla (PUE) | Q49867786 |
| 69219 | Coajomulco | MX | Michoacán de Ocampo (MIC) | Morelos (MOR) | Q61270339 |
| 70747 | Huautla de Jiménez | MX | Puebla (PUE) | Oaxaca (OAX) | Q20145546 |
| 73289 | San Andrés Ocotlán | MX | Morelos (MOR) | Estado de México (MEX) | Q20240027 |
| 73955 | San Juan Yautepec | MX | Morelos (MOR) | Estado de México (MEX) | Q61247985 |
| 74235 | San Miguel del Milagro | MX | Puebla (PUE) | Tlaxcala (TLA) | Q6119471 |
| 74339 | San Pedro Huaquilpan | MX | Morelos (MOR) | Hidalgo (HID) | Q50031422 |
| 80345 | Lídice | PA | Panamá (8) | Panamá Oeste (10) | Q931897 |
| 145911 | Davila | PH | Abra (ABR) | Ilocos Norte (ILN) | Q31563030 |
| 88262 | Sulęcin | PL | Lesser Poland (12) | Lubusz (08) | Q1113241, Q2615990 |
| 88704 | Zawidów | PL | Silesia (24) | Lower Silesia (02) | Q167756, Q33526100 |
| 143244 | Alcains | PT | Guarda (09) | Castelo Branco (05) | Q1024258, Q131539725 |
| 97254 | Kozjak | RS | Mačva (08) | South Banat (04) | Q1000445 |
| 97402 | Sumulicë | RS | Pirot (22) | Pčinja (24) | Q3104463, Q49368487 |
| 98568 | Gorskaya | RU | Leningrad (LEN) | Saint Petersburg (SPE) | Q4145885, Q4145889 |
| 148564 | Ha'il | SA | Eastern Province (04) | Ha'il (06) | Q675568 |

### Verification
- Every new `state_id` belongs to the record's country and its `iso2` equals the new `state_code`.
- An independent review checked all 44 against Wikidata and Wikipedia: 44 correct, every new state at the same
  administrative level as the old one, and every old and new state's own `wikiDataId` right.
- The 58 records set aside by the guards and the 100 unresolved ones are left unchanged for a hand review.

### Left for follow-up
- **Duplicates.** About 15 of the moved records duplicate a record already in their new state (10 of the 11
  Spanish ones, and one each in GR, JO, KE, PH, RS, SA). Merging them is part of the duplicate-records decision.
- **Wrong `wikiDataId`s** on 7 moved records (19724, 33090, 34691, 34859, 38078, 40109, 97402) point to other
  places; not changed here.
- **More of the same:** 12 more Spanish records filed under León lie in other provinces (e.g. El Barco de Ávila,
  Las Navas del Marqués); *La Villette* (a Marseille quartier filed under Calvados) and *Weiwangzhuang* (Tianjin,
  filed under Shandong). They were held back or unresolved here and go into the next pass.

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/*.json` (18 files) — `state_id` and `state_code` on 44 records

## Mexican cities filed under the wrong state

### How they were found
Matching `MX.json` to its GeoNames source (the #1634 work) showed 166 records whose GeoNames entry lies in a
different state from the one they are filed under — 82 of them filed under Morelos. After removing the records
already moved in the neighbour-based pass, 161 were checked on Wikidata the same way: the item with the record's
name within 2 km of its point, followed up its "located in" (P131) chain to exactly one Mexican state (matched by
the state's own `wikiDataId`).

| Result | Records |
|---|---:|
| Wikidata places it in exactly one other state | 150 |
| … and no same-named place in the filed state, population consistent | **127** |
| Held back: a same-named place exists in the filed state | 23 |
| Wikidata agrees with the filed state | 5 |
| Unresolved (no same-named item nearby, or contained in several) | 6 |

For all 127, the new state is the one GeoNames gives too — two independent sources agree.

### Fix
**127 cities** move to the state they are in. Only `state_id` and `state_code` change; every record's
`timezone` already matches its new state (including *Yécora*, Chihuahua → Sonora).

| Was filed under | Now | Records |
|---|---|---:|
| Morelos (MOR) | Estado de México (MEX) | 73 |
| Estado de México (MEX) | Michoacán de Ocampo (MIC) | 29 |
| Hidalgo (HID) | Estado de México (MEX) | 4 |
| Hidalgo (HID) | Puebla (PUE) | 3 |
| Puebla (PUE) | Tlaxcala (TLA) | 3 |
| Querétaro (QUE) | Guanajuato (GUA) | 2 |
| Hidalgo (HID) | Tlaxcala (TLA) | 2 |
| Michoacán de Ocampo (MIC) | Querétaro (QUE) | 1 |
| Guerrero (GRO) | Oaxaca (OAX) | 1 |
| Coahuila de Zaragoza (COA) | Durango (DUR) | 1 |
| Guerrero (GRO) | Puebla (PUE) | 1 |
| Estado de México (MEX) | Guanajuato (GUA) | 1 |
| Puebla (PUE) | Veracruz de Ignacio de la Llave (VER) | 1 |
| Veracruz de Ignacio de la Llave (VER) | Estado de México (MEX) | 1 |
| Hidalgo (HID) | Veracruz de Ignacio de la Llave (VER) | 1 |
| Hidalgo (HID) | San Luis Potosí (SLP) | 1 |
| Veracruz de Ignacio de la Llave (VER) | Puebla (PUE) | 1 |
| Chihuahua (CHH) | Sonora (SON) | 1 |

<details><summary>All 127 records</summary>

| id | City | Move | Wikidata evidence |
|---|---|---|---|
| 68023 | Acachuén | MEX → MIC | Q49846289 |
| 68031 | Acalpican de Morelos | MEX → MIC | Q49845719 |
| 68107 | Agua Caliente | MEX → MIC | Q20274371 |
| 68366 | Arroyo Vista Hermosa | MOR → MEX | Q61236298 |
| 68742 | Calle Real | MOR → MEX | Q61234959 |
| 68815 | Carapán | MEX → MIC | Q5748894 |
| 68918 | Cerritos de Cárdenas | MOR → MEX | Q61245966 |
| 68948 | Chachahuantla | HID → PUE | Q8344456 |
| 69066 | Chilchota | MEX → MIC | Q20275622 |
| 69095 | Chitejé de Garabato | MIC → QUE | Q61287491 |
| 69523 | Coyotillos | HID → MEX | Q5790467 |
| 69980 | El Habillal | MEX → MIC | Q49915139 |
| 70004 | El Jicaral | GRO → OAX | Q20230841 |
| 70094 | El Paredón | HID → PUE | Q61296650 |
| 70103 | El Pilar | MEX → MIC | Q61261837 |
| 70307 | Enthavi | MOR → MEX | Q20238414 |
| 70376 | Etúcuaro | MEX → MIC | Q5850204 |
| 70730 | Huancito | MEX → MIC | Q61237249 |
| 70802 | Huitrón | COA → DUR | Q49950102 |
| 70897 | Ixcamilpa | GRO → PUE | Q12814736, Q6793335 |
| 70985 | Jaltepec | MOR → MEX | Q20236036 |
| 70999 | Janambo | MEX → MIC | Q61261926 |
| 71000 | Janamuato | MEX → MIC | Q4495388 |
| 71192 | La Calle | MEX → GUA | Q49997889 |
| 71320 | La Huanica | MOR → MEX | Q61246336 |
| 71517 | La Unidad Huitzizilapan | MOR → MEX | Q61244805 |
| 71636 | Las Ranas | MEX → MIC | Q4254716 |
| 71953 | Manantiales | PUE → VER | Q61253618 |
| 72126 | Miguel Bocanegra | MOR → MEX | Q20148570 |
| 72474 | Ocumicho | MEX → MIC | Q61239354 |
| 72977 | Puerto de Carroza | QUE → GUA | Q50029157 |
| 72979 | Puerto de Nieto | QUE → GUA | Q49942628 |
| 73013 | Pérez de Galeana | MOR → MEX | Q6093836 |
| 73101 | Reyes Acozac | MOR → MEX | Q5980300 |
| 73219 | Salitrillo | HID → MEX | Q61248120 |
| 73276 | San Andrés Cuexcontitlán | MOR → MEX | Q61236088 |
| 73335 | San Antonio Guaracha | MEX → MIC | Q61269269 |
| 73381 | San Antonio del Puente | MOR → MEX | Q61234890 |
| 73428 | San Bartolomé Tlaltelulco | MOR → MEX | Q20288201 |
| 73492 | San Diego Alcalá | MOR → MEX | Q20288602 |
| 73525 | San Felipe Teotitlán | MOR → MEX | Q44664818 |
| 73555 | San Francisco Chimalpa | MOR → MEX | Q6118758 |
| 73599 | San Francisco Tetetla | MOR → MEX | Q61235157 |
| 73635 | San Gaspar Tlahuelilpan | MOR → MEX | Q112147189, Q61245372 |
| 73701 | San Jerónimo Acazulco | MOR → MEX | Q7414369 |
| 73706 | San Jerónimo Chicahualco | MOR → MEX | Q112147199, Q61245388 |
| 73734 | San Jose Solís | MOR → MEX | Q61246031 |
| 73737 | San José | MOR → MEX | Q61235812 |
| 73752 | San José Buenavista el Grande | MOR → MEX | Q61234938 |
| 73759 | San José Comalco | MOR → MEX | Q61234664 |
| 73760 | San José Corral Blanco | HID → PUE | Q61296583 |
| 73849 | San José el Llanito | MOR → MEX | Q61245333 |
| 73917 | San Juan Pueblo Nuevo | MOR → MEX | Q6119124 |
| 73939 | San Juan Tilapa | MOR → MEX | Q20144188 |
| 73950 | San Juan Xochiaca | MOR → MEX | Q61234766 |
| 73957 | San Juan Zitlaltepec | MOR → MEX | Q2183319 |
| 73978 | San Juan la Isla | MOR → MEX | Q6119171 |
| 74001 | San Lorenzo Cuauhtenco | MOR → MEX | Q61249621 |
| 74007 | San Lorenzo Nenamicoyan | MOR → MEX | Q61245228 |
| 74008 | San Lorenzo Oyamel | MOR → MEX | Q20144948 |
| 74048 | San Luis Ayucán | MOR → MEX | Q61245277 |
| 74071 | San Marcos Guaquilpan | HID → TLA | Q61276353 |
| 74080 | San Marcos de la Cruz | MOR → MEX | Q61249624 |
| 74118 | San Mateo Atarasquíllo | MOR → MEX | Q20240217 |
| 74120 | San Mateo Ayecac | PUE → TLA | Q61276672 |
| 74131 | San Mateo Otzacatipan | MOR → MEX | Q6119380 |
| 74158 | San Miguel Almaya | MOR → MEX | Q20293661 |
| 74162 | San Miguel Ameyalco | MOR → MEX | Q20146811 |
| 74164 | San Miguel Atepoxco | MOR → MEX | Q61244698 |
| 74168 | San Miguel Balderas | MOR → MEX | Q20293701 |
| 74219 | San Miguel Totoltepec | MOR → MEX | Q61236019 |
| 74231 | San Miguel de La Victoria | MOR → MEX | Q61245237 |
| 74255 | San Nicolás Coatepec | MOR → MEX | Q20147741 |
| 74259 | San Nicolás Peralta | MOR → MEX | Q61245529 |
| 74261 | San Nicolás Solís | MOR → MEX | Q61245997 |
| 74264 | San Nicolás Tlazala | MOR → MEX | Q61249638 |
| 74285 | San Pablo Autopan | MOR → MEX | Q6119502 |
| 74316 | San Pedro Atlapulco | MOR → MEX | Q61245009 |
| 74375 | San Pedro Techuchulco | MOR → MEX | Q20148863 |
| 74386 | San Pedro Tlaltizapan | MOR → MEX | Q20240290 |
| 74387 | San Pedro Tlanixco | VER → MEX | Q6119568 |
| 74392 | San Pedro Totoltepec | MOR → MEX | Q61236022 |
| 74395 | San Pedro Tultepec | MOR → MEX | Q6119571 |
| 74397 | San Pedro Xalpa | MOR → MEX | Q20264736 |
| 74403 | San Pedro Zictepec | MOR → MEX | Q20240295 |
| 74454 | San Sebastián | MOR → MEX | Q50033383 |
| 74538 | Santa Ana Jilotzingo | MOR → MEX | Q61246424 |
| 74619 | Santa Cruz Ayotuxco | MOR → MEX | Q23985722 |
| 74637 | Santa Cruz Pueblo Nuevo | MOR → MEX | Q20296730 |
| 74651 | Santa Cruz el Porvenir | PUE → TLA | Q61276748 |
| 74698 | Santa Martha | MOR → MEX | Q61245072 |
| 74706 | Santa María Actipac | HID → MEX | Q61249595 |
| 74709 | Santa María Ajoloapan | MOR → MEX | Q61245814 |
| 74712 | Santa María Apaxco | HID → MEX | Q6120538 |
| 74716 | Santa María Atarasquillo | MOR → MEX | Q6120540 |
| 74757 | Santa María Magdalena Ocotitlán | MOR → MEX | Q20297777 |
| 74877 | Santiago Analco | MOR → MEX | Q61245349 |
| 74896 | Santiago Cuaula | HID → TLA | Q61276328 |
| 74933 | Santiago Oxthoc | MOR → MEX | Q61245171 |
| 74945 | Santiago Tepatlaxco | MOR → MEX | Q61244815, Q99333136 |
| 74969 | Santiago Tílapa | MOR → MEX | Q20240440 |
| 74999 | Santo Domingo Aztacameca | MOR → MEX | Q56317938 |
| 75197 | Tamándaro | MEX → MIC | Q20286146 |
| 75201 | Tanaquillo | MEX → MIC | Q61237246 |
| 75203 | Tancazahuela | HID → VER | Q61257824 |
| 75209 | Tangancícuaro de Arista | MEX → MIC | Q20286295 |
| 75234 | Tarécuato | MEX → MIC | Q107563757 |
| 75366 | Tengüecho | MEX → MIC | Q61263923 |
| 75467 | Teremendo | MEX → MIC | Q61268819 |
| 75523 | Tezapotla | HID → SLP | Q61298601 |
| 75538 | Tianguistongo | MOR → MEX | Q21574043 |
| 75598 | Tlachaloya | MOR → MEX | Q61236047 |
| 75626 | Tlacuitlapa | MOR → MEX | Q61233985 |
| 75655 | Tlaltenanguito | MOR → MEX | Q61234678 |
| 75708 | Tlazazalca | MEX → MIC | Q3847160 |
| 75775 | Tres Mezquites | MEX → MIC | Q20290130 |
| 75813 | Tupátaro | MEX → MIC | Q61264837, Q61265624 |
| 75900 | Urén | MEX → MIC | Q61237252 |
| 75954 | Venta de Bravo | MEX → MIC | Q49900102 |
| 76028 | Villa Lázaro Cárdenas | VER → PUE | Q49901631, Q49901639 |
| 76034 | Villa Mariano Matamoros | PUE → TLA | Q20292722 |
| 76036 | Villa Morelos | MEX → MIC | Q12352823 |
| 76076 | Villachuato | MEX → MIC | Q4111421 |
| 76252 | Yécora | CHH → SON | Q22874690 |
| 76322 | Zaragoza de Guadalupe | MOR → MEX | Q20240748 |
| 76344 | Zipiajo | MEX → MIC | Q61238915 |
| 76365 | Zopoco | MEX → MIC | Q20295636 |

</details>

### Verification
- Every new `state_id` is a Mexican state whose `iso2` equals the new `state_code`.
- For every record, GeoNames' state and Wikidata's containing state are the same.

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/MX.json` — `state_id` and `state_code` on 127 records

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
| Move (namesake ruled out by population in 22 of them) | **30** |
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
| 44853 | Parigny | Loire (42) | Manche (50) | Q1062309, Q49360014 | yes |
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

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/FR.json` — `state_id` and `state_code` on 30 records

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

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/MX.json` — `state_id` and `state_code` on 28 records

## Spanish cities filed under the wrong province

**90 Spanish cities** move to the province they are in, found by two checks. They include a provincial capital
and large towns: *Castelló de la Plana* (180,379 people), *Elche* (243,128), *Alcoy* and *Burriana* filed under
Valencia; *La Laguna* (150,661), *La Orotava* and *Los Llanos de Aridane* under Las Palmas; the Zaragoza districts
*Delicias* and *Oliver-Valdefierro* under Huesca.

CSC's own province records point at the wrong Wikidata items, so a "located in" (P131) check against them does not
work: Valencia → Q5720 (Valencian Community), Huesca → Q4040 (Aragon), Las Palmas → Q5813 (Canary Islands);
Alicante → Q11959, Santa Cruz de Tenerife → Q14328, Zaragoza → Q10305, Lugo → Q11125 and Teruel → Q14336 are the
cities. Both checks therefore use the **INE municipality code** (P772) on Wikidata, whose first two digits are the
province.

### Check 1: population fingerprint (49 records)
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames populated
place with the same name (or an alternate name) within 3 km and **exactly the record's population**. GeoNames'
Spanish second-level codes are the same letters as CSC's province `iso2`. For 57 ES records that entry lies in
another province; 7 of them (León records) are moved by #1647, still open. For the other 50, the same-named Wikidata
item within about 2 km of the record's point, or the municipality it is located in, carries an INE code:

| Result | Records |
|---|---:|
| INE province = the GeoNames province, not the filed one | **47** |
| No same-named item with an INE code (spelled differently, or a district without its own code): settled by check 2 or by hand | 3 |

The 3: *Vallehermosa* is Vallehermoso on La Gomera (check 2). *Arenys de Lledó / Arens de Lledó* is 0.0 km from the
Teruel municipality Arens de Lledó (INE 44027), with its exact GeoNames population. *El Grao* (16,026 people) is El
Grau de Castelló: the GeoNames entry with that population is 0.0 km away and the four nearest municipalities are all
in Castellón.

### Check 2: the record's point (41 records)
For every ES record not moved by check 1 or #1647, the three nearest of the 8,277 Wikidata municipalities that have an INE code and coordinates.
40 records have all three in one province other than the filed one, the nearest under 3 km away. A record moves
only when its name agrees with that province: it is one of those municipalities (37), or a same-named GeoNames place
within 3 km lies in that province (2: *Formentera de Segura*, *Vallehermosa*). This catches records whose GeoNames
population has changed since 2019, such as Castelló de la Plana and Elche. The review found two more that the
three-nearest rule missed because Madrid municipalities are close by: *El Tiemblo* and *Las Navas del Marqués*, each
0.2–0.6 km from its Ávila municipality and filed under León.

Held: *La Zubia* (151401), filed under Granada, has the point of La Granada in Barcelona. Its coordinates are
wrong, not its province; not changed here.

### Same-named places in the old province
Seven moved records share a name with a place in the province they were filed under. In each, the point and the
population are the other place's:
- *Corrales*, *La Cuesta* (León) and *San Isidro* (Alicante): 171–1,840 km from the namesake.
- *Lobios*: 75 km from the Ourense municipality. The record is the parish in Sober, Lugo, so CSC keeps no record
  for the Ourense municipality (a coverage gap). Its stored population, 2,512, is GeoNames' figure, not the
  parish's (72 in 2019), so the point is the evidence here, not the population.
- *Fonfría*: population 35, at the Teruel municipality (0.0 km), not the Zamora one.
- *La Seca*: at the Valladolid municipality (0.1 km), not the place in León.
- *El Grao*: Castellón's port district, not Valencia's.

### Fix
Only `state_id` and `state_code` change; every record's `timezone` already fits its new province
(`Europe/Madrid`, or `Atlantic/Canary` in Santa Cruz de Tenerife).

| Move | Records |
|---|---:|
| Valencia → Alicante | 25 |
| Valencia → Castellón | 21 |
| Las Palmas → Santa Cruz de Tenerife | 17 |
| Huesca → Zaragoza | 8 |
| 10 other pairs (Huesca → Teruel, León → Ávila (6), León → Segovia, León → Zamora, Zamora → Teruel, León → Valladolid, Ourense → Lugo, León → Palencia, Alicante → Santa Cruz de Tenerife, León → Burgos) | 19 |

The municipality column names the INE municipality the record lies in (its first two digits are the province).
Check 1 = population fingerprint, 2 = the record's point.

| id | City | Was filed under | Now | Population | Municipality (INE) | Check |
|---|---|---|---|---:|---|---|
| 31943 | Adzaneta | Valencia (V) | Castellón (CS) | 1,462 | Adzaneta (12001) | 1 |
| 32101 | Alcocéber | Valencia (V) | Castellón (CS) | 5,000 | Alcalá de Chivert (12004) | 1 |
| 32123 | Alcoy | Valencia (V) | Alicante (A) | 60,372 | Alcoy (03009) | 2 |
| 32273 | Almassora | Valencia (V) | Castellón (CS) | 28,497 | Almazora (12009) | 2 |
| 32309 | Almozara | Huesca (HU) | Zaragoza (Z) | 25,767 | Zaragoza (50297) | 1 |
| 32450 | Arenys de Lledó / Arens de Lledó | Huesca (HU) | Teruel (TE) | 224 | Arens de Lledó (44027) | 1+2 (by hand) |
| 32456 | Ares del Maestre | Valencia (V) | Castellón (CS) | 227 | Ares del Maestre (12014) | 1 |
| 32669 | Barraco | León (LE) | Ávila (AV) | 2,111 | El Barraco (05022) | 1 |
| 32778 | Benassal | Valencia (V) | Castellón (CS) | 1,329 | Benasal (12026) | 1 |
| 32797 | Benicàssim | Valencia (V) | Castellón (CS) | 20,322 | Benicasim (12028) | 2 |
| 32822 | Benitachell | Valencia (V) | Alicante (A) | 3,630 | Benitachell (03042) | 1 |
| 33032 | Burriana | Valencia (V) | Castellón (CS) | 36,927 | Burriana (12032) | 2 |
| 33438 | Castelló de la Plana | Valencia (V) | Castellón (CS) | 180,379 | Castellón de la Plana (12040) | 2 |
| 33632 | Chilches | Valencia (V) | Castellón (CS) | 2,273 | Chilches (12053) | 2 |
| 33803 | Corrales | León (LE) | Zamora (ZA) | 1,029 | Corrales del Vino (49054) | 1 |
| 33835 | Crevillente | Valencia (V) | Alicante (A) | 24,273 | Crevillente (03059) | 2 |
| 33875 | Cuevas de Vinromá | Valencia (V) | Castellón (CS) | 1,822 | Cuevas de Vinromá (12050) | 1 |
| 33924 | Delicias | Huesca (HU) | Zaragoza (Z) | 110,520 | Zaragoza (50297) | 1 |
| 33979 | El Barco de Ávila | León (LE) | Ávila (AV) | 2,297 | El Barco de Ávila (05021) | 2 |
| 33982 | El Burgo de Ebro | Huesca (HU) | Zaragoza (Z) | 2,704 | El Burgo de Ebro (50062) | 2 |
| 33984 | El Campello | Valencia (V) | Alicante (A) | 30,600 | El Campello (03050) | 2 |
| 33990 | El Castellar | Huesca (HU) | Teruel (TE) | 0 | El Castellar (44070) | 2 |
| 33999 | El Grao | Valencia (V) | Castellón (CS) | 16,026 | Castellón de la Plana (12040) | 1+2 (by hand) |
| 34000 | El Hoyo de Pinares | León (LE) | Ávila (AV) | 2,183 | El Hoyo de Pinares (05102) | 2 |
| 34004 | El Paso | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 8,156 | El Paso (38027) | 2 |
| 34020 | El Tiemblo | León (LE) | Ávila (AV) | 4,526 | El Tiemblo (05241) | 2 (review) |
| 34030 | Elche | Valencia (V) | Alicante (A) | 243,128 | Elche (03065) | 2 |
| 34207 | Fonfría | Zamora (ZA) | Teruel (TE) | 35 | Fonfría (44102) | 2 |
| 34222 | Formentera de Segura | Valencia (V) | Alicante (A) | 2,873 | Formentera del Segura (03070) | 2 |
| 34634 | Hondón de las Nieves | Valencia (V) | Alicante (A) | 2,474 | Hondón de las Nieves (03077) | 1 |
| 34792 | Jalón | Valencia (V) | Alicante (A) | 3,042 | Jalón (03081) | 2 |
| 34808 | Javea | Valencia (V) | Alicante (A) | 28,016 | Jávea (03082) | 1 |
| 34815 | Jijona | Valencia (V) | Alicante (A) | 6,540 | Jijona (03083) | 2 |
| 34854 | La Almunia de Doña Godina | Huesca (HU) | Zaragoza (Z) | 7,937 | La Almunia de Doña Godina (50025) | 2 |
| 34866 | La Carrera | León (LE) | Ávila (AV) | 0 | La Carrera (05051) | 2 |
| 34869 | La Cuesta | León (LE) | Segovia (SG) | 5,000 | Turégano (40208) | 1 |
| 34877 | La Ginebrosa | Huesca (HU) | Teruel (TE) | 196 | La Ginebrosa (44118) | 2 |
| 34880 | La Guancha | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 5,593 | La Guancha (38018) | 2 |
| 34885 | La Iglesuela del Cid | Huesca (HU) | Teruel (TE) | 513 | La Iglesuela del Cid (44126) | 1 |
| 34887 | La Laguna | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 150,661 | San Cristóbal de La Laguna (38023) | 1 |
| 34894 | La Matanza de Acentejo | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 9,160 | La Matanza de Acentejo (38025) | 2 |
| 34898 | La Orotava | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 42,585 | La Orotava (38026) | 2 |
| 34923 | La Romana | Valencia (V) | Alicante (A) | 2,672 | La Romana (03114) | 2 |
| 34925 | La Seca | León (LE) | Valladolid (VA) | 1,013 | La Seca (47158) | 2 |
| 34934 | La Victoria de Acentejo | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 9,313 | La Victoria de Acentejo (38051) | 2 |
| 34987 | Las Navas del Marqués | León (LE) | Ávila (AV) | 5,590 | Las Navas del Marqués (05168) | 2 (review) |
| 34990 | Las Rosas | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 2,000 | Arona (38006) | 1 |
| 35095 | Lobios | Ourense (OR) | Lugo (LU) | 2,512 | Sober (27059) | 1 |
| 35105 | Lomo de Arico | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 7,189 | Arico (38005) | 1 |
| 35122 | Los Gigantes | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 2,721 | Santiago del Teide (38040) | 1 |
| 35124 | Los Llanos de Aridane | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 20,283 | Los Llanos de Aridane (38024) | 2 |
| 35128 | Los Montesinos | Valencia (V) | Alicante (A) | 5,682 | Los Montesinos (03903) | 2 |
| 35135 | Los Silos | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 4,705 | Los Silos (38042) | 2 |
| 35357 | Mazo | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 4,805 | Villa de Mazo (38053) | 1 |
| 35406 | Mequinensa / Mequinenza | Huesca (HU) | Zaragoza (Z) | 2,479 | Mequinenza (50165) | 1 |
| 35546 | Montecanal | Huesca (HU) | Zaragoza (Z) | 20,000 | Zaragoza (50297) | 1 |
| 35592 | Monóvar | Valencia (V) | Alicante (A) | 10,038 | Monóvar (03089) | 2 |
| 35683 | Muro del Alcoy | Valencia (V) | Alicante (A) | 7,983 | Muro de Alcoy (03092) | 1 |
| 35893 | Oliver-Valdefierro | Huesca (HU) | Zaragoza (Z) | 30,228 | Zaragoza (50297) | 1 |
| 35938 | Orcheta | Valencia (V) | Alicante (A) | 1,303 | Orcheta (03098) | 1 |
| 35958 | Oropesa del Mar | Valencia (V) | Castellón (CS) | 8,830 | Oropesa del Mar (12085) | 1 |
| 36128 | Peníscola | Valencia (V) | Castellón (CS) | 8,496 | Peñíscola (12089) | 2 |
| 36213 | Pinoso | Valencia (V) | Alicante (A) | 6,837 | Pinoso (03105) | 2 |
| 36240 | Playa de las Américas | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 3,000 | Arona (38006) | 1 |
| 36410 | Puebla de Alfindén | Huesca (HU) | Zaragoza (Z) | 3,552 | La Puebla de Alfindén (50219) | 1 |
| 36553 | Realejo Alto | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 35,963 | Los Realejos (38031) | 1 |
| 36678 | Rosell | Valencia (V) | Castellón (CS) | 952 | Rosell (12096) | 1 |
| 36701 | Ruesga | León (LE) | Palencia (P) | 1,120 | Cervera de Pisuerga (34056) | 1 |
| 36838 | San Ildefonso | León (LE) | Segovia (SG) | 5,426 | Real Sitio de San Ildefonso (40181) | 1 |
| 36839 | San Isidro | Alicante (A) | Santa Cruz de Tenerife (TF) | 19,541 | Granadilla de Abona (38017) | 1 |
| 36843 | San Juan de Alicante | Valencia (V) | Alicante (A) | 21,939 | San Juan de Alicante (03119) | 1 |
| 36845 | San Juan de Moró | Valencia (V) | Castellón (CS) | 1,947 | San Juan de Moró (12902) | 1 |
| 36925 | San Vicent del Raspeig | Valencia (V) | Alicante (A) | 56,715 | San Vicente del Raspeig (03122) | 1 |
| 36978 | Sant Jordi | Valencia (V) | Castellón (CS) | 637 | San Jorge (12099) | 1 |
| 37180 | Sauzal | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 8,172 | El Sauzal (38041) | 1 |
| 37247 | Sierra-Engarcerán | Valencia (V) | Castellón (CS) | 1,068 | Sierra Engarcerán (12105) | 1 |
| 37368 | Tanque | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 3,068 | Los Silos (38042); name and population are El Tanque (38044) | 2 |
| 37497 | Torre de la Horadada | Valencia (V) | Alicante (A) | 2,676 | Pilar de la Horadada (03902) | 1 |
| 37834 | Vall de Ebo | Valencia (V) | Alicante (A) | 346 | Vall de Ebo (03135) | 1 |
| 37850 | Vallehermosa | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 2,829 | Vallehermoso (38050) | 2 |
| 37952 | Vergel | Valencia (V) | Alicante (A) | 4,409 | Vergel (03138) | 2 |
| 38049 | Villafamés | Valencia (V) | Castellón (CS) | 1,660 | Villafamés (12128) | 1 |
| 38064 | Villafranca del Cid | Valencia (V) | Castellón (CS) | 2,227 | Villafranca del Cid (12129) | 1 |
| 38088 | Villajoyosa | Valencia (V) | Alicante (A) | 33,797 | Villajoyosa (03139) | 1 |
| 38311 | Villasana de Mena | León (LE) | Burgos (BU) | 3,427 | Valle de Mena (09410) | 1 |
| 38358 | Villavieja | Valencia (V) | Castellón (CS) | 3,352 | Villavieja (12136) | 1 |
| 38533 | els Poblets | Valencia (V) | Alicante (A) | 3,708 | Els Poblets (03901) | 1 |
| 38534 | l'Alcora | Valencia (V) | Castellón (CS) | 10,581 | Alcora (12005) | 2 |
| 38535 | l'Alfàs del Pi | Valencia (V) | Alicante (A) | 20,160 | Alfaz del Pi (03011) | 2 |
| 38554 | la Nucia | Valencia (V) | Alicante (A) | 18,783 | La Nucía (03094) | 2 |

### Also found (not changed here)
- **Duplicates.** At least 35 of the moved records (same province, within 1.5 km, similar name) now sit next to a
  near-identical record from a later import (ids 152xxx), for example *Elche* and *Elche/Elx*, or *Orcheta* and *Orxeta*. They wait for the
  duplicate-merge policy in #1643.
- **Wrong `wikiDataId`.** 24 of the 88 records of the first pass carry a Wikidata ID of a place in another province, e.g. *Adzaneta*
  → Q576753 (Aduna, Gipuzkoa), *Villajoyosa* → Q1918587. This is the copy-forward problem of #1641.
- **Province Wikidata IDs.** The eight wrong province IDs above, and similar ones in other countries, are left for a
  separate fix of `states.json`.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/ES.json` — `state_id` and `state_code` on 90 records

## Italian cities filed under the wrong province

### How they were found
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames place with
the same name (or an alternate name) within 3 km and **exactly the record's population** (GeoNames `cities500`).
6,076 Italian records have such an entry. GeoNames' second-level codes were mapped to CSC provinces by majority:
96.5% of those records are filed under the province their entry's code maps to. For 117 of the rest, the entry's
code maps clearly (at least 5 records, at least 80% agreement) to another province.

Each of the 117 was checked on Wikidata: the item with the record's name within 2 km of its point, and its current
**ISTAT municipality code** (P635; for a *frazione*, the code of the comune it is located in). The first three
digits are the province, mapped to CSC's `iso2` by the province's licence-plate code (P395). Codes with an end
date are ignored, because a comune that changes province gets a new code.

| Result | Records |
|---|---:|
| ISTAT province = the GeoNames province, not the filed one | **112** |
| No item with exactly that name; moved after the review found the comune (Cassino d'Alberi, Puia-Villanova, Capanne-Prato-Cinquale) | **3** |
| Held: the place spans two comuni in different provinces (Ponte a Elsa, Campoleone) | 2 |

100 of the first 112 already carry a `wikiDataId`, and in all 100 it is one of the matched items, the place in the new
province; the other 12 have none. Name, point, population and Wikidata ID all describe the same place; only the
province was wrong. Many are *frazioni* of comuni that merged or sit next to a provincial border, e.g. the
Valsamoggia villages (Bazzano, Crespellano, Savigno…) under Modena instead of Bologna, the Aprilia villages under
Rome instead of Latina, Salorno and Proves under Trentino instead of South Tyrol, and Bibione under Udine instead of
Venice.

Four share their name with a comune in the old province, which CSC does not otherwise hold: *Amato* (Catanzaro),
*Casoli* (Chieti), *La Maddalena* (the island comune, in Gallura Nord-Est Sardegna since April 2025, which CSC does
not have; Sassari before) and *Massa* (the provincial capital). These records are the
*frazioni* in Reggio Calabria, Teramo, Capoterra (Cagliari) and Massa e Cozzile (Pistoia), by point, population and
`wikiDataId`. The missing towns are a coverage gap, not part of this fix.

### Fix
**115 cities** move to their province. Only `state_id` and `state_code` change; all keep `Europe/Rome`.

| Move | Records |
|---|---:|
| Reggio Emilia → Modena | 5 |
| Modena → Bologna | 5 |
| Rome → Latina | 5 |
| Treviso → Venice | 4 |
| 69 other province pairs, 1–3 each | 96 |

ISTAT codes below are those of the comune the record belongs to on Wikidata. For comuni merged since, they are the
former codes, with the same province prefix: Polesine Parmense and Zibello (now Polesine Zibello, 034050), Sorbolo
(Sorbolo Mezzani, 034051), Caminata and Nibbiano (Alta Val Tidone, 033049), Borgofranco sul Po and Carbonara di Po
(Borgocarbonara, 020073).

| id | City | Was filed under | Now | Population | ISTAT code |
|---|---|---|---|---:|---|
| 58286 | Panzano in Chianti | Siena (SI) | Florence (FI) | 1,161 | 048021 |
| 58371 | Pecorara | Pavia (PV) | Piacenza (PC) | 141 | 033031, 033049 |
| 58388 | Pegolotte | Padua (PD) | Venice (VE) | 1,346 | 027010 |
| 58458 | Pescia Romana | Grosseto (GR) | Viterbo (VT) | 1,013 | 056035 |
| 58536 | Pianillo | Salerno (SA) | Naples (NA) | 7,253 | 063003 |
| 58537 | Piano | Salerno (SA) | Avellino (AV) | 4,745 | 064061, 064121 |
| 58710 | Pisignano | Forlì-Cesena (FC) | Ravenna (RA) | 1,208 | 039007 |
| 58785 | Polesine Parmense | Cremona (CR) | Parma (PR) | 697 | 034029 |
| 58837 | Ponte Caffaro | Trentino (TN) | Brescia (BS) | 1,478 | 017010 |
| 58900 | Popoli | L'Aquila (AQ) | Pescara (PE) | 5,394 | 068033 |
| 58941 | Porto d'Adda | Bergamo (BG) | Monza and Brianza (MB) | 1,052 | 108053 |
| 59098 | Proves - Proveis | Trentino (TN) | South Tyrol (BZ) | 288 | 021069 |
| 59198 | Puia-Villanova | Treviso (TV) | Pordenone (PN) | 2,167 | 093034 (Prata di Pordenone) |
| 59217 | Quarantoli | Mantua (MN) | Modena (MO) | 1,059 | 036022 |
| 59241 | Quero | Treviso (TV) | Belluno (BL) | 1,807 | 025075 |
| 59274 | Ramiseto | Parma (PR) | Reggio Emilia (RE) | 352 | 035046 |
| 59388 | Rio Salso-Case Bernardi | Rimini (RN) | Pesaro and Urbino (PU) | 1,425 | 041065 |
| 59426 | Rivanazzano | Alessandria (AL) | Pavia (PV) | 4,671 | 018122 |
| 59663 | Rottanova | Rovigo (RO) | Venice (VE) | 1,046 | 027006 |
| 59768 | Salice Terme | Alessandria (AL) | Pavia (PV) | 1,663 | 018073 |
| 59773 | Salionze | Mantua (MN) | Verona (VR) | 1,288 | 023089 |
| 59779 | Salorno | Trentino (TN) | South Tyrol (BZ) | 2,783 | 021076 |
| 59806 | Sambuceto | Pescara (PE) | Chieti (CH) | 9,596 | 069081 |
| 60034 | San Liberale | Treviso (TV) | Venice (VE) | 2,298 | 027020 |
| 60122 | San Michele dei Mucchietti | Reggio Emilia (RE) | Modena (MO) | 1,649 | 036040 |
| 60166 | San Pierino | Pisa (PI) | Florence (FI) | 1,881 | 048019 |
| 60427 | Santa Croce Scuole | Reggio Emilia (RE) | Modena (MO) | 1,066 | 036005 |
| 60591 | Savigno | Modena (MO) | Bologna (BO) | 1,184 | 037061 |
| 60798 | Sesto Imolese | Ravenna (RA) | Bologna (BO) | 1,513 | 037032 |
| 60881 | Sistiana-Visogliano | Gorizia (GO) | Trieste (TS) | 2,996 | 032001 |
| 60951 | Sorbolo | Reggio Emilia (RE) | Parma (PR) | 7,137 | 034037 |
| 61008 | Spigno Saturnia Inferiore | Frosinone (FR) | Latina (LT) | 954 | 059031 |
| 61009 | Spigno Saturnia Superiore | Frosinone (FR) | Latina (LT) | 231 | 059031 |
| 61084 | Strada | Ancona (AN) | Macerata (MC) | 1,547 | 043012 |
| 61234 | Terontola | Perugia (PG) | Arezzo (AR) | 1,608 | 051017 |
| 61252 | Terrossa | Vicenza (VI) | Verona (VR) | 1,179 | 023063 |
| 61263 | Tessera | Treviso (TV) | Venice (VE) | 1,239 | 027042 |
| 61322 | Torchiati | Salerno (SA) | Avellino (AV) | 2,762 | 064121 |
| 61345 | Torrazza dei Mandelli | Monza and Brianza (MB) | Milan (MI) | 1,046 | 015044 |
| 61719 | Valli | Padua (PD) | Venice (VE) | 1,143 | 027008 |
| 61777 | Vas | Treviso (TV) | Belluno (BL) | 487 | 025075 |
| 61910 | Vicarello | Pisa (PI) | Livorno (LI) | 3,106 | 049008 |
| 62259 | Zibello | Cremona (CR) | Parma (PR) | 910 | 034048 |
| 135244 | Abetone | Modena (MO) | Pistoia (PT) | 151 | 047023 |
| 135343 | Alano di Piave | Treviso (TV) | Belluno (BL) | 1,518 | 025002 |
| 135371 | Albiano Magra | La Spezia (SP) | Massa and Carrara (MS) | 1,907 | 045001 |
| 135462 | Amato | Catanzaro (CZ) | Reggio Calabria (RC) | 1,086 | 080071 |
| 135493 | Anduins | Udine (UD) | Pordenone (PN) | 229 | 093049 |
| 135544 | Aquila di Arroscia | Cuneo (CN) | Imperia (IM) | 118 | 008003 |
| 135899 | Bastia | Vicenza (VI) | Padua (PD) | 1,802 | 028071 |
| 135915 | Bazzano | Modena (MO) | Bologna (BO) | 6,131 | 037061 |
| 136042 | Bibione | Udine (UD) | Venice (VE) | 2,564 | 027034 |
| 136071 | Bivio Mortola | Frosinone (FR) | Caserta (CE) | 567 | 061069 |
| 136164 | Borghetto-Melara | La Spezia (SP) | Massa and Carrara (MS) | 1,868 | 045008 |
| 136175 | Borgo Massano | Rimini (RN) | Pesaro and Urbino (PU) | 1,302 | 041030 |
| 136200 | Borgo di Ranzo | Savona (SV) | Imperia (IM) | 219 | 008048 |
| 136204 | Borgofranco sul Po | Rovigo (RO) | Mantua (MN) | 420 | 020006 |
| 136245 | Boscochiaro | Rovigo (RO) | Venice (VE) | 1,321 | 027006 |
| 136381 | Bubano | Ravenna (RA) | Bologna (BO) | 1,450 | 037045 |
| 136499 | Calcara | Modena (MO) | Bologna (BO) | 2,370 | 037061 |
| 136587 | Camilleri-Vallelata | Rome (RM) | Latina (LT) | 1,101 | 059001 |
| 136588 | Caminata | Pavia (PV) | Piacenza (PC) | 212 | 033009 |
| 136622 | Campione | Varese (VA) | Como (CO) | 2,117 | 013040 |
| 136634 | Campo di Carne | Rome (RM) | Latina (LT) | 3,792 | 059001 |
| 136653 | Campofiorenzo-California | Monza and Brianza (MB) | Lecco (LC) | 1,306 | 097016 |
| 136663 | Campolongo Maggiore Liettoli | Padua (PD) | Venice (VE) | 3,578 | 027003 |
| 136760 | Capanne-Prato-Cinquale | Lucca (LU) | Massa and Carrara (MS) | 8,270 | 045011 (Montignoso) |
| 136848 | Carbonara di Po | Rovigo (RO) | Mantua (MN) | 937 | 020009 |
| 136949 | Casa Ponte | Milan (MI) | Pavia (PV) | 193 | 018166 |
| 136963 | Casalazzara | Rome (RM) | Latina (LT) | 1,496 | 059001 |
| 137056 | Casei | Alessandria (AL) | Pavia (PV) | 2,162 | 018033 |
| 137083 | Casoli | Chieti (CH) | Teramo (TE) | 1,085 | 067004 |
| 137090 | Casorzo | Alessandria (AL) | Asti (AT) | 617 | 005020 |
| 137113 | Cassino d'Alberi | Milan (MI) | Lodi (LO) | 1,048 | 098041 (Mulazzano) |
| 137170 | Castel di Judica | Enna (EN) | Catania (CT) | 1,754 | 087013 |
| 137229 | Castelletto | Modena (MO) | Bologna (BO) | 2,125 | 037061 |
| 137339 | Castiglione | La Spezia (SP) | Genoa (GE) | 466 | 010013 |
| 137393 | Catena | Prato (PO) | Pistoia (PT) | 1,542 | 047017 |
| 137608 | Cesarolo | Udine (UD) | Venice (VE) | 1,651 | 027034 |
| 137680 | Chiopris | Gorizia (GO) | Udine (UD) | 385 | 030024 |
| 137816 | Clusane | Bergamo (BG) | Brescia (BS) | 2,196 | 017085 |
| 137832 | Codisotto | Mantua (MN) | Reggio Emilia (RE) | 1,262 | 035026 |
| 137852 | Colico Piano | Como (CO) | Lecco (LC) | 7,204 | 097023 |
| 137854 | Collagna | Parma (PR) | Reggio Emilia (RE) | 399 | 035046 |
| 138144 | Crespellano | Modena (MO) | Bologna (BO) | 4,438 | 037061 |
| 138217 | Cutigliano | Modena (MO) | Pistoia (PT) | 399 | 047004 |
| 138255 | Dese | Treviso (TV) | Venice (VE) | 1,302 | 027042 |
| 138341 | Duino | Gorizia (GO) | Trieste (TS) | 1,369 | 032001 |
| 138450 | Faro Superiore | Reggio Calabria (RC) | Messina (ME) | 2,586 | 083048 |
| 138678 | Fossignano | Rome (RM) | Latina (LT) | 3,718 | 059001 |
| 138680 | Fossoli | Reggio Emilia (RE) | Modena (MO) | 3,578 | 036005 |
| 138897 | Genio Civile | Rome (RM) | Latina (LT) | 4,298 | 059001 |
| 138974 | Gionghi-Cappella | Vicenza (VI) | Trentino (TN) | 483 | 022102 |
| 139157 | Guardavalle Marina | Reggio Calabria (RC) | Catanzaro (CZ) | 2,346 | 079061 |
| 139293 | La Maddalena | Sassari (SS) | Cagliari (CA) | 7,877 | 092011 |
| 139342 | Lambrinia | Lodi (LO) | Pavia (PV) | 1,135 | 018048 |
| 139536 | Lisanza | Novara (NO) | Varese (VA) | 1,068 | 012120 |
| 139560 | Locara | Vicenza (VI) | Verona (VR) | 1,684 | 023069 |
| 139742 | Magreta | Reggio Emilia (RE) | Modena (MO) | 3,344 | 036015 |
| 139756 | Malavicina | Verona (VR) | Mantua (MN) | 1,952 | 020053 |
| 139854 | Marcon-Gaggio-Colmello | Treviso (TV) | Venice (VE) | 12,565 | 027020 |
| 139881 | Marina di Carrara | La Spezia (SP) | Massa and Carrara (MS) | 25,000 | 045003 |
| 139889 | Marina di Massa | Lucca (LU) | Massa and Carrara (MS) | 19,092 | 045010 |
| 139966 | Massa | Massa and Carrara (MS) | Pistoia (PT) | 350 | 047008 |
| 140114 | Mezzano Inferiore | Reggio Emilia (RE) | Parma (PR) | 1,285 | 034051 |
| 140133 | Migliarina | Reggio Emilia (RE) | Modena (MO) | 1,229 | 036005 |
| 140512 | Monterado | Pesaro and Urbino (PU) | Ancona (AN) | 525 | 042050 |
| 140561 | Monticelli Terme | Reggio Emilia (RE) | Parma (PR) | 4,345 | 034023 |
| 140587 | Montoro Superiore | Salerno (SA) | Avellino (AV) | 8,054 | 064062, 064121 |
| 140599 | Moransengo | Turin (TO) | Asti (AT) | 70 | 005122 |
| 140637 | Morsano | Venice (VE) | Pordenone (PN) | 1,478 | 093028 |
| 140700 | Musestre | Venice (VE) | Treviso (TV) | 1,182 | 026069 |
| 140758 | Nibbiano | Pavia (PV) | Piacenza (PC) | 418 | 033029 |
| 140912 | Oltre Brenta | Venice (VE) | Padua (PD) | 1,680 | 028058 |
| 140947 | Orentano | Lucca (LU) | Pisa (PI) | 1,676 | 050009 |

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/IT.json` — `state_id` and `state_code` on 115 records

## Cities with the wrong clock time

### How they were found
1. **Country check.** Every city's timezone is one the IANA zone table (`zone.tab`) lists for its country, allowing
   for backward-compatible alias names — except four: three defensible edge cases (an Antarctic station and
   Tromelin under the French Southern Territories, Nouméa under France) and *Walpole Island*, Ontario, which used
   the US zone `America/Detroit`.
2. **Neighbour check** in countries with several zones: 157 cities whose timezone differs from all ten nearest
   same-country cities, which agree with each other. 95 of them only differ in the zone's *name* (Sydney vs
   Melbourne, Mérida vs Mexico City — same clock time) and are left alone. 48 have a different **UTC offset** in
   January or July. Two of those are in Mato Grosso do Sul, where `America/Campo_Grande` is right and the
   neighbours are across the state line; they are left alone. Crimea (Kyiv vs Simferopol) is a political choice
   and is excluded.
3. **State check.** For every remaining city, the proposed zone is also the majority zone of the other cities in
   its own state (47 of 47).

### Fix
**47 cities** take their state's zone. Only `timezone` changes.

| Country | State | Records | Was | Now | Cities |
|---|---|---:|---|---|---|
| AU | WA | 17 | `Australia/Sydney` | `Australia/Perth` | Albany, Armadale, Bayswater, Capel, Coolgardie, Dardanup, Gosnells, Kalamunda, Kwinana, Malaga, Muchea, Munster, Murray, Serpentine-Jarrahdale, Stoneville, Subiaco, Swan |
| MX | SIN | 8 | `America/Mexico_City` | `America/Mazatlan` | Alfonso G. Calderón Velarde, El Dorado, Elota, Mazatlán, Navolato, Oso Viejo, Sinaloa, Villa Juárez |
| MX | BCN | 3 | `America/Mexico_City` | `America/Tijuana` | Lázaro Cárdenas, Mexicali, Tijuana |
| RU | SVE | 3 | `Europe/Moscow` | `Asia/Yekaterinburg` | Revda, Tugulym, Yekaterinburg |
| CA | AB | 2 | `America/Toronto` | `America/Edmonton` | Fort Saskatchewan, Millet |
| CA | BC | 2 | `America/Toronto` | `America/Vancouver` | Salt Spring Island, White Rock |
| CA | MB | 2 | `America/Toronto` | `America/Winnipeg` | De Salaberry, West St. Paul |
| MX | SON | 2 | `America/Mexico_City` | `America/Hermosillo` | Campo Sesenta, Sinahuiza |
| CA | ON | 1 | `America/Detroit` | `America/Toronto` | Walpole Island |
| ID | NB | 1 | `Asia/Jakarta` | `Asia/Makassar` | Lombok Utara |
| KI | G | 1 | `Pacific/Enderbury` | `Pacific/Tarawa` | Maiana |
| MX | ROO | 1 | `America/Mexico_City` | `America/Cancun` | Othón P. Blanco |
| RU | IRK | 1 | `Europe/Moscow` | `Asia/Irkutsk` | Tulun |
| RU | KEM | 1 | `Europe/Moscow` | `Asia/Novokuznetsk` | Gur’yevsk |
| RU | NVS | 1 | `Europe/Moscow` | `Asia/Novosibirsk` | Iskitimskiy Rayon |
| RU | SAM | 1 | `Europe/Moscow` | `Europe/Samara` | Bogatyr’ |

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/{AU,CA,ID,KI,MX,RU}.json` — `timezone` on 47 records
