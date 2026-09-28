# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Review history

This fix went through five independent Codex reviews. Every confirmed finding is kept as a regression test,
and all of them pass.

| Round | Finding | Fix | Test |
|---|---|---|---|
| 1 | Correct IDs removed: exact-name matching, and records never allowed to keep their own ID (*El Capulín (La Nueva Pochota)* lost an entity 1 m away) | Verify each record's existing ID before re-matching | 134/134 |
| 2 | More removed: saint-name and honorific forms (*Apoala* = "Santiago Apoala", *Mixquiahuala de Juárez* = "Mixquiahuala") | Recognise those naming conventions | 8/8 |
| 3 | The `type` field is wrong in both directions, so trusting it swapped town and municipality (*Medellín* is the municipality, *Medellín de Bravo* its seat town) | Decide by the municipality's seat town (P36) and record position | 9/9 |
| 4 | Still trusting `type` for lone records: 24 records typed `city` are really municipalities and were moved to their seat towns | Decide a record's kind from its **GeoNames provenance** | 25/25 |
| 5 | 3 IDs left blank that were findable: an accent variant (*San Damián Texoloc* vs "Texóloc"), a GeoNames entry moved 178 m (*Ciudad Cerralvo*), and a town record outside the groups holding its municipality's ID (*Polotitlán*) | Unaccented lookups; same-name GeoNames entry within 250 m; move such town records to their seat town; align duplicate copies with their original | 5/5 |

## Method

Every change is checked against Wikidata individually. Nothing is inferred from the existing (wrong) IDs.

### What kind of place is each record?

`MX.json`'s `type` field is unreliable: **1,543 records** say the opposite of their source. The 2019 import
came from GeoNames, so each record is matched to its GeoNames entry — a same-name entry within 250 m first
(GeoNames sometimes moves a point slightly), otherwise the only kind of entry within 25 m (ignoring
neighbourhood, historical and abandoned entries) — and takes its kind from it: **ADM2 → municipality,
PPL… → town**. This covers 8,493 records; the rest fall back to `type`.

### 1. Verify each record's existing ID first

A record keeps its current `wikiDataId` when the entity is a real place (settlement, neighbourhood,
municipality or Mexico City borough — never a river, hill, school…) and either:

- **Coordinate identity:** one of the entity's coordinates is within **10 m** of the record. A copied-forward
  ID belongs to the *previous* row's place, so it cannot land on this record by chance.
- **Name match:** a form of the record's name matches a label or alias, and the entity sits within **3 km**
  (towns) or within **60 km and in the same state** (municipalities, whose coordinates are centroids).
  Name forms: as written; without the bracketed part; the bracketed alternate; without "Ciudad (de)",
  "Ejido" or a trailing state name; ordinals spelled out; within two letters when within 1 km; and four
  Mexican conventions — a leading saint name (*Apoala* ↔ "Santiago Apoala"), a saint name on a municipality
  record (*San Andrés Calpan* ↔ "Calpan"), an honorific "de Surname" (*Medellín de Bravo* ↔ "Medellín"), and
  a bare saint name plus one word (*San Hipólito* ↔ "San Hipólito Xochiltenango"). Not treated as the same
  place: "Nuevo X" vs "X", "X Primer/Segundo Sector", "Salto de X", "de la/los …" phrases.
- **Guards:** a record named "Barrio Cuarto (La Loma)" does not match an entity calling itself "Barrio Cuarto
  (La Trampa)"; an entity whose own coordinates disagree (it may merge two places) is trusted only if it is
  named like the record and one of its coordinates is within 1 km.

**Town or municipality?** Using each record's real kind and the municipality's seat town (Wikidata P36):

- a **town** record holding a municipality ID moves to that municipality's seat town when it is within 3 km;
- when two differently named records verify one municipality, the town nearest the seat town gets the seat
  town and the other keeps the municipality;
- a record that is itself a municipality is never moved to a town;
- a town record **outside** the duplicate groups that holds its municipality's ID (*Polotitlán de la
  Ilustración*) moves to the seat town, so the municipality ID can go to the municipality record
  (3 records outside the groups change this way).

### 2. Re-match the rest

Look up the record's name forms, as written and unaccented, among Wikidata labels and aliases in Mexico. A
candidate must be the right kind for the record and sit within 3 km (towns) or within 60 km in the same state
(municipalities). Candidates with self-consistent coordinates are preferred; one whose coordinates disagree is
used only if nothing else qualifies and one of its coordinates is within 1 km. Same-named candidates in
**different municipalities** → left blank rather than guessed. No ID is handed to a second record.

**Duplicate copies.** A later batch re-added some places. Two records in the same shared-ID group, same state
and same name form, within 3 km and without contradicting populations, are one place entered twice: the copy
takes the original's ID, and the pair is listed for merging.

