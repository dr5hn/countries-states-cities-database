# Fix Summary: Copy-forward duplicate wikiDataIds in other country files

## Issue Reference
**Original Issue:** [#1641](https://github.com/dr5hn/countries-states-cities-database/issues/1641) — follow-up to
[#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) (Mexico, fixed in #1637)

## Problem

A 2019 import bug carried the previous row's `wikiDataId` forward whenever no Wikidata match was found, so runs
of consecutive records share one QID. Across 177 country files, 41,631 records sit in 15,454 shared-QID groups.
Each country is fixed in its own PR and documented in its own section below.

## France

**Before:** 6,401 records of `contributions/cities/FR.json` in 2,036 shared-QID groups — e.g. `Q1366381`
(Saint-Germain, Aube) sat on 17 records, from *Saint-Germain* to *Saint-Germain-du-Puch*.

### Review history

| Round | Finding | Fix |
|---|---|---|
| 1 | All 6,149 INSEE matches reproduced; samples 59/60 changed and 20/20 kept IDs correct. But: *Marseille Saint-Victor* got the abbey; five records whose coordinates are wrong got a place near those coordinates instead of the commune their department and population name (*Ballon*, *Saint-Leu*, *Saint-François*, *Puiseaux*, *Mareuil*); 13 blanks were findable; the edit-while-running check never re-read the file, a rerun overwrote the report, and a lone "quartier prioritaire" could still be chosen | Census-population check for distant INSEE matches; religious buildings and "quartiers prioritaires" never chosen; spelling-slip matches; "Bourg de" and last-part name forms; four reviewed decisions; the file is re-read before writing and a no-op rerun leaves the report alone |
| 2 | All 24 changed records correct; all 6,166 INSEE matches reproduced. The edit-while-running check compared only `wikiDataId`, and an aborted run still rewrote the report; a few doc claims overstated | Any change to a planned record's name, state, coordinates, population or ID aborts the run before anything is written; doc corrected |
| 3 | Data correct. Conflict resolution also reads records outside the plan (the lone holder of a proposed QID), so an edit to one of those mid-run could still produce a duplicate QID; files were overwritten in place; four wrong IDs outside the groups; "16 records have wrong coordinates" and "by INSEE code" overstated | Any added, removed, reordered or edited record in FR.json aborts the run (with a no-network unit test that replays the reviewer's case); FR.json, the report and the cache are written to a temp file and swapped in; the four IDs fixed as reviewed decisions; doc corrected |

### Method

Every record in a shared-QID group is matched again from scratch; nothing is inferred from the shared ID.
French cities are communes, and every commune item on Wikidata carries its **INSEE code** (P374), which starts
with the department number — the record's `state_code`. FR records carry no full INSEE code, so "INSEE
matching" here means **department prefix plus normalized name**: the item's INSEE code must start with the
record's department, and its French label must equal the record's name once case, accents, hyphens and
apostrophes are folded. Department plus name is a strong identity check, which Mexico lacked.

1. **INSEE: department prefix + name (6,166 records).** The item whose INSEE code starts with the record's
   department and whose French label is the record's name (folded as above).
   When a commune merger leaves several items on one code (the historic commune and the new one), the one
   without a dissolution date (P576) wins: *Aigre* gets the current commune Q60544458, not the pre-2019
   Q1451759. Accepted within 5 km (6,150 records; 5,911 within 1 km). Farther away only when one of the item's
   census populations (dated 1990 or later, or undated) is within 5% of the record's — then one of the two
   points is wrong, not the identity (16 records: in 15 the database's point is wrong, e.g. *Saint-Leu*,
   population 29,278, is Saint-Leu in Réunion although its coordinates are in Saône-et-Loire, and *Ballon*, 823,
   is Ballon in Charente-Maritime, not the Sarthe village at its coordinates; in *Chef-Boutonne* Wikidata's
   point is the one that is off).
2. **Named place nearby (202 records).** Otherwise: a settlement, neighbourhood or commune within 3 km whose
   label or alias, in any language, is the record's name. This catches:
   - renamed communes: *Cadillac* → Cadillac-sur-Garonne; *Cransac* (now Cransac-les-Thermes) and *Céreste*
     (now Céreste-en-Luberon) keep their existing IDs;
   - Catalan names: *Argelers* → Argelès-sur-Mer, *Banyuls de la Marenda* → Banyuls-sur-Mer;
   - neighbourhoods, mostly Marseille quartiers, including "Marseille Endoume"-style names;
   - commune centres named "Bourg de X" (*Bourg de Joué-sur-Erdre* → Joué-sur-Erdre);
   - records filed under the wrong department (see below).

   Never chosen: a religious building (the abbey that shares the Saint-Victor quartier's name) or a
   "quartier prioritaire" (an urban-policy zone reusing a neighbourhood's name). Preference when several
   items match: the record's own QID; then an item whose French label *is* the name (the locality
   *Berck-Plage*, not the commune Berck that lists it as an alias; the former commune *Bienville*, not
   Eurville-Bienville); then a commune over other items such as GeoNames-generated stubs, current communes
   first, then the main item (most Wikipedia articles). With no exact name, the one place within 1 km whose
   name is at most two letters off: *La Page* → La Plage, *La Millère* → La Millière.
3. **Merged commune bearing its name (6 records).** Still nothing: the one commune within 3 km whose name
   starts or ends with the record's name, with a population within a factor of two when both are known —
   *Tignieu* → Tignieu-Jameyzieu, *Veigy* → Veigy-Foncenex, *Cosnes* → Cosnes-et-Romain, *Porcieu* →
   Porcieu-Amblagnieu, *Les Ancizes* → Les Ancizes-Comps, *Pragoulin* → Saint-Sylvestre-Pragoulin.
4. **Reviewed decisions (4 records in the groups)** — the right item cannot be reached mechanically:

   | Record | ID | Evidence |
   |---|---|---|
   | 43904 Marseille Saint-Victor | Q3463494 | quartier Saint-Victor, 7e arrondissement; the item has no coordinates, and the nearby Q1858504 is the abbey |
   | 42904 La Valentine | Q3213417 | quartier La Valentine, 11e; no coordinates; population 3,399 vs the record's 3,212 |
   | 44400 Mouret | Q3233960 | quartier Les Mourets, 13e, 0.9 km from the record (filed under department 12 in error) |
   | 39990 Beuville | Q49346076 | the settlement item at the record's point (3 m); the commune Biéville-Beuville is record 40041's ID and lists Beuville only as an alias |
5. **Blank (23 records)** when nothing verifies.
6. **Reviewed decisions outside the groups (4 records).** Review round 3 found four wrong IDs that were not
   copied forward. Each was checked on Wikidata (label, INSEE code against the record's department, point
   against the record's, census population) on 2 October 2026, and is applied through the same reviewed-decision
   list, so the script stays the source of the data:

   | Record | Was | Now | Evidence |
   |---|---|---|---|
   | 46134 Saint-Julien (filed 83) | Q765366, a commune in Côtes-d'Armor 857 km away | Q3462652 | quartier Saint-Julien, Marseille 12e, 0.5 km from the record; population 10,068 vs 9,939. Filed under Var in error (Marseille is in 13) |
   | 44032 Messac (filed 17) | Q35728287, the settlement in Ille-et-Vilaine at the record's point | Q1144439 | the commune Messac, INSEE 17231 = the record's department; population 104 vs 104. The Ille-et-Vilaine Messac (Q666305, INSEE 35176) had 3,089 people in 2015 and is now part of Guipry-Messac, which has its own record (161781): the record's department and population agree, its point is wrong (step 1's rule) |
   | 43005 Landes (filed 17) | Q12563, the department of Landes | Q24695 | the commune Landes, INSEE 17202 = the record's department; population 575 vs 575. The record's point is in the Landes department (0.4 km from Ygos-Saint-Saturnin) and is wrong |
   | 156001 Villegusien-le-Lac (52) | Q1331384, the commune dissolved in 2015 (now a commune déléguée) | Q28464428 | the current commune (2016–), INSEE 52529; population 993 vs 993; the same current-commune rule as step 1 |

One ID per place: a QID landing on two records is either one place entered twice (both within 3 km —
reported for merging) or a conflict, in which case the group record is blanked (*Sarrola*, whose commune
belongs to *Sarrola-Carcopino* 8.7 km away).

### Results

| Outcome | Records |
|---|---:|
| Existing ID verified and kept | **1,808** |
| New verified ID | **4,570** |
| ID removed | **23** |
| **Records in shared-QID groups** | **6,401** |
| Outside the groups: wrong ID replaced after review | **4** |

- Shared-QID groups: **2,036 → 0**
- Records changed: **4,597** (4,593 in the groups + 4 outside), only the `wikiDataId` field; record count
  unchanged at 10,534
- Records with a `wikiDataId`: 10,079 → 10,056

### Verification

- After the fix no QID is shared anywhere in FR.json; rerunning the script changes nothing and leaves the report
  untouched.
- The script aborts without writing FR.json or the report if, while it runs, a record is added, removed or
  reordered, or edited in its id, name, department, coordinates, population or `wikiDataId` (other fields, such as
  `native`, are left as they are), because conflict resolution reads
  records outside the plan too. FR.json, the report and the cache are written to a temp file and swapped in.
  `test_france_fix_copyforward_wikidataids.py` (no network) replays the reviewer's case — *Abilly* (unplanned)
  taking Q28520 while *Abbeville* is matched to Q28520 — and checks the run aborts with both files untouched;
  it fails against the previous version of the script.
- 46 records are matched by position to a commune in another department. Where both the record and the commune
  have a population (44), they agree within 30% in 43 — e.g. *Évry*, filed under Yonne, has 51,900 people: it is
  Évry in Essonne, not the village in Yonne. The exception, *Jumelles*, carries the population of the commune it
  merged into (Longué-Jumelles). Where the record's department and population instead agree on another commune,
  that commune wins (step 1).
- The list of blanks and the conflict is in `bin/scripts/fixes/france_fix_copyforward_wikidataids.report.json`.

### Found along the way

**Records filed under the wrong department (46).** Matched by name and coordinates to a commune in another
department (populations agree in 43 of the 44 with both figures) — e.g. *Albens* (filed 74, in 73), *Évry* (89 → 91), *Vire* (71 → 14),
*Pierrefitte-sur-Seine* (95 → 93), and eight Maine-et-Loire villages filed under Loire-Atlantique. Not changed
here.

**Database-coordinate errors (15), plus one Wikidata-coordinate discrepancy.** Of the 16 records matched by
department, name and population despite a distant point (step 1), 15 have a wrong stored point — *Saint-Leu*
(Réunion) and *Saint-François* (Guadeloupe) sit in mainland France, *Ballon* 252 km away, *Mareuil*,
*Puiseaux*, *Doubs*, *Mayenne*, *Buxerolles* 10–58 km away, *Louplande* and *Charmes-la-Grande* 6–7 km away,
and five Corsican communes (Furiani, Ghisonaccia, Lumio, Morosaglia, Oletta). Not changed here. The 16th,
*Chef-Boutonne*, is a Wikidata discrepancy, not a database error: the stored point is right (by the town hall),
and it is Wikidata's point for the merged commune that lies 5.8 km off. Outside the groups, *Messac* and
*Landes* (step 6) also have wrong stored points; not changed here either.

**Departments stored as cities (17).** *Cantal*, *Charente-Maritime*, *Dordogne*, *Département du Vaucluse*,
*Gers*, *Gironde*, *Haute-Marne*, *Manche*, *Nord*, *Pas-de-Calais*, *Sarthe*, *Seine-et-Marne*, *Territoire
de Belfort*, *Val-de-Marne*, *Var*, *Vosges*, *Yvelines* are department names with `type: city` (e.g. *Gironde*
has 1,674,980 people). Their IDs are removed; the records should probably be deleted separately. (*Doubs* and
*Mayenne* looked like departments too, but their populations are those of the communes Doubs and Mayenne.)

**Wrong IDs outside the shared groups (4).** *Saint-Julien*, *Messac*, *Landes* and *Villegusien-le-Lac*:
fixed here as reviewed decisions (step 6). *Saint-Julien* is also filed under the wrong department (83, not
13); not changed here.

### Known limitations

- **Merged communes:** where a merger kept the old name (*Aigre*, *Douzy*, *Chef-Boutonne*), the record gets the
  current commune, not the pre-merger item, by the convention that a city record means the place as it is
  today. The records carry pre-merger populations, so the pre-merger item would be equally defensible.
- **Left blank:** *Boulazac* (the former commune's point is 7 km from the record and its scope differs from
  today's Boulazac Isle Manoire), *Fouillard* (two same-named items 0.6 km apart), *Pietranera*, *Port à Binson*
  (no matching item), *Saint-Quentin-en-Yvelines* (no settlement item; Q1120022 is the agglomeration),
  *Sarrola* (conflict above).
- *Courteilles* (41267) keeps Q34797143, whose INSEE code and point are the former commune merged into
  Giel-Courteilles, although its French Wikipedia link is for Courteilles in Alençon — the item itself is
  inconsistent.
- Results reflect Wikidata as of the run (29 September 2026; the four step-6 IDs were checked on 2 October
  2026); the script caches lookups, and deleting the cache refreshes them.

### Reproduce

```bash
python3 bin/scripts/fixes/france_fix_copyforward_wikidataids.py --dry-run   # plan + report only
python3 bin/scripts/fixes/france_fix_copyforward_wikidataids.py             # write FR.json
python3 -m unittest bin/scripts/fixes/test_france_fix_copyforward_wikidataids.py   # tests, no network (Python 3.11+)
```

Wikidata lookups are cached in `$CSC_CACHE_DIR` (default `<tmp>/csc-copyforward-fr`).

## Brazil, Germany, Spain and Austria

**Before:** in `BR.json`, `DE.json`, `ES.json` and `AT.json`, 2,671, 1,278, 1,099 and 935 pairs of neighbouring records
shared one `wikiDataId` (origin/master 59743ae2). A random sample of 400 cities on 8 Oct 2026 found 59 wrong Wikidata ids among the
360 it could decide (16.4%; 40 stayed unresolved), mostly this pattern.

### Method

Every record in the four files is matched again from scratch; nothing is inferred from the shared id.

- **Municipalities** are matched to the official register by name and state or province, and the Wikidata item
  carrying the same official code is taken: [IBGE municipalities](https://servicodados.ibge.gov.br/api/v1/localidades/municipios)
  (BR, P1585), [Destatis GV-ISys, 30 Sep 2026](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/_inhalt.html)
  (DE, AGS, P439), [INE municipality dictionary, 1 Jan 2026](https://www.ine.es/daco/daco42/codmun/diccionario26.xlsx)
  (ES, P772) and [Statistik Austria Gemeindeverzeichnis, 1 Jan 2026](https://www.statistik.at/fileadmin/pages/453/RegGemVz2026.ods)
  (AT, GKZ, P964). The item must lie near the record (DE: register and item points both within 5 km; BR: within
  25 km only with an agreeing item name).
- **Other records** (localities, districts, former municipalities) need an exact label or alias, a point within 5 km
  and a compatible instance-of.
- A replacement also needs evidence that the current id is another place (a point more than 5 km away, or a
  different official code); otherwise the record is held. Eight false links are cleared to null after manual review;
  no city record is removed.

### Results

| Country | Changed |
| --- | --- |
| BR | 2,432 |
| DE | 1,087 |
| ES | 1,114 |
| AT | 767 |

5,400 ids changed, 8 of them removed (the current item named a non-place or a different place and no
item fits), 3,259 held. Records sharing one id in these four files fell from 9,879 to
1,520. Examples: Acaiaca (BR) Q1784836 -> Q1749743 (IBGE 3100401); Absberg (DE) Q255698 -> Q331886
(AGS 09577111); Ababuj (ES) Q1607619 -> Q594888 (INE 44001); Abfaltersbach (AT) Q292866 -> Q319992 (GKZ 70701).

### Review

A Codex review re-extracted every register, fetched every old and new item live and checked all 4,974 code-backed
targets (all active, matching code, not dissolved or redirected). It found 5 wrong replacements (three villages given
their parent municipality's item: Albersdorf, Oehling, Raffelstetten; Langenlebarn-Oberaigen given the larger
Langenlebarn; Neu-Pattern given the abandoned Pattern), now corrected; 46 replacements that only swapped a municipality's
item for its main settlement's item or the reverse (not another place), now kept as they were; and 67 wrong ids the first pass had held, now corrected
with the evidence in its report.

### Known limitations

- 3,259 held records keep their current id: no compatible item, a nearby namesake, the settlement of the
  same municipality, or no point to prove another place. They need manual research.
- 46 groups of records now share an id because they are the same place under two spellings or names
  (Batayporã twice, Ipaussu and Ipauçu, Köpenick and Berlin Köpenick); with the 51 Spanish same-place pairs they are
  listed in the audit files for a separate merge, not merged here.
- ES and AT registers carry no coordinates, so their municipality matches rest on name, province and code, with the
  item's point checked against the record.

### Reproduce

The plan was built from snapshots of the four registers and of Wikidata taken on 8 October 2026; the matcher and the
snapshots are kept with the project's audit files rather than in this repository, because the matcher replays cached
inputs and does not download them. To check a single record, look up its official code in the register linked above
and the Wikidata item carrying that code (P1585, P439, P772 or P964).

## Japan, the Netherlands, Romania and Poland

**Before:** in `JP.json`, `NL.json`, `RO.json` and `PL.json`, 481, 428, 356 and 344 pairs of neighbouring records
shared one `wikiDataId` (origin/master 6aba19fc).

### Method

Every record in the four files is matched again from scratch, with the five safeguards the review of the previous
batch asked for. The matcher replaces a record's id (888 records) only when all of these hold:

- its folded name or native name equals an official register row of the same level in its prefecture, province,
  county or voivodeship: [MIC local government codes](https://www.soumu.go.jp/denshijiti/code.html) (JP, P429),
  [CBS 86097NED gemeenten and woonplaatsen](https://www.cbs.nl/nl-nl/cijfers/detail/86097NED) (NL, P382 / P981),
  [INS SIRUTA](https://data.europa.eu/data/datasets/fcba1a54-cffd-422c-b3ac-920f63564085) (RO, P843; corroborated
  against the live INS locality service) and [GUS TERYT TERC/SIMC](https://eteryt.stat.gov.pl/) (PL, P1653 / P4046);
- the Wikidata item carries that exact active code, a matching label or alias, a compatible instance-of and a point
  within 5 km of the record; a village gets the village's item, not its municipality's;
- the current id is a different place: its point is more than 5 km away and it does not carry the same code;
- the current item is not a related identity of the same place (kept: 655 records, of which 427 are a capital or
  main settlement of the other, 190 a same-named parent or seat, 38 a redirect to the target).

### Review

A Codex review fetched every old and new item live and confirmed all 888 matcher replacements. From its sample of
held and kept records and its check of shared ids it found 92 wrong ids the matcher had left alone (for example Naka,
Ibaraki carrying the item of Naha, Okinawa). Applied: 38 set to the right item and 54 cleared, plus Ono, Hyogo set to
its own item. These 39 reviewed corrections rest on the review's identity evidence rather than the safeguards above
(some items carry no official code, six are 5-19 km from the record). A second review showed that many held records
share an item whose owner the matcher verified by official code in another prefecture or province (Hakone carried
Hakodate's item); those 371 links are cleared too. A cleared id is a demonstrably wrong link, removed pending a
verified replacement; it does not mean that no item exists.

### Results

| Country | Changed | Cleared | Held | Neighbouring pairs sharing an id |
| --- | --- | --- | --- | --- |
| JP | 196 | 131 | 389 | 481 -> 279 |
| NL | 130 | 212 | 398 | 428 -> 77 |
| RO | 311 | 38 | 358 | 356 -> 11 |
| PL | 290 | 44 | 60 | 344 -> 10 |

927 ids changed (888 by the matcher, 39 from the review), 425 wrong links cleared, 1205 held. Examples: Abashiri
(JP) Q2828134 -> Q305640 (MIC 012114); 't Zand (NL) Q2766547 -> Q2384262 (CBS 2758); Aleşd (RO) Q2718372 -> Q16898117
(SIRUTA 26706); Augustów (PL) Q567332 -> Q464763 (TERYT 0977539).

### Known limitations

- 1205 held records keep their current id, most because no official row of that name and level exists in their region
  (Japanese and Dutch records below municipality level, romanisations that do not match). They need manual research.
- 402 groups of records still share an id. 200 are the same place in two records (Kanazawa and
  Kanazawa-shi; Warsaw twice; Ono and Ono Shi), for a separate merge. 73 span two states with unresolved members
  and no record verified directly by official code at that item (JP 31, NL 35, RO 1, PL 6); 13 of them hold a
  matcher-verified identity through a redirect or a capital or seat relation, 60 none. In one state, 6 groups join records verified as
  different places and 62 have members whose common identity the matcher did not establish; 61 are not yet
  adjudicated. The ledger is in the audit files.
- The SIRUTA publisher file was unreachable; a public mirror of the S1 2025 edition was used and checked code by code
  against the official INS locality service.

### Reproduce

The registers and Wikidata responses were saved on 8 October 2026 with their URLs and SHA-256 hashes. Two steps,
both kept with the project's audit files: the preparer and matcher reproduce the matcher output, then
`assemble_final.py` applies the 464 reviewed decisions (`review_overlay.json`, each checked against the data
before it is applied) and regenerates the ledger, the counts and the final report. To check a matcher change, look up its official code in
the register linked above and the item carrying that code; a reviewed change cites its evidence in the overlay.

## China, Russia, the United States and the United Kingdom

**Before:** in `CN.json`, `RU.json`, `US.json` and `GB.json`, 610, 337, 639 and 316 pairs of neighbouring records
shared one `wikiDataId` (origin/master f96a556e).

### Method

The batch-2 matcher and its review safeguards, with each country's official register: provincial administrative-division
code tables for China (P442; eight provinces retrievable: Beijing, Liaoning, Jilin, Fujian, Hunan, Hainan, Chongqing,
Ningxia), Rosstat OKTMO and OKATO for Russia (P764, P721), the Census Gazetteer GEOID and GNIS ids for the US (P774,
P590) and ONS codes and place names for the UK (P836). The matcher replaces an id only when the record's exact official
name in its state and level, the item's active code, its label, type and a point within 5 km all agree, and the old item
is shown to be another place; a village never takes its municipality's item and related identities (capital, seat,
redirect) are kept. Of the 519 changes, 504 pass these automatic gates and 15 are review decisions. A held id is cleared when its item is verified by official code for a record in another state or country and lies
over 5 km away (386), or when review showed the item is another place (14).

Review then decided 31 ids by hand, separately from the gates above and each with its own cited sources: 2 Russian
replacements that had picked a nearby namesake keep their original id, Essoyla gets the verified settlement, and 28
links already wrong on master are fixed. These override the related-identity rule where review proved it wrong, for
example a district that carried its seat town's item within 5 km: 14 replaced
(a district's own item instead of its seat, a village instead of the surrounding town) and 14 cleared (an item for
another province, a disambiguation page, a village's item on a police-department record). Each is listed with its sources in the audit
report.

### Results

| Country | Changed | Cleared | Held | Neighbouring pairs sharing an id |
| --- | --- | --- | --- | --- |
| CN | 8 | 30 | 4,078 | 610 -> 576 |
| RU | 59 | 86 | 3,739 | 337 -> 191 |
| US | 429 | 183 | 2,078 | 639 -> 77 |
| GB | 23 | 101 | 2,462 | 316 -> 192 |

519 ids changed, 400 wrong links cleared (pending a verified replacement), 12,357 held. China stays mostly held: only eight
provincial code tables could be retrieved, and the national list was unavailable.

### Known limitations

- 12,357 held records keep their id; China most of all (4,078), then the UK and Russia, where many records are
  below the level their register covers.
- 876 groups still share an id: 10 the same place in two records, 698 across states with unresolved members
  (2 holding a verified identity), 168 in one state with identity not established. Ledger in the audit files.

### Reproduce

Registers and Wikidata responses were saved on 8 October 2026 with URLs, editions and SHA-256 hashes; the matcher writes
the v1 files and the assembler the final manifest, ledger and counts, kept with the project's audit files.

## Australia, India, the Philippines and Turkey

**Before:** in `AU.json`, `IN.json`, `PH.json` and `TR.json`, 1,953 pairs of neighbouring records shared one `wikiDataId`.

### Method

The batch-3 matcher and its review safeguards, with each country's official code on Wikidata: ABS ASGS 2021 suburb
and locality (SAL) and LGA codes for Australia (P10112), checked against the Composite Gazetteer of Australia; Census
2011 town and village codes for India (P5578); PSGC for the Philippines (P988); and Turkey's address-register province,
district, neighbourhood and village codes (P14358, P14366, P12883, P13588). The matcher replaces an id only when the
record's exact official name in its state and level, the item's active code, its label, type and a point within 5 km
all agree, and the old item is shown, by its own official code, to be another place; a village never takes its
district's item and related identities (capital, seat, redirect) are kept. A held id is cleared only when its item is
verified by official code for a record in another state and lies over 5 km away (111); each clear names that record.
Of the 400 changes, 365 pass these automatic gates.

Review then decided 38 ids by hand, separately from the gates and each with its own sources: the automatic match
for Muratpaşa had taken the district's item for the town, and 37 links already wrong on master are fixed, 34
replaced (a town's own item instead of its district's, Jaipur city instead of the district, suburbs that carried another
state's suburb such as Araluen NT with Applecross WA) and 3 cleared (a village carrying a merged item, and two Turkish
towns carrying a district item 450 km away). Each is listed with its sources in the audit report.

### Results

| Country | Changed | Cleared | Held | Neighbouring pairs sharing an id |
| --- | --- | --- | --- | --- |
| AU | 374 | 109 | 1,348 | 782 -> 296 |
| IN | 5 | 3 | 4,327 | 604 -> 597 |
| PH | 0 | 0 | 4,544 | 191 -> 191 |
| TR | 21 | 2 | 963 | 376 -> 356 |

400 ids changed and 114 wrong links cleared (pending a verified replacement), most in Australia; 11,182 held.

### Known limitations

- The Philippines is held entirely: PSA's PSGC workbook returned HTTP 403 and its API needs a token, so no register
  bytes were verified.
- India's census codes are from 2011 and the current local-body codes (LGD) sit behind a CAPTCHA; Turkey's register
  edition is 31 December 2021. Both stay mostly held.
- 1486 groups still share an id: 1216 across states (13 holding a verified identity) and 270 in one state, identity not established. Ledger in the audit files.

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/BR.json`, `DE.json`, `ES.json`, `AT.json` — `wikiDataId` corrected on 2,432, 1,087,
  1,114 and 767 records
- `contributions/cities/JP.json`, `NL.json`, `RO.json`, `PL.json` — `wikiDataId` corrected on 196, 130,
  311 and 290 records, cleared on 131, 212, 38 and 44
- `contributions/cities/CN.json`, `RU.json`, `US.json`, `GB.json` — `wikiDataId` corrected on 8, 59,
  429 and 23 records, cleared on 30, 86, 183 and 101
- `contributions/cities/AU.json`, `IN.json`, `TR.json` — `wikiDataId` corrected on 374, 5 and
  21 records, cleared on 109, 3 and 2
- `contributions/cities/FR.json` — `wikiDataId` corrected on 4,597 records
- `bin/scripts/fixes/france_fix_copyforward_wikidataids.py` — the matcher
- `bin/scripts/fixes/france_fix_copyforward_wikidataids.report.json` — blanks and conflict
- `bin/scripts/fixes/test_france_fix_copyforward_wikidataids.py` — tests for the mid-run edit abort, the
  reviewed decisions outside the groups and idempotency (no network)
