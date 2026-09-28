# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Review history

This fix went through three independent Codex reviews. Each round's confirmed problems are kept as a
regression test, and all of them now pass.

| Round | Finding | Fix |
|---|---|---|
| 1 (v1) | 134 correct IDs removed: v1 required an exact name match and never let a record keep its own ID (e.g. *El Capulín (La Nueva Pochota)* lost an ID whose entity, "El Capulín", sits 1 m away) | Verify each record's existing ID before re-matching (below) — **134/134 now kept** |
| 2 (v2) | 8 further correct IDs removed: saint-name and honorific name forms (*Apoala* = "Santiago Apoala", *Mixquiahuala de Juárez* = "Mixquiahuala"), and municipality pairs (*Medellín de Bravo*, *Ocuilan de Arteaga*) | Recognise those naming conventions — **8/8 now kept** |
| 3 | The `type` field is wrong in both directions, so letting the record whose `type` matches own the municipality swapped identities (*Medellín* is the municipality, *Medellín de Bravo* its seat town); 4 town records restored to a municipality ID although a seat-town entity exists | Use the municipality's seat town (Wikidata P36) and record position, not `type`, to decide who is the town — **9/9 expected outcomes**; 75 town records now point at their seat town |

## Method

Every change is checked against Wikidata individually. Nothing is inferred from the existing (wrong) IDs.

### 1. Verify each record's existing ID first

A record keeps its current `wikiDataId` when the entity is a real place (settlement, neighbourhood,
municipality or Mexico City borough — never a river, hill, school…) and either:

- **Coordinate identity:** one of the entity's coordinates is within **10 m** of the record. A copied-forward
  ID belongs to the *previous* row's place, so it cannot land on this record by chance. If the entity's own
  coordinates disagree with each other (it may merge two places), a name match is also required.
- **Name match:** a form of the record's name matches a label or alias, and the entity sits within **3 km**
  (towns) or within **60 km and in the same state** (municipalities, whose coordinates are centroids, not
  seats). Name forms tried: as written; without the bracketed part; the bracketed alternate itself; without
  "Ciudad (de)", "Ejido" or a trailing state name; ordinals spelled out ("2da." → "segunda"); within two
  letters when the entity is within 1 km; and these Mexican naming conventions:
  - the entity adds a leading saint name — *Apoala* ↔ "Santiago Apoala";
  - the record adds a saint name, for municipalities only — *San Andrés Calpan* ↔ "Calpan Municipality";
  - either adds an honorific "de Surname" — *Medellín de Bravo* ↔ "Medellín";
  - a bare saint name plus one word — *San Hipólito* ↔ "San Hipólito Xochiltenango".

  Deliberately **not** treated as the same place: "Nuevo X" vs "X", "X Primer/Segundo Sector", "Salto de X",
  "de la/los …" phrases, and a saint-named town record vs a bare town entity (it may be a barrio).
- **Sibling guard:** "Barrio Cuarto (La Loma)" does not match an entity that calls itself
  "Barrio Cuarto (La Trampa)" — the brackets name different places.

**Town or municipality?** `MX.json`'s `type` is unreliable in both directions (many towns are typed
`adm2`; some municipalities are typed `city`), so position decides, using the municipality's seat town
(Wikidata *capital*, P36):

- when two records with **different names** verify the same municipality, the one within 3 km of its
  seat town, and nearest to it, gets the seat town; the other keeps the municipality (*Medellín de Bravo*
  → the town "Medellín", *Medellín* → the municipality);
- when a single town-typed record holds a municipality ID and the seat town is within 3 km, it gets the
  seat town instead (*Tamasopo*, *Ahuatempan*, *Jaltepetongo* …);
- records whose names reduce to the same form (*Ciudad General Terán* / *General Terán Nuevo León*) are
  one place entered twice, so they are not split.

Otherwise, the record whose `type` matches the entity keeps it and the other is re-matched.

### 2. Re-match the rest

Look up the record's name forms among Wikidata labels and aliases in Mexico. A candidate must be the right
kind for the record (`adm2` → municipality; `section` → settlement or neighbourhood; otherwise settlement),
have self-consistent coordinates, and sit within 3 km (towns) or within 60 km in the same state
(municipalities). If same-named candidates fall in **different municipalities**, the record is left blank
rather than guessed. No ID is handed to a second record.

