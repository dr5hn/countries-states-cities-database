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

## Country fields out of date

An audit of `countries.json` against Wikidata and the IANA time zone database (tzdata 2026c) found values that are wrong
today. Only those fields change.

### Currency, domain and capital
| Country | Field | Was | Now | Why |
|---|---|---|---|---|
| Congo (CG) | currency, name, symbol | CDF, Congolese Franc, FC | XAF, Central African CFA franc, FCFA | CDF is the DR Congo's franc; the Republic of the Congo uses the CFA franc, as Cameroon and the CAR do in this file |
| Curaçao (CW) | currency, name, symbol | ANG, Netherlands Antillean guilder, ƒ | XCG, Caribbean guilder, Cg | The Caribbean guilder replaced the ANG on 31 March 2025 |
| Sint Maarten (SX) | currency, name, symbol | as Curaçao | as Curaçao | Same currency union |
| Bonaire, Sint Eustatius and Saba (BQ) | tld | .an | .bq | .an (Netherlands Antilles) was retired in 2015; .bq is the ISO-based ccTLD (registered but not in the root zone, like .bl and .mf already in this file; residents use .nl) |
| Burundi (BI) | capital | Bujumbura | Gitega | Gitega has been the political capital since 2019 (Bujumbura remains the economic capital) |

### Time zone offsets
The file stores each zone's **standard** (non-daylight) offset: New York is EST (−5), Berlin CET (+1). Two groups
break that:

- **Offsets changed by law since the data was generated:** Kazakhstan moved to UTC+5 (March 2024); Chihuahua and
  Ojinaga to UTC−6 (2022); Jordan and Syria to permanent UTC+3 (2022); Volgograd to UTC+3 (2020); Samoa dropped
  daylight saving (2021); South Sudan to UTC+2 (2021); Nuuk and Scoresbysund to UTC−2 (2023–24); Norfolk Island's
  standard time is UTC+11 (2015); Vostok is UTC+5 and Casey UTC+8.
- **Southern-hemisphere zones stored their summer offset:** Australia (Sydney, Melbourne, Hobart, Adelaide, Broken
  Hill, Lord Howe, Currie, Macquarie), New Zealand (Auckland, Chatham, McMurdo) and Chile (Santiago, Easter Island).

Each new value is checked against tzdata 2026c: it is the zone's smaller 2026 offset (its standard time). The
abbreviation and name follow (e.g. AEDT → AEST); Kazakhstan's garbled "Alma-Ata Time[1" becomes "Kazakhstan Time".

| Country | Zone | gmtOffset was | Now |
|---|---|---:|---:|
| AQ | Antarctica/Casey | 39600 | 28800 |
| AQ | Antarctica/McMurdo | 46800 | 43200 |
| AQ | Antarctica/Vostok | 21600 | 18000 |
| AU | Antarctica/Macquarie | 39600 | 36000 |
| AU | Australia/Adelaide | 37800 | 34200 |
| AU | Australia/Broken_Hill | 37800 | 34200 |
| AU | Australia/Currie | 39600 | 36000 |
| AU | Australia/Hobart | 39600 | 36000 |
| AU | Australia/Lord_Howe | 39600 | 37800 |
| AU | Australia/Melbourne | 39600 | 36000 |
| AU | Australia/Sydney | 39600 | 36000 |
| CL | America/Santiago | −10800 | −14400 |
| CL | Pacific/Easter | −18000 | −21600 |
| GL | America/Nuuk | −10800 | −7200 |
| GL | America/Scoresbysund | −3600 | −7200 |
| JO | Asia/Amman | 7200 | 10800 |
| KZ | Asia/Almaty | 21600 | 18000 |
| KZ | Asia/Qostanay | 21600 | 18000 |
| MX | America/Chihuahua | −25200 | −21600 |
| MX | America/Ojinaga | −25200 | −21600 |
| NZ | Pacific/Auckland | 46800 | 43200 |
| NZ | Pacific/Chatham | 49500 | 45900 |
| NF | Pacific/Norfolk | 43200 | 39600 |
| RU | Europe/Volgograd | 14400 | 10800 |
| WS | Pacific/Apia | 50400 | 46800 |
| SS | Africa/Juba | 10800 | 7200 |
| SY | Asia/Damascus | 7200 | 10800 |

### After the independent review
The review confirmed all 32 values above and pointed to 2026 changes that the first pass missed, because it tested
2026 offsets while these take effect late in 2026. Each is checked against tzdata 2026c's 2027 offsets:

| Country | Zone | gmtOffset was | Now | Change |
|---|---|---:|---:|---|
| MA, EH | Africa/Casablanca, Africa/El_Aaiun (3 entries) | 3600 | 0 | Permanent UTC+0 from 20 September 2026 |
| CA | America/Vancouver | −28800 | −25200 | British Columbia on permanent UTC−7 |
| CA | America/Edmonton | −25200 | −21600 | Alberta on permanent UTC−6 |
| CA | America/Yellowknife | −25200 | −21600 | Follows Edmonton in tzdata |

Labels only: Amman and Damascus take "AST / Arabia Standard Time" (as Riyadh in this file) instead of "+03";
Atyrau's "MSD+1 / Moscow Daylight Time+1" and Qyzylorda's "Qyzylorda Summer Time" become "KZT / Kazakhstan Time";
Anadyr's garbled "Anadyr Time[4" is repaired; Khartoum (UTC+2 since 2017) is CAT, not EAT.

Not changed yet: tzdata 2026d and 2026e (newer than the data used here) also move the Northwest Territories to
UTC−6 (Inuvik) and Manitoba to permanent UTC−5 (Winnipeg, Rainy River); to be applied with a newer tzdata.

### Also found (not changed here)
- **Debatable:** Palau's capital (Wikidata: Ngerulmud, the seat of government in Melekeok state), Equatorial
  Guinea's (Wikidata: Ciudad de la Paz), Kosovo's iso3 (XKX, used by the EU and others; Wikidata: XKS).
- **Postal codes:** 21 countries' `postal_code_format` and `postal_code_regex` disagree (e.g. Greece's format
  `### ##` vs a regex for five digits with no space; Honduras `#####` vs six digits). Each needs checking against the
  national postal service.
- **Zone ownership:** a few countries list another country's zone: Sint Maarten America/Anguilla and Bouvet Island
  Europe/Oslo are tzdata links to zones of other countries; Kosovo uses Europe/Belgrade, the zone for its time.
  Left as they are.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/countries/countries.json` — timezone offsets on 33 entries (with their labels) and labels only on 4 (Atyrau, Qyzylorda, Anadyr, Khartoum); currency on 3 countries; tld on 1; capital on 1

## Batches of cities filed under one wrong state

**453 cities** from three bulk additions move to the state they are in: Lisbon-area parishes filed under Guarda
(Portugal, ids 143xxx), villages of Zhytomyr Oblast and three others filed under Poltava (Ukraine, 149xxx) and villages of Nagano filed
under Kōchi (Japan, 148xxx). Each batch put all its records under one state; some belong there, many do not.

### How they were found
A check of CSC's own neighbours misses these, because a misfiled record's neighbours are misfiled too. So each
record was compared with the nearest places in the full GeoNames dump of its country. GeoNames' region codes were
mapped to CSC states by majority vote of the 2019 import's records whose population matches a GeoNames entry exactly.
A record is a candidate when all five nearest mapped places (within 10 km, the nearest within 3 km) lie in one other
state: PT 224, UA 147, JP 77.

### How they were verified
Every record in these batches carries a `wikiDataId`. It counts only if it is the record's place: a label equal to
the record's name, and a point within 5 km. Its "located in" (P131) chain then gives the state.

| Result | PT | UA | JP |
|---|---:|---:|---:|
| GeoNames candidate, Wikidata agrees: **moved** | **202** | **142** | **65** |
| Rest of the batch: Wikidata names another state and a same-named or nearby GeoNames place agrees: **moved** | **10** | **15** | **8** |
| GeoNames candidate, but Wikidata says the filed state is right (border areas): kept | 17 | 0 | 6 |
| GeoNames candidate, but the Wikidata ID fails the identity test or its chain gives no single state: held | 5 | 5 | 6 |
| Rest of the batch: Wikidata confirms the filed state | 267 | 69 | 32 |
| Rest of the batch: no usable Wikidata ID or chain, or the sources disagree: kept | 6 | 4 | 0 |

The GeoNames candidates include a few records outside the batches (UA 2, JP 9); one of them moves (Ukraine, 109xxx).

### Added after the independent review
The review checked every moved point against OpenStreetMap region outlines (442 of 442 inside the new state) and found
13 records left in the batches that are still misfiled. GeoNames' nearest places pointed to the right state for most;
they had been held because the Wikidata label differs in form ("Azambuja (town)" vs "Azambuja") or its "located in"
chain did not resolve. 11 move now; two also get their Wikidata item's point, whose population equals the record's:

| Country | id | City | Was | Now | Note |
|---|---|---|---|---|---|
| PT | 143293 | Azambuja (town) | Guarda | Lisbon | |
| PT | 143347 | Castelo (Lisbon) | Guarda | Lisbon | |
| PT | 143604 | Santa Catarina | Guarda | Lisbon | |
| PT | 143609 | Santa Iria da Azóia | Guarda | Lisbon | |
| PT | 143318 | Cadaval | Guarda | Lisbon | point was in Barrancos (Beja), 218 km away; now Q33661928's (39.24621, -9.06738) |
| UA | 149427 | Korosten | Poltavska | Zhytomyrska | |
| UA | 149492 | Ruzhyn (settlement) | Poltavska | Zhytomyrska | |
| UA | 149503 | Taraschanka | Poltavska | Zhytomyrska | |
| UA | 149441 | Lisogirka | Poltavska | Vinnytska | OpenStreetMap and Wikidata agree |
| JP | 148244 | Togari | Kōchi | Nagano | |
| JP | 148247 | Mitsushima | Kōchi | Nagano | |
| JP | 148215 | Motoyama | Kōchi | (stays) | point was in Nagoya; now Q735494's (33.75969, 133.58669) in Kōchi |

Still held: *Nyvky* (149465), whose point is in Zhytomyr Oblast but whose Wikidata item is a Kyiv neighbourhood.
Duplicates among these (Korosten 109801, Ruzhyn 110394, Santa Iria da Azóia 143610 and 89504, Azambuja 89009) wait
for the duplicate policy.

*Ōshika* (148260) has only one GeoNames place within 10 km; it agrees with Wikidata (Nagano). *Lisogirka* (149441) was held
(Wikidata says Vinnytsia, GeoNames Zhytomyr) and moved after the review.

### Fix
Only `state_id` and `state_code` change (plus two points, above); every record's `timezone` already fits its new state.

| Country | Move | Records |
|---|---|---:|
| PT | Guarda → Lisbon | 216 |
| UA | Poltavska → Zhytomyrska | 157 |
| UA | Poltavska → Vinnytska | 1 |
| JP | Kōchi → Nagano | 75 |
| UA | Kirovohradska → Dnipropetrovska | 1 |
| UA | Poltavska → Ternopilska | 1 |
| UA | Poltavska → Dnipropetrovska | 1 |
| PT | Guarda → Castelo Branco | 1 |

| Country | id | City | Was filed under | Now | Own Wikidata ID (distance) | Sources |
|---|---|---|---|---|---|---|
| JP | 148212 | Tōmi | Kōchi | Nagano | Q840859 (0.0 km) | GeoNames + Wikidata |
| JP | 148214 | Agematsu | Kōchi | Nagano | Q374859 (0.2 km) | GeoNames + Wikidata |
| JP | 148216 | Sakaki | Kōchi | Nagano | Q1348962 (0.0 km) | GeoNames + Wikidata |
| JP | 148217 | Kiso | Kōchi | Nagano | Q1743742 (0.0 km) | GeoNames + Wikidata |
| JP | 148219 | Yamagata | Kōchi | Nagano | Q1348998 (0.0 km) | GeoNames + Wikidata |
| JP | 148220 | Urugi | Kōchi | Nagano | Q1203126 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148222 | Takamori | Kōchi | Nagano | Q1203136 (0.0 km) | GeoNames + Wikidata |
| JP | 148224 | Nakagawa | Kōchi | Nagano | Q1194229 (0.0 km) | GeoNames + Wikidata |
| JP | 148225 | Fujimi | Kōchi | Nagano | Q1204145 (0.0 km) | GeoNames + Wikidata |
| JP | 148226 | Takagi | Kōchi | Nagano | Q1203939 (0.0 km) | GeoNames + Wikidata |
| JP | 148228 | Minamimaki | Kōchi | Nagano | Q1203240 (0.0 km) | GeoNames + Wikidata |
| JP | 148229 | Yasuoka | Kōchi | Nagano | Q902559 (0.0 km) | GeoNames + Wikidata |
| JP | 148233 | Obuse | Kōchi | Nagano | Q1348977 (0.0 km) | GeoNames + Wikidata |
| JP | 148234 | Yamanouchi | Kōchi | Nagano | Q1204468 (0.0 km) | GeoNames + Wikidata |
| JP | 148235 | Minamiminowa | Kōchi | Nagano | Q1347404 (0.0 km) | GeoNames + Wikidata |
| JP | 148236 | Iijima | Kōchi | Nagano | Q522462 (0.1 km) | GeoNames + Wikidata |
| JP | 148237 | Karuizawa | Kōchi | Nagano | Q1012064 (0.0 km) | GeoNames + Wikidata |
| JP | 148238 | Nagawa | Kōchi | Nagano | Q1346846 (1.8 km) | GeoNames + Wikidata |
| JP | 148239 | Sakuho | Kōchi | Nagano | Q1203700 (0.0 km) | GeoNames + Wikidata |
| JP | 148240 | Nozawaonsen | Kōchi | Nagano | Q1354760 (0.0 km) | GeoNames + Wikidata |
| JP | 148241 | Omi | Kōchi | Nagano | Q1349060 (0.0 km) | GeoNames + Wikidata |
| JP | 148242 | Otari | Kōchi | Nagano | Q1204497 (0.0 km) | GeoNames + Wikidata |
| JP | 148243 | Nakajō | Kōchi | Nagano | Q854747 (0.0 km) | GeoNames + Wikidata |
| JP | 148246 | Ueda | Kōchi | Nagano | Q844852 (0.0 km) | GeoNames + Wikidata |
| JP | 148249 | Nakano | Kōchi | Nagano | Q838652 (0.0 km) | GeoNames + Wikidata |
| JP | 148250 | Ōtaki | Kōchi | Nagano | Q1204275 (0.0 km) | GeoNames + Wikidata |
| JP | 148251 | Ōkuwa | Kōchi | Nagano | Q1204461 (0.9 km) | GeoNames + Wikidata |
| JP | 148252 | Matsukawa | Kōchi | Nagano | Q222825 (0.0 km) | GeoNames + Wikidata |
| JP | 148253 | Yawata | Kōchi | Nagano | Q104658420 (0.0 km) | GeoNames + Wikidata |
| JP | 148254 | Minowa | Kōchi | Nagano | Q1346975 (0.0 km) | GeoNames + Wikidata |
| JP | 148256 | Minamiaiki | Kōchi | Nagano | Q763885 (0.0 km) | GeoNames + Wikidata |
| JP | 148259 | Aoki | Kōchi | Nagano | Q615719 (0.0 km) | GeoNames + Wikidata |
| JP | 148260 | Ōshika | Kōchi | Nagano | Q1203751 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148261 | Asahi | Kōchi | Nagano | Q720461 (0.6 km) | GeoNames + Wikidata |
| JP | 148263 | Nagiso | Kōchi | Nagano | Q1310803 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148264 | Kijimadaira | Kōchi | Nagano | Q1204471 (0.1 km) | GeoNames + Wikidata |
| JP | 148265 | Miyada | Kōchi | Nagano | Q959501 (0.0 km) | GeoNames + Wikidata |
| JP | 148267 | Ikusaka | Kōchi | Nagano | Q1347517 (0.0 km) | GeoNames + Wikidata |
| JP | 148268 | Toyooka | Kōchi | Nagano | Q44545 (0.0 km) | GeoNames + Wikidata |
| JP | 148269 | Hakuba | Kōchi | Nagano | Q1011157 (0.5 km) | GeoNames + Wikidata |
| JP | 148272 | Shimosuwa | Kōchi | Nagano | Q1204211 (0.0 km) | GeoNames + Wikidata |
| JP | 148274 | Hara | Kōchi | Nagano | Q1203041 (0.0 km) | GeoNames + Wikidata |
| JP | 148275 | Sakae | Kōchi | Nagano | Q1204286 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148277 | Shimojō | Kōchi | Nagano | Q1203050 (0.0 km) | GeoNames + Wikidata |
| JP | 148278 | Shinano | Kōchi | Nagano | Q1349050 (0.0 km) | GeoNames + Wikidata |
| JP | 148279 | Anan | Kōchi | Nagano | Q1203314 (0.0 km) | GeoNames + Wikidata |
| JP | 148281 | Kitaaiki | Kōchi | Nagano | Q1202620 (0.0 km) | GeoNames + Wikidata |
| JP | 148283 | Takayama | Kōchi | Nagano | Q1349115 (0.0 km) | GeoNames + Wikidata |
| JP | 148284 | Ikeda | Kōchi | Nagano | Q1204048 (0.0 km) | GeoNames + Wikidata |
| JP | 148285 | Tateshina | Kōchi | Nagano | Q1346895 (0.0 km) | GeoNames + Wikidata |
| JP | 148286 | Hiraya | Kōchi | Nagano | Q1346768 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148287 | Achi | Kōchi | Nagano | Q1203279 (0.0 km) | GeoNames + Wikidata |
| JP | 148288 | Kawakami | Kōchi | Nagano | Q588091 (0.0 km) | GeoNames + Wikidata |
| JP | 148290 | Iizuna | Kōchi | Nagano | Q772034 (0.0 km) | GeoNames + Wikidata |
| JP | 148291 | Miyota | Kōchi | Nagano | Q1204123 (0.2 km) | GeoNames + Wikidata |
| JP | 148292 | Matsumoto | Kōchi | Nagano | Q213324 (0.0 km) | GeoNames + Wikidata |
| JP | 148293 | Chikuhoku | Kōchi | Nagano | Q1072656 (3.3 km) | GeoNames + Wikidata |
| JP | 148294 | Sanada | Kōchi | Nagano | Q7415455 (0.0 km) | GeoNames + Wikidata |
| JP | 148295 | Tatsuno | Kōchi | Nagano | Q1347504 (0.0 km) | GeoNames + Wikidata |
| JP | 148297 | Neba | Kōchi | Nagano | Q1204111 (0.2 km) | Wikidata + GeoNames (nearby) |
| JP | 148299 | Azumino | Kōchi | Nagano | Q534667 (0.0 km) | GeoNames + Wikidata |
| JP | 148301 | Shiojiri | Kōchi | Nagano | Q857272 (0.4 km) | GeoNames + Wikidata |
| JP | 148303 | Ogawa | Kōchi | Nagano | Q1348971 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148304 | Chino | Kōchi | Nagano | Q838660 (0.0 km) | GeoNames + Wikidata |
| JP | 148306 | Komoro | Kōchi | Nagano | Q838657 (0.0 km) | GeoNames + Wikidata |
| JP | 148307 | Okaya | Kōchi | Nagano | Q838672 (0.0 km) | GeoNames + Wikidata |
| JP | 148309 | Suwa | Kōchi | Nagano | Q846338 (0.0 km) | GeoNames + Wikidata |
| JP | 148310 | Nagano | Kōchi | Nagano | Q128849 (0.2 km) | GeoNames + Wikidata |
| JP | 148312 | Iiyama | Kōchi | Nagano | Q851097 (0.0 km) | GeoNames + Wikidata |
| JP | 148313 | Ina | Kōchi | Nagano | Q840888 (0.0 km) | Wikidata + GeoNames (nearby) |
| JP | 148315 | Iida | Kōchi | Nagano | Q841129 (0.0 km) | GeoNames + Wikidata |
| JP | 148316 | Saku | Kōchi | Nagano | Q495821 (0.0 km) | GeoNames + Wikidata |
| JP | 148321 | Ōmachi | Kōchi | Nagano | Q385375 (0.3 km) | GeoNames + Wikidata |
| PT | 143239 | Agualva | Guarda | Lisbon | Q397872 (0.6 km) | GeoNames + Wikidata |
| PT | 143241 | Ajuda | Guarda | Lisbon | Q413311 (0.0 km) | GeoNames + Wikidata |
| PT | 143243 | Alcabideche | Guarda | Lisbon | Q31877422 (0.0 km) | GeoNames + Wikidata |
| PT | 143244 | Alcains | Guarda | Castelo Branco | Q1024258 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143245 | Alcoentre | Guarda | Lisbon | Q31877572 (0.0 km) | GeoNames + Wikidata |
| PT | 143246 | Alcântara | Guarda | Lisbon | Q1017927 (0.0 km) | GeoNames + Wikidata |
| PT | 143247 | Aldeia Galega da Merceana | Guarda | Lisbon | Q2119101 (0.0 km) | GeoNames + Wikidata |
| PT | 143248 | Aldeia Gavinha | Guarda | Lisbon | Q2119745 (0.0 km) | GeoNames + Wikidata |
| PT | 143257 | Alenquer | Guarda | Lisbon | Q988830 (0.0 km) | GeoNames + Wikidata |
| PT | 143259 | Alfornelos | Guarda | Lisbon | Q1021359 (0.0 km) | GeoNames + Wikidata |
| PT | 143262 | Alguber | Guarda | Lisbon | Q2119125 (0.0 km) | GeoNames + Wikidata |
| PT | 143264 | Algueirão–Mem Martins | Guarda | Lisbon | Q180972 (0.0 km) | GeoNames + Wikidata |
| PT | 143265 | Algés | Guarda | Lisbon | Q1975409 (0.0 km) | GeoNames + Wikidata |
| PT | 143267 | Almargem | Guarda | Lisbon | Q31879382 (0.0 km) | GeoNames + Wikidata |
| PT | 143268 | Almargem do Bispo | Guarda | Lisbon | Q2119224 (0.0 km) | GeoNames + Wikidata |
| PT | 143272 | Alto do Pina | Guarda | Lisbon | Q443627 (0.0 km) | GeoNames + Wikidata |
| PT | 143273 | Alvalade | Guarda | Lisbon | Q448231 (0.0 km) | GeoNames + Wikidata |
| PT | 143276 | Alverca do Ribatejo | Guarda | Lisbon | Q431690 (0.0 km) | GeoNames + Wikidata |
| PT | 143278 | Amadora | Guarda | Lisbon | Q189166 (0.0 km) | GeoNames + Wikidata |
| PT | 143279 | Ameixoeira | Guarda | Lisbon | Q461261 (0.0 km) | GeoNames + Wikidata |
| PT | 143281 | Anjos | Guarda | Lisbon | Q551464 (0.0 km) | GeoNames + Wikidata |
| PT | 143282 | Apelação | Guarda | Lisbon | Q618141 (0.0 km) | GeoNames + Wikidata |
| PT | 143284 | Arranhó | Guarda | Lisbon | Q699206 (0.0 km) | GeoNames + Wikidata |
| PT | 143288 | Aveiras de Baixo | Guarda | Lisbon | Q790339 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143289 | Aveiras de Cima | Guarda | Lisbon | Q790340 (0.0 km) | GeoNames + Wikidata |
| PT | 143292 | Azambuja | Guarda | Lisbon | Q634164 (0.0 km) | GeoNames + Wikidata |
| PT | 143294 | Azenhas do Mar | Guarda | Lisbon | Q1648341 (0.2 km) | GeoNames + Wikidata |
| PT | 143296 | Azueira | Guarda | Lisbon | Q31894809 (0.0 km) | GeoNames + Wikidata |
| PT | 143299 | Barcarena | Guarda | Lisbon | Q31910854 (0.0 km) | GeoNames + Wikidata |
| PT | 143301 | Beato | Guarda | Lisbon | Q686717 (0.0 km) | GeoNames + Wikidata |
| PT | 143302 | Belas | Guarda | Lisbon | Q815283 (0.0 km) | GeoNames + Wikidata |
| PT | 143305 | Benfica | Guarda | Lisbon | Q534230 (0.0 km) | GeoNames + Wikidata |
| PT | 143307 | Bobadela | Guarda | Lisbon | Q888361 (0.0 km) | GeoNames + Wikidata |
| PT | 143309 | Brandoa | Guarda | Lisbon | Q266202 (0.0 km) | GeoNames + Wikidata |
| PT | 143310 | Bucelas | Guarda | Lisbon | Q997658 (0.0 km) | GeoNames + Wikidata |
| PT | 143311 | Buraca | Guarda | Lisbon | Q1010176 (0.0 km) | GeoNames + Wikidata |
| PT | 143312 | Cabanas de Torres | Guarda | Lisbon | Q1024717 (0.0 km) | GeoNames + Wikidata |
| PT | 143314 | Cacem | Guarda | Lisbon | Q1025066 (0.0 km) | GeoNames + Wikidata |
| PT | 143315 | Cachoeiras | Guarda | Lisbon | Q1025044 (0.0 km) | GeoNames + Wikidata |
| PT | 143316 | Cadafais | Guarda | Lisbon | Q687504 (0.0 km) | GeoNames + Wikidata |
| PT | 143319 | Calhandriz | Guarda | Lisbon | Q748055 (0.0 km) | GeoNames + Wikidata |
| PT | 143321 | Campelos | Guarda | Lisbon | Q582153 (0.0 km) | GeoNames + Wikidata |
| PT | 143322 | Campo Grande | Guarda | Lisbon | Q963573 (0.0 km) | GeoNames + Wikidata |
| PT | 143323 | Campolide | Guarda | Lisbon | Q1031527 (0.0 km) | GeoNames + Wikidata |
| PT | 143324 | Caneças | Guarda | Lisbon | Q1026716 (0.0 km) | GeoNames + Wikidata |
| PT | 143326 | Carcavelos | Guarda | Lisbon | Q663893 (0.6 km) | GeoNames + Wikidata |
| PT | 143327 | Cardosas | Guarda | Lisbon | Q430228 (0.0 km) | GeoNames + Wikidata |
| PT | 143328 | Carmões | Guarda | Lisbon | Q119690 (0.0 km) | GeoNames + Wikidata |
| PT | 143329 | Carnaxide | Guarda | Lisbon | Q1013271 (0.0 km) | GeoNames + Wikidata |
| PT | 143331 | Carnide | Guarda | Lisbon | Q1044020 (0.0 km) | GeoNames + Wikidata |
| PT | 143332 | Carnota | Guarda | Lisbon | Q224591 (0.0 km) | GeoNames + Wikidata |
| PT | 143335 | Carregado | Guarda | Lisbon | Q1044914 (0.0 km) | GeoNames + Wikidata |
| PT | 143337 | Carvoeira | Guarda | Lisbon | Q388896 (0.0 km) | GeoNames + Wikidata |
| PT | 143339 | Casal de Cambra | Guarda | Lisbon | Q1046749 (0.3 km) | GeoNames + Wikidata |
| PT | 143344 | Castanheira do Ribatejo | Guarda | Lisbon | Q1048511 (0.9 km) | GeoNames + Wikidata |
| PT | 143353 | Caxias | Guarda | Lisbon | Q33210 (0.0 km) | GeoNames + Wikidata |
| PT | 143356 | Cercal | Guarda | Lisbon | Q377823 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143359 | Charneca | Guarda | Lisbon | Q1067627 (0.0 km) | GeoNames + Wikidata |
| PT | 143360 | Cheleiros | Guarda | Lisbon | Q770211 (0.0 km) | GeoNames + Wikidata |
| PT | 143364 | Colares | Guarda | Lisbon | Q1107623 (1.4 km) | GeoNames + Wikidata |
| PT | 143365 | Coração de Jesus | Guarda | Lisbon | Q1026670 (0.0 km) | GeoNames + Wikidata |
| PT | 143372 | Cruz Quebrada - Dafundo | Guarda | Lisbon | Q1021364 (0.0 km) | GeoNames + Wikidata |
| PT | 143375 | Damaia | Guarda | Lisbon | Q377919 (0.0 km) | GeoNames + Wikidata |
| PT | 143376 | Dois Portos | Guarda | Lisbon | Q1234975 (0.0 km) | GeoNames + Wikidata |
| PT | 143379 | Encarnação | Guarda | Lisbon | Q1024864 (0.0 km) | GeoNames + Wikidata |
| PT | 143380 | Enxara do Bispo | Guarda | Lisbon | Q637142 (0.0 km) | GeoNames + Wikidata |
| PT | 143381 | Ericeira | Guarda | Lisbon | Q1351868 (0.0 km) | GeoNames + Wikidata |
| PT | 143387 | Falagueira | Guarda | Lisbon | Q1024775 (0.0 km) | GeoNames + Wikidata |
| PT | 143389 | Famões | Guarda | Lisbon | Q375205 (0.0 km) | GeoNames + Wikidata |
| PT | 143390 | Fanhões | Guarda | Lisbon | Q1395657 (0.0 km) | GeoNames + Wikidata |
| PT | 143393 | Figueira do Guincho | Guarda | Lisbon | Q49350155 (0.0 km) | GeoNames + Wikidata |
| PT | 143394 | Figueiros | Guarda | Lisbon | Q915093 (0.0 km) | GeoNames + Wikidata |
| PT | 143400 | Fontanelas | Guarda | Lisbon | Q5465145 (0.5 km) | GeoNames + Wikidata |
| PT | 143405 | Forte da Casa | Guarda | Lisbon | Q1438943 (0.0 km) | GeoNames + Wikidata |
| PT | 143408 | Freiria | Guarda | Lisbon | Q1454635 (0.0 km) | GeoNames + Wikidata |
| PT | 143413 | Frielas | Guarda | Lisbon | Q1024850 (0.0 km) | GeoNames + Wikidata |
| PT | 143420 | Gradil | Guarda | Lisbon | Q1024960 (0.0 km) | GeoNames + Wikidata |
| PT | 143423 | Graça | Guarda | Lisbon | Q1520260 (0.0 km) | GeoNames + Wikidata |
| PT | 143427 | Igreja Nova | Guarda | Lisbon | Q1024983 (0.0 km) | GeoNames + Wikidata |
| PT | 143438 | Lamas | Guarda | Lisbon | Q1024811 (0.0 km) | GeoNames + Wikidata |
| PT | 143441 | Lapa | Guarda | Lisbon | Q1631359 (0.0 km) | GeoNames + Wikidata |
| PT | 143449 | Loures | Guarda | Lisbon | Q917535 (0.0 km) | GeoNames + Wikidata |
| PT | 143450 | Lourinhã | Guarda | Lisbon | Q986017 (0.0 km) | GeoNames + Wikidata |
| PT | 143451 | Lousa | Guarda | Lisbon | Q595642 (0.5 km) | GeoNames + Wikidata |
| PT | 143452 | Lumiar | Guarda | Lisbon | Q924723 (0.0 km) | GeoNames + Wikidata |
| PT | 143454 | Madalena | Guarda | Lisbon | Q387982 (0.0 km) | GeoNames + Wikidata |
| PT | 143455 | Mafra | Guarda | Lisbon | Q986419 (0.0 km) | GeoNames + Wikidata |
| PT | 143459 | Malveira | Guarda | Lisbon | Q604302 (0.0 km) | GeoNames + Wikidata |
| PT | 143462 | Manique do Intendente | Guarda | Lisbon | Q1575170 (0.0 km) | GeoNames + Wikidata |
| PT | 143467 | Marteleira | Guarda | Lisbon | Q1902992 (0.0 km) | GeoNames + Wikidata |
| PT | 143468 | Marvila | Guarda | Lisbon | Q1786435 (0.0 km) | GeoNames + Wikidata |
| PT | 143469 | Massamá | Guarda | Lisbon | Q1907450 (0.3 km) | GeoNames + Wikidata |
| PT | 143471 | Matacães | Guarda | Lisbon | Q1908045 (0.0 km) | GeoNames + Wikidata |
| PT | 143473 | Maxial | Guarda | Lisbon | Q1759782 (0.9 km) | GeoNames + Wikidata |
| PT | 143476 | Maçussa | Guarda | Lisbon | Q1894283 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143477 | Meca | Guarda | Lisbon | Q1452082 (0.0 km) | GeoNames + Wikidata |
| PT | 143481 | Mercês | Guarda | Lisbon | Q182737 (0.0 km) | GeoNames + Wikidata |
| PT | 143483 | Milharado | Guarda | Lisbon | Q35729849 (0.0 km) | GeoNames + Wikidata |
| PT | 143484 | Mina | Guarda | Lisbon | Q1894295 (0.0 km) | GeoNames + Wikidata |
| PT | 143486 | Mira-Sintra | Guarda | Lisbon | Q1270529 (0.0 km) | GeoNames + Wikidata |
| PT | 143487 | Miragaia | Guarda | Lisbon | Q959668 (0.0 km) | GeoNames + Wikidata |
| PT | 143494 | Moledo | Guarda | Lisbon | Q1024954 (0.0 km) | GeoNames + Wikidata |
| PT | 143495 | Monte Abraão | Guarda | Lisbon | Q1945710 (0.3 km) | GeoNames + Wikidata |
| PT | 143497 | Monte Redondo | Guarda | Lisbon | Q1755149 (0.0 km) | GeoNames + Wikidata |
| PT | 143498 | Montelavar | Guarda | Lisbon | Q1946059 (0.1 km) | GeoNames + Wikidata |
| PT | 143503 | Mártires | Guarda | Lisbon | Q432607 (0.0 km) | GeoNames + Wikidata |
| PT | 143510 | Nossa Senhora de Fátima | Guarda | Lisbon | Q1752948 (0.0 km) | GeoNames + Wikidata |
| PT | 143512 | Odivelas | Guarda | Lisbon | Q850837 (0.0 km) | GeoNames + Wikidata |
| PT | 143513 | Odivelas Municipality | Guarda | Lisbon | Q3348715 (0.7 km) | GeoNames + Wikidata |
| PT | 143514 | Oeiras | Guarda | Lisbon | Q926700 (0.0 km) | GeoNames + Wikidata |
| PT | 143515 | Oeiras e São Julião da Barra | Guarda | Lisbon | Q1863492 (0.0 km) | GeoNames + Wikidata |
| PT | 143516 | Olhalvo | Guarda | Lisbon | Q2019798 (0.0 km) | GeoNames + Wikidata |
| PT | 143517 | Olival de Basto | Guarda | Lisbon | Q1024249 (0.0 km) | GeoNames + Wikidata |
| PT | 143518 | Olival do Basto | Guarda | Lisbon | Q49358934 (0.0 km) | GeoNames + Wikidata |
| PT | 143519 | Ota | Guarda | Lisbon | Q951481 (0.0 km) | GeoNames + Wikidata |
| PT | 143520 | Outeiro da Cabeça | Guarda | Lisbon | Q2041940 (0.0 km) | GeoNames + Wikidata |
| PT | 143522 | Painho | Guarda | Lisbon | Q1024948 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143528 | Parede | Guarda | Lisbon | Q2052148 (0.0 km) | GeoNames + Wikidata |
| PT | 143529 | Paço de Arcos | Guarda | Lisbon | Q2065632 (0.0 km) | GeoNames + Wikidata |
| PT | 143532 | Pena | Guarda | Lisbon | Q1233617 (0.0 km) | GeoNames + Wikidata |
| PT | 143535 | Penha de França | Guarda | Lisbon | Q1786389 (0.0 km) | GeoNames + Wikidata |
| PT | 143537 | Peral | Guarda | Lisbon | Q2070111 (0.0 km) | GeoNames + Wikidata |
| PT | 143539 | Pereiro de Palhacana | Guarda | Lisbon | Q1757340 (0.0 km) | GeoNames + Wikidata |
| PT | 143540 | Pero Pinheiro | Guarda | Lisbon | Q246559 (1.8 km) | GeoNames + Wikidata |
| PT | 143546 | Ponte do Rol | Guarda | Lisbon | Q1026353 (0.0 km) | GeoNames + Wikidata |
| PT | 143547 | Pontinha | Guarda | Lisbon | Q2103898 (1.1 km) | GeoNames + Wikidata |
| PT | 143548 | Portela | Guarda | Lisbon | Q1024837 (0.0 km) | GeoNames + Wikidata |
| PT | 143549 | Porto Salvo | Guarda | Lisbon | Q2093255 (0.0 km) | GeoNames + Wikidata |
| PT | 143555 | Prazeres | Guarda | Lisbon | Q1850965 (0.0 km) | GeoNames + Wikidata |
| PT | 143556 | Prior Velho | Guarda | Lisbon | Q1024836 (0.0 km) | GeoNames + Wikidata |
| PT | 143559 | Pêro Moniz | Guarda | Lisbon | Q1024979 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143561 | Póvoa de Santa Iria | Guarda | Lisbon | Q49362876 (0.0 km) | GeoNames + Wikidata |
| PT | 143562 | Póvoa de Santo Adrião | Guarda | Lisbon | Q511708 (0.0 km) | GeoNames + Wikidata |
| PT | 143565 | Queijas | Guarda | Lisbon | Q49363043 (0.0 km) | GeoNames + Wikidata |
| PT | 143571 | Ramada | Guarda | Lisbon | Q1961840 (0.0 km) | GeoNames + Wikidata |
| PT | 143572 | Ramalhal | Guarda | Lisbon | Q2119138 (0.0 km) | GeoNames + Wikidata |
| PT | 143578 | Reboleira | Guarda | Lisbon | Q928716 (0.0 km) | GeoNames + Wikidata |
| PT | 143581 | Reguengo Grande | Guarda | Lisbon | Q2119131 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143584 | Ribafria | Guarda | Lisbon | Q2119991 (0.0 km) | GeoNames + Wikidata |
| PT | 143585 | Ribamar | Guarda | Lisbon | Q990177 (0.0 km) | GeoNames + Wikidata |
| PT | 143590 | Rio de Mouro | Guarda | Lisbon | Q1631953 (0.0 km) | GeoNames + Wikidata |
| PT | 143592 | Runa | Guarda | Lisbon | Q1385363 (0.0 km) | GeoNames + Wikidata |
| PT | 143596 | Sacavém | Guarda | Lisbon | Q126681 (0.0 km) | GeoNames + Wikidata |
| PT | 143597 | Sacramento | Guarda | Lisbon | Q1817058 (0.0 km) | GeoNames + Wikidata |
| PT | 143603 | Santa Bárbara | Guarda | Lisbon | Q2118840 (0.0 km) | GeoNames + Wikidata |
| PT | 143606 | Santa Engrácia | Guarda | Lisbon | Q612059 (0.0 km) | GeoNames + Wikidata |
| PT | 143610 | Santa Iria de Azoia | Guarda | Lisbon | Q2057078 (0.0 km) | GeoNames + Wikidata |
| PT | 143611 | Santa Isabel | Guarda | Lisbon | Q368655 (0.0 km) | GeoNames + Wikidata |
| PT | 143612 | Santa Justa | Guarda | Lisbon | Q1786376 (0.0 km) | GeoNames + Wikidata |
| PT | 143614 | Santa Maria de Belém | Guarda | Lisbon | Q33852278 (0.7 km) | GeoNames + Wikidata |
| PT | 143615 | Santa Maria do Castelo e São Miguel | Guarda | Lisbon | Q177403 (0.0 km) | GeoNames + Wikidata |
| PT | 143616 | Santa Maria dos Olivais | Guarda | Lisbon | Q1786397 (0.0 km) | GeoNames + Wikidata |
| PT | 143617 | Santa Maria e São Miguel | Guarda | Lisbon | Q1661925 (0.0 km) | GeoNames + Wikidata |
| PT | 143621 | Santiago dos Velhos | Guarda | Lisbon | Q1025011 (0.0 km) | GeoNames + Wikidata |
| PT | 143622 | Santo Antão do Tojal | Guarda | Lisbon | Q738803 (0.0 km) | GeoNames + Wikidata |
| PT | 143623 | Santo António dos Cavaleiros | Guarda | Lisbon | Q1024976 (0.0 km) | GeoNames + Wikidata |
| PT | 143624 | Santo Condestável | Guarda | Lisbon | Q1786417 (0.0 km) | GeoNames + Wikidata |
| PT | 143625 | Santo Estêvão | Guarda | Lisbon | Q961456 (0.0 km) | GeoNames + Wikidata |
| PT | 143626 | Santo Estêvão das Galés | Guarda | Lisbon | Q731589 (0.7 km) | GeoNames + Wikidata |
| PT | 143627 | Santo Isidoro | Guarda | Lisbon | Q787763 (0.0 km) | GeoNames + Wikidata |
| PT | 143628 | Santo Quintino | Guarda | Lisbon | Q2119144 (0.0 km) | GeoNames + Wikidata |
| PT | 143629 | Santos-o-Velho | Guarda | Lisbon | Q1890230 (0.0 km) | GeoNames + Wikidata |
| PT | 143630 | Sapataria | Guarda | Lisbon | Q2119190 (0.0 km) | GeoNames + Wikidata |
| PT | 143639 | Silveira | Guarda | Lisbon | Q49367778 (0.0 km) | GeoNames + Wikidata |
| PT | 143643 | Sobral da Abelheira | Guarda | Lisbon | Q1024986 (0.0 km) | GeoNames + Wikidata |
| PT | 143645 | Sobral de Monte Agraço | Guarda | Lisbon | Q1005105 (0.0 km) | GeoNames + Wikidata |
| PT | 143646 | Sobralinho | Guarda | Lisbon | Q944452 (0.0 km) | GeoNames + Wikidata |
| PT | 143647 | Socorro | Guarda | Lisbon | Q1466131 (0.0 km) | GeoNames + Wikidata |
| PT | 143654 | São Bartolomeu dos Galegos | Guarda | Lisbon | Q1794739 (0.0 km) | GeoNames + Wikidata |
| PT | 143655 | São Brás | Guarda | Lisbon | Q1024772 (0.0 km) | GeoNames + Wikidata |
| PT | 143656 | São Cristóvão e São Lourenço | Guarda | Lisbon | Q1740339 (0.0 km) | GeoNames + Wikidata |
| PT | 143657 | São Domingos de Benfica | Guarda | Lisbon | Q1618787 (0.0 km) | GeoNames + Wikidata |
| PT | 143658 | São Domingos de Rana | Guarda | Lisbon | Q33502987 (0.0 km) | GeoNames + Wikidata |
| PT | 143659 | São Francisco Xavier | Guarda | Lisbon | Q972747 (0.0 km) | GeoNames + Wikidata |
| PT | 143660 | São Jorge de Arroios | Guarda | Lisbon | Q1850958 (0.0 km) | GeoNames + Wikidata |
| PT | 143661 | São José | Guarda | Lisbon | Q1786370 (0.0 km) | GeoNames + Wikidata |
| PT | 143662 | São João | Guarda | Lisbon | Q1528245 (0.0 km) | GeoNames + Wikidata |
| PT | 143663 | São João Dos Montes | Guarda | Lisbon | Q33862485 (2.5 km) | GeoNames + Wikidata |
| PT | 143664 | São João da Talha | Guarda | Lisbon | Q1024823 (0.0 km) | GeoNames + Wikidata |
| PT | 143665 | São João das Lampas | Guarda | Lisbon | Q992328 (2.0 km) | GeoNames + Wikidata |
| PT | 143666 | São João de Brito | Guarda | Lisbon | Q960058 (0.0 km) | GeoNames + Wikidata |
| PT | 143667 | São João de Deus | Guarda | Lisbon | Q786334 (0.0 km) | GeoNames + Wikidata |
| PT | 143669 | São Julião do Tojal | Guarda | Lisbon | Q1024945 (0.0 km) | GeoNames + Wikidata |
| PT | 143670 | São Mamede | Guarda | Lisbon | Q2035325 (0.0 km) | GeoNames + Wikidata |
| PT | 143671 | São Marcos | Guarda | Lisbon | Q1021763 (0.7 km) | GeoNames + Wikidata |
| PT | 143673 | São Miguel | Guarda | Lisbon | Q969311 (0.0 km) | GeoNames + Wikidata |
| PT | 143675 | São Miguel de Alcainça | Guarda | Lisbon | Q267405 (0.0 km) | GeoNames + Wikidata |
| PT | 143676 | São Nicolau | Guarda | Lisbon | Q1786384 (0.0 km) | GeoNames + Wikidata |
| PT | 143678 | São Paulo | Guarda | Lisbon | Q1817090 (0.0 km) | GeoNames + Wikidata |
| PT | 143680 | São Pedro da Cadeira | Guarda | Lisbon | Q33503173 (0.0 km) | GeoNames + Wikidata |
| PT | 143681 | São Pedro de Penaferrim | Guarda | Lisbon | Q1617626 (0.0 km) | GeoNames + Wikidata |
| PT | 143684 | São Sebastião da Pedreira | Guarda | Lisbon | Q1285555 (0.0 km) | GeoNames + Wikidata |
| PT | 143686 | São Vicente de Fora | Guarda | Lisbon | Q1026664 (0.0 km) | GeoNames + Wikidata |
| PT | 143691 | Terrugem | Guarda | Lisbon | Q1328618 (0.0 km) | GeoNames + Wikidata |
| PT | 143694 | Torres Vedras | Guarda | Lisbon | Q917319 (0.0 km) | GeoNames + Wikidata |
| PT | 143700 | Triana | Guarda | Lisbon | Q1704986 (0.0 km) | GeoNames + Wikidata |
| PT | 143702 | Turcifal | Guarda | Lisbon | Q2119181 (0.9 km) | GeoNames + Wikidata |
| PT | 143703 | Unhos | Guarda | Lisbon | Q954974 (0.0 km) | GeoNames + Wikidata |
| PT | 143712 | Vale do Paraíso | Guarda | Lisbon | Q1024768 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143720 | Venda Nova | Guarda | Lisbon | Q1024973 (0.0 km) | GeoNames + Wikidata |
| PT | 143721 | Venda do Pinheiro | Guarda | Lisbon | Q1024966 (0.0 km) | GeoNames + Wikidata |
| PT | 143722 | Venteira | Guarda | Lisbon | Q1024994 (0.0 km) | GeoNames + Wikidata |
| PT | 143723 | Ventosa | Guarda | Lisbon | Q33511589 (0.0 km) | GeoNames + Wikidata |
| PT | 143724 | Vermelha | Guarda | Lisbon | Q1901338 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143726 | Vialonga | Guarda | Lisbon | Q33511692 (0.0 km) | GeoNames + Wikidata |
| PT | 143738 | Vila Franca de Xira | Guarda | Lisbon | Q917326 (0.0 km) | GeoNames + Wikidata |
| PT | 143740 | Vila Franca do Rosário | Guarda | Lisbon | Q1025009 (0.0 km) | GeoNames + Wikidata |
| PT | 143742 | Vila Nova da Rainha | Guarda | Lisbon | Q144683 (0.0 km) | GeoNames + Wikidata |
| PT | 143744 | Vila Nova de São Pedro | Guarda | Lisbon | Q1010908 (0.0 km) | Wikidata + GeoNames (nearby) |
| PT | 143749 | Vila Verde dos Francos | Guarda | Lisbon | Q2118819 (0.0 km) | GeoNames + Wikidata |
| PT | 143751 | Vilar | Guarda | Lisbon | Q1024961 (0.0 km) | GeoNames + Wikidata |
| PT | 143757 | Vimeiro | Guarda | Lisbon | Q1932382 (0.0 km) | GeoNames + Wikidata |
| UA | 109934 | Lozuvatka | Kirovohradska | Dnipropetrovska | Q4265521 (0.7 km) | GeoNames + Wikidata |
| UA | 149311 | Abramok | Poltavska | Zhytomyrska | Q4055011 (0.0 km) | GeoNames + Wikidata |
| UA | 149312 | Adamivka | Poltavska | Zhytomyrska | Q2068017 (0.0 km) | GeoNames + Wikidata |
| UA | 149313 | Adamove | Poltavska | Zhytomyrska | Q4057335 (0.0 km) | GeoNames + Wikidata |
| UA | 149314 | Agativka | Poltavska | Zhytomyrska | Q4056703 (0.0 km) | GeoNames + Wikidata |
| UA | 149316 | Andrushivka | Poltavska | Zhytomyrska | Q148909 (0.0 km) | GeoNames + Wikidata |
| UA | 149318 | Avratin | Poltavska | Zhytomyrska | Q4056049 (0.0 km) | GeoNames + Wikidata |
| UA | 149323 | Barashi | Poltavska | Zhytomyrska | Q4077969 (0.0 km) | GeoNames + Wikidata |
| UA | 149324 | Bazar | Poltavska | Zhytomyrska | Q2022610 (0.0 km) | GeoNames + Wikidata |
| UA | 149325 | Bekhi | Poltavska | Zhytomyrska | Q4086027 (0.0 km) | GeoNames + Wikidata |
| UA | 149326 | Berdychiv | Poltavska | Zhytomyrska | Q158799 (0.0 km) | GeoNames + Wikidata |
| UA | 149327 | Berestivka | Poltavska | Zhytomyrska | Q2067931 (0.0 km) | GeoNames + Wikidata |
| UA | 149328 | Berestovets | Poltavska | Zhytomyrska | Q4084783 (0.0 km) | GeoNames + Wikidata |
| UA | 149329 | Berezianka | Poltavska | Zhytomyrska | Q4084692 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149330 | Berezovii Grud | Poltavska | Zhytomyrska | Q4085537 (0.0 km) | GeoNames + Wikidata |
| UA | 149331 | Bereztsi | Poltavska | Zhytomyrska | Q4084689 (0.0 km) | GeoNames + Wikidata |
| UA | 149332 | Bicheva | Poltavska | Zhytomyrska | Q4087601 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149333 | Bigun | Poltavska | Zhytomyrska | Q4080567 (0.0 km) | GeoNames + Wikidata |
| UA | 149334 | Bikiv | Poltavska | Zhytomyrska | Q4100957 (0.0 km) | GeoNames + Wikidata |
| UA | 149335 | Bila Krynytsia | Poltavska | Zhytomyrska | Q2902643 (0.0 km) | GeoNames + Wikidata |
| UA | 149336 | Bilii Bereg | Poltavska | Zhytomyrska | Q4083065 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149337 | Bilka | Poltavska | Zhytomyrska | Q4082016 (0.0 km) | GeoNames + Wikidata |
| UA | 149338 | Bilylivka | Poltavska | Zhytomyrska | Q1994731 (0.0 km) | GeoNames + Wikidata |
| UA | 149339 | Bistrik | Poltavska | Zhytomyrska | Q4101119 (0.0 km) | GeoNames + Wikidata |
| UA | 149340 | Bistriyivka | Poltavska | Zhytomyrska | Q4101107 (0.0 km) | GeoNames + Wikidata |
| UA | 149342 | Broniki | Poltavska | Zhytomyrska | Q4096993 (0.0 km) | GeoNames + Wikidata |
| UA | 149343 | Bronitska Guta | Poltavska | Zhytomyrska | Q4097010 (0.0 km) | GeoNames + Wikidata |
| UA | 149344 | Bronitsia | Poltavska | Zhytomyrska | Q4097007 (0.0 km) | GeoNames + Wikidata |
| UA | 149345 | Brovki Pershi | Poltavska | Zhytomyrska | Q947465 (0.0 km) | GeoNames + Wikidata |
| UA | 149346 | Brusyliv | Poltavska | Zhytomyrska | Q946994 (0.0 km) | GeoNames + Wikidata |
| UA | 149347 | Buchmany | Poltavska | Zhytomyrska | Q2670513 (0.0 km) | GeoNames + Wikidata |
| UA | 149348 | Buki | Poltavska | Zhytomyrska | Q4098569 (0.0 km) | GeoNames + Wikidata |
| UA | 149349 | Buldichiv | Poltavska | Zhytomyrska | Q4098921 (0.0 km) | GeoNames + Wikidata |
| UA | 149350 | Buriaki | Poltavska | Zhytomyrska | Q2913489 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149351 | Burkivtsi | Poltavska | Zhytomyrska | Q4099657 (0.0 km) | GeoNames + Wikidata |
| UA | 149352 | Bykivka | Poltavska | Zhytomyrska | Q2670499 (0.0 km) | GeoNames + Wikidata |
| UA | 149354 | Cherniakhiv | Poltavska | Zhytomyrska | Q872377 (0.0 km) | GeoNames + Wikidata |
| UA | 149355 | Chervone | Poltavska | Zhytomyrska | Q787722 (0.0 km) | GeoNames + Wikidata |
| UA | 149356 | Chopovychi | Poltavska | Zhytomyrska | Q2980446 (0.0 km) | GeoNames + Wikidata |
| UA | 149358 | Chudniv | Poltavska | Zhytomyrska | Q149271 (0.0 km) | GeoNames + Wikidata |
| UA | 149360 | Dashynka | Poltavska | Zhytomyrska | Q4155490 (0.0 km) | GeoNames + Wikidata |
| UA | 149361 | Davidivka | Poltavska | Zhytomyrska | Q4153834 (0.0 km) | GeoNames + Wikidata |
| UA | 149362 | Davydky | Poltavska | Zhytomyrska | Q4153710 (0.0 km) | GeoNames + Wikidata |
| UA | 149363 | Denyshi | Poltavska | Zhytomyrska | Q4158075 (0.0 km) | GeoNames + Wikidata |
| UA | 149364 | Derhanivka | Poltavska | Zhytomyrska | Q4158721 (0.0 km) | GeoNames + Wikidata |
| UA | 149365 | Dibrova | Poltavska | Zhytomyrska | Q1209354 (0.0 km) | GeoNames + Wikidata |
| UA | 149366 | Didkovichi | Poltavska | Zhytomyrska | Q4156713 (0.0 km) | GeoNames + Wikidata |
| UA | 149367 | Didovichi | Poltavska | Zhytomyrska | Q4156741 (0.0 km) | GeoNames + Wikidata |
| UA | 149368 | Divochki | Poltavska | Zhytomyrska | Q4156444 (0.0 km) | GeoNames + Wikidata |
| UA | 149369 | Dovbysh | Poltavska | Zhytomyrska | Q2993483 (0.0 km) | GeoNames + Wikidata |
| UA | 149370 | Druzhba | Poltavska | Zhytomyrska | Q611942 (0.0 km) | GeoNames + Wikidata |
| UA | 149371 | Dubivka | Poltavska | Zhytomyrska | Q4169424 (0.0 km) | GeoNames + Wikidata |
| UA | 149372 | Dubnyki | Poltavska | Zhytomyrska | Q7277540 (0.0 km) | GeoNames + Wikidata |
| UA | 149373 | Dubrivka | Poltavska | Zhytomyrska | Q4161162 (0.0 km) | GeoNames + Wikidata |
| UA | 149374 | Dvorishche | Poltavska | Zhytomyrska | Q4156008 (0.0 km) | GeoNames + Wikidata |
| UA | 149376 | Elivka | Poltavska | Zhytomyrska | Q4174648 (0.0 km) | GeoNames + Wikidata |
| UA | 149379 | Glinivtsi | Poltavska | Zhytomyrska | Q4139837 (0.0 km) | GeoNames + Wikidata |
| UA | 149380 | Godikha | Poltavska | Zhytomyrska | Q4141222 (0.0 km) | GeoNames + Wikidata |
| UA | 149381 | Golovenka | Poltavska | Zhytomyrska | Q4141784 (0.0 km) | GeoNames + Wikidata |
| UA | 149382 | Golovki | Poltavska | Zhytomyrska | Q4141903 (0.0 km) | GeoNames + Wikidata |
| UA | 149383 | Golubyatin | Poltavska | Zhytomyrska | Q4142643 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149384 | Gorbuliv | Poltavska | Zhytomyrska | Q4143670 (0.0 km) | GeoNames + Wikidata |
| UA | 149385 | Gordiyivka | Poltavska | Zhytomyrska | Q4143849 (0.0 km) | GeoNames + Wikidata |
| UA | 149387 | Gorodkivka | Poltavska | Zhytomyrska | Q4145259 (0.0 km) | GeoNames + Wikidata |
| UA | 149388 | Gorodok | Poltavska | Zhytomyrska | Q4145357 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149389 | Gorodske | Poltavska | Zhytomyrska | Q4145468 (0.0 km) | GeoNames + Wikidata |
| UA | 149390 | Goropayi | Poltavska | Zhytomyrska | Q4145756 (0.0 km) | GeoNames + Wikidata |
| UA | 149391 | Goshiv | Poltavska | Zhytomyrska | Q4147163 (0.0 km) | GeoNames + Wikidata |
| UA | 149392 | Gromada | Poltavska | Zhytomyrska | Q4150140 (0.0 km) | GeoNames + Wikidata |
| UA | 149393 | Grozyne | Poltavska | Zhytomyrska | Q4150085 (0.0 km) | GeoNames + Wikidata |
| UA | 149394 | Grushki | Poltavska | Zhytomyrska | Q4150958 (0.0 km) | GeoNames + Wikidata |
| UA | 149396 | Gulsk | Poltavska | Zhytomyrska | Q4151907 (0.0 km) | GeoNames + Wikidata |
| UA | 149397 | Gumenniki | Poltavska | Zhytomyrska | Q4152062 (0.0 km) | GeoNames + Wikidata |
| UA | 149398 | Guta-Potiyivka | Poltavska | Zhytomyrska | Q4152948 (0.0 km) | GeoNames + Wikidata |
| UA | 149399 | Guto-Mariatin | Poltavska | Zhytomyrska | Q4153035 (0.0 km) | GeoNames + Wikidata |
| UA | 149402 | Holovyne | Poltavska | Zhytomyrska | Q2670503 (0.0 km) | GeoNames + Wikidata |
| UA | 149403 | Holubivka | Poltavska | Zhytomyrska | Q4142498 (0.0 km) | GeoNames + Wikidata |
| UA | 149405 | Horodets | Poltavska | Zhytomyrska | Q7284988 (0.0 km) | GeoNames + Wikidata |
| UA | 149406 | Horodnytsia | Poltavska | Zhytomyrska | Q2670476 (0.0 km) | GeoNames + Wikidata |
| UA | 149408 | Hranitne | Poltavska | Zhytomyrska | Q2980455 (0.0 km) | GeoNames + Wikidata |
| UA | 149410 | Hryshkivtsi | Poltavska | Zhytomyrska | Q2993492 (0.0 km) | GeoNames + Wikidata |
| UA | 149411 | Iemilivka | Poltavska | Zhytomyrska | Q4175477 (0.0 km) | GeoNames + Wikidata |
| UA | 149412 | Ievgenivka | Poltavska | Zhytomyrska | Q4172872 (0.0 km) | GeoNames + Wikidata |
| UA | 149413 | Irshansk | Poltavska | Zhytomyrska | Q2652172 (3.1 km) | Wikidata + GeoNames (nearby) |
| UA | 149414 | Ivanivka | Poltavska | Zhytomyrska | Q52444 (0.0 km) | GeoNames + Wikidata |
| UA | 149415 | Ivankiv | Poltavska | Zhytomyrska | Q4195806 (0.0 km) | GeoNames + Wikidata |
| UA | 149416 | Ivanopil | Poltavska | Zhytomyrska | Q2670459 (0.0 km) | GeoNames + Wikidata |
| UA | 149420 | Khodaky | Poltavska | Zhytomyrska | Q2067925 (0.0 km) | GeoNames + Wikidata |
| UA | 149422 | Khoroshiv | Poltavska | Zhytomyrska | Q2993479 (0.0 km) | GeoNames + Wikidata |
| UA | 149425 | Korchak | Poltavska | Zhytomyrska | Q4234462 (0.0 km) | GeoNames + Wikidata |
| UA | 149426 | Kornyn | Poltavska | Zhytomyrska | Q2980432 (0.0 km) | GeoNames + Wikidata |
| UA | 149428 | Korostyshiv | Poltavska | Zhytomyrska | Q149190 (0.0 km) | GeoNames + Wikidata |
| UA | 149435 | Kupech | Poltavska | Zhytomyrska | Q4247459 (0.0 km) | GeoNames + Wikidata |
| UA | 149436 | Kvitneve | Poltavska | Zhytomyrska | Q4180942 (0.0 km) | GeoNames + Wikidata |
| UA | 149439 | Lasky | Poltavska | Zhytomyrska | Q4254749 (0.0 km) | GeoNames + Wikidata |
| UA | 149440 | Lazarivka | Poltavska | Zhytomyrska | Q4252858 (0.0 km) | GeoNames + Wikidata |
| UA | 149442 | Liubar | Poltavska | Zhytomyrska | Q2652151 (0.0 km) | GeoNames + Wikidata |
| UA | 149445 | Luhyny | Poltavska | Zhytomyrska | Q2652141 (0.0 km) | GeoNames + Wikidata |
| UA | 149448 | Malyn | Poltavska | Zhytomyrska | Q148997 (0.0 km) | GeoNames + Wikidata |
| UA | 149452 | Morozivka | Poltavska | Zhytomyrska | Q7224179 (0.0 km) | GeoNames + Wikidata |
| UA | 149454 | Myropil | Poltavska | Zhytomyrska | Q2980442 (0.0 km) | GeoNames + Wikidata |
| UA | 149455 | Narodychi | Poltavska | Zhytomyrska | Q2603008 (0.0 km) | GeoNames + Wikidata |
| UA | 149457 | Nemyryntsi | Poltavska | Zhytomyrska | Q4316931 (0.0 km) | GeoNames + Wikidata |
| UA | 149458 | Nova Borova | Poltavska | Zhytomyrska | Q2980437 (0.0 km) | GeoNames + Wikidata |
| UA | 149459 | Nova Chortoriia | Poltavska | Zhytomyrska | Q4322387 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149460 | Novi Bilokorovychi | Poltavska | Zhytomyrska | Q2629639 (0.0 km) | GeoNames + Wikidata |
| UA | 149462 | Novi Vorobyi | Poltavska | Zhytomyrska | Q4326351 (0.0 km) | GeoNames + Wikidata |
| UA | 149463 | Novohrad-Volynskyi | Poltavska | Zhytomyrska | Q149024 (0.0 km) | GeoNames + Wikidata |
| UA | 149464 | Novoozerianka | Poltavska | Zhytomyrska | Q2670496 (0.0 km) | GeoNames + Wikidata |
| UA | 149468 | Olevsk | Poltavska | Zhytomyrska | Q913143 (0.0 km) | GeoNames + Wikidata |
| UA | 149472 | Ovruch | Poltavska | Zhytomyrska | Q27039 (0.0 km) | GeoNames + Wikidata |
| UA | 149473 | Ozerne | Poltavska | Zhytomyrska | Q1586535 (0.0 km) | GeoNames + Wikidata |
| UA | 149474 | Pavoloch | Poltavska | Zhytomyrska | Q4341950 (0.0 km) | GeoNames + Wikidata |
| UA | 149475 | Pershotravensk | Poltavska | Zhytomyrska | Q2629643 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149476 | Pershotravneve | Poltavska | Zhytomyrska | Q2670465 (0.0 km) | GeoNames + Wikidata |
| UA | 149479 | Pishchiv | Poltavska | Zhytomyrska | Q4364117 (0.0 km) | GeoNames + Wikidata |
| UA | 149480 | Polianka | Poltavska | Zhytomyrska | Q2670222 (0.0 km) | GeoNames + Wikidata |
| UA | 149482 | Popilnia | Poltavska | Zhytomyrska | Q2652368 (0.0 km) | GeoNames + Wikidata |
| UA | 149484 | Potiivka | Poltavska | Zhytomyrska | Q2067940 (0.0 km) | GeoNames + Wikidata |
| UA | 149487 | Radomyshl | Poltavska | Zhytomyrska | Q149163 (0.0 km) | GeoNames + Wikidata |
| UA | 149489 | Rohachi | Poltavska | Zhytomyrska | Q4395406 (0.1 km) | Wikidata + GeoNames (nearby) |
| UA | 149490 | Romaniv | Poltavska | Zhytomyrska | Q2629338 (0.0 km) | GeoNames + Wikidata |
| UA | 149496 | Shumsk | Poltavska | Ternopilska | Q219601 (0.0 km) | GeoNames + Wikidata |
| UA | 149497 | Slovechne | Poltavska | Zhytomyrska | Q3878279 (0.0 km) | GeoNames + Wikidata |
| UA | 149498 | Smolovivshchina | Poltavska | Dnipropetrovska | Q108896852 (0.1 km) | GeoNames + Wikidata |
| UA | 149502 | Tabory | Poltavska | Zhytomyrska | Q4449304 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149504 | Topory | Poltavska | Zhytomyrska | Q4460882 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149505 | Travneve | Poltavska | Zhytomyrska | Q4461695 (0.0 km) | GeoNames + Wikidata |
| UA | 149511 | Velyki Korovyntsi | Poltavska | Zhytomyrska | Q2670469 (0.0 km) | GeoNames + Wikidata |
| UA | 149513 | Veresna | Poltavska | Zhytomyrska | Q4107700 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149515 | Virlya | Poltavska | Zhytomyrska | Q4112053 (0.0 km) | GeoNames + Wikidata |
| UA | 149517 | Yablunets | Poltavska | Zhytomyrska | Q2670247 (0.0 km) | GeoNames + Wikidata |
| UA | 149518 | Yarun | Poltavska | Zhytomyrska | Q4539028 (0.0 km) | GeoNames + Wikidata |
| UA | 149519 | Yemilchyne | Poltavska | Zhytomyrska | Q2641633 (0.0 km) | GeoNames + Wikidata |
| UA | 149520 | Zabaro-Davidivka | Poltavska | Zhytomyrska | Q4182362 (0.0 km) | GeoNames + Wikidata |
| UA | 149522 | Zakrinichchia | Poltavska | Zhytomyrska | Q4185014 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149523 | Zalissia | Poltavska | Zhytomyrska | Q4185265 (0.0 km) | GeoNames + Wikidata |
| UA | 149524 | Zaliznia | Poltavska | Zhytomyrska | Q4185403 (0.0 km) | GeoNames + Wikidata |
| UA | 149525 | Zaluzhne | Poltavska | Zhytomyrska | Q4185527 (0.0 km) | GeoNames + Wikidata |
| UA | 149526 | Zapadnia | Poltavska | Zhytomyrska | Q4186608 (0.0 km) | GeoNames + Wikidata |
| UA | 149527 | Zarichchia | Poltavska | Zhytomyrska | Q4187421 (0.0 km) | GeoNames + Wikidata |
| UA | 149528 | Zarudintsi | Poltavska | Zhytomyrska | Q4187633 (0.0 km) | GeoNames + Wikidata |
| UA | 149530 | Zbranki | Poltavska | Zhytomyrska | Q7268773 (0.0 km) | GeoNames + Wikidata |
| UA | 149531 | Zdorovets | Poltavska | Zhytomyrska | Q4190003 (0.0 km) | GeoNames + Wikidata |
| UA | 149532 | Zherdeli | Poltavska | Zhytomyrska | Q4179550 (0.0 km) | GeoNames + Wikidata |
| UA | 149533 | Zhitintsi | Poltavska | Zhytomyrska | Q4180655 (0.0 km) | Wikidata + GeoNames (nearby) |
| UA | 149534 | Zhovte | Poltavska | Zhytomyrska | Q4182075 (0.0 km) | GeoNames + Wikidata |
| UA | 149535 | Zhovtii Brid | Poltavska | Zhytomyrska | Q4182092 (0.0 km) | GeoNames + Wikidata |
| UA | 149536 | Zhupanivka | Poltavska | Zhytomyrska | Q4181651 (0.0 km) | GeoNames + Wikidata |
| UA | 149537 | Zhurbintsi | Poltavska | Zhytomyrska | Q4181869 (0.0 km) | GeoNames + Wikidata |
| UA | 149538 | Zhytomyr | Poltavska | Zhytomyrska | Q156713 (0.0 km) | GeoNames + Wikidata |
| UA | 149540 | Zlobichi | Poltavska | Zhytomyrska | Q4192464 (0.0 km) | GeoNames + Wikidata |
| UA | 149541 | Zoriane | Poltavska | Zhytomyrska | Q4194051 (0.0 km) | GeoNames + Wikidata |
| UA | 149542 | Zorokiv | Poltavska | Zhytomyrska | Q4194028 (0.0 km) | GeoNames + Wikidata |
| UA | 149543 | Zosimivka | Poltavska | Zhytomyrska | Q4194091 (0.0 km) | GeoNames + Wikidata |
| UA | 149544 | Zubivshchina | Poltavska | Zhytomyrska | Q4194455 (0.0 km) | GeoNames + Wikidata |
| UA | 149545 | Zvizdal | Poltavska | Zhytomyrska | Q12106415 (0.3 km) | GeoNames + Wikidata |

### Also found (not changed here)
- **Duplicates.** 110 of the moved records now sit within 1.5 km of a near-identical record in the same state (e.g.
  *Alcabideche* 143243 and 88915): the batches re-added places that already existed. They wait for the
  duplicate-merge policy in #1643.
- **The Philippines** has the same problem on a larger scale (about 1,560 records, plus 974 duplicates); it needs its
  own pass.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/{PT,UA,JP}.json` — `state_id` and `state_code` on 453 records; coordinates on 2

## Cities filed under the wrong state: 12 more countries

### How they were found
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames place
(`cities500`) with the same name within 3 km and **exactly the record's population**. Per country, GeoNames'
region codes were mapped to CSC states by majority vote of the records fingerprinted to them; a record is a
candidate when its entry's code maps (at least 5 records, 80% agreement) to another state. Mexico, Spain, France
and Italy are covered by their own PRs.

256 candidates in 22 countries: Italy's 117 went to #1657. The Philippines, Sri Lanka and Sierra Leone were dropped
(GeoNames' regions are a different level from CSC's states, or predate a new province), and two records where GeoNames
predates a province split (Miraflores in Lima, La Libertad in Santa Elena). The other 86 were checked on Wikidata:
the item with the record's name within 2 km of its point, followed up its "located in" (P131) chain to a CSC state.

| Result | Records |
|---|---:|
| Wikidata agrees with GeoNames; no same-named place in the filed state; populations compatible | **19** |
| Wikidata agrees, but its region is not in CSC (Dīla, below): held | 1 |
| Held by a guard, moved after a hand check (Horn, Ngawi) | **2** |
| Held by a guard (a same-named place in the filed state, or a population mismatch) | 8 |
| Wikidata says the filed state is right, e.g. Yanam (Puducherry, inside Andhra Pradesh) | 15 |
| No same-named item nearby, or contained in no or several CSC states | 41 |

### Fix
**21 cities** move. Only `state_id` and `state_code` change; every record's `timezone` already fits its new state.

| Country | id | City | Was filed under | Now | Population | Matched Wikidata items | Note |
|---|---|---|---|---|---:|---|---|
| CA | 16417 | Fallingbrook | Prince Edward Island (PE) | Ontario (ON) | 25,000 | Q5432394 |  |
| CH | 17934 | Horn | St. Gallen (SG) | Thurgau (TG) | 2,274 | Q15964148, Q22640379 | Held by the guard for two hamlets named Horn in St. Gallen; the record (2,274 people) is the Thurgau municipality, by exact GeoNames population |
| DZ | 31303 | Chemini | Tizi Ouzou (15) | Béjaïa (06) | 21,585 | Q1118209, Q2962465 |  |
| DZ | 31357 | Ighram | Tizi Ouzou (15) | Béjaïa (06) | 15,030 | Q2215840 |  |
| DZ | 31372 | Makouda | Boumerdès (35) | Tizi Ouzou (15) | 34,515 | Q2374784, Q3280947 |  |
| DZ | 31456 | Tizi Gheniff | Boumerdès (35) | Tizi Ouzou (15) | 27,974 | Q3019923, Q3529984 |  |
| GB | 49213 | Cushendall | Mid and East Antrim (MEA) | Causeway Coast and Glens (CCG) | 1,226 | Q104359932, Q2580652 | Wikidata resolves only to Northern Ireland (the district record carries another item); GeoNames and the 2015 district map say Causeway Coast and Glens |
| ID | 56886 | Ngawi | Jawa Barat (JB) | Jawa Timur (JI) | 22,412 | Q10773354, Q65299225 | Held by the guard for a population mismatch: the matched Wikidata items are Ngawi district (kecamatan, about 85,800 people); the record is its seat town, in East Java |
| IN | 132453 | Khailar | Madhya Pradesh (MP) | Uttar Pradesh (UP) | 13,334 | Q2119908 |  |
| IN | 132934 | Margherita | Arunachal Pradesh (AR) | Assam (AS) | 26,914 | Q1924981, Q63356754 |  |
| KZ | 65657 | Būrabay | North Kazakhstan (59) | Akmola (11) | 6,500 | Q1009456 |  |
| MY | 76531 | Pantai Cenang | Perlis (09) | Kedah (02) | 15,000 | Q33328099 |  |
| NO | 79257 | Jevnaker | Innlandet (34) | Akershus (32) | 4,308 | Q11283023, Q11978556 | Akershus since the 2024 county split |
| NO | 79480 | Sande | Telemark (40) | Vestfold (39) | 1,389 | Q130348197, Q183029 | Holmestrand, Vestfold |
| RS | 97406 | Tabanović | Belgrade (00) | Mačva (08) | 1,286 | Q2736282 |  |
| RU | 98424 | Fili | Moscow (MOS) | Moscow (MOW) | 80,000 | Q1002971, Q4483851 |  |
| RU | 98425 | Filimonki | Moscow (MOS) | Moscow (MOW) | 1,329 | Q4483879 | Part of Moscow since the 2012 expansion (New Moscow) |
| RU | 99980 | Mosrentgen | Moscow (MOS) | Moscow (MOW) | 5,214 | Q4120441 | Part of Moscow since the 2012 expansion (New Moscow) |
| UA | 109819 | Kotsyubyns’ke | Kyiv (30) | Kyivska (32) | 17,623 | Q2026969 | An enclave of Kyiv Oblast inside the city of Kyiv |
| UA | 110313 | Prolisky | Kyiv (30) | Kyivska (32) | 1,852 | Q4380462 |  |
| UA | 110490 | Smyga | Khmelnytska (68) | Rivnenska (56) | 2,800 | Q2473563, Q25445118 |  |

The "Matched Wikidata items" column lists the items found at the record's point by name, which include stations
(Horn, Margherita, Jevnaker, Sande, Fili, Smyha); it is not the record's own `wikiDataId`.

### Also found (not changed here)
- **Khailar** (132453) now duplicates record 147498 in Uttar Pradesh (1.0 km apart, same population and Wikidata
  ID). It waits for the duplicate-merge policy in #1643.
- **Dīla** (38625) is not moved: Southern Nations, Nationalities, and Peoples Region was dissolved in 2023, and
  Dilla (Gedeo Zone) is now in South Ethiopia Regional State, which CSC does not have yet. The record's point is
  about 1 km north-east of the town and falls just inside Sidama, so it needs Q905423's point (6.4125, 38.3117) too.
  Both wait for South Ethiopia and Central Ethiopia to be added as states.
- **Wrong `wikiDataId`** (the copy-forward problem of #1641) on three moved records, Fallingbrook → Q1744221 (Falher,
  Alberta), Pantai Cenang → Q1923195 (Paka, Terengganu) and Smyga → Q219595 (Smila), and on Dīla → Q3033674 (Dodola).

### Rollback
Revert the commit. No `id`s change.

### Files Changed
- `contributions/cities/{CA,CH,DZ,GB,ID,IN,KZ,MY,NO,RS,RU,UA}.json` — `state_id` and `state_code` on 21 records

## Towns filed under a neighbouring city's state

**92 cities** move to the state they are in. Most were filed under the nearest large city's authority: Fife towns
(*Kirkcaldy*, *Dunfermline*, *Rosyth*) under Edinburgh or West Lothian, *Birkenhead* and *Wallasey* under Liverpool,
*Penzance* and *St Ives* under the Isles of Scilly, *Ryde* under Portsmouth, *Batley* and *Dewsbury* under Wakefield,
*Redditch* under Solihull, *Caerphilly* under Cardiff, and Moscow districts under Moscow Oblast.

### How they were found
Each record was compared with its five nearest GeoNames places (`cities500`). GeoNames' region codes were mapped to
CSC states by majority vote of the 2019 import's records whose population matches a GeoNames entry exactly. A record is
a candidate when all five places, within 15 km and the nearest within 5 km, map to one other state.

### How they were verified
Each record's own `wikiDataId` counts only if it is the record's place: a label or alias equal to the record's name
(for some, the municipality or district of that name), and a point within 5 km. Its current "located in" (P131) chain must then reach the GeoNames state and not the filed one.
Of 527 candidates outside the countries handled elsewhere, 90 passed. Eight were left out after a hand check:
- France (6): Saint-Leu is a coordinates error fixed in #1648, Messac's population is the other Messac's, and France
  has its own passes.
- Italy (2): Solaro and Piobesi Torinese have wrong points, not wrong provinces.

The rest were not moved:
- Most had no usable Wikidata ID (copy-forward IDs point elsewhere; #1641), or Wikidata confirmed the filed state.
- In Saint Lucia and Jamaica (Kingston's neighbourhoods) GeoNames uses coarser regions than CSC.
- Romania's 30 Mureș candidates are artefacts: CSC's Mureș and Maramureș records carry each other's Wikidata IDs, and
  Mureș' point lies in Alba County, about 125 km from Mureș' centre. That goes to the state Wikidata ID fix.

### Fix
Only `state_id` and `state_code` change, plus the points of Ashton in Makerfield and Barra de Carrasco (below);
every record's `timezone` already fits its new state.

| Country | Move | Records |
|---|---|---:|
| GB | Edinburgh → Fife | 10 |
| GB | West Lothian → Fife | 8 |
| GB | Portsmouth → Isle of Wight | 4 |
| GB | Plymouth → Cornwall | 4 |
| RU | Moscow Oblast (MOS) → Moscow city (MOW) | 4 |
| GB | Sandwell → Worcestershire | 3 |
| GB | Warrington → Cheshire West and Chester | 3 |
| GB | Clackmannanshire → Fife | 3 |
| GB | Isles of Scilly → Cornwall | 3 |
| GR | Central Greece → Thessaly | 3 |
| GB | Solihull → Worcestershire | 2 |
| GB | Havering → Thurrock | 2 |
| GB | Wakefield → Kirklees | 2 |
| GB | Liverpool → Wirral | 2 |
| GB | Wirral → Cheshire West and Chester | 2 |
| GB | Merthyr Tydfil → Caerphilly | 2 |
| GB | Calderdale → Bradford | 2 |
| GB | Falkirk → Fife | 2 |
| GB | Dundee → Fife | 2 |
| MX | Estado de México → Michoacán de Ocampo | 2 |
| NO | Buskerud → Akershus | 2 |
| GB | St Helens → Wigan | 1 |
| GB | Birmingham → Worcestershire | 1 |
| GB | Cardiff → Caerphilly | 1 |
| GB | Bradford → Kirklees | 1 |
| GB | Bristol → North Somerset | 1 |
| GB | Coventry → Solihull | 1 |
| GB | Blaenau Gwent → Caerphilly | 1 |
| GB | Bexley → Thurrock | 1 |
| GB | Wrexham → Flintshire | 1 |
| GB | Dudley → North Tyneside | 1 |
| RS | Nišava → Central Banat | 1 |
| RS | Pomoravlje → Mačva | 1 |
| RS | Raška → Mačva | 1 |
| RS | Braničevo → Mačva | 1 |
| RS | North Bačka → Mačva | 1 |

| Country | id | City | Was filed under | Now | Population | Own Wikidata ID (distance) |
|---|---|---|---|---|---:|---|
| GB | 48171 | Aberdour | Edinburgh (EDH) | Fife (FIF) | 1710 | Q2014221 (0.2 km) |
| GB | 48235 | Alvechurch | Solihull (SOL) | Worcestershire (WOR) | 3534 | Q1639867 (0.1 km) |
| GB | 48296 | Ashton in Makerfield | St Helens (SHN) | Wigan (WGN) | 29039 | Q2557991 (0.7 km) |
| GB | 48318 | Aveley | Havering (HAV) | Thurrock (THR) | 9801 | Q2449718 (0.2 km) |
| GB | 48348 | Ballingry | Edinburgh (EDH) | Fife (FIF) | 5740 | Q1012304 (0.2 km) |
| GB | 48404 | Barnt Green | Birmingham (BIR) | Worcestershire (WOR) | 5366 | Q582689 (0.6 km) |
| GB | 48429 | Batley | Wakefield (WKF) | Kirklees (KIR) | 50807 | Q810847 (1.5 km) |
| GB | 48457 | Belbroughton | Sandwell (SAW) | Worcestershire (WOR) | 1272 | Q2268622 (0.1 km) |
| GB | 48469 | Bembridge | Portsmouth (POR) | Isle of Wight (IOW) | 3560 | Q2624470 (0.6 km) |
| GB | 48520 | Birkenhead | Liverpool (LIV) | Wirral (WRL) | 325264 | Q746718 (1.1 km) |
| GB | 48780 | Burntisland | Edinburgh (EDH) | Fife (FIF) | 6590 | Q1011521 (0.3 km) |
| GB | 48813 | Caerphilly | Cardiff (CRF) | Caerphilly (CAY) | 31060 | Q909119 (0.4 km) |
| GB | 48816 | Cairneyhill | West Lothian (WLN) | Fife (FIF) | 2400 | Q1011976 (0.1 km) |
| GB | 48826 | Callington | Plymouth (PLY) | Cornwall (CON) | 5983 | Q2045500 (0.3 km) |
| GB | 48853 | Cardenden | Edinburgh (EDH) | Fife (FIF) | 5420 | Q1014545 (1.2 km) |
| GB | 49027 | Cleckheaton | Bradford (BRD) | Kirklees (KIR) | 27393 | Q1022447 (0.4 km) |
| GB | 49130 | Cowdenbeath | Edinburgh (EDH) | Fife (FIF) | 11640 | Q1010263 (0.4 km) |
| GB | 49174 | Crossford | West Lothian (WLN) | Fife (FIF) | 2360 | Q3698674 (0.3 km) |
| GB | 49176 | Crossgates | Edinburgh (EDH) | Fife (FIF) | 2610 | Q5188613 (0.1 km) |
| GB | 49221 | Dalgety Bay | Edinburgh (EDH) | Fife (FIF) | 10050 | Q1984807 (1.4 km) |
| GB | 49279 | Dewsbury | Wakefield (WKF) | Kirklees (KIR) | 62945 | Q525508 (0.9 km) |
| GB | 49352 | Dunfermline | West Lothian (WLN) | Fife (FIF) | 53100 | Q211950 (0.2 km) |
| GB | 49423 | Easton-in-Gordano | Bristol (BST) | North Somerset (NSM) | 4824 | Q3895750 (0.2 km) |
| GB | 49456 | Ellesmere Port | Wirral (WRL) | Cheshire West and Chester (CHW) | 61090 | Q1011600 (0.3 km) |
| GB | 49580 | Fochriw | Merthyr Tydfil (MTY) | Caerphilly (CAY) | 1250 | Q8564160 (0.1 km) |
| GB | 49613 | Frodsham | Warrington (WRT) | Cheshire West and Chester (CHW) | 9339 | Q2464851 (0.2 km) |
| GB | 49768 | Gunnislake | Plymouth (PLY) | Cornwall (CON) | 4044 | Q5619265 (0.0 km) |
| GB | 49778 | Hagley | Sandwell (SAW) | Worcestershire (WOR) | 7239 | Q1009859 (0.7 km) |
| GB | 49854 | Haworth | Calderdale (CLD) | Bradford (BRD) | 6379 | Q384570 (0.5 km) |
| GB | 49931 | High Valleyfield | Falkirk (FAL) | Fife (FIF) | 2280 | Q50355626 (0.0 km) |
| GB | 50062 | Inverkeithing | West Lothian (WLN) | Fife (FIF) | 4890 | Q1010422 (0.8 km) |
| GB | 50110 | Kelty | Clackmannanshire (CLK) | Fife (FIF) | 6730 | Q1010156 (0.2 km) |
| GB | 50159 | Kincardine | Falkirk (FAL) | Fife (FIF) | 2750 | Q1011221 (0.1 km) |
| GB | 50163 | Kinghorn | Edinburgh (EDH) | Fife (FIF) | 2840 | Q1010266 (0.4 km) |
| GB | 50202 | Kirkcaldy | Edinburgh (EDH) | Fife (FIF) | 50010 | Q691685 (0.8 km) |
| GB | 50239 | Landrake | Plymouth (PLY) | Cornwall (CON) | 1115 | Q11752791 (0.0 km) |
| GB | 50304 | Limekilns | West Lothian (WLN) | Fife (FIF) | 1410 | Q1011954 (0.6 km) |
| GB | 50377 | Lochgelly | Edinburgh (EDH) | Fife (FIF) | 7320 | Q3835992 (0.1 km) |
| GB | 50490 | Marazion | Isles of Scilly (IOS) | Cornwall (CON) | 1483 | Q1892416 (0.1 km) |
| GB | 50552 | Meriden | Coventry (COV) | Solihull (SOL) | 1753 | Q1747363 (0.4 km) |
| GB | 50697 | New Tredegar | Blaenau Gwent (BGW) | Caerphilly (CAY) | 4650 | Q3402398 (0.4 km) |
| GB | 50723 | Newport-on-Tay | Dundee (DND) | Fife (FIF) | 4310 | Q508190 (0.3 km) |
| GB | 50762 | North Queensferry | West Lothian (WLN) | Fife (FIF) | 1060 | Q1009725 (0.3 km) |
| GB | 50782 | Northwich | Warrington (WRT) | Cheshire West and Chester (CHW) | 47421 | Q2009813 (0.2 km) |
| GB | 50794 | Oakley | Clackmannanshire (CLK) | Fife (FIF) | 2260 | Q3305082 (1.6 km) |
| GB | 50839 | Oxenhope | Calderdale (CLD) | Bradford (BRD) | 1872 | Q2090507 (0.0 km) |
| GB | 50894 | Penzance | Isles of Scilly (IOS) | Cornwall (CON) | 20734 | Q208209 (0.3 km) |
| GB | 51004 | Purfleet | Bexley (BEX) | Thurrock (THR) |  | Q1972020 (0.7 km) |
| GB | 51052 | Redditch | Solihull (SOL) | Worcestershire (WOR) | 81919 | Q865716 (0.2 km) |
| GB | 51075 | Rhymney | Merthyr Tydfil (MTY) | Caerphilly (CAY) | 8545 | Q3401116 (0.2 km) |
| GB | 51104 | Romsley | Sandwell (SAW) | Worcestershire (WOR) | 1642 | Q7363330 (0.8 km) |
| GB | 51114 | Rosyth | West Lothian (WLN) | Fife (FIF) | 13780 | Q376329 (0.5 km) |
| GB | 51152 | Ryde | Portsmouth (POR) | Isle of Wight (IOW) | 24100 | Q776556 (0.3 km) |
| GB | 51183 | Saline | Clackmannanshire (CLK) | Fife (FIF) | 1080 | Q7404674 (0.3 km) |
| GB | 51186 | Saltash | Plymouth (PLY) | Cornwall (CON) | 16288 | Q1994597 (0.9 km) |
| GB | 51201 | Saughall | Wirral (WRL) | Cheshire West and Chester (CHW) | 3009 | Q2134251 (0.4 km) |
| GB | 51227 | Seaview | Portsmouth (POR) | Isle of Wight (IOW) | 2337 | Q7442238 (0.2 km) |
| GB | 51363 | South Ockendon | Havering (HAV) | Thurrock (THR) | 22442 | Q747456 (1.6 km) |
| GB | 51398 | St Ives | Isles of Scilly (IOS) | Cornwall (CON) | 9966 | Q724182 (0.6 km) |
| GB | 51404 | St. Helens | Portsmouth (POR) | Isle of Wight (IOW) | 1213 | Q1860807 (0.1 km) |
| GB | 51566 | Tayport | Dundee (DND) | Fife (FIF) | 3810 | Q1010148 (0.0 km) |
| GB | 51656 | Townhill | West Lothian (WLN) | Fife (FIF) | 1180 | Q7830119 (0.7 km) |
| GB | 51668 | Treuddyn | Wrexham (WRX) | Flintshire (FLN) | 1687 | Q7838896 (0.2 km) |
| GB | 51732 | Wallasey | Liverpool (LIV) | Wirral (WRL) | 60284 | Q780923 (0.0 km) |
| GB | 51779 | Weaverham | Warrington (WRT) | Cheshire West and Chester (CHW) | 6488 | Q7978376 (0.3 km) |
| GB | 51896 | Wideopen | Dudley (DUD) | North Tyneside (NTY) | 8976 | Q9372539 (0.5 km) |
| GR | 154219 | Tempi | Central Greece (H) | Thessaly (E) | 51 | Q1231770 (3.7 km) |
| GR | 154220 | Tyrnavos | Central Greece (H) | Thessaly (E) | 10027 | Q24251225 (4.6 km) |
| GR | 154229 | Farkadona | Central Greece (H) | Thessaly (E) | 1829 | Q786461 (1.1 km) |
| MX | 68982 | Chaparaco | Estado de México (MEX) | Michoacán de Ocampo (MIC) | 2808 | Q61269629 (0.1 km) |
| MX | 74086 | San Martín | Estado de México (MEX) | Michoacán de Ocampo (MIC) | 533 | Q20293526 (0.6 km) |
| NO | 79574 | Sætre | Buskerud (33) | Akershus (32) | 3009 | Q2440843 (0.6 km) |
| NO | 79685 | Åros | Buskerud (33) | Akershus (32) | 1142 | Q1873950 (0.2 km) |
| RS | 97143 | Aleksandrovo | Nišava (20) | Central Banat (02) | 3061 | Q848667 (0.1 km) |
| RS | 97201 | Dublje | Pomoravlje (13) | Mačva (08) | 3558 | Q3040542 (0.0 km) |
| RS | 97231 | Jarebice | Raška (18) | Mačva (08) | 1549 | Q2435677 (0.9 km) |
| RS | 97245 | Klenje | Braničevo (11) | Mačva (08) | 3653 | Q2722401 (0.1 km) |
| RS | 97259 | Krivaja | North Bačka (01) | Mačva (08) | 1296 | Q2736657 (1.0 km) |
| RU | 98320 | Dorogomilovo | Moscow (MOS) | Moscow (MOW) | 75669 | Q2358875 (2.0 km) |
| RU | 98754 | Izmaylovo | Moscow (MOS) | Moscow (MOW) | 108666 | Q4198639 (2.6 km) |
| RU | 99008 | Khoroshëvo-Mnevniki | Moscow (MOS) | Moscow (MOW) | 182497 | Q630277 (0.8 km) |
| RU | 99166 | Kommunarka | Moscow (MOS) | Moscow (MOW) | 5223 | Q1780477 (0.0 km) |

### Added after the independent review
The review found all 82 correct (OpenStreetMap reverse lookup plus each record's Wikidata chain) and five more of the
same kind, now moved; it also moved one point:

| Country | id | City | Was | Now | Note |
|---|---|---|---|---|---|
| GB | 51399 | St Just | Isles of Scilly | Cornwall | St Just in Penwith, on the mainland; its Wikidata ID is St Ives' (#1641) |
| GB | 51012 | Queensferry | West Lothian | Edinburgh | South Queensferry, in the City of Edinburgh council area |
| MX | 75197 | Tamándaro | Estado de México | Michoacán de Ocampo | in Jacona; own Wikidata item agrees |
| NO | 79240 | Hurum | Buskerud | Akershus | in Asker since 2020, like Sætre and Åros; its Wikidata item is the former municipality, which was in Buskerud |
| NO | 79471 | Røyken | Buskerud | Akershus | as Hurum |
| GB | 48296 | Ashton in Makerfield | (Wigan, above) | — | point moved from Old Boston, Haydock (St Helens) to the town centre, Q2557991's (53.487, −2.641) |

### Later additions checked against the 2019 import
Records added after the 2019 import were compared with their ten nearest 2019 records; where most of those lie in
another state, the record's own Wikidata item (same name, within 5 km) decided. Most such records are filed
correctly (the 2019 import simply lacks some areas, e.g. Ohio and Mureș). Five were not, and move:

| Country | id | City | Was | Now | Evidence |
|---|---|---|---|---|---|
| IN | 147448 | Bhimtal | Uttar Pradesh | Uttarakhand | Nainital district; own Wikidata item Q795774 |
| IN | 147692 | Bagewadi | Maharashtra | Karnataka | Belagavi district; own Wikidata item Q4841558 |
| MX | 142385 | El Colomo | Jalisco | Nayarit | Bahía de Banderas; own Wikidata item Q28102158 |
| PK | 143778 | Umerkot | Punjab | Sindh | Umerkot District; own Wikidata item Q2625910 |
| UY | 153693 | Barra de Carrasco | Montevideo | Canelones | Ciudad de la Costa; own Wikidata item Q808781. Point moved from Carrasco, Montevideo (−34.884, −56.047) to Q808781's (−34.869511, −56.028058) |

Also found: moving *Farkadona* (154229) puts it 1.1 km from record 52599 *Farkadóna* in Thessaly, the same place; it
waits for the duplicate policy. Four other records carry these records' Wikidata IDs by copy-forward (#1641).

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/{GB,GR,IN,MX,NO,PK,RS,RU,UY}.json` — `state_id` and `state_code` on 92 records; coordinates on 1

## States with a wrong or missing Wikidata ID

**277 states** get a corrected `wikiDataId`: 276 the right Wikidata item (252 whose item carries the state's own
ISO 3166-2 code, P300, and 24 matched another way: Estonian, Puerto Rico and Icelandic municipality items and the
Chatham Islands Territory) and one wrong ID removed (Port-Hercule, below). 203 pointed to the wrong item and 74 had none. Many wrong IDs were unrelated things: Icelandic municipalities pointed to The Knesset, bird and mollusc species
and *OK Computer*; Estonian ones to a Vuelta a España stage and a girls' college in India; São Tomé's districts to the
Seal of North Dakota and the Lisbon Oceanarium; Ceuta to Tricerro in Italy; Melilla to George II. Others pointed to a
related place: Spanish provinces to their autonomous community or capital city, British unitary authorities to their
town, Italian metropolitan cities to another one (Bologna had Milan's, Cagliari Naples', Florence Turin's).

### How they were found
Wikidata's ISO 3166-2 code (P300, current statements only) was read for all items that have one: 5,273 codes. Each
CSC state's `iso3166_2` was looked up. 4,634 states already carry the item with their code. 271 carry another item or none; for 266 of them exactly one
current item has their code, and those are the candidates below.

### Which were changed
| Set | States |
|---|---:|
| The ISO-coded item's name matches the state's name; CSC's item has no ISO code of the same country | 215 |
| CSC's item carries another code of the same country: swapped pairs (Mureș/Maramureș, Buenos Aires city/province, Lankaran city/district) and provinces carrying their community's ID | 26 |
| Names differ only in form (e.g. Seville → Seville Province, Ad Dali' → Dhale Governorate); checked by hand | 13 |
| Estonia's EE-430/EE-431: CSC had the two codes the wrong way round, so these follow the name (and the codes are swapped, below) | 2 |

Not changed:
- **Algeria (7):** CSC's IDs are right, but its ISO codes for the 2019 provinces are shifted (El M'ghair is DZ-57, not
  DZ-49). Fixing codes changes `state_code` for their cities, so it waits for a decision in #1643.
- **Rhône (FR-69):** the ISO-coded item is the post-2015 "departmental district"; CSC's item is kept.
- **Bikini & Kili, Woqooyi Galbeed:** the ISO-coded items don't clearly match. 395 more codes have no Wikidata item.

States by country: BD 63, EE 39, IS 37, ES 32, IT 13, MC 10, ST 7, ID 6, GB 6, LT 6, AZ 5, CD 4, IN 4, BS 3, TO 3, PR 3, ME 3, CA 2, YE 2, AR 2, RO 2, MA 2, ET 2, DO 2, KE 1, RW 1, SC 1, PH 1, BE 1, KI 1, CI 1, RS 1, NZ 1, LV 1, CZ 1, TZ 1, FR 1, AF 1, AO 1, MD 1, PE 1, MK 1, TT 1.

### After the independent review
The review found all 256 correct or better than before (250 correct, 6 arguable) and prompted these changes:
- **Municipality items instead of the town:** the ISO-coded items for five Icelandic municipalities are the towns, so
  those states now carry the municipality items (Akureyrarbær, Hafnarfjarðarkaupstaður, Kópavogsbær, Garðabær,
  Vestmannaeyjabær). The Chatham Islands carry Chatham Islands Territory (the territorial authority), not the
  archipelago.
- **Five more ISO matches** that the first pass missed: Akranes, Bolungarvík (IS), Herceg Novi (ME), Ituri (CD) and
  Moore's Island (BS).
- **Estonia's EE-430 and EE-431:** ISO, the Estonian EHAK codes and Wikidata agree that EE-430 is Lääneranna and EE-431
  Lääne-Harju. CSC had them the other way round, so the two states' `iso2`/`iso3166_2` are swapped. No city is
  filed under either.

The counts of Wikidata codes above depend on the day and on which statements count (best rank or not); the review
got 5,228–5,361 codes. Still to do: about 28 Icelandic states whose ISO codes have no Wikidata item still carry
unrelated IDs, and some `type` fields no longer fit (Lankaran city and district are swapped; Dorset is now a
unitary authority).

### Found by checking state points
With the corrected IDs, each state's point was compared with its Wikidata item's point. 16 more states whose ISO
codes have no Wikidata item turned out to carry an unrelated ID, placing them thousands of km away: three Puerto
Rico municipalities (Florida carried the US state, Río Grande a Colorado county, San Sebastián the Spanish city)
now carry the municipality items that #1644 gives their cities, and 13 Estonian municipalities (items in Rome,
Brittany, Madrid and elsewhere) carry the municipality item with their EHAK code (P1140), the "City" item for the
urban municipalities.

| Country | ISO 3166-2 | State | Was | Now |
|---|---|---|---|---|
| EE | EE-184 | Haapsalu | Q193724 | Q43281004 (Haapsalu City) |
| EE | EE-296 | Keila | Q999376 | Q23890555 (Keila City) |
| EE | EE-424 | Loksa | Q749031 | Q23890528 (Loksa City) |
| EE | EE-503 | Märjamaa | Q2627820 | Q44848112 (Märjamaa Rural Municipality) |
| EE | EE-528 | Noo | Q2627825 | Q1020142 (Nõo Rural Municipality) |
| EE | EE-567 | Paide | Q193797 | Q44792192 (Paide City) |
| EE | EE-661 | Rakvere | Q193808 | Q44857261 (Rakvere Rural Municipality) |
| EE | EE-663 | Rakvere | Q193808 | Q23890468 (Rakvere City) |
| EE | EE-732 | Setomaa | Q15732448 | Q42900601 (Setomaa Rural Municipality) |
| EE | EE-855 | Valga | Q2627988 | Q42846054 (Valga Rural Municipality) |
| EE | EE-897 | Viljandi | Q193832 | Q23890459 (Viljandi City) |
| EE | EE-899 | Viljandi | Q193832 | Q15100022 (Viljandi Rural Municipality) |
| EE | EE-907 | Vormsi | Q665175 | Q426207 (Vormsi Rural Municipality) |
| PR | PR-054 | Florida | Q812 | Q2271950 (Florida, Puerto Rico) |
| PR | PR-119 | Río Grande | Q160636 | Q979996 (Río Grande, Puerto Rico) |
| PR | PR-131 | San Sebastián | Q10313 | Q2413209 (San Sebastián, Puerto Rico) |

### Fix
Only `wikiDataId` changes, on 277 states, plus `iso2`/`iso3166_2` on the two Estonian states.

Scope notes from the review (not changed): EHAK codes are matched as Wikidata records them, which for Märjamaa
(0503, now 0502) and Valga (0855, now 0857) are the pre-reform codes; Jõhvi's item is the 2005–2025 municipality
(its successor is Q136536093); Islas Baleares (ES-PM) carries the historical province item, which matches its ISO
code, not the autonomous community (ES-IB); Saint-Roman's item is the former quarter, replaced by La Rousse in 2012.
The ISO codes themselves are unchanged.

| Country | ISO 3166-2 | State | Was | Now |
|---|---|---|---|---|
| AF | AF-WAR | Wardak | Q171366 (Idaea dimidiata) | Q183056 (Maidan Wardak Province) |
| AO | AO-NAM | Namibe | Q214246 (Georg Schories) | Q216819 (Namibe Province) |
| AR | AR-B | Buenos Aires | Q1486 (Buenos Aires) | Q44754 (Buenos Aires Province) |
| AR | AR-C | Autonomous City of Buenos Aires | Q44754 (Buenos Aires Province) | Q1486 (Buenos Aires) |
| AZ | AZ-LA | Lankaran | Q269986 (Lankaran District) | Q228811 (Lankaran) |
| AZ | AZ-LAN | Lankaran | Q228811 (Lankaran) | Q269986 (Lankaran District) |
| AZ | AZ-NA | Naftalan | Q202354 (Thomas Eboli) | Q21979624 (Naftalan) |
| AZ | AZ-NV | Nakhchivan | Q156203 (Bild) | Q230104 (Nakhchivan) |
| AZ | AZ-XA | Khankendi | Q80415 (Artur Grigorian) | Q129352 (Khankendi) |
| BD | BD-01 | Bandarban | — | Q806273 (Bandarban District) |
| BD | BD-02 | Barguna | — | Q808172 (Barguna District) |
| BD | BD-03 | Bogura | — | Q2039066 (Bogura District) |
| BD | BD-04 | Brahmanbaria | — | Q897330 (Brahmanbaria District) |
| BD | BD-05 | Bagerhat | — | Q2344861 (Bagerhat District) |
| BD | BD-06 | Barishal | — | Q1763301 (Barishal District) |
| BD | BD-07 | Bhola | — | Q855042 (Bhola District) |
| BD | BD-08 | Cumilla | — | Q1480778 (Cumilla District) |
| BD | BD-09 | Chandpur | — | Q1429697 (Chandpur District) |
| BD | BD-10 | Chattogram | — | Q1074991 (Chattogram District) |
| BD | BD-11 | Cox's Bazar | — | Q1122278 (Cox's Bazar District) |
| BD | BD-12 | Chuadanga | — | Q2094570 (Chuadanga District) |
| BD | BD-13 | Dhaka | — | Q1850485 (Dhaka District) |
| BD | BD-14 | Dinajpur | — | Q1985120 (Dinajpur District) |
| BD | BD-15 | Faridpur | — | Q2093552 (Faridpur District) |
| BD | BD-16 | Feni | — | Q1404741 (Feni District) |
| BD | BD-17 | Gopalganj | — | Q1537813 (Gopalganj District) |
| BD | BD-18 | Gazipur | — | Q2094101 (Gazipur District) |
| BD | BD-19 | Gaibandha | — | Q2344595 (Gaibandha District) |
| BD | BD-20 | Habiganj | — | Q1438974 (Habiganj District) |
| BD | BD-21 | Jamalpur | — | Q2039306 (Jamalpur District) |
| BD | BD-22 | Jashore | — | Q1862981 (Jashore District) |
| BD | BD-23 | Jhenaidah | — | Q2188750 (Jhenaidah District) |
| BD | BD-24 | Joypurhat | — | Q2348146 (Joypurhat District) |
| BD | BD-25 | Jhalakathi | — | Q2093327 (Jhalokati District) |
| BD | BD-26 | Kishoreganj | — | Q2344833 (Kishoreganj District) |
| BD | BD-27 | Khulna | — | Q2093344 (Khulna District) |
| BD | BD-28 | Kurigram | — | Q2348751 (Kurigram District) |
| BD | BD-29 | Khagrachhari | — | Q1429685 (Khagrachari District) |
| BD | BD-31 | Lakshmipur | — | Q1550252 (Lakshmipur District) |
| BD | BD-32 | Lalmonirhat | — | Q2373734 (Lalmonirhat District) |
| BD | BD-33 | Manikganj | — | Q2024719 (Manikganj District) |
| BD | BD-34 | Mymensingh | — | Q1429976 (Mymensingh District) |
| BD | BD-35 | Munshiganj | — | Q1990519 (Munshiganj District) |
| BD | BD-36 | Madaripur | — | Q928836 (Madaripur District) |
| BD | BD-37 | Magura | — | Q2039085 (Magura District) |
| BD | BD-38 | Moulvibazar | — | Q281435 (Moulvibazar District) |
| BD | BD-39 | Meherpur | — | Q1474206 (Meherpur District) |
| BD | BD-40 | Narayanganj | — | Q2208354 (Narayanganj District) |
| BD | BD-41 | Netrakona | — | Q2344966 (Netrokona District) |
| BD | BD-42 | Narsingdi | — | Q2042638 (Narsingdi District) |
| BD | BD-43 | Narail | — | Q1550260 (Narail District) |
| BD | BD-44 | Natore | — | Q2093361 (Natore District) |
| BD | BD-45 | Chapai Nawabganj | — | Q46043 (Chapai Nawabganj) |
| BD | BD-46 | Nilphamari | — | Q2188627 (Nilphamari District) |
| BD | BD-47 | Noakhali | — | Q68585 (Noakhali District) |
| BD | BD-48 | Naogaon | — | Q2094277 (Naogaon District) |
| BD | BD-49 | Pabna | — | Q1083505 (Pabna District) |
| BD | BD-50 | Pirojpur | — | Q609190 (Pirojpur District) |
| BD | BD-51 | Patuakhali | — | Q1429761 (Patuakhali District) |
| BD | BD-52 | Panchagarh | — | Q2367822 (Panchagarh District) |
| BD | BD-53 | Rajbari | — | Q2348762 (Rajbari District) |
| BD | BD-54 | Rajshahi | — | Q2344697 (Rajshahi District) |
| BD | BD-55 | Rangpur | — | Q2344570 (Rangpur District) |
| BD | BD-56 | Rangamati | — | Q2121686 (Rangamati District) |
| BD | BD-57 | Sherpur | — | Q2039314 (Sherpur District) |
| BD | BD-58 | Satkhira | — | Q1233680 (Satkhira District) |
| BD | BD-59 | Sirajganj | — | Q2429432 (Sirajganj District) |
| BD | BD-60 | Sylhet | — | Q2093352 (Sylhet District) |
| BD | BD-61 | Sunamganj | — | Q2093388 (Sunamganj District) |
| BD | BD-62 | Shariatpur | — | Q253007 (Shariatpur District) |
| BD | BD-63 | Tangail | — | Q952184 (Tangail District) |
| BD | BD-64 | Thakurgaon | — | Q2367825 (Thakurgaon District) |
| BE | BE-VLG | Flanders | Q234 (Flanders) | Q9337 (Flemish Region) |
| BS | BS-AK | Acklins | Q341919 (Acklins) | Q122687952 (Acklins) |
| BS | BS-MI | Moore's Island | Q2702345 | Q21713445 (Moore's Island District) |
| BS | BS-NP | New Providence | Q858513 (New Providence) | Q3339000 (New Providence) |
| CA | CA-BC | British Columbia | Q1974 (British Columbia) | Q1973 (British Columbia) |
| CA | CA-PE | Prince Edward Island | Q1979 (Prince Edward Island) | Q1978 (Prince Edward Island) |
| CD | CD-BC | Kongo Central | Q130588 (Kongo Central) | Q1043494 (Kongo Central) |
| CD | CD-IT | Ituri | Q750659 | Q24909562 (Ituri Province) |
| CD | CD-KE | Kasaï Oriental | Q80953 (Kasaï-Oriental) | Q917992 (Kasai-Oriental) |
| CD | CD-KG | Kwango | Q757095 (Kwango District) | Q24205498 (Kwango Province) |
| CI | CI-SV | Savanes | Q853460 (Savanes Region) | Q21002161 (Savanes District) |
| CZ | CZ-205 | Kutná Hora | Q155975 (Kutná Hora) | Q268426 (Kutná Hora District) |
| DO | DO-40 | Ozama | — | Q27922453 (Ozama) |
| DO | DO-41 | Valdesia | — | Q2671273 (Valdesia) |
| EE | EE-130 | Alutaguse | Q15732413 (Pârjol) | Q42892510 (Alutaguse Rural Municipality) |
| EE | EE-141 | Anija | Q2627549 (2007 Vuelta a España, Stage 4) | Q44491324 (Anija Rural Municipality) |
| EE | EE-142 | Antsla | Q2627562 | Q44491738 (Antsla Rural Municipality) |
| EE | EE-171 | Elva | Q2627638 (Mozhaysk Municipal Okrug) | Q42811297 (Elva Rural Municipality) |
| EE | EE-205 | Hiiumaa | Q15732426 (Plesiopontonia) | Q31277892 (Hiiumaa Rural Municipality) |
| EE | EE-214 | Häädemeeste | Q2627678 (Albardakade) | Q44511402 (Häädemeeste Rural Municipality) |
| EE | EE-245 | Joelähtme | Q2627704 (Mochau) | Q993036 (Jõelähtme Rural Municipality) |
| EE | EE-247 | Jõgeva | Q2627707 (10617 Takumi) | Q44624256 (Jõgeva Rural Municipality) |
| EE | EE-251 | Jõhvi | Q2627709 (Noordstraat) | Q1640282 (Jõhvi Rural Municipality) |
| EE | EE-255 | Järva | Q15732430 (Gokhale Memorial Girls' College) | Q42808650 (Järva Rural Municipality) |
| EE | EE-321 | Kohtla-Järve | Q193761 | Q23890605 (Kohtla-Järve City, urban municipality; EHAK 0321) |
| EE | EE-430 | Lääneranna | Q15732433 (Claudio Pätz) | Q31273628 (Lääneranna Rural Municipality) |
| EE | EE-431 | Lääne-Harju | Q15732432 (Anavra, Karditsa) | Q42309166 (Lääne-Harju Rural Municipality) |
| EE | EE-441 | Lääne-Nigula | Q2627784 (1968 Red Square demonstration) | Q43281154 (Lääne-Nigula Rural Municipality) |
| EE | EE-442 | Lüganuse | Q2627795 (Iselma endroedyyoungai) | Q44826366 (Lüganuse Rural Municipality) |
| EE | EE-514 | Narva-Jõesuu | Q995303 | Q43266354 (Narva-Jõesuu City) |
| EE | EE-557 | Otepää | Q658072 (Pishchalskoye peat narrow gauge railway) | Q44509132 (Otepää Rural Municipality) |
| EE | EE-586 | Peipsiääre | Q15732441 (Avram Iancu) | Q44490248 (Peipsiääre Rural Municipality) |
| EE | EE-615 | Põhja-Sakala | Q15732443 (Velimachi) | Q31273591 (Põhja-Sakala Rural Municipality) |
| EE | EE-618 | Poltsamaa | Q2627867 (Nokia 6210) | Q44854656 (Põltsamaa Rural Municipality) |
| EE | EE-638 | Põhja-Pärnu | Q2627856 | Q42329911 (Põhja-Pärnumaa Rural Municipality) |
| EE | EE-698 | Rõuge | Q2627908 | Q44511803 (Rõuge Rural Municipality) |
| EE | EE-735 | Sillamäe | Q193814 (Hīnayāna) | Q23890602 (Sillamäe City, urban municipality) |
| EE | EE-809 | Tori | Q2627966 (Juris Kalniņš) | Q44492102 (Tori Rural Municipality) |
| EE | EE-834 | Türi | Q2627979 (Shaktipat) | Q44818587 (Türi Rural Municipality) |
| EE | EE-928 | Väike-Maarja | Q2628018 (Phaisurellops rugifrons) | Q1020183 (Väike-Maarja Rural Municipality) |
| ES | ES-A | Alicante | Q11959 (Alicante) | Q54936 (Province of Alicante) |
| ES | ES-AL | Almeria | Q10400 (Almería) | Q81802 (Almería Province) |
| ES | ES-B | Barcelona | Q1492 (Barcelona) | Q81949 (Barcelona Province) |
| ES | ES-C | A Coruña | Q8757 (A Coruña) | Q82119 (A Coruña Province) |
| ES | ES-CA | Cádiz | Q15682 (Cádiz) | Q81978 (Cádiz Province) |
| ES | ES-CE | Ceuta | Q25212 (Tricerro) | Q5823 (Ceuta) |
| ES | ES-CO | Córdoba | Q5818 (Córdoba) | Q81972 (Córdoba Province) |
| ES | ES-CR | Ciudad Real | Q15093 (Ciudad Real) | Q54932 (Province of Ciudad Real) |
| ES | ES-GC | Las Palmas | Q5813 (Canary Islands) | Q95080 (Las Palmas) |
| ES | ES-GI | Girona | Q7038 (Girona) | Q7194 (Girona) |
| ES | ES-GR | Granada | Q8810 (Granada) | Q82142 (Province of Granada) |
| ES | ES-GU | Guadalajara | Q11953 (Guadalajara) | Q54925 (Guadalajara Province) |
| ES | ES-H | Huelva | Q12246 (Huelva) | Q95015 (Province of Huelva) |
| ES | ES-HU | Huesca | Q4040 (Aragon) | Q55182 (Huesca Province) |
| ES | ES-J | Jaén | Q15681 (Jaén) | Q95025 (Jaén Province) |
| ES | ES-L | Lleida | Q15090 (Lleida) | Q13904 (Province of Lleida) |
| ES | ES-LU | Lugo | Q11125 (Lugo) | Q95027 (Lugo Province) |
| ES | ES-M | Madrid | Q5756 (Community of Madrid) | Q24004405 (Madrid Province) |
| ES | ES-MA | Málaga | Q8851 (Málaga) | Q95028 (Málaga Province) |
| ES | ES-ML | Melilla | Q131981 (George II of Great Britain) | Q5831 (Melilla) |
| ES | ES-MU | Murcia | Q5772 (Region of Murcia) | Q24271891 (Murcia Province) |
| ES | ES-NA | Navarra | Q4018 (Navarre) | Q24004404 (Province of Navarre) |
| ES | ES-O | Asturias | Q3934 (Asturias) | Q24004403 (Province of Asturias) |
| ES | ES-PM | Islas Baleares | Q5765 (Balearic Islands) | Q107356469 (Balearic Islands) |
| ES | ES-S | Cantabria | Q3946 (Cantabria) | Q31920747 (Cantabria Province) |
| ES | ES-SE | Sevilla | Q8717 (Seville) | Q95088 (Seville Province) |
| ES | ES-T | Tarragona | Q15088 (Tarragona) | Q98392 (Province of Tarragona) |
| ES | ES-TE | Teruel | Q14336 (Teruel) | Q54955 (Teruel Province) |
| ES | ES-TF | Santa Cruz de Tenerife | Q14328 (Santa Cruz de Tenerife) | Q99976 (Santa Cruz de Tenerife Province) |
| ES | ES-TO | Toledo | Q5836 (Toledo) | Q54929 (Toledo Province) |
| ES | ES-V | Valencia | Q5720 (Valencian Community) | Q54939 (Province of Valencia) |
| ES | ES-Z | Zaragoza | Q10305 (Zaragoza) | Q55180 (Zaragoza Province) |
| ET | ET-SI | Sidama | Q30107894 | Q1070673 (Sidama Region) |
| ET | ET-SW | Southwest Ethiopia Peoples | Q105085548 (Yoni Berkovits) | Q109788993 (Southwest Ethiopia Regional State) |
| FR | FR-42 | Loire | Q16994 (Pays de la Loire) | Q12569 (Loire) |
| GB | GB-BPL | Blackpool | Q170377 (Blackpool) | Q20989106 (Blackpool) |
| GB | GB-DND | Dundee | Q123709 (Dundee) | Q2357511 (Dundee City) |
| GB | GB-DOR | Dorset | Q21694711 (Dorset) | Q55231693 (Dorset) |
| GB | GB-MDB | Middlesbrough | Q171866 (Middlesbrough) | Q2673020 (Middlesbrough) |
| GB | GB-NWP | Newport | Q11294004 (Newport) | Q5283458 (Newport) |
| GB | GB-SOS | Southend-on-Sea | Q203995 (Southend-on-Sea) | Q21487155 (Southend-on-Sea) |
| ID | ID-JW | Jawa | Q3757 (Java) | Q124377739 (Jawa) |
| ID | ID-KB | Kalimantan Barat | Q3795 (Kalimantan) | Q3916 (West Kalimantan) |
| ID | ID-ML | Maluku | Q3827 (Maluku Islands) | Q141280973 (Maluku) |
| ID | ID-NU | Nusa Tenggara | Q3803 (Lesser Sunda Islands) | Q141280974 (Nusa Tenggara) |
| ID | ID-SL | Sulawesi | Q3812 (Sulawesi) | Q141280976 (Sulawesi) |
| ID | ID-SM | Sumatera | Q3492 (Sumatra) | Q141280977 (Sumatera) |
| IN | IN-CH | Chandigarh | Q43433 (Chandigarh) | Q120971341 (Chandigarh) |
| IN | IN-DH | Dadra and Nagar Haveli and Daman and Diu | Q66710 (Daman and Diu) | Q77997266 (Dadra and Nagar Haveli and Daman and Diu) |
| IN | IN-DL | Delhi | Q1353 (Delhi) | Q9357528 (National Capital Territory of Delhi) |
| IN | IN-JK | Jammu and Kashmir | Q1180 (Jammu and Kashmir) | Q66278313 (Jammu and Kashmir) |
| IS | IS-AKN | Akranes | Q203163 | Q2476720 (Akraneskaupstaður) |
| IS | IS-AKU | Akureyri | Q133396 (The Knesset) | Q4317203 (Akureyrarbær) |
| IS | IS-ARN | Árneshreppur | Q731910 (Giant kingfisher) | Q252238 (Árneshreppur) |
| IS | IS-ASA | Ásahreppur | Q731911 (Hypselodoris fontandraui) | Q252482 (Ásahreppur) |
| IS | IS-BLA | Bláskógabyggð | Q839959 (Stub-tailed Spadebill) | Q886944 (Bláskógabyggð) |
| IS | IS-BOG | Borgarbyggð | Q948607 (Kotex) | Q893528 (Borgarbyggð) |
| IS | IS-BOL | Bolungarvík | Q739842 | Q1798343 (Bolungarvíkurkaupstaður) |
| IS | IS-DAB | Dalabyggð | Q1158005 (Dallas Semiconductor) | Q1157787 (Dalabyggð) |
| IS | IS-DAV | Dalvíkurbyggð | Q1158009 (2012 Dallas Tennis Classic) | Q1158104 (Dalvíkurbyggð) |
| IS | IS-EOM | Eyja- og Miklaholtshreppur | Q1379862 (Heliodrom camp) | Q1385816 (Eyja- og Miklaholtshreppur) |
| IS | IS-EYF | Eyjafjarðarsveit | Q1379858 (Evangelical Lutheran Church in Baden) | Q510141 (Eyjafjarðarsveit) |
| IS | IS-FJD | Fjarðabyggð | Q1421198 | Q1146805 (Fjarðabyggð) |
| IS | IS-FJL | Fjallabyggð | Q1421195 (Highway M19) | Q729833 (Fjallabyggð) |
| IS | IS-FLA | Flóahreppur | Q1428698 (Flight operations quality assurance) | Q962730 (Flóahreppur) |
| IS | IS-FLR | Fljótsdalshreppur | Q1428695 (focal dystonia) | Q1429028 (Fljótsdalshreppur) |
| IS | IS-GAR | Garðabær | Q202996 (OK Computer) | Q27015626 (Garðabær) |
| IS | IS-GRN | Grindavík | Q212876 (Magnentius) | Q2796543 (Grindavíkurbær) |
| IS | IS-GRU | Grundarfjörður | Q1548758 (Großer Kornberg) | Q1019459 (Grundarfjarðarbær) |
| IS | IS-HAF | Hafnarfjörður | Q208045 (gold) | Q2238508 (Hafnarfjarðarkaupstaður) |
| IS | IS-HUG | Húnabyggð | Q1639015 (Bolivia Route 31) | Q112288159 (Húnabyggð) |
| IS | IS-HUV | Húnaþing vestra | Q1639016 (Mother Albania) | Q1652058 (Húnaþing vestra) |
| IS | IS-HVE | Hveragerði | Q212882 | Q1025701 (Hveragerðisbær) |
| IS | IS-KOP | Kópavogur | Q208042 (regression analysis) | Q27013397 (Kópavogsbær) |
| IS | IS-MUL | Múlaþing | Q2063295 (Paul Zollinger) | Q96776922 (Múlaþing) |
| IS | IS-RGE | Rangárþing eystra | Q2131208 (Mangora chicanna) | Q669991 (Rangárþing eystra) |
| IS | IS-RGY | Rangárþing ytra | Q2131209 (Kunstlinie Almere Flevoland) | Q540016 (Rangárþing ytra) |
| IS | IS-SDN | Suðurnesjabær | Q2368394 (Surbajny) | Q60297275 (Suðurnesjabær) |
| IS | IS-SDV | Súðavík | Q2371172 | Q60860400 (Súðavíkurhreppur) |
| IS | IS-SEL | Seltjarnarnes | Q208043 (Lar Gibbon) | Q214057 (Seltjarnarnes) |
| IS | IS-SFA | Árborg | Q731908 (Pop) | Q252205 (Sveitarfélagið Árborg) |
| IS | IS-SKR | Skagafjörður | Q2289057 (Colletes michenerianus) | Q1549436 (Skagafjörður) |
| IS | IS-SOL | Ölfus | Q2620321 (Xanthesma lucida) | Q297010 (Ölfus) |
| IS | IS-SSS | Skagaströnd | Q2289076 (1970 Singapore Open Badminton Championships) | Q1796734 (Sveitarfélagið Skagaströnd) |
| IS | IS-STR | Strandabyggð | Q2361008 (Bonnie Blue Flag) | Q979864 (Strandabyggð) |
| IS | IS-SVG | Vogar | Q208047 (1968 Tunnel Rats) | Q3482077 (Vogar) |
| IS | IS-TJO | Tjörneshreppur | Q2433113 (Florida State Road 817) | Q628888 (Tjörneshreppur) |
| IS | IS-VEM | Vestmannaeyjar | Q208048 (Band of Brothers) | Q9368476 (Vestmannaeyjabær) |
| IT | IT-BA | Bari | Q18684135 (Anthony Costello) | Q18241854 (Metropolitan City of Bari) |
| IT | IT-BO | Bologna | Q18288155 (Metropolitan City of Milan) | Q18288145 (Metropolitan City of Bologna) |
| IT | IT-CA | Cagliari | Q18241891 (Metropolitan City of Naples) | Q3622022 (Metropolitan City of Cagliari) |
| IT | IT-CT | Catania | Q18241870 (All My Ganstas) | Q20991246 (Metropolitan City of Catania) |
| IT | IT-FI | Florence | Q18288162 (Metropolitan City of Turin) | Q18288148 (Metropolitan City of Florence) |
| IT | IT-GE | Genoa | Q18288197 (Così per gioco) | Q18288152 (Metropolitan City of Genoa) |
| IT | IT-ME | Messina | Q18241892 (White Cross) | Q20991250 (Metropolitan City of Messina) |
| IT | IT-MI | Milan | Q18288187 (1982 in Yukon) | Q18288155 (Metropolitan City of Milan) |
| IT | IT-NA | Naples | Q18241895 | Q18241891 (Metropolitan City of Naples) |
| IT | IT-RC | Reggio Calabria | Q18241896 (Traian Bogdan) | Q3678586 (Metropolitan City of Reggio Calabria) |
| IT | IT-RM | Rome | Q18288203 (Francesco Cubeddu) | Q18288160 (Metropolitan City of Rome) |
| IT | IT-TN | Trentino | Q16290 (Star Trek: The Next Generation) | Q16289 (Trentino) |
| IT | IT-TO | Turin | Q18288204 (1984 in Newfoundland and Labrador) | Q18288162 (Metropolitan City of Turin) |
| KE | KE-30 | Nairobi City | Q3870 (Nairobi) | Q3335223 (Nairobi City County) |
| KI | KI-L | Line | Q55076234 (Line Islands) | Q31866835 (Line Islands) |
| LT | LT-03 | Alytus | Q3685407 (Alytus City Municipality) | Q769940 (Alytus District Municipality) |
| LT | LT-16 | Kaunas | Q928949 (Colorado Party) | Q1351722 (Kaunas District Municipality) |
| LT | LT-20 | Klaipėdos miestas | Q928918 (Industrial Canal) | Q16456513 (Klaipeda City Municipality) |
| LT | LT-32 | Panevėžio miestas | Q928992 (Hemiodontidae) | Q3685412 (Panevėžys City Municipality) |
| LT | LT-44 | Šiauliai | Q4993831 (Šiauliai City Municipality) | Q1417346 (Šiauliai District Municipality) |
| LT | LT-58 | Vilnius | Q928917 (Sony Ericsson K300i) | Q118903 (Vilnius District Municipality) |
| LV | LV-113 | Valmiera | Q108037 (Valmiera) | Q97233086 (Valmiera Municipality) |
| MA | MA-MOH | Mohammadia | Q647417 (Mohammedia) | Q1149096 (Mohammedia Prefecture) |
| MA | MA-RAB | Rabat | Q3551 (Rabat) | Q966104 (Rabat Prefecture) |
| MC | MC-GA | La Gare | — | Q13378488 (La Gare) |
| MC | MC-MA | Malbousquet | — | Q13378486 (Malbousquet) |
| MC | MC-MO | Monaco-Ville | Q55103 (Sant'Angelo dei Lombardi) | Q55115 (Monaco-Ville) |
| MC | MC-MU | Moulins | — | Q13378485 (Moulins) |
| MC | MC-PH | Port-Hercule | Q1416547 (financial plan) | — (removed; Q7230673 is the port, not the quarter, and no quarter item was verified) |
| MC | MC-SD | Sainte-Dévote | — | Q18635826 (Ravin de Sainte-Dévote) |
| MC | MC-SO | La Source | — | Q13378482 (La Source) |
| MC | MC-SP | Spélugues | — | Q13378480 (Spélugues) |
| MC | MC-SR | Saint-Roman | — | Q99324616 (Saint Roman) |
| MC | MC-VR | Vallon de la Rousse | — | Q13378479 (Vallon de la Rousse) |
| MD | MD-LE | Leova | Q862618 (Kungsholmen city district) | Q1826662 (Leova District) |
| ME | ME-08 | Herceg-Novi | Q187144 | Q3317366 (Herceg Novi Municipality) |
| ME | ME-24 | Tuzi | Q2656869 (Chirita) | Q12750439 (Tuzi Municipality) |
| ME | ME-25 | Zeta | Q25411815 | Q12750430 (Zeta Municipality) |
| MK | MK-303 | Debar | — | Q1344996 (Debar Municipality) |
| NZ | NZ-CIT | Chatham Islands | Q26882619 (Chatham Islands Council) | Q86771569 (Chatham Islands Territory) |
| PE | PE-LMA | Municipalidad Metropolitana de Lima | Q2868 (Lima) | Q579240 (Lima) |
| PH | PH-MGN | Maguindanao del Norte | Q13845 (Maguindanao) | Q114019739 (Maguindanao del Norte) |
| RO | RO-MM | Maramureș | Q190711 (Mureș County) | Q188813 (Maramureș County) |
| RO | RO-MS | Mureș | Q188813 (Maramureș County) | Q190711 (Mureș County) |
| RS | RS-00 | Belgrade | Q3711 (Belgrade) | Q2074197 (City of Belgrade) |
| RW | RW-01 | Kigali | Q167196 (City of Kigali) | Q3859 (Kigali) |
| SC | SC-15 | La Digue | Q581154 (La Digue) | Q1094917 (La Digue and Inner Islands) |
| ST | ST-01 | Água Grande | Q652808 | Q249742 (Água Grande) |
| ST | ST-02 | Cantagalo | Q652819 (Moerocles) | Q1033696 (Cantagalo) |
| ST | ST-03 | Caué | Q652823 (Seal of North Dakota) | Q1051692 (Caué) |
| ST | ST-04 | Lemba | Q652810 (Wilczków) | Q785367 (Lembá) |
| ST | ST-05 | Lobata | Q652816 (Most Wanted) | Q1139384 (Lobata) |
| ST | ST-06 | Mé-Zóchi | Q652812 (port authority) | Q1139407 (Mé-Zóchi) |
| ST | ST-P | Príncipe | Q652806 (Lisbon Oceanarium) | Q2366966 (Príncipe Autonomous Region) |
| TO | TO-01 | ʻEua | Q18472979 (Template:Nereids) | Q4533167 (ʻEua district) |
| TO | TO-02 | Haʻapai | Q10293470 (Haʻapai district) | Q4494291 (Haʻapai district) |
| TO | TO-05 | Vavaʻu | Q10389402 (Vava‘u) | Q4102091 (Vava‘u) |
| TT | TT-TOB | Tobago | Q128323 (Trinidad) | Q185111 (Tobago) |
| TZ | TZ-31 | Songwe | Q458382 (Mbeya Region) | Q25618976 (Songwe Region) |
| YE | YE-DA | Ad Dali' | Q241087 (Alda Merini) | Q328187 (Dhale Governorate) |
| YE | YE-SA | Amanat Al Asimah | Q2471 (Sanaa) | Q32130189 (Amanat al-Asimah Governorate) |

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/states/states.json` — `wikiDataId` on 277 states; `iso2`/`iso3166_2` on 2

## Philippine records filed under the wrong province

**1,785 Philippine records** (mostly barangays) move to the province they are in. Most were filed under a small
province far away, often the first of a region's provinces in alphabetical order: none of the 277 records filed under
Bataan was within 60 km of Bataan (they were in Cebu, Bohol and Negros); Abra held Pangasinan's barangays, Antique
those of Negros Occidental and Iloilo, Benguet those of Bukidnon. In 1,325 of them even the region was wrong. Both the
2019 import (ids 81xxx–85xxx, 1,026 moved) and a later batch (143xxx–146xxx, 759 moved) are affected.

### How they were verified
Two sources, both required:
1. **The record's own Wikidata item.** Every PH record has a `wikiDataId`. It counts only if it is the record's place:
   a label or alias equal to the record's name and a point within 5 km. Its current "located in" (P131) chain gives
   the CSC province (CSC's Philippine province IDs match their ISO 3166-2 codes).
2. **GeoNames.** The full Philippine dump's province codes were mapped to CSC provinces by majority vote of the
   records Wikidata verified (not of the filed provinces, which are unreliable here). At least 4 of the 5 nearest
   mapped places, or a same-named place within 3 km, must lie in the same province.

| Own Wikidata item (5,357 records) | Filed under a province | Filed under a region |
|---|---:|---:|
| Confirms the filed state | 363 | 835 |
| Names another state | 1860 | 105 |
| Not the record's place (copy-forward ID, #1641) | 1759 | 291 |
| No chain to a CSC state | 71 | 73 |

Of the 1,860 province-filed records Wikidata places elsewhere, 1,810 were confirmed by GeoNames,
22 were not, and 28 have no single province in their chain.
The region-filed records it places elsewhere were checked at region level: their chain's province lies in the filed
region for all but 5, which are held, so region-filed records keep their region.

### After the independent review
The review tested all 1,810 confirmed points against geoBoundaries' province polygons (NAMRIA/PSA 2020, with
Maguindanao split into del Norte and del Sur by municipality) and checked 238 with Nominatim: 1,763 correct,
42 wrong, 5 within 2 km of a border. The wrong ones come from **provinces that were split or created**, where
Wikidata and GeoNames both still carry the older unit, so the two sources agreed on the wrong answer:
- 15 Davao Occidental barangays were already filed correctly; they stay (Wikidata still places them in Davao del Sur).
- 18 records go to **Maguindanao del Sur**, not del Norte: their Wikidata item is in the old Maguindanao (Q13845),
  dissolved in 2022.
- 3 go to **Sarangani** (Glan, Malapatan), 2 to **Davao del Norte** (Samal, New Corella), 1 to **Guimaras**
  (Salvacion, Buenavista) and 1 to **Pangasinan** (Gueset), where the polygons and Nominatim agree.
- 10 are held at their current state: Osias (its point is in Bukidnon); Kalbugan and, found by the second review,
  Gocoton, Malingao, Manaulanan and Pedtad, barangays of the BARMM Special Geographic Area (the 2020 polygons and
  Wikidata still show them in Cotabato; PSA lists them under the SGA's municipalities), which CSC has no state for;
  and 4 records within about 1 km of the Sultan Kudarat–Maguindanao del Sur border.

So 1,785 records move, 1,760 as first confirmed and 25 to the province the polygons show.

Not in this PR: the 1,759 province-filed records whose Wikidata ID is another place's need a different
second source; the review sizes the remaining province-filed records outside their province at about 812.

### Fix
Only `state_id` and `state_code` change; all keep `Asia/Manila`.

| Filed under | Moved out |
|---|---:|
| Antique | 226 |
| Bataan | 207 |
| Agusan del Sur | 188 |
| Abra | 188 |
| Occidental Mindoro | 156 |
| Albay | 145 |
| Agusan del Norte | 132 |
| Benguet | 127 |
| Cagayan | 102 |
| Batanes | 76 |
| Oriental Mindoro | 71 |
| Bukidnon | 66 |
| Camarines Norte | 42 |
| Bulacan | 36 |
| Zamboanga Sibugay | 18 |
| 1 other provinces | 5 |

| Move (top 20 of 72 pairs) | Records |
|---|---:|
| Abra → Pangasinan | 134 |
| Antique → Negros Occidental | 106 |
| Bataan → Cebu | 91 |
| Benguet → Bukidnon | 68 |
| Agusan del Norte → Cagayan | 65 |
| Antique → Iloilo | 62 |
| Bataan → Bohol | 61 |
| Albay → Camarines Sur | 61 |
| Bataan → Negros Oriental | 55 |
| Occidental Mindoro → Batangas | 55 |
| Occidental Mindoro → Quezon | 50 |
| Agusan del Norte → Isabela | 50 |
| Agusan del Sur → Nueva Ecija | 48 |
| Bukidnon → Cotabato | 34 |
| Agusan del Sur → Tarlac | 38 |
| Batanes → Leyte | 37 |
| Agusan del Sur → Bulacan | 36 |
| Antique → Capiz | 35 |
| Cagayan → Sulu | 35 |
| Benguet → Misamis Oriental | 34 |
| other pairs | 630 |

<details>
<summary>All 1,785 records (id, name, was, now, own Wikidata ID)</summary>

| id | Name | Was | Now | Wikidata |
|---|---|---|---|---|
| 81126 | Abaca | Bataan | Bohol | Q31460863 |
| 81127 | Abaca | Antique | Iloilo | Q31460873 |
| 81128 | Abangay | Antique | Iloilo | Q31460921 |
| 81130 | Abilay | Antique | Iloilo | Q31461068 |
| 81131 | Abis | Bataan | Negros Oriental | Q31461082 |
| 81133 | Abra de Ilog | Oriental Mindoro | Occidental Mindoro | Q107454 |
| 81136 | Abucayan | Bataan | Bohol | Q31461262 |
| 81145 | Adela | Oriental Mindoro | Occidental Mindoro | Q31461749 |
| 81148 | Adtugan | Benguet | Bukidnon | Q31461879 |
| 81150 | Ag-ambulong | Antique | Capiz | Q31461951 |
| 81151 | Aga | Occidental Mindoro | Batangas | Q31461964 |
| 81152 | Aganan | Antique | Iloilo | Q31461988 |
| 81159 | Aglalana | Antique | Iloilo | Q31462180 |
| 81160 | Aglayan | Benguet | Bukidnon | Q31462192 |
| 81164 | Agos | Albay | Camarines Sur | Q31462329 |
| 81165 | Agpangi | Antique | Negros Occidental | Q31462354 |
| 81169 | Aguining | Bataan | Bohol | Q31462473 |
| 81170 | Aguisan | Antique | Negros Occidental | Q31462501 |
| 81171 | Agupit | Albay | Camarines Sur | Q31462526 |
| 81180 | Alacaygan | Antique | Negros Occidental | Q31462963 |
| 81181 | Alad | Oriental Mindoro | Romblon | Q31462988 |
| 81187 | Alangilan | Bataan | Negros Oriental | Q31463224 |
| 81188 | Alangilanan | Bataan | Negros Oriental | Q31463238 |
| 81189 | Alanib | Benguet | Bukidnon | Q31463252 |
| 81191 | Alayao | Albay | Camarines Norte | Q31463313 |
| 81193 | Alburquerque | Bataan | Bohol | Q404369 |
| 81206 | Algeciras | Oriental Mindoro | Palawan | Q5668216 |
| 81208 | Aliang | Occidental Mindoro | Cavite | Q31463963 |
| 81210 | Alibug | Oriental Mindoro | Occidental Mindoro | Q31464005 |
| 81211 | Alibunan | Antique | Iloilo | Q31464015 |
| 81212 | Alicante | Antique | Negros Occidental | Q31464026 |
| 81216 | Alijis | Antique | Negros Occidental | Q31464170 |
| 81218 | Alim | Antique | Negros Occidental | Q31464191 |
| 81220 | Alimono | Antique | Iloilo | Q31464249 |
| 81231 | Alpaco | Bataan | Cebu | Q31464869 |
| 81236 | Alugan | Batanes | Eastern Samar | Q31465087 |
| 81237 | Alupay | Occidental Mindoro | Batangas | Q31465112 |
| 81246 | Amdos | Bataan | Negros Oriental | Q31465525 |
| 81247 | Amio | Bataan | Negros Oriental | Q31465632 |
| 81270 | Ani-e | Benguet | Misamis Oriental | Q31466705 |
| 81274 | Anito | Batanes | Northern Samar | Q31466823 |
| 81275 | Anonang | Bataan | Cebu | Q31466932 |
| 81276 | Anopog | Bataan | Negros Oriental | Q31466943 |
| 81277 | Anoring | Antique | Iloilo | Q31466956 |
| 81279 | Antequera | Bataan | Bohol | Q404459 |
| 81288 | Anuling | Occidental Mindoro | Cavite | Q31467448 |
| 81290 | Apad | Albay | Camarines Sur | Q31467536 |
| 81296 | Aplaya | Benguet | Misamis Oriental | Q31467719 |
| 81297 | Aplaya | Occidental Mindoro | Laguna | Q31467732 |
| 81298 | Apoya | Bataan | Negros Oriental | Q31467878 |
| 81301 | Aquino | Antique | Aklan | Q31468026 |
| 81302 | Araal | Antique | Negros Occidental | Q31468038 |
| 81306 | Aranas Sur | Antique | Aklan | Q31468181 |
| 81307 | Aranda | Antique | Negros Occidental | Q31468194 |
| 81310 | Arcangel | Antique | Aklan | Q31468353 |
| 81315 | Armenia | Albay | Masbate | Q31468839 |
| 81322 | Asturga | Antique | Capiz | Q31469829 |
| 81324 | Atabayan | Antique | Iloilo | Q31469899 |
| 81326 | Atipuluhan | Antique | Negros Occidental | Q31470140 |
| 81328 | Atop-atop | Bataan | Cebu | Q31470242 |
| 81330 | Aumbay | Benguet | Davao del Norte | Q31470691 |
| 81335 | Aurora | Zamboanga Sibugay | Zamboanga del Sur | Q132015 |
| 81340 | Aya | Occidental Mindoro | Batangas | Q31471450 |
| 81341 | Ayugan | Albay | Camarines Sur | Q31471535 |
| 81343 | Ayusan Uno | Occidental Mindoro | Quezon | Q31471579 |
| 81344 | Azagra | Bataan | Negros Oriental | Q31471600 |
| 81350 | Babug | Oriental Mindoro | Occidental Mindoro | Q31472591 |
| 81357 | Bachauan | Bataan | Cebu | Q31473047 |
| 81358 | Baclayon | Bataan | Bohol | Q404489 |
| 81378 | Bacuyangan | Antique | Negros Occidental | Q31474227 |
| 81387 | Bagacay | Albay | Sorsogon | Q31474720 |
| 81388 | Bagahanlad | Albay | Masbate | Q31474868 |
| 81389 | Bagakay | Benguet | Misamis Occidental | Q31474911 |
| 81394 | Bagay | Bataan | Cebu | Q31475294 |
| 81396 | Bago City | Antique | Negros Occidental | Q628297 |
| 81404 | Bagroy | Antique | Negros Occidental | Q31796174 |
| 81405 | Bagtic | Bataan | Negros Oriental | Q31475740 |
| 81414 | Bagupaye | Occidental Mindoro | Quezon | Q31476159 |
| 81416 | Bahay | Albay | Camarines Sur | Q31476220 |
| 81421 | Bailan | Antique | Capiz | Q31476426 |
| 81422 | Bairan | Bataan | Cebu | Q31476767 |
| 81428 | Bal-os | Bataan | Negros Oriental | Q31477483 |
| 81430 | Balabag | Antique | Aklan | Q31477589 |
| 81440 | Balanacan | Oriental Mindoro | Marinduque | Q31478141 |
| 81448 | Balaogan | Albay | Camarines Sur | Q31478483 |
| 81457 | Balayong | Bataan | Negros Oriental | Q31478887 |
| 81465 | Balibagan Oeste | Antique | Iloilo | Q31480155 |
| 81469 | Balila | Benguet | Bukidnon | Q31480411 |
| 81470 | Balili | Benguet | Lanao del Norte | Q31480432 |
| 81471 | Balilihan | Bataan | Bohol | Q404519 |
| 81480 | Balinsacayao | Batanes | Leyte | Q31480869 |
| 81483 | Balitoc | Occidental Mindoro | Batangas | Q31481061 |
| 81487 | Baliwagan | Antique | Negros Occidental | Q31481165 |
| 81491 | Balocawehay | Batanes | Leyte | Q31481484 |
| 81492 | Balogo | Bataan | Negros Oriental | Q31481551 |
| 81499 | Balucawi | Albay | Masbate | Q31481991 |
| 81512 | Banaba | Occidental Mindoro | Cavite | Q31482683 |
| 81514 | Banalo | Occidental Mindoro | Batangas | Q31482744 |
| 81520 | Bancal | Antique | Iloilo | Q31482926 |
| 81526 | Bangahan | Benguet | Bukidnon | Q31483320 |
| 81536 | Banhigan | Bataan | Cebu | Q31483843 |
| 81539 | Banilad | Bataan | Negros Oriental | Q31484008 |
| 81540 | Banilad | Occidental Mindoro | Batangas | Q31483987 |
| 81554 | Bantilan | Occidental Mindoro | Quezon | Q31485086 |
| 81555 | Bantiqui | Batanes | Leyte | Q31485106 |
| 81558 | Bantuanon | Benguet | Bukidnon | Q31485209 |
| 81559 | Banugao | Occidental Mindoro | Quezon | Q31485371 |
| 81560 | Bao | Albay | Camarines Sur | Q31485453 |
| 81564 | Barahan | Oriental Mindoro | Occidental Mindoro | Q31485876 |
| 81568 | Baras | Occidental Mindoro | Rizal | Q106766 |
| 81581 | Barong Barong | Oriental Mindoro | Palawan | Q31796387 |
| 81586 | Barra | Albay | Masbate | Q31487532 |
| 81587 | Barra | Benguet | Misamis Oriental | Q31487511 |
| 81593 | Basak | Benguet | Bukidnon | Q31488145 |
| 81594 | Basak | Bataan | Negros Oriental | Q31488165 |
| 81599 | Basdiot | Bataan | Cebu | Q31488566 |
| 81601 | Basiad | Albay | Camarines Norte | Q31488714 |
| 81602 | Basiao | Antique | Capiz | Q31488756 |
| 81608 | Basud | Albay | Camarines Norte | Q356607 |
| 81618 | Batas | Occidental Mindoro | Cavite | Q31490066 |
| 81622 | Bateria | Bataan | Cebu | Q31490267 |
| 81632 | Batobalane | Albay | Camarines Norte | Q31490707 |
| 81643 | Baud | Bataan | Cebu | Q31796455 |
| 81651 | Bay-ang | Antique | Iloilo | Q31492049 |
| 81672 | Beberon | Albay | Camarines Sur | Q31494327 |
| 81673 | Becerril | Bataan | Cebu | Q31494370 |
| 81683 | Biao | Antique | Negros Occidental | Q31498224 |
| 81685 | Biasong | Bataan | Cebu | Q31498289 |
| 81690 | Bien Unido | Bataan | Bohol | Q404581 |
| 81696 | Bignay Uno | Occidental Mindoro | Quezon | Q31500802 |
| 81697 | Biking | Bataan | Bohol | Q31500925 |
| 81700 | Bilao | Antique | Capiz | Q31501112 |
| 81701 | Bilar | Bataan | Bohol | Q404604 |
| 81704 | Bilog-Bilog | Occidental Mindoro | Batangas | Q31501457 |
| 81705 | Bilwang | Batanes | Leyte | Q31501500 |
| 81706 | Binabaan | Antique | Iloilo | Q31501605 |
| 81708 | Binahaan | Occidental Mindoro | Quezon | Q31501749 |
| 81713 | Binantocan | Antique | Capiz | Q31502177 |
| 81714 | Binanwanaan | Albay | Camarines Sur | Q31502196 |
| 81722 | Binitinan | Benguet | Misamis Oriental | Q31502648 |
| 81723 | Binlod | Bataan | Cebu | Q31796544 |
| 81726 | Binon-an | Antique | Iloilo | Q31502739 |
| 81727 | Binonga | Antique | Negros Occidental | Q31502760 |
| 81728 | Bintacay | Oriental Mindoro | Marinduque | Q31502820 |
| 81735 | Binulasan | Occidental Mindoro | Quezon | Q31503129 |
| 81741 | Bitangan | Occidental Mindoro | Cavite | Q31503898 |
| 81742 | Bitanjuan | Batanes | Leyte | Q31503918 |
| 81746 | Bitoon | Bataan | Cebu | Q31504138 |
| 81757 | Bocana | Antique | Negros Occidental | Q31507507 |
| 81765 | Bolanon | Antique | Negros Occidental | Q31508304 |
| 81767 | Bolboc | Occidental Mindoro | Batangas | Q31508358 |
| 81769 | Bolilao | Antique | Iloilo | Q31508514 |
| 81775 | Bolo | Occidental Mindoro | Batangas | Q31508732 |
| 81776 | Bolo | Albay | Camarines Sur | Q31508714 |
| 81777 | Bolo | Antique | Capiz | Q31508750 |
| 81779 | Bolo Bolo | Benguet | Misamis Oriental | Q31508783 |
| 81780 | Bolong | Antique | Iloilo | Q31508839 |
| 81783 | Bonawon | Bataan | Negros Oriental | Q31509073 |
| 81784 | Bonbon | Bataan | Cebu | Q31509109 |
| 81785 | Bonbon | Benguet | Camiguin | Q31509090 |
| 81794 | Bood | Bataan | Bohol | Q31509765 |
| 81800 | Bosdak | Occidental Mindoro | Quezon | Q31510182 |
| 81805 | Boton | Albay | Sorsogon | Q31510449 |
| 81820 | Buanoy | Bataan | Cebu | Q31514603 |
| 81838 | Buga | Antique | Iloilo | Q31516357 |
| 81839 | Bugaan | Occidental Mindoro | Batangas | Q31516378 |
| 81841 | Bugang | Antique | Negros Occidental | Q31516428 |
| 81842 | Bugas | Bataan | Cebu | Q31516446 |
| 81845 | Bugcaon | Benguet | Bukidnon | Q31516533 |
| 81846 | Bugho | Batanes | Leyte | Q31516584 |
| 81847 | Bugko | Batanes | Northern Samar | Q31516601 |
| 81849 | Bugsoc | Bataan | Bohol | Q31516649 |
| 81853 | Buhatan | Albay | Sorsogon | Q31516896 |
| 81855 | Bukal | Occidental Mindoro | Quezon | Q31517014 |
| 81856 | Bukal Sur | Occidental Mindoro | Quezon | Q31517031 |
| 81863 | Bulad | Antique | Negros Occidental | Q31517275 |
| 81869 | Bulasa | Bataan | Cebu | Q31517497 |
| 81870 | Bulata | Antique | Negros Occidental | Q31517509 |
| 81875 | Bulihan | Occidental Mindoro | Cavite | Q31517689 |
| 81881 | Bulo | Albay | Masbate | Q31518147 |
| 81882 | Bulod | Bataan | Negros Oriental | Q31518196 |
| 81887 | Buluang | Albay | Camarines Sur | Q31518316 |
| 81889 | Buluangan | Antique | Negros Occidental | Q31518349 |
| 81896 | Bungahan | Occidental Mindoro | Batangas | Q31518652 |
| 81897 | Bungoy | Occidental Mindoro | Quezon | Q31518685 |
| 81898 | Bungsuan | Antique | Capiz | Q31518703 |
| 81903 | Buracan | Albay | Camarines Sur | Q31518967 |
| 81905 | Buray | Antique | Iloilo | Q31519021 |
| 81911 | Burias | Antique | Capiz | Q31519409 |
| 81913 | Burirao | Oriental Mindoro | Palawan | Q31519493 |
| 81915 | Busay | Antique | Negros Occidental | Q31520103 |
| 81916 | Busdi | Benguet | Bukidnon | Q31520193 |
| 81918 | Busing | Albay | Masbate | Q31520362 |
| 81921 | Butag | Albay | Sorsogon | Q31520577 |
| 81922 | Butazon | Batanes | Leyte | Q31520695 |
| 81929 | Buyabod | Oriental Mindoro | Marinduque | Q31521165 |
| 81931 | Buyuan | Antique | Iloilo | Q31521273 |
| 81934 | Cabacao | Oriental Mindoro | Occidental Mindoro | Q31522337 |
| 81935 | Cabacungan | Antique | Negros Occidental | Q31522373 |
| 81936 | Cabacuñgan | Batanes | Leyte | Q31522390 |
| 81938 | Cabadiangan | Antique | Negros Occidental | Q31522425 |
| 81941 | Cabalawan | Bataan | Cebu | Q31522551 |
| 81945 | Cabanbanan | Occidental Mindoro | Laguna | Q31522767 |
| 81946 | Cabanbanan | Antique | Negros Occidental | Q31522784 |
| 81947 | Cabangahan | Bataan | Negros Oriental | Q31522833 |
| 81948 | Cabangahan | Benguet | Bukidnon | Q31522817 |
| 81959 | Cabay | Occidental Mindoro | Quezon | Q31523174 |
| 81960 | Cabay | Batanes | Eastern Samar | Q31523188 |
| 81963 | Cabcab | Albay | Catanduanes | Q31523304 |
| 81966 | Cabiguan | Albay | Sorsogon | Q31523479 |
| 81967 | Cabilao | Antique | Iloilo | Q31523511 |
| 81968 | Cabilauan | Antique | Iloilo | Q31523546 |
| 81971 | Cabitan | Albay | Masbate | Q31523660 |
| 81976 | Cabra | Oriental Mindoro | Occidental Mindoro | Q31523887 |
| 81987 | Cadagmayan Norte | Antique | Iloilo | Q31524702 |
| 81988 | Caditaan | Albay | Sorsogon | Q31524899 |
| 81990 | Cadlan | Albay | Camarines Sur | Q31524951 |
| 81992 | Cagamotan | Batanes | Northern Samar | Q31525048 |
| 81996 | Cagbang | Antique | Iloilo | Q31525277 |
| 81999 | Cagsiay | Occidental Mindoro | Quezon | Q31525663 |
| 82002 | Caigangan | Oriental Mindoro | Marinduque | Q31525951 |
| 82005 | Cajimos | Oriental Mindoro | Romblon | Q31526152 |
| 82008 | Calabaca | Albay | Camarines Norte | Q31526268 |
| 82011 | Calabugao | Benguet | Bukidnon | Q31526440 |
| 82019 | Calampisauan | Antique | Negros Occidental | Q31526861 |
| 82031 | Calape | Bataan | Bohol | Q404652 |
| 82033 | Calasgasan | Albay | Camarines Norte | Q31527358 |
| 82051 | Calidñgan | Bataan | Cebu | Q31528189 |
| 82058 | Calizo | Antique | Aklan | Q31528520 |
| 82062 | Calolbon | Albay | Catanduanes | Q31528638 |
| 82069 | Calumboyan | Bataan | Cebu | Q31528830 |
| 82070 | Calumpang | Occidental Mindoro | Laguna | Q31528943 |
| 82081 | Camalobalo | Antique | Negros Occidental | Q31529407 |
| 82083 | Camandag | Antique | Negros Occidental | Q31529443 |
| 82084 | Camangcamang | Antique | Negros Occidental | Q31529514 |
| 82085 | Cambanay | Bataan | Cebu | Q31529678 |
| 82087 | Cambuga | Occidental Mindoro | Quezon | Q31529800 |
| 82090 | Caminauit | Oriental Mindoro | Occidental Mindoro | Q31530113 |
| 82091 | Camindangan | Antique | Negros Occidental | Q31530129 |
| 82092 | Camingawan | Antique | Negros Occidental | Q31530146 |
| 82093 | Camohaguin | Occidental Mindoro | Quezon | Q31530180 |
| 82094 | Camp Flora | Occidental Mindoro | Quezon | Q31530351 |
| 82095 | Campoyo | Bataan | Negros Oriental | Q31811284 |
| 82096 | Campusong | Bataan | Cebu | Q31530812 |
| 82099 | Can-asujan | Bataan | Cebu | Q31530908 |
| 82103 | Canauay | Bataan | Negros Oriental | Q31531316 |
| 82104 | Canayan | Benguet | Bukidnon | Q31531385 |
| 82106 | Candabong | Bataan | Bohol | Q31531572 |
| 82110 | Candiis | Benguet | Misamis Oriental | Q31531751 |
| 82111 | Candijay | Bataan | Bohol | Q404680 |
| 82114 | Canhandugan | Batanes | Leyte | Q31532002 |
| 82115 | Canhaway | Bataan | Bohol | Q31532018 |
| 82116 | Caningay | Antique | Negros Occidental | Q31532114 |
| 82117 | Canjulao | Bataan | Bohol | Q31532244 |
| 82119 | Canmaya Diot | Bataan | Bohol | Q31532292 |
| 82120 | Canomoy | Albay | Masbate | Q31532355 |
| 82121 | Canroma | Antique | Negros Occidental | Q31532372 |
| 82122 | Cansilayan | Antique | Negros Occidental | Q31532421 |
| 82123 | Cansolungon | Antique | Negros Occidental | Q31532510 |
| 82124 | Cansuje | Bataan | Cebu | Q31532526 |
| 82130 | Canturay | Antique | Negros Occidental | Q31532688 |
| 82133 | Capaga | Antique | Capiz | Q31532923 |
| 82135 | Capalonga | Albay | Camarines Norte | Q119624 |
| 82139 | Capitan Ramon | Antique | Negros Occidental | Q31533207 |
| 82141 | Capucnasan | Albay | Camarines Sur | Q31533555 |
| 82144 | Capuluan | Occidental Mindoro | Quezon | Q31533670 |
| 82145 | Capuy | Albay | Sorsogon | Q31533736 |
| 82146 | Carabalan | Antique | Negros Occidental | Q31533787 |
| 82147 | Caracal | Zamboanga Sibugay | Zamboanga del Norte | Q31533881 |
| 82153 | Caranan | Albay | Camarines Sur | Q31534112 |
| 82156 | Caraycayon | Albay | Camarines Sur | Q31534192 |
| 82160 | Caridad | Antique | Negros Occidental | Q31534420 |
| 82161 | Caridad | Batanes | Leyte | Q31534436 |
| 82165 | Carmelo | Antique | Iloilo | Q31534741 |
| 82166 | Carmelo | Bataan | Cebu | Q31534728 |
| 82176 | Caromatan | Benguet | Lanao del Norte | Q274387 |
| 82182 | Carriedo | Albay | Sorsogon | Q31535624 |
| 82184 | Cartagena | Antique | Negros Occidental | Q31535826 |
| 82185 | Caruray | Oriental Mindoro | Palawan | Q31535999 |
| 82187 | Casala-an | Bataan | Negros Oriental | Q31536143 |
| 82189 | Casay | Bataan | Cebu | Q31536208 |
| 82190 | Casay | Occidental Mindoro | Quezon | Q31536192 |
| 82191 | Casian | Oriental Mindoro | Palawan | Q31536327 |
| 82194 | Cassanayan | Antique | Capiz | Q31536570 |
| 82195 | Castañas | Occidental Mindoro | Quezon | Q31536599 |
| 82198 | Castillo | Albay | Camarines Sur | Q31536695 |
| 82200 | Catabangan | Albay | Camarines Sur | Q31537084 |
| 82212 | Caticugan | Bataan | Negros Oriental | Q31537709 |
| 82213 | Catigbian | Bataan | Bohol | Q404750 |
| 82216 | Catmondaan | Bataan | Cebu | Q31537842 |
| 82221 | Catungawan Sur | Bataan | Bohol | Q31538007 |
| 82223 | Causip | Albay | Camarines Sur | Q31538249 |
| 82233 | Cayang | Bataan | Cebu | Q31538834 |
| 82235 | Cayanguan | Antique | Aklan | Q31538887 |
| 82236 | Cayhagan | Antique | Negros Occidental | Q31539026 |
| 82243 | Chambrey | Antique | Negros Occidental | Q31541307 |
| 82244 | Cigaras | Occidental Mindoro | Laguna | Q31544418 |
| 82252 | Codcod | Antique | Negros Occidental | Q31548281 |
| 82253 | Cogan | Bataan | Cebu | Q31548513 |
| 82254 | Cogon | Bataan | Cebu | Q31548640 |
| 82256 | Cogon | Antique | Capiz | Q31548713 |
| 82257 | Cogon Cruz | Bataan | Cebu | Q31548730 |
| 82258 | Cogtong | Bataan | Bohol | Q31548759 |
| 82261 | Colonia | Bataan | Cebu | Q31549999 |
| 82278 | Conduaga | Oriental Mindoro | Palawan | Q31551178 |
| 82284 | Consuegra | Batanes | Leyte | Q31551919 |
| 82285 | Consuelo | Bataan | Cebu | Q31551953 |
| 82286 | Consuelo | Antique | Negros Occidental | Q31551969 |
| 82287 | Consuelo | Benguet | Misamis Oriental | Q31551936 |
| 82293 | Corella | Bataan | Bohol | Q404799 |
| 82301 | Cosina | Benguet | Bukidnon | Q31553701 |
| 82310 | Culacling | Albay | Camarines Sur | Q31556972 |
| 82313 | Culasian | Batanes | Leyte | Q31557088 |
| 82319 | Cumadcad | Albay | Sorsogon | Q31557396 |
| 82321 | Curry | Albay | Camarines Sur | Q31557635 |
| 82326 | Da-an Sur | Antique | Capiz | Q31558206 |
| 82331 | Daet | Albay | Camarines Norte | Q356655 |
| 82333 | Dagatan | Occidental Mindoro | Quezon | Q31558560 |
| 82334 | Dagohoy | Bataan | Bohol | Q404854 |
| 82336 | Daguit | Albay | Camarines Norte | Q31558689 |
| 82338 | Dagumba-an | Benguet | Bukidnon | Q31558723 |
| 82348 | Daliciasao | Antique | Negros Occidental | Q31559889 |
| 82351 | Dalirig | Benguet | Bukidnon | Q31559953 |
| 82352 | Dalorong | Benguet | Bukidnon | Q31560037 |
| 82354 | Dalupaon | Albay | Camarines Sur | Q31560165 |
| 82356 | Dalwangan | Benguet | Bukidnon | Q31560225 |
| 82360 | Damayan | Antique | Capiz | Q31560664 |
| 82361 | Damilag | Benguet | Bukidnon | Q31560685 |
| 82362 | Damolog | Bataan | Cebu | Q31560752 |
| 82367 | Dancagan | Benguet | Bukidnon | Q31561216 |
| 82368 | Dancalan | Antique | Negros Occidental | Q31561233 |
| 82369 | Dangcalan | Albay | Sorsogon | Q31561282 |
| 82376 | Dapawan | Oriental Mindoro | Romblon | Q31561712 |
| 82377 | Dapdap | Batanes | Eastern Samar | Q31561745 |
| 82378 | Dapdap | Albay | Masbate | Q31561728 |
| 82379 | Dapdapan | Antique | Capiz | Q31561798 |
| 82384 | Daraitan | Occidental Mindoro | Rizal | Q31562034 |
| 82390 | Datagon | Bataan | Negros Oriental | Q31562401 |
| 82394 | Dauis | Bataan | Bohol | Q404908 |
| 82400 | Dayapan | Occidental Mindoro | Batangas | Q31563653 |
| 82401 | Daykitin | Oriental Mindoro | Marinduque | Q31563687 |
| 82402 | De la Paz | Antique | Iloilo | Q31563846 |
| 82403 | De la Paz | Bataan | Bohol | Q31563830 |
| 82412 | Del Rosario | Albay | Camarines Sur | Q31564711 |
| 82415 | Dian-ay | Antique | Negros Occidental | Q31565964 |
| 82420 | Dicayong | Zamboanga Sibugay | Zamboanga del Norte | Q31566526 |
| 82428 | Dimaluna | Benguet | Misamis Occidental | Q31567338 |
| 82431 | Dimayon | Benguet | Lanao del Norte | Q31567480 |
| 82432 | Dimiao | Bataan | Bohol | Q404930 |
| 82445 | Disod | Zamboanga Sibugay | Zamboanga del Norte | Q31568302 |
| 82447 | Dobdoban | Oriental Mindoro | Romblon | Q31568794 |
| 82449 | Doljo | Bataan | Bohol | Q31569353 |
| 82451 | Dologon | Benguet | Bukidnon | Q31569516 |
| 82462 | Doos | Batanes | Leyte | Q31570463 |
| 82465 | Dos Hermanas | Antique | Negros Occidental | Q31570645 |
| 82469 | Duero | Bataan | Bohol | Q404951 |
| 82471 | Dugcal | Albay | Camarines Sur | Q31572050 |
| 82472 | Dugongan | Albay | Camarines Norte | Q31572087 |
| 82475 | Dulangan | Antique | Capiz | Q31572249 |
| 82477 | Dulao | Antique | Negros Occidental | Q31572303 |
| 82484 | Dumalaguing | Benguet | Bukidnon | Q31572527 |
| 82495 | Dungon | Antique | Aklan | Q31573097 |
| 82497 | Duran | Antique | Capiz | Q31573326 |
| 82506 | El Pardo | Bataan | Cebu | Q31576346 |
| 82512 | Erenas | Batanes | Northern Samar | Q31578713 |
| 82533 | Eustaquio Lopez | Antique | Negros Occidental | Q31579725 |
| 82535 | Fabrica | Albay | Camarines Sur | Q31580420 |
| 82537 | Feliciano | Antique | Aklan | Q31581507 |
| 82544 | Gabao | Albay | Sorsogon | Q31796877 |
| 82545 | Gabas | Batanes | Leyte | Q31796886 |
| 82546 | Gabawan | Oriental Mindoro | Romblon | Q31587580 |
| 82548 | Gabi | Antique | Iloilo | Q31587626 |
| 82556 | Gambalidio | Albay | Camarines Sur | Q31588283 |
| 82570 | Garcia Hernandez | Bataan | Bohol | Q404976 |
| 82572 | Gatbo | Albay | Camarines Sur | Q31589365 |
| 82588 | Gibato | Antique | Capiz | Q31590688 |
| 82589 | Gibgos | Albay | Camarines Sur | Q31590704 |
| 82593 | Gimampang | Benguet | Misamis Oriental | Q31457787 |
| 82594 | Ginabuyan | Batanes | Leyte | Q31457832 |
| 82596 | Gines-Patay | Antique | Iloilo | Q31457872 |
| 82608 | Granada | Antique | Iloilo | Q31811331 |
| 82614 | Guba | Bataan | Negros Oriental | Q31811348 |
| 82623 | Guijalo | Albay | Camarines Sur | Q31811356 |
| 82625 | Guiljungan | Antique | Negros Occidental | Q31811361 |
| 82629 | Guinacotan | Albay | Camarines Norte | Q31811363 |
| 82631 | Guindapunan | Batanes | Leyte | Q31811364 |
| 82633 | Guindulman | Bataan | Bohol | Q405058 |
| 82637 | Guinoaliuan | Antique | Aklan | Q31811370 |
| 82641 | Guinticgan | Antique | Iloilo | Q31811374 |
| 82642 | Guintubhan | Antique | Negros Occidental | Q31811375 |
| 82645 | Guirang | Batanes | Western Samar | Q31811378 |
| 82648 | Guisguis | Occidental Mindoro | Quezon | Q31811380 |
| 82652 | Gulod | Occidental Mindoro | Rizal | Q31811387 |
| 82655 | Gumaus | Albay | Camarines Norte | Q31811390 |
| 82656 | Gumian | Occidental Mindoro | Quezon | Q31811391 |
| 82658 | Guruyan | Albay | Sorsogon | Q31811395 |
| 82661 | Guyam Malaki | Occidental Mindoro | Cavite | Q31811397 |
| 82664 | Hacienda Refugio | Antique | Negros Occidental | Q31811402 |
| 82665 | Hacienda Santa Rosa | Antique | Negros Occidental | Q31811403 |
| 82670 | Haguimit | Antique | Negros Occidental | Q31811407 |
| 82671 | Halapitan | Benguet | Bukidnon | Q31811408 |
| 82672 | Halayhay | Occidental Mindoro | Cavite | Q31811409 |
| 82673 | Halayhayin | Occidental Mindoro | Laguna | Q31811410 |
| 82674 | Haligue | Occidental Mindoro | Batangas | Q31811411 |
| 82679 | Harrison | Oriental Mindoro | Occidental Mindoro | Q31811423 |
| 82683 | Hibaiyo | Bataan | Negros Oriental | Q31811433 |
| 82688 | Himaao | Albay | Camarines Sur | Q31811443 |
| 82690 | Himaya | Antique | Negros Occidental | Q31811444 |
| 82692 | Hinapalanan | Benguet | Misamis Oriental | Q31811446 |
| 82695 | Hingatungan | Batanes | Southern Leyte | Q31811447 |
| 82700 | Hipadpad | Batanes | Eastern Samar | Q31811449 |
| 82701 | Hipasngo | Batanes | Leyte | Q31811450 |
| 82702 | Hipona | Antique | Capiz | Q31811451 |
| 82703 | Hobo | Albay | Camarines Sur | Q31811452 |
| 82705 | Hukay | Occidental Mindoro | Batangas | Q31811458 |
| 82708 | Ibabang Tayuman | Occidental Mindoro | Quezon | Q31811463 |
| 82710 | Ibarra | Batanes | Southern Leyte | Q31811464 |
| 82715 | Igang | Antique | Iloilo | Q31811470 |
| 82717 | Igbon | Antique | Iloilo | Q31811471 |
| 82718 | Igcocolo | Antique | Iloilo | Q31811472 |
| 82719 | Igmaya-an | Antique | Negros Occidental | Q31811473 |
| 82721 | Igpit | Benguet | Misamis Oriental | Q31811475 |
| 82728 | Ilihan | Occidental Mindoro | Batangas | Q31811483 |
| 82729 | Ilihan | Bataan | Cebu | Q31811484 |
| 82733 | Imbang | Antique | Negros Occidental | Q31811487 |
| 82734 | Imbatug | Benguet | Bukidnon | Q31811488 |
| 82735 | Imelda | Benguet | Zamboanga Sibugay | Q131838 |
| 82737 | Impalutao | Benguet | Bukidnon | Q31811491 |
| 82740 | Inabanga | Bataan | Bohol | Q405088 |
| 82742 | Inapatan | Albay | Camarines Sur | Q31811495 |
| 82745 | Inayauan | Antique | Negros Occidental | Q31811498 |
| 82747 | Indulang | Benguet | Bukidnon | Q31811500 |
| 82751 | Inicbulan | Occidental Mindoro | Batangas | Q31811505 |
| 82753 | Inobulan | Benguet | Misamis Oriental | Q31811506 |
| 82754 | Intampilan | Antique | Capiz | Q31811507 |
| 82762 | Iraray | Oriental Mindoro | Palawan | Q31811515 |
| 82763 | Irasan | Zamboanga Sibugay | Zamboanga del Norte | Q31811517 |
| 82766 | Irirum | Oriental Mindoro | Occidental Mindoro | Q31811519 |
| 82772 | Isugod | Oriental Mindoro | Palawan | Q31811522 |
| 82782 | Jagna | Bataan | Bohol | Q405110 |
| 82783 | Jaguimitan | Antique | Iloilo | Q31811528 |
| 82786 | Jalaud | Antique | Iloilo | Q31811533 |
| 82787 | Jamabalod | Antique | Iloilo | Q31811535 |
| 82790 | Janagdong | Occidental Mindoro | Quezon | Q31811537 |
| 82793 | Janopol | Occidental Mindoro | Batangas | Q31811540 |
| 82794 | Jantianon | Bataan | Negros Oriental | Q31811541 |
| 82796 | Japitan | Antique | Negros Occidental | Q31811543 |
| 82800 | Javalera | Occidental Mindoro | Cavite | Q31811546 |
| 82802 | Jayubó | Antique | Iloilo | Q31811549 |
| 82803 | Jetafe | Bataan | Bohol | Q405005 |
| 82805 | Jibao-an | Antique | Iloilo | Q31811552 |
| 82812 | Jose Pañganiban | Albay | Camarines Norte | Q356681 |
| 82817 | Jubasan | Batanes | Northern Samar | Q31811560 |
| 82818 | Jugno | Bataan | Negros Oriental | Q31811561 |
| 82822 | Kabalantian | Benguet | Misamis Oriental | Q31811565 |
| 82827 | Kabilauan | Antique | Iloilo | Q31811568 |
| 82830 | Kabulohan | Benguet | Bukidnon | Q31811571 |
| 82831 | Kabulusan | Occidental Mindoro | Laguna | Q31811572 |
| 82833 | Kabuynan | Batanes | Leyte | Q31811575 |
| 82834 | Kadingilan | Benguet | Bukidnon | Q357100 |
| 82843 | Kalanganan | Benguet | Lanao del Norte | Q31811586 |
| 82852 | Kalilangan | Benguet | Bukidnon | Q357124 |
| 82854 | Kaliliog | Albay | Camarines Sur | Q31811598 |
| 82856 | Kalugmanan | Benguet | Bukidnon | Q31811599 |
| 82859 | Kampokpok | Batanes | Leyte | Q31811602 |
| 82861 | Kandabong | Bataan | Negros Oriental | Q31811604 |
| 82869 | Kapatalan | Occidental Mindoro | Laguna | Q31811611 |
| 82890 | Kaytitinga | Occidental Mindoro | Cavite | Q31811632 |
| 82893 | Kibangay | Benguet | Bukidnon | Q31811636 |
| 82894 | Kibawe | Benguet | Bukidnon | Q357152 |
| 82896 | Kibonsod | Benguet | Misamis Oriental | Q31811637 |
| 82898 | Kibureau | Benguet | Bukidnon | Q31811638 |
| 82900 | Kilim | Batanes | Leyte | Q31811639 |
| 82901 | Kiloloran | Occidental Mindoro | Quezon | Q31811641 |
| 82902 | Kimanuit | Benguet | Bukidnon | Q31811642 |
| 82903 | Kimaya | Benguet | Misamis Oriental | Q31811643 |
| 82906 | Kinalaglagan | Occidental Mindoro | Batangas | Q31811647 |
| 82910 | Kinatakutan | Occidental Mindoro | Quezon | Q31811651 |
| 82912 | Kipit | Zamboanga Sibugay | Zamboanga del Norte | Q31811653 |
| 82914 | Kisolon | Benguet | Bukidnon | Q31811656 |
| 82916 | Kitaotao | Benguet | Bukidnon | Q357175 |
| 82919 | Kitobo | Benguet | Bukidnon | Q31811659 |
| 82934 | Kumalisquis | Antique | Negros Occidental | Q31811687 |
| 82938 | La Curva | Oriental Mindoro | Occidental Mindoro | Q31811693 |
| 82940 | La Fortuna | Benguet | Bukidnon | Q31811696 |
| 82941 | La Granja | Antique | Negros Occidental | Q31811698 |
| 82942 | La Hacienda | Bataan | Bohol | Q31811701 |
| 82952 | La Roxas | Benguet | Bukidnon | Q31811712 |
| 82962 | Labo | Albay | Camarines Norte | Q356708 |
| 82963 | Labog | Oriental Mindoro | Palawan | Q23787486 |
| 82970 | Lacaron | Antique | Capiz | Q31811728 |
| 82971 | Lacdayan | Occidental Mindoro | Quezon | Q31811729 |
| 82982 | Laguitas | Benguet | Bukidnon | Q31811739 |
| 82985 | Lajong | Albay | Sorsogon | Q31811743 |
| 82988 | Lalab | Antique | Aklan | Q31811750 |
| 82989 | Lalagsan | Antique | Negros Occidental | Q31811752 |
| 82990 | Lalauigan | Batanes | Eastern Samar | Q31811754 |
| 82991 | Lalig | Occidental Mindoro | Quezon | Q31811755 |
| 82993 | Lamak | Batanes | Leyte | Q31811757 |
| 83008 | Lanas | Oriental Mindoro | Romblon | Q31811772 |
| 83009 | Lanas | Bataan | Cebu | Q31811771 |
| 83012 | Langatian | Zamboanga Sibugay | Zamboanga del Norte | Q31811775 |
| 83014 | Langob | Bataan | Cebu | Q31811777 |
| 83016 | Langtad | Bataan | Cebu | Q31811781 |
| 83019 | Lanipao | Benguet | Lanao del Norte | Q31811785 |
| 83021 | Lanot | Antique | Capiz | Q31811788 |
| 83022 | Lantangan | Antique | Iloilo | Q31811791 |
| 83023 | Lantangan | Albay | Masbate | Q31811789 |
| 83024 | Lantapan | Benguet | Bukidnon | Q31811792 |
| 83030 | Lapase | Benguet | Misamis Occidental | Q31811796 |
| 83035 | Lapining | Benguet | Lanao del Norte | Q31811800 |
| 83036 | Lapolapo | Occidental Mindoro | Batangas | Q31811801 |
| 83041 | Larap | Albay | Camarines Norte | Q31811806 |
| 83054 | Lawigan | Antique | Iloilo | Q31811817 |
| 83056 | Laylay | Oriental Mindoro | Marinduque | Q31811820 |
| 83059 | Lañgub | Antique | Negros Occidental | Q31811822 |
| 83067 | Leon Postigo | Zamboanga Sibugay | Zamboanga del Norte | Q132540 |
| 83070 | Lepanto | Bataan | Cebu | Q31811834 |
| 83078 | Libas | Batanes | Leyte | Q31811846 |
| 83079 | Libas | Oriental Mindoro | Marinduque | Q31811844 |
| 83082 | Libato | Occidental Mindoro | Batangas | Q31811848 |
| 83090 | Liberty | Batanes | Leyte | Q31811862 |
| 83095 | Libona | Benguet | Bukidnon | Q357226 |
| 83096 | Liboran | Benguet | Bukidnon | Q31811867 |
| 83097 | Liboro | Albay | Camarines Sur | Q31811869 |
| 83105 | Ligaya | Oriental Mindoro | Occidental Mindoro | Q31811874 |
| 83108 | Lila | Bataan | Bohol | Q405141 |
| 83109 | Lilio | Occidental Mindoro | Laguna | Q31811877 |
| 83114 | Lim-oo | Batanes | Leyte | Q31811882 |
| 83119 | Limbaan | Benguet | Davao del Norte | Q31811887 |
| 83122 | Limbuhan | Albay | Masbate | Q31811890 |
| 83123 | Limon | Batanes | Leyte | Q31811893 |
| 83124 | Limon | Oriental Mindoro | Romblon | Q31811891 |
| 83128 | Linabo | Benguet | Bukidnon | Q31811898 |
| 83129 | Linabuan | Antique | Aklan | Q31811900 |
| 83130 | Linabuan Sur | Antique | Aklan | Q31811901 |
| 83135 | Linaon | Antique | Negros Occidental | Q31811907 |
| 83137 | Lingasan | Zamboanga Sibugay | Zamboanga del Norte | Q31811910 |
| 83138 | Lingating | Benguet | Bukidnon | Q31811912 |
| 83141 | Lingion | Benguet | Bukidnon | Q31811913 |
| 83144 | Lintangan | Zamboanga Sibugay | Zamboanga del Norte | Q31811916 |
| 83146 | Lipa City | Occidental Mindoro | Batangas | Q1725 |
| 83151 | Little Baguio | Benguet | Bukidnon | Q31811924 |
| 83157 | Loay | Bataan | Bohol | Q405171 |
| 83159 | Loboc | Bataan | Bohol | Q405197 |
| 83165 | Lombog | Bataan | Bohol | Q31811936 |
| 83168 | Lono | Antique | Capiz | Q31811940 |
| 83169 | Lonoy | Antique | Capiz | Q31811941 |
| 83175 | Loon | Bataan | Bohol | Q405224 |
| 83186 | Lourdes | Benguet | Misamis Oriental | Q31811958 |
| 83188 | Lourdes | Albay | Camarines Sur | Q31811959 |
| 83192 | Lubang | Oriental Mindoro | Occidental Mindoro | Q107476 |
| 83194 | Lubigan | Albay | Camarines Sur | Q31811964 |
| 83203 | Lucero | Antique | Capiz | Q31811973 |
| 83204 | Lucsuhin | Occidental Mindoro | Batangas | Q31811975 |
| 83206 | Lugo | Bataan | Cebu | Q31811976 |
| 83207 | Lugui | Albay | Camarines Norte | Q31811977 |
| 83211 | Luklukan | Albay | Camarines Norte | Q31811981 |
| 83212 | Luksuhin | Occidental Mindoro | Cavite | Q31811982 |
| 83218 | Lumbangan | Occidental Mindoro | Batangas | Q31811989 |
| 83222 | Lumbayao | Benguet | Bukidnon | Q31811991 |
| 83225 | Lumil | Occidental Mindoro | Cavite | Q31811996 |
| 83235 | Lunao | Benguet | Misamis Oriental | Q31812003 |
| 83236 | Lunas | Bataan | Cebu | Q31812004 |
| 83241 | Luntal | Occidental Mindoro | Batangas | Q31812010 |
| 83245 | Lupo | Antique | Aklan | Q31812013 |
| 83247 | Lurugan | Benguet | Bukidnon | Q31812014 |
| 83248 | Lusacan | Occidental Mindoro | Quezon | Q31812015 |
| 83250 | Lut-od | Bataan | Cebu | Q31812017 |
| 83254 | Maagnas | Albay | Camarines Sur | Q31812023 |
| 83256 | Maanas | Benguet | Misamis Oriental | Q31812025 |
| 83257 | Maao | Antique | Negros Occidental | Q31812026 |
| 83260 | Maasin | Antique | Iloilo | Q275015 |
| 83263 | Maayong Tubig | Bataan | Negros Oriental | Q31812032 |
| 83274 | Mabinay | Bataan | Negros Oriental | Q195004 |
| 83275 | Mabini | Occidental Mindoro | Batangas | Q59313 |
| 83280 | Mabini | Bataan | Bohol | Q405268 |
| 83285 | Mabiton | Albay | Masbate | Q31812048 |
| 83289 | Mabunga | Occidental Mindoro | Quezon | Q31812052 |
| 83293 | Macaas | Bataan | Cebu | Q31812056 |
| 83297 | Macalamcam A | Occidental Mindoro | Batangas | Q31812060 |
| 83298 | Macalaya | Albay | Sorsogon | Q31812061 |
| 83316 | Madulao | Occidental Mindoro | Quezon | Q31812076 |
| 83323 | Magallon Cadre | Antique | Negros Occidental | Q31812079 |
| 83329 | Magay | Bataan | Cebu | Q31812082 |
| 83330 | Magbay | Oriental Mindoro | Occidental Mindoro | Q31812083 |
| 83336 | Maglamin | Benguet | Bukidnon | Q31812088 |
| 83353 | Maguyam | Occidental Mindoro | Cavite | Q31812103 |
| 83355 | Mahabang Parang | Occidental Mindoro | Batangas | Q31812105 |
| 83366 | Mailag | Benguet | Bukidnon | Q31812115 |
| 83379 | Makiwalo | Batanes | Northern Samar | Q31812122 |
| 83380 | Malabag | Occidental Mindoro | Cavite | Q31812123 |
| 83382 | Malabanan | Occidental Mindoro | Batangas | Q31812125 |
| 83383 | Malabanban Norte | Occidental Mindoro | Quezon | Q31812126 |
| 83389 | Malabugas | Bataan | Negros Oriental | Q31812131 |
| 83392 | Malaga | Batanes | Western Samar | Q31812133 |
| 83394 | Malaiba | Bataan | Negros Oriental | Q31812136 |
| 83395 | Malainen Luma | Occidental Mindoro | Cavite | Q31812137 |
| 83396 | Malajog | Batanes | Western Samar | Q31812138 |
| 83402 | Malanday | Occidental Mindoro | Rizal | Q31812144 |
| 83403 | Malangabang | Antique | Iloilo | Q31812145 |
| 83407 | Malaruhatan | Occidental Mindoro | Batangas | Q31812149 |
| 83411 | Malasugui | Albay | Camarines Norte | Q31812153 |
| 83412 | Malatap | Albay | Camarines Norte | Q31812155 |
| 83414 | Malawag | Albay | Camarines Sur | Q31812157 |
| 83416 | Malaya | Occidental Mindoro | Rizal | Q31812158 |
| 83417 | Malayal | Zamboanga Sibugay | Zamboanga del Norte | Q31812159 |
| 83418 | Malaybalay | Benguet | Bukidnon | Q1856 |
| 83419 | Malayo-an | Antique | Iloilo | Q31812160 |
| 83421 | Malbug | Albay | Masbate | Q31812163 |
| 83422 | Malbug | Bataan | Cebu | Q31812164 |
| 83423 | Malhiao | Bataan | Cebu | Q31812166 |
| 83424 | Malibago | Oriental Mindoro | Marinduque | Q31812167 |
| 83429 | Maliig | Oriental Mindoro | Occidental Mindoro | Q31812172 |
| 83441 | Malingin | Bataan | Cebu | Q31812180 |
| 83443 | Malinta | Albay | Masbate | Q31812182 |
| 83451 | Malocloc | Antique | Capiz | Q31812188 |
| 83452 | Maloco | Antique | Aklan | Q31812189 |
| 83453 | Maloh | Bataan | Negros Oriental | Q31812190 |
| 83459 | Maluko | Benguet | Bukidnon | Q31812195 |
| 83462 | Malusay | Bataan | Negros Oriental | Q31812198 |
| 83466 | Malway | Bataan | Negros Oriental | Q31812202 |
| 83467 | Mamala | Occidental Mindoro | Quezon | Q31812203 |
| 83469 | Mamatid | Occidental Mindoro | Laguna | Q31812205 |
| 83470 | Mambagatan | Antique | Negros Occidental | Q31812206 |
| 83473 | Mambatangan | Benguet | Bukidnon | Q31812208 |
| 83474 | Mambayaan | Benguet | Misamis Oriental | Q31812209 |
| 83476 | Mambulo | Albay | Camarines Sur | Q31812212 |
| 83477 | Mamburao | Oriental Mindoro | Occidental Mindoro | Q107488 |
| 83480 | Mampurog | Albay | Camarines Norte | Q31812214 |
| 83485 | Managok | Benguet | Bukidnon | Q31812219 |
| 83486 | Manalad | Antique | Negros Occidental | Q31812220 |
| 83488 | Manalongon | Bataan | Negros Oriental | Q31812222 |
| 83490 | Mananum | Benguet | Misamis Oriental | Q31812225 |
| 83500 | Mancilang | Bataan | Cebu | Q31812236 |
| 83502 | Mandangoa | Benguet | Misamis Oriental | Q31812239 |
| 83505 | Mandih | Zamboanga Sibugay | Zamboanga del Norte | Q31812240 |
| 83512 | Mangas | Occidental Mindoro | Cavite | Q31812246 |
| 83516 | Manggahan | Occidental Mindoro | Cavite | Q31812249 |
| 83518 | Mangoso | Antique | Capiz | Q31812251 |
| 83522 | Manika | Antique | Aklan | Q31812256 |
| 83525 | Maninihon | Bataan | Negros Oriental | Q31812258 |
| 83527 | Manjoy | Antique | Capiz | Q31812259 |
| 83529 | Manlucahoc | Antique | Negros Occidental | Q31812260 |
| 83532 | Manolo Fortich | Benguet | Bukidnon | Q357272 |
| 83533 | Manquiring | Albay | Camarines Sur | Q31812263 |
| 83536 | Mantalongon | Bataan | Cebu | Q31812268 |
| 83538 | Mantang | Batanes | Eastern Samar | Q31812270 |
| 83540 | Mantiquil | Bataan | Negros Oriental | Q31812271 |
| 83546 | Manup | Antique | Aklan | Q31812277 |
| 83553 | Mapili | Antique | Iloilo | Q31812283 |
| 83555 | Mapulo | Occidental Mindoro | Batangas | Q31812285 |
| 83556 | Mapulot | Occidental Mindoro | Quezon | Q31812286 |
| 83557 | Maputi | Benguet | Misamis Oriental | Q31812287 |
| 83561 | Maramag | Benguet | Bukidnon | Q357299 |
| 83562 | Maranding | Benguet | Lanao del Norte | Q31812291 |
| 83564 | Marao | Occidental Mindoro | Quezon | Q31812292 |
| 83565 | Maravilla | Bataan | Cebu | Q31812293 |
| 83576 | Mariano | Benguet | Misamis Oriental | Q31812301 |
| 83579 | Maribong | Antique | Iloilo | Q31812302 |
| 83580 | Maricaban | Bataan | Cebu | Q31812303 |
| 83581 | Maricalom | Antique | Negros Occidental | Q31812304 |
| 83589 | Marupit | Albay | Camarines Sur | Q31812310 |
| 83590 | Masaba | Bataan | Cebu | Q31812312 |
| 83592 | Masaling | Antique | Negros Occidental | Q31812314 |
| 83594 | Masalukot Uno | Occidental Mindoro | Quezon | Q31812316 |
| 83596 | Masapang | Occidental Mindoro | Laguna | Q31812317 |
| 83598 | Masarayao | Batanes | Leyte | Q31812319 |
| 83602 | Masiga | Oriental Mindoro | Marinduque | Q31812324 |
| 83608 | Masoli | Albay | Camarines Sur | Q31812328 |
| 83609 | Masonogan | Antique | Capiz | Q31812330 |
| 83611 | Mataas Na Kahoy | Occidental Mindoro | Batangas | Q59740 |
| 83614 | Matagbak | Occidental Mindoro | Cavite | Q31812335 |
| 83615 | Matala | Occidental Mindoro | Batangas | Q31812337 |
| 83619 | Matangad | Benguet | Misamis Oriental | Q31812339 |
| 83623 | Mataywanac | Occidental Mindoro | Batangas | Q31812342 |
| 83628 | Matingain | Occidental Mindoro | Batangas | Q31812351 |
| 83630 | Matlang | Batanes | Leyte | Q31812353 |
| 83637 | Maugat West | Occidental Mindoro | Batangas | Q31812362 |
| 83643 | Maya | Bataan | Cebu | Q31812368 |
| 83644 | Mayabon | Bataan | Negros Oriental | Q31812369 |
| 83645 | Mayana | Bataan | Bohol | Q31812370 |
| 83647 | Mayapusi | Bataan | Negros Oriental | Q31812371 |
| 83650 | Mayngaran | Albay | Masbate | Q31812375 |
| 83653 | Maypangdan | Batanes | Eastern Samar | Q31812377 |
| 83654 | Maño | Bataan | Cebu | Q31812379 |
| 83655 | McKinley | Bataan | Negros Oriental | Q31812386 |
| 83658 | Mendez-Nuñez | Occidental Mindoro | Cavite | Q62784 |
| 83659 | Mercedes | Albay | Camarines Norte | Q356734 |
| 83665 | Miaga | Albay | Masbate | Q31812407 |
| 83667 | Mianay | Antique | Capiz | Q31812408 |
| 83668 | Miaray | Benguet | Bukidnon | Q31812409 |
| 83686 | Minlagas | Benguet | Misamis Oriental | Q31812441 |
| 83687 | Minolos | Bataan | Cebu | Q31812442 |
| 83689 | Minuyan | Antique | Negros Occidental | Q31812444 |
| 83690 | Miranda | Antique | Negros Occidental | Q31812445 |
| 83696 | Molugan | Benguet | Misamis Oriental | Q31812455 |
| 83698 | Monbon | Albay | Sorsogon | Q31812457 |
| 83703 | Monpon | Antique | Iloilo | Q31812463 |
| 83705 | Montaneza | Bataan | Cebu | Q31812466 |
| 83706 | Montecillo | Occidental Mindoro | Quezon | Q31812467 |
| 83708 | Montilla | Antique | Negros Occidental | Q31812469 |
| 83709 | Moog | Benguet | Misamis Oriental | Q31812473 |
| 83710 | Morales | Antique | Aklan | Q31812477 |
| 83718 | Mozon | Occidental Mindoro | Batangas | Q31812501 |
| 83722 | Mulauin | Occidental Mindoro | Batangas | Q31812508 |
| 83734 | Nabangig | Albay | Masbate | Q31812521 |
| 83738 | Nabulao | Antique | Negros Occidental | Q31812523 |
| 83744 | Nagbalaye | Bataan | Negros Oriental | Q31812526 |
| 83746 | Naghalin | Batanes | Leyte | Q31812527 |
| 83756 | Nahawan | Bataan | Bohol | Q31812536 |
| 83758 | Naili | Antique | Aklan | Q31812537 |
| 83759 | Nailong | Bataan | Cebu | Q31812538 |
| 83760 | Naisud | Antique | Aklan | Q31812539 |
| 83762 | Nalundan | Bataan | Negros Oriental | Q31812541 |
| 83773 | Nangka | Bataan | Negros Oriental | Q31812575 |
| 83774 | Nangka | Antique | Negros Occidental | Q31812576 |
| 83776 | Napalitan | Benguet | Misamis Oriental | Q31812580 |
| 83777 | Napnapan | Antique | Iloilo | Q31812582 |
| 83778 | Napoles | Antique | Negros Occidental | Q31812585 |
| 83779 | Napuro | Batanes | Western Samar | Q31812586 |
| 83785 | Natalungan | Benguet | Bukidnon | Q31812592 |
| 83787 | Nato | Antique | Negros Occidental | Q31812594 |
| 83788 | Nato | Albay | Camarines Sur | Q31812593 |
| 83796 | Navotas | Occidental Mindoro | Rizal | Q31812600 |
| 83798 | Nena | Batanes | Eastern Samar | Q31812603 |
| 83799 | Nenita | Batanes | Northern Samar | Q31812604 |
| 83810 | New Pandanon | Antique | Negros Occidental | Q31812626 |
| 83823 | Novallas | Bataan | Negros Oriental | Q31812669 |
| 83826 | Nueva Fuerza | Bataan | Bohol | Q31812670 |
| 83828 | Nueva Vida Sur | Bataan | Bohol | Q31812673 |
| 83829 | Nugas | Bataan | Cebu | Q31812674 |
| 83836 | Obong | Bataan | Cebu | Q31812689 |
| 83838 | Ocaña | Bataan | Cebu | Q31812690 |
| 83839 | Ochanado | Antique | Aklan | Q31812692 |
| 83840 | Ocoy | Bataan | Cebu | Q31812695 |
| 83841 | Odala | Oriental Mindoro | Occidental Mindoro | Q31812696 |
| 83842 | Odicon | Albay | Camarines Sur | Q31812698 |
| 83843 | Odiong | Antique | Negros Occidental | Q31812701 |
| 83847 | Ogod | Albay | Sorsogon | Q31812706 |
| 83848 | Ogtongon | Antique | Negros Occidental | Q31812707 |
| 83851 | Olingan | Zamboanga Sibugay | Zamboanga del Norte | Q31812715 |
| 83854 | Ondoy | Antique | Aklan | Q31812717 |
| 83861 | Orong | Antique | Negros Occidental | Q31812725 |
| 83863 | Osiao | Albay | Sorsogon | Q31812729 |
| 83869 | Owak | Bataan | Cebu | Q31812737 |
| 83871 | Paagahan | Occidental Mindoro | Laguna | Q31812745 |
| 83873 | Paclolo | Oriental Mindoro | Occidental Mindoro | Q31812751 |
| 83884 | Padre Zamora | Bataan | Negros Oriental | Q31457212 |
| 83900 | Paiisa | Occidental Mindoro | Quezon | Q31812760 |
| 83904 | Pajo | Bataan | Cebu | Q31457983 |
| 83905 | Pakiad | Antique | Iloilo | Q31457997 |
| 83909 | Palahanan Uno | Occidental Mindoro | Batangas | Q31458075 |
| 83910 | Palali | Albay | Camarines Norte | Q31458090 |
| 83911 | Palampas | Antique | Negros Occidental | Q31458111 |
| 83913 | Palangue | Occidental Mindoro | Cavite | Q31458154 |
| 83914 | Palanit | Batanes | Northern Samar | Q31458162 |
| 83916 | Palaroo | Batanes | Leyte | Q31458200 |
| 83920 | Palestina | Albay | Camarines Sur | Q31458275 |
| 83922 | Palhi | Batanes | Leyte | Q31458296 |
| 83930 | Palsong | Albay | Camarines Sur | Q31458509 |
| 83931 | Paluan | Oriental Mindoro | Occidental Mindoro | Q107493 |
| 83936 | Pambuhan | Albay | Camarines Norte | Q31460833 |
| 83941 | Pan-an | Benguet | Misamis Occidental | Q31460979 |
| 83949 | Panalipan | Bataan | Cebu | Q31461175 |
| 83950 | Panalo-on | Benguet | Lanao del Norte | Q31461189 |
| 83955 | Panaytayon | Bataan | Bohol | Q31461351 |
| 83957 | Pancol | Oriental Mindoro | Palawan | Q31461376 |
| 83960 | Pandan | Albay | Catanduanes | Q123163 |
| 83968 | Pangabuan | Benguet | Misamis Occidental | Q31461722 |
| 83976 | Pangdan | Batanes | Western Samar | Q31461899 |
| 83979 | Panglao | Bataan | Bohol | Q178330 |
| 83981 | Pangpang | Batanes | Northern Samar | Q31462037 |
| 83982 | Panguiranan | Albay | Masbate | Q31462073 |
| 83987 | Panikihan | Occidental Mindoro | Quezon | Q31462197 |
| 83993 | Panlaitan | Oriental Mindoro | Palawan | Q31462363 |
| 83995 | Panognawan | Bataan | Cebu | Q31462401 |
| 83996 | Pansol | Occidental Mindoro | Batangas | Q31462469 |
| 83997 | Pansoy | Occidental Mindoro | Quezon | Q31462495 |
| 84002 | Pantay Na Matanda | Occidental Mindoro | Batangas | Q31462566 |
| 84003 | Pantijan No 2 | Occidental Mindoro | Cavite | Q31462853 |
| 84006 | Panubigan | Zamboanga Sibugay | Zamboanga del Sur | Q31462881 |
| 84012 | Paracale | Albay | Camarines Norte | Q356759 |
| 84014 | Paradahan | Occidental Mindoro | Cavite | Q31463131 |
| 84015 | Paraiso | Antique | Negros Occidental | Q31463205 |
| 84024 | Parion | Antique | Capiz | Q31463448 |
| 84033 | Pasong Kawayan Primero | Occidental Mindoro | Cavite | Q31463983 |
| 84038 | Patabog | Occidental Mindoro | Quezon | Q31464155 |
| 84039 | Patao | Bataan | Cebu | Q31464177 |
| 84040 | Patawag | Zamboanga Sibugay | Zamboanga del Norte | Q31464222 |
| 84045 | Patique | Antique | Negros Occidental | Q31464314 |
| 84048 | Pato-o | Oriental Mindoro | Romblon | Q31464380 |
| 84049 | Patonan | Antique | Negros Occidental | Q31464404 |
| 84050 | Patong | Batanes | Northern Samar | Q31464416 |
| 84053 | Patrocinio | Benguet | Misamis Oriental | Q31464500 |
| 84055 | Patuto | Occidental Mindoro | Cavite | Q31812775 |
| 84057 | Paulba | Albay | Camarines Sur | Q31465202 |
| 84062 | Pawican | Albay | Masbate | Q31465360 |
| 84063 | Pawili | Albay | Camarines Sur | Q31465371 |
| 84064 | Pawing | Batanes | Leyte | Q31465382 |
| 84068 | Payapa | Occidental Mindoro | Batangas | Q31465451 |
| 84070 | Paypay | Bataan | Cebu | Q31465604 |
| 84072 | Pañgobilian | Oriental Mindoro | Palawan | Q31465664 |
| 84075 | Perrelos | Bataan | Cebu | Q31466671 |
| 84076 | Peña | Albay | Masbate | Q31467063 |
| 84102 | Pinagsibaan | Occidental Mindoro | Batangas | Q31468906 |
| 84105 | Pinamopoan | Batanes | Leyte | Q31469029 |
| 84106 | Pinamungahan | Bataan | Cebu | Q316259 |
| 84108 | Pinayagan Norte | Bataan | Bohol | Q31469161 |
| 84112 | Pinit | Albay | Camarines Sur | Q31470104 |
| 84113 | Pinokawan | Bataan | Negros Oriental | Q31470569 |
| 84116 | Pinugay | Occidental Mindoro | Rizal | Q31470765 |
| 84126 | Piña | Batanes | Western Samar | Q31471724 |
| 84136 | Platagata | Antique | Iloilo | Q31472259 |
| 84141 | Polahongon | Batanes | Leyte | Q31473515 |
| 84144 | Polañge | Batanes | Northern Samar | Q31473623 |
| 84155 | Polopina | Antique | Iloilo | Q31474413 |
| 84157 | Pongol | Benguet | Bukidnon | Q31474749 |
| 84158 | Ponong | Antique | Iloilo | Q31474789 |
| 84159 | Ponot | Zamboanga Sibugay | Zamboanga del Norte | Q132520 |
| 84162 | Pontian | Benguet | Bukidnon | Q31474985 |
| 84176 | Prinza | Occidental Mindoro | Batangas | Q31478320 |
| 84177 | Progreso | Occidental Mindoro | Quezon | Q31478469 |
| 84258 | Puerto Bello | Batanes | Leyte | Q31479195 |
| 84273 | Punang | Oriental Mindoro | Palawan | Q31480161 |
| 84274 | Punao | Antique | Negros Occidental | Q31480183 |
| 84279 | Punta | Occidental Mindoro | Rizal | Q31480339 |
| 84281 | Punta | Oriental Mindoro | Romblon | Q31480382 |
| 84282 | Punta Silum | Benguet | Misamis Oriental | Q31480405 |
| 84288 | Putat | Bataan | Cebu | Q31480847 |
| 84289 | Putiao | Albay | Sorsogon | Q31480868 |
| 84290 | Puting Kahoy | Occidental Mindoro | Cavite | Q31480975 |
| 84293 | Putol | Occidental Mindoro | Batangas | Q31481101 |
| 84305 | Quilo-quilo | Occidental Mindoro | Batangas | Q31482049 |
| 84307 | Quinagaringan | Antique | Iloilo | Q31482113 |
| 84312 | Quipot | Antique | Iloilo | Q31482518 |
| 84313 | Quipot | Occidental Mindoro | Quezon | Q31482497 |
| 84316 | Quisao | Occidental Mindoro | Rizal | Q31482579 |
| 84317 | Quitang | Albay | Camarines Sur | Q31482600 |
| 84333 | Rebe | Benguet | Lanao del Norte | Q31485466 |
| 84335 | Recodo | Albay | Masbate | Q31485511 |
| 84343 | Rizal | Oriental Mindoro | Occidental Mindoro | Q107499 |
| 84348 | Rizal | Occidental Mindoro | Laguna | Q75928 |
| 84362 | Roxas | Oriental Mindoro | Palawan | Q111689 |
| 84365 | Saavedra | Bataan | Cebu | Q31497076 |
| 84366 | Sabang | Batanes | Western Samar | Q31497225 |
| 84368 | Sabang | Albay | Sorsogon | Q31497141 |
| 84371 | Sabang Indan | Albay | Camarines Norte | Q31497425 |
| 84373 | Sablayan | Oriental Mindoro | Occidental Mindoro | Q107505 |
| 84385 | Sagasa | Antique | Negros Occidental | Q31498157 |
| 84388 | Sagbayan | Bataan | Bohol | Q405472 |
| 84391 | Sagrada | Albay | Camarines Sur | Q31498429 |
| 84398 | Sagurong | Albay | Camarines Sur | Q31498613 |
| 84400 | Salamanca | Antique | Negros Occidental | Q31499316 |
| 84402 | Salawagan | Benguet | Bukidnon | Q31499398 |
| 84409 | Salimbalan | Benguet | Bukidnon | Q31499792 |
| 84417 | Salvacion | Antique | Guimaras | Q31500606 |
| 84420 | Salvacion | Batanes | Northern Samar | Q31500650 |
| 84430 | Sampagar | Benguet | Bukidnon | Q31501110 |
| 84435 | Sampiro | Occidental Mindoro | Batangas | Q31501256 |
| 84452 | San Antonio | Batanes | Northern Samar | Q175163 |
| 84467 | San Eduardo | Batanes | Eastern Samar | Q31502928 |
| 84537 | San Lucas | Albay | Camarines Sur | Q31505902 |
| 84552 | San Martin | Benguet | Misamis Oriental | Q31506287 |
| 84575 | San Pablo | Occidental Mindoro | Laguna | Q76001 |
| 84579 | San Pascual | Albay | Masbate | Q191630 |
| 84586 | San Pedro | Occidental Mindoro | Laguna | Q75933 |
| 84594 | San Rafael | Antique | Iloilo | Q275329 |
| 84599 | San Ramon | Albay | Camarines Sur | Q31507846 |
| 84606 | San Roque | Bataan | Bohol | Q31508064 |
| 84620 | San Vicente | Oriental Mindoro | Palawan | Q111707 |
| 84623 | San Vicente | Albay | Camarines Norte | Q302791 |
| 84627 | Sandayong Sur | Bataan | Cebu | Q31509402 |
| 84629 | Sandolot | Bataan | Negros Oriental | Q31509527 |
| 84632 | Sangat | Bataan | Cebu | Q31812879 |
| 84635 | Sankanan | Benguet | Bukidnon | Q31509978 |
| 84642 | Santa Angel | Antique | Capiz | Q31510180 |
| 84661 | Santa Cruz | Oriental Mindoro | Marinduque | Q107042 |
| 84664 | Santa Elena | Albay | Camarines Norte | Q356853 |
| 84671 | Santa Filomena | Bataan | Cebu | Q31511083 |
| 84676 | Santa Justina | Albay | Camarines Sur | Q31511203 |
| 84722 | Santo Niño | Batanes | Western Samar | Q608320 |
| 84750 | Saravia | Antique | Negros Occidental | Q195304 |
| 84751 | Saraza | Oriental Mindoro | Palawan | Q31513694 |
| 84759 | Seres | Zamboanga Sibugay | Zamboanga del Norte | Q31516088 |
| 84761 | Sevilla | Bataan | Bohol | Q386388 |
| 84769 | Sibaguan | Antique | Capiz | Q31518334 |
| 84772 | Sibucao | Antique | Negros Occidental | Q31518522 |
| 84781 | Sico Uno | Occidental Mindoro | Batangas | Q31518847 |
| 84783 | Sierra Bullones | Bataan | Bohol | Q405628 |
| 84788 | Sikatuna | Bataan | Bohol | Q405674 |
| 84789 | Silab | Bataan | Negros Oriental | Q31519614 |
| 84790 | Silae | Benguet | Bukidnon | Q31519647 |
| 84793 | Silanga | Batanes | Western Samar | Q31519749 |
| 84796 | Silongin | Occidental Mindoro | Quezon | Q31520022 |
| 84799 | Simala | Bataan | Cebu | Q31520255 |
| 84809 | Sinala | Occidental Mindoro | Batangas | Q31520798 |
| 84817 | Sinisian | Occidental Mindoro | Batangas | Q31521001 |
| 84819 | Sinonoc | Benguet | Misamis Occidental | Q31812885 |
| 84822 | Sinuknipan | Albay | Camarines Sur | Q31521169 |
| 84844 | Solo | Occidental Mindoro | Batangas | Q31526853 |
| 84846 | Songculan | Bataan | Bohol | Q31527012 |
| 84852 | Suay | Antique | Negros Occidental | Q31535870 |
| 84853 | Suba | Oriental Mindoro | Palawan | Q31535887 |
| 84861 | Sugod | Albay | Sorsogon | Q31536691 |
| 84865 | Sulangan | Batanes | Eastern Samar | Q31536931 |
| 84867 | Sulangan | Antique | Iloilo | Q31536915 |
| 84879 | Sumpong | Benguet | Bukidnon | Q31537787 |
| 84880 | Sungai | Benguet | Misamis Oriental | Q31538212 |
| 84892 | Tabalong | Bataan | Bohol | Q31540768 |
| 84895 | Tabid | Benguet | Misamis Occidental | Q31540931 |
| 84902 | Taboc | Benguet | Misamis Oriental | Q31541165 |
| 84908 | Tabonok | Bataan | Cebu | Q31541296 |
| 84910 | Tabu | Antique | Negros Occidental | Q31541332 |
| 84917 | Tabunok | Bataan | Cebu | Q31541517 |
| 84922 | Tacub | Benguet | Lanao del Norte | Q31541621 |
| 84933 | Tagbacan Ibaba | Occidental Mindoro | Quezon | Q31542094 |
| 84934 | Tagbak | Oriental Mindoro | Occidental Mindoro | Q31542111 |
| 84935 | Tagbilaran City | Bataan | Bohol | Q1826 |
| 84938 | Tagbubungang Diot | Batanes | Leyte | Q31542217 |
| 84955 | Tajao | Bataan | Cebu | Q31542924 |
| 84958 | Tala | Occidental Mindoro | Quezon | Q31543116 |
| 84960 | Talaban | Antique | Negros Occidental | Q31543149 |
| 84963 | Talaga | Occidental Mindoro | Batangas | Q31543198 |
| 84965 | Talahib Payap | Occidental Mindoro | Batangas | Q31543280 |
| 84968 | Talakag | Benguet | Bukidnon | Q357420 |
| 84976 | Talipan | Occidental Mindoro | Quezon | Q31543685 |
| 84980 | Talisay | Albay | Camarines Norte | Q356878 |
| 84981 | Talisay | Bataan | Cebu | Q316500 |
| 84989 | Taloc | Antique | Negros Occidental | Q31544366 |
| 84990 | Talokgañgan | Antique | Iloilo | Q31544378 |
| 84992 | Talon | Antique | Capiz | Q31544426 |
| 84997 | Talubatib | Albay | Camarines Norte | Q31544543 |
| 85006 | Tambalan | Bataan | Negros Oriental | Q31544795 |
| 85007 | Tambalisa | Antique | Iloilo | Q31544809 |
| 85009 | Tambo | Bataan | Negros Oriental | Q31544900 |
| 85010 | Tambo | Albay | Camarines Sur | Q31544885 |
| 85013 | Tambongon | Bataan | Cebu | Q31544976 |
| 85016 | Tamiso | Bataan | Negros Oriental | Q31545061 |
| 85017 | Tamlang | Antique | Negros Occidental | Q31545076 |
| 85026 | Tampocon | Bataan | Negros Oriental | Q31545284 |
| 85032 | Tandayag | Bataan | Negros Oriental | Q31545462 |
| 85034 | Tangal | Oriental Mindoro | Occidental Mindoro | Q31545546 |
| 85037 | Tangnan | Bataan | Bohol | Q31545722 |
| 85052 | Tapilon | Bataan | Cebu | Q31546409 |
| 85053 | Tapon | Bataan | Cebu | Q31546447 |
| 85054 | Tara | Albay | Camarines Sur | Q31546587 |
| 85057 | Tariric | Albay | Camarines Sur | Q31546761 |
| 85059 | Tarong | Antique | Iloilo | Q31546844 |
| 85062 | Tarusan | Oriental Mindoro | Palawan | Q31546986 |
| 85066 | Tawala | Bataan | Bohol | Q31547652 |
| 85071 | Tayaman | Oriental Mindoro | Occidental Mindoro | Q31547824 |
| 85079 | Taytayan | Bataan | Cebu | Q31548709 |
| 85080 | Tayud | Bataan | Cebu | Q31548744 |
| 85083 | Taywanak Ilaya | Occidental Mindoro | Cavite | Q31548772 |
| 85098 | Ticala-an | Benguet | Bukidnon | Q31555175 |
| 85106 | Tigbaw | Albay | Masbate | Q31555670 |
| 85107 | Tigbinan | Albay | Camarines Norte | Q31555687 |
| 85108 | Tiglauigan | Antique | Negros Occidental | Q31555844 |
| 85110 | Tignoan | Occidental Mindoro | Quezon | Q31555881 |
| 85114 | Tigui | Oriental Mindoro | Marinduque | Q31555945 |
| 85115 | Tiguib | Bataan | Negros Oriental | Q31555961 |
| 85116 | Tiguion | Oriental Mindoro | Marinduque | Q31555978 |
| 85118 | Tigum | Antique | Iloilo | Q31556010 |
| 85120 | Tilik | Oriental Mindoro | Occidental Mindoro | Q31556141 |
| 85121 | Tiling | Antique | Negros Occidental | Q31556148 |
| 85122 | Timonan | Zamboanga Sibugay | Zamboanga del Norte | Q31556509 |
| 85123 | Timpas | Antique | Capiz | Q31556529 |
| 85127 | Tinalmud | Albay | Camarines Sur | Q31556713 |
| 85129 | Tinambacan | Batanes | Western Samar | Q31556764 |
| 85132 | Tinaogan | Bataan | Negros Oriental | Q31556882 |
| 85133 | Tinawagan | Albay | Camarines Sur | Q31556914 |
| 85134 | Tindog | Bataan | Cebu | Q31556979 |
| 85137 | Tiniguiban | Oriental Mindoro | Palawan | Q31557092 |
| 85139 | Tinongan | Antique | Negros Occidental | Q31557156 |
| 85141 | Tinubuan | Bataan | Cebu | Q31557223 |
| 85146 | Tipolo | Bataan | Bohol | Q31557407 |
| 85147 | Tiring | Antique | Iloilo | Q31557561 |
| 85164 | Tomingad | Oriental Mindoro | Romblon | Q31558671 |
| 85169 | Toong | Occidental Mindoro | Batangas | Q31559109 |
| 85173 | Tortosa | Antique | Negros Occidental | Q31559430 |
| 85174 | Totolan | Bataan | Bohol | Q31559594 |
| 85176 | Tranca | Occidental Mindoro | Batangas | Q31560255 |
| 85177 | Trapiche | Antique | Iloilo | Q31560282 |
| 85179 | Trinidad | Bataan | Bohol | Q405749 |
| 85189 | Tubigagmanoc | Bataan | Cebu | Q31562320 |
| 85190 | Tubigan | Benguet | Misamis Oriental | Q31562338 |
| 85192 | Tubli | Albay | Catanduanes | Q31562406 |
| 85204 | Tudela | Benguet | Misamis Occidental | Q196248 |
| 85207 | Tugas | Antique | Aklan | Q31562990 |
| 85209 | Tugbong | Batanes | Leyte | Q31563055 |
| 85210 | Tugdan | Oriental Mindoro | Romblon | Q31563071 |
| 85211 | Tugos | Albay | Camarines Norte | Q31563103 |
| 85213 | Tuhian | Occidental Mindoro | Quezon | Q31563137 |
| 85215 | Tulay | Occidental Mindoro | Cavite | Q31563233 |
| 85216 | Tulay na Lupa | Albay | Camarines Norte | Q31563251 |
| 85219 | Tumalaytay | Albay | Masbate | Q31563551 |
| 85221 | Tumarbong | Oriental Mindoro | Palawan | Q31563633 |
| 85224 | Tumcon Ilawod | Antique | Iloilo | Q31563767 |
| 85230 | Tuod | Benguet | Misamis Oriental | Q31564079 |
| 85233 | Tupsan | Benguet | Camiguin | Q31564193 |
| 85234 | Tutay | Bataan | Cebu | Q31565553 |
| 85235 | Tutubigan | Batanes | Western Samar | Q31565602 |
| 85240 | Ualog | Antique | Negros Occidental | Q31567264 |
| 85241 | Ubay | Bataan | Bohol | Q406015 |
| 85248 | Umaganhan | Batanes | Leyte | Q31567618 |
| 85256 | Unidos | Benguet | Misamis Occidental | Q31567943 |
| 85258 | Union | Bataan | Cebu | Q31568039 |
| 85269 | Usab | Albay | Masbate | Q31569869 |
| 85270 | Uson | Albay | Masbate | Q191636 |
| 85271 | Utabi | Albay | Sorsogon | Q31569980 |
| 85283 | Victoria | Batanes | Northern Samar | Q175283 |
| 85284 | Victoria | Occidental Mindoro | Laguna | Q75953 |
| 85287 | Viejo Daan Banua | Antique | Negros Occidental | Q31572633 |
| 85291 | Vigo | Oriental Mindoro | Occidental Mindoro | Q31572791 |
| 85304 | Vinzons | Albay | Camarines Norte | Q356898 |
| 85306 | Viriato | Batanes | Northern Samar | Q31573865 |
| 85307 | Vista Alegre | Antique | Negros Occidental | Q31573897 |
| 85309 | Vito | Antique | Negros Occidental | Q31574008 |
| 85313 | Wawa | Oriental Mindoro | Occidental Mindoro | Q31580136 |
| 85314 | Wawa | Occidental Mindoro | Batangas | Q31580103 |
| 85317 | Wright | Batanes | Western Samar | Q31593711 |
| 85320 | Yook | Oriental Mindoro | Marinduque | Q31595451 |
| 85321 | Yubo | Antique | Negros Occidental | Q31595888 |
| 85322 | Yumbing | Benguet | Camiguin | Q31595966 |
| 85323 | Yuni | Occidental Mindoro | Quezon | Q31595996 |
| 143939 | Dualing | Bukidnon | Cotabato | Q31571737 |
| 143941 | Dunguan | Bukidnon | Cotabato | Q31573114 |
| 143946 | Glad | Bukidnon | Cotabato | Q31457955 |
| 143947 | Glamang | Bukidnon | South Cotabato | Q31457985 |
| 143955 | Kabalen | Bukidnon | South Cotabato | Q31811566 |
| 143957 | Kalaisan | Bukidnon | Cotabato | Q31811580 |
| 143958 | Kalamangog | Bukidnon | Sultan Kudarat | Q31811582 |
| 143968 | Kisante | Bukidnon | Cotabato | Q31811654 |
| 143970 | Klinan | Bukidnon | South Cotabato | Q31811664 |
| 143975 | Labu-o | Bukidnon | Cotabato | Q31811723 |
| 143980 | Lambontong | Bukidnon | South Cotabato | Q31811762 |
| 143981 | Lamian | Bukidnon | South Cotabato | Q31811763 |
| 143983 | Lampitak | Bukidnon | South Cotabato | Q31811769 |
| 143991 | Liliongan | Bukidnon | Cotabato | Q31811878 |
| 143992 | Limbalod | Bukidnon | Cotabato | Q31811888 |
| 143993 | Limulan | Bukidnon | Sultan Kudarat | Q31811897 |
| 143995 | Linao | Bukidnon | Cotabato | Q31811906 |
| 144001 | Lunen | Bukidnon | South Cotabato | Q31812007 |
| 144003 | M'lang | Bukidnon | Cotabato | Q315213 |
| 144015 | Malamote | Bukidnon | Cotabato | Q31812141 |
| 144017 | Malapag | Bukidnon | Cotabato | Q31812146 |
| 144019 | Malasila | Bukidnon | Cotabato | Q31812150 |
| 144022 | Malisbeng | Bukidnon | Sultan Kudarat | Q31812183 |
| 144023 | Malitubog | Bukidnon | Cotabato | Q31812186 |
| 144029 | Manuangan | Bukidnon | Cotabato | Q31812272 |
| 144036 | Minapan | Bukidnon | Cotabato | Q31812431 |
| 144039 | New Cebu | Bukidnon | Cotabato | Q31812613 |
| 144043 | Noling | Bukidnon | Sultan Kudarat | Q31812653 |
| 144047 | Paatan | Bukidnon | Cotabato | Q31812747 |
| 144049 | Pagangan | Bukidnon | Cotabato | Q31457641 |
| 144052 | Palkan | Bukidnon | South Cotabato | Q31458353 |
| 144055 | Pangyan | Bukidnon | Sarangani | Q31462122 |
| 144057 | Patindeguen | Bukidnon | Cotabato | Q31464304 |
| 144068 | Puloypuloy | Bukidnon | Sultan Kudarat | Q31479916 |
| 144069 | Punolu | Bukidnon | Cotabato | Q31480317 |
| 144070 | Puricay | Bukidnon | Sultan Kudarat | Q31480656 |
| 144071 | Ragandang | Bukidnon | Sultan Kudarat | Q31483266 |
| 144074 | Saguing | Bukidnon | Cotabato | Q31498553 |
| 144080 | Santo Niño | Bukidnon | South Cotabato | Q31512848 |
| 144082 | Sapu Padidu | Bukidnon | Sarangani | Q31513504 |
| 144084 | Sebu | Bukidnon | South Cotabato | Q31515335 |
| 144085 | Silway 7 | Bukidnon | South Cotabato | Q31520234 |
| 144086 | Sinolon | Bukidnon | South Cotabato | Q31521071 |
| 144087 | Sulit | Bukidnon | South Cotabato | Q31537011 |
| 144092 | Taguisa | Bukidnon | Sultan Kudarat | Q31542699 |
| 144103 | Tomado | Bukidnon | Cotabato | Q31558503 |
| 144104 | Tran | Bukidnon | Sultan Kudarat | Q31560240 |
| 144108 | Tuyan | Bukidnon | Sarangani | Q31565668 |
| 144109 | Upper Klinan | Bukidnon | South Cotabato | Q31569431 |
| 144110 | Upper San Mateo | Bukidnon | Cotabato | Q31569595 |
| 144124 | Bansalan | Bohol | Davao del Sur | Q314778 |
| 144151 | Carmen | Bohol | Davao del Norte | Q314422 |
| 144216 | Mabini | Bohol | Davao de Oro | Q187225 |
| 144224 | Magsaysay | Bohol | Davao del Sur | Q314864 |
| 144287 | Santa Cruz | Bohol | Davao del Sur | Q314965 |
| 144334 | Amas | Bukidnon | Cotabato | Q31465342 |
| 144335 | Bagontapay | Bukidnon | Cotabato | Q31796144 |
| 144336 | Baguer | Bukidnon | Cotabato | Q31475802 |
| 144339 | Balogo | Bukidnon | Cotabato | Q31481612 |
| 144340 | Banawa | Bukidnon | Cotabato | Q31796268 |
| 144344 | Bantogon | Bukidnon | Sultan Kudarat | Q31485148 |
| 144346 | Basak | Bukidnon | Sultan Kudarat | Q31488188 |
| 144348 | Batutitik | Bukidnon | South Cotabato | Q31491210 |
| 144349 | Bau | Bukidnon | Cotabato | Q31491255 |
| 144351 | Bialong | Bukidnon | Cotabato | Q31498182 |
| 144355 | Bual | Bukidnon | Cotabato | Q31514458 |
| 144360 | Bulatukan | Bukidnon | Cotabato | Q31517523 |
| 144366 | City of Kidapawan | Bukidnon | Cotabato | Q31545067 |
| 144367 | City of Koronadal | Bukidnon | South Cotabato | Q31545081 |
| 144368 | City of Tacurong | Bukidnon | Sultan Kudarat | Q31545405 |
| 144369 | Colongolo | Bukidnon | South Cotabato | Q31549980 |
| 144371 | Agay | Bulacan | Agusan del Norte | Q31462038 |
| 144375 | Amaga | Bulacan | Surigao del Sur | Q31465217 |
| 144377 | Aras-asan | Bulacan | Surigao del Sur | Q31468241 |
| 144381 | Bah-Bah | Bulacan | Agusan del Sur | Q31476198 |
| 144382 | Balangbalang | Bulacan | Agusan del Norte | Q31478228 |
| 144384 | Bangonay | Bulacan | Agusan del Norte | Q31483691 |
| 144387 | Basa | Bulacan | Agusan del Sur | Q31488101 |
| 144389 | Bayabas | Bulacan | Surigao del Sur | Q155499 |
| 144392 | Bigaan | Bulacan | Surigao del Sur | Q31500778 |
| 144393 | Binucayan | Bulacan | Agusan del Sur | Q31503087 |
| 144413 | Causwagan | Bulacan | Agusan del Sur | Q31538266 |
| 144416 | Comagascas | Bulacan | Agusan del Norte | Q31550282 |
| 144419 | Culit | Bulacan | Agusan del Norte | Q31557218 |
| 144420 | Dakbayan sa Bislig | Bulacan | Surigao del Sur | Q31559049 |
| 144432 | Guinabsan | Bulacan | Agusan del Norte | Q31811362 |
| 144436 | Jagupit | Bulacan | Agusan del Norte | Q31811530 |
| 144439 | Kinabhangan | Bulacan | Agusan del Norte | Q31811645 |
| 144445 | Lapinigan | Bulacan | Agusan del Sur | Q31811799 |
| 144446 | Las Nieves | Bulacan | Agusan del Norte | Q627529 |
| 144456 | Los Arcos | Bulacan | Agusan del Sur | Q31811956 |
| 144457 | Loyola | Bulacan | Surigao del Sur | Q31811962 |
| 144459 | Mabahin | Bulacan | Surigao del Sur | Q31812034 |
| 144465 | Manapa | Bulacan | Agusan del Norte | Q31812226 |
| 144467 | Matabao | Bulacan | Agusan del Norte | Q31812333 |
| 144469 | Maygatasan | Bulacan | Agusan del Sur | Q31812374 |
| 144472 | Panikian | Bulacan | Surigao del Sur | Q31462171 |
| 144478 | Punta | Bulacan | Agusan del Norte | Q31480360 |
| 144485 | San Agustin | Bulacan | Surigao del Sur | Q155618 |
| 144488 | San Francisco | Bulacan | Agusan del Sur | Q627190 |
| 144496 | Sanghan | Bulacan | Agusan del Norte | Q31509883 |
| 144503 | Santiago | Bulacan | Agusan del Norte | Q588955 |
| 144506 | Sinubong | Bulacan | Agusan del Sur | Q31521133 |
| 144512 | Tagcatong | Bulacan | Agusan del Norte | Q31542280 |
| 144514 | Talacogon | Bulacan | Agusan del Sur | Q627286 |
| 144519 | Tidman | Bulacan | Surigao del Sur | Q31555326 |
| 144525 | Unidad | Bulacan | Surigao del Sur | Q31567927 |
| 144528 | Idtig | Cagayan | Maguindanao del Sur | Q31811469 |
| 144534 | Kagay | Cagayan | Sulu | Q31811578 |
| 144535 | Kajatian | Cagayan | Sulu | Q31811579 |
| 144536 | Kalang | Cagayan | Sulu | Q31811585 |
| 144539 | Kambing | Cagayan | Sulu | Q31811601 |
| 144540 | Kanlagay | Cagayan | Sulu | Q31811605 |
| 144541 | Kansipati | Cagayan | Sulu | Q31811607 |
| 144544 | Karungdong | Cagayan | Sulu | Q31811615 |
| 144546 | Katidtuan | Cagayan | Maguindanao del Norte | Q31811618 |
| 144547 | Katuli | Cagayan | Maguindanao del Norte | Q31811624 |
| 144549 | Kitango | Cagayan | Maguindanao del Sur | Q31811657 |
| 144550 | Kitapak | Cagayan | Maguindanao del Sur | Q31811658 |
| 144551 | Kolape | Cagayan | Tawi-Tawi | Q31811670 |
| 144552 | Kulase | Cagayan | Sulu | Q31811683 |
| 144553 | Kulay-Kulay | Cagayan | Sulu | Q31811684 |
| 144554 | Kulempang | Cagayan | Maguindanao del Norte | Q31811685 |
| 144555 | Kungtad | Cagayan | Sulu | Q31811688 |
| 144556 | Labuñgan | Cagayan | Maguindanao del Norte | Q31811725 |
| 144557 | Laminusa | Cagayan | Sulu | Q31811764 |
| 144560 | Langpas | Cagayan | Sulu | Q31811779 |
| 144562 | Larap | Cagayan | Tawi-Tawi | Q31811807 |
| 144563 | Latung | Cagayan | Sulu | Q31811812 |
| 144564 | Layog | Cagayan | Maguindanao del Sur | Q31811821 |
| 144565 | Ligayan | Cagayan | Tawi-Tawi | Q31811876 |
| 144566 | Limbo | Cagayan | Maguindanao del Norte | Q31811889 |
| 144568 | Lookan | Cagayan | Tawi-Tawi | Q31811945 |
| 144571 | Lumbac | Cagayan | Lanao del Sur | Q31811987 |
| 144580 | Mahala | Cagayan | Sulu | Q31812106 |
| 144582 | Makir | Cagayan | Maguindanao del Norte | Q31812121 |
| 144585 | Manubul | Cagayan | Sulu | Q31812273 |
| 144590 | Marsada | Cagayan | Sulu | Q31812309 |
| 144594 | Mataya | Cagayan | Maguindanao del Norte | Q31812340 |
| 144595 | Mauboh | Cagayan | Sulu | Q31812360 |
| 144596 | Mileb | Cagayan | Maguindanao del Sur | Q31812417 |
| 144599 | Municipality of Lantawan | Cagayan | Basilan | Q31814341 |
| 144601 | Municipality of Sultan Gumander | Cagayan | Lanao del Sur | Q31814404 |
| 144604 | New Panamao | Cagayan | Sulu | Q31814447 |
| 144605 | Nuyo | Cagayan | Maguindanao del Norte | Q31812678 |
| 144606 | Old Panamao | Cagayan | Sulu | Q156107 |
| 144610 | Andalan | Cagayan | Sulu | Q31466155 |
| 144611 | Anuling | Cagayan | Sulu | Q31467461 |
| 144612 | Awang | Cagayan | Maguindanao del Norte | Q31471303 |
| 144613 | Bacayawan | Cagayan | Lanao del Sur | Q31796124 |
| 144614 | Bacolod Grande | Cagayan | Lanao del Sur | Q31473698 |
| 144616 | Badak | Cagayan | Maguindanao del Sur | Q31474248 |
| 144617 | Bagan | Cagayan | Maguindanao del Sur | Q31475063 |
| 144627 | Pandakan | Cagayan | Sulu | Q31461425 |
| 144628 | Baka | Cagayan | Maguindanao del Norte | Q31476872 |
| 144629 | Bakung | Cagayan | Tawi-Tawi | Q31796194 |
| 144631 | Balas | Cagayan | Basilan | Q31478523 |
| 144634 | Bangkal | Cagayan | Sulu | Q31483604 |
| 144636 | Bankaw | Cagayan | Tawi-Tawi | Q31484136 |
| 144638 | Barurao | Cagayan | Maguindanao del Sur | Q31488037 |
| 144640 | Baunu-Timbangan | Cagayan | Sulu | Q31796474 |
| 144641 | Bawison | Cagayan | Sulu | Q31491687 |
| 144644 | Begang | Cagayan | Basilan | Q31495237 |
| 144646 | Binuang | Cagayan | Sulu | Q31502946 |
| 144647 | Blinsung | Cagayan | Maguindanao del Norte | Q31505825 |
| 144651 | Bualan | Cagayan | Lanao del Sur | Q31514490 |
| 144655 | Buansa | Cagayan | Sulu | Q31514619 |
| 144657 | Budta | Cagayan | Maguindanao del Norte | Q31515760 |
| 144660 | Pang | Cagayan | Sulu | Q31461710 |
| 144666 | Parian Dakula | Cagayan | Sulu | Q31463416 |
| 144667 | Pata | Cagayan | Sulu | Q156225 |
| 144668 | Bugasan | Cagayan | Maguindanao del Norte | Q31516465 |
| 144677 | Colonia | Cagayan | Basilan | Q31550016 |
| 144678 | Dado | Cagayan | Maguindanao del Sur | Q31558386 |
| 144679 | Dadus | Cagayan | Maguindanao del Norte | Q31558404 |
| 144680 | Dalican | Cagayan | Maguindanao del Sur | Q31559874 |
| 144681 | Dalumangcob | Cagayan | Maguindanao del Norte | Q31560132 |
| 144682 | Damabalas | Cagayan | Maguindanao del Sur | Q31560626 |
| 144683 | Damatulan | Cagayan | Maguindanao del Sur | Q31560642 |
| 144688 | Digal | Cagayan | Maguindanao del Sur | Q31566837 |
| 144690 | Dinganen | Cagayan | Maguindanao del Norte | Q31567872 |
| 144695 | Gang | Cagayan | Maguindanao del Norte | Q31588598 |
| 144696 | Guiong | Cagayan | Basilan | Q31811376 |
| 144698 | Pawak | Cagayan | Lanao del Sur | Q31465336 |
| 144699 | Payuhan | Cagayan | Sulu | Q31465652 |
| 144701 | Pidsandawan | Cagayan | Maguindanao del Sur | Q31467725 |
| 144702 | Pinaring | Cagayan | Maguindanao del Norte | Q31469100 |
| 144706 | Punay | Cagayan | Sulu | Q31480205 |
| 144707 | Rimpeso | Cagayan | Maguindanao del Norte | Q31488764 |
| 144711 | Sambuluan | Cagayan | Maguindanao del Sur | Q31500985 |
| 144712 | Sanga-Sanga | Cagayan | Tawi-Tawi | Q31509803 |
| 144714 | Sapa | Cagayan | Tawi-Tawi | Q31513250 |
| 144716 | Sapadun | Cagayan | Maguindanao del Norte | Q31513320 |
| 144717 | Satan | Cagayan | Maguindanao del Sur | Q31513807 |
| 144718 | Semut | Cagayan | Basilan | Q31515925 |
| 144721 | Simuay | Cagayan | Maguindanao del Norte | Q31520646 |
| 144723 | Sionogan | Cagayan | Sulu | Q31521243 |
| 144733 | Tabiauan | Cagayan | Sulu | Q31540914 |
| 144735 | Tairan Camp | Cagayan | Basilan | Q31542874 |
| 144742 | Tapayan | Cagayan | Maguindanao del Norte | Q31546273 |
| 144743 | Tapikan | Cagayan | Maguindanao del Sur | Q31546392 |
| 144747 | Taungoh | Cagayan | Tawi-Tawi | Q31547533 |
| 144748 | Taviran | Cagayan | Maguindanao del Norte | Q31547601 |
| 144751 | Tongouson | Cagayan | Tawi-Tawi | Q31558946 |
| 144756 | Tumbagaan | Cagayan | Tawi-Tawi | Q31563718 |
| 144757 | Tunggol | Cagayan | Sulu | Q31563984 |
| 144758 | Tungol | Cagayan | Maguindanao del Sur | Q31563999 |
| 144760 | Ungus-Ungus | Cagayan | Tawi-Tawi | Q31567911 |
| 144762 | Uyaan | Cagayan | Lanao del Sur | Q31570060 |
| 144764 | Ambuclao | Camarines Norte | Benguet | Q31465455 |
| 144765 | Amlimay | Camarines Norte | Benguet | Q31465690 |
| 144766 | Ampusungan | Camarines Norte | Benguet | Q31465740 |
| 144767 | Angad | Camarines Norte | Abra | Q31466484 |
| 144768 | Atok | Camarines Norte | Benguet | Q30104 |
| 144769 | Baculongan | Camarines Norte | Benguet | Q31474139 |
| 144770 | Baguinge | Camarines Norte | Ifugao | Q31475822 |
| 144772 | Bakun | Camarines Norte | Benguet | Q30325 |
| 144775 | Bangao | Camarines Norte | Benguet | Q31483427 |
| 144782 | Betwagan | Camarines Norte | Mountain Province | Q31497947 |
| 144783 | Bocos | Camarines Norte | Ifugao | Q31507591 |
| 144784 | Bokod | Camarines Norte | Benguet | Q30328 |
| 144788 | Bucloc | Camarines Norte | Abra | Q28030 |
| 144792 | Calaba | Camarines Norte | Abra | Q31526217 |
| 144796 | Daguioman | Camarines Norte | Abra | Q28044 |
| 144797 | Dalipey | Camarines Norte | Benguet | Q31559922 |
| 144798 | Dalupirip | Camarines Norte | Benguet | Q31560195 |
| 144804 | Hapao | Camarines Norte | Ifugao | Q31811419 |
| 144808 | Itogon | Camarines Norte | Benguet | Q30335 |
| 144809 | Kabayan | Camarines Norte | Benguet | Q30338 |
| 144811 | Kapangan | Camarines Norte | Benguet | Q30345 |
| 144815 | La Trinidad | Camarines Norte | Benguet | Q30351 |
| 144816 | Lacub | Camarines Norte | Abra | Q29007 |
| 144826 | Loacan | Camarines Norte | Benguet | Q31811930 |
| 144830 | Malibcong | Camarines Norte | Abra | Q29069 |
| 144832 | Mankayan | Camarines Norte | Benguet | Q30356 |
| 144834 | Monamon | Camarines Norte | Mountain Province | Q31812456 |
| 144835 | Nangalisan | Camarines Norte | Benguet | Q31812565 |
| 144837 | Natubleng | Camarines Norte | Benguet | Q31812596 |
| 144841 | Pidigan | Camarines Norte | Abra | Q29102 |
| 144844 | Potia | Camarines Norte | Ifugao | Q31476548 |
| 144848 | Sablan | Camarines Norte | Benguet | Q30358 |
| 144850 | Sadsadan | Camarines Norte | Mountain Province | Q31497987 |
| 144853 | San Isidro | Camarines Norte | Abra | Q801530 |
| 144858 | Tabaan | Camarines Norte | Benguet | Q31540712 |
| 144862 | Tacadang | Camarines Norte | Benguet | Q31541533 |
| 144864 | Taloy | Camarines Norte | Benguet | Q31544478 |
| 144866 | Tayum | Camarines Norte | Abra | Q29139 |
| 144867 | Tineg | Camarines Norte | Abra | Q29146 |
| 144870 | Topdac | Camarines Norte | Benguet | Q31559128 |
| 144872 | Tublay | Camarines Norte | Benguet | Q30363 |
| 144874 | Tuding | Camarines Norte | Benguet | Q31562922 |
| 145098 | Abut | Agusan del Norte | Isabela | Q31461315 |
| 145100 | Afusing Centro | Agusan del Norte | Cagayan | Q31461913 |
| 145102 | Alabug | Agusan del Norte | Cagayan | Q31462925 |
| 145103 | Alannay | Agusan del Norte | Cagayan | Q31463264 |
| 145106 | Alicia | Agusan del Norte | Isabela | Q49354 |
| 145107 | Allacapan | Agusan del Norte | Cagayan | Q43508 |
| 145108 | Almaguer North | Agusan del Norte | Nueva Vizcaya | Q31464719 |
| 145110 | Amulung | Agusan del Norte | Cagayan | Q43515 |
| 145112 | Antagan Segunda | Agusan del Norte | Isabela | Q31467011 |
| 145113 | Aparri | Agusan del Norte | Cagayan | Q43517 |
| 145115 | Atulayan | Agusan del Norte | Cagayan | Q31470354 |
| 145117 | Awallan | Agusan del Norte | Cagayan | Q31471279 |
| 145118 | Bacnor East | Agusan del Norte | Isabela | Q31473363 |
| 145120 | Baggabag B | Agusan del Norte | Nueva Vizcaya | Q31475378 |
| 145126 | Ballesteros | Agusan del Norte | Cagayan | Q49058 |
| 145128 | Bangad | Agusan del Norte | Isabela | Q31483277 |
| 145129 | Banganan | Agusan del Norte | Nueva Vizcaya | Q31483405 |
| 145130 | Banquero | Agusan del Norte | Isabela | Q31484597 |
| 145131 | Barucboc Norte | Agusan del Norte | Isabela | Q31487940 |
| 145132 | Basco | Agusan del Norte | Batanes | Q43180 |
| 145134 | Battung | Agusan del Norte | Cagayan | Q31490943 |
| 145137 | Belance | Agusan del Norte | Nueva Vizcaya | Q31495281 |
| 145139 | Binalan | Agusan del Norte | Cagayan | Q31501811 |
| 145141 | Bintawan | Agusan del Norte | Nueva Vizcaya | Q31502863 |
| 145142 | Bitag Grande | Agusan del Norte | Cagayan | Q31503878 |
| 145145 | Buliwao | Agusan del Norte | Nueva Vizcaya | Q31517827 |
| 145146 | Bulu | Agusan del Norte | Isabela | Q31518229 |
| 145149 | Busilak | Agusan del Norte | Nueva Vizcaya | Q31520346 |
| 145151 | Cabannungan Second | Agusan del Norte | Isabela | Q31522933 |
| 145152 | Cabaritan East | Agusan del Norte | Cagayan | Q31523036 |
| 145155 | Cabiraoan | Agusan del Norte | Cagayan | Q31523644 |
| 145156 | Calamagui East | Agusan del Norte | Isabela | Q31526725 |
| 145157 | Calantac | Agusan del Norte | Cagayan | Q31527116 |
| 145158 | Calaoagan | Agusan del Norte | Cagayan | Q31527172 |
| 145159 | Calayan | Agusan del Norte | Cagayan | Q49062 |
| 145160 | Calinaoan Malasin | Agusan del Norte | Isabela | Q31528319 |
| 145161 | Calog Norte | Agusan del Norte | Cagayan | Q31528622 |
| 145162 | Camalaniugan | Agusan del Norte | Cagayan | Q49313 |
| 145163 | Capissayan Sur | Agusan del Norte | Cagayan | Q31533175 |
| 145165 | Casambalangan | Agusan del Norte | Cagayan | Q31536158 |
| 145166 | Catayauan | Agusan del Norte | Cagayan | Q31537465 |
| 145170 | Cullalabo del Sur | Agusan del Norte | Isabela | Q31557235 |
| 145172 | Dalaoig | Agusan del Norte | Cagayan | Q31559752 |
| 145173 | Daragutan | Agusan del Norte | Isabela | Q31562001 |
| 145174 | Dassun | Agusan del Norte | Cagayan | Q31562368 |
| 145177 | Diamantina | Agusan del Norte | Isabela | Q31565915 |
| 145178 | Dibuluan | Agusan del Norte | Isabela | Q31566298 |
| 145179 | Dicabisagan | Agusan del Norte | Isabela | Q31566380 |
| 145180 | Dicamay | Agusan del Norte | Isabela | Q31566461 |
| 145185 | Dodan | Agusan del Norte | Cagayan | Q31569067 |
| 145191 | Eden | Agusan del Norte | Isabela | Q31575500 |
| 145192 | Enrile | Agusan del Norte | Cagayan | Q49315 |
| 145194 | Estefania | Agusan del Norte | Cagayan | Q31579409 |
| 145195 | Furao | Agusan del Norte | Isabela | Q31587261 |
| 145196 | Gadu | Agusan del Norte | Cagayan | Q31587779 |
| 145197 | Gammad | Agusan del Norte | Cagayan | Q31588396 |
| 145199 | Ganapi | Agusan del Norte | Isabela | Q31588494 |
| 145200 | Gappal | Agusan del Norte | Isabela | Q31588778 |
| 145201 | Gattaran | Agusan del Norte | Cagayan | Q31589448 |
| 145202 | Gonzaga | Agusan del Norte | Cagayan | Q49317 |
| 145203 | Guiddam | Agusan del Norte | Cagayan | Q31811353 |
| 145205 | Iguig | Agusan del Norte | Cagayan | Q49318 |
| 145208 | Ineangan | Agusan del Norte | Nueva Vizcaya | Q31811501 |
| 145209 | Itbayat | Agusan del Norte | Batanes | Q43451 |
| 145210 | Ivana | Agusan del Norte | Batanes | Q43454 |
| 145215 | Lal-lo | Agusan del Norte | Cagayan | Q49320 |
| 145217 | Lallayug | Agusan del Norte | Cagayan | Q31811756 |
| 145218 | Lanna | Agusan del Norte | Cagayan | Q31811787 |
| 145219 | Lapi | Agusan del Norte | Cagayan | Q31811798 |
| 145220 | Larion Alto | Agusan del Norte | Cagayan | Q31811808 |
| 145221 | Lasam | Agusan del Norte | Cagayan | Q49321 |
| 145223 | Luna | Agusan del Norte | Isabela | Q49375 |
| 145224 | Mabasa | Agusan del Norte | Nueva Vizcaya | Q31812035 |
| 145226 | Mabuttal East | Agusan del Norte | Cagayan | Q31812055 |
| 145228 | Maddarulug Norte | Agusan del Norte | Cagayan | Q31812071 |
| 145230 | Magalalag | Agusan del Norte | Cagayan | Q31812077 |
| 145232 | Maguilling | Agusan del Norte | Cagayan | Q31812100 |
| 145233 | Mahatao | Agusan del Norte | Batanes | Q43458 |
| 145234 | Malasin | Agusan del Norte | Nueva Vizcaya | Q31812152 |
| 145237 | Maluno Sur | Agusan del Norte | Isabela | Q31812196 |
| 145238 | Manaring | Agusan del Norte | Isabela | Q31812227 |
| 145239 | Manga | Agusan del Norte | Cagayan | Q31812243 |
| 145240 | Masaya Sur | Agusan del Norte | Isabela | Q31812323 |
| 145241 | Masipi West | Agusan del Norte | Isabela | Q31812325 |
| 145242 | Maxingal | Agusan del Norte | Cagayan | Q31812367 |
| 145243 | Minallo | Agusan del Norte | Isabela | Q31812427 |
| 145244 | Minanga Norte | Agusan del Norte | Isabela | Q31812429 |
| 145246 | Minante Segundo | Agusan del Norte | Isabela | Q31812430 |
| 145247 | Minuri | Agusan del Norte | Isabela | Q31812443 |
| 145248 | Mozzozzin Sur | Agusan del Norte | Isabela | Q31812502 |
| 145249 | Mungo | Agusan del Norte | Cagayan | Q31812509 |
| 145252 | Nabannagan West | Agusan del Norte | Cagayan | Q31812522 |
| 145253 | Nagrumbuan | Agusan del Norte | Isabela | Q31812530 |
| 145256 | Namuac | Agusan del Norte | Cagayan | Q31812553 |
| 145257 | Nattapian | Agusan del Norte | Cagayan | Q31812595 |
| 145258 | Paddaya | Agusan del Norte | Cagayan | Q31812758 |
| 145261 | Palanan | Agusan del Norte | Isabela | Q50102 |
| 145263 | Pangal Sur | Agusan del Norte | Isabela | Q31461736 |
| 145265 | Pattao | Agusan del Norte | Cagayan | Q31464513 |
| 145266 | Peñablanca | Agusan del Norte | Cagayan | Q49327 |
| 145267 | Piat | Agusan del Norte | Cagayan | Q49331 |
| 145268 | Pinoma | Agusan del Norte | Isabela | Q31470592 |
| 145271 | Quibal | Agusan del Norte | Cagayan | Q31481922 |
| 145273 | Ragan Norte | Agusan del Norte | Isabela | Q31483245 |
| 145277 | Rizal | Agusan del Norte | Cagayan | Q49333 |
| 145280 | Sabtang | Agusan del Norte | Batanes | Q43460 |
| 145283 | Salinungan Proper | Agusan del Norte | Isabela | Q31499877 |
| 145284 | San Agustin | Agusan del Norte | Isabela | Q50158 |
| 145297 | San Mateo | Agusan del Norte | Isabela | Q50171 |
| 145302 | Sanchez Mira | Agusan del Norte | Cagayan | Q49336 |
| 145303 | Sandiat Centro | Agusan del Norte | Isabela | Q31509509 |
| 145304 | Santa Ana | Agusan del Norte | Cagayan | Q49337 |
| 145309 | Santa Praxedes | Agusan del Norte | Cagayan | Q49339 |
| 145311 | Santiago | Agusan del Norte | Isabela | Q50180 |
| 145313 | Santo Niño | Agusan del Norte | Cagayan | Q49346 |
| 145316 | Siempre Viva | Agusan del Norte | Isabela | Q31518935 |
| 145317 | Sillawit | Agusan del Norte | Isabela | Q31519951 |
| 145318 | Simanu Sur | Agusan del Norte | Isabela | Q31520316 |
| 145319 | Simimbaan | Agusan del Norte | Isabela | Q31520382 |
| 145320 | Sinamar | Agusan del Norte | Isabela | Q31520814 |
| 145321 | Sindon | Agusan del Norte | Isabela | Q31520918 |
| 145322 | Solana | Agusan del Norte | Cagayan | Q49348 |
| 145324 | Soyung | Agusan del Norte | Isabela | Q31528868 |
| 145325 | Taguing | Agusan del Norte | Cagayan | Q31542683 |
| 145326 | Tapel | Agusan del Norte | Cagayan | Q31546308 |
| 145327 | Tuao | Agusan del Norte | Cagayan | Q49350 |
| 145332 | Tupang | Agusan del Norte | Cagayan | Q31564096 |
| 145333 | Uddiawan | Agusan del Norte | Nueva Vizcaya | Q31567440 |
| 145334 | Ugac Sur | Agusan del Norte | Cagayan | Q31567455 |
| 145335 | Ugad | Agusan del Norte | Isabela | Q31567471 |
| 145337 | Uyugan | Agusan del Norte | Batanes | Q43469 |
| 145339 | Yeban Norte | Agusan del Norte | Isabela | Q31594849 |
| 145340 | Acli | Agusan del Sur | Pampanga | Q31461479 |
| 145341 | Agbannawag | Agusan del Sur | Nueva Ecija | Q31462071 |
| 145342 | Akle | Agusan del Sur | Bulacan | Q31462738 |
| 145344 | Alua | Agusan del Sur | Nueva Ecija | Q31465032 |
| 145345 | Amacalan | Agusan del Sur | Tarlac | Q31465168 |
| 145346 | Amucao | Agusan del Sur | Tarlac | Q31465766 |
| 145347 | Amuñgan | Agusan del Sur | Zambales | Q31465795 |
| 145350 | Angat | Agusan del Sur | Bulacan | Q54551 |
| 145355 | Arenas | Agusan del Sur | Pampanga | Q31468478 |
| 145356 | Arminia | Agusan del Sur | Tarlac | Q31468884 |
| 145359 | Bacsay | Agusan del Sur | Tarlac | Q31473913 |
| 145360 | Bagac | Agusan del Sur | Bataan | Q54456 |
| 145361 | Bagong Barrio | Agusan del Sur | Bulacan | Q31475521 |
| 145362 | Bagong-Sikat | Agusan del Sur | Nueva Ecija | Q31475648 |
| 145363 | Bahay Pare | Agusan del Sur | Pampanga | Q31476263 |
| 145364 | Bakulong | Agusan del Sur | Tarlac | Q31477373 |
| 145365 | Balagtas | Agusan del Sur | Bulacan | Q54553 |
| 145366 | Balanga | Agusan del Sur | Bataan | Q1719 |
| 145368 | Balas | Agusan del Sur | Pampanga | Q31478546 |
| 145369 | Balasing | Agusan del Sur | Bulacan | Q31478625 |
| 145372 | Balingcanaway | Agusan del Sur | Tarlac | Q31480806 |
| 145375 | Baliuag | Agusan del Sur | Bulacan | Q54554 |
| 145376 | Baloc | Agusan del Sur | Nueva Ecija | Q31481461 |
| 145378 | Balsic | Agusan del Sur | Bataan | Q31481739 |
| 145379 | Balucuc | Agusan del Sur | Pampanga | Q31482011 |
| 145380 | Balut | Agusan del Sur | Bataan | Q31482330 |
| 145381 | Balutu | Agusan del Sur | Tarlac | Q31482432 |
| 145384 | Banawang | Agusan del Sur | Bataan | Q31796280 |
| 145386 | Baquero Norte | Agusan del Sur | Tarlac | Q31485626 |
| 145388 | Batitang | Agusan del Sur | Nueva Ecija | Q31490411 |
| 145390 | Beddeng | Agusan del Sur | Zambales | Q31494497 |
| 145391 | Biay | Agusan del Sur | Zambales | Q31498310 |
| 145392 | Bibiclat | Agusan del Sur | Nueva Ecija | Q31498375 |
| 145395 | Bilad | Agusan del Sur | Tarlac | Q31501008 |
| 145399 | Bolitoc | Agusan del Sur | Zambales | Q31508621 |
| 145402 | Buenlag | Agusan del Sur | Tarlac | Q31516154 |
| 145403 | Buensuseso | Agusan del Sur | Pampanga | Q31516171 |
| 145405 | Bulaon | Agusan del Sur | Pampanga | Q31517466 |
| 145406 | Bularit | Agusan del Sur | Tarlac | Q31517481 |
| 145407 | Bulawin | Agusan del Sur | Zambales | Q31517537 |
| 145408 | Bulihan | Agusan del Sur | Bulacan | Q31517708 |
| 145409 | Buliran | Agusan del Sur | Nueva Ecija | Q31517743 |
| 145410 | Buliran Segundo | Agusan del Sur | Nueva Ecija | Q31517761 |
| 145411 | Bulualto | Agusan del Sur | Bulacan | Q31518244 |
| 145413 | Bunol | Agusan del Sur | Nueva Ecija | Q31518837 |
| 145420 | Cabayaoasan | Agusan del Sur | Tarlac | Q31523236 |
| 145421 | Cabcaben | Agusan del Sur | Bataan | Q31523321 |
| 145423 | Cabog | Agusan del Sur | Aurora | Q31523768 |
| 145424 | Cafe | Agusan del Sur | Tarlac | Q31525016 |
| 145425 | Calaba | Agusan del Sur | Nueva Ecija | Q31526235 |
| 145426 | Calancuasan Norte | Agusan del Sur | Nueva Ecija | Q31526918 |
| 145427 | Calangain | Agusan del Sur | Pampanga | Q31526971 |
| 145428 | Calantas | Agusan del Sur | Pampanga | Q31527149 |
| 145430 | Calibungan | Agusan del Sur | Tarlac | Q31528101 |
| 145431 | Calibutbut | Agusan del Sur | Pampanga | Q31528119 |
| 145432 | Calingcuan | Agusan del Sur | Tarlac | Q31528353 |
| 145433 | Calumpang | Agusan del Sur | Bulacan | Q31528994 |
| 145434 | Calumpit | Agusan del Sur | Bulacan | Q54564 |
| 145435 | Cama Juan | Agusan del Sur | Nueva Ecija | Q31529256 |
| 145436 | Camachile | Agusan del Sur | Bataan | Q31529290 |
| 145437 | Camias | Agusan del Sur | Bulacan | Q31530047 |
| 145440 | Candating | Agusan del Sur | Pampanga | Q31531654 |
| 145451 | City of Balanga | Agusan del Sur | Bataan | Q31544748 |
| 145452 | City of Gapan | Agusan del Sur | Nueva Ecija | Q31544974 |
| 145453 | City of Malolos | Agusan del Sur | Bulacan | Q31545127 |
| 145454 | City of Meycauayan | Agusan del Sur | Bulacan | Q31545176 |
| 145455 | City of San Fernando | Agusan del Sur | Pampanga | Q31545290 |
| 145457 | Comillas | Agusan del Sur | Tarlac | Q31550446 |
| 145462 | Conversion | Agusan del Sur | Nueva Ecija | Q31552072 |
| 145464 | Culubasa | Agusan del Sur | Pampanga | Q31557380 |
| 145465 | Cut-cut Primero | Agusan del Sur | Tarlac | Q31557801 |
| 145467 | Dampol | Agusan del Sur | Bulacan | Q31560847 |
| 145471 | Digdig | Agusan del Sur | Nueva Ecija | Q31566853 |
| 145475 | Dinalupihan | Agusan del Sur | Bataan | Q54457 |
| 145480 | Entablado | Agusan del Sur | Nueva Ecija | Q31578451 |
| 145481 | Estipona | Agusan del Sur | Tarlac | Q31579541 |
| 145482 | Estrella | Agusan del Sur | Nueva Ecija | Q31579577 |
| 145491 | Gueset | Agusan del Sur | Pangasinan | Q31811350 |
| 145492 | Guiguinto | Agusan del Sur | Bulacan | Q54589 |
| 145494 | Guisguis | Agusan del Sur | Zambales | Q31811381 |
| 145495 | Guyong | Agusan del Sur | Bulacan | Q31811398 |
| 145497 | Hermosa | Agusan del Sur | Bataan | Q54458 |
| 145501 | La Paz | Agusan del Sur | Tarlac | Q28733 |
| 145502 | Lambakin | Agusan del Sur | Bulacan | Q31811758 |
| 145504 | Lanat | Agusan del Sur | Tarlac | Q31811773 |
| 145505 | Laug | Agusan del Sur | Pampanga | Q31811813 |
| 145507 | Lawang Kupang | Agusan del Sur | Nueva Ecija | Q31811816 |
| 145508 | Lennec | Agusan del Sur | Nueva Ecija | Q31811827 |
| 145510 | Ligaya | Agusan del Sur | Nueva Ecija | Q31811875 |
| 145512 | Liozon | Agusan del Sur | Zambales | Q31811918 |
| 145513 | Lipay | Agusan del Sur | Zambales | Q31811919 |
| 145515 | Lomboy | Agusan del Sur | Tarlac | Q31811938 |
| 145516 | Lourdes | Agusan del Sur | Pampanga | Q31811960 |
| 145519 | Lucapon | Agusan del Sur | Zambales | Q31811969 |
| 145523 | Mabayo | Agusan del Sur | Bataan | Q31812037 |
| 145525 | Mabilog | Agusan del Sur | Tarlac | Q31812041 |
| 145528 | Macapsing | Agusan del Sur | Nueva Ecija | Q31812065 |
| 145530 | Macatbong | Agusan del Sur | Nueva Ecija | Q31812067 |
| 145532 | Magliman | Agusan del Sur | Pampanga | Q31812089 |
| 145533 | Magtangol | Agusan del Sur | Nueva Ecija | Q31812099 |
| 145534 | Maguinao | Agusan del Sur | Bulacan | Q31812101 |
| 145535 | Malabon | Agusan del Sur | Zambales | Q31812128 |
| 145536 | Malacampa | Agusan del Sur | Tarlac | Q31812132 |
| 145537 | Maligaya | Agusan del Sur | Nueva Ecija | Q31812171 |
| 145538 | Malino | Agusan del Sur | Pampanga | Q31812181 |
| 145539 | Malolos | Agusan del Sur | Bulacan | Q2180 |
| 145540 | Maloma | Agusan del Sur | Zambales | Q31812191 |
| 145541 | Maluid | Agusan del Sur | Tarlac | Q31812194 |
| 145542 | Malusac | Agusan del Sur | Pampanga | Q31812197 |
| 145543 | Mambog | Agusan del Sur | Zambales | Q31812210 |
| 145544 | Mamonit | Agusan del Sur | Tarlac | Q31812213 |
| 145545 | Manacsac | Agusan del Sur | Nueva Ecija | Q31812217 |
| 145547 | Mandili | Agusan del Sur | Pampanga | Q31812241 |
| 145548 | Mangga | Agusan del Sur | Nueva Ecija | Q31812248 |
| 145551 | Mapalacsiao | Agusan del Sur | Tarlac | Q31812279 |
| 145552 | Mapalad | Agusan del Sur | Nueva Ecija | Q31812281 |
| 145553 | Mapaniqui | Agusan del Sur | Pampanga | Q31812282 |
| 145554 | Maquiapo | Agusan del Sur | Pampanga | Q31812288 |
| 145555 | Marawa | Agusan del Sur | Nueva Ecija | Q31812295 |
| 145557 | Marilao | Agusan del Sur | Bulacan | Q54595 |
| 145558 | Mariveles | Agusan del Sur | Bataan | Q54460 |
| 145559 | Masalipit | Agusan del Sur | Bulacan | Q31812315 |
| 145562 | Matayumtayum | Agusan del Sur | Tarlac | Q31812341 |
| 145563 | Maturanoc | Agusan del Sur | Nueva Ecija | Q31812358 |
| 145566 | Meycauayan | Agusan del Sur | Bulacan | Q2187 |
| 145569 | Moriones | Agusan del Sur | Tarlac | Q31812480 |
| 145571 | Motrico | Agusan del Sur | Tarlac | Q31812488 |
| 145574 | Nagpandayan | Agusan del Sur | Nueva Ecija | Q31812529 |
| 145575 | Nambalan | Agusan del Sur | Tarlac | Q31812547 |
| 145578 | Nancamarinan | Agusan del Sur | Tarlac | Q31812557 |
| 145579 | Nieves | Agusan del Sur | Nueva Ecija | Q31812642 |
| 145580 | Niugan | Agusan del Sur | Bulacan | Q31812651 |
| 145581 | Norzagaray | Agusan del Sur | Bulacan | Q31812668 |
| 145582 | Obando | Agusan del Sur | Bulacan | Q54599 |
| 145584 | Orani | Agusan del Sur | Bataan | Q54462 |
| 145586 | Paco Roman | Agusan del Sur | Nueva Ecija | Q31812752 |
| 145587 | Padapada | Agusan del Sur | Tarlac | Q31812755 |
| 145594 | Panan | Agusan del Sur | Zambales | Q31461231 |
| 145596 | Pandacaqui | Agusan del Sur | Pampanga | Q31461413 |
| 145597 | Pandi | Agusan del Sur | Bulacan | Q54600 |
| 145601 | Pantubig | Agusan del Sur | Bulacan | Q31462862 |
| 145602 | Paombong | Agusan del Sur | Bulacan | Q54605 |
| 145605 | Parista | Agusan del Sur | Nueva Ecija | Q31463459 |
| 145606 | Pau | Agusan del Sur | Pampanga | Q31465013 |
| 145608 | Pias | Agusan del Sur | Nueva Ecija | Q31467495 |
| 145611 | Pinambaran | Agusan del Sur | Bulacan | Q31468999 |
| 145612 | Pio | Agusan del Sur | Pampanga | Q31470807 |
| 145613 | Piñahan | Agusan del Sur | Nueva Ecija | Q31471792 |
| 145617 | Porais | Agusan del Sur | Nueva Ecija | Q31475385 |
| 145618 | Prado Siongco | Agusan del Sur | Pampanga | Q31477207 |
| 145619 | Pulilan | Agusan del Sur | Bulacan | Q54761 |
| 145624 | Pulungmasle | Agusan del Sur | Pampanga | Q31479980 |
| 145625 | Puncan | Agusan del Sur | Nueva Ecija | Q31480226 |
| 145628 | Putlod | Agusan del Sur | Nueva Ecija | Q31481018 |
| 145630 | Rajal Norte | Agusan del Sur | Nueva Ecija | Q31483599 |
| 145634 | Sagana | Agusan del Sur | Nueva Ecija | Q31498115 |
| 145635 | Salapungan | Agusan del Sur | Pampanga | Q31499357 |
| 145636 | Salaza | Agusan del Sur | Zambales | Q31499481 |
| 145667 | San Isidro | Agusan del Sur | Nueva Ecija | Q55572 |
| 145674 | San Jose del Monte | Agusan del Sur | Bulacan | Q2193 |
| 145680 | San Luis | Agusan del Sur | Pampanga | Q55724 |
| 145695 | San Rafael | Agusan del Sur | Bulacan | Q54765 |
| 145699 | San Roque | Agusan del Sur | Bulacan | Q31508116 |
| 145707 | Santa Ana | Agusan del Sur | Pampanga | Q55727 |
| 145709 | Santa Cruz | Agusan del Sur | Zambales | Q31510657 |
| 145719 | Santa Maria | Agusan del Sur | Bulacan | Q54768 |
| 145724 | Santa Rita | Agusan del Sur | Pampanga | Q55730 |
| 145744 | Sapang | Agusan del Sur | Tarlac | Q31513336 |
| 145745 | Sapang Buho | Agusan del Sur | Nueva Ecija | Q31513352 |
| 145750 | Sibul | Agusan del Sur | Bulacan | Q31518590 |
| 145752 | Siclong | Agusan del Sur | Nueva Ecija | Q31518810 |
| 145754 | Sinilian First | Agusan del Sur | Tarlac | Q31520980 |
| 145755 | Soledad | Agusan del Sur | Nueva Ecija | Q31526812 |
| 145757 | Suklayin | Agusan del Sur | Aurora | Q31536835 |
| 145759 | Sulucan | Agusan del Sur | Bulacan | Q31537386 |
| 145762 | Tabuating | Agusan del Sur | Nueva Ecija | Q31541367 |
| 145763 | Tal I Mun Doc | Agusan del Sur | Pampanga | Q31543084 |
| 145764 | Talaga | Agusan del Sur | Tarlac | Q31543215 |
| 145767 | Taltal | Agusan del Sur | Zambales | Q31544528 |
| 145769 | Tariji | Agusan del Sur | Tarlac | Q31546744 |
| 145772 | Telabastagan | Agusan del Sur | Pampanga | Q31549292 |
| 145773 | Tikiw | Agusan del Sur | Nueva Ecija | Q31556107 |
| 145774 | Tinang | Agusan del Sur | Tarlac | Q31556832 |
| 145775 | Tondod | Agusan del Sur | Nueva Ecija | Q31558899 |
| 145776 | Uacon | Agusan del Sur | Zambales | Q31567197 |
| 145777 | Umiray | Agusan del Sur | Aurora | Q31567719 |
| 145779 | Vargas | Agusan del Sur | Tarlac | Q31571431 |
| 145782 | Villa Isla | Agusan del Sur | Nueva Ecija | Q31572920 |
| 145791 | Alac | Abra | Pangasinan | Q31462940 |
| 145795 | Allangigan Primero | Abra | Ilocos Sur | Q31464377 |
| 145796 | Aloleng | Abra | Pangasinan | Q31464858 |
| 145797 | Amagbagan | Abra | Pangasinan | Q31465243 |
| 145798 | Anambongan | Abra | Pangasinan | Q31465967 |
| 145800 | Angatel | Abra | Pangasinan | Q31466551 |
| 145801 | Anulid | Abra | Pangasinan | Q31467422 |
| 145804 | Baay | Abra | Ilocos Norte | Q31472039 |
| 145805 | Bacag | Abra | Pangasinan | Q31472798 |
| 145807 | Bacnar | Abra | Pangasinan | Q31473342 |
| 145809 | Bactad Proper | Abra | Pangasinan | Q31473934 |
| 145810 | Bacundao Weste | Abra | Pangasinan | Q31474163 |
| 145813 | Bail | Abra | La Union | Q31476406 |
| 145816 | Balingueo | Abra | Pangasinan | Q31480848 |
| 145817 | Balogo | Abra | Pangasinan | Q31481571 |
| 145819 | Baluyot | Abra | Pangasinan | Q31482453 |
| 145821 | Bangan-Oda | Abra | Pangasinan | Q31483383 |
| 145827 | Banog Sur | Abra | Pangasinan | Q31484515 |
| 145829 | Bantog | Abra | Pangasinan | Q31485128 |
| 145830 | Barangobong | Abra | Pangasinan | Q31485918 |
| 145831 | Baro | Abra | Pangasinan | Q31487159 |
| 145832 | Barong | Abra | Ilocos Norte | Q31487279 |
| 145833 | Basing | Abra | Pangasinan | Q31489110 |
| 145836 | Bataquil | Abra | Pangasinan | Q31489984 |
| 145840 | Bayaoas | Abra | Pangasinan | Q31492418 |
| 145841 | Bical Norte | Abra | Pangasinan | Q31498416 |
| 145842 | Bil-Loca | Abra | Ilocos Norte | Q31500945 |
| 145843 | Binabalian | Abra | Pangasinan | Q31501626 |
| 145845 | Binday | Abra | Pangasinan | Q31502321 |
| 145848 | Bogtong | Abra | Pangasinan | Q31507979 |
| 145849 | Bolaoit | Abra | Pangasinan | Q31508322 |
| 145851 | Bolingit | Abra | Pangasinan | Q31508587 |
| 145852 | Bolo | Abra | Pangasinan | Q31508767 |
| 145853 | Botao | Abra | Pangasinan | Q31510308 |
| 145854 | Boñgalon | Abra | Pangasinan | Q31511059 |
| 145855 | Bued | Abra | Pangasinan | Q31515791 |
| 145857 | Buenlag | Abra | Pangasinan | Q31516138 |
| 145859 | Bulog | Abra | Pangasinan | Q31518211 |
| 145864 | Butubut Norte | Abra | La Union | Q31521111 |
| 145865 | Caabiangan | Abra | Pangasinan | Q31522252 |
| 145867 | Cabalaoangan | Abra | Pangasinan | Q31522519 |
| 145868 | Cabalitian | Abra | Pangasinan | Q31522601 |
| 145869 | Cabittaogan | Abra | Ilocos Sur | Q31523679 |
| 145870 | Cabugao | Abra | Ilocos Sur | Q12832 |
| 145871 | Cabungan | Abra | Pangasinan | Q31524357 |
| 145874 | Callaguip | Abra | Ilocos Norte | Q31528537 |
| 145875 | Calomboyan | Abra | Pangasinan | Q31528655 |
| 145876 | Calongbuyan | Abra | Ilocos Sur | Q31528670 |
| 145877 | Calsib | Abra | Pangasinan | Q31528732 |
| 145878 | Camaley | Abra | Pangasinan | Q31529355 |
| 145879 | Canan Norte | Abra | Pangasinan | Q31531186 |
| 145880 | Canaoalan | Abra | Pangasinan | Q31531218 |
| 145882 | Cantoria | Abra | La Union | Q31532673 |
| 145884 | Capandanan | Abra | Pangasinan | Q31532983 |
| 145885 | Capulaan | Abra | Pangasinan | Q31533635 |
| 145886 | Caramutan | Abra | Pangasinan | Q31534094 |
| 145889 | Caronoan West | Abra | La Union | Q31535268 |
| 145890 | Carot | Abra | Pangasinan | Q31535284 |
| 145891 | Carriedo | Abra | Pangasinan | Q31535640 |
| 145892 | Carusucan | Abra | Pangasinan | Q31536046 |
| 145894 | Cato | Abra | Pangasinan | Q31537858 |
| 145895 | Catuday | Abra | Pangasinan | Q31537975 |
| 145896 | Cayanga | Abra | Pangasinan | Q31538853 |
| 145897 | Cayungnan | Abra | Pangasinan | Q31539118 |
| 145899 | City of Batac | Abra | Ilocos Norte | Q31544763 |
| 145900 | City of Candon | Abra | Ilocos Sur | Q31544898 |
| 145901 | City of Urdaneta | Abra | Pangasinan | Q31545553 |
| 145902 | City of Vigan | Abra | Ilocos Sur | Q31545603 |
| 145903 | Comillas Norte | Abra | Ilocos Sur | Q31550460 |
| 145904 | Corrooy | Abra | La Union | Q31553608 |
| 145908 | Damortis | Abra | La Union | Q31560768 |
| 145909 | Darapidap | Abra | Ilocos Sur | Q31562119 |
| 145911 | Davila | Abra | Ilocos Norte | Q31563030 |
| 145912 | Diaz | Abra | Pangasinan | Q31566098 |
| 145913 | Dilan | Abra | Pangasinan | Q31567081 |
| 145915 | Domalanoan | Abra | Pangasinan | Q31569750 |
| 145917 | Don Pedro | Abra | Pangasinan | Q31570023 |
| 145918 | Dorongan Punta | Abra | Pangasinan | Q31570581 |
| 145919 | Doyong | Abra | Pangasinan | Q31571281 |
| 145920 | Dulig | Abra | Pangasinan | Q31572336 |
| 145922 | Dumpay | Abra | Pangasinan | Q31572821 |
| 145923 | Eguia | Abra | Pangasinan | Q31576082 |
| 145924 | Esmeralda | Abra | Pangasinan | Q31579019 |
| 145925 | Fuerte | Abra | Ilocos Sur | Q31586993 |
| 145927 | Gayaman | Abra | Pangasinan | Q31589638 |
| 145930 | Guiling | Abra | Pangasinan | Q31811360 |
| 145931 | Guiset East | Abra | Pangasinan | Q31811379 |
| 145933 | Halog West | Abra | La Union | Q31811413 |
| 145935 | Inabaan Sur | Abra | La Union | Q31811493 |
| 145937 | Isla | Abra | Pangasinan | Q31811521 |
| 145938 | Labayug | Abra | Pangasinan | Q31811719 |
| 145939 | Labney | Abra | Pangasinan | Q31811720 |
| 145941 | Lagasit | Abra | Pangasinan | Q31811733 |
| 145942 | Laguit Centro | Abra | Pangasinan | Q31811738 |
| 145945 | Leones East | Abra | La Union | Q31811832 |
| 145946 | Lepa | Abra | Pangasinan | Q31811833 |
| 145947 | Libas | Abra | Pangasinan | Q31811845 |
| 145950 | Linmansangan | Abra | Pangasinan | Q31811914 |
| 145951 | Lloren | Abra | La Union | Q31811928 |
| 145952 | Lobong | Abra | Pangasinan | Q31811931 |
| 145953 | Longos | Abra | Pangasinan | Q31811939 |
| 145954 | Loqueb Este | Abra | Pangasinan | Q31811952 |
| 145955 | Lucap | Abra | Pangasinan | Q31811968 |
| 145956 | Lucero | Abra | Pangasinan | Q31811974 |
| 145957 | Luna | Abra | La Union | Q40419 |
| 145958 | Lunec | Abra | Pangasinan | Q31812006 |
| 145959 | Lungog | Abra | Ilocos Sur | Q31812009 |
| 145961 | Mabilao | Abra | Pangasinan | Q31812039 |
| 145962 | Mabilbila Sur | Abra | Ilocos Sur | Q31812040 |
| 145964 | Mabusag | Abra | Ilocos Norte | Q31812054 |
| 145965 | Macabuboni | Abra | Pangasinan | Q31812057 |
| 145966 | Macalong | Abra | Pangasinan | Q31812063 |
| 145967 | Macalva Norte | Abra | La Union | Q31812064 |
| 145968 | Macayug | Abra | Pangasinan | Q31812068 |
| 145971 | Magtaking | Abra | Pangasinan | Q31812097 |
| 145972 | Malabago | Abra | Pangasinan | Q31812124 |
| 145973 | Malanay | Abra | Pangasinan | Q31812142 |
| 145975 | Malawa | Abra | Pangasinan | Q31812156 |
| 145981 | Mapolopolo | Abra | Pangasinan | Q31812284 |
| 145983 | Maticmatic | Abra | Pangasinan | Q31812347 |
| 145984 | Minien East | Abra | Pangasinan | Q31812440 |
| 145985 | Nagbacalan | Abra | Ilocos Norte | Q31812525 |
| 145987 | Nagsaing | Abra | Pangasinan | Q31812532 |
| 145988 | Naguelguel | Abra | Pangasinan | Q31812534 |
| 145989 | Naguilayan | Abra | Pangasinan | Q31812535 |
| 145990 | Naguilian | Abra | La Union | Q40450 |
| 145991 | Nalsian Norte | Abra | Pangasinan | Q31812540 |
| 145992 | Nama | Abra | Pangasinan | Q31812545 |
| 145993 | Namboongan | Abra | La Union | Q31812550 |
| 145994 | Nancalobasaan | Abra | Pangasinan | Q31812555 |
| 145997 | Navatat | Abra | Pangasinan | Q31812599 |
| 145998 | Nibaliw Central | Abra | Pangasinan | Q31812640 |
| 145999 | Nilombot | Abra | Pangasinan | Q31812645 |
| 146000 | Ninoy | Abra | Pangasinan | Q31812648 |
| 146002 | Oaqui | Abra | La Union | Q31812687 |
| 146003 | Olea | Abra | Pangasinan | Q31812712 |
| 146004 | Padong | Abra | Ilocos Norte | Q31812759 |
| 146011 | Pangapisan | Abra | Pangasinan | Q31461842 |
| 146012 | Pangascasan | Abra | Pangasinan | Q31461865 |
| 146013 | Pangpang | Abra | Pangasinan | Q31462023 |
| 146015 | Paringao | Abra | La Union | Q31463426 |
| 146016 | Parioc Segundo | Abra | Ilocos Sur | Q31463438 |
| 146017 | Pasibi West | Abra | Pangasinan | Q31463844 |
| 146019 | Patayac | Abra | Pangasinan | Q31464234 |
| 146020 | Patpata Segundo | Abra | Ilocos Sur | Q31464451 |
| 146021 | Payocpoc Sur | Abra | La Union | Q31465580 |
| 146023 | Pindangan Centro | Abra | Pangasinan | Q31469209 |
| 146025 | Pogonsili | Abra | Pangasinan | Q31473175 |
| 146030 | Pudoc | Abra | Ilocos Sur | Q31479091 |
| 146031 | Pudoc North | Abra | Ilocos Sur | Q31479112 |
| 146032 | Puelay | Abra | Pangasinan | Q31479152 |
| 146034 | Puro Pinget | Abra | Ilocos Sur | Q31480697 |
| 146035 | Quiling | Abra | Ilocos Norte | Q31482007 |
| 146036 | Quinarayan | Abra | Ilocos Sur | Q31482237 |
| 146037 | Quintong | Abra | Pangasinan | Q31482389 |
| 146042 | Rimus | Abra | La Union | Q31488806 |
| 146043 | Rissing | Abra | La Union | Q31489272 |
| 146046 | Sablig | Abra | Pangasinan | Q31497600 |
| 146047 | Sagud-Bahley | Abra | Pangasinan | Q31498491 |
| 146048 | Sagunto | Abra | Pangasinan | Q31498593 |
| 146051 | Samon | Abra | Pangasinan | Q31501045 |
| 146055 | San Eugenio | Abra | La Union | Q31503111 |
| 146063 | San Juan | Abra | La Union | Q40517 |
| 146074 | Sanlibo | Abra | Pangasinan | Q31509994 |
| 146085 | Santo Tomas | Abra | La Union | Q40521 |
| 146093 | Sonquil | Abra | Pangasinan | Q31527044 |
| 146095 | Subusub | Abra | La Union | Q31536043 |
| 146098 | Sumabnit | Abra | Pangasinan | Q31537416 |
| 146099 | Suso | Abra | Ilocos Sur | Q31538925 |
| 146101 | Tablac | Abra | Ilocos Sur | Q31541018 |
| 146102 | Tabug | Abra | Ilocos Norte | Q31541435 |
| 146105 | Talospatang | Abra | Pangasinan | Q31544443 |
| 146106 | Taloy | Abra | Pangasinan | Q31544495 |
| 146107 | Tamayo | Abra | Pangasinan | Q31544686 |
| 146108 | Tamorong | Abra | Ilocos Sur | Q31545153 |
| 146110 | Tanolong | Abra | Pangasinan | Q31545973 |
| 146112 | Tebag East | Abra | Pangasinan | Q31549005 |
| 146113 | Telbang | Abra | Pangasinan | Q31549342 |
| 146114 | Tiep | Abra | Pangasinan | Q31555457 |
| 146115 | Toboy | Abra | Pangasinan | Q31557872 |
| 146116 | Tobuan | Abra | Pangasinan | Q31557889 |
| 146117 | Tococ East | Abra | Pangasinan | Q31557905 |
| 146119 | Tombod | Abra | Pangasinan | Q31558640 |
| 146120 | Tondol | Abra | Pangasinan | Q31558917 |
| 146121 | Toritori | Abra | Pangasinan | Q31559209 |
| 146123 | Umanday Centro | Abra | Pangasinan | Q31567634 |
| 146125 | Unzad | Abra | Pangasinan | Q31568647 |
| 146128 | Uyong | Abra | Pangasinan | Q31570082 |

</details>

### Also found (not changed here)
- **Duplicates.** The later batch re-added about 974 places that the 2019 import already holds under their region;
  after this PR most of them sit in the right province next to their region-filed twin. They wait for the
  duplicate-merge policy in #1643.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/PH.json` — `state_id` and `state_code` on 1,785 records

## Philippine records filed under the wrong province (second pass)

**477 more Philippine records** move to the province they are in (344 of them to another region too). #1663 moved
records whose own Wikidata item could be verified; these are ones it could not use, mostly because their
`wikiDataId` is a same-named place elsewhere (copy-forward, #1641). They show the same pattern: 41 Cebu places filed
under Bataan, Batangas and Quezon ones under Occidental Mindoro, Nueva Ecija ones under Agusan del Sur.

### How they were verified
The #1663 review showed that Wikidata and GeoNames can agree on an outdated province where one was split or created
(Davao Occidental, Maguindanao, Sarangani, Guimaras). So this pass requires province polygons:
1. **geoBoundaries province polygons** (PHL ADM2, NAMRIA/PSA 2020), mapped to CSC: Compostela Valley is Davao de
   Oro, Samar is Western Samar, City of Isabela is Basilan, and Maguindanao is split into del Norte and del Sur by
   municipality (RA 11550). Coastlines don't count as borders; a point just off the simplified coast takes the
   province within 3 km. A record within 2 km of another province is held.
2. **The nearest Wikidata municipalities and cities** (1,488 items, each with its current province): the nearest,
   within 10 km, and at least one other of the three nearest must lie in the same province.

| Result | Records |
|---|---:|
| Polygons and Wikidata municipalities agree on another province: **moved** | **477** |
| … but the place is in the BARMM Special Geographic Area (Kabasalan, found by the second review): held | 1 |
| The record is itself a municipality or city whose point is wrong (see review): not moved | 42 |
| Wikidata municipalities disagree with the polygons: held | 233 |
| More than 3 km off the polygons (bad point, or a small island): held | 170 |
| Within 2 km of another province: held | 118 |

### After the independent review
The review reverse-geocoded all 520 first-draft points with OpenStreetMap: every point lies in the province given.
But 40 records are named municipalities or cities whose **coordinates** are wrong, 6–58 km from the place (Davao
City, Biñan, Lake Sebu, Lucban, Oroquieta, Midsayap…); their own `wikiDataId` is that municipality, in the province
they were filed under. Following the point moved them to the wrong province. Those 40, plus 2 unsure (Santo Domingo,
whose point is in Iriga; Ligawasan, in the BARMM Special Geographic Area), are left out: their points need fixing
first, which is a separate change. A guard now skips any record whose own Wikidata item is a same-named municipality
or city within 60 km; beyond that distance the item is a namesake (e.g. San Quintin, Abra for a San Quintin in
Pangasinan), and OpenStreetMap confirmed those moves.

### Fix
Only `state_id` and `state_code` change; all keep `Asia/Manila`.

| Move (pairs with 11+ records, of 68) | Records |
|---|---:|
| Bataan → Cebu | 41 |
| Occidental Mindoro → Quezon | 21 |
| Occidental Mindoro → Batangas | 21 |
| Agusan del Sur → Nueva Ecija | 20 |
| Zamboanga Sibugay → Zamboanga del Sur | 19 |
| Antique → Aklan | 18 |
| Bukidnon → Sarangani | 17 |
| Antique → Negros Occidental | 15 |
| Abra → Pangasinan | 15 |
| Bataan → Bohol | 14 |
| Agusan del Sur → Tarlac | 14 |
| Batanes → Leyte | 13 |
| Antique → Iloilo | 12 |
| Antique → Guimaras | 11 |
| Albay → Masbate | 11 |
| Agusan del Norte → Isabela | 11 |
| other pairs | 204 |

<details>
<summary>All 477 records (id, name, was, now, nearest Wikidata municipality)</summary>

| id | Name | Was | Now | Nearest municipality |
|---|---|---|---|---|
| 81134 | Abucay | Albay | Sorsogon | Pilar (7.0 km) |
| 81141 | Abuyon | Occidental Mindoro | Quezon | San Narciso (8.0 km) |
| 81146 | Adlaon | Bataan | Cebu | Cordova (7.6 km) |
| 81156 | Agcogon | Oriental Mindoro | Romblon | San Jose (2.9 km) |
| 81166 | Agsungot | Bataan | Cebu | Consolacion (6.1 km) |
| 81167 | Aguada | Albay | Sorsogon | Magallanes (1.3 km) |
| 81172 | Agusan | Benguet | Misamis Oriental | Tagoloan (5.0 km) |
| 81182 | Alae | Benguet | Bukidnon | Manolo Fortich (8.6 km) |
| 81199 | Alegria | Antique | Negros Occidental | Murcia (7.3 km) |
| 81244 | Ambulong | Occidental Mindoro | Batangas | Talisay (5.0 km) |
| 81245 | Ambulong | Antique | Aklan | Batan (0.7 km) |
| 81293 | Apas | Bataan | Cebu | Consolacion (8.4 km) |
| 81319 | Asia | Antique | Negros Occidental | Hinoba-an (7.9 km) |
| 81332 | Aurora | Occidental Mindoro | Quezon | San Francisco (0.4 km) |
| 81337 | Avila | Antique | Guimaras | Buenavista (6.7 km) |
| 81363 | Bacolod | Albay | Masbate | Milagros (1.0 km) |
| 81383 | Badlan | Antique | Iloilo | Calinog (2.9 km) |
| 81386 | Bagacay | Bataan | Bohol | Calape (4.2 km) |
| 81390 | Bagalangit | Occidental Mindoro | Batangas | 蒂萊 (7.0 km) |
| 81400 | Bagong Sikat | Oriental Mindoro | Occidental Mindoro | San Jose (1.8 km) |
| 81412 | Bagumbayan | Antique | Negros Occidental | Valladolid (2.3 km) |
| 81419 | Baikingon | Benguet | Misamis Oriental | Opol (5.1 km) |
| 81433 | Balagon | Zamboanga Sibugay | Zamboanga del Sur | Midsalip (8.8 km) |
| 81435 | Balagtas | Batanes | Leyte | Matag-ob (5.2 km) |
| 81436 | Balagtasin | Occidental Mindoro | Batangas | San Jose (3.2 km) |
| 81437 | Balagui | Batanes | Biliran | Cabucgayan (4.7 km) |
| 81459 | Balele | Occidental Mindoro | Batangas | Balete (5.5 km) |
| 81482 | Balite Segundo | Occidental Mindoro | Cavite | Amadeo (5.2 km) |
| 81486 | Baliuag Nuevo | Albay | Camarines Sur | ミナラバク (5.5 km) |
| 81488 | Baliwagan | Benguet | Misamis Oriental | Balingasag (3.6 km) |
| 81496 | Balogo | Batanes | Leyte | Albuera (4.1 km) |
| 81545 | Banos | Oriental Mindoro | Occidental Mindoro | Calintaan (8.6 km) |
| 81567 | Baras | Batanes | Leyte | Palo (3.9 km) |
| 81609 | Basud | Batanes | Leyte | San Isidro (5.8 km) |
| 81617 | Batarasa | Oriental Mindoro | Palawan | Bataraza (1.4 km) |
| 81620 | Batasan | Oriental Mindoro | Occidental Mindoro | سبلیں ، وکڈینٹل مندورو (8.5 km) |
| 81644 | Baugo | Bataan | Cebu | Cordova (8.0 km) |
| 81659 | Bayas | Antique | Iloilo | Estancia (3.9 km) |
| 81664 | Baybayin | Occidental Mindoro | Batangas | Rosario (7.4 km) |
| 81681 | Biabas | Bataan | Bohol | کاندییائی (3.8 km) |
| 81691 | Biga | Occidental Mindoro | Cavite | Silang (3.0 km) |
| 81693 | Biga | Benguet | Misamis Oriental | Lugait (1.9 km) |
| 81702 | Bilaran | Occidental Mindoro | Batangas | Tuy (3.2 km) |
| 81715 | Binay | Occidental Mindoro | Quezon | San Narciso (8.1 km) |
| 81732 | Binuatan | Zamboanga Sibugay | Zamboanga del Sur | Dinas (0.8 km) |
| 81733 | Binubusan | Occidental Mindoro | Batangas | Lian (7.3 km) |
| 81745 | Biton | Bataan | Cebu | Daanbantayan (1.9 km) |
| 81763 | Bohol | Bataan | Bohol | Carmen (4.1 km) |
| 81772 | Bolisong | Bataan | Negros Oriental | Manjuyod (0.9 km) |
| 81795 | Boot | Occidental Mindoro | Batangas | Balete (4.0 km) |
| 81799 | Boroon | Benguet | Lanao del Norte | Linamon (1.8 km) |
| 81807 | Brgy. Bachaw Norte Kalibo | Antique | Aklan | Kalibo (1.5 km) |
| 81808 | Brgy. Bulwang Numancia | Antique | Aklan | Kalibo (1.9 km) |
| 81809 | Brgy. Mabilo New Washington | Antique | Aklan | New Washington (4.4 km) |
| 81810 | Brgy. Nalook kalibo | Antique | Aklan | Kalibo (2.4 km) |
| 81811 | Brgy. New Buswang Kalibo | Antique | Aklan | Kalibo (1.7 km) |
| 81812 | Brgy. Tinigao Kalibo | Antique | Aklan | Kalibo (0.9 km) |
| 81815 | Buagsong | Bataan | Cebu | Cordova (1.1 km) |
| 81833 | Buenavista | Albay | Masbate | Uson (5.5 km) |
| 81848 | Bugo | Benguet | Misamis Oriental | Tagoloan (3.0 km) |
| 81862 | Bulacnin | Occidental Mindoro | Batangas | ماتاسناکاحوئی (4.5 km) |
| 81894 | Bunga | Batanes | Biliran | Cabucgayan (2.3 km) |
| 81950 | Cabanglasan | Benguet | Bukidnon | Cabanglasan (5.8 km) |
| 81952 | Cabano | Antique | Guimaras | San Lorenzo (0.2 km) |
| 81955 | Cabatang | Occidental Mindoro | Quezon | Tiaong (5.7 km) |
| 81978 | Cabugao | Antique | Iloilo | Santa Barbara (1.8 km) |
| 81993 | Cagayan | Oriental Mindoro | Tawi-Tawi | Mapun (0.1 km) |
| 82013 | Calachuchi | Albay | Masbate | Milagros (2.4 km) |
| 82027 | Calantas | Occidental Mindoro | Batangas | Balayan (6.2 km) |
| 82030 | Calape | Antique | Negros Occidental | Isabela (8.2 km) |
| 82043 | Calaya | Antique | Guimaras | Sibunag (1.6 km) |
| 82048 | Calero | Bataan | Cebu | Liloan (5.9 km) |
| 82052 | Calilayan | Occidental Mindoro | Quezon | اگدانگان (3.4 km) |
| 82056 | Calintaan | Oriental Mindoro | Occidental Mindoro | Calintaan (1.4 km) |
| 82082 | Camambugan | Bataan | Bohol | Ubay (3.8 km) |
| 82125 | Cantao-an | Bataan | Cebu | Minglanilla (5.1 km) |
| 82155 | Caraycaray | Batanes | Biliran | Naval (4.9 km) |
| 82174 | Carmen Grande | Antique | Negros Occidental | Pontevedra (3.8 km) |
| 82199 | Casuguran | Occidental Mindoro | Quezon | Jomalig (5.2 km) |
| 82211 | Caticlan | Antique | Aklan | マライ (6.6 km) |
| 82271 | Concepcion | Oriental Mindoro | Romblon | Santa Maria (5.0 km) |
| 82276 | Concepcion Ibaba | Occidental Mindoro | Quezon | Candelaria (4.2 km) |
| 82277 | Concordia | Antique | Guimaras | Nueva Valencia (2.3 km) |
| 82283 | Constancia | Antique | Guimaras | Jordan (5.9 km) |
| 82300 | Cortez | Antique | Aklan | Balete (3.4 km) |
| 82365 | Damulog | Benguet | Bukidnon | Damulog (0.3 km) |
| 82371 | Danlugan | Zamboanga Sibugay | Zamboanga del Sur | Dumalinao (8.3 km) |
| 82399 | Dayap | Occidental Mindoro | Laguna | Calauan (3.8 km) |
| 82435 | Dinahican | Occidental Mindoro | Quezon | Infanta (7.8 km) |
| 82458 | Don Carlos | Benguet | Bukidnon | Don Carlos (1.1 km) |
| 82488 | Dumanjog | Bataan | Cebu | Dumanjug (5.2 km) |
| 82498 | East Migpulao | Zamboanga Sibugay | Zamboanga del Sur | Dinas (3.0 km) |
| 82499 | East Valencia | Antique | Guimaras | Buenavista (7.5 km) |
| 82511 | Eraan | Oriental Mindoro | Palawan | Rizal (7.2 km) |
| 82513 | Ermita | Antique | Iloilo | Barotac Nuevo (1.8 km) |
| 82518 | Esperanza | Bataan | Cebu | San Francisco (6.7 km) |
| 82525 | Estaca | Bataan | Bohol | Garcia Hernandez (9.1 km) |
| 82549 | Gabi | Bataan | Cebu | Cordova (1.8 km) |
| 82587 | Giawang | Bataan | Bohol | کاندییائی (3.2 km) |
| 82590 | Gibong | Antique | Aklan | Nabas (7.1 km) |
| 82610 | Guadalupe | Bataan | Cebu | Barili (8.1 km) |
| 82615 | Gubaan | Zamboanga Sibugay | Zamboanga del Sur | Aurora (3.5 km) |
| 82618 | Guibodangan | Bataan | Cebu | Barili (4.3 km) |
| 82630 | Guinayangan Fourth District of Quezon | Occidental Mindoro | Quezon | Guinayangan (0.2 km) |
| 82632 | Guindarohan | Bataan | Cebu | Minglanilla (3.8 km) |
| 82634 | Guiniculalay | Zamboanga Sibugay | Zamboanga del Sur | Dinas (7.4 km) |
| 82635 | Guinisiliban | Benguet | Camiguin | Guinsiliban (0.4 km) |
| 82636 | Guinlo | Oriental Mindoro | Palawan | Taytay (8.7 km) |
| 82651 | Guiwanon | Bataan | Cebu | Bantayan (2.8 km) |
| 82667 | Hagnaya | Bataan | Cebu | Medellin (4.5 km) |
| 82676 | Hamoraon | Albay | Masbate | Milagros (4.7 km) |
| 82685 | Hilantagaan | Bataan | Cebu | Santa Fe (5.1 km) |
| 82691 | Himensulan | Bataan | Cebu | San Francisco (9.5 km) |
| 82697 | Hinlayagan Ilaud | Bataan | Bohol | San Miguel (3.9 km) |
| 82704 | Hondagua | Occidental Mindoro | Quezon | カラウアグ (5.1 km) |
| 82712 | Ichon | Batanes | Southern Leyte | Macrohon (4.8 km) |
| 82726 | Ilaya | Zamboanga Sibugay | Zamboanga del Norte | Piñan (7.4 km) |
| 82736 | Imelda | Albay | Camarines Norte | San Lorenzo Ruiz (1.7 km) |
| 82744 | Inayagan | Bataan | Cebu | Minglanilla (3.2 km) |
| 82757 | Ipil | Oriental Mindoro | Marinduque | Santa Cruz (6.3 km) |
| 82768 | Isabang | Occidental Mindoro | Quezon | 薩里阿亞 (4.2 km) |
| 82779 | Jaclupan | Bataan | Cebu | Minglanilla (6.6 km) |
| 82789 | Jampang | Bataan | Cebu | Argao (2.7 km) |
| 82791 | Jandayan Norte | Bataan | Bohol | Getafe (4.0 km) |
| 82795 | Japitan | Bataan | Cebu | Barili (3.5 km) |
| 82820 | Kabac | Bataan | Cebu | Madridejos (5.2 km) |
| 82832 | Kabungahan | Bataan | Cebu | Compostela (5.9 km) |
| 82835 | Kagawasan | Zamboanga Sibugay | Zamboanga del Sur | Dumalinao (6.3 km) |
| 82849 | Kalian | Zamboanga Sibugay | Zamboanga del Sur | Lapuyan (6.4 km) |
| 82850 | Kalibo (poblacion) | Antique | Aklan | Kalibo (0.6 km) |
| 82860 | Kananya | Batanes | Leyte | Kananga (0.1 km) |
| 82863 | Kanluran | Occidental Mindoro | Cavite | ロサリオ (0.5 km) |
| 82865 | Kaongkod | Bataan | Cebu | Madridejos (3.0 km) |
| 82883 | Kauit | Bataan | Cebu | Medellin (6.6 km) |
| 82907 | Kinalansan | Albay | Camarines Sur | San Jose (3.8 km) |
| 82926 | Kotkot | Bataan | Cebu | Liloan (3.8 km) |
| 82927 | Kuanos | Bataan | Cebu | Minglanilla (4.6 km) |
| 82977 | Lagindingan | Benguet | Misamis Oriental | Laguindingan (1.3 km) |
| 83007 | Lanao | Bataan | Cebu | Daanbantayan (2.7 km) |
| 83013 | Langcangan | Benguet | Misamis Occidental | Lopez Jaena (7.9 km) |
| 83031 | Lapaz | Bataan | Cebu | San Remigio (3.5 km) |
| 83062 | Legrada | Zamboanga Sibugay | Zamboanga del Sur | Dinas (4.1 km) |
| 83085 | Libertad | Oriental Mindoro | Romblon | Odiongan (6.1 km) |
| 83088 | Libertad | Antique | Iloilo | Banate (2.2 km) |
| 83136 | Linay | Zamboanga Sibugay | Zamboanga del Norte | Manukan (4.6 km) |
| 83161 | Locmayan | Antique | Guimaras | Nueva Valencia (6.4 km) |
| 83172 | Looc | Benguet | Misamis Oriental | Salay (2.8 km) |
| 83217 | Lumbang | Occidental Mindoro | Laguna | Lumban (0.1 km) |
| 83224 | Lumbog | Zamboanga Sibugay | Zamboanga del Sur | Margosatubig (4.5 km) |
| 83234 | Luna | Albay | Masbate | San Jacinto (2.1 km) |
| 83244 | Lupi Viejo | Albay | Camarines Sur | Lupi (0.1 km) |
| 83276 | Mabini | Antique | Negros Occidental | Toboso (9.5 km) |
| 83284 | Mabitac | Occidental Mindoro | Laguna | Mabitac (1.6 km) |
| 83340 | Magsalangi | Albay | Masbate | Milagros (7.5 km) |
| 83372 | Mainit Norte | Occidental Mindoro | Quezon | Perez (5.9 km) |
| 83387 | Malabonot | Antique | Aklan | マライ (7.7 km) |
| 83426 | Malicboy | Occidental Mindoro | Quezon | Padre Burgos (7.0 km) |
| 83430 | Malilinao | Batanes | Leyte | Matag-ob (5.4 km) |
| 83432 | Malim | Zamboanga Sibugay | Zamboanga del Sur | Tabina (2.9 km) |
| 83438 | Malinao Ilaya | Occidental Mindoro | Quezon | Padre Burgos (8.6 km) |
| 83481 | Mamungan | Benguet | Lanao del Norte | Balo-i (0.2 km) |
| 83504 | Mandaue City | Bataan | Cebu | Cordova (8.5 km) |
| 83511 | Mangarine | Oriental Mindoro | Occidental Mindoro | San Jose (3.3 km) |
| 83514 | Mangero | Occidental Mindoro | Quezon | San Andres (5.8 km) |
| 83530 | Manoc-Manoc | Antique | Aklan | マライ (5.9 km) |
| 83535 | Mansilingan | Antique | Negros Occidental | Murcia (6.9 km) |
| 83537 | Mantampay | Benguet | Lanao del Norte | Balo-i (5.6 km) |
| 83568 | Marawis | Antique | Negros Occidental | Hinigaran (4.7 km) |
| 83575 | Maria Cristina | Benguet | Lanao del Norte | Linamon (5.2 km) |
| 83578 | Maribojoc | Bataan | Bohol | Maribojoc (1.1 km) |
| 83584 | Marintoc | Albay | Masbate | Mobo (9.1 km) |
| 83599 | Masaya | Occidental Mindoro | Laguna | Bay (3.5 km) |
| 83610 | Mat-i | Benguet | Misamis Oriental | Naawan (6.1 km) |
| 83639 | Maulawin | Occidental Mindoro | Laguna | 百胜滩 (1.8 km) |
| 83712 | Morobuan | Antique | Guimaras | Jordan (4.9 km) |
| 83727 | Muricay | Zamboanga Sibugay | Zamboanga del Sur | Labangan (6.1 km) |
| 83797 | Nañgka | Benguet | Lanao del Norte | Linamon (3.2 km) |
| 83800 | New Agutaya | Oriental Mindoro | Palawan | San Vicente (6.9 km) |
| 83856 | Oracon | Antique | Guimaras | Sibunag (6.0 km) |
| 83866 | Osmeña | Oriental Mindoro | Palawan | Araceli (7.9 km) |
| 83875 | Pacol | Antique | Negros Occidental | Valladolid (2.6 km) |
| 83945 | Panacan | Oriental Mindoro | Palawan | Narra (4.2 km) |
| 83954 | Panayacan | Antique | Aklan | Tangalan (4.4 km) |
| 83972 | Pangao | Occidental Mindoro | Batangas | ماتاسناکاحوئی (4.9 km) |
| 83975 | Pangdan | Bataan | Cebu | Minglanilla (6.6 km) |
| 83988 | Panique | Oriental Mindoro | Romblon | San Andres (4.3 km) |
| 84000 | Pantao-Ragat | Benguet | Lanao del Norte | Poona Piagapo (6.0 km) |
| 84011 | Parabcan | Albay | Camarines Sur | Presentacion (0.1 km) |
| 84031 | Pasil | Antique | Iloilo | Zarraga (2.6 km) |
| 84059 | Pawa | Antique | Capiz | Panay (2.8 km) |
| 84065 | Payabon | Bataan | Negros Oriental | Bindoy (1.2 km) |
| 84067 | Payao | Antique | Negros Occidental | Binalbagan (6.7 km) |
| 84110 | Pines | Benguet | Misamis Occidental | Aloran (4.5 km) |
| 84125 | Piña | Antique | Guimaras | Buenavista (6.5 km) |
| 84132 | Plaridel | Batanes | Leyte | Inopacan (7.6 km) |
| 84148 | Polo | Antique | Aklan | Madalag (6.4 km) |
| 84150 | Polo | Bataan | Negros Oriental | Amlan (5.1 km) |
| 84167 | Port Barton | Oriental Mindoro | Palawan | San Vicente (5.9 km) |
| 84168 | Potot | Albay | Masbate | Milagros (8.5 km) |
| 84179 | Prosperidad | Antique | Negros Occidental | Don Salvador Benedicto (8.8 km) |
| 84264 | Pulo | Occidental Mindoro | Quezon | Infanta (3.6 km) |
| 84286 | Puro | Albay | Masbate | Aroroy (3.6 km) |
| 84308 | Quinapundan | Batanes | Eastern Samar | Quinapondan (0.1 km) |
| 84328 | Rancheria Payau | Zamboanga Sibugay | Zamboanga del Sur | Lakewood (1.0 km) |
| 84341 | Rizal | Albay | Sorsogon | Castilla (4.8 km) |
| 84349 | Robonkon | Zamboanga Sibugay | Zamboanga del Sur | Dumalinao (9.1 km) |
| 84369 | Sabang | Occidental Mindoro | Cavite | Naic (4.2 km) |
| 84379 | Sagacad | Zamboanga Sibugay | Zamboanga del Sur | Guipos (5.3 km) |
| 84383 | Sagang | Antique | Negros Occidental | La Castellana (1.4 km) |
| 84414 | Salogon | Albay | Camarines Sur | Tigaon (4.0 km) |
| 84418 | Salvacion | Oriental Mindoro | Palawan | Busuanga (0.5 km) |
| 84437 | San Agustin | Oriental Mindoro | Occidental Mindoro | Rizal (5.8 km) |
| 84451 | San Antonio | Antique | Iloilo | San Miguel (2.6 km) |
| 84459 | San Carlos | Occidental Mindoro | Batangas | Rosario (3.9 km) |
| 84465 | San Diego | Occidental Mindoro | Batangas | Lian (2.8 km) |
| 84501 | San Isidro | Occidental Mindoro | Quezon | General Luna (9.9 km) |
| 84502 | San Isidro | Bataan | Bohol | Calape (3.7 km) |
| 84511 | San Joaquin | Antique | Iloilo | San Joaquin (6.3 km) |
| 84527 | San Juan | Antique | Negros Occidental | Pontevedra (3.0 km) |
| 84564 | San Miguel | Occidental Mindoro | Batangas | Padre Garcia (2.2 km) |
| 84567 | San Miguel | Oriental Mindoro | Palawan | Linapacan (0.1 km) |
| 84585 | San Pedro | Albay | Masbate | Cataingan (1.7 km) |
| 84587 | San Pedro | Batanes | Leyte | Burauen (9.1 km) |
| 84588 | San Pedro | Oriental Mindoro | Occidental Mindoro | Rizal (4.8 km) |
| 84590 | San Pedro One | Occidental Mindoro | Batangas | Malvar (1.9 km) |
| 84596 | San Rafael | Occidental Mindoro | Laguna | Nagcarlan (0.9 km) |
| 84611 | San Salvador | Antique | Iloilo | Barotac Viejo (5.5 km) |
| 84612 | San Sebastian | Batanes | Western Samar | San Sebastian (1.1 km) |
| 84619 | San Vicente | Benguet | Bukidnon | Kitaotao (3.1 km) |
| 84621 | San Vicente | Batanes | Leyte | Kananga (7.5 km) |
| 84624 | San Vicente | Occidental Mindoro | Quezon | Lopez (6.2 km) |
| 84651 | Santa Catalina Sur | Occidental Mindoro | Quezon | Candelaria (6.4 km) |
| 84653 | Santa Clara | Occidental Mindoro | Batangas | San Pascual (5.9 km) |
| 84659 | Santa Cruz | Occidental Mindoro | Laguna | Santa Cruz (0.2 km) |
| 84663 | Santa Cruz | Antique | Negros Occidental | Murcia (6.5 km) |
| 84693 | Santa Nino | Bataan | Cebu | Tuburan (7.0 km) |
| 84694 | Santa Paz | Batanes | Leyte | Matalom (2.6 km) |
| 84698 | Santa Rita Aplaya | Occidental Mindoro | Batangas | San Pascual (3.1 km) |
| 84701 | Santa Rosa Sur | Albay | Camarines Norte | Jose Panganiban (4.9 km) |
| 84702 | Santa Teresa | Oriental Mindoro | Occidental Mindoro | Magsaysay (7.6 km) |
| 84703 | Santa Teresa | Antique | Guimaras | Jordan (3.2 km) |
| 84706 | Santa Teresita | Albay | Camarines Sur | Baao (6.4 km) |
| 84711 | Santiago | Antique | Iloilo | Barotac Viejo (6.8 km) |
| 84727 | Santo Niño | Occidental Mindoro | Batangas | Ibaan (3.5 km) |
| 84738 | Santor | Occidental Mindoro | Batangas | Malvar (8.0 km) |
| 84763 | Siari | Zamboanga Sibugay | Zamboanga del Norte | Sindangan (9.6 km) |
| 84779 | Sibutao | Zamboanga Sibugay | Zamboanga del Norte | Sibutad (2.5 km) |
| 84787 | Siguinon | Batanes | Leyte | Albuera (2.9 km) |
| 84795 | Sillon | Bataan | Cebu | Bantayan (3.7 km) |
| 84828 | Siraway | Zamboanga Sibugay | Zamboanga del Norte | Sirawai (0.1 km) |
| 84841 | Solana | Benguet | Misamis Oriental | Jasaan (3.8 km) |
| 84859 | Sugbongkogon | Benguet | Misamis Oriental | Sugbongcogon (1.2 km) |
| 84866 | Sulangan | Bataan | Cebu | Bantayan (7.1 km) |
| 84877 | Sumilao | Benguet | Bukidnon | Sumilao (5.8 km) |
| 84904 | Tabon | Bataan | Cebu | Badian (9.8 km) |
| 84905 | Tabon | Oriental Mindoro | Palawan | Quezon (0.5 km) |
| 84907 | Tabonoc | Batanes | Leyte | Bato (2.6 km) |
| 84913 | Tabuc Pontevedra | Antique | Capiz | Pontevedra (1.8 km) |
| 84921 | Taclobo | Oriental Mindoro | Romblon | San Fernando (1.8 km) |
| 84942 | Tagkawayan Sabang | Occidental Mindoro | Quezon | タグカワヤン (2.7 km) |
| 84952 | Tagum Norte | Bataan | Bohol | Trinidad (5.1 km) |
| 84967 | Talaibon | Occidental Mindoro | Batangas | Ibaan (2.4 km) |
| 84971 | Talangnan | Bataan | Cebu | Malabuyoc (1.8 km) |
| 84974 | Talibon | Bataan | Bohol | Talibon (0.3 km) |
| 85004 | Tambac | Antique | Aklan | New Washington (3.5 km) |
| 85024 | Tampayan | Oriental Mindoro | Romblon | Magdiwang (2.1 km) |
| 85036 | Tangke | Bataan | Cebu | Minglanilla (7.6 km) |
| 85047 | Tapas | Antique | Capiz | Tapaz (0.1 km) |
| 85065 | Tawagan | Zamboanga Sibugay | Zamboanga del Sur | Labangan (5.2 km) |
| 85069 | Tayabas Ibaba | Occidental Mindoro | Quezon | კატანაუანი (5.8 km) |
| 85096 | Tibigan | Bataan | Bohol | Tubigon (0.5 km) |
| 85113 | Tiguha | Zamboanga Sibugay | Zamboanga del Sur | Lapuyan (7.5 km) |
| 85124 | Tinaan | Bataan | Cebu | Madridejos (1.8 km) |
| 85143 | Tiparak | Zamboanga Sibugay | Zamboanga del Sur | Tambulig (4.1 km) |
| 85150 | Tiwi | Antique | Iloilo | Barotac Nuevo (5.0 km) |
| 85165 | Tominhao | Bataan | Cebu | Daanbantayan (4.2 km) |
| 85183 | Tuban | Oriental Mindoro | Occidental Mindoro | سبلیں ، وکڈینٹل مندورو (7.1 km) |
| 85197 | Tubod-dugoan | Bataan | Cebu | Dumanjug (1.9 km) |
| 85201 | Tucdao | Batanes | Biliran | Culaba (9.1 km) |
| 85202 | Tucuran | Zamboanga Sibugay | Zamboanga del Sur | Tukuran (0.5 km) |
| 85220 | Tumalim | Occidental Mindoro | Batangas | Tuy (7.1 km) |
| 85238 | Tuyum | Antique | Negros Occidental | Cauayan (6.5 km) |
| 85247 | Umabay | Albay | Masbate | Mobo (3.9 km) |
| 85252 | Ungca | Antique | Iloilo | Pavia (2.9 km) |
| 85255 | Unidos | Antique | Aklan | マライ (9.9 km) |
| 85277 | Valencia | Batanes | Leyte | Kananga (8.6 km) |
| 85279 | Valle Hermoso | Bataan | Bohol | Carmen (4.7 km) |
| 85318 | Yapak | Antique | Aklan | マライ (6.2 km) |
| 143935 | Daliao | Bukidnon | Sarangani | Maasim (4.8 km) |
| 143949 | Glan Peidu | Bukidnon | Sarangani | Glan (3.9 km) |
| 143952 | Ilaya | Bukidnon | Sarangani | Glan (2.6 km) |
| 143956 | Kablalan | Bukidnon | Sarangani | Glan (4.9 km) |
| 143960 | Kamanga | Bukidnon | Sarangani | Maasim (6.6 km) |
| 143961 | Kapatan | Bukidnon | Sarangani | Glan (9.4 km) |
| 144000 | Lun Pequeño | Bukidnon | Sarangani | Alabel (7.2 km) |
| 144007 | Mabay | Bukidnon | Sarangani | Maitum (3.3 km) |
| 144020 | Malbang | Bukidnon | Sarangani | Maasim (5.4 km) |
| 144031 | Marbel | Bukidnon | Cotabato | Matalam (3.3 km) |
| 144032 | Mariano Marcos | Bukidnon | Sultan Kudarat | Lambayong (7.6 km) |
| 144037 | Mindupok | Bukidnon | Sarangani | Maitum (9.2 km) |
| 144038 | Nalus | Bukidnon | Sarangani | Kiamba (5.0 km) |
| 144063 | Polo | Bukidnon | South Cotabato | Polomolok (7.3 km) |
| 144076 | Salunayan | Bukidnon | Cotabato | Midsayap (5.7 km) |
| 144078 | San Miguel | Bukidnon | South Cotabato | Norala (5.0 km) |
| 144079 | San Vicente | Bukidnon | South Cotabato | Banga (3.3 km) |
| 144090 | T'boli | Bukidnon | South Cotabato | T'Boli (8.5 km) |
| 144093 | Taluya | Bukidnon | Sarangani | Glan (3.7 km) |
| 144095 | Tambilil | Bukidnon | Sarangani | Kiamba (5.8 km) |
| 144099 | Tañgo | Bukidnon | Sarangani | Glan (6.7 km) |
| 144102 | Tinoto | Bukidnon | Sarangani | Maasim (8.6 km) |
| 144157 | Concepcion | Bohol | Davao del Norte | Sawata (1.5 km) |
| 144171 | Esperanza | Bohol | Davao del Norte | Asuncion (5.8 km) |
| 144197 | La Libertad | Bohol | Davao del Norte | Braulio E. Dujali (5.6 km) |
| 144286 | San Vicente | Bohol | Davao de Oro | Laak (7.1 km) |
| 144327 | Tubod | Bohol | Davao del Norte | Carmen (6.9 km) |
| 144338 | Baliton | Bukidnon | Sarangani | Glan (9.5 km) |
| 144345 | Barongis | Bukidnon | Cotabato | Libungan (5.6 km) |
| 144347 | Batasan | Bukidnon | Cotabato | Makilala (9.2 km) |
| 144354 | Buadtasan | Bukidnon | Sarangani | Kiamba (2.1 km) |
| 144365 | Cebuano | Bukidnon | South Cotabato | Tupi (6.4 km) |
| 144376 | Anticala | Bulacan | Agusan del Norte | Remedios T. Romualdez (8.5 km) |
| 144379 | Bacolod | Bulacan | Surigao del Sur | Cagwait (2.0 km) |
| 144383 | Bancasi | Bulacan | Agusan del Norte | Buenavista (6.4 km) |
| 144396 | Buenavista | Bulacan | Agusan del Norte | Buenavista (0.3 km) |
| 144401 | Butuan | Bulacan | Agusan del Norte | Magallanes (8.2 km) |
| 144406 | Caloc-an | Bulacan | Agusan del Norte | Magallanes (3.1 km) |
| 144409 | Capalayan | Bulacan | Surigao del Norte | Tagana-an (6.4 km) |
| 144418 | Cuevas | Bulacan | Agusan del Sur | Trento (4.7 km) |
| 144424 | Del Pilar | Bulacan | Agusan del Norte | Tubay (7.0 km) |
| 144434 | Ipil | Bulacan | Surigao del Norte | San Francisco (2.2 km) |
| 144441 | La Paz | Bulacan | Agusan del Sur | La Paz (1.5 km) |
| 144443 | La Union | Bulacan | Agusan del Norte | Remedios T. Romualdez (6.6 km) |
| 144448 | Libas | Bulacan | Surigao del Norte | Del Carmen (2.2 km) |
| 144449 | Libertad | Bulacan | Agusan del Norte | Magallanes (8.9 km) |
| 144455 | Los Angeles | Bulacan | Agusan del Norte | Remedios T. Romualdez (5.1 km) |
| 144458 | Luna | Bulacan | Surigao del Norte | Sison (9.2 km) |
| 144460 | Mabua | Bulacan | Surigao del Norte | San Francisco (3.5 km) |
| 144474 | Patin-ay | Bulacan | Agusan del Sur | Prosperidad (6.6 km) |
| 144495 | San Miguel | Bulacan | Surigao del Sur | San Miguel (7.0 km) |
| 144497 | Santa Ana | Bulacan | Agusan del Norte | Tubay (5.5 km) |
| 144501 | Santa Monica | Bulacan | Surigao del Norte | Santa Monica (0.0 km) |
| 144508 | Socorro | Bulacan | Surigao del Norte | Socorro (0.4 km) |
| 144520 | Tigao | Bulacan | Surigao del Sur | Cortes (7.6 km) |
| 144521 | Trento | Bulacan | Agusan del Sur | Trento (7.9 km) |
| 144526 | Union | Bulacan | Surigao del Norte | ジェネラル・ルナ (5.8 km) |
| 144559 | Lamitan City | Cagayan | Basilan | Tuburan (9.8 km) |
| 144576 | Luuk Datan | Cagayan | Tawi-Tawi | Simunul (9.9 km) |
| 144591 | Marunggas | Cagayan | Sulu | Hadji Panglima Tahil (5.6 km) |
| 144597 | Molundo | Cagayan | Lanao del Sur | Mulondo (0.4 km) |
| 144598 | Municipality of Indanan | Cagayan | Sulu | Indanan (0.9 km) |
| 144600 | Municipality of Pangutaran | Cagayan | Sulu | Pangutaran (3.3 km) |
| 144603 | New Batu Batu | Cagayan | Tawi-Tawi | Panglima Sugala (0.7 km) |
| 144619 | Pagatin | Cagayan | Maguindanao del Sur | Datu Salibo (5.6 km) |
| 144623 | Paitan | Cagayan | Nueva Vizcaya | Bayombong (2.1 km) |
| 144624 | Panabuan | Cagayan | Sulu | Indanan (4.3 km) |
| 144639 | Bato Bato | Cagayan | Sulu | Indanan (4.4 km) |
| 144649 | Bongued | Cagayan | Maguindanao del Norte | Kabuntalan (3.9 km) |
| 144659 | Pandan Niog | Cagayan | Sulu | Pangutaran (8.3 km) |
| 144665 | Parangan | Cagayan | Tawi-Tawi | Panglima Sugala (6.1 km) |
| 144674 | Cagayan de Tawi-Tawi | Cagayan | Tawi-Tawi | Mapun (7.0 km) |
| 144692 | Ebcor Town | Cagayan | Maguindanao del Norte | Barira (5.6 km) |
| 144704 | Poon-a-Bayabao | Cagayan | Lanao del Sur | Poona Bayabao (1.9 km) |
| 144734 | Tablas | Cagayan | Basilan | Tuburan (2.4 km) |
| 144738 | Talipaw | Cagayan | Sulu | Maimbung (7.2 km) |
| 144771 | Baguio | Camarines Norte | Benguet | Tuba (4.5 km) |
| 144780 | Bayabas | Camarines Norte | Benguet | Sablan (6.0 km) |
| 144789 | Buguias | Camarines Norte | Benguet | Buguias (9.7 km) |
| 144790 | Bulalacao | Camarines Norte | Benguet | Mankayan (2.8 km) |
| 144791 | Butigui | Camarines Norte | Mountain Province | Paracelis (8.0 km) |
| 144802 | Gambang | Camarines Norte | Benguet | Buguias (7.2 km) |
| 144803 | Guinsadan | Camarines Norte | Mountain Province | Bauko (3.1 km) |
| 144821 | Langiden | Camarines Norte | Abra | Langiden (6.7 km) |
| 144823 | Licuan | Camarines Norte | Abra | Licuan-Baay (6.5 km) |
| 144852 | Sal-Lapadan | Camarines Norte | Abra | Sallapadan (2.8 km) |
| 144856 | San Ramon | Camarines Norte | Abra | Manabo (2.2 km) |
| 145046 | San Mariano | Davao Occidental | Davao de Oro | Maragusan (5.1 km) |
| 145099 | Accusilian | Agusan del Norte | Cagayan | ტუაო (1.6 km) |
| 145122 | Bagong Tanza | Agusan del Norte | Isabela | Aurora (2.8 km) |
| 145123 | Bagu | Agusan del Norte | Cagayan | Pamplona (4.8 km) |
| 145140 | Binguang | Agusan del Norte | Isabela | San Pablo (1.2 km) |
| 145143 | Bone South | Agusan del Norte | Nueva Vizcaya | Aritao (7.1 km) |
| 145164 | Carig | Agusan del Norte | Cagayan | Solana (5.6 km) |
| 145186 | Dumabato | Agusan del Norte | Quirino | Maddela (3.2 km) |
| 145190 | Echague (town) | Agusan del Norte | Isabela | エチャグエ (0.1 km) |
| 145193 | Esperanza East | Agusan del Norte | Isabela | Burgos (5.1 km) |
| 145214 | La Paz | Agusan del Norte | Isabela | Cabatuan (5.3 km) |
| 145250 | Municipality of Delfin Albano | Agusan del Norte | Isabela | Tumauini (7.1 km) |
| 145251 | Muñoz East | Agusan del Norte | Isabela | Roxas (4.6 km) |
| 145260 | Palagao Norte | Agusan del Norte | Cagayan | Gattaran (8.0 km) |
| 145274 | Ramon (municipal capital) | Agusan del Norte | Isabela | Ramon (0.2 km) |
| 145275 | Ramos West | Agusan del Norte | Isabela | エチャグエ (6.7 km) |
| 145282 | Salinas | Agusan del Norte | Nueva Vizcaya | Aritao (8.2 km) |
| 145285 | San Antonio | Agusan del Norte | Nueva Vizcaya | Bambang (4.1 km) |
| 145287 | San Bernardo | Agusan del Norte | Isabela | Santo Tomas (1.7 km) |
| 145290 | San Isidro | Agusan del Norte | Isabela | エチャグエ (7.0 km) |
| 145301 | San Vicente | Agusan del Norte | Cagayan | Santa Ana (5.5 km) |
| 145305 | Santa Cruz | Agusan del Norte | Cagayan | Pamplona (6.5 km) |
| 145351 | Angeles | Agusan del Sur | Pampanga | Porac (9.5 km) |
| 145357 | Bacabac | Agusan del Sur | Tarlac | Camiling (4.5 km) |
| 145367 | Balaoang | Agusan del Sur | Tarlac | Paniqui (6.9 km) |
| 145370 | Balayang | Agusan del Sur | Tarlac | Victoria (3.4 km) |
| 145373 | Balite | Agusan del Sur | Tarlac | Pura (2.3 km) |
| 145377 | Baloy | Agusan del Sur | Nueva Ecija | Talugtug (4.9 km) |
| 145389 | Bayanan | Agusan del Sur | Oriental Mindoro | Baco (7.8 km) |
| 145393 | Bicos | Agusan del Sur | Nueva Ecija | Llanera (2.3 km) |
| 145394 | Biga | Agusan del Sur | Oriental Mindoro | Baco (8.7 km) |
| 145396 | Bobon Second | Agusan del Sur | Tarlac | Mayantoc (4.1 km) |
| 145444 | Carmen | Agusan del Sur | Nueva Ecija | Zaragoza (3.6 km) |
| 145449 | Cavite | Agusan del Sur | Nueva Ecija | Guimba (2.0 km) |
| 145450 | Cawayan Bugtong | Agusan del Sur | Nueva Ecija | Guimba (3.3 km) |
| 145463 | Culianin | Agusan del Sur | Bulacan | Bustos (4.3 km) |
| 145469 | Del Pilar | Agusan del Sur | Pampanga | Mexico (3.9 km) |
| 145473 | Diliman Primero | Agusan del Sur | Bulacan | San Ildefonso (6.1 km) |
| 145524 | Mabilang | Agusan del Sur | Tarlac | Camiling (8.2 km) |
| 145546 | Manatal | Agusan del Sur | Bulacan | Pandi (3.8 km) |
| 145549 | Manibaug Pasig | Agusan del Sur | Pampanga | Porac (3.6 km) |
| 145592 | Pamatawan | Agusan del Sur | Zambales | Castillejos (1.6 km) |
| 145595 | Pance | Agusan del Sur | Tarlac | Ramos (3.4 km) |
| 145598 | Pando | Agusan del Sur | Tarlac | La Paz (7.2 km) |
| 145603 | Papaya | Agusan del Sur | Nueva Ecija | San Antonio (2.3 km) |
| 145620 | Pulo | Agusan del Sur | Bulacan | Angat (4.1 km) |
| 145621 | Pulong Gubat | Agusan del Sur | Bulacan | Guiguinto (3.8 km) |
| 145622 | Pulong Sampalok | Agusan del Sur | Bulacan | Doña Remedios Trinidad (5.0 km) |
| 145623 | Pulung Santol | Agusan del Sur | Pampanga | Porac (3.6 km) |
| 145627 | Purac | Agusan del Sur | Zambales | Botolan (4.3 km) |
| 145632 | Rizal | Agusan del Sur | Nueva Ecija | Bongabon (6.2 km) |
| 145633 | Sabang | Agusan del Sur | Bataan | Morong (2.5 km) |
| 145638 | Salvacion I | Agusan del Sur | Nueva Ecija | Lupao (4.8 km) |
| 145641 | San Agustin | Agusan del Sur | Zambales | San Marcelino (4.6 km) |
| 145643 | San Alejandro | Agusan del Sur | Nueva Ecija | Quezon (4.1 km) |
| 145644 | San Andres | Agusan del Sur | Nueva Ecija | Guimba (6.7 km) |
| 145645 | San Anton | Agusan del Sur | Nueva Ecija | Jaen (1.7 km) |
| 145651 | San Basilio | Agusan del Sur | Pampanga | სანტა-რიტა (5.4 km) |
| 145655 | San Casimiro | Agusan del Sur | Nueva Ecija | Licab (2.5 km) |
| 145657 | San Cristobal | Agusan del Sur | Nueva Ecija | Licab (1.6 km) |
| 145661 | San Felipe Old | Agusan del Sur | Nueva Ecija | Aliaga (6.7 km) |
| 145663 | San Francisco | Agusan del Sur | Nueva Ecija | San Antonio (5.5 km) |
| 145677 | San Juan de Mata | Agusan del Sur | Tarlac | San Jose (9.5 km) |
| 145679 | San Lorenzo | Agusan del Sur | Zambales | Masinloc (5.4 km) |
| 145685 | San Mariano | Agusan del Sur | Nueva Ecija | San Antonio (2.8 km) |
| 145690 | San Nicolas | Agusan del Sur | Tarlac | Victoria (0.9 km) |
| 145694 | San Patricio | Agusan del Sur | Pampanga | Mexico (3.8 km) |
| 145701 | San Roque Dau First | Agusan del Sur | Pampanga | სანტა-რიტა (4.6 km) |
| 145706 | San Vincente | Agusan del Sur | Oriental Mindoro | Baco (9.9 km) |
| 145712 | Santa Fe | Agusan del Sur | Zambales | San Marcelino (7.0 km) |
| 145714 | Santa Ines West | Agusan del Sur | Tarlac | Santa Ignacia (7.4 km) |
| 145728 | Santa Teresa First | Agusan del Sur | Pampanga | Lubao (4.6 km) |
| 145730 | Santo Cristo | Agusan del Sur | Nueva Ecija | San Isidro (2.3 km) |
| 145736 | Santo Niño | Agusan del Sur | Tarlac | Concepcion (3.3 km) |
| 145738 | Santo Rosario | Agusan del Sur | Nueva Ecija | Santa Rosa (5.4 km) |
| 145746 | Sapol | Agusan del Sur | Oriental Mindoro | Baco (9.9 km) |
| 145749 | Saysain | Agusan del Sur | Bataan | Bagac (3.8 km) |
| 145758 | Sula | Agusan del Sur | Tarlac | San Jose (7.7 km) |
| 145760 | Tabacao | Agusan del Sur | Nueva Ecija | Talavera (7.7 km) |
| 145761 | Tabon | Agusan del Sur | Nueva Ecija | San Isidro (4.3 km) |
| 145765 | Talang | Agusan del Sur | Pampanga | San Luis (5.2 km) |
| 145778 | Upig | Agusan del Sur | Bulacan | San Ildefonso (8.0 km) |
| 145781 | Villa Aglipay | Agusan del Sur | Tarlac | San Jose (1.8 km) |
| 145815 | Balingasay | Abra | Pangasinan | Bolinao (5.3 km) |
| 145847 | Bobonan | Abra | Pangasinan | Pozorrubio (3.2 km) |
| 145873 | Calepaan | Abra | Pangasinan | Binalonan (4.0 km) |
| 145893 | Caterman | Abra | Ilocos Sur | Galimuyod (5.9 km) |
| 145906 | Dagup | Abra | La Union | Bagulin (3.4 km) |
| 145932 | Hacienda | Abra | Pangasinan | Bugallon (2.2 km) |
| 145960 | Lusong | Abra | La Union | ბანგარი (3.5 km) |
| 145976 | Malibong East | Abra | Pangasinan | Urbiztondo (2.7 km) |
| 146007 | Paitan Este | Abra | Pangasinan | Sual (7.2 km) |
| 146008 | Palacpalac | Abra | Pangasinan | Pozorrubio (2.6 km) |
| 146009 | Palguyod | Abra | Pangasinan | Pozorrubio (3.3 km) |
| 146026 | Polo | Abra | Pangasinan | Bani (9.7 km) |
| 146027 | Polong | Abra | Pangasinan | Lingayen (5.6 km) |
| 146028 | Polong Norte | Abra | Pangasinan | Malasiqui (1.6 km) |
| 146040 | Ranao | Abra | Pangasinan | Bani (5.2 km) |
| 146058 | San Fernando Poblacion | Abra | La Union | San Juan (5.9 km) |
| 146060 | San Gabriel First | Abra | Pangasinan | Bayambang (4.7 km) |
| 146071 | San Quintin | Abra | Pangasinan | San Quintin (0.0 km) |
| 146109 | Tandoc | Abra | Pangasinan | Calasiao (7.5 km) |

</details>

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/PH.json` — `state_id` and `state_code` on 477 records

## Philippine municipalities whose point lies in another province

**69 Philippine municipality and city records** take their own Wikidata item's point (Maitum and Dilasag take
GeoNames' on-land point instead, as their item's point is just offshore): the stored point lies in a
neighbouring province, 7–58 km from the place (Davao City sat in Cotabato province; Lucban and Mauban, Quezon, in
Laguna; Oroquieta in Zamboanga del Norte). *Kibungan* (Benguet) was also filed under the wrong
province (Camarines Norte, point in Ilocos Sur) and moves with its point.

The review of #1664 found these: following the bad point there would have moved the municipality to the wrong
province.

### How they were verified
- **The record is the municipality:** its `wikiDataId` is a municipality or city of the Philippines whose label or
  alias is the record's name, and the record's population is within ×1.5 of the item's (for most, identical; these
  populations match current Wikidata figures, and for common names the same figure also appears on same-named
  records elsewhere, so the Wikidata item is the main evidence).
- **The point is wrong, not the item:** province polygons (geoBoundaries PHL ADM2, as in #1664) put the stored point
  in another province, at least 2 km from the right one, and the item's point inside the item's province (Maitum and Dilasag take GeoNames' on-land point
  instead, as their item's point is just offshore).

620 municipality records are more than 5 km from their item's point, but a municipality spans many kilometres, so
only those whose point lies in another province are changed here.

### After the independent review
The review (Wikidata items; Nominatim on all old and new points) found 70 of 71 correct. Changes:
- *Jose Abad Santos* (144184) is left out: it is a copy of record 144949, which is already right; moving it would
  put two identical records 30 m apart. It waits for the duplicate policy in #1643.
- *South Upi* (144726) is left out: its old point is inside South Upi, so it does not meet this PR's rule.

Six fixed records now sit within 1 km of an older record carrying the same Wikidata item, filed under the wrong
province or a region: Kibungan / 82897, Davao City / 82396 "Davao", Tapaz / 85047 "Tapas", M'lang / 144003,
Lumban / 83217 "Lumbang", San Agustin / 144485. They are duplicates for the #1643 duplicate clean-up.

### Fix
`latitude` and `longitude` change on 69 records; `state_id`/`state_code` on 1. All keep `Asia/Manila`.

| id | Municipality | Province | Stored point was in | km off | Population | New point (Wikidata, or GeoNames) |
|---|---|---|---|---:|---:|---|
| 81219 | Alimodian | Iloilo | Antique | 25.7 | 39,814 | Q274508 (10.81956, 122.43216) |
| 81444 | Balangkayan | Eastern Samar | Western Samar | 31.7 | 10,014 | Q313914 (11.47278, 125.51083) |
| 81611 | Batad | Iloilo | Capiz | 11.4 | 22,174 | Q274654 (11.41667, 123.11667) |
| 81666 | Bayog | Zamboanga del Sur | Zamboanga Sibugay | 18.8 | 32,687 | Q132032 (7.84741, 123.04226) |
| 81828 | Buenavista | Guimaras | Iloilo | 7.4 | 70,691 | Q313781 (10.69700, 122.64800) |
| 82055 | Calinog | Iloilo | Capiz | 32.5 | 63,896 | Q274713 (11.12252, 122.53802) |
| 82164 | Carles | Iloilo | Capiz | 9.0 | 74,177 | Q274731 (11.56667, 123.13333) |
| 82181 | Carrascal | Surigao del Sur | Agusan del Norte | 25.8 | 25,672 | Q155558 (9.36833, 125.94944) |
| 82540 | Floridablanca | Pampanga | Zambales | 14.0 | 146,095 | Q55700 (14.97400, 120.52800) |
| 82709 | Ibajay | Aklan | Antique | 13.3 | 53,399 | Q626695 (11.82111, 122.16167) |
| 82788 | Jamindan | Capiz | Antique | 48.9 | 40,472 | Q356106 (11.40944, 122.51028) |
| 82792 | Janiuay | Iloilo | Antique | 25.7 | 67,509 | Q82570 (10.95000, 122.50000) |
| 83066 | Leon | Iloilo | Antique | 25.8 | 52,777 | Q274987 (10.78085, 122.38940) |
| 83074 | Lianga | Surigao del Sur | Agusan del Sur | 9.4 | 34,213 | Q155590 (8.63296, 126.09322) |
| 83140 | Lingig | Surigao del Sur | Agusan del Sur | 23.1 | 35,203 | Q155598 (8.03805, 126.41266) |
| 83198 | Lucban | Quezon | Laguna | 7.4 | 54,134 | Q103941 (14.11333, 121.55694) |
| 83308 | Madalag | Aklan | Antique | 27.1 | 19,043 | Q626820 (11.52694, 122.30639) |
| 83313 | Madrid | Surigao del Sur | Agusan del Norte | 26.3 | 16,872 | Q155605 (9.26194, 125.96472) |
| 83373 | Maitum | Sarangani | Sultan Kudarat | 20.4 | 46,120 | GeoNames 1703471 (6.03917, 124.49861); Q174442's point is 1.2 km offshore |
| 83582 | Marihatag | Surigao del Sur | Agusan del Sur | 54.8 | 19,730 | Q155611 (8.80083, 126.29833) |
| 83635 | Mauban | Quezon | Laguna | 19.9 | 70,135 | Q103952 (14.19111, 121.73083) |
| 83646 | Mayantoc | Tarlac | Zambales | 27.1 | 34,091 | Q56444 (15.62028, 120.37750) |
| 83669 | Midsalip | Zamboanga del Sur | Zamboanga del Norte | 23.0 | 35,643 | Q132262 (8.03278, 123.31472) |
| 83862 | Oroquieta | Misamis Occidental | Zamboanga del Norte | 30.9 | 71,373 | Q1067897 (8.48333, 123.80000) |
| 84163 | Porac | Pampanga | Zambales | 24.8 | 147,551 | Q55721 (15.07194, 120.54194) |
| 84463 | San Clemente | Tarlac | Pangasinan | 12.4 | 13,781 | Q56471 (15.71194, 120.36028) |
| 84744 | Sapang Dalaga | Misamis Occidental | Zamboanga del Norte | 7.6 | 21,006 | Q196222 (8.55000, 123.56667) |
| 84868 | Sulat | Eastern Samar | Western Samar | 24.6 | 15,776 | Q314257 (11.81667, 125.45000) |
| 84936 | Tagbina | Surigao del Sur | Agusan del Sur | 13.6 | 41,157 | Q155633 (8.45778, 126.15778) |
| 143938 | Datu Montawal | Maguindanao del Sur | Cotabato | 10.2 | 42,181 | Q212411 (7.10000, 124.76667) |
| 144025 | Malungon | Sarangani | South Cotabato | 34.5 | 78,599 | Q174468 (6.37759, 125.27265) |
| 144035 | Midsayap | Cotabato | Maguindanao del Norte | 12.4 | 115,735 | Q315283 (7.19167, 124.53333) |
| 144059 | Pigcawayan | Cotabato | Maguindanao del Norte | 19.7 | 53,593 | Q304654 (7.27898, 124.42425) |
| 144251 | Nabunturan | Davao de Oro | Davao del Norte | 14.3 | 85,949 | Q315570 (7.60341, 125.96705) |
| 144280 | San Luis | Aurora | Nueva Ecija | 25.3 | 36,841 | Q53092 (15.71667, 121.51667) |
| 144773 | Balbalan | Kalinga | Abra | 26.8 | 13,332 | Q35848 (17.44361, 121.20083) |
| 144781 | Besao | Mountain Province | Ilocos Sur | 12.1 | 6,315 | Q36012 (17.09528, 120.85611) |
| 144793 | Calanasan | Apayao | Ilocos Norte | 35.0 | 12,176 | Q29018 (18.25500, 121.04361) |
| 144806 | Hungduan | Ifugao | Mountain Province | 12.8 | 8,970 | Q30413 (16.83333, 121.00000) |
| 144810 | Kabugao | Apayao | Ilocos Norte | 37.8 | 16,425 | Q30053 (18.02389, 121.18333) |
| 144813 | Kibungan | Benguet (was Camarines Norte) | Ilocos Sur | 29.0 | 16,884 | Q30349 (16.69389, 120.65389) |
| 144828 | Lubuagan | Kalinga | Abra | 28.9 | 8,660 | Q35858 (17.35000, 121.18333) |
| 144839 | Pasil | Kalinga | Abra | 23.6 | 10,690 | Q35866 (17.38944, 121.15972) |
| 144863 | Tadian | Mountain Province | Ilocos Sur | 9.5 | 18,073 | Q36099 (16.99611, 120.82083) |
| 144903 | Boston | Davao Oriental | Davao de Oro | 28.7 | 15,074 | Q314574 (7.86972, 126.37611) |
| 144930 | Davao City | Davao del Sur | Cotabato | 57.8 | 1,848,947 | Q1473 (7.06623, 125.60944) |
| 145105 | Alfonso Castañeda | Nueva Vizcaya | Nueva Ecija | 17.9 | 8,933 | Q51474 (15.79333, 121.30250) |
| 145150 | Cabagan | Isabela | Kalinga | 29.7 | 55,445 | Q49361 (17.43333, 121.76667) |
| 145181 | Diffun | Quirino | Nueva Vizcaya | 21.2 | 58,254 | Q53071 (16.59361, 121.50250) |
| 145188 | Dupax del Sur | Nueva Vizcaya | Nueva Ecija | 22.8 | 22,388 | Q51484 (16.28417, 121.09167) |
| 145211 | Jones | Isabela | Quirino | 10.2 | 46,160 | Q49372 (16.55833, 121.70000) |
| 145213 | Kayapa | Nueva Vizcaya | Benguet | 18.0 | 27,865 | Q51486 (16.35833, 120.88611) |
| 145236 | Mallig | Isabela | Mountain Province | 8.9 | 32,509 | Q49435 (17.20861, 121.61056) |
| 145254 | Nagtipunan | Quirino | Nueva Vizcaya | 40.5 | 26,541 | Q53073 (16.21667, 121.60000) |
| 145295 | San Manuel | Isabela | Ifugao | 9.7 | 29,693 | Q50164 (17.01667, 121.63333) |
| 145422 | Cabiao | Nueva Ecija | Pampanga | 10.9 | 89,497 | Q55545 (15.25222, 120.85750) |
| 145445 | Carranglan | Nueva Ecija | Pangasinan | 20.7 | 43,694 | Q55546 (15.96083, 121.06306) |
| 145472 | Dilasag | Aurora | Quirino | 27.1 | 17,536 | GeoNames 1714887 (16.39750, 122.21306); Q53084's point is 0.1 km offshore |
| 145476 | Dingalan | Aurora | Nueva Ecija | 23.8 | 29,286 | Q53087 (15.38333, 121.40000) |
| 145477 | Dipaculao | Aurora | Quirino | 18.6 | 33,597 | Q53089 (15.98333, 121.63333) |
| 145556 | Maria Aurora | Aurora | Nueva Ecija | 25.3 | 45,972 | Q53090 (15.79670, 121.47370) |
| 146097 | Sugpon | Ilocos Sur | La Union | 9.3 | 4,238 | Q12893 (16.84472, 120.51528) |
| 154504 | Tapaz | Capiz | Antique | 51.6 | 57,684 | Q356398 (11.26222, 122.53694) |
| 154526 | M'lang | Cotabato | Maguindanao del Sur | 14.1 | 98,646 | Q315213 (6.94676, 124.87927) |
| 154575 | Lumban | Laguna | Rizal | 10.6 | 32,793 | Q69824 (14.29700, 121.45900) |
| 154580 | Santa Maria | Laguna | Rizal | 9.8 | 30,076 | Q75943 (14.47500, 121.42500) |
| 154807 | Bontoc | Southern Leyte | Leyte | 14.0 | 32,082 | Q173622 (10.35000, 124.96667) |
| 154831 | San Agustin | Surigao del Sur | Agusan del Sur | 30.2 | 23,698 | Q155618 (8.74366, 126.22143) |
| 154841 | Santa Rita | Western Samar | Leyte | 14.4 | 42,915 | Q816471 (11.45222, 124.94083) |

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/PH.json` — coordinates on 69 records; `state_id`/`state_code` on 1

## State levels, Algeria's ISO codes and Sulu's region

### Problem
- **`level`:** 159 states had a `level` not below their parent's: provinces at level 1 under level-1 regions in
  Morocco, Burkina Faso and Belgium; Guinea's regions and prefectures both at 2; Fiji's provinces at 1 under
  level-2 divisions; Spain's provinces at 1 under communities with no level. The docs define `level` as depth
  within the country (top = 1, next = 2), as France and Italy already follow.
- **Algeria:** seven of the provinces created in 2019 carried shifted ISO 3166-2 codes (El M'ghair as DZ-49
  instead of DZ-57, and so on).
- **Sulu:** filed under Bangsamoro (1316). The Supreme Court excluded Sulu from BARMM in 2024, and Executive
  Order 91 of 30 July 2025 assigned it to Region IX (PSGC 0906600000).

### Fix
- `level` on 226 states: Morocco 64 (6 roots get 1, 58 provinces 2), Burkina Faso 45, Belgium 10, Guinea 8
  (regions → 1), Fiji 19 (4 divisions and Rotuma → 1, 14 provinces → 2), Guinea-Bissau 11, Spain 69
  (19 communities and autonomous cities → 1, 50 provinces → 2). Every root is 1, every child its parent's + 1.
- Algeria, `iso2` and `iso3166_2` on 7 states (Ouled Djellal, Touggourt and Djanet were already right):

| id | Province | iso2 was → now | ISO 3166-2 | Wikidata |
|---|---|---|---|---|
| 4905 | El M'ghair | 49 → 57 | DZ-57 | Q77103173 |
| 4906 | El Menia | 50 → 58 | DZ-58 | Q76520264 |
| 4908 | Bordj Baji Mokhtar | 52 → 50 | DZ-50 | Q76592938 |
| 4909 | Béni Abbès | 53 → 52 | DZ-52 | Q21606902 |
| 4910 | Timimoun | 54 → 49 | DZ-49 | Q21606903 |
| 4913 | In Salah | 57 → 53 | DZ-53 | Q76593022 |
| 4914 | In Guezzam | 58 → 54 | DZ-54 | Q77102475 |

  No city or postcode refers to these provinces.
- Sulu (1288): `parent_id` 1316 → 1325 (Zamboanga Peninsula).

### Verification
- The Algerian codes match each province's Wikidata P300 and the Algerian official gazettes (2021, 2024).
- Sulu: Wikidata Q13887 P131 is Q13682 (Zamboanga Peninsula) from 2025-07-30; PSA announced the transfer.
- Each targeted state's level is its parent's + 1; (country, iso2) stays unique; all cities match their state.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/states/states.json` — `level` on 226 states, `iso2`/`iso3166_2` on 7, `parent_id` on 1

## Departments and council areas stored as cities

### Problem
The 2019 import brought in French departments and British council areas as city records, typed like towns, so
they appear in settlement lists.

### Fix
`type` → `area` on 155 records (73 FR, 82 GB). A record qualifies only if (a) its name carries an administrative
designator or it is a positively identified unit with no same-named populated place, (b) its population is empty
or within 5% of the unit's (GeoNames ADM2), (c) its own Wikidata item, if any, is administrative, and (d) no
same-named populated place has its population. 97 candidates were left alone, among them towns whose point sat on
the unit's point (Manchester, Birmingham, Leeds, Mayenne, Doubs, Landes) and bare names shared with a town
(Vienne, Gironde, Kent).

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/{FR,GB}.json` — `type` on 155 records

## Postal code formats

### Problem
21 countries' `postal_code_format` and `postal_code_regex` disagreed with each other or with the national scheme
(e.g. Greece's format `### ##` against a regex without the space; Honduras and Nicaragua with digit counts their
posts no longer use; Samoa with American Samoa's code; Chad with Turks and Caicos'), or were unanchored.

### Fix
Formats and regexes from the UPU addressing sheets and national postal sources; regexes are anchored whole-string
patterns. `postal_code_format` is a display mask (`#` a digit, `@` a letter, or any letter or digit for Ireland and
Panama) listing the main forms with `|`; the regex also accepts compatible variants (Greek codes without the space,
Cuban and Salvadoran codes without `CP`, Latvian and Lithuanian codes without the country prefix). The UAE, Hong
Kong, Macau and Chad have no national postcode scheme, and none is substantiated for North Korea; all five get
`null`. Panama's 2026 geocodes (e.g. A3AXE-PLZ29) and older office
codes are both accepted; Vietnam accepts its current five digits and the six-digit legacy codes still stored.

### Verification
Every postcode stored for these countries (AS, GR, LV, PA, SO, SV, VN) matches its new regex.

### Rollback
Revert the PR (squash commit).

### Files Changed
- `contributions/countries/countries.json` — postal format and regex on 21 countries

## Inuvik on permanent UTC−6 (tzdata 2026d)

The Northwest Territories moved to permanent UTC−6 on 2026-08-21 (IANA tzdata 2026d). Canada's `America/Inuvik`
entry in `countries.json` (standard offsets) changes from −25200 / UTC−07:00 / MST to −21600 / UTC−06:00 / CST.
Rollback: revert the PR. Files: `contributions/countries/countries.json` (1 timezone entry).

## States and cities on the wrong time zone

**95 states and 1,535 cities** get the right IANA time zone. #1649 checked each city against its neighbours;
that misses these, because here the wrong zone is shared by a whole state, most of its cities, or a whole country.

### States (95)
- **Russia (27):** federal subjects outside Moscow time were stored as `Europe/Moscow`; each takes its legal zone.
- **Papua New Guinea (21):** every province was on `Pacific/Bougainville` (UTC+11); only Bougainville uses it, the
  rest of the country is on `Pacific/Port_Moresby` (UTC+10).
- **Indonesia (17):** provinces on central time (WITA, UTC+8: Nusa Tenggara, Sulawesi, South/East/North
  Kalimantan) or eastern time (WIT, UTC+9: North Maluku and the five newer Papua provinces) were stored as
  `Asia/Jakarta` (UTC+7); Maluku and Papua already had `Asia/Jayapura`.
- **DR Congo (16):** the eastern provinces (Kivu, Katanga, Kasaï, Ituri, Uélé, Maniema, Tshopo…) were on
  `Africa/Kinshasa` (UTC+1); they are on `Africa/Lubumbashi` (UTC+2).
- **Mongolia (5):** Khovd, Uvs and Bayan-Ölgii are on `Asia/Hovd` (UTC+7) in tzdata. Zavkhan and Govi-Altai follow
  tzdata too (a #1643 decision): both states move from the `Asia/Choibalsan` alias to `Asia/Ulaanbaatar` (UTC+8), and
  their two cities, Uliastay and Altai, from `Asia/Hovd`. Mongolia's standards agency lists the two aimags on UTC+7;
  tzdata follows the observed UTC+8 and records the conflict.
- **French Polynesia (4):** the Austral, Leeward, Windward and Tuamotu-Gambier groups were on `Pacific/Gambier`
  (UTC−9); they are on Tahiti time (UTC−10), except the Gambier Islands themselves.
- **Kiribati (2), Micronesia (2), Greenland (1):** Gilbert and Line Islands had the Phoenix Islands' zone; Kosrae
  and Pohnpei had Chuuk's (UTC+10, they are UTC+11); Qeqertalik (west coast) had Danmarkshavn's UTC+0.

| Country | State | Was | Now |
|---|---|---|---|
| CD | Bas-Uélé | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Haut-Katanga | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Haut-Lomami | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Haut-Uélé | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Ituri | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Kasaï Central | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Kasaï Oriental | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Kasaï | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Lomami | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Lualaba | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Maniema | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Nord-Kivu | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Sankuru | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Sud-Kivu | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Tanganyika | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Tshopo | Africa/Kinshasa | Africa/Lubumbashi |
| FM | Kosrae | Pacific/Chuuk | Pacific/Kosrae |
| FM | Pohnpei | Pacific/Chuuk | Pacific/Pohnpei |
| GL | Qeqertalik | America/Danmarkshavn | America/Nuuk |
| ID | Kalimantan Timur | Asia/Jakarta | Asia/Makassar |
| ID | Kalimantan Selatan | Asia/Jakarta | Asia/Makassar |
| ID | Kalimantan Utara | Asia/Jakarta | Asia/Makassar |
| ID | Maluku Utara | Asia/Jakarta | Asia/Jayapura |
| ID | Nusa Tenggara Barat | Asia/Jakarta | Asia/Makassar |
| ID | Nusa Tenggara Timur | Asia/Jakarta | Asia/Makassar |
| ID | Nusa Tenggara | Asia/Jakarta | Asia/Makassar |
| ID | Papua Barat | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Barat Daya | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Pegunungan | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Selatan | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Tengah | Asia/Jakarta | Asia/Jayapura |
| ID | Sulawesi Utara | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Tenggara | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Selatan | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Barat | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Tengah | Asia/Jakarta | Asia/Makassar |
| KI | Gilbert | Pacific/Enderbury | Pacific/Tarawa |
| KI | Line | Pacific/Enderbury | Pacific/Kiritimati |
| MN | Khovd | Asia/Choibalsan | Asia/Hovd |
| MN | Uvs | Asia/Choibalsan | Asia/Hovd |
| MN | Bayan-Ölgii | Asia/Choibalsan | Asia/Hovd |
| MN | Govi-Altai | Asia/Choibalsan | Asia/Ulaanbaatar |
| MN | Zavkhan | Asia/Choibalsan | Asia/Ulaanbaatar |
| PF | Austral Islands | Pacific/Gambier | Pacific/Tahiti |
| PF | Leeward Islands | Pacific/Gambier | Pacific/Tahiti |
| PF | Tuamotu-Gambier | Pacific/Gambier | Pacific/Tahiti |
| PF | Windward Islands | Pacific/Gambier | Pacific/Tahiti |
| PG | Chimbu | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Central | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | East New Britain | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Eastern Highlands | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Enga | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | East Sepik | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Gulf | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Hela | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Jiwaka | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Milne Bay | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Morobe | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Madang | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Manus | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Port Moresby | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | New Ireland | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Oro | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Sandaun | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Southern Highlands | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | West New Britain | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Western Highlands | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Western | Pacific/Bougainville | Pacific/Port_Moresby |
| RU | Altai Republic | Europe/Moscow | Asia/Barnaul |
| RU | Altai Krai | Europe/Moscow | Asia/Barnaul |
| RU | Amur | Europe/Moscow | Asia/Yakutsk |
| RU | Astrakhan | Europe/Moscow | Europe/Astrakhan |
| RU | Bashkortostan | Europe/Moscow | Asia/Yekaterinburg |
| RU | Buryatia | Europe/Moscow | Asia/Irkutsk |
| RU | Chelyabinsk | Europe/Moscow | Asia/Yekaterinburg |
| RU | Kemerovo | Europe/Moscow | Asia/Novokuznetsk |
| RU | Kurgan | Europe/Moscow | Asia/Yekaterinburg |
| RU | Khabarovsk | Europe/Moscow | Asia/Vladivostok |
| RU | Khanty-Mansi | Europe/Moscow | Asia/Yekaterinburg |
| RU | Khakassia | Europe/Moscow | Asia/Krasnoyarsk |
| RU | Novosibirsk | Europe/Moscow | Asia/Novosibirsk |
| RU | Orenburg | Europe/Moscow | Asia/Yekaterinburg |
| RU | Perm | Europe/Moscow | Asia/Yekaterinburg |
| RU | Primorsky | Europe/Moscow | Asia/Vladivostok |
| RU | Sakha | Europe/Moscow | Asia/Yakutsk |
| RU | Saratov | Europe/Moscow | Europe/Saratov |
| RU | Sverdlovsk | Europe/Moscow | Asia/Yekaterinburg |
| RU | Tomsk | Europe/Moscow | Asia/Tomsk |
| RU | Tuva | Europe/Moscow | Asia/Krasnoyarsk |
| RU | Tyumen | Europe/Moscow | Asia/Yekaterinburg |
| RU | Udmurt | Europe/Moscow | Europe/Samara |
| RU | Ulyanovsk | Europe/Moscow | Europe/Ulyanovsk |
| RU | Yamalo-Nenets | Europe/Moscow | Asia/Yekaterinburg |
| RU | Jewish | Europe/Moscow | Asia/Vladivostok |
| RU | Zabaykalsky | Europe/Moscow | Asia/Chita |

### Cities (1,535)
- **Single-zone states:** a city on another offset takes the state's zone (Western Australia's towns on Sydney
  time; Mato Grosso, Mato Grosso do Sul, Rondônia and Acre on São Paulo time; Sinaloa; the Indonesian, Papua New
  Guinean, Congolese and Russian cases above). Western Australia's Eucla area (east of 125.5°E, UTC+8:45) is excluded.
- **Elsewhere:** a city whose offset differs from its state's zone, while at least 4 of its 5 nearest same-state
  cities are on the state's offset, takes their zone (e.g. Sonora on Mexico City time, Alberta on Toronto time).
  Multi-zone areas keep their cities, since there the neighbours share the city's offset.
- **By hand:** British Columbia's Central Coast and Port McNeill (Vancouver), Peace River (Dawson Creek), Elkford
  (Edmonton); Amazonas' central and northern municipalities (Manaus) and Atalaia do Norte, Envira and Ipixuna (Eirunepé,
  UTC−5); Sakha's Moscow-time cities in Yakutsk-time districts (Yakutsk).
- **Guard:** a city is changed only when at least 3 of its 5 nearest same-country cities are filed in the same state.
  This does not catch a batch filed in the wrong state together: the review found two such records moved across a
  zone line (Milpillas, Puente de Camotlán) and they are left as they were.

| Country | State | City zone was | Now | Cities |
|---|---|---|---|---:|
| BR | Mato Grosso | America/Sao_Paulo | America/Cuiaba | 121 |
| AU | Western Australia | Australia/Sydney | Australia/Perth | 118 |
| RU | Altai Krai | Europe/Moscow | Asia/Barnaul | 67 |
| BR | Mato Grosso do Sul | America/Sao_Paulo | America/Campo_Grande | 56 |
| RU | Irkutsk | Europe/Moscow | Asia/Irkutsk | 53 |
| RU | Bashkortostan | Europe/Moscow | Asia/Yekaterinburg | 49 |
| RU | Krasnoyarsk | Europe/Moscow | Asia/Krasnoyarsk | 49 |
| RU | Zabaykalsky | Europe/Moscow | Asia/Chita | 46 |
| BR | Rondônia | America/Sao_Paulo | America/Porto_Velho | 45 |
| RU | Chelyabinsk | Europe/Moscow | Asia/Yekaterinburg | 43 |
| RU | Amur | Europe/Moscow | Asia/Yakutsk | 38 |
| RU | Primorsky | Europe/Moscow | Asia/Vladivostok | 33 |
| RU | Sakha | Europe/Moscow | Asia/Yakutsk | 29 |
| RU | Novosibirsk | Europe/Moscow | Asia/Novosibirsk | 28 |
| RU | Saratov | Europe/Moscow | Europe/Saratov | 25 |
| RU | Sverdlovsk | Europe/Moscow | Asia/Yekaterinburg | 25 |
| RU | Kemerovo | Europe/Moscow | Asia/Novokuznetsk | 24 |
| RU | Tyumen | Europe/Moscow | Asia/Yekaterinburg | 23 |
| RU | Orenburg | Europe/Moscow | Asia/Yekaterinburg | 22 |
| RU | Buryatia | Europe/Moscow | Asia/Irkutsk | 21 |
| RU | Ulyanovsk | Europe/Moscow | Europe/Ulyanovsk | 21 |
| ID | Nusa Tenggara Timur | Asia/Jakarta | Asia/Makassar | 18 |
| ID | Sulawesi Selatan | Asia/Jakarta | Asia/Makassar | 18 |
| MX | Sinaloa | America/Mexico_City | America/Mazatlan | 18 |
| RU | Khabarovsk | Europe/Moscow | Asia/Vladivostok | 18 |
| RU | Kurgan | Europe/Moscow | Asia/Yekaterinburg | 18 |
| RU | Perm | Europe/Moscow | Asia/Yekaterinburg | 18 |
| RU | Omsk | Europe/Moscow | Asia/Omsk | 17 |
| BR | Amazonas | America/Sao_Paulo | America/Manaus | 16 |
| ID | Sulawesi Tenggara | Asia/Jakarta | Asia/Makassar | 16 |
| RU | Kamchatka | Europe/Moscow | Asia/Kamchatka | 16 |
| RU | Samara | Europe/Moscow | Europe/Samara | 16 |
| RU | Tomsk | Europe/Moscow | Asia/Tomsk | 16 |
| CA | British Columbia | America/Toronto | America/Vancouver | 15 |
| PF | Tuamotu-Gambier | Pacific/Gambier | Pacific/Tahiti | 15 |
| RU | Khakassia | Europe/Moscow | Asia/Krasnoyarsk | 13 |
| RU | Tuva | Europe/Moscow | Asia/Krasnoyarsk | 12 |
| MX | Sonora | America/Mexico_City | America/Hermosillo | 11 |
| PF | Windward Islands | Pacific/Gambier | Pacific/Tahiti | 11 |
| RU | Altai Republic | Europe/Moscow | Asia/Barnaul | 11 |
| BR | Acre | America/Sao_Paulo | America/Rio_Branco | 10 |
| ID | Sulawesi Tengah | Asia/Jakarta | Asia/Makassar | 10 |
| KI | Gilbert | Pacific/Enderbury | Pacific/Tarawa | 10 |
| RU | Jewish | Europe/Moscow | Asia/Vladivostok | 10 |
| ID | Kalimantan Selatan | Asia/Jakarta | Asia/Makassar | 9 |
| ID | Sulawesi Utara | Asia/Jakarta | Asia/Makassar | 9 |
| PG | Morobe | Pacific/Bougainville | Pacific/Port_Moresby | 9 |
| ID | Maluku | Asia/Jakarta | Asia/Jayapura | 8 |
| ID | Papua | Asia/Jakarta | Asia/Jayapura | 8 |
| RU | Astrakhan | Europe/Moscow | Europe/Astrakhan | 8 |
| RU | Udmurt | Europe/Moscow | Europe/Samara | 8 |
| FM | Pohnpei | Pacific/Chuuk | Pacific/Pohnpei | 7 |
| ID | Maluku Utara | Asia/Jakarta | Asia/Jayapura | 7 |
| ID | Papua Pegunungan | Asia/Jakarta | Asia/Jayapura | 7 |
| PG | Eastern Highlands | Pacific/Bougainville | Pacific/Port_Moresby | 7 |
| CA | Alberta | America/Toronto | America/Edmonton | 6 |
| ID | Kalimantan Timur | Asia/Jakarta | Asia/Makassar | 6 |
| ID | Papua Tengah | Asia/Jakarta | Asia/Jayapura | 6 |
| ID | Sulawesi Barat | Asia/Jakarta | Asia/Makassar | 6 |
| MX | Baja California | America/Mexico_City | America/Tijuana | 6 |
| PF | Leeward Islands | Pacific/Gambier | Pacific/Tahiti | 6 |
| PG | Chimbu | Pacific/Bougainville | Pacific/Port_Moresby | 6 |
| ID | Gorontalo | Asia/Jakarta | Asia/Makassar | 5 |
| ID | Papua Barat Daya | Asia/Jakarta | Asia/Jayapura | 5 |
| PF | Austral Islands | Pacific/Gambier | Pacific/Tahiti | 5 |
| PG | Enga | Pacific/Bougainville | Pacific/Port_Moresby | 5 |
| PG | Madang | Pacific/Bougainville | Pacific/Port_Moresby | 5 |
| RU | Chukotka | Europe/Moscow | Asia/Anadyr | 5 |
| RU | Yamalo-Nenets | Europe/Moscow | Asia/Yekaterinburg | 5 |
| CA | Saskatchewan | America/Toronto | America/Regina | 4 |
| ID | Kalimantan Utara | Asia/Jakarta | Asia/Makassar | 4 |
| ID | Nusa Tenggara Barat | Asia/Jakarta | Asia/Makassar | 4 |
| ID | Papua Barat | Asia/Jakarta | Asia/Jayapura | 4 |
| ID | Papua Selatan | Asia/Jakarta | Asia/Jayapura | 4 |
| MX | Baja California Sur | America/Mexico_City | America/Mazatlan | 4 |
| MX | Quintana Roo | America/Mexico_City | America/Cancun | 4 |
| PG | Central | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| PG | Milne Bay | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| PG | Sandaun | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| PG | Western Highlands | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| RU | Kaliningrad | Europe/Moscow | Europe/Kaliningrad | 4 |
| RU | Khanty-Mansi | Europe/Moscow | Asia/Yekaterinburg | 4 |
| BR | Amazonas | America/Sao_Paulo | America/Eirunepe | 3 |
| CA | Manitoba | America/Toronto | America/Winnipeg | 3 |
| MX | Nayarit, Bahía de Banderas (3 filed under Jalisco) | America/Mazatlan | America/Bahia_Banderas | 6 |
| MN | Zavkhan, Govi-Altai | Asia/Hovd | Asia/Ulaanbaatar | 2 |
| BR | Amazonas (Lábrea) | America/Sao_Paulo | America/Manaus | 1 |
| GL | Avannaata (Qaanaaq) | America/Danmarkshavn | America/Nuuk | 1 |
| PG | Hela | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| PG | Jiwaka | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| PG | Southern Highlands | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| PG | Western | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| ID | Bali | Asia/Jakarta | Asia/Makassar | 2 |
| MN | Khovd | Asia/Choibalsan | Asia/Hovd | 2 |
| PG | East New Britain | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | Gulf | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | New Ireland | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | Oro | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | West New Britain | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| BR | Roraima | America/Sao_Paulo | America/Boa_Vista | 1 |
| CA | British Columbia | America/Toronto | America/Dawson_Creek | 1 |
| CA | British Columbia | America/Toronto | America/Edmonton | 1 |
| CD | Lualaba | Africa/Kinshasa | Africa/Lubumbashi | 1 |
| FM | Kosrae | Pacific/Chuuk | Pacific/Kosrae | 1 |
| PF | Marquesas Islands | Pacific/Gambier | Pacific/Marquesas | 1 |
| PG | Manus | Pacific/Bougainville | Pacific/Port_Moresby | 1 |
| PG | Port Moresby | Pacific/Bougainville | Pacific/Port_Moresby | 1 |

### Not changed
- **Uncertain:** Sakha's cities in the Verkhoyansk, Oymyakon and Kolyma areas (three zones).
- **Amazonas** follows IANA's east/west geography: the Tabatinga–Porto Acre line of Decree 2,784/1913, as amended by
  Law 12,876/2013, with UTC−5 west of it. Itamarati and Lábrea lie east of the line and take `America/Manaus`.
  Tabatinga is the line's starting point; the decree's implementing regulation (Decree 10,546/1913, art. 2(III))
  puts both endpoint towns in the UTC−4 zone, so it keeps `America/Manaus` too. Practice is disputed: a 2019
  Ministry of Education (ENEM) notice groups 13 Amazonas municipalities, Tabatinga, Boca do Acre and Jutaí among
  them, with Acre's time, against IANA's explicit eastern list; the conflict is recorded, not resolved.
- **Multi-zone by design:** US states split between zones (Tennessee, Kentucky, Indiana, Florida, Texas, the Dakotas,
  Nebraska, Kansas, Idaho, Arizona's Navajo Nation) and Mexico's US-border strip (Coahuila, Nuevo León, Tamaulipas,
  Chihuahua).
- **Political:** Xinjiang (state `Asia/Urumqi`, cities `Asia/Shanghai`) and Crimea (state `Europe/Kiev`, cities
  `Europe/Simferopol`).
- **Same offset, different name** (Magadan on `Asia/Sakhalin`, Kirov, Volgograd, Cyprus's `Asia/Famagusta`,
  Uzbekistan's `Asia/Samarkand`, Palestine's Gaza/Hebron, Mongolia's `Asia/Choibalsan`) is not an error in time.

### Independent review
Round 1 was reviewed: all 30 states correct (the 27 Russian mappings checked against Russian law and tzdata) and 360
of 1,069 cities checked by OpenStreetMap, all correct. Round 2 (from that review's findings) was reviewed in full (all 459 new cities with OpenStreetMap): 455 correct;
the 2 wrong and 2 uncertain cities and two Mongolian aimags were corrected as described above. A second (Codex)
review found the three Bahía de Banderas records filed under Jalisco given Mexico City's zone (their municipality
has its own, `America/Bahia_Banderas`) and Lábrea left on São Paulo time; both are fixed, with three more Bahía de
Banderas records, Qaanaaq and the two Mongolian aimags' cities.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/states/states.json` — `timezone` on 95 states
- `contributions/cities/*.json` (13 countries) — `timezone` on 1,535 cities

## Chinese records at (0, 0)

### Problem
22 records of the later CN county batch (ids 157xxx–159xxx) had coordinates (0, 0). 17 are real places with a
Wikidata item; 5 are not places: three named "Directly" (the heading for county-level units administered directly
by a province, mistranslated) and two generic aggregates, Dongbu ("eastern part", Zhongshan) and Chengqu ("urban
area", Danzhou; its Wikidata link is a disambiguation page).

### Fix
- 17 records take their Wikidata item's point, and 16 its `wikiDataId` (Shennongjia's is held back, below); native names are corrected (the batch's
  back-transliterations used wrong characters) and `translations` follow (Latin-script languages the new name,
  `zh-CN` the native, other scripts the item's Wikidata label, or the new English name where there is none) and seven English names take the established short romanization:
  Lungchuan → Longchuan, Daicheng → Dacheng, Durbote → Dorbod, Qianguorluosi → Qian Gorlos, Chengduo → Chindu,
  Simong → Mainling, Shennongjia Forestry → Shennongjia (now `administrative zone`).
- Removed: 157533 Dongbu, 157656 Chengqu, 157658 / 158123 / 158224 Directly. Their 20 children (Hainan's
  directly administered cities and counties, Jiyuan, Xiantao, Qianjiang, Tianmen, Shennongjia) keep their state
  and level; `parent_id` is cleared.

### Verification
- Each point is the P625 of the record's Wikidata item (a representative point). Jiagedaqi and Songling lie in
  Inner Mongolia's territory but are administered by Heilongjiang, where CSC files them; that stays.
- No city or postcode refers to a removed id.

### Held back

- 158228: `wikiDataId` left empty, since Q1359055 is already record 20089's (a duplicate candidate for the #1643 duplicates check).

### Removed records (archive)

<details>
<summary>Full rows as removed (replacement id: none)</summary>

```json
[
  {
    "id": 157533,
    "name": "Dongbu",
    "state_id": 2279,
    "state_code": "GD",
    "country_id": 45,
    "country_code": "CN",
    "type": "area",
    "level": 2,
    "parent_id": 20451,
    "latitude": "0E-8",
    "longitude": "0E-8",
    "native": "东部",
    "population": null,
    "timezone": "Asia/Shanghai",
    "translations": {
      "br": "Dongbu",
      "ko": "동부",
      "pt-BR": "Dongbu",
      "pt": "Dongbu",
      "nl": "Dongbu",
      "hr": "Dongbu",
      "fa": "دونگبو",
      "de": "Dongbu",
      "es": "Dongbu",
      "fr": "Dongbu",
      "ja": "東部",
      "it": "Dongbu",
      "zh-CN": "东部",
      "tr": "Dongbu",
      "ru": "Дунбу",
      "uk": "Дунбу",
      "pl": "Dongbu",
      "hi": "डोंगबू",
      "ar": "دونغبو"
    },
    "created_at": "2014-01-01T17:31:01",
    "updated_at": "2025-11-21T20:15:06",
    "flag": 1,
    "wikiDataId": null,
    "replacement_id": null
  },
  {
    "id": 157656,
    "name": "Chengqu",
    "state_id": 2273,
    "state_code": "HI",
    "country_id": 45,
    "country_code": "CN",
    "type": "area",
    "level": 2,
    "parent_id": 157655,
    "latitude": "0E-8",
    "longitude": "0E-8",
    "native": "城区",
    "population": 450959,
    "timezone": "Asia/Shanghai",
    "translations": {
      "br": "Chengqu",
      "ko": "청취",
      "pt-BR": "Chengqu",
      "pt": "Chengqu",
      "nl": "Chengqu",
      "hr": "Chengqu",
      "fa": "چنگکو",
      "de": "Chengqu",
      "es": "Chengqu",
      "fr": "Chengqu",
      "ja": "成区",
      "it": "Chengqu",
      "zh-CN": "城区",
      "tr": "Chengqu",
      "ru": "Чэнцюй",
      "uk": "Chengqu",
      "pl": "Chengqu",
      "hi": "चेंगकू",
      "ar": "تشينجكو"
    },
    "created_at": "2014-01-01T17:31:01",
    "updated_at": "2025-11-26T18:54:28",
    "flag": 1,
    "wikiDataId": "Q424839",
    "replacement_id": null
  },
  {
    "id": 157658,
    "name": "Directly",
    "state_id": 2273,
    "state_code": "HI",
    "country_id": 45,
    "country_code": "CN",
    "type": "prefecture",
    "level": 1,
    "parent_id": null,
    "latitude": "0E-8",
    "longitude": "0E-8",
    "native": "直接地",
    "population": null,
    "timezone": "Asia/Shanghai",
    "translations": {
      "br": "War-eeun",
      "ko": "곧장",
      "pt-BR": "Diretamente",
      "pt": "Diretamente",
      "nl": "Direct",
      "hr": "Direktno",
      "fa": "مستقیماً",
      "de": "Direkt",
      "es": "Directamente",
      "fr": "Directement",
      "ja": "直接",
      "it": "Direttamente",
      "zh-CN": "直接地",
      "tr": "Doğrudan",
      "ru": "Напрямую",
      "uk": "Безпосередньо",
      "pl": "Bezpośrednio",
      "hi": "सीधे",
      "ar": "مباشرة"
    },
    "created_at": "2014-01-01T17:31:01",
    "updated_at": "2025-11-21T20:15:23",
    "flag": 1,
    "wikiDataId": null,
    "replacement_id": null
  },
  {
    "id": 158123,
    "name": "Directly",
    "state_id": 2259,
    "state_code": "HA",
    "country_id": 45,
    "country_code": "CN",
    "type": "prefecture",
    "level": 1,
    "parent_id": null,
    "latitude": "0E-8",
    "longitude": "0E-8",
    "native": "直接地",
    "population": null,
    "timezone": "Asia/Shanghai",
    "translations": {
      "br": "War-eeun",
      "ko": "곧장",
      "pt-BR": "Diretamente",
      "pt": "Diretamente",
      "nl": "Direct",
      "hr": "Direktno",
      "fa": "مستقیماً",
      "de": "Direkt",
      "es": "Directamente",
      "fr": "Directement",
      "ja": "直接",
      "it": "Direttamente",
      "zh-CN": "直接地",
      "tr": "Doğrudan",
      "ru": "Напрямую",
      "uk": "Безпосередньо",
      "pl": "Bezpośrednio",
      "hi": "सीधे",
      "ar": "مباشرة"
    },
    "created_at": "2014-01-01T17:31:01",
    "updated_at": "2025-11-21T20:18:33",
    "flag": 1,
    "wikiDataId": null,
    "replacement_id": null
  },
  {
    "id": 158224,
    "name": "Directly",
    "state_id": 2274,
    "state_code": "HB",
    "country_id": 45,
    "country_code": "CN",
    "type": "prefecture",
    "level": 1,
    "parent_id": null,
    "latitude": "0E-8",
    "longitude": "0E-8",
    "native": "直接地",
    "population": null,
    "timezone": "Asia/Shanghai",
    "translations": {
      "br": "War-eeun",
      "ko": "곧장",
      "pt-BR": "Diretamente",
      "pt": "Diretamente",
      "nl": "Direct",
      "hr": "Direktno",
      "fa": "مستقیماً",
      "de": "Direkt",
      "es": "Directamente",
      "fr": "Directement",
      "ja": "直接",
      "it": "Direttamente",
      "zh-CN": "直接地",
      "tr": "Doğrudan",
      "ru": "Напрямую",
      "uk": "Безпосередньо",
      "pl": "Bezpośrednio",
      "hi": "सीधे",
      "ar": "مباشرة"
    },
    "created_at": "2014-01-01T17:31:01",
    "updated_at": "2025-11-21T20:18:56",
    "flag": 1,
    "wikiDataId": null,
    "replacement_id": null
  }
]
```

</details>

### Rollback
Revert the PR (squash commit); the removed rows come back with their ids, which are not reused meanwhile (new
records get ids above the current maximum).

### Files Changed
- `contributions/cities/CN.json` — 17 records repaired, 20 `parent_id`s cleared, 5 records removed

## Mexican city types: municipality vs. seat town

### Problem
`MX.json` mixed municipality records (the territory) and seat towns under the same types (see #1634/#1650).

### Fix
Convention (also in TYPE_FIELD.md, whose settlement filters now leave out MX `municipality`): `adm1` = state-capital
town, `adm2` = municipal-seat town (GeoNames PPLA2), `municipality` = the municipal territory (GeoNames ADM2),
`city` = any other locality. `type` changes on 443 records: 351 become `municipality` (245 from `city`, 105 from
`adm2`, 1 from `section`), being on their municipality's GeoNames ADM2 point, nearer to it than to any same-named
town, with a population that is not a town's of that municipality; 92 seat towns become `adm2` (91 from `city`,
1 from `municipality`).

Left alone: records whose population is exactly a town's (the 2019 import copied GeoNames populations, so this
identifies the source entry, wherever the town lies in the municipality): 88 seat towns (56 already `adm2`, 32
made `adm2`) and 26 plain towns; and 8 whose own
Wikidata item is the seat town while P1376 names a separate municipality. Also unchanged: 141 `adm2` records whose
source entry is a plain town (PPL); 12 are confirmed seats, 129 need an INEGI seat check.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/MX.json` — `type` on 443 records
- `TYPE_FIELD.md` — the Mexican convention and the filter snippets

## Duplicate city records merged

### Problem
Some places were recorded twice, usually by a later batch re-adding a place the 2019 import already had.

### Fix
A pair is merged only when both records are the same place at the same scope: the same Wikidata item, matching
GeoNames entries (El Guayabo's two are alias entries for one locality; Davao's and Jose Abad Santos's items link a
settlement and an administrative entry, and both records are the whole city or municipality), no conflicting known
populations (four pairs have one population missing), and not a municipality next to its own town. The older id is
kept; the later copy is removed; populations are not added, and the kept record keeps its own fields (Jardines de la
Silla, 71005, stays without a population although the removed copy had 53,742, kept in the archive below). Jose Abad Santos keeps 144184 with the removed copy's
Davao Occidental state and point.

| Removed id | Removed record | Country | Kept id |
|---|---|---|---|
| 149670 | Agualeguas Nuevo León | MX | 68123 |
| 149709 | El Carmen Nuevo León | MX | 68826 |
| 149677 | Apodaca | MX | 69144 |
| 149753 | Juárez Nuevo León | MX | 69146 |
| 149735 | General Escobedo | MX | 69156 |
| 149737 | General Terán Nuevo León | MX | 69157 |
| 149814 | Sabinas Hidalgo | MX | 69177 |
| 149702 | Doctor Coss Nuevo León | MX | 69694 |
| 149747 | Iturbide Nuevo León | MX | 70893 |
| 149748 | Jardines de la Silla | MX | 71005 |
| 149795 | Linares Nuevo León | MX | 71679 |
| 149810 | Parás Nuevo León | MX | 72664 |
| 70666 | Heriberto Valdez Romero (El Guayabo) | MX | 69978 |
| 143243 | Alcabideche | PT | 88915 |
| 147498 | Khailar | IN | 132453 |
| 144949 | Jose Abad Santos | PH | 144184 |
| 144930 | Davao City | PH | 82396 |
| 154831 | San Agustin | PH | 144485 |

Kept apart: town/municipality pairs (Farkadona 52599/154229, Kibungan, Tapaz, M'lang, Lumban, Huixquilucan,
Elche 34030/152170, Benito Juárez/Tecolotes) and homonyms (Gucheng 157835 Hebei / 158169 Hubei). The wider screens
(about 900 PH pairs from the 144xxx–146xxx batch, and CN, ES, PT, UA, JP candidates) stay until each pair is checked
the same way.

### Removed records (archive)

<details>
<summary>Full rows as removed (with the id that replaces each)</summary>

```json
[
  {
    "id": 149670,
    "name": "Agualeguas Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "26.31083333",
    "longitude": "-99.53916667",
    "native": "Agualeguas Nuevo León",
    "population": 1995,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Agualeguas Nuevo León",
      "ko": "아구알레구아스 누에보 레온",
      "pt-BR": "Agualeguas Nuevo León",
      "pt": "Agualeguas Nuevo León",
      "nl": "Agualeguas Nuevo León",
      "hr": "Agualeguas Nuevo León",
      "fa": "آگوالگواس نوئوو لئون",
      "de": "Agualeguas Nuevo León",
      "es": "Agualeguas Nuevo León",
      "fr": "Agualeguas Nuevo León",
      "ja": "アグアレグアス・ヌエボ・レオン",
      "it": "Agualeguas Nuevo León",
      "zh-CN": "新莱昂州阿瓜莱瓜斯",
      "tr": "Agualeguas Nuevo León",
      "ru": "Агуалегуас Нуэво-Леон",
      "uk": "Агуалегуас Нуево-Леон",
      "pl": "Agualeguas Nuevo León",
      "hi": "अगुआलेगुआस नुएवो लियोन",
      "ar": "أغواليغواس نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q3310805",
    "replacement_id": 68123
  },
  {
    "id": 149709,
    "name": "El Carmen Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "25.93222778",
    "longitude": "-100.36412222",
    "native": "El Carmen Nuevo León",
    "population": 9568,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "El Carmen Nuevo León",
      "ko": "엘 카르멘 누에보 레온",
      "pt-BR": "El Carmen Nuevo León",
      "pt": "El Carmen Nuevo León",
      "nl": "El Carmen Nuevo León",
      "hr": "El Carmen Novi León",
      "fa": "ال کارمن نوئوو لئون",
      "de": "El Carmen Nuevo León",
      "es": "El Carmen Nuevo León",
      "fr": "El Carmen Nuevo León",
      "ja": "エル・カルメン・ヌエボ・レオン",
      "it": "El Carmen Nuevo León",
      "zh-CN": "新莱昂州埃尔卡门",
      "tr": "El Carmen Nuevo León",
      "ru": "Эль Кармен Нуэво Леон",
      "uk": "Ель Кармен Нуево-Леон",
      "pl": "El Carmen Nuevo León",
      "hi": "एल कारमेन नुएवो लियोन",
      "ar": "إل كارمن نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q3846844",
    "replacement_id": 68826
  },
  {
    "id": 149677,
    "name": "Apodaca",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "25.78166667",
    "longitude": "-100.18861111",
    "native": "Apodaca",
    "population": 467157,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Apodaca",
      "ko": "아포다카",
      "pt-BR": "Apodaca",
      "pt": "Apodaca",
      "nl": "Apodaca",
      "hr": "Apodaca",
      "fa": "آپوداکا",
      "de": "Apodaca",
      "es": "Apodaca",
      "fr": "Apodaca",
      "ja": "アポダカ",
      "it": "Apodaca",
      "zh-CN": "阿波达卡",
      "tr": "Apodaca",
      "ru": "Аподака",
      "uk": "Аподака",
      "pl": "Apodaca",
      "hi": "अपोडाका",
      "ar": "أبوداكا"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q1782406",
    "replacement_id": 69144
  },
  {
    "id": 149753,
    "name": "Juárez Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "25.65000000",
    "longitude": "-100.08333333",
    "native": "Juárez Nuevo León",
    "population": null,
    "timezone": "America/Mexico_City",
    "translations": {
      "br": "Juárez Nuevo León",
      "ko": "후아레스 누에보 레온",
      "pt-BR": "Juárez Nuevo León",
      "pt": "Juárez Nuevo León",
      "nl": "Juárez Nuevo León",
      "hr": "Juárez Nuevo León",
      "fa": "خوارس نوئوو لئون",
      "de": "Juárez Nuevo León",
      "es": "Juárez Nuevo León",
      "fr": "Juárez Nuevo León",
      "ja": "フアレス・ヌエボ・レオン",
      "it": "Juárez Nuevo León",
      "zh-CN": "新莱昂州华雷斯",
      "tr": "Juárez Nuevo León",
      "ru": "Хуарес Нуэво-Леон",
      "uk": "Хуарес-Нуево-Леон",
      "pl": "Juárez Nuevo León",
      "hi": "जुआरेज़ नुएवो लियोन",
      "ar": "خواريز نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T17:11:50",
    "flag": 1,
    "wikiDataId": "Q1827219",
    "replacement_id": 69146
  },
  {
    "id": 149735,
    "name": "General Escobedo",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "25.80833333",
    "longitude": "-100.32666667",
    "native": "General Escobedo",
    "population": 0,
    "timezone": "America/Mexico_City",
    "translations": {
      "br": "Escobedo jeneral",
      "ko": "에스코베도 장군",
      "pt-BR": "General Escobedo",
      "pt": "General Escobedo",
      "nl": "Generaal Escobedo",
      "hr": "General Escobedo",
      "fa": "ژنرال اسکوبدو",
      "de": "General Escobedo",
      "es": "General Escobedo",
      "fr": "Général Escobedo",
      "ja": "エスコベド将軍",
      "it": "Generale Escobedo",
      "zh-CN": "埃斯科韦多将军",
      "tr": "General Escobedo",
      "ru": "Генерал Эскобедо",
      "uk": "Генерал Ескобедо",
      "pl": "Generał Escobedo",
      "hi": "जनरल एस्कोबेडो",
      "ar": "الجنرال إسكوبيدو"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T17:11:50",
    "flag": 1,
    "wikiDataId": "Q778941",
    "replacement_id": 69156
  },
  {
    "id": 149737,
    "name": "General Terán Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "25.26666667",
    "longitude": "-99.68333333",
    "native": "General Terán Nuevo León",
    "population": 6333,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Jeneral Terán Nuevo León",
      "ko": "테란 누에보 레온 장군",
      "pt-BR": "General Terán Nuevo León",
      "pt": "General Terán Nuevo León",
      "nl": "Generaal Terán Nuevo León",
      "hr": "General Terán Nuevo León",
      "fa": "ژنرال تران نوئوو لئون",
      "de": "General Terán Nuevo León",
      "es": "General Terán Nuevo León",
      "fr": "Général Terán Nuevo León",
      "ja": "テラン・ヌエボ・レオン将軍",
      "it": "Generale Terán Nuevo León",
      "zh-CN": "新莱昂州特兰将军",
      "tr": "General Terán Nuevo León",
      "ru": "Генерал Теран Нуэво-Леон",
      "uk": "Генерал Теран Нуево-Леон",
      "pl": "Generał Terán Nuevo León",
      "hi": "जनरल टेरान नुएवो लियोन",
      "ar": "الجنرال تيران نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q27769173",
    "replacement_id": 69157
  },
  {
    "id": 149814,
    "name": "Sabinas Hidalgo",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "26.49833333",
    "longitude": "-100.18111111",
    "native": "Sabinas Hidalgo",
    "population": 33068,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Sabinas Hidalgo",
      "ko": "사비나스 이달고",
      "pt-BR": "Sabinas Hidalgo",
      "pt": "Sabinas Hidalgo",
      "nl": "Sabinas Hidalgo",
      "hr": "Sabinas Hidalgo",
      "fa": "سابیناس هیدالگو",
      "de": "Sabinas Hidalgo",
      "es": "Sabinas Hidalgo",
      "fr": "Sabinas Hidalgo",
      "ja": "サビナス・イダルゴ",
      "it": "Sabinas Hidalgo",
      "zh-CN": "萨维纳斯·伊达尔戈",
      "tr": "Sabinas Hidalgo",
      "ru": "Сабинас Идальго",
      "uk": "Сабінас Ідальго",
      "pl": "Sabinas Hidalgo",
      "hi": "सबिनास हिडाल्गो",
      "ar": "سابيناس هيدالغو"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q2391830",
    "replacement_id": 69177
  },
  {
    "id": 149702,
    "name": "Doctor Coss Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "25.92589722",
    "longitude": "-99.18437222",
    "native": "Doctor Coss Nuevo León",
    "population": 790,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Mezeg Coss Nuevo León",
      "ko": "닥터 코스 누에보 레온",
      "pt-BR": "Doutor Coss Nuevo León",
      "pt": "Doutor Coss Nuevo León",
      "nl": "Dokter Coss Nuevo León",
      "hr": "Doktor Coss Novi León",
      "fa": "دکتر کاس نوئوو لئون",
      "de": "Doctor Coss Nuevo León",
      "es": "Doctor Coss Nuevo León",
      "fr": "Docteur Coss Nuevo León",
      "ja": "ドクター・コス・ヌエボ・レオン",
      "it": "Dottor Coss Nuevo León",
      "zh-CN": "新莱昂州科斯医生",
      "tr": "Doktor Coss Nuevo León",
      "ru": "Доктор Косс Нуэво-Леон",
      "uk": "Доктор Косс Нуево-Леон",
      "pl": "Doktor Coss Nuevo León",
      "hi": "डॉक्टर कॉस नुएवो लियोन",
      "ar": "الدكتور كوس نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q3311232",
    "replacement_id": 69694
  },
  {
    "id": 149747,
    "name": "Iturbide Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "24.72527778",
    "longitude": "-99.90000000",
    "native": "Iturbide Nuevo León",
    "population": null,
    "timezone": "America/Mexico_City",
    "translations": {
      "br": "Iturbide Nuevo León",
      "ko": "이투르비데 누에보 레온",
      "pt-BR": "Iturbide Nuevo León",
      "pt": "Iturbide Nuevo León",
      "nl": "Iturbide Nuevo León",
      "hr": "Iturbide Nuevo León",
      "fa": "ایتوربیده نوئوو لئون",
      "de": "Iturbide Nuevo León",
      "es": "Iturbide Nuevo León",
      "fr": "Iturbide Nuevo León",
      "ja": "イトゥルビデ・ヌエボ・レオン",
      "it": "Iturbide Nuevo León",
      "zh-CN": "新莱昂州伊图尔维德",
      "tr": "Iturbide Nuevo León",
      "ru": "Iturbide Nuevo León",
      "uk": "Ітурбіде Нуево-Леон",
      "pl": "Iturbide Nuevo León",
      "hi": "इतुर्बिडे नुएवो लियोन",
      "ar": "إيتوربيدي نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T17:11:50",
    "flag": 1,
    "wikiDataId": "Q116918876",
    "replacement_id": 70893
  },
  {
    "id": 149748,
    "name": "Jardines de la Silla",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "25.62926700",
    "longitude": "-100.18667790",
    "native": "Jardines de la Silla",
    "population": 53742,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Jardines de la Silla",
      "ko": "하르디네스 드 라 실라",
      "pt-BR": "Jardines de la Silla",
      "pt": "Jardines de la Silla",
      "nl": "Tuinen van de Silla",
      "hr": "Vrtovi Silla",
      "fa": "باغ‌های سیلا",
      "de": "Gärten von la Silla",
      "es": "Jardines de la Silla",
      "fr": "Jardins de la Silla",
      "ja": "シラ庭園",
      "it": "Giardini della Silla",
      "zh-CN": "西拉花园",
      "tr": "Silla Bahçeleri",
      "ru": "Хардинес-де-ла-Силья",
      "uk": "Сади Сілья",
      "pl": "Ogrody Silla",
      "hi": "जार्डिनेस डे ला सिला",
      "ar": "حدائق سيلا"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q20148675",
    "replacement_id": 71005
  },
  {
    "id": 149795,
    "name": "Linares Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "24.85965278",
    "longitude": "-99.56786944",
    "native": "Linares Nuevo León",
    "population": 70378,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Linares Nuevo León",
      "ko": "리나레스 누에보 레온",
      "pt-BR": "Linares Novo León",
      "pt": "Linares Novo León",
      "nl": "Linares Nuevo León",
      "hr": "Linares Novi León",
      "fa": "لینارس نوئوو لئون",
      "de": "Linares Nuevo León",
      "es": "Linares Nuevo León",
      "fr": "Linares Nuevo León",
      "ja": "リナレス・ヌエボ・レオン",
      "it": "Linares Nuevo León",
      "zh-CN": "新莱昂州利纳雷斯",
      "tr": "Linares Nuevo León",
      "ru": "Линарес Нуэво-Леон",
      "uk": "Лінарес, Нуево-Леон",
      "pl": "Linares Nuevo León",
      "hi": "लिनारेस नुएवो लियोन",
      "ar": "ليناريس نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q991413",
    "replacement_id": 71679
  },
  {
    "id": 149810,
    "name": "Parás Nuevo León",
    "state_id": 3452,
    "state_code": "NLE",
    "country_id": 142,
    "country_code": "MX",
    "type": "adm2",
    "level": null,
    "parent_id": null,
    "latitude": "26.49888889",
    "longitude": "-99.52250000",
    "native": "Parás Nuevo León",
    "population": 788,
    "timezone": "America/Monterrey",
    "translations": {
      "br": "Paras Nuevo León",
      "ko": "파라스 누에보 레온",
      "pt-BR": "Parás Nuevo León",
      "pt": "Parás Nuevo León",
      "nl": "Parás Nuevo León",
      "hr": "Paras Nuevo León",
      "fa": "پارس نوئوو لئون",
      "de": "Parás Nuevo León",
      "es": "Parás Nuevo León",
      "fr": "Parás Nuevo León",
      "ja": "ヌエボレオン州",
      "it": "Parás Nuevo León",
      "zh-CN": "新莱昂州帕拉斯",
      "tr": "Parás Nuevo León",
      "ru": "Парас Нуэво-Леон",
      "uk": "Парас Нуево-Леон",
      "pl": "Parás Nuevo León",
      "hi": "पारस नुएवो लियोन",
      "ar": "باراس نويفو ليون"
    },
    "created_at": "2022-05-09T09:15:28",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q61280919",
    "replacement_id": 72664
  },
  {
    "id": 70666,
    "name": "Heriberto Valdez Romero (El Guayabo)",
    "state_id": 3449,
    "state_code": "SIN",
    "country_id": 142,
    "country_code": "MX",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "25.94056000",
    "longitude": "-109.13722000",
    "native": "Heriberto Valdez Romero (El Guayabo)",
    "population": 2065,
    "timezone": "America/Mazatlan",
    "translations": {
      "br": "Heriberto Valdez Romero (El Guayabo)",
      "ko": "Heriberto Valdez Romero(엘 구아야보)",
      "pt-BR": "Heriberto Valdez Romero (El Guayabo)",
      "pt": "Heriberto Valdez Romero (El Guayabo)",
      "nl": "Heriberto Valdez Romero (El Guayabo)",
      "hr": "Heriberto Valdez Romero (El Guayabo)",
      "fa": "هریبرتو والدز رومرو (ال گوایابو)",
      "de": "Heriberto Valdez Romero (El Guayabo)",
      "es": "Heriberto Valdez Romero (El Guayabo)",
      "fr": "Heriberto Valdez Romero (El Guayabo)",
      "ja": "ヘリベルト・バルデス・ロメロ（エル・グアヤボ）",
      "it": "Heriberto Valdez Romero (El Guayabo)",
      "zh-CN": "埃里博托·瓦尔迪兹·罗梅罗 (El Guayabo)",
      "tr": "Heriberto Valdez Romero (El Guayabo)",
      "ru": "Эриберто Вальдес Ромеро (Эль Гуаябо)",
      "uk": "Еріберто Вальдес Ромеро (Ель Гуаябо)",
      "pl": "Heriberto Valdez Romero (El Guayabo)",
      "hi": "हेरिबर्टो वाल्डेज़ रोमेरो (एल गुआयाबो)",
      "ar": "هيريبرتو فالديز روميرو (إل جوايابو)"
    },
    "created_at": "2019-10-06T10:08:45",
    "updated_at": "2025-12-02T14:39:55",
    "flag": 1,
    "wikiDataId": "Q18784997",
    "replacement_id": 69978
  },
  {
    "id": 143243,
    "name": "Alcabideche",
    "state_id": 2228,
    "state_code": "11",
    "country_id": 177,
    "country_code": "PT",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "38.73361111",
    "longitude": "-9.40916667",
    "native": "Alcabideche",
    "population": 33315,
    "timezone": "Europe/Lisbon",
    "translations": {
      "br": "Alcabideche",
      "ko": "알카비데체",
      "pt-BR": "Alcabideche",
      "pt": "Alcabideche",
      "nl": "Alcabideche",
      "hr": "Alcabideche",
      "fa": "آلکابدچه",
      "de": "Alcabideche",
      "es": "Alcabideche",
      "fr": "Alcabideche",
      "ja": "アルカビデシェ",
      "it": "Alcabideche",
      "zh-CN": "阿尔卡比德什",
      "tr": "Alcabideche",
      "ru": "Алкабидеше",
      "uk": "Алькабідеше",
      "pl": "Alcabideche",
      "hi": "अल्काबिडेचे",
      "ar": "ألكابيديتشي"
    },
    "created_at": "2020-06-29T01:03:32",
    "updated_at": "2025-12-02T14:38:56",
    "flag": 1,
    "wikiDataId": "Q31877422",
    "replacement_id": 88915
  },
  {
    "id": 147498,
    "name": "Khailar",
    "state_id": 4022,
    "state_code": "UP",
    "country_id": 101,
    "country_code": "IN",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "25.35000000",
    "longitude": "78.53000000",
    "native": "खैलर",
    "population": 13334,
    "timezone": "Asia/Kolkata",
    "translations": {
      "br": "Khailar",
      "ko": "카일라르",
      "pt-BR": "Khailar",
      "pt": "Khailar",
      "nl": "Khailar",
      "hr": "Khailar",
      "fa": "خیلار",
      "de": "Khailar",
      "es": "Khailar",
      "fr": "Khailar",
      "ja": "カイル",
      "it": "Khailar",
      "zh-CN": "海拉尔",
      "tr": "Haylar",
      "ru": "Хайлар",
      "uk": "Хайлар",
      "pl": "Khailar",
      "hi": "खैलर",
      "ar": "خيلار"
    },
    "created_at": "2021-06-06T22:48:16",
    "updated_at": "2025-12-02T14:38:56",
    "flag": 1,
    "wikiDataId": "Q2119908",
    "replacement_id": 132453
  },
  {
    "id": 144949,
    "name": "Jose Abad Santos",
    "state_id": 1309,
    "state_code": "DVO",
    "country_id": 174,
    "country_code": "PH",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "5.91246550",
    "longitude": "125.64459320",
    "native": "Jose Abad Santos",
    "population": 72552,
    "timezone": "Asia/Manila",
    "translations": {
      "br": "Jose Abad Santos",
      "ko": "호세 아바드 산토스",
      "pt-BR": "José Abad Santos",
      "pt": "José Abad Santos",
      "nl": "José Abad Santos",
      "hr": "José Abad Santos",
      "fa": "خوزه آباد سانتوس",
      "de": "José Abad Santos",
      "es": "José Abad Santos",
      "fr": "José Abad Santos",
      "ja": "ホセ・アバド・サントス",
      "it": "José Abad Santos",
      "zh-CN": "何塞·阿巴德·桑托斯",
      "tr": "Jose Abad Santos",
      "ru": "Хосе Абад Сантос",
      "uk": "Хосе Абад Сантос",
      "pl": "Jose Abad Santos",
      "hi": "जोस अबाद सैंटोस",
      "ar": "خوسيه آباد سانتوس"
    },
    "created_at": "2020-10-25T04:53:39",
    "updated_at": "2025-12-02T16:59:27",
    "flag": 1,
    "wikiDataId": "Q314824",
    "replacement_id": 144184
  },
  {
    "id": 144930,
    "name": "Davao City",
    "state_id": 1318,
    "state_code": "DAS",
    "country_id": 174,
    "country_code": "PH",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "7.06623333",
    "longitude": "125.60944167",
    "native": "Davao City",
    "population": 1848947,
    "timezone": "Asia/Manila",
    "translations": {
      "br": "Kêr Davao",
      "ko": "다바오 시",
      "pt-BR": "Cidade de Davao",
      "pt": "Cidade de Davao",
      "nl": "Davao City",
      "hr": "Grad Davao",
      "fa": "شهر داوائو",
      "de": "Davao City",
      "es": "Ciudad de Davao",
      "fr": "Ville de Davao",
      "ja": "ダバオ市",
      "it": "Città di Davao",
      "zh-CN": "达沃市",
      "tr": "Davao Şehri",
      "ru": "Город Давао",
      "uk": "Місто Давао",
      "pl": "Miasto Davao",
      "hi": "दावाओ शहर",
      "ar": "مدينة دافاو"
    },
    "created_at": "2025-03-22T01:06:36",
    "updated_at": "2025-12-02T17:11:50",
    "flag": 1,
    "wikiDataId": "Q1473",
    "replacement_id": 82396
  },
  {
    "id": 154831,
    "name": "San Agustin",
    "state_id": 1296,
    "state_code": "SUR",
    "country_id": 174,
    "country_code": "PH",
    "type": "city",
    "level": null,
    "parent_id": null,
    "latitude": "8.74366389",
    "longitude": "126.22143333",
    "native": "San Agustin",
    "population": 23698,
    "timezone": "Asia/Manila",
    "translations": {
      "br": "San Agustin",
      "ko": "산 아구스틴",
      "pt-BR": "Santo Agostinho",
      "pt": "Santo Agostinho",
      "nl": "San Agustin",
      "hr": "San Agustin",
      "fa": "سن آگوستین",
      "de": "San Agustin",
      "es": "San Agustín",
      "fr": "San Agustín",
      "ja": "サン・アグスティン",
      "it": "Sant'Agostino",
      "zh-CN": "圣奥古斯丁",
      "tr": "San Agustin",
      "ru": "Сан-Агустин",
      "uk": "Сан-Агустін",
      "pl": "San Agustin",
      "hi": "सैन अगस्टिन",
      "ar": "سان أوغستين"
    },
    "created_at": "2025-03-27T03:17:48",
    "updated_at": "2025-12-02T17:11:50",
    "flag": 1,
    "wikiDataId": "Q155618",
    "replacement_id": 144485
  }
]
```

</details>

### Rollback
Revert the PR (squash commit); the removed rows come back with their ids, which are not reused meanwhile.

### Files Changed
- `contributions/cities/{IN,MX,PH,PT}.json` — 18 records removed; state and point on 1 kept record

## Ethiopia's 2023 regions

### Problem
SNNPR was dissolved in August 2023 (Central Ethiopia and South Ethiopia; Sidama and South West Ethiopia had left in
2020 and 2021). CSC still filed 21 records under SNNPR, and Dīla, Gedeo Zone's seat, under Sidama with a point
0.7 km off inside Sidama.

### Fix
- New states 5827 Central Ethiopia (Q122415622) and 5828 South Ethiopia (Q122148951): `type` region, level 1,
  `Africa/Addis_Ababa`; ISO 3166-2 has no codes yet, so `iso3166_2` is null and `iso2` is GeoNames' local code
  (55, 56), as for the French Southern Territories' districts.
- 22 records move by their zone (Wikidata item, regional government zone lists): 8 to Central Ethiopia (Halaba,
  Gurage, East Gurage, Hadiya, Kembata and Tembaro, Yem) and 14 to South Ethiopia (Gamo, Gofa, Wolaita, Gedeo,
  South Omo, Ari, Konso, Gardula/Dirashe). Sources: Central Ethiopia's (https://cerspo.gov.et/home) and South
  Ethiopia's (https://www.southethiopiarspo.gov.et/overview/) zone lists; Wikidata Q122415622 and Q122148951;
  GeoNames' Ethiopian divisions (https://www.geonames.org/ET/administrative-division-ethiopia.html), which give the
  local codes 55 and 56 and no ISO code.
- Dīla (38625) takes Q905423's point (6.41250, 38.31167).
- SNNPR (state 1) is removed; no city, state or postcode refers to it afterwards.

### Left for follow-up
Wrong `wikiDataId`s on Bako, Felege Neway, Kolito, Lobuni, Sodo, Yem and Dīla (copy-forward, #1641); Konso's exact
town identity; Q3110186 conflates Bako and Jinka.

### Removed records (archive)

<details>
<summary>Full rows as removed (replacement id: none)</summary>

```json
[
  {
    "id": 1,
    "name": "Southern Nations, Nationalities, and Peoples",
    "country_id": 70,
    "country_code": "ET",
    "fips_code": "54",
    "iso2": "SN",
    "iso3166_2": "ET-SN",
    "type": "region",
    "level": 1,
    "parent_id": null,
    "native": "ደቡብ ብሔር ብሔረሰቦችና ሕዝቦች",
    "latitude": "6.51569110",
    "longitude": "36.95410700",
    "timezone": "Africa/Addis_Ababa",
    "translations": {
      "br": "Broadoù, broadelezhioù ha pobloù ar Su",
      "ko": "남부 국가, 민족 및 민족",
      "pt-BR": "Nações, Nacionalidades e Povos do Sul",
      "pt": "Nações, Nacionalidades e Povos do Sul",
      "nl": "Zuidelijke naties, nationaliteiten en volkeren",
      "hr": "Južne nacije, narodnosti i ljudi",
      "fa": "ملت‌ها، ملیت‌ها و مردمان جنوبی",
      "de": "Südliche Nationen, Nationalitäten und Völker",
      "es": "Naciones, nacionalidades y pueblos del Sur",
      "fr": "Nations, nationalités et peuples du Sud",
      "ja": "南方の諸国、民族、そして人々",
      "it": "Nazioni, nazionalità e popoli del Sud",
      "zh-CN": "南方国家、民族和人民",
      "tr": "Güney Milletleri, Milliyetleri ve Halkları",
      "ru": "Южные нации, национальности и народы",
      "uk": "Південні нації, національності та народи",
      "pl": "Narody, narodowości i ludy Południa",
      "hi": "दक्षिणी राष्ट्र, राष्ट्रीयताएँ और लोग",
      "ar": "الأمم والقوميات والشعوب الجنوبية"
    },
    "created_at": "2019-10-06T08:48:35",
    "updated_at": "2025-10-11T06:25:10",
    "flag": 1,
    "wikiDataId": "Q203193",
    "population": null,
    "replacement_id": null
  }
]
```

</details>

### Rollback
Revert the PR (squash commit); state 1 comes back with its id.

### Files Changed
- `contributions/states/states.json` — 2 states added, 1 removed
- `contributions/cities/ET.json` — state on 22 records, point on 1

## Chinese disambiguation IDs, Shennongjia, and four small fixes

### Problem
932 records of the later CN county batch (ids 157329–160015) carry a `wikiDataId` that is a disambiguation page.
Shennongjia was recorded twice (20089, 158228). Saint-Julien (Marseille) was filed under Var; La Zubia (Granada)
had La Granada's point (Barcelona); Solaro (Milan) sat in a Pavia hamlet and carried its item; Lingao and
Changjiang had wrong native characters.

### Fix
- `wikiDataId` on 174 CN records: the 5 former "Directly" children and 169 records whose single same-province
  candidate passes every check (record, Wikidata and GeoNames points within 5 km; exact Chinese administrative name
  on GeoNames; live P442; current P131 = the record's parent). 758 are held for a later pass. Baisha and Lingshui
  are 10.6 and 11.9 km from their item's representative point, but the items are the right autonomous counties
  (P442 469025, 469028), and GeoNames' county entries agree.
- Sources: each record's new item on Wikidata (e.g. https://www.wikidata.org/wiki/Q1001424) and its GeoNames
  administrative entry; Hubei's land-resources table for Shennongjia
  (https://zrzyt.hubei.gov.cn/bmdt/ztzl/cljsydzsdt/shennongjia/202103/t20210329_3428194.shtml); Marseille's 12th
  arrondissement (https://mairie11-12.marseille.fr/le-12e-arrondissement/saint-julien); AEMET for La Zubia
  (https://www.aemet.es/es/eltiempo/prediccion/municipios/zubia-la-id18193); Q42275 for Solaro.
- 158228 Shennongjia removed in favour of 20089 (same forest district; 20089 is GeoNames 1795614's ADM2 entry);
  20089 becomes `administrative zone`, level 2.
- 157668 Lingao 临高, 157670 Changjiang 昌江 (native and `zh-CN`).
- 46134 Saint-Julien: state Var (83) → Bouches-du-Rhône (13).
- 151401 La Zubia: point (37.12088, −3.58508), its own item's, as AEMET gives it.
- 60904 Solaro: item Q42275 (ISTAT 015213) and its point (45.61500, 9.08389).

### Removed records (archive)

<details>
<summary>Full rows as removed (with the id that replaces each)</summary>

```json
[
  {
    "id": 158228,
    "name": "Shennongjia",
    "state_id": 2274,
    "state_code": "HB",
    "country_id": 45,
    "country_code": "CN",
    "type": "administrative zone",
    "level": 2,
    "parent_id": null,
    "latitude": "31.74572000",
    "longitude": "110.67456000",
    "native": "神农架",
    "population": null,
    "timezone": "Asia/Shanghai",
    "translations": {
      "br": "Shennongjia",
      "ko": "선눙자 임구",
      "pt-BR": "Shennongjia",
      "pt": "Shennongjia",
      "nl": "Shennongjia",
      "hr": "Shennongjia",
      "fa": "شننگجیا",
      "de": "Shennongjia",
      "es": "Shennongjia",
      "fr": "Shennongjia",
      "ja": "神農架林区",
      "it": "Shennongjia",
      "zh-CN": "神农架",
      "tr": "Shennongjia",
      "ru": "Шэньнунцзя",
      "uk": "Shennongjia",
      "pl": "Shennongjia",
      "hi": "Shennongjia",
      "ar": "Shennongjia"
    },
    "created_at": "2014-01-01T17:31:01",
    "updated_at": "2025-11-21T20:18:56",
    "flag": 1,
    "wikiDataId": null,
    "replacement_id": 20089
  }
]
```

</details>

### Rollback
Revert the PR (squash commit); 158228 comes back with its id.

### Files Changed
- `contributions/cities/{CN,FR,ES,IT}.json` — 180 records changed, 1 removed

## Postcodes outside their country

### Problem
The coordinate validator still flagged 21 postcodes: 3 Australian codes at (0, 0), 6 Somali codes inside Kenya,
and 12 Danish codes whose centre is at sea.

### Fix
- AU 6947 Wangara (44896) and 6965 Bibra Lake (44910): Australia Post's points for these PO-box codes
  (https://auspost.com.au/postcode/wangara, https://auspost.com.au/postcode/bibra-lake).
- AU 6958 (44904), the Navy warships routing code: point cleared (no place; Defence routes it via Rockingham,
  https://www.defence.gov.au/sites/default/files/2020-08/NWCC-MailAdvice.pdf); the code stays.
- SO 31001 Luuq (833300) and 33001/33002 Doolow (833302/833303): their towns' points (Q1878274, Q1017164; GeoNames
  54715, 60632; OSM agrees on Gedo). These are the towns' points, not verified postal-area centroids.
- Held: Kaarani 12001/12002 and Kenia 32001 (no same-named place in Gedo confirmed).
- Not changed: Denmark's 12 sea centres come from the official postal areas, which include coastal water.

### Rollback
Revert the PR (squash commit).

### Files Changed
- `contributions/postcodes/{AU,SO}.json` — points on 6 records

## Cities filed under the wrong state (third pass)

### Problem
Rerunning the neighbour test and the GeoNames fingerprint on current data (outside PH, LK, SL) found 282
candidates, among them a systematic batch: Taiwan (state 2255) held 49 mainland Jiangsu places from the 2019 import.

### Fix
`state_id` and `state_code` on 141 records in 14 countries, each with two independent agreeing sources or an official
one: CN 50 (47 Jiangsu records out of Taiwan), FR 41, GB 15, MX 11, RU 6, RS 5, DZ 3, IN 3, ES 2 and IR, NO, SA, SN,
TH 1 each. Held: places spanning two provinces (Ponte a Elsa, Campoleone), records whose point is wrong rather than
their state, conflicting official codes, enclaves. Follow-up: East Attica (GR) holds 91 records, mostly Eastern
Macedonia and Thrace places.

### Rollback
Revert the PR (squash commit). No `id`s change.

### Files Changed
- `contributions/cities/*.json` (14 countries) — `state_id` and `state_code` on 141 records
