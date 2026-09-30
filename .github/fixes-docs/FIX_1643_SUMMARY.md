# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Italian cities filed under the wrong province

### How they were found
The 2019 import copied each city's population from GeoNames, so a record's source entry is the GeoNames place with
the same name (or an alternate name) within 3 km and **exactly the record's population** (GeoNames `cities500`).
6,076 Italian records have such an entry. GeoNames' second-level codes were mapped to CSC provinces by majority:
96.5% of those records are filed under the province their entry's code maps to. For 117 of the rest, the entry's
code maps clearly (at least 5 records, at least 80% agreement) to another province.

Each of the 117 was checked on Wikidata: the item with the record's name within 2 km of its point, and its current
**ISTAT municipality code** (P635; for a *frazione*, the code of the comune it is located in). The first three
digits are the province, mapped to CSC's `iso2` by the province's licence-plate code (P395). Codes with an end
date are ignored, because a comune that changes province gets a new code.

| Result | Records |
|---|---:|
| ISTAT province = the GeoNames province, not the filed one | **112** |
| No item with exactly that name; moved after the review found the comune (Cassino d'Alberi, Puia-Villanova, Capanne-Prato-Cinquale) | **3** |
| Held: the place spans two comuni in different provinces (Ponte a Elsa, Campoleone) | 2 |

100 of the first 112 already carry a `wikiDataId`, and in all 100 it is one of the matched items, the place in the new
province; the other 12 have none. Name, point, population and Wikidata ID all describe the same place; only the
province was wrong. Many are *frazioni* of comuni that merged or sit next to a provincial border, e.g. the
Valsamoggia villages (Bazzano, Crespellano, Savigno…) under Modena instead of Bologna, the Aprilia villages under
Rome instead of Latina, Salorno and Proves under Trentino instead of South Tyrol, and Bibione under Udine instead of
Venice.

Four share their name with a comune in the old province, which CSC does not otherwise hold: *Amato* (Catanzaro),
*Casoli* (Chieti), *La Maddalena* (the island comune, in Gallura Nord-Est Sardegna since April 2025, which CSC does
not have; Sassari before) and *Massa* (the provincial capital). These records are the
*frazioni* in Reggio Calabria, Teramo, Capoterra (Cagliari) and Massa e Cozzile (Pistoia), by point, population and
`wikiDataId`. The missing towns are a coverage gap, not part of this fix.

### Fix
**115 cities** move to their province. Only `state_id` and `state_code` change; all keep `Europe/Rome`.

| Move | Records |
|---|---:|
| Reggio Emilia → Modena | 5 |
| Modena → Bologna | 5 |
| Rome → Latina | 5 |
| Treviso → Venice | 4 |
| 69 other province pairs, 1–3 each | 96 |

| id | City | Was filed under | Now | Population | ISTAT code |
|---|---|---|---|---:|---|
| 58286 | Panzano in Chianti | Siena (SI) | Florence (FI) | 1,161 | 048021 |
| 58371 | Pecorara | Pavia (PV) | Piacenza (PC) | 141 | 033031, 033049 |
| 58388 | Pegolotte | Padua (PD) | Venice (VE) | 1,346 | 027010 |
| 58458 | Pescia Romana | Grosseto (GR) | Viterbo (VT) | 1,013 | 056035 |
| 58536 | Pianillo | Salerno (SA) | Naples (NA) | 7,253 | 063003 |
| 58537 | Piano | Salerno (SA) | Avellino (AV) | 4,745 | 064061, 064121 |
| 58710 | Pisignano | Forlì-Cesena (FC) | Ravenna (RA) | 1,208 | 039007 |
| 58785 | Polesine Parmense | Cremona (CR) | Parma (PR) | 697 | 034029 |
| 58837 | Ponte Caffaro | Trentino (TN) | Brescia (BS) | 1,478 | 017010 |
| 58900 | Popoli | L'Aquila (AQ) | Pescara (PE) | 5,394 | 068033 |
| 58941 | Porto d'Adda | Bergamo (BG) | Monza and Brianza (MB) | 1,052 | 108053 |
| 59098 | Proves - Proveis | Trentino (TN) | South Tyrol (BZ) | 288 | 021069 |
| 59198 | Puia-Villanova | Treviso (TV) | Pordenone (PN) | 2,167 | 093034 (Prata di Pordenone) |
| 59217 | Quarantoli | Mantua (MN) | Modena (MO) | 1,059 | 036022 |
| 59241 | Quero | Treviso (TV) | Belluno (BL) | 1,807 | 025075 |
| 59274 | Ramiseto | Parma (PR) | Reggio Emilia (RE) | 352 | 035046 |
| 59388 | Rio Salso-Case Bernardi | Rimini (RN) | Pesaro and Urbino (PU) | 1,425 | 041065 |
| 59426 | Rivanazzano | Alessandria (AL) | Pavia (PV) | 4,671 | 018122 |
| 59663 | Rottanova | Rovigo (RO) | Venice (VE) | 1,046 | 027006 |
| 59768 | Salice Terme | Alessandria (AL) | Pavia (PV) | 1,663 | 018073 |
| 59773 | Salionze | Mantua (MN) | Verona (VR) | 1,288 | 023089 |
| 59779 | Salorno | Trentino (TN) | South Tyrol (BZ) | 2,783 | 021076 |
| 59806 | Sambuceto | Pescara (PE) | Chieti (CH) | 9,596 | 069081 |
| 60034 | San Liberale | Treviso (TV) | Venice (VE) | 2,298 | 027020 |
| 60122 | San Michele dei Mucchietti | Reggio Emilia (RE) | Modena (MO) | 1,649 | 036040 |
| 60166 | San Pierino | Pisa (PI) | Florence (FI) | 1,881 | 048019 |
| 60427 | Santa Croce Scuole | Reggio Emilia (RE) | Modena (MO) | 1,066 | 036005 |
| 60591 | Savigno | Modena (MO) | Bologna (BO) | 1,184 | 037061 |
| 60798 | Sesto Imolese | Ravenna (RA) | Bologna (BO) | 1,513 | 037032 |
| 60881 | Sistiana-Visogliano | Gorizia (GO) | Trieste (TS) | 2,996 | 032001 |
| 60951 | Sorbolo | Reggio Emilia (RE) | Parma (PR) | 7,137 | 034037 |
| 61008 | Spigno Saturnia Inferiore | Frosinone (FR) | Latina (LT) | 954 | 059031 |
| 61009 | Spigno Saturnia Superiore | Frosinone (FR) | Latina (LT) | 231 | 059031 |
| 61084 | Strada | Ancona (AN) | Macerata (MC) | 1,547 | 043012 |
| 61234 | Terontola | Perugia (PG) | Arezzo (AR) | 1,608 | 051017 |
| 61252 | Terrossa | Vicenza (VI) | Verona (VR) | 1,179 | 023063 |
| 61263 | Tessera | Treviso (TV) | Venice (VE) | 1,239 | 027042 |
| 61322 | Torchiati | Salerno (SA) | Avellino (AV) | 2,762 | 064121 |
| 61345 | Torrazza dei Mandelli | Monza and Brianza (MB) | Milan (MI) | 1,046 | 015044 |
| 61719 | Valli | Padua (PD) | Venice (VE) | 1,143 | 027008 |
| 61777 | Vas | Treviso (TV) | Belluno (BL) | 487 | 025075 |
| 61910 | Vicarello | Pisa (PI) | Livorno (LI) | 3,106 | 049008 |
| 62259 | Zibello | Cremona (CR) | Parma (PR) | 910 | 034048 |
| 135244 | Abetone | Modena (MO) | Pistoia (PT) | 151 | 047023 |
| 135343 | Alano di Piave | Treviso (TV) | Belluno (BL) | 1,518 | 025002 |
| 135371 | Albiano Magra | La Spezia (SP) | Massa and Carrara (MS) | 1,907 | 045001 |
| 135462 | Amato | Catanzaro (CZ) | Reggio Calabria (RC) | 1,086 | 080071 |
| 135493 | Anduins | Udine (UD) | Pordenone (PN) | 229 | 093049 |
| 135544 | Aquila di Arroscia | Cuneo (CN) | Imperia (IM) | 118 | 008003 |
| 135899 | Bastia | Vicenza (VI) | Padua (PD) | 1,802 | 028071 |
| 135915 | Bazzano | Modena (MO) | Bologna (BO) | 6,131 | 037061 |
| 136042 | Bibione | Udine (UD) | Venice (VE) | 2,564 | 027034 |
| 136071 | Bivio Mortola | Frosinone (FR) | Caserta (CE) | 567 | 061069 |
| 136164 | Borghetto-Melara | La Spezia (SP) | Massa and Carrara (MS) | 1,868 | 045008 |
| 136175 | Borgo Massano | Rimini (RN) | Pesaro and Urbino (PU) | 1,302 | 041030 |
| 136200 | Borgo di Ranzo | Savona (SV) | Imperia (IM) | 219 | 008048 |
| 136204 | Borgofranco sul Po | Rovigo (RO) | Mantua (MN) | 420 | 020006 |
| 136245 | Boscochiaro | Rovigo (RO) | Venice (VE) | 1,321 | 027006 |
| 136381 | Bubano | Ravenna (RA) | Bologna (BO) | 1,450 | 037045 |
| 136499 | Calcara | Modena (MO) | Bologna (BO) | 2,370 | 037061 |
| 136587 | Camilleri-Vallelata | Rome (RM) | Latina (LT) | 1,101 | 059001 |
| 136588 | Caminata | Pavia (PV) | Piacenza (PC) | 212 | 033009 |
| 136622 | Campione | Varese (VA) | Como (CO) | 2,117 | 013040 |
| 136634 | Campo di Carne | Rome (RM) | Latina (LT) | 3,792 | 059001 |
| 136653 | Campofiorenzo-California | Monza and Brianza (MB) | Lecco (LC) | 1,306 | 097016 |
| 136663 | Campolongo Maggiore Liettoli | Padua (PD) | Venice (VE) | 3,578 | 027003 |
| 136760 | Capanne-Prato-Cinquale | Lucca (LU) | Massa and Carrara (MS) | 8,270 | 045011 (Montignoso) |
| 136848 | Carbonara di Po | Rovigo (RO) | Mantua (MN) | 937 | 020009 |
| 136949 | Casa Ponte | Milan (MI) | Pavia (PV) | 193 | 018166 |
| 136963 | Casalazzara | Rome (RM) | Latina (LT) | 1,496 | 059001 |
| 137056 | Casei | Alessandria (AL) | Pavia (PV) | 2,162 | 018033 |
| 137083 | Casoli | Chieti (CH) | Teramo (TE) | 1,085 | 067004 |
| 137090 | Casorzo | Alessandria (AL) | Asti (AT) | 617 | 005020 |
| 137113 | Cassino d'Alberi | Milan (MI) | Lodi (LO) | 1,048 | 098041 (Mulazzano) |
| 137170 | Castel di Judica | Enna (EN) | Catania (CT) | 1,754 | 087013 |
| 137229 | Castelletto | Modena (MO) | Bologna (BO) | 2,125 | 037061 |
| 137339 | Castiglione | La Spezia (SP) | Genoa (GE) | 466 | 010013 |
| 137393 | Catena | Prato (PO) | Pistoia (PT) | 1,542 | 047017 |
| 137608 | Cesarolo | Udine (UD) | Venice (VE) | 1,651 | 027034 |
| 137680 | Chiopris | Gorizia (GO) | Udine (UD) | 385 | 030024 |
| 137816 | Clusane | Bergamo (BG) | Brescia (BS) | 2,196 | 017085 |
| 137832 | Codisotto | Mantua (MN) | Reggio Emilia (RE) | 1,262 | 035026 |
| 137852 | Colico Piano | Como (CO) | Lecco (LC) | 7,204 | 097023 |
| 137854 | Collagna | Parma (PR) | Reggio Emilia (RE) | 399 | 035046 |
| 138144 | Crespellano | Modena (MO) | Bologna (BO) | 4,438 | 037061 |
| 138217 | Cutigliano | Modena (MO) | Pistoia (PT) | 399 | 047004 |
| 138255 | Dese | Treviso (TV) | Venice (VE) | 1,302 | 027042 |
| 138341 | Duino | Gorizia (GO) | Trieste (TS) | 1,369 | 032001 |
| 138450 | Faro Superiore | Reggio Calabria (RC) | Messina (ME) | 2,586 | 083048 |
| 138678 | Fossignano | Rome (RM) | Latina (LT) | 3,718 | 059001 |
| 138680 | Fossoli | Reggio Emilia (RE) | Modena (MO) | 3,578 | 036005 |
| 138897 | Genio Civile | Rome (RM) | Latina (LT) | 4,298 | 059001 |
| 138974 | Gionghi-Cappella | Vicenza (VI) | Trentino (TN) | 483 | 022102 |
| 139157 | Guardavalle Marina | Reggio Calabria (RC) | Catanzaro (CZ) | 2,346 | 079061 |
| 139293 | La Maddalena | Sassari (SS) | Cagliari (CA) | 7,877 | 092011 |
| 139342 | Lambrinia | Lodi (LO) | Pavia (PV) | 1,135 | 018048 |
| 139536 | Lisanza | Novara (NO) | Varese (VA) | 1,068 | 012120 |
| 139560 | Locara | Vicenza (VI) | Verona (VR) | 1,684 | 023069 |
| 139742 | Magreta | Reggio Emilia (RE) | Modena (MO) | 3,344 | 036015 |
| 139756 | Malavicina | Verona (VR) | Mantua (MN) | 1,952 | 020053 |
| 139854 | Marcon-Gaggio-Colmello | Treviso (TV) | Venice (VE) | 12,565 | 027020 |
| 139881 | Marina di Carrara | La Spezia (SP) | Massa and Carrara (MS) | 25,000 | 045003 |
| 139889 | Marina di Massa | Lucca (LU) | Massa and Carrara (MS) | 19,092 | 045010 |
| 139966 | Massa | Massa and Carrara (MS) | Pistoia (PT) | 350 | 047008 |
| 140114 | Mezzano Inferiore | Reggio Emilia (RE) | Parma (PR) | 1,285 | 034051 |
| 140133 | Migliarina | Reggio Emilia (RE) | Modena (MO) | 1,229 | 036005 |
| 140512 | Monterado | Pesaro and Urbino (PU) | Ancona (AN) | 525 | 042050 |
| 140561 | Monticelli Terme | Reggio Emilia (RE) | Parma (PR) | 4,345 | 034023 |
| 140587 | Montoro Superiore | Salerno (SA) | Avellino (AV) | 8,054 | 064062, 064121 |
| 140599 | Moransengo | Turin (TO) | Asti (AT) | 70 | 005122 |
| 140637 | Morsano | Venice (VE) | Pordenone (PN) | 1,478 | 093028 |
| 140700 | Musestre | Venice (VE) | Treviso (TV) | 1,182 | 026069 |
| 140758 | Nibbiano | Pavia (PV) | Piacenza (PC) | 418 | 033029 |
| 140912 | Oltre Brenta | Venice (VE) | Padua (PD) | 1,680 | 028058 |
| 140947 | Orentano | Lucca (LU) | Pisa (PI) | 1,676 | 050009 |

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/cities/IT.json` — `state_id` and `state_code` on 115 records
