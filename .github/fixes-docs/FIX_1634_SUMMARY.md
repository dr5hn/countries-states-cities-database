# Fix Summary: Duplicate wikiDataIds in Mexico cities

## Issue Reference
**Original Issue:** [#1634](https://github.com/dr5hn/countries-states-cities-database/issues/1634) — Systemic duplicate wikiDataId across `contributions/cities/MX.json`

## Problem

In `contributions/cities/MX.json`, **5,211 records** fell into **1,938 groups** that each shared one
`wikiDataId`. 99% of the groups were runs of consecutive `id`s, which points to a 2019 import bug: when no
Wikidata match was found for a row, the previous row's ID was carried forward. The result was IDs such as
`Q1144317` (Ejutla de Crespo, Oaxaca) sitting on 11 different places across four states.

## Review history

This fix went through eight independent Codex reviews. Every confirmed finding is kept as a regression test,
and all of them pass.

| Round | Finding | Fix | Test |
|---|---|---|---|
| 1 | Correct IDs removed: exact-name matching, and records never allowed to keep their own ID (*El Capulín (La Nueva Pochota)* lost an entity 1 m away) | Verify each record's existing ID before re-matching | 134/134 |
| 2 | More removed: saint-name and honorific forms (*Apoala* = "Santiago Apoala", *Mixquiahuala de Juárez* = "Mixquiahuala") | Recognise those naming conventions | 8/8 |
| 3 | The `type` field is wrong in both directions, so trusting it swapped town and municipality (*Medellín* is the municipality, *Medellín de Bravo* its seat town) | Decide by the municipality's seat town (P36) and record position | 9/9 |
| 4 | Still trusting `type` for lone records: 24 records typed `city` are really municipalities and were moved to their seat towns | Decide a record's kind from its **GeoNames provenance** | 25/25 |
| 5 | 3 IDs left blank that were findable: an accent variant (*San Damián Texoloc* vs "Texóloc"), a GeoNames entry moved 178 m (*Ciudad Cerralvo*), and a town record outside the groups holding its municipality's ID (*Polotitlán*) | Unaccented lookups; same-name GeoNames entry within 250 m; move such town records to their seat town; align duplicate copies with their original | 5/5 |
| 6 | 4 wrong: *Carmen* left blank because its twin *El Carmen Nuevo León* (same population, 475 m) held the ID; *Estancia de Ánimas* and *Marín* left blank as ambiguous; *Venustiano Carranza* (renamed San Pedro Cahro) given its municipality. 1 unresolved: the two *Villaldama* records, 6.5 km apart, treated as one place | Share an ID with a verified twin; pick same-named places by GeoNames municipality; use GeoNames names when Wikidata links to the same GeoNames entry; resolve Wikidata redirects; duplicates only within 3 km | 11/11 (the 6 records, plus 5 settled by the new GeoNames checks) |
| 7 | 1 wrong of 113: *Pozos de Gamboa* kept Q20264912, an item mixing this town (point, GeoNames link) with Pozo Gamboa in Miguel Auza (parent, INEGI code). 3 blanks resolvable from GeoNames history and a municipal plan | The GeoNames-link rule rejects an item whose own municipality lies over 60 km from its point; 4 reviewed decisions | 4/4 |
| 8 | The 4 decisions confirmed. But the 60 km check is unsound (*Santa Rosalía* is 104 km from its own municipality's point in Mulegé), and *Villaldama Nuevo León*'s position is no evidence: it had the town record's exact coordinates until an undocumented 2025 move | Replace the distance check with an INEGI identity check; keep *Apetatitlán* by review (GeoNames files it under the wrong municipality); leave *Villaldama Nuevo León* blank | 6/6 |

## Method

Every change is checked against Wikidata individually. Nothing is inferred from the existing (wrong) IDs.

### What kind of place is each record?

`MX.json`'s `type` field cannot tell a town from its municipality: `adm2` marks a municipality's seat town
(GeoNames PPLA2) but also some municipalities themselves, and 310 municipality entries are typed `city`. The 2019
import came from GeoNames, so each record is matched to its GeoNames entry — an entry within 250 m whose name or
alternate name is the record's name first (GeoNames sometimes moves a point slightly, and lists a seat town
such as "San Miguel Ahuehuetitlán" with the short name "Ahuehuetitlán"), otherwise the only kind of entry
within 25 m (ignoring neighbourhood, historical and abandoned entries) — and takes its kind from it:
**ADM2 → municipality, PPL… → town**. This covers 8,692 records; the rest fall back to `type`.

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
- **Same GeoNames entry:** the record's GeoNames entry lists one of the entity's names **and** the entity
  links (P1566) to that very GeoNames entry, and the entity's INEGI locality code (P1976), when it has one,
  lies in that GeoNames entry's municipality — so an item mixing two places is rejected (Q20264912 carries
  Pozo de Gamboa, Pánuco's point and GeoNames link but the INEGI code of Pozo Gamboa, Miguel Auza). This covers renamed places and GeoNames' own alternate names:
  *Venustiano Carranza* = "San Pedro Cahro", *Tepuxtepec* = "Salto de Tepuxtepec", *San Gaspar Tonatico* =
  "Tonatico" (the municipality is a separate record, *Tonatico*).
- **Guards:** a record named "Barrio Cuarto (La Loma)" does not match an entity calling itself "Barrio Cuarto
  (La Trampa)"; an entity whose own coordinates disagree (it may merge two places) is trusted only if it is
  named like the record and one of its coordinates is within 1 km.

**Town or municipality?** Using each record's real kind and the municipality's seat town (Wikidata P36):

- a **town** record holding a municipality ID moves to that municipality's seat town when it is within 3 km;
- when two differently named records verify one municipality, the town nearest the seat town gets the seat
  town and the other keeps the municipality — unless the two are one place entered twice (same state, same
  name form, within 3 km, no contradicting populations);
- a record that is itself a municipality is never moved to a town;
- a town record **outside** the duplicate groups that holds its municipality's ID (*Polotitlán de la
  Ilustración*) moves to the seat town, so the municipality ID can go to the municipality record
  (3 records outside the groups change this way).

