# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

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

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/*.json` (18 files) — `state_id` and `state_code` on 44 records
