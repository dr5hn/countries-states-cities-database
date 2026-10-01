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
