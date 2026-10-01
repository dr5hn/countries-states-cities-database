# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

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

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/{GB,GR,IN,MX,NO,PK,RS,RU,UY}.json` — `state_id` and `state_code` on 92 records; coordinates on 1
