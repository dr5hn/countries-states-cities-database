# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Spanish cities filed under the wrong province

### How they were found
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames place with
the same name (or an alternate name) within 3 km and **exactly the record's population**. GeoNames' Spanish
second-level codes are the same letters as CSC's province `iso2`. For 57 ES records that entry lies in another
province; 7 of them (León records) are already moved by #1647. The other 50 were checked on Wikidata.

CSC's own Spanish province records point at the wrong Wikidata items in several places, so a "located in" (P131)
check against them does not work: Valencia → Q5720 (Valencian Community), Huesca → Q4040 (Aragon), Las Palmas →
Q5813 (Canary Islands), Alicante → Q11959 (the city), Santa Cruz de Tenerife → Q14328 (the city), Zaragoza →
Q10305 (the city). The check therefore uses the **INE municipality code** (P772) of the same-named Wikidata item
within 2 km of the record's point, or of the municipality that item is located in. Its first two digits are the
province.

| Result | Records |
|---|---:|
| INE province = the GeoNames province, not the filed one | **47** |
| No INE code on the item or its municipality: held (Arenys de Lledó, El Grao, Vallehermosa) | 3 |

Four of the 47 have a place with the same name in the old province: Corrales and La Cuesta (León), Lobios (Ourense),
San Isidro (Alicante). In each case the record's point is 75–1,840 km from that namesake, and its population is
exactly that of the place in the new province, so the record is the other place. *San Isidro* (19,541 people) is
the town in Granadilla de Abona, Tenerife, and already has `Atlantic/Canary`. After the move CSC has no record for
the Ourense municipality of Lobios; that is a coverage gap, not part of this fix.

### Fix
**47 cities** move to their province. Only `state_id` and `state_code` change; every record's `timezone` already
fits its new province (`Europe/Madrid`, or `Atlantic/Canary` for Santa Cruz de Tenerife).

| Move | Records |
|---|---:|
| Valencia → Castellón | 13 |
| Valencia → Alicante | 11 |
| Las Palmas → Santa Cruz de Tenerife | 8 |
| Huesca → Zaragoza (Zaragoza city districts, Mequinenza, La Puebla de Alfindén) | 6 |
| León → Segovia, Ávila, Zamora, Palencia, Burgos | 6 |
| Huesca → Teruel, Ourense → Lugo, Alicante → Santa Cruz de Tenerife | 3 |

