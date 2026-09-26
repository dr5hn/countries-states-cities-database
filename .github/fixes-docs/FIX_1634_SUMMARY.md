# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Method

Every change was checked against Wikidata individually. Nothing was inferred from the existing (wrong) IDs.

1. **Find each group's true owner.** A member keeps the shared ID only if (a) its name matches the
   entity's label, (b) it is the same kind of place, and (c) it sits close to the entity's coordinates.
2. **Re-match everyone else.** Each remaining record was looked up on Wikidata by exact name, restricted to
   Mexico (`P17` = Q96).
3. **Remove the ID** when nothing verifies. A blank `wikiDataId` is better than one that points at a
   different place.

### Thresholds come from the data, not guesses

For the owners confirmed in step 1, the record sat within **0.75 km** of Wikidata's coordinates 95% of the
time and within **2.9 km** 99% of the time; the 2019 import evidently took its coordinates from Wikidata.
So towns are matched within **3 km**.

Municipality entities are different: their coordinates are the centre of the whole municipality, not the
seat town the record uses, and are typically 5–30 km away. For `adm2` records the match therefore requires
**the same state** (the entity's `P131` must be the record's state) instead of a tight radius, with a 60 km
sanity cap. The largest accepted distances belong to very large municipalities (Mazapil, 12,139 km²:
49 km; Ramos Arizpe, 6,754 km²: 51 km).

### Safeguards

- **Right kind of place.** Town records only accept settlements (locality of Mexico, human settlement,
  village, town, city…). An earlier dry run without this rule matched two archaeological sites, a police
  station, a river, a beach, a mountain and an island that shared a town's name. `adm2` records only
  accept municipalities (`Q1952852`, labelled "X Municipality" / "Municipio de X" on Wikidata).
- **No new duplicates.** Candidates are assigned nearest-first, and a QID already held by any record is
  never handed out again. Post-fix, no QID in `MX.json` appears twice.
- **Stale-data guard.** Before writing, every targeted record's current `wikiDataId` was checked against the
  plan; any mismatch would have aborted the run.

## Results

| Outcome | `city` & others | `adm2` | Total |
|---|---:|---:|---:|
| Kept (verified owner) | 1,026 | 177 | **1,203** |
| New verified ID | 2,687 | 268 | **2,955** |
| ID removed (nothing verifiable) | 894 | 159 | **1,053** |
| **Records touched** | | | **5,211** |

- Duplicate-QID groups: **1,938 → 0**
- Records changed: 4,008 — the only field changed is `wikiDataId`
- Record count: 9,321 → 9,321
- Records with a `wikiDataId`: 9,321 → 8,268

Town matches: median distance 0.15 km, 90th percentile 0.44 km, maximum 2.82 km.

## Verification

- Every new town ID resolves to a settlement type; every new `adm2` ID to a municipality in the record's state.
- Random samples were read against Wikidata descriptions, e.g. *La Cruz del Palmar* (Guanajuato) →
  Q49997793 "town in Allende Municipality, Guanajuato" (0.07 km); *Tarimoro* (`adm2`) → Q4451992
  "Tarimoro Municipality, Guanajuato".
- Sampled removals were confirmed wrong, e.g. *La Rivera* (Baja California Sur) had carried
  "La Rinconada, Chiapas"; *Pino Suárez* (Hidalgo) had carried "Pinal de Amoles, Querétaro".

## Deliberately not done

- **Recovering the 1,053 removed IDs.** Many fail only on naming, e.g. *Ciudad Sabinas Hidalgo* vs
  Wikidata's "Sabinas Hidalgo", or parenthesised alternates such as *Vicente Guerrero (San Javier)*.
  Looser matching could recover some but raises the risk of a wrong match, so it's left for a follow-up.
- **State corrections.** Some records appear filed under the wrong state (e.g. *Tupátaro*'s coordinates and
  Wikidata entity are in Michoacán, but the record says Estado de México). Out of scope here.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method above carries over, but
each country needs its own municipality/settlement type codes checked first (the Mexico codes were
verified against a known municipality, Q49953734).

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 4,008 records.
