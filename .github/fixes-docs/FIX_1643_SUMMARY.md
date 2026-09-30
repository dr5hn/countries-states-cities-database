# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

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
| Unresolved (no same-named item nearby, or contained in several) | 51 |

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

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/MX.json` — `state_id` and `state_code` on 127 records