| id | City | Was filed under | Now | Population | Wikidata | INE code |
|---|---|---|---|---:|---|---|
| 31943 | Adzaneta | Valencia (V) | Castellón (CS) | 1,462 | Q1635908, Q24003989 | 12001 |
| 32101 | Alcocéber | Valencia (V) | Castellón (CS) | 5,000 | Q2832200 | 12004 |
| 32309 | Almozara | Huesca (HU) | Zaragoza (Z) | 25,767 | Q9018307 | 50297 |
| 32456 | Ares del Maestre | Valencia (V) | Castellón (CS) | 227 | Q24011911, Q785949 | 12014 |
| 32669 | Barraco | León (LE) | Ávila (AV) | 2,111 | Q1618246, Q24003173 | 05022 |
| 32778 | Benassal | Valencia (V) | Castellón (CS) | 1,329 | Q1635350, Q24011904 | 12026 |
| 32822 | Benitachell | Valencia (V) | Alicante (A) | 3,630 | Q817349 | 03042 |
| 33803 | Corrales | León (LE) | Zamora (ZA) | 1,029 | Q1990609, Q24016720 | 49054 |
| 33875 | Cuevas de Vinromá | Valencia (V) | Castellón (CS) | 1,822 | Q1646761, Q24011892 | 12050 |
| 33924 | Delicias | Huesca (HU) | Zaragoza (Z) | 110,520 | Q131379287, Q8560730 | 50297 |
| 34634 | Hondón de las Nieves | Valencia (V) | Alicante (A) | 2,474 | Q1768905, Q24008510 | 03077 |
| 34808 | Javea | Valencia (V) | Alicante (A) | 28,016 | Q23984892, Q851020 | 03082 |
| 34869 | La Cuesta | León (LE) | Segovia (SG) | 5,000 | Q16466422 | 40208 |
| 34885 | La Iglesuela del Cid | Huesca (HU) | Teruel (TE) | 513 | Q1651517, Q24015103 | 44126 |
| 34887 | La Laguna | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 150,661 | Q16628307, Q54898 | 38023 |
| 34990 | Las Rosas | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 2,000 | Q24004406 | 38 |
| 35095 | Lobios | Ourense (OR) | Lugo (LU) | 2,512 | Q115769827, Q20549481 | 27059 |
| 35105 | Lomo de Arico | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 7,189 | Q6162455 | 38005 |
| 35122 | Los Gigantes | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 2,721 | Q1489481, Q24024538 | 38040 |
| 35357 | Mazo | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 4,805 | Q23984118, Q434321 | 38053 |
| 35406 | Mequinensa / Mequinenza | Huesca (HU) | Zaragoza (Z) | 2,479 | Q23995090 | 50165 |
| 35546 | Montecanal | Huesca (HU) | Zaragoza (Z) | 20,000 | Q13049643 | 50297 |
| 35683 | Muro del Alcoy | Valencia (V) | Alicante (A) | 7,983 | Q1768714 | 03092 |
| 35893 | Oliver-Valdefierro | Huesca (HU) | Zaragoza (Z) | 30,228 | Q9052125 | 50297 |
| 35938 | Orcheta | Valencia (V) | Alicante (A) | 1,303 | Q1768824, Q23982261 | 03098 |
| 35958 | Oropesa del Mar | Valencia (V) | Castellón (CS) | 8,830 | Q120172357, Q1596349, Q8841351 | 12085 |
| 36240 | Playa de las Américas | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 3,000 | Q267946 | 38006 |
| 36410 | Puebla de Alfindén | Huesca (HU) | Zaragoza (Z) | 3,552 | Q1640155, Q23993446 | 50219 |
| 36553 | Realejo Alto | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 35,963 | Q20018122 | 38031 |
| 36678 | Rosell | Valencia (V) | Castellón (CS) | 952 | Q1645981, Q37416935 | 12096 |
| 36701 | Ruesga | León (LE) | Palencia (P) | 1,120 | Q6113499 | 34056 |
| 36838 | San Ildefonso | León (LE) | Segovia (SG) | 5,426 | Q1125500, Q24014452 | 40181 |
| 36839 | San Isidro | Alicante (A) | Santa Cruz de Tenerife (TF) | 19,541 | Q6118899 | 38017 |
| 36843 | San Juan de Alicante | Valencia (V) | Alicante (A) | 21,939 | Q23980331, Q740204 | 03119 |
| 36845 | San Juan de Moró | Valencia (V) | Castellón (CS) | 1,947 | Q23992364, Q627890 | 12902 |
| 36925 | San Vicent del Raspeig | Valencia (V) | Alicante (A) | 56,715 | Q491667 | 03122 |
| 36978 | Sant Jordi | Valencia (V) | Castellón (CS) | 637 | Q2045712, Q23992348 | 12099 |
| 37180 | Sauzal | Las Palmas (GC) | Santa Cruz de Tenerife (TF) | 8,172 | Q5823284 | 38041 |
| 37247 | Sierra-Engarcerán | Valencia (V) | Castellón (CS) | 1,068 | Q1635361, Q23992663 | 12105 |
| 37497 | Torre de la Horadada | Valencia (V) | Alicante (A) | 2,676 | Q4894850 | 03902 |
| 37834 | Vall de Ebo | Valencia (V) | Alicante (A) | 346 | Q1983371 | 03135 |
| 38049 | Villafamés | Valencia (V) | Castellón (CS) | 1,660 | Q1116829, Q23990478 | 12128 |
| 38064 | Villafranca del Cid | Valencia (V) | Castellón (CS) | 2,227 | Q23991990, Q537017 | 12129 |
| 38088 | Villajoyosa | Valencia (V) | Alicante (A) | 33,797 | Q23978009, Q935589 | 03139 |
| 38311 | Villasana de Mena | León (LE) | Burgos (BU) | 3,427 | Q6162948 | 09410 |
| 38358 | Villavieja | Valencia (V) | Castellón (CS) | 3,352 | Q1768916, Q23977929 | 12136 |
| 38533 | els Poblets | Valencia (V) | Alicante (A) | 3,708 | Q120172085, Q987444 | 03901 |

*Las Rosas* (south Tenerife, 28.02, −16.65) has only a province code: its item is located directly in the province item.

### Also found (not changed here)
The six wrong province Wikidata IDs above, and similar ones in other countries, are left for a separate fix of
`states.json`.

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/ES.json` — `state_id` and `state_code` on 47 records
