# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

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

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/states/states.json` — `wikiDataId` on 277 states; `iso2`/`iso3166_2` on 2
