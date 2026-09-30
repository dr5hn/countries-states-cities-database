# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Philippine records filed under the wrong province (second pass)

**520 more Philippine records** move to the province they are in (362 of them to another region too). #1663 moved
records whose own Wikidata item could be verified; these are the ones it could not use, mostly because their
`wikiDataId` belongs to another place (copy-forward, #1641). They show the same pattern: 41 Cebu barangays filed
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

Of the 2,264 province-filed records #1663 does not move, 1,223 already lie in their province.

| Result | Records |
|---|---:|
| Polygons and Wikidata municipalities agree on another province: **moved** | **520** |
| Wikidata municipalities disagree with the polygons: held | 233 |
| More than 3 km off the polygons (bad point, or a small island): held | 170 |
| Within 2 km of another province: held | 118 |

The #1663 reviewer's own containment test on the same polygons agrees with all 506 of these it could place; the
other 14 are coastal points it left just outside the simplified coastline.

### Fix
Only `state_id` and `state_code` change; all keep `Asia/Manila`.

| Move (top 15 of 99 pairs) | Records |
|---|---:|
| Bataan → Cebu | 41 |
| Occidental Mindoro → Quezon | 21 |
| Occidental Mindoro → Batangas | 21 |
| Zamboanga Sibugay → Zamboanga del Sur | 20 |
| Agusan del Sur → Nueva Ecija | 20 |
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
| other pairs | 257 |

<details>
<summary>All 520 records (id, name, was, now, nearest Wikidata municipality)</summary>

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
| 81390 | Bagalangit | Occidental Mindoro | Batangas | Q59835 (7.0 km) |
| 81400 | Bagong Sikat | Oriental Mindoro | Occidental Mindoro | San Jose (1.8 km) |
| 81412 | Bagumbayan | Antique | Negros Occidental | Valladolid (2.3 km) |
| 81419 | Baikingon | Benguet | Misamis Oriental | Opol (5.1 km) |
| 81433 | Balagon | Zamboanga Sibugay | Zamboanga del Sur | Midsalip (8.8 km) |
| 81435 | Balagtas | Batanes | Leyte | Matag-ob (5.2 km) |
| 81436 | Balagtasin | Occidental Mindoro | Batangas | San Jose (3.2 km) |
| 81437 | Balagui | Batanes | Biliran | Cabucgayan (4.7 km) |
| 81459 | Balele | Occidental Mindoro | Batangas | Balete (5.5 km) |
| 81482 | Balite Segundo | Occidental Mindoro | Cavite | Amadeo (5.2 km) |
| 81486 | Baliuag Nuevo | Albay | Camarines Sur | Q208864 (5.5 km) |
| 81488 | Baliwagan | Benguet | Misamis Oriental | Balingasag (3.6 km) |
| 81496 | Balogo | Batanes | Leyte | Albuera (4.1 km) |
| 81545 | Banos | Oriental Mindoro | Occidental Mindoro | Calintaan (8.6 km) |
| 81567 | Baras | Batanes | Leyte | Palo (3.9 km) |
| 81609 | Basud | Batanes | Leyte | San Isidro (5.8 km) |
| 81611 | Batad | Iloilo | Capiz | Pilar (8.8 km) |
| 81617 | Batarasa | Oriental Mindoro | Palawan | Bataraza (1.4 km) |
| 81620 | Batasan | Oriental Mindoro | Occidental Mindoro | Q107505 (8.5 km) |
| 81644 | Baugo | Bataan | Cebu | Cordova (8.0 km) |
| 81659 | Bayas | Antique | Iloilo | Estancia (3.9 km) |
| 81664 | Baybayin | Occidental Mindoro | Batangas | Rosario (7.4 km) |
| 81681 | Biabas | Bataan | Bohol | Q404680 (3.8 km) |
| 81691 | Biga | Occidental Mindoro | Cavite | Silang (3.0 km) |
| 81693 | Biga | Benguet | Misamis Oriental | Lugait (1.9 km) |
| 81702 | Bilaran | Occidental Mindoro | Batangas | Tuy (3.2 km) |
| 81715 | Binay | Occidental Mindoro | Quezon | San Narciso (8.1 km) |
| 81732 | Binuatan | Zamboanga Sibugay | Zamboanga del Sur | Dinas (0.8 km) |
| 81733 | Binubusan | Occidental Mindoro | Batangas | Lian (7.3 km) |
| 81745 | Biton | Bataan | Cebu | Daanbantayan (1.9 km) |
| 81749 | Biñan | Laguna | Cavite | Q62638 (3.1 km) |
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
| 81862 | Bulacnin | Occidental Mindoro | Batangas | Q59740 (4.5 km) |
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
| 82052 | Calilayan | Occidental Mindoro | Quezon | Q103777 (3.4 km) |
| 82056 | Calintaan | Oriental Mindoro | Occidental Mindoro | Calintaan (1.4 km) |
| 82082 | Camambugan | Bataan | Bohol | Ubay (3.8 km) |
| 82118 | Canlaon | Negros Oriental | Negros Occidental | La Castellana (5.6 km) |
| 82125 | Cantao-an | Bataan | Cebu | Minglanilla (5.1 km) |
| 82155 | Caraycaray | Batanes | Biliran | Naval (4.9 km) |
| 82174 | Carmen Grande | Antique | Negros Occidental | Pontevedra (3.8 km) |
| 82199 | Casuguran | Occidental Mindoro | Quezon | Jomalig (5.2 km) |
| 82211 | Caticlan | Antique | Aklan | Q626905 (6.6 km) |
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
| 82587 | Giawang | Bataan | Bohol | Q404680 (3.2 km) |
| 82590 | Gibong | Antique | Aklan | Nabas (7.1 km) |
| 82610 | Guadalupe | Bataan | Cebu | Barili (8.1 km) |
| 82615 | Gubaan | Zamboanga Sibugay | Zamboanga del Sur | Aurora (3.5 km) |
| 82618 | Guibodangan | Bataan | Cebu | Barili (4.3 km) |
| 82622 | Guihulñgan | Negros Oriental | Negros Occidental | Isabela (7.8 km) |
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
| 82704 | Hondagua | Occidental Mindoro | Quezon | Q103833 (5.1 km) |
| 82712 | Ichon | Batanes | Southern Leyte | Macrohon (4.8 km) |
| 82726 | Ilaya | Zamboanga Sibugay | Zamboanga del Norte | Piñan (7.4 km) |
| 82736 | Imelda | Albay | Camarines Norte | San Lorenzo Ruiz (1.7 km) |
| 82744 | Inayagan | Bataan | Cebu | Minglanilla (3.2 km) |
| 82757 | Ipil | Oriental Mindoro | Marinduque | Santa Cruz (6.3 km) |
| 82768 | Isabang | Occidental Mindoro | Quezon | Q104078 (4.2 km) |
| 82779 | Jaclupan | Bataan | Cebu | Minglanilla (6.6 km) |
| 82788 | Jamindan | Capiz | Antique | Culasi (7.3 km) |
| 82789 | Jampang | Bataan | Cebu | Argao (2.7 km) |
| 82791 | Jandayan Norte | Bataan | Bohol | Getafe (4.0 km) |
| 82795 | Japitan | Bataan | Cebu | Barili (3.5 km) |
| 82820 | Kabac | Bataan | Cebu | Madridejos (5.2 km) |
| 82832 | Kabungahan | Bataan | Cebu | Compostela (5.9 km) |
| 82835 | Kagawasan | Zamboanga Sibugay | Zamboanga del Sur | Dumalinao (6.3 km) |
| 82849 | Kalian | Zamboanga Sibugay | Zamboanga del Sur | Lapuyan (6.4 km) |
| 82850 | Kalibo (poblacion) | Antique | Aklan | Kalibo (0.6 km) |
| 82860 | Kananya | Batanes | Leyte | Kananga (0.1 km) |
| 82863 | Kanluran | Occidental Mindoro | Cavite | Q63102 (0.5 km) |
| 82865 | Kaongkod | Bataan | Cebu | Madridejos (3.0 km) |
| 82883 | Kauit | Bataan | Cebu | Medellin (6.6 km) |
| 82907 | Kinalansan | Albay | Camarines Sur | San Jose (3.8 km) |
| 82926 | Kotkot | Bataan | Cebu | Liloan (3.8 km) |
| 82927 | Kuanos | Bataan | Cebu | Minglanilla (4.6 km) |
| 82977 | Lagindingan | Benguet | Misamis Oriental | Laguindingan (1.3 km) |
| 82986 | Lake Sebu | South Cotabato | Sultan Kudarat | Palimbang (7.8 km) |
| 83007 | Lanao | Bataan | Cebu | Daanbantayan (2.7 km) |
| 83013 | Langcangan | Benguet | Misamis Occidental | Lopez Jaena (7.9 km) |
| 83031 | Lapaz | Bataan | Cebu | San Remigio (3.5 km) |
| 83062 | Legrada | Zamboanga Sibugay | Zamboanga del Sur | Dinas (4.1 km) |
| 83066 | Leon | Iloilo | Antique | San Remigio (7.7 km) |
| 83085 | Libertad | Oriental Mindoro | Romblon | Odiongan (6.1 km) |
| 83088 | Libertad | Antique | Iloilo | Banate (2.2 km) |
| 83136 | Linay | Zamboanga Sibugay | Zamboanga del Norte | Manukan (4.6 km) |
| 83161 | Locmayan | Antique | Guimaras | Nueva Valencia (6.4 km) |
| 83172 | Looc | Benguet | Misamis Oriental | Salay (2.8 km) |
| 83198 | Lucban | Quezon | Laguna | Q75888 (3.4 km) |
| 83217 | Lumbang | Occidental Mindoro | Laguna | Lumban (0.1 km) |
| 83224 | Lumbog | Zamboanga Sibugay | Zamboanga del Sur | Margosatubig (4.5 km) |
| 83234 | Luna | Albay | Masbate | San Jacinto (2.1 km) |
| 83244 | Lupi Viejo | Albay | Camarines Sur | Lupi (0.1 km) |
| 83276 | Mabini | Antique | Negros Occidental | Toboso (9.5 km) |
| 83284 | Mabitac | Occidental Mindoro | Laguna | Mabitac (1.6 km) |
| 83308 | Madalag | Aklan | Antique | Culasi (2.5 km) |
| 83340 | Magsalangi | Albay | Masbate | Milagros (7.5 km) |
| 83372 | Mainit Norte | Occidental Mindoro | Quezon | Perez (5.9 km) |
| 83387 | Malabonot | Antique | Aklan | Q626905 (7.7 km) |
| 83426 | Malicboy | Occidental Mindoro | Quezon | Padre Burgos (7.0 km) |
| 83430 | Malilinao | Batanes | Leyte | Matag-ob (5.4 km) |
| 83432 | Malim | Zamboanga Sibugay | Zamboanga del Sur | Tabina (2.9 km) |
| 83438 | Malinao Ilaya | Occidental Mindoro | Quezon | Padre Burgos (8.6 km) |
| 83481 | Mamungan | Benguet | Lanao del Norte | Balo-i (0.2 km) |
| 83504 | Mandaue City | Bataan | Cebu | Cordova (8.5 km) |
| 83511 | Mangarine | Oriental Mindoro | Occidental Mindoro | San Jose (3.3 km) |
| 83514 | Mangero | Occidental Mindoro | Quezon | San Andres (5.8 km) |
| 83530 | Manoc-Manoc | Antique | Aklan | Q626905 (5.9 km) |
| 83535 | Mansilingan | Antique | Negros Occidental | Murcia (6.9 km) |
| 83537 | Mantampay | Benguet | Lanao del Norte | Balo-i (5.6 km) |
| 83568 | Marawis | Antique | Negros Occidental | Hinigaran (4.7 km) |
| 83575 | Maria Cristina | Benguet | Lanao del Norte | Linamon (5.2 km) |
| 83578 | Maribojoc | Bataan | Bohol | Maribojoc (1.1 km) |
| 83584 | Marintoc | Albay | Masbate | Mobo (9.1 km) |
| 83599 | Masaya | Occidental Mindoro | Laguna | Bay (3.5 km) |
| 83610 | Mat-i | Benguet | Misamis Oriental | Naawan (6.1 km) |
| 83635 | Mauban | Quezon | Laguna | Cavinti (5.4 km) |
| 83639 | Maulawin | Occidental Mindoro | Laguna | Q75905 (1.8 km) |
| 83699 | Moncada | Tarlac | Pangasinan | Q41762 (5.1 km) |
| 83712 | Morobuan | Antique | Guimaras | Jordan (4.9 km) |
| 83727 | Muricay | Zamboanga Sibugay | Zamboanga del Sur | Labangan (6.1 km) |
| 83797 | Nañgka | Benguet | Lanao del Norte | Linamon (3.2 km) |
| 83800 | New Agutaya | Oriental Mindoro | Palawan | San Vicente (6.9 km) |
| 83856 | Oracon | Antique | Guimaras | Sibunag (6.0 km) |
| 83862 | Oroquieta | Misamis Occidental | Zamboanga del Norte | La Libertad (2.3 km) |
| 83866 | Osmeña | Oriental Mindoro | Palawan | Araceli (7.9 km) |
| 83875 | Pacol | Antique | Negros Occidental | Valladolid (2.6 km) |
| 83945 | Panacan | Oriental Mindoro | Palawan | Narra (4.2 km) |
| 83954 | Panayacan | Antique | Aklan | Tangalan (4.4 km) |
| 83972 | Pangao | Occidental Mindoro | Batangas | Q59740 (4.9 km) |
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
| 84720 | Santo Domingo | Albay | Camarines Sur | Buhi (7.5 km) |
| 84727 | Santo Niño | Occidental Mindoro | Batangas | Ibaan (3.5 km) |
| 84738 | Santor | Occidental Mindoro | Batangas | Malvar (8.0 km) |
| 84744 | Sapang Dalaga | Misamis Occidental | Zamboanga del Norte | Rizal (6.1 km) |
| 84760 | Sergio Osmeña Sr | Zamboanga Sibugay | Zamboanga del Sur | Josefina (7.2 km) |
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
| 84936 | Tagbina | Surigao del Sur | Agusan del Sur | Rosario (6.5 km) |
| 84942 | Tagkawayan Sabang | Occidental Mindoro | Quezon | Q104087 (2.7 km) |
| 84952 | Tagum Norte | Bataan | Bohol | Trinidad (5.1 km) |
| 84967 | Talaibon | Occidental Mindoro | Batangas | Ibaan (2.4 km) |
| 84971 | Talangnan | Bataan | Cebu | Malabuyoc (1.8 km) |
| 84974 | Talibon | Bataan | Bohol | Talibon (0.3 km) |
| 85004 | Tambac | Antique | Aklan | New Washington (3.5 km) |
| 85024 | Tampayan | Oriental Mindoro | Romblon | Magdiwang (2.1 km) |
| 85036 | Tangke | Bataan | Cebu | Minglanilla (7.6 km) |
| 85047 | Tapas | Antique | Capiz | Tapaz (0.1 km) |
| 85065 | Tawagan | Zamboanga Sibugay | Zamboanga del Sur | Labangan (5.2 km) |
| 85069 | Tayabas Ibaba | Occidental Mindoro | Quezon | Q103872 (5.8 km) |
| 85096 | Tibigan | Bataan | Bohol | Tubigon (0.5 km) |
| 85113 | Tiguha | Zamboanga Sibugay | Zamboanga del Sur | Lapuyan (7.5 km) |
| 85124 | Tinaan | Bataan | Cebu | Madridejos (1.8 km) |
| 85143 | Tiparak | Zamboanga Sibugay | Zamboanga del Sur | Tambulig (4.1 km) |
| 85150 | Tiwi | Antique | Iloilo | Barotac Nuevo (5.0 km) |
| 85165 | Tominhao | Bataan | Cebu | Daanbantayan (4.2 km) |
| 85183 | Tuban | Oriental Mindoro | Occidental Mindoro | Q107505 (7.1 km) |
| 85197 | Tubod-dugoan | Bataan | Cebu | Dumanjug (1.9 km) |
| 85201 | Tucdao | Batanes | Biliran | Culaba (9.1 km) |
| 85202 | Tucuran | Zamboanga Sibugay | Zamboanga del Sur | Tukuran (0.5 km) |
| 85220 | Tumalim | Occidental Mindoro | Batangas | Tuy (7.1 km) |
| 85238 | Tuyum | Antique | Negros Occidental | Cauayan (6.5 km) |
| 85247 | Umabay | Albay | Masbate | Mobo (3.9 km) |
| 85252 | Ungca | Antique | Iloilo | Pavia (2.9 km) |
| 85255 | Unidos | Antique | Aklan | Q626905 (9.9 km) |
| 85277 | Valencia | Batanes | Leyte | Kananga (8.6 km) |
| 85279 | Valle Hermoso | Bataan | Bohol | Carmen (4.7 km) |
| 85318 | Yapak | Antique | Aklan | Q626905 (6.2 km) |
| 143935 | Daliao | Bukidnon | Sarangani | Maasim (4.8 km) |
| 143949 | Glan Peidu | Bukidnon | Sarangani | Glan (3.9 km) |
| 143952 | Ilaya | Bukidnon | Sarangani | Glan (2.6 km) |
| 143956 | Kablalan | Bukidnon | Sarangani | Glan (4.9 km) |
| 143960 | Kamanga | Bukidnon | Sarangani | Maasim (6.6 km) |
| 143961 | Kapatan | Bukidnon | Sarangani | Glan (9.4 km) |
| 144000 | Lun Pequeño | Bukidnon | Sarangani | Alabel (7.2 km) |
| 144007 | Mabay | Bukidnon | Sarangani | Maitum (3.3 km) |
| 144020 | Malbang | Bukidnon | Sarangani | Maasim (5.4 km) |
| 144025 | Malungon | Sarangani | South Cotabato | Tupi (3.2 km) |
| 144031 | Marbel | Bukidnon | Cotabato | Matalam (3.3 km) |
| 144032 | Mariano Marcos | Bukidnon | Sultan Kudarat | Lambayong (7.6 km) |
| 144035 | Midsayap | Cotabato | Maguindanao del Norte | Kabuntalan (8.2 km) |
| 144037 | Mindupok | Bukidnon | Sarangani | Maitum (9.2 km) |
| 144038 | Nalus | Bukidnon | Sarangani | Kiamba (5.0 km) |
| 144044 | Norala | South Cotabato | Sultan Kudarat | Bagumbayan (3.5 km) |
| 144059 | Pigcawayan | Cotabato | Maguindanao del Norte | Sultan Mastura (6.3 km) |
| 144063 | Polo | Bukidnon | South Cotabato | Polomolok (7.3 km) |
| 144076 | Salunayan | Bukidnon | Cotabato | Midsayap (5.7 km) |
| 144078 | San Miguel | Bukidnon | South Cotabato | Norala (5.0 km) |
| 144079 | San Vicente | Bukidnon | South Cotabato | Banga (3.3 km) |
| 144090 | T'boli | Bukidnon | South Cotabato | T'Boli (8.5 km) |
| 144093 | Taluya | Bukidnon | Sarangani | Glan (3.7 km) |
| 144095 | Tambilil | Bukidnon | Sarangani | Kiamba (5.8 km) |
| 144098 | Tantangan | South Cotabato | Sultan Kudarat | Bagumbayan (4.1 km) |
| 144099 | Tañgo | Bukidnon | Sarangani | Glan (6.7 km) |
| 144102 | Tinoto | Bukidnon | Sarangani | Maasim (8.6 km) |
| 144157 | Concepcion | Bohol | Davao del Norte | Sawata (1.5 km) |
| 144171 | Esperanza | Bohol | Davao del Norte | Asuncion (5.8 km) |
| 144197 | La Libertad | Bohol | Davao del Norte | Braulio E. Dujali (5.6 km) |
| 144251 | Nabunturan | Davao de Oro | Davao del Norte | New Corella (3.8 km) |
| 144286 | San Vicente | Bohol | Davao de Oro | Laak (7.1 km) |
| 144327 | Tubod | Bohol | Davao del Norte | Carmen (6.9 km) |
| 144333 | Alamada | Cotabato | Maguindanao del Norte | Buldon (3.8 km) |
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
| 144526 | Union | Bulacan | Surigao del Norte | Q155784 (5.8 km) |
| 144532 | Kabasalan | Cagayan | Cotabato | Pikit (2.7 km) |
| 144542 | Kapai | Lanao del Sur | Lanao del Norte | Tagoloan (1.4 km) |
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
| 144773 | Balbalan | Kalinga | Abra | Malibcong (2.1 km) |
| 144780 | Bayabas | Camarines Norte | Benguet | Sablan (6.0 km) |
| 144781 | Besao | Mountain Province | Ilocos Sur | Quirino (7.6 km) |
| 144789 | Buguias | Camarines Norte | Benguet | Buguias (9.7 km) |
| 144790 | Bulalacao | Camarines Norte | Benguet | Mankayan (2.8 km) |
| 144791 | Butigui | Camarines Norte | Mountain Province | Paracelis (8.0 km) |
| 144793 | Calanasan | Apayao | Ilocos Norte | Vintar (7.3 km) |
| 144802 | Gambang | Camarines Norte | Benguet | Buguias (7.2 km) |
| 144803 | Guinsadan | Camarines Norte | Mountain Province | Bauko (3.1 km) |
| 144810 | Kabugao | Apayao | Ilocos Norte | Solsona (9.6 km) |
| 144813 | Kibungan | Camarines Norte | Ilocos Sur | Cervantes (8.3 km) |
| 144821 | Langiden | Camarines Norte | Abra | Langiden (6.7 km) |
| 144823 | Licuan | Camarines Norte | Abra | Licuan-Baay (6.5 km) |
| 144839 | Pasil | Kalinga | Abra | Daguioman (8.0 km) |
| 144852 | Sal-Lapadan | Camarines Norte | Abra | Sallapadan (2.8 km) |
| 144856 | San Ramon | Camarines Norte | Abra | Manabo (2.2 km) |
| 144930 | Davao City | Davao del Sur | Cotabato | Antipas (7.3 km) |
| 145046 | San Mariano | Davao Occidental | Davao de Oro | Maragusan (5.1 km) |
| 145099 | Accusilian | Agusan del Norte | Cagayan | Q49350 (1.6 km) |
| 145122 | Bagong Tanza | Agusan del Norte | Isabela | Aurora (2.8 km) |
| 145123 | Bagu | Agusan del Norte | Cagayan | Pamplona (4.8 km) |
| 145140 | Binguang | Agusan del Norte | Isabela | San Pablo (1.2 km) |
| 145143 | Bone South | Agusan del Norte | Nueva Vizcaya | Aritao (7.1 km) |
| 145164 | Carig | Agusan del Norte | Cagayan | Solana (5.6 km) |
| 145181 | Diffun | Quirino | Nueva Vizcaya | Quezon (7.3 km) |
| 145186 | Dumabato | Agusan del Norte | Quirino | Maddela (3.2 km) |
| 145190 | Echague (town) | Agusan del Norte | Isabela | Q49369 (0.1 km) |
| 145193 | Esperanza East | Agusan del Norte | Isabela | Burgos (5.1 km) |
| 145211 | Jones | Isabela | Quirino | Saguday (5.0 km) |
| 145213 | Kayapa | Nueva Vizcaya | Benguet | Itogon (9.3 km) |
| 145214 | La Paz | Agusan del Norte | Isabela | Cabatuan (5.3 km) |
| 145250 | Municipality of Delfin Albano | Agusan del Norte | Isabela | Tumauini (7.1 km) |
| 145251 | Muñoz East | Agusan del Norte | Isabela | Roxas (4.6 km) |
| 145260 | Palagao Norte | Agusan del Norte | Cagayan | Gattaran (8.0 km) |
| 145274 | Ramon (municipal capital) | Agusan del Norte | Isabela | Ramon (0.2 km) |
| 145275 | Ramos West | Agusan del Norte | Isabela | Q49369 (6.7 km) |
| 145282 | Salinas | Agusan del Norte | Nueva Vizcaya | Aritao (8.2 km) |
| 145285 | San Antonio | Agusan del Norte | Nueva Vizcaya | Bambang (4.1 km) |
| 145287 | San Bernardo | Agusan del Norte | Isabela | Santo Tomas (1.7 km) |
| 145290 | San Isidro | Agusan del Norte | Isabela | Q49369 (7.0 km) |
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
| 145422 | Cabiao | Nueva Ecija | Pampanga | Arayat (8.9 km) |
| 145444 | Carmen | Agusan del Sur | Nueva Ecija | Q28731 (3.6 km) |
| 145445 | Carranglan | Nueva Ecija | Pangasinan | San Quintin (6.2 km) |
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
| 145641 | San Agustin | Agusan del Sur | Zambales | Q56623 (4.6 km) |
| 145643 | San Alejandro | Agusan del Sur | Nueva Ecija | Quezon (4.1 km) |
| 145644 | San Andres | Agusan del Sur | Nueva Ecija | Guimba (6.7 km) |
| 145645 | San Anton | Agusan del Sur | Nueva Ecija | Jaen (1.7 km) |
| 145651 | San Basilio | Agusan del Sur | Pampanga | Q55730 (5.4 km) |
| 145655 | San Casimiro | Agusan del Sur | Nueva Ecija | Licab (2.5 km) |
| 145657 | San Cristobal | Agusan del Sur | Nueva Ecija | Licab (1.6 km) |
| 145661 | San Felipe Old | Agusan del Sur | Nueva Ecija | Aliaga (6.7 km) |
| 145663 | San Francisco | Agusan del Sur | Nueva Ecija | San Antonio (5.5 km) |
| 145677 | San Juan de Mata | Agusan del Sur | Tarlac | San Jose (9.5 km) |
| 145679 | San Lorenzo | Agusan del Sur | Zambales | Masinloc (5.4 km) |
| 145685 | San Mariano | Agusan del Sur | Nueva Ecija | San Antonio (2.8 km) |
| 145690 | San Nicolas | Agusan del Sur | Tarlac | Victoria (0.9 km) |
| 145694 | San Patricio | Agusan del Sur | Pampanga | Mexico (3.8 km) |
| 145701 | San Roque Dau First | Agusan del Sur | Pampanga | Q55730 (4.6 km) |
| 145706 | San Vincente | Agusan del Sur | Oriental Mindoro | Baco (9.9 km) |
| 145712 | Santa Fe | Agusan del Sur | Zambales | Q56623 (7.0 km) |
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
| 145960 | Lusong | Abra | La Union | Q40298 (3.5 km) |
| 145976 | Malibong East | Abra | Pangasinan | Q43154 (2.7 km) |
| 146007 | Paitan Este | Abra | Pangasinan | Sual (7.2 km) |
| 146008 | Palacpalac | Abra | Pangasinan | Pozorrubio (2.6 km) |
| 146009 | Palguyod | Abra | Pangasinan | Pozorrubio (3.3 km) |
| 146026 | Polo | Abra | Pangasinan | Bani (9.7 km) |
| 146027 | Polong | Abra | Pangasinan | Lingayen (5.6 km) |
| 146028 | Polong Norte | Abra | Pangasinan | Malasiqui (1.6 km) |
| 146040 | Ranao | Abra | Pangasinan | Bani (5.2 km) |
| 146058 | San Fernando Poblacion | Abra | La Union | San Juan (5.9 km) |
| 146060 | San Gabriel First | Abra | Pangasinan | Q41762 (4.7 km) |
| 146071 | San Quintin | Abra | Pangasinan | San Quintin (0.0 km) |
| 146097 | Sugpon | Ilocos Sur | La Union | Santol (3.7 km) |
| 146109 | Tandoc | Abra | Pangasinan | Calasiao (7.5 km) |
| 154504 | Tapaz | Capiz | Antique | Barbaza (5.9 km) |
| 154524 | Ligawasan | Cotabato | Maguindanao del Sur | Rajah Buayan (3.1 km) |
| 154580 | Santa Maria | Laguna | Rizal | Q106817 (5.3 km) |
| 154807 | Bontoc | Southern Leyte | Leyte | Bato (9.2 km) |
| 154841 | Santa Rita | Western Samar | Leyte | Babatngon (3.3 km) |

</details>

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/PH.json` — `state_id` and `state_code` on 520 records
