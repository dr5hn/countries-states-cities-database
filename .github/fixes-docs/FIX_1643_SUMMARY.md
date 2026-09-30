# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

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
  for the Ourense municipality (a coverage gap).
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
| 10 other pairs (Huesca → Teruel, León → Ávila (5), León → Segovia, León → Zamora, Zamora → Teruel, León → Valladolid, Ourense → Lugo, León → Palencia, Alicante → Santa Cruz de Tenerife, León → Burgos) | 19 |

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
- **Wrong `wikiDataId`.** 24 of the 88 records carry a Wikidata ID of a place in another province, e.g. *Adzaneta*
  → Q576753 (Aduna, Gipuzkoa), *Villajoyosa* → Q1918587. This is the copy-forward problem of #1641.
- **Province Wikidata IDs.** The eight wrong province IDs above, and similar ones in other countries, are left for a
  separate fix of `states.json`.

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/ES.json` — `state_id` and `state_code` on 90 records
