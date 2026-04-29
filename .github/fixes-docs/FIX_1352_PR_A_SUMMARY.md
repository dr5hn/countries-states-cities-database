# FIX #1352 — France: missing metropolitan communes (PR-A of 4)

**Issue:** [#1352 — France data: missing cities, regions misclassified](https://github.com/dr5hn/countries-states-cities-database/issues/1352)
**Scope:** Add missing metropolitan French communes (`contributions/cities/FR.json`).
**Sibling PRs (separate, parallel):**
- **PR-B** — re-classify cities currently under the wrong CSC region (this PR *flags* 1,194 candidates but does not move them).
- **PR-C** — clean up obsolete / merged communes and quartiers stored as cities.
- **PR-D** — overseas territories (GP, MQ, GF, RE, YT, BL, MF, PM, WF, PF, TF, NC).
**Date:** 2026-04-25

## Problem

The reporter observed that `contributions/cities/FR.json` (10,079 records) is missing many metropolitan communes vs. the canonical INSEE list maintained by data.gouv.fr (~34,800 metropolitan communes). Notable absentees, all large communes-nouvelles created since 2015, are in the top 15 of this PR's additions:

| Population | Commune | Created (or renamed) |
|------------|---------|----------------------|
| 78,258 | Cherbourg-en-Cotentin | 2016 |
| 66,919 | Évry-Courcouronnes | 2019 |
| 53,615 | Saint-Ouen-sur-Seine | 2018 (rename) |
| 38,168 | Oullins-Pierre-Bénite | 2024 |
| 31,779 | Herblay-sur-Seine | 2018 |
| 30,689 | Le Chesnay-Rocquencourt | 2019 |
| 25,797 | Sèvremoine | 2015 |
| 23,989 | Beaupréau-en-Mauges | 2015 |
| 21,999 | Chemillé-en-Anjou | 2015 |
| 21,134 | Montaigu-Vendée | 2018 |

Cities like **Ajaccio** (76 K) and **Bastia** (47 K) *are* in CSC, but stored under `20R` (the Corse collectivity) instead of `2A`/`2B` (the departments). The diff flags them as cross-region matches → **PR-B's** territory, not added here.

A naïve full-import would balloon FR.json from 10K to 35K records in a single PR — unreviewable. **PR-A applies a conservative population-thresholded slice** and surfaces the rest for follow-up PRs.

## Scope of THIS PR

| | Before | After | Δ |
|---|--------|-------|---|
| `contributions/cities/FR.json` | 10,079 | **10,534** | **+455** |

All additions are metropolitan-France communes with **population ≥ 2,000** (configurable in the script via `--pop-threshold`). The 2,000 floor matches the user's expected envelope (200–800) while keeping the diff reviewable.

### Distribution by CSC state

| state_code | added |
|------------|-------|
| PDL (Pays-de-la-Loire) | 82 |
| ARA (Auvergne-Rhône-Alpes) | 78 |
| NOR (Normandie) | 77 |
| NAQ (Nouvelle-Aquitaine) | 56 |
| BRE (Bretagne) | 42 |
| OCC (Occitanie) | 31 |
| GES (Grand-Est) | 21 |
| CVL (Centre-Val de Loire) | 21 |
| IDF (Île-de-France) | 16 |
| BFC (Bourgogne-Franche-Comté) | 12 |
| HDF (Hauts-de-France) | 10 |
| PAC (Provence-Alpes-Côte-d'Azur) | 9 |

Skew toward PDL/NOR/ARA reflects the concentration of recent commune mergers ("communes nouvelles") in those regions. **Corsica (`2A`/`2B`/`20R`) sees zero adds in this PR**: every Corsican upstream commune at pop ≥ 2,000 was matched to an existing CSC record (often under `20R`, the collectivity) — those state-code mismatches are PR-B's reclassification scope.

## Methodology

### Sources

1. **`villes.min.json`** — the file the reporter attached to the issue
   (`https://github.com/user-attachments/files/25721910/villes.min.json`).
   35,029 rows of `{nom, departement, region, code}`. INSEE codes are canonical.
2. **`geo.api.gouv.fr/communes`** — used to enrich missing communes with
   coordinates and population (the reporter's file has neither). Same INSEE
   codes, 34,969 rows. Fetched as
   `https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,codeRegion,centre,population&format=json`.

Neither file is committed; both are downloaded by the script (or by the reviewer) into a temporary directory.

### Matching

CSC's `FR.json` does **not** carry an INSEE code, so we cannot diff by INSEE directly. Instead the script matches by `(target_state_code, normalised_name)` where:

- `normalised_name` = NFKD-fold-to-ASCII + manual ligature expansion (`œ→oe`, `æ→ae`, `ß→ss`) + canonicalise toponymic prepositions (`lès → lez`) + strip non-letter characters + lowercase. The ligature/preposition handling caught four would-be duplicates that the simpler accent fold missed (`Annœullin`/`Annoeullin`, `Paimbœuf`/`Paimboeuf`, `Rœschwoog`/`Roeschwoog`, `Saint-Christol-lez-Alès`/`Saint-Christol-lès-Alès`).
- `target_state_code` is derived from the upstream `(departement, region)` pair using:
  - INSEE region code → CSC region iso2 (e.g., `84 → ARA`, `11 → IDF`, `94 → 2A/2B`).
  - **Department-level overrides** for the five departments that the existing
    FR.json stores at department-level rather than region-level: `2A`, `2B`,
    `48`, `52`, `55`. (Discovered empirically; new records in those depts must
    follow suit to match existing convention.)

If the primary state lookup misses, the script also tries every other metropolitan CSC state code. A hit there is **not** a successful match — it's a *cross-region match*, flagged for PR-B (region reclassification), and the upstream record is still considered "missing" only if no fallback hit exists.

### Conservative filter

A missing upstream commune is auto-added only if **all** of:

- A `target_state_code` was determined (i.e., upstream region is metropolitan and mapped).
- `geo.api.gouv.fr` provided coordinates and a non-null `population`.
- Coordinates lie inside the metropolitan FR bounding box from `.github/data/country-bounds.json`.
- `population ≥ 2,000`.

Anything that fails any criterion lands in the `france_cities_diff.deferred.json` artifact with structured `skip_reasons`. Future PRs can lower the threshold or re-validate the deferred entries without re-running discovery.

### Field choices for new records

Following the existing FR.json convention:

```json
{
  "name": "Évry-Courcouronnes",         // INSEE official French name
  "state_id": 4796, "state_code": "IDF",
  "country_id": 75, "country_code": "FR",
  "type": "city",
  "level": null, "parent_id": null,
  "latitude": "48.62870000", "longitude": "2.43130000",
  "native": "Évry-Courcouronnes",        // identical to name (no English exonym for ~all communes)
  "population": 66919,                   // from geo.api.gouv.fr
  "timezone": "Europe/Paris"
}
```

Auto-managed fields (`id`, `created_at`, `updated_at`, `flag`) are deliberately omitted — the JSON-first import will assign them. Translations and `wikiDataId` are intentionally not generated; we'd rather leave them empty than synthesise low-quality values.

## Validation

Run locally against the modified FR.json:

| Check | Result |
|-------|--------|
| JSON valid + canonical 2-space indent | OK |
| Schema (required fields, types, ranges, no auto-managed) | **0 errors** (455 records) |
| Cross-reference (state_id/country_id exist, codes match) | OK |
| Coordinates inside FR metropolitan bounding box | OK |
| Exact-name + same-state duplicates | **0** |
| Fuzzy duplicates (Levenshtein ≤ 2 + < 5km) | **1** (Bréhan vs Rohan, dept 56 — genuinely two different communes 4.3km apart, INSEE 56025 vs 56196) |
| Schema warnings | 2,275 (`unknown field` for `type`/`level`/`parent_id`/`native`/`population` — same warnings the existing 10,079 records produce; warnings, not errors) |

Re-validation:

```bash
python3 bin/scripts/fixes/france_cities_diff.py \
  --upstream /path/to/villes.min.json \
  --geo /path/to/geo-api-communes.json
```

## Diagnostic output (not auto-applied — for follow-up PRs)

The diff also surfaces issues that are out-of-scope for PR-A but relevant to the broader #1352 plan. Counts in `bin/scripts/fixes/france_cities_diff.report.json`:

| Category | Count | Owner |
|----------|-------|-------|
| `missing` total (all metro communes upstream not in CSC) | 24,118 | PR-A.2+ (lower the population threshold) |
| `missing` with population ≥ 2,000 (auto-applied here) | 455 | **THIS PR** |
| `cross_region_matches` (CSC city under wrong region) | 1,194 | **PR-B** |
| `coord_mismatches` > 1km (homonym-filtered, single-name only) | 4,836 | **PR-C** (still includes intra-region homonyms; see caveat below) |
| `extra` (CSC city with no metro upstream match) | 643 | **PR-C** (largely obsolete-merged communes, quartiers, or department names mistakenly stored as cities) |

### Notable `extra` findings worth flagging for PR-C

- **Department names stored as cities**: `Alpes-Maritimes`, `Alpes-de-Haute-Provence`, `Ardennes` — these are dept-level admin units, not communes.
- **Obsolete/merged communes**: `Aime`, `Aigueblanche`, `Albens` (merged into `Aime-la-Plagne`); `Annecy-le-Vieux` (merged into Annecy in 2017); `Ancenis` (merged into `Ancenis-Saint-Géréon` in 2019); `Antrain` (merged into Val-Couesnon).
- **Quartiers stored as cities**: `Arenc`, `Bonsecours`, `Montolivet`, `Saint-Barnabé`, `La Villette` — most of the top "PAC coord-mismatch" hits are Marseille neighbourhoods coincidentally sharing names with unrelated communes elsewhere.
- **Spelling variants**: `Argelers` (Catalan/Occitan; standard French is `Argelès-sur-Mer`).

### Coordinate-mismatch caveat

The coord-mismatch column is a *report*, not a fix. It triggers when a CSC city's `(state, name)` matches a single-named upstream commune more than 1 km away. The 1,978 entries where the same name occurs multiple times in the metro upstream were skipped to avoid spurious flags. **Even after that filter, intra-region homonyms can produce false-positive mismatches** — e.g., the top PAC entries (`La Villette`, `Saint-Barnabé`, `Vieille-Chapelle`, `Bonsecours`) are Marseille quartiers being matched against unrelated communes elsewhere in PAC. Real coord errors will need INSEE-coded ground truth, which is partly what PR-C will add.

## Edge cases handled

1. **`œ`/`æ` ligatures** — NFKD does not decompose these. Manually mapped in `normalise_name`.
2. **`lès` ↔ `lez` preposition** — both are valid orthographies; canonicalised to `lez` for matching.
3. **Corsica** — INSEE region 94 (`Corse`) covers two depts, `2A` and `2B`. CSC has *three* states for it: `2A` (id 4996), `2B` (id 4997), and `20R` (id 4806, the *collectivity*). Our existing data is split across all three (104 / 229 / 28 records). New records use the dept code (`2A`/`2B`) since that's the dominant pattern (333 vs 28). Existing `20R` records were correctly recognised as cross-region matches against upstream `2A`/`2B`, not as "extras".
4. **Dept-coded depts inside region-coded regions** — five depts (`2A`, `2B`, `48`, `52`, `55`) are stored at dept-level in existing FR.json; the rest of their parent regions are stored at region-level. The `DEPT_OVERRIDES` constant codifies this so new records line up with existing convention.
5. **Bas-Rhin/Haut-Rhin (Alsace, dept 67/68)** — `states.json` has both `GES` (Grand-Est, the region) and `6AE` (Alsace, the European Collectivity). All 514+366 existing Alsatian cities use `GES`; **none** use `6AE`. New records likewise go under `GES` to match upstream's region mapping (depts 67/68 → region 44 → `GES`).
6. **Paris** — present once as `state_code=IDF, type=capital, id=44856`. No arrondissements in CSC, none in upstream `villes.min.json` either. Untouched.
7. **Métropole de Lyon (`69M`)** — `states.json` has it as a separate state, but no cities reference it; existing Rhône cities (dept 69) use `ARA`. New records continue that pattern.

## Out of scope (handled by sibling PRs)

- **Region reclassification (1,194 cross-region matches)** — PR-B.
- **Obsolete/merged commune cleanup, quartiers stored as cities, department-as-city records (~643 extras)** — PR-C.
- **Lower-population missing communes (~23,663 deferred)** — future PR-A.2 with a tighter source review.
- **Overseas territories (GP, MQ, GF, RE, YT, BL, MF, PM, WF, PF, TF, NC)** — PR-D. The script's `METRO_REGIONS` set excludes upstream regions `01`/`02`/`03`/`04`/`06`/`975`/`977`/`978`/`984`/`986`/`987`/`988`/`989`.
- **Translations / wikiDataId for new records** — left empty rather than synthesised; can be backfilled in a later pass.

## Files in this PR

| Path | Status |
|------|--------|
| `contributions/cities/FR.json` | +455 records appended |
| `bin/scripts/fixes/france_cities_diff.py` | new |
| `bin/scripts/fixes/france_cities_diff.report.json` | new (diff summary; useful audit trail) |
| `.github/fixes-docs/FIX_1352_PR_A_SUMMARY.md` | new (this file) |

`france_cities_diff.merge.json` (the proposed-records artifact) and `france_cities_diff.deferred.json` (skipped-records artifact, ~7 MB) are intentionally **not** committed — `merge.json` content is now in FR.json and the deferred set is regeneratable on demand.
