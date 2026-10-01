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