### 3. Remove the ID when nothing verifies

A blank `wikiDataId` is better than one pointing at a different place.

## Results

| Outcome | Towns & others | `adm2` | Total |
|---|---:|---:|---:|
| Existing ID verified and kept | 1,366 | 359 | **1,725** |
| New verified ID (incl. 165 moved to their seat town) | 2,849 | 230 | **3,079** |
| ID removed | 390 | 20 | **410** |
| **Records in duplicate groups** | | | **5,211** |

- Shared-ID groups: **1,938 → 13** (the 13 are genuine duplicate records, see below)
- Records changed: **3,489** (3 of them outside the duplicate groups), only the `wikiDataId` field; record
  count unchanged at 9,321
- Records with a `wikiDataId`: 9,321 → 8,911
- **357 of the 410 removed IDs point more than 60 km away** — beyond even the municipality limit

## Verification

- **Regression tests:** round 1 **134/134**, round 2 **8/8**, round 3 **9/9**, round 4 **25/25**, round 5 **5/5**.
- Town/municipality pairs resolved by provenance: *Medellín* (GeoNames ADM2) keeps municipality Q2541899,
  *Medellín de Bravo* (PPLA2, population 2,725) gets its seat town Q6008533; *Ocuilan* keeps Q3308528,
  *Ocuilan de Arteaga* gets Q55974788; *Coyotepec* keeps Q5180099 and *San Vicente Coyotepec* keeps its
  town Q61296185.
- *San Andrés Calpan* (typed `adm2`) is the GeoNames **town** (PPLA2, population 7,161 exact), and *Ciudad
  General Terán* is the town (PPL, population 6,333 exact; the municipality's entry is 19 km away), so both get
  their seat-town entities (Q20133184, Q27769173) rather than the municipality their `type` suggested.
- *Polotitlán* (GeoNames ADM2) gets municipality Q3308505, freed by moving *Polotitlán de la Ilustración*
  (PPLA2, a record outside the groups) to its seat town Q104154055; *San Damián Texoloc* gets Q61288561
  ("San Damián Texóloc", found via its unaccented alias); *Ciudad Cerralvo* gets Q61127668.
- *Condémbaro* gets Q61263614 (Tancítaro), not Q20276537, whose coordinates are 92 km apart; *Barrio Cuarto
  (La Loma)* gets Q49861414 ("Barrio Cuarto", alias "La Loma"), not an entity merging La Loma and La Trampa.

## Found along the way

**Wrong `type` values (1,543 records).** GeoNames says 1,231 records typed `adm2` are towns and 312 typed
`city` or `section` are municipalities. The IDs here follow the real kind; the `type` field itself should be
corrected separately.

**Duplicate records (13 pairs).** Both records of each pair describe the same place and hold the same ID;
they should be merged separately. Twelve are a later Nuevo León batch (`id` 149xxx) re-adding existing places,
often with identical populations: Agualeguas, Apodaca, Benito Juárez, General Escobedo, General Terán, Sabinas
Hidalgo, Doctor Coss, Iturbide, Jardines de la Silla, Linares, Parás, Villaldama. The thirteenth is
*Huixquilucan* / *Huixquilucan de Degollado* (Estado de México).

**Pre-existing state errors.** These records match their entity by name and location, but are filed under
the wrong state. Not changed here:

| Record | Filed under | Entity is in |
|---|---|---|
| 76028 Villa Lázaro Cárdenas | Veracruz | Puebla |
| 72388 Nuevo Ixcatlán | Oaxaca | Veracruz |
| 75900 Urén | Estado de México | Michoacán |
| 73759 San José Comalco | Morelos | Estado de México |
| 68918 Cerritos de Cárdenas | Morelos | Estado de México |
| 74104 San Martín Peras | Guerrero | Oaxaca |
| 74131 San Mateo Otzacatipan | Morelos | Estado de México |

## Known limitations

- **13 removed IDs sit within 1 km** of the record but could not be verified mechanically, several of them
  deliberately (different sectors, old vs new town, possible barrio): Carretas, Cañada, Gustavo Adolfo Madero,
  La Isla Km 10, Mazamitlongo, Monclova Segundo Sector, Montenegro la Lana, Necaxa, Nuevo Sitalá, Pozos de
  Gamboa, San Gaspar Tonatico, San Pedro Mixtepec, Tepuxtepec.
- **3 seat-town moves have no GeoNames match** and rely on the record's name and position (each within
  0.4 km of the seat town): Jaltepetongo, San Martín de los Canseco, Tamazola.
- *San Carlos* (73456, Tabasco) keeps Q20136621 on coordinate identity, but that entity is labelled "Caobal"
  and described as "bad geoname 3519588" — identity unresolved.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method carries over, but each
country needs its own place-type codes, naming conventions and GeoNames dump checked first.

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 3,489 records.
