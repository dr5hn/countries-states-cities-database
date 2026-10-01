# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

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

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/PH.json` — coordinates on 69 records; `state_id`/`state_code` on 1
