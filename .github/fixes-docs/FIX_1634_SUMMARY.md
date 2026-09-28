# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Review history

This fix went through two independent Codex reviews. Each round's confirmed problems are kept as a
regression test, and all of them now pass.

| Round | Finding | Fix |
|---|---|---|
| 1 (v1) | 134 correct IDs removed: v1 required an exact name match and never let a record keep its own ID (e.g. *El Capulín (La Nueva Pochota)* lost an ID whose entity, "El Capulín", sits 1 m away) | Verify each record's existing ID before re-matching (below) — **134/134 now kept** |
| 2 (v2) | 8 further correct IDs removed: saint-name and honorific name forms (*Apoala* = "Santiago Apoala", *Mixquiahuala de Juárez* = "Mixquiahuala"), and town records (*Medellín*, *Ocuilan*) keeping their municipality's ID instead of the municipality records | Recognise those naming conventions; the municipality record now wins — **8/8 now kept** |

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

When records of both kinds (town and municipality) verify the same ID, the one whose `type` matches the
entity keeps it and the other is re-matched.

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
| Existing ID verified and kept | 1,408 | 478 | **1,886** |
| New verified ID | 2,750 | 72 | **2,822** |
| ID removed | 447 | 56 | **503** |
| **Records in duplicate groups** | | | **5,211** |

- Shared-ID groups: **1,938 → 11** (the 11 are genuine duplicate records, see below)
- Records changed: **3,325**, only the `wikiDataId` field; record count unchanged at 9,321
- Records with a `wikiDataId`: 9,321 → 8,818
- **428 of the 503 removed IDs point more than 60 km away** — beyond even the municipality limit
- New town IDs: median 0.15 km from the record, maximum 2.8 km; new municipality IDs: up to 49 km
  (Mazapil, 12,139 km²)

## Verification

- **Regression tests:** round-1 false removals **134/134** kept; round-2 false removals **8/8** kept.
- *Medellín* (72061) and *Ocuilan* (72470), typed `city`, no longer hold their municipality's ID; *Ocuilan*
  now points at Q55974788, "Ocuilan de Arteaga, seat of Ocuilan municipality".
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

**Type mismatches restored, not re-audited.** Hundreds of kept IDs link a record to the other kind of place
— mostly a record typed `adm2` linked to its seat town. Many towns in `MX.json` are typed `adm2`, so this is
the original 2019 link, restored as it was.

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
- A few cases the reviews could not settle either way: *Ahuatempan* and *Jaltepetongo* (town records) keep
  their municipality's ID and *Pichátaro* (a municipality record) keeps its town's ID, as original links like
  the other type mismatches; *Mina* and *Tlapanaloya* are removed.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method carries over, but each
country needs its own place-type codes and naming conventions checked first.

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 3,325 records.