### 3. Remove the ID when nothing verifies

A blank `wikiDataId` is better than one pointing at a different place.

## Results

| Outcome | Towns & others | `adm2` | Total |
|---|---:|---:|---:|
| Existing ID verified and kept | 1,338 | 476 | **1,814** |
| New verified ID (incl. 75 moved to their seat town) | 2,820 | 74 | **2,894** |
| ID removed | 447 | 56 | **503** |
| **Records in duplicate groups** | | | **5,211** |

- Shared-ID groups: **1,938 → 11** (the 11 are genuine duplicate records, see below)
- Records changed: **3,397**, only the `wikiDataId` field; record count unchanged at 9,321
- Records with a `wikiDataId`: 9,321 → 8,818
- **429 of the 503 removed IDs point more than 60 km away** — beyond even the municipality limit
- New town IDs: median 0.15 km from the record, maximum 2.8 km; new municipality IDs: up to 49 km
  (Mazapil, 12,139 km²)

## Verification

- **Regression tests:** round 1 **134/134**, round 2 **8/8**, round 3 **9/9** expected outcomes.
- *Medellín* (72061) keeps the municipality Q2541899 and *Medellín de Bravo* (72062) gets its seat town
  Q6008533 (0.3 km); *Ocuilan* (72470) keeps municipality Q3308528 and *Ocuilan de Arteaga* (72471) gets
  Q55974788 — the record's position and population match the town, whatever its `type` says.
- *Ahuatempan*, *Jaltepetongo*, *Santa Lucía* and *Tamazola* point at their seat towns (Q20232027,
  Q61276667, Q61275583, Q20283868) instead of the municipalities; a sample of the other seat-town moves
  all point at the entity described as the "cabecera" (seat) of that municipality.
- *Monclova Segundo Sector*, *San Gaspar Tonatico* and *Necaxa* stay unmatched, by design.
- *Condémbaro* (Michoacán) gets Q61263614, the Tancítaro locality, not Q20276537, whose coordinates are 92 km
  apart.
- *Barrio Cuarto (La Loma)* moves off an entity that merges La Loma with La Trampa, onto Q49861414
  ("Barrio Cuarto", alias "La Loma", 0.5 km away).
- The round-2 review sampled the new IDs (30 towns, 15 municipalities incl. the farthest) and found no
  wrong-place assignments, and found no wrong-place links among 40 IDs kept on coordinates/spelling or 25
  kept despite a type mismatch.

## Found along the way

**Duplicate records (11 pairs, all Nuevo León).** A later batch (`id` 149xxx) re-added places that already
existed, often with a " Nuevo León" suffix or without "Ciudad". Both records of each pair verify the same
entity, so both keep it; the duplicate records should be merged separately:
Agualeguas, Apodaca, Benito Juárez, General Escobedo, General Terán, Sabinas Hidalgo, Doctor Coss, Iturbide,
Jardines de la Silla, Linares, Parás.

**Records whose `type` looks wrong.** Hundreds of records typed `adm2` keep the ID of the town they
actually describe (e.g. *Pichátaro*, a town in Tingambato municipality, typed `adm2`). The ID is right; the
`type` should be corrected in a separate pass.

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

- **19 removed IDs sit within 1 km** of the record but could not be verified mechanically, several of them
  deliberately (different sectors, old vs new town, possible barrio): Carretas, Cañada, Chipilo de Francisco
  Javier Mina, Gustavo Adolfo Madero, Gutiérrez Zamora, Huixquilucan de Degollado, La Isla Km 10,
  Mazamitlongo, Monclova Segundo Sector, Montenegro la Lana, Necaxa, Nuevo Sitalá, Pozos de Gamboa, Río
  Blanco, San Gaspar Tonatico, San Pedro Mixtepec, Tepuxtepec, Tres de Mayo, Venustiano Carranza.
- **San Carlos (73456, Tabasco)** keeps Q20136621 on coordinate identity, but that entity is labelled
  "Caobal" and described on Wikidata as "bad geoname 3519588". Identity unresolved; worth a human look.
- *Mina* and *Tlapanaloya* are removed; the reviews could not settle them either way.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method carries over, but each
country needs its own place-type codes and naming conventions checked first.

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 3,397 records.
