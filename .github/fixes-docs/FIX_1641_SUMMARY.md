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

### Method

Every record in a shared-QID group is matched again from scratch; nothing is inferred from the shared ID.
French cities are communes, and every commune item on Wikidata carries its **INSEE code** (P374), which starts
with the department number — the record's `state_code`. That gives a direct identity check, unlike Mexico.

1. **INSEE (6,149 records).** The item in the record's department whose French label is the record's name,
   within 5 km of the record. When a commune merger leaves several items on one code (the historic commune
   and the new one), the one without a dissolution date (P576) wins: *Aigre* gets the current commune
   Q60544458, not the pre-2019 Q1451759. 5,910 of these matches are within 1 km, all within 5 km.
2. **Named place nearby (208 records).** Otherwise: a settlement, neighbourhood or commune within 3 km whose
   label or alias, in any language, is the record's name. This catches:
   - renamed communes: *Cadillac* → Cadillac-sur-Garonne; *Cransac* (now Cransac-les-Thermes) and *Céreste*
     (now Céreste-en-Luberon) keep their existing IDs;
   - Catalan names: *Argelers* → Argelès-sur-Mer, *Banyuls de la Marenda* → Banyuls-sur-Mer;
   - neighbourhoods: 95 quartiers, mostly in Marseille, including "Marseille Endoume"-style names;
   - records filed under the wrong department (see below).

   Preference when several items match: the record's own QID; then an item whose French label *is* the name
   (the locality *Berck-Plage*, not the commune Berck that lists it as an alias; the former commune
   *Bienville*, not Eurville-Bienville); then a commune over other items such as GeoNames-generated stubs,
   current communes first, then the main item (most Wikipedia articles). "Quartiers prioritaires" —
   urban-policy zones that reuse a neighbourhood's name — are never chosen.
3. **Merged commune bearing its name (5 records).** Still nothing: the one commune in the department within
   3 km whose name starts with the record's name — *Tignieu* → Tignieu-Jameyzieu, *Veigy* → Veigy-Foncenex,
   *Cosnes* → Cosnes-et-Romain, *Porcieu* → Porcieu-Amblagnieu, *Les Ancizes* → Les Ancizes-Comps.
4. **Blank (39 records)** when nothing verifies.

One ID per place: a QID landing on two records is either one place entered twice (both within 3 km —
reported for merging) or a conflict, in which case the group record is blanked.

### Results

| Outcome | Records |
|---|---:|
| Existing ID verified and kept | **1,802** |
| New verified ID | **4,560** |
| ID removed | **39** |
| **Records in shared-QID groups** | **6,401** |

- Shared-QID groups: **2,036 → 1** (a genuine duplicate record, see below)
- Records changed: **4,599**, only the `wikiDataId` field; record count unchanged at 10,534
- Records with a `wikiDataId`: 10,079 → 10,040

### Verification

- After the fix, no QID is shared in FR.json except the one duplicate pair; rerunning the script changes nothing.
- 47 records are matched by position to a commune in another department. Their stored populations agree with
  the matched commune in 44 of the 45 that have both figures (*Évry*, filed under Yonne, has 51,900 — Évry in
  Essonne, not the village in Yonne). The exception, *Jumelles*, carries the population of the commune it merged
  into (Longué-Jumelles).
- The full list of blanks, the duplicate pair and the conflict is in
  `bin/scripts/fixes/france_fix_copyforward_wikidataids.report.json`.

### Found along the way

**Records filed under the wrong department (47).** Matched by name and coordinates to a commune in another
department — e.g. *Albens* (filed 74, in 73), *Évry* (89 → 91), *Vire* (71 → 14), *Pierrefitte-sur-Seine*
(95 → 93), and eight Maine-et-Loire villages filed under Loire-Atlantique. Not changed here.

**Departments stored as cities (19).** *Cantal*, *Charente-Maritime*, *Dordogne*, *Doubs*, *Département du
Vaucluse*, *Gers*, *Gironde*, *Haute-Marne*, *Manche*, *Mayenne*, *Nord*, *Pas-de-Calais*, *Sarthe*,
*Seine-et-Marne*, *Territoire de Belfort*, *Val-de-Marne*, *Var*, *Vosges*, *Yvelines* are department
names with `type: city`. Their IDs are removed; the records should probably be deleted separately.

**Duplicate record (1 pair).** *Beuville* (39990) is the former commune merged into *Biéville-Beuville* (40041);
both now hold Q317610.

### Known limitations

- **Commune 5–18 km from the record** (left blank): Boulazac, Buxerolles, Charmes-la-Grande, Louplande and
  five Corsican records (Furiani, Ghisonaccia, Lumio, Morosaglia, Oletta) — the record's coordinates are too far
  from the commune to confirm.
- **No item found:** Bourg de Joué-sur-Erdre, La Millère, La Page, La Valentine (Marseille quartiers), Mouret,
  Pietranera, Port à Binson, Pragoulin, Saint-Quentin-en-Yvelines; *Fouillard* has two same-named items;
  *Sarrola* is left blank because its commune belongs to *Sarrola-Carcopino*, 8.7 km away.

### Reproduce

```bash
python3 bin/scripts/fixes/france_fix_copyforward_wikidataids.py --dry-run   # plan + report only
python3 bin/scripts/fixes/france_fix_copyforward_wikidataids.py             # write FR.json
```

Wikidata lookups are cached in `$CSC_CACHE_DIR` (default `<tmp>/csc-copyforward-fr`).

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/FR.json` — `wikiDataId` corrected on 4,599 records
- `bin/scripts/fixes/france_fix_copyforward_wikidataids.py` — the matcher
- `bin/scripts/fixes/france_fix_copyforward_wikidataids.report.json` — blanks, duplicates, conflicts
