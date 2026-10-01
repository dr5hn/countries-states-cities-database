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
- The script writes nothing if FR.json changes in any way while it runs (a record added, removed, reordered, or
  edited in its id, name, department, coordinates, population or `wikiDataId`), because conflict resolution reads
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
python3 -m unittest bin/scripts/fixes/test_france_fix_copyforward_wikidataids.py   # tests, no network
```

Wikidata lookups are cached in `$CSC_CACHE_DIR` (default `<tmp>/csc-copyforward-fr`).

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/FR.json` — `wikiDataId` corrected on 4,597 records
- `bin/scripts/fixes/france_fix_copyforward_wikidataids.py` — the matcher
- `bin/scripts/fixes/france_fix_copyforward_wikidataids.report.json` — blanks and conflict
- `bin/scripts/fixes/test_france_fix_copyforward_wikidataids.py` — tests for the mid-run edit abort, the
  reviewed decisions outside the groups and idempotency (no network)
