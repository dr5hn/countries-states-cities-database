# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Batches of cities filed under one wrong state

**453 cities** from three bulk additions move to the state they are in: Lisbon-area parishes filed under Guarda
(Portugal, ids 143xxx), villages of Zhytomyr Oblast and two others filed under Poltava (Ukraine, 149xxx) and villages of Nagano filed
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
| PT | Guarda → Lisbon | 211 |
| UA | Poltavska → Zhytomyrska | 154 |
| JP | Kōchi → Nagano | 73 |
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

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/{PT,UA,JP}.json` — `state_id` and `state_code` on 453 records; coordinates on 2
