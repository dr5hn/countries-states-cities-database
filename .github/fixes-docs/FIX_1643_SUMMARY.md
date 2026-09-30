# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Philippine cities filed under the wrong province

**1,810 Philippine records** (mostly barangays) move to the province they are in. Most were filed under a small
province far away, often the first of a region's provinces in alphabetical order: none of the 277 records filed under
Bataan was within 60 km of Bataan (they were in Cebu, Bohol and Negros); Abra held Pangasinan's barangays, Antique
those of Negros Occidental and Iloilo, Benguet those of Bukidnon. In 1,335 of them even the region was wrong. Both the
2019 import (ids 81xxx–85xxx, 1,026 moved) and a later batch (144xxx–146xxx, 784 moved) are affected.

### How they were verified
Two sources, both required:
1. **The record's own Wikidata item.** Every PH record has a `wikiDataId`. It counts only if it is the record's place:
   a label or alias equal to the record's name and a point within 5 km. Its current "located in" (P131) chain gives
   the CSC province (CSC's Philippine province IDs match their ISO 3166-2 codes).
2. **GeoNames.** The full Philippine dump's province codes were mapped to CSC provinces by majority vote of the
   records Wikidata verified (not of the filed provinces, which are unreliable here): 73 codes. At least 4 of the
   5 nearest mapped places, or a same-named place within 3 km, must lie in the same province.

| Own Wikidata item (5,357 records) | Filed under a province | Filed under a region |
|---|---:|---:|
| Confirms the filed state | 363 | 835 |
| Names another state | 1860 | 105 |
| Not the record's place (copy-forward ID, #1641) | 1759 | 291 |
| No chain to a CSC state | 71 | 73 |

Of the province-filed records Wikidata places elsewhere, **1,810** are confirmed by GeoNames and move; 26 are not
confirmed and 29 have no single province in their chain (held). The region-filed records it places elsewhere all
turn out to be in the right region (their province's parent), so they keep their region.

Not in this PR: the 1759 province-filed records whose Wikidata ID is another place's need a
different second source (the nearest municipalities), and records filed only under a region stay at region level.

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
| Cagayan | 103 |
| Batanes | 76 |
| Bukidnon | 75 |
| Oriental Mindoro | 71 |

| Move (top 20 of 68 pairs) | Records |
|---|---:|
| Abra → Pangasinan | 134 |
| Antique → Negros Occidental | 106 |
| Bataan → Cebu | 91 |
| Benguet → Bukidnon | 68 |
| Agusan del Norte → Cagayan | 65 |
| Antique → Iloilo | 63 |
| Bataan → Bohol | 61 |
| Albay → Camarines Sur | 61 |
| Bataan → Negros Oriental | 55 |
| Occidental Mindoro → Batangas | 55 |
| Occidental Mindoro → Quezon | 50 |
| Agusan del Norte → Isabela | 50 |
| Agusan del Sur → Nueva Ecija | 49 |
| Cagayan → Maguindanao del Norte | 42 |
| Bukidnon → Cotabato | 39 |
| Agusan del Sur → Tarlac | 38 |
| Batanes → Leyte | 37 |
| Agusan del Sur → Bulacan | 36 |
| Antique → Capiz | 35 |
| Benguet → Misamis Oriental | 35 |
| other pairs | 640 |

<details>
<summary>All 1,810 records (id, name, was, now, own Wikidata ID)</summary>

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
| 81330 | Aumbay | Benguet | Camiguin | Q31470691 |
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
| 83119 | Limbaan | Benguet | Misamis Oriental | Q31811887 |
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
| 84417 | Salvacion | Antique | Iloilo | Q31500606 |
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
| 143936 | Damawato | Bukidnon | Sultan Kudarat | Q31560657 |
| 143939 | Dualing | Bukidnon | Cotabato | Q31571737 |
| 143941 | Dunguan | Bukidnon | Cotabato | Q31573114 |
| 143946 | Glad | Bukidnon | Cotabato | Q31457955 |
| 143947 | Glamang | Bukidnon | South Cotabato | Q31457985 |
| 143950 | Gocoton | Bukidnon | Cotabato | Q31458381 |
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
| 144021 | Malingao | Bukidnon | Cotabato | Q31812179 |
| 144022 | Malisbeng | Bukidnon | Sultan Kudarat | Q31812183 |
| 144023 | Malitubog | Bukidnon | Cotabato | Q31812186 |
| 144027 | Manaulanan | Bukidnon | Cotabato | Q31812232 |
| 144029 | Manuangan | Bukidnon | Cotabato | Q31812272 |
| 144036 | Minapan | Bukidnon | Cotabato | Q31812431 |
| 144039 | New Cebu | Bukidnon | Cotabato | Q31812613 |
| 144043 | Noling | Bukidnon | Sultan Kudarat | Q31812653 |
| 144046 | Osias | Bukidnon | Cotabato | Q31812730 |
| 144047 | Paatan | Bukidnon | Cotabato | Q31812747 |
| 144049 | Pagangan | Bukidnon | Cotabato | Q31457641 |
| 144052 | Palkan | Bukidnon | South Cotabato | Q31458353 |
| 144055 | Pangyan | Bukidnon | South Cotabato | Q31462122 |
| 144057 | Patindeguen | Bukidnon | Cotabato | Q31464304 |
| 144058 | Pedtad | Bukidnon | Cotabato | Q31465985 |
| 144062 | Pimbalayan | Bukidnon | Sultan Kudarat | Q31468793 |
| 144068 | Puloypuloy | Bukidnon | Sultan Kudarat | Q31479916 |
| 144069 | Punolu | Bukidnon | Cotabato | Q31480317 |
| 144070 | Puricay | Bukidnon | Sultan Kudarat | Q31480656 |
| 144071 | Ragandang | Bukidnon | Sultan Kudarat | Q31483266 |
| 144074 | Saguing | Bukidnon | Cotabato | Q31498553 |
| 144077 | Sampao | Bukidnon | Sultan Kudarat | Q31501236 |
| 144080 | Santo Niño | Bukidnon | South Cotabato | Q31512848 |
| 144082 | Sapu Padidu | Bukidnon | South Cotabato | Q31513504 |
| 144084 | Sebu | Bukidnon | South Cotabato | Q31515335 |
| 144085 | Silway 7 | Bukidnon | South Cotabato | Q31520234 |
| 144086 | Sinolon | Bukidnon | South Cotabato | Q31521071 |
| 144087 | Sulit | Bukidnon | South Cotabato | Q31537011 |
| 144092 | Taguisa | Bukidnon | Sultan Kudarat | Q31542699 |
| 144103 | Tomado | Bukidnon | Cotabato | Q31558503 |
| 144104 | Tran | Bukidnon | Sultan Kudarat | Q31560240 |
| 144108 | Tuyan | Bukidnon | South Cotabato | Q31565668 |
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
| 144350 | Bayasong | Bukidnon | Sultan Kudarat | Q31492544 |
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
| 144528 | Idtig | Cagayan | Maguindanao del Norte | Q31811469 |
| 144534 | Kagay | Cagayan | Sulu | Q31811578 |
| 144535 | Kajatian | Cagayan | Sulu | Q31811579 |
| 144536 | Kalang | Cagayan | Sulu | Q31811585 |
| 144537 | Kalbugan | Cagayan | Maguindanao del Norte | Q31811590 |
| 144539 | Kambing | Cagayan | Sulu | Q31811601 |
| 144540 | Kanlagay | Cagayan | Sulu | Q31811605 |
| 144541 | Kansipati | Cagayan | Sulu | Q31811607 |
| 144544 | Karungdong | Cagayan | Sulu | Q31811615 |
| 144546 | Katidtuan | Cagayan | Maguindanao del Norte | Q31811618 |
| 144547 | Katuli | Cagayan | Maguindanao del Norte | Q31811624 |
| 144549 | Kitango | Cagayan | Maguindanao del Norte | Q31811657 |
| 144550 | Kitapak | Cagayan | Maguindanao del Norte | Q31811658 |
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
| 144564 | Layog | Cagayan | Maguindanao del Norte | Q31811821 |
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
| 144596 | Mileb | Cagayan | Maguindanao del Norte | Q31812417 |
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
| 144616 | Badak | Cagayan | Maguindanao del Norte | Q31474248 |
| 144617 | Bagan | Cagayan | Maguindanao del Norte | Q31475063 |
| 144627 | Pandakan | Cagayan | Sulu | Q31461425 |
| 144628 | Baka | Cagayan | Maguindanao del Norte | Q31476872 |
| 144629 | Bakung | Cagayan | Tawi-Tawi | Q31796194 |
| 144631 | Balas | Cagayan | Basilan | Q31478523 |
| 144634 | Bangkal | Cagayan | Sulu | Q31483604 |
| 144636 | Bankaw | Cagayan | Tawi-Tawi | Q31484136 |
| 144638 | Barurao | Cagayan | Maguindanao del Norte | Q31488037 |
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
| 144678 | Dado | Cagayan | Maguindanao del Norte | Q31558386 |
| 144679 | Dadus | Cagayan | Maguindanao del Norte | Q31558404 |
| 144680 | Dalican | Cagayan | Maguindanao del Norte | Q31559874 |
| 144681 | Dalumangcob | Cagayan | Maguindanao del Norte | Q31560132 |
| 144682 | Damabalas | Cagayan | Maguindanao del Norte | Q31560626 |
| 144683 | Damatulan | Cagayan | Maguindanao del Norte | Q31560642 |
| 144688 | Digal | Cagayan | Maguindanao del Norte | Q31566837 |
| 144690 | Dinganen | Cagayan | Maguindanao del Norte | Q31567872 |
| 144695 | Gang | Cagayan | Maguindanao del Norte | Q31588598 |
| 144696 | Guiong | Cagayan | Basilan | Q31811376 |
| 144698 | Pawak | Cagayan | Lanao del Sur | Q31465336 |
| 144699 | Payuhan | Cagayan | Sulu | Q31465652 |
| 144701 | Pidsandawan | Cagayan | Maguindanao del Norte | Q31467725 |
| 144702 | Pinaring | Cagayan | Maguindanao del Norte | Q31469100 |
| 144706 | Punay | Cagayan | Sulu | Q31480205 |
| 144707 | Rimpeso | Cagayan | Maguindanao del Norte | Q31488764 |
| 144711 | Sambuluan | Cagayan | Maguindanao del Norte | Q31500985 |
| 144712 | Sanga-Sanga | Cagayan | Tawi-Tawi | Q31509803 |
| 144714 | Sapa | Cagayan | Tawi-Tawi | Q31513250 |
| 144716 | Sapadun | Cagayan | Maguindanao del Norte | Q31513320 |
| 144717 | Satan | Cagayan | Maguindanao del Norte | Q31513807 |
| 144718 | Semut | Cagayan | Basilan | Q31515925 |
| 144721 | Simuay | Cagayan | Maguindanao del Norte | Q31520646 |
| 144723 | Sionogan | Cagayan | Sulu | Q31521243 |
| 144733 | Tabiauan | Cagayan | Sulu | Q31540914 |
| 144735 | Tairan Camp | Cagayan | Basilan | Q31542874 |
| 144742 | Tapayan | Cagayan | Maguindanao del Norte | Q31546273 |
| 144743 | Tapikan | Cagayan | Maguindanao del Norte | Q31546392 |
| 144747 | Taungoh | Cagayan | Tawi-Tawi | Q31547533 |
| 144748 | Taviran | Cagayan | Maguindanao del Norte | Q31547601 |
| 144751 | Tongouson | Cagayan | Tawi-Tawi | Q31558946 |
| 144756 | Tumbagaan | Cagayan | Tawi-Tawi | Q31563718 |
| 144757 | Tunggol | Cagayan | Sulu | Q31563984 |
| 144758 | Tungol | Cagayan | Maguindanao del Norte | Q31563999 |
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
| 144886 | Balangonan | Davao Occidental | Davao del Sur | Q31478354 |
| 144893 | Basiawan | Davao Occidental | Davao del Sur | Q31488818 |
| 144902 | Bolila | Davao Occidental | Davao del Sur | Q31508479 |
| 144905 | Buhangin | Davao Occidental | Davao del Sur | Q31516861 |
| 144912 | Caburan | Davao Occidental | Davao del Sur | Q31524373 |
| 144952 | Kalbay | Davao Occidental | Davao del Sur | Q31811589 |
| 144961 | Kinangan | Davao Occidental | Davao del Sur | Q31811650 |
| 144965 | Lacaron | Davao Occidental | Davao del Sur | Q31811727 |
| 144967 | Lais | Davao Occidental | Davao del Sur | Q31811741 |
| 144969 | Lapuan | Davao Occidental | Davao del Sur | Q31811802 |
| 145004 | Mangili | Davao Occidental | Davao del Sur | Q31812250 |
| 145026 | Nuing | Davao Occidental | Davao del Sur | Q31812675 |
| 145033 | Pangian | Davao Occidental | Davao del Sur | Q31461924 |
| 145065 | Sugal | Davao Occidental | Davao del Sur | Q31536125 |
| 145074 | Talagutong | Davao Occidental | Davao del Sur | Q31543247 |
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
| 145491 | Gueset | Agusan del Sur | Nueva Ecija | Q31811350 |
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

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/PH.json` — `state_id` and `state_code` on 1,810 records
