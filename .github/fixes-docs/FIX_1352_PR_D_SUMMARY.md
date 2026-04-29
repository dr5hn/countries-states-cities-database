# FIX 1352 — PR-D: Populate missing FR-overseas city files

**Issue:** [#1352](https://github.com/dr5hn/countries-states-cities-database/issues/1352) — France data: missing cities and regions misclassified

**PR scope (PR-D of 4):** Populate the 5 missing overseas-territory city files (GF, BL, MF, PM, TF) and add the parent state records they require.

## Scope expansion vs. original brief

The original PR-D brief said *"DO NOT touch states.json — that's PR-B."* While drafting, I discovered that **PR-B's brief is polish-only** ("Don't add or delete state records"), so the parent state records for these 5 territories were never going to be added by any sibling PR. Cities require a real `state_id` to pass cross-reference validation, so PR-D was expanded to include the 9 minimal state records the cities depend on. This expansion was approved before any state edits were made.

Each new state lives under its own overseas country (GF=76, BL=189, MF=190, PM=187, TF=78) — **not** under FR. This matches the modelling pattern already used by MQ/GP/NC/PF/RE/YT/WF, which the database treats as separate countries because they hold distinct ISO 3166-1 alpha-2 codes.

## What was added

### State records — `contributions/states/states.json` (9 new records)

| id   | name                              | country | iso2 | iso3166_2 | type                  | wikiData |
|------|-----------------------------------|---------|------|-----------|-----------------------|----------|
| 5815 | Guyane                            | GF (76) | 01   | FR-973    | overseas region       | Q3769    |
| 5816 | Saint-Barthélemy                  | BL (189)| 01   | FR-BL     | overseas collectivity | Q25362   |
| 5817 | Saint-Martin                      | MF (190)| 01   | FR-MF     | overseas collectivity | Q126125  |
| 5818 | Saint-Pierre and Miquelon         | PM (187)| 01   | FR-PM     | overseas collectivity | Q34617   |
| 5819 | Adélie Land                       | TF (78) | 01   | —         | district              | Q184319  |
| 5820 | Crozet Islands                    | TF (78) | 02   | —         | district              | Q186940  |
| 5821 | Kerguelen Islands                 | TF (78) | 03   | —         | district              | Q133888  |
| 5822 | Saint-Paul and Amsterdam Islands  | TF (78) | 04   | —         | district              | Q1149385 |
| 5823 | Scattered Islands                 | TF (78) | 05   | —         | district              | Q230589  |

**Per-territory state count rationale**

- **GF — 1 state.** Single overseas region/département (Guyane). The 22 communes are flat children of this single region, mirroring the user's spec ("default to single département").
- **BL, MF — 1 state each.** Single-commune overseas collectivities. Mirrors user's spec.
- **PM — 1 state.** Two real communes (Saint-Pierre and Miquelon-Langlade), but no PM precedent exists in the DB. Per the spec ("if PM has no precedent, mirror BL/MF — single state"), modelled as a single overseas collectivity with both communes as cities.
- **TF — 5 states.** The 5 statutory districts of the French Southern and Antarctic Lands, each with its principal research station as a "city".

**iso3166_2 codes**: TF districts have no ISO 3166-2 sub-codes (TF itself is an ISO 3166-1 by-exception code), so set to `null`. BL/MF/PM use `FR-BL`/`FR-MF`/`FR-PM` (ISO 3166-1 by-exception codes that double as the FR sub-codes). GF uses `FR-973` (the proper ISO 3166-2 sub-code for the Guyane région).

### City records (31 new records across 5 files)

| File | Count | Cities |
|------|-------|--------|
| `contributions/cities/GF.json` | 22 | All 22 communes of French Guiana, sorted alphabetically: Apatou, Awala-Yalimapo, Camopi, Cayenne, Grand-Santi, Iracoubo, Kourou, Macouria, Mana, Maripasoula, Matoury, Montsinéry-Tonnegrande, Ouanary, Papaichton, Régina, Remire-Montjoly, Roura, Saint-Élie, Saint-Georges, Saint-Laurent-du-Maroni, Saül, Sinnamary |
| `contributions/cities/BL.json` | 1 | Gustavia (capital) |
| `contributions/cities/MF.json` | 1 | Marigot (capital) |
| `contributions/cities/PM.json` | 2 | Miquelon-Langlade, Saint-Pierre |
| `contributions/cities/TF.json` | 5 | Alfred Faure (Crozet), Dumont d'Urville Station (Adélie), Martin-de-Viviès (Saint-Paul/Amsterdam), Port-aux-Français (Kerguelen), Tromelin (Scattered Islands) |

## Edge case: TF (uninhabited territory)

The French Southern and Antarctic Lands have no permanent civilian population. The "cities" recorded for TF are the principal research stations / administrative bases of each district — they're the closest analogue to a populated locality the territory has. Each station has a stable Wikidata entity, fixed coordinates, and is described as the district's de facto capital in the official TAAF documentation.

Tromelin (Scattered Islands) is a French weather station and 1,200-m airstrip on Tromelin Island; it's the most-documented Scattered-Islands base. The Scattered Islands as a whole are administered remotely from Saint-Denis, Réunion, but Tromelin is the only one of the five with a continuous human presence and a stable Wikidata coordinate, so it represents the district here.

Timezones for TF cities reflect physical location:
- Adélie Land → `Antarctica/DumontDUrville`
- Crozet, Kerguelen, Saint-Paul/Amsterdam → `Indian/Kerguelen`
- Tromelin (Scattered Islands) → `Indian/Reunion` (Tromelin shares Réunion's UTC+4)

## Sources

- **GF communes** — Wikidata SPARQL (`P31=Q484170` commune ∧ `P131*=Q3769` French Guiana), cross-referenced with [Wikipedia: Communes of French Guiana](https://en.wikipedia.org/wiki/Communes_of_French_Guiana). Coordinates and Q-IDs from Wikidata.
- **BL/MF/PM** — Wikipedia articles for Gustavia (Q34112), Marigot (Q200605), Saint-Pierre commune (Q185678), Miquelon-Langlade (Q570289).
- **TF stations** — Wikipedia articles for each station: Dumont d'Urville Station, Alfred Faure, Port-aux-Français (Q839559), Martin-de-Viviès, Tromelin Island.
- **Country/state IDs** — verified against `contributions/countries/countries.json` and existing `contributions/states/states.json` (max prior id = 5814; new ids 5815–5823 are non-conflicting).

## Validator implications

The repo's PR validator runs as `continue-on-error: true` (advisory only — see `.github/workflows/pr-validator.yml`), so the items below do not block merging.

- **Schema validator**: the 9 new state records include `id` (5815–5823) which `validate-schema.js` flags as auto-managed-only. This is intentional — without pre-assigned state IDs, the 31 cities cannot reference their parent states and `validate-cross-reference.js` would error 31 times instead. The contributor convention (per `bin/scripts/sync/normalize_json.py`) pre-assigns sequential IDs to new state records so cross-refs resolve cleanly; we did that manually since this worktree has no MySQL instance.
- **Cross-reference validator**: all 31 cities reference state IDs 5815–5818 (singular states for GF/BL/MF/PM) or 5819–5823 (TF districts), all of which exist in the same PR. `state_code` matches each state's `iso2` per the existing FR-overseas convention.
- **Coordinate-bounds validator**: GF, BL, MF, PM, TF have **no entries** in `.github/data/country-bounds.json`, so this validator skips them entirely — no warnings expected.
- **Duplicate detector**: no existing cities for these territories, so duplicate detection runs against an empty baseline.

## Out of scope

- FR.json city additions — handled by **PR-A** (`feat/issue-1352-france-cities-diff`).
- FR mainland states polish (renames, `iso3166_2` corrections) — **PR-B** (`feat/issue-1352-france-states-polish`).
- Documentation of the FR / FR-overseas modelling decision — **PR-C** (`feat/issue-1352-multi-level-territories-doc`).

## Counts

| Category    | Records |
|-------------|---------|
| New states  | 9       |
| New cities  | 31      |
| Files added | 5 (GF, BL, MF, PM, TF .json) |
| Files modified | 1 (states.json) |
