# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Review history

This fix went through four independent Codex reviews. Every confirmed finding is kept as a regression test,
and all of them pass.

| Round | Finding | Fix | Test |
|---|---|---|---|
| 1 | Correct IDs removed: exact-name matching, and records never allowed to keep their own ID (*El Capulín (La Nueva Pochota)* lost an entity 1 m away) | Verify each record's existing ID before re-matching | 134/134 |
| 2 | More removed: saint-name and honorific forms (*Apoala* = "Santiago Apoala", *Mixquiahuala de Juárez* = "Mixquiahuala") | Recognise those naming conventions | 8/8 |
| 3 | The `type` field is wrong in both directions, so trusting it swapped town and municipality (*Medellín* is the municipality, *Medellín de Bravo* its seat town) | Decide by the municipality's seat town (P36) and record position | 9/9 |
| 4 | Still trusting `type` for lone records: 24 records typed `city` are really municipalities and were moved to their seat towns | Decide a record's kind from its **GeoNames provenance** | 25/25 |

## Method

Every change is checked against Wikidata individually. Nothing is inferred from the existing (wrong) IDs.

### What kind of place is each record?

`MX.json`'s `type` field is unreliable: **947 records** say the opposite of their source. The 2019 import came
from GeoNames, so each record is matched to the GeoNames entry at its coordinates (within 25 m, preferring an
entry with the same name) and takes its kind from that entry — **ADM2 → municipality, PPL… → town**. This
covers 5,973 records; the rest fall back to `type`.

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
- a record that is itself a municipality is never moved to a town, and records whose names reduce to the
  same form (*Ciudad General Terán* / *General Terán Nuevo León*) are one place entered twice and not split.

### 2. Re-match the rest

Look up the record's name forms among Wikidata labels and aliases in Mexico. A candidate must be the right
kind for the record, have self-consistent coordinates, and sit within 3 km (towns) or within 60 km in the same
state (municipalities). Same-named candidates in **different municipalities** → left blank rather than
guessed. No ID is handed to a second record.

### 3. Remove the ID when nothing verifies

A blank `wikiDataId` is better than one pointing at a different place.

## Results

| Outcome | Towns & others | `adm2` | Total |
|---|---:|---:|---:|
| Existing ID verified and kept | 1,365 | 423 | **1,788** |
| New verified ID (incl. 107 moved to their seat town) | 2,801 | 149 | **2,950** |
| ID removed | 439 | 34 | **473** |
| **Records in duplicate groups** | | | **5,211** |

- Shared-ID groups: **1,938 → 12** (the 12 are genuine duplicate records, see below)
- Records changed: **3,423**, only the `wikiDataId` field; record count unchanged at 9,321
- Records with a `wikiDataId`: 9,321 → 8,848
- **408 of the 473 removed IDs point more than 60 km away** — beyond even the municipality limit

## Verification

- **Regression tests:** round 1 **134/134**, round 2 **8/8**, round 3 **9/9**, round 4 **25/25**.
- Town/municipality pairs resolved by provenance: *Medellín* (GeoNames ADM2) keeps municipality Q2541899,
  *Medellín de Bravo* (PPLA2, population 2,725) gets its seat town Q6008533; *Ocuilan* keeps Q3308528,
  *Ocuilan de Arteaga* gets Q55974788; *Coyotepec* keeps Q5180099 and *San Vicente Coyotepec* keeps its
  town Q61296185.
- *San Andrés Calpan* (typed `adm2`) is the GeoNames **town** (PPLA2, population 7,161 exact), so it gets its
  seat-town entity Q20133184 rather than the Calpan municipality.
- *Condémbaro* gets Q61263614 (Tancítaro), not Q20276537, whose coordinates are 92 km apart; *Barrio Cuarto
  (La Loma)* gets Q49861414 ("Barrio Cuarto", alias "La Loma"), not an entity merging La Loma and La Trampa.

## Found along the way

**Wrong `type` values (947 records).** GeoNames says 635 records typed `adm2` are towns and 312 typed `city` or
`section` are municipalities. The IDs here follow the real kind; the `type` field itself should be corrected
separately.

**Duplicate records (12 pairs).** Both records of each pair verify the same entity, so both keep it; they
should be merged separately. Eleven are a later Nuevo León batch (`id` 149xxx) re-adding existing places:
Agualeguas, Apodaca, Benito Juárez, General Escobedo, General Terán, Sabinas Hidalgo, Doctor Coss, Iturbide,
Jardines de la Silla, Linares, Parás. The twelfth is *Huixquilucan* / *Huixquilucan de Degollado*
(Estado de México).

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

- **14 removed IDs sit within 1 km** of the record but could not be verified mechanically, several of them
  deliberately (different sectors, old vs new town, possible barrio): Carretas, Cañada, Gustavo Adolfo Madero,
  La Isla Km 10, Mazamitlongo, Monclova Segundo Sector, Montenegro la Lana, Necaxa, Nuevo Sitalá, Pozos de
  Gamboa, San Gaspar Tonatico, San Pedro Mixtepec, Tepuxtepec, Venustiano Carranza.
- **10 seat-town moves have no GeoNames match** and rely on the record's name and position (each within
  0.4 km of the seat town): Chapantongo, Jaltepetongo, San Juan Atepec, San Martín de los Canseco, Santa María
  Alotepec, Santo Domingo Chihuitán, Santo Domingo Petapa, Tamazola, Taretán, Teococuilco de Marcos Pérez.
- *San Carlos* (73456, Tabasco) keeps Q20136621 on coordinate identity, but that entity is labelled "Caobal"
  and described as "bad geoname 3519588" — identity unresolved.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method carries over, but each
country needs its own place-type codes, naming conventions and GeoNames dump checked first.

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 3,423 records.
