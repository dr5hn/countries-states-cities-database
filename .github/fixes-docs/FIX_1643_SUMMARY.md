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