### 2. Re-match the rest

Look up the record's name forms, as written and unaccented, among Wikidata labels and aliases in Mexico. A
candidate must be the right kind for the record and sit within 3 km (towns) or within 60 km in the same state
(municipalities). Candidates with self-consistent coordinates are preferred; one whose coordinates disagree is
used only if nothing else qualifies and one of its coordinates is within 1 km. No ID is handed to a second
record, except to a twin (below).

**Same name, different municipalities.** When candidates share a parent municipality, the nearest wins
(*Marín*: the town and "Ejido Marín" are both in Marín). When they do not:

1. take the one whose INEGI locality code (P1976) lies in the municipality of the record's GeoNames entry —
   *Ojo de Agua* is in Tepeji del Río, Hidalgo (13-063), not Jilotepec, Estado de México (16 records);
2. otherwise take the nearest if it is at most half as far as the next (*Estancia de Ánimas*, 0.18 km vs
   0.71 km);
3. otherwise leave it blank rather than guess (3 records, since settled by review — see below).

GeoNames numbers four states in the old FIPS order (05 Chiapas, 06 Chihuahua, 07 Coahuila, 08 Colima); they
are mapped to INEGI's codes (07, 08, 05, 06) before comparing.

**Duplicate copies.** A later batch re-added some places. Two records in the same state with the same name
form (ignoring a leading article: "El Carmen" = "Carmen"), within 3 km and without contradicting populations,
are one place entered twice: the copy takes the original's ID, and the pair is listed for merging.

### Reviewed decisions

Six records need evidence the rules cannot read: GeoNames' edit history (a point moved further than the
matching radius), an official municipal document, an upstream GeoNames error, or this repository's own
history. Each was found by review and re-checked here against Wikidata, the GeoNames dump and `git log`:

| Record | ID | Evidence |
|---|---|---|
| 72875 Pozos de Gamboa | Q61285628 | Pozo de Gamboa, Pánuco (INEGI 320370016), the municipality of its GeoNames entry 3991930. The old Q20264912 mixes this town with Pozo Gamboa in Miguel Auza (320290081) |
| 69871 El Carmen | Q61248206 | El Carmen, Hueypoxtla (150360002). Record population 1,238 = GeoNames 3817826 = the 2010 figure in Hueypoxtla's municipal plan; the neighbouring Tizayuca El Carmen (130690002) has 7,029 |
| 75372 Teocalco | Q6141720 | GeoNames 9091728: population 1,123 = record, Tlaxcoapan (13-074), point moved 0.46 km in 2026. Q6141720 links to it and is Tlaxcoapan locality 130740004 |
| 71211 La Ceja | Q61292080 | GeoNames 9512860: population 1,940 = record, Huimilpan (22-008), point moved 1.2 km in 2025. Q61292080 is Huimilpan locality 220080135 |
| 68306 Apetatitlán Antonio Carbajal | Q20224318 (kept) | The seat town of Apetatitlán de Antonio Carvajal (INEGI 290020001), linked to the record's GeoNames entry 3518140. GeoNames files that entry under neighbouring Contla (29-018) in error, so the INEGI check alone would reject it |
| 149825 Villaldama Nuevo León | blank | Added in 2022 in the Nuevo León batch with exactly the coordinates of town record 69194; moved 6 km on 6 Aug 2025 with no recorded source. Its current position near GeoNames' municipality point therefore does not show it is the municipality |

### 3. Remove the ID when nothing verifies

A blank `wikiDataId` is better than one pointing at a different place.

### 4. Resolve Wikidata redirects

Every final ID is checked for a redirect and replaced by the current item (78 IDs, e.g. `Q7920663` →
`Q6119540`). Where Wikidata merged two items, the two records that held them now share one ID and are listed
as duplicate records (2 pairs).

## Results

