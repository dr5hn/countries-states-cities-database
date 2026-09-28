# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Revision history

The first version of this fix (v1) was reviewed by Codex, which found it **removed correct IDs**: of 169
removals it checked, 134 had carried the right entity (7 of 30 in a plain random sample). v1 required an
exact name match, so a record such as *El Capulín (La Nueva Pochota)* lost an ID whose entity, labelled
"El Capulín", sits 1 metre away. This version (v2) rebuilds the method around verifying existing IDs first,
and uses Codex's 134 confirmed cases as a regression test: **all 134 are now kept**.

## Method (v2)

Every change is checked against Wikidata individually. Nothing is inferred from the existing (wrong) IDs.

### 1. Verify each record's existing ID first

A record keeps its current `wikiDataId` when the entity is a real place (settlement, neighbourhood,
municipality or Mexico City borough — never a river, hill, school…) and either:

- **Coordinate identity:** one of the entity's coordinates is within **10 m** of the record. A copied-forward
  ID belongs to the *previous* row's place, so it cannot land on this record by chance. If the entity's own
  coordinates disagree with each other (it may merge two places), a name match is also required.
- **Name match:** a form of the record's name matches a label or alias — the name as written, without its
  bracketed part, the bracketed alternate itself, without "Ciudad (de)", "Ejido" or a trailing state name,
  with ordinals spelled out ("2da." → "segunda"), or within two letters when the entity is within 1 km. The
  entity's coordinates must agree with each other, and it must sit within **3 km** (towns) or within
  **60 km and in the same state** (municipalities, whose coordinates are centroids, not seats).
- **Sibling guard:** a record named "Barrio Cuarto (La Loma)" does not match an entity that calls itself
  "Barrio Cuarto (La Trampa)" — the brackets name different places.

When records of both kinds (town and municipality) verify the same ID, the one whose `type` matches the
entity keeps it and the other is re-matched.

### 2. Re-match the rest

Look up the record's name (plus the variants above, without the bracketed part) among Wikidata labels and
aliases in Mexico. A candidate must be the right kind for the record (`adm2` → municipality; `section` →
settlement or neighbourhood; otherwise settlement), have self-consistent coordinates, and sit within 3 km
(towns) or within 60 km in the same state (municipalities). If same-named candidates fall in **different
municipalities**, the record is left blank rather than guessed. No ID is handed to a second record.

### 3. Remove the ID when nothing verifies

A blank `wikiDataId` is better than one pointing at a different place.

## Results

| Outcome | Towns & others | `adm2` | Total |
|---|---:|---:|---:|
| Existing ID verified and kept | 1,399 | 469 | **1,868** |
| New verified ID | 2,749 | 72 | **2,821** |
| ID removed | 457 | 65 | **522** |
| **Records in duplicate groups** | | | **5,211** |

- Shared-ID groups: **1,938 → 11** (the 11 are genuine duplicate records, see below)
- Records changed: **3,343**, only the `wikiDataId` field; record count unchanged at 9,321
- Records with a `wikiDataId`: 9,321 → 8,799
- New town IDs: median **0.15 km** from the record, 90th percentile 0.43 km, maximum 2.8 km
- New municipality IDs: median 3.4 km, maximum 49 km (Mazapil, 12,139 km²)

## Verification

- **Codex regression:** all 134 confirmed false removals from the v1 review now keep their ID.
- **Condémbaro** (Michoacán) gets Q61263614, the Tancítaro locality — not Q20276537, whose coordinates are
  92 km apart and which Codex flagged.
- **Barrio Cuarto (La Loma)** moves off an entity that merges La Loma with La Trampa, onto Q49861414
  ("Barrio Cuarto", alias "La Loma", 0.5 km away).
- **Removals are overwhelmingly real:** for 481 of the 522, the removed ID's entity is more than 3 km from
  the record (median 316 km).

## Found along the way

**Duplicate records (11 pairs, all Nuevo León).** A later batch (`id` 149xxx) re-added places that already
existed, often with a " Nuevo León" suffix or without "Ciudad". Both records of each pair verify the same
entity, so both keep it; the duplicate records should be merged separately:
Agualeguas, Apodaca, Benito Juárez, General Escobedo, General Terán, Sabinas Hidalgo, Doctor Coss, Iturbide,
Jardines de la Silla, Linares, Parás.

**Type mismatches restored, not re-audited.** 425 kept IDs link a record to the other kind of place — mostly
a record typed `adm2` linked to its seat town. Many towns in `MX.json` are typed `adm2`, so this is the
original 2019 link, restored as it was.

**Pre-existing state errors.** Some records are filed under the wrong state (e.g. *San Martín Peras* under
Guerrero, entity in Oaxaca; *Cerritos de Cárdenas* under Morelos, entity in Estado de México). Not changed here.

## Known limitations

31 removed IDs sit within 1 km of the record but could not be verified mechanically, mostly because Mexican
localities are cited with and without their saint's name (*Apoala* / "Santiago Apoala") or old/new
qualifiers (*Necaxa* / "Nuevo Necaxa"). A looser rule would also join *Monclova Segundo Sector* to
"Monclova primer sector", so they are left blank for a human pass: Ahuatempan, Ahuehuetitlán, Apoala,
Carretas, Cañada, Chipilo de Francisco Javier Mina, Gustavo Adolfo Madero, Gutiérrez Zamora, Huixquilucan
de Degollado, Jaltepetongo, Jamiltepec, La Isla Km 10, Mazamitlongo, Mixquiahuala de Juarez, Monclova
Segundo Sector, Montenegro la Lana, Moyotzingo, Necaxa, Nopala de Villagran, Nuevo Sitalá, Ocuilan de
Arteaga, Pichátaro, Pozos de Gamboa, Río Blanco, San Gaspar Tonatico, San Hipólito, San Pedro Mixtepec,
Tepuxtepec, Tres de Mayo, Venustiano Carranza, Zacatepec.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method carries over, but each
country needs its own place-type codes checked first (the Mexico codes were verified against a known
municipality, Q49953734).

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 3,343 records.