| Outcome | Towns & others | `adm2` | Total |
|---|---:|---:|---:|
| Existing ID verified and kept (78 updated to the merged Wikidata item) | 1,373 | 356 | **1,729** |
| New verified ID (incl. 169 moved to their seat town, 4 reviewed) | 2,872 | 232 | **3,104** |
| ID removed | 362 | 16 | **378** |
| **Records in duplicate groups** | | | **5,211** |

- Shared-ID groups: **1,938 → 15** (the 15 are genuine duplicate records, see below)
- Records changed: **3,563** (3 of them outside the duplicate groups), only the `wikiDataId` field; record
  count unchanged at 9,321
- Records with a `wikiDataId`: 9,321 → 8,943
- **336 of the 378 removed IDs point more than 60 km away** — beyond even the municipality limit

## Verification

- **Regression tests:** round 1 **134/134**, round 2 **8/8**, round 3 **9/9**, round 4 **25/25**, round 5 **5/5**,
  round 6 **11/11**, rounds 7–8 **6/6**; without its reviewed decision *Pozos de Gamboa* is left blank, not given the mixed item. Round-1 expectations whose item Wikidata has since merged are compared as the merged item.
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
- Round 6: *Carmen* shares Q3846844 with its twin *El Carmen Nuevo León* (149709, same population 9,568);
  *Venustiano Carranza* gets Q6119540 (its original ID, now a redirect); *Ciudad de Villaldama* (GeoNames
  town) gets its seat town Q61285822; *Villaldama Nuevo León* is left blank (see reviewed decisions).
- *Condémbaro* gets Q61263614 (Tancítaro), not Q20276537, whose coordinates are 92 km apart; *Barrio Cuarto
  (La Loma)* gets Q49861414 ("Barrio Cuarto", alias "La Loma"), not an entity merging La Loma and La Trampa.

## Found along the way

**`type` values that break the convention (about 510 records).** In CSC, `adm2` normally marks a municipality's
seat town (GeoNames PPLA2, 1,123 records) and `adm1` a state capital. Misfits: 310 records that are the
municipality itself are typed `city` (186 more are typed `adm2`, 4 `municipality`), 141 records typed `adm2` are
plain towns, and 59 seat towns are typed `city`. An earlier version of this summary counted 1,580 wrong types by
reading `adm2` as "municipality"; that misread the convention. The IDs here follow the real kind; the `type`
field itself is not changed here and needs a decision on what a municipality record should be typed.

**Duplicate records (15 pairs).** Both records of each pair describe the same place and hold the same ID;
they should be merged separately.

- Twelve are a later Nuevo León batch (`id` 149xxx) re-adding existing places, often with identical
  populations: Agualeguas, Apodaca, Benito Juárez, Carmen, Doctor Coss, General Escobedo, General Terán,
  Iturbide, Jardines de la Silla, Linares, Parás, Sabinas Hidalgo.
- *Huixquilucan* / *Huixquilucan de Degollado* (Estado de México).
- Two whose Wikidata items were merged: *Benito Juárez* / *Tecolots* (Baja California, now "Tecolotes"; their
  populations, 4,167 and 5,259, need reconciling when merged) and *El Guayabo* / *Heriberto Valdez Romero (El
  Guayabo)* (Sinaloa).

**Records filed under the wrong state.** 166 records sit in a different state from their GeoNames entry (82
of them filed under Morelos). These ones also match a Wikidata entity by name and location in that other
state:

| Record | Filed under | Entity is in |
|---|---|---|
| 76028 Villa Lázaro Cárdenas | Veracruz | Puebla |
| 72388 Nuevo Ixcatlán | Oaxaca | Veracruz |
| 75900 Urén | Estado de México | Michoacán |
| 75813 Tupátaro | Estado de México | Michoacán |
| 73759 San José Comalco | Morelos | Estado de México |
| 68918 Cerritos de Cárdenas | Morelos | Estado de México |
| 74104 San Martín Peras | Guerrero | Oaxaca |
| 74131 San Mateo Otzacatipan | Morelos | Estado de México |

Not changed here.

## Known limitations

- **5 removed IDs sit within 1 km** of the record but could not be verified, deliberately (different
  sectors, old vs new town, possible barrio): Cañada, La Isla Km 10, Mazamitlongo, Monclova Segundo Sector,
  Necaxa.
- The INEGI identity check needs an INEGI code on the item; an item without one (e.g. Q20144006, *Gustavo
  Adolfo Madero*) is kept on its name and GeoNames link alone.
- *San Carlos* (73456, Tabasco) keeps Q20136621 on coordinate identity, but that entity is labelled "Caobal"
  and described as "bad geoname 3519588" — identity unresolved.

## Same bug in other countries

The same copy-forward pattern exists across **178 country files (~29,450 affected records)**, e.g. FR 4,365,
BR 2,726, DE 1,284, ES 1,211, AT 936, AU 784, IN 706, JP 675, US 651. The method carries over, but each
country needs its own place-type codes, naming conventions and GeoNames dump checked first.

## Rollback

Revert the commit. No `id`s change, so nothing downstream needs repair.

## Files Changed
- `contributions/cities/MX.json` — `wikiDataId` corrected on 3,563 records.
