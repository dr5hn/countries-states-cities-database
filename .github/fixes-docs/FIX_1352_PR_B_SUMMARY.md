# FIX #1352 (PR-B) — France: department + region metadata polish

**Issue:** [#1352 — France data review (Option C, 4 sub-PRs)](https://github.com/dr5hn/countries-states-cities-database/issues/1352)
**Scope of this PR:** Department + region metadata polish ONLY. Cities are PR-A; overseas city files are PR-D; PR-C is reserved for follow-up.
**Date:** 2026-04-25
**Authoritative source:** data.gouv.fr open feeds (INSEE-derived)
- `departements.min.json` (101 entries: 96 metropolitan + 5 overseas DROM) — https://github.com/user-attachments/files/25721909/departements.min.json
- `regions.min.json` (18 entries: 13 metropolitan + 5 overseas DROM) — https://github.com/user-attachments/files/25721911/regions.min.json

## Problem

A targeted diff of `contributions/states/states.json` (124 FR records) against the data.gouv.fr feeds surfaced two categories of stale metadata:

1. **Garbage `native` values on 11 metropolitan departments.** The `native` field on records like Ain, Aude, Eure, Gard, Gers, Indre, Lot, Manche, Meuse, Haut-Rhin, and Var contained unrelated French sentence fragments ("Se faire", "entendus", "Ton", "Gardien", "Génie", "Interne", "Parcelle", "Quelques", "Notre"…) plus a typo ("Miuse" for Meuse, "Peau" for Haut-Rhin). These appear to be the residue of a translation pipeline that emitted text fragments rather than the geographic name.
2. **Misclassified Corse + English in a `native` field.** Corse (ISO 3166-2 `FR-20R`) was tagged `metropolitan collectivity with special status`, but data.gouv.fr lists Corse in the **regions** feed, and Wikipedia/INSEE confirm it is one of France's 18 regions (with enhanced autonomy, but a region nonetheless). Its `native` was the typo `"Corsée"`. Separately, French Guiana (ISO `FR-973`, type `overseas region`) had its `native` set to the English string `"French Guiana"` instead of the French `"Guyane"`.

## Tooling

A new read-only diff script lives at `bin/scripts/fixes/france_states_diff.py`. It compares the data.gouv.fr feeds against repo `country_code='FR'` records and reports four sections:

- **Real deltas** (department + region native names; region type)
- **Typographical-only diffs** (advisory; differs in punctuation/hyphens only)
- **Coverage of fields not in the feeds** (`fips_code`, `iso3166_2`, `latitude`, `longitude`, `wikiDataId`, `timezone`)
- **Repo records outside the feed scope** (overseas collectivities, dependencies, special-status metropolitan collectivities, overseas territory)

Run with:

```bash
python3 bin/scripts/fixes/france_states_diff.py
# or with explicit paths
python3 bin/scripts/fixes/france_states_diff.py --departements /tmp/fr1352/departements.min.json --regions /tmp/fr1352/regions.min.json
```

After this PR's edits the script reports `Department deltas: 0` and `Region deltas: 0`. Remaining output is advisory only.

## Changes Applied (13 records, all in `contributions/states/states.json`)

### Department `native` repairs (11)

| ISO2 | `name` (English) | `native` before | `native` after |
|------|------------------|-----------------|----------------|
| 01   | Ain              | `Se faire`      | `Ain`          |
| 11   | Aude             | `entendus`      | `Aude`         |
| 27   | Eure             | `Ton`           | `Eure`         |
| 30   | Gard             | `Gardien`       | `Gard`         |
| 32   | Gers             | `Génie`         | `Gers`         |
| 36   | Indre            | `Interne`       | `Indre`        |
| 46   | Lot              | `Parcelle`      | `Lot`          |
| 50   | Manche           | `Quelques`      | `Manche`       |
| 55   | Meuse            | `Miuse`         | `Meuse`        |
| 68   | Haut-Rhin        | `Peau`          | `Haut-Rhin`    |
| 83   | Var              | `Notre`         | `Var`          |

### Overseas region `native` repair (1)

| ISO2 | `name` (English) | `native` before  | `native` after |
|------|------------------|------------------|----------------|
| 973  | French Guiana    | `French Guiana`  | `Guyane`       |

### Corse reclassification + native typo (1 record, 2 fields)

| ISO2 | Field    | Before                                            | After                  |
|------|----------|---------------------------------------------------|------------------------|
| 20R  | `type`   | `metropolitan collectivity with special status`   | `metropolitan region`  |
| 20R  | `native` | `Corsée`                                          | `Corse`                |

After this change, the FR `type` distribution becomes:

| Type | Count |
|------|------:|
| metropolitan department | 95 |
| metropolitan region | **13** (was 12; +Corse) |
| overseas region | 5 |
| overseas collectivity | 5 |
| metropolitan collectivity with special status | **2** (was 3; −Corse, leaving Lyon Métropole + Paris) |
| European collectivity | 1 |
| overseas collectivity with special status | 1 |
| overseas territory | 1 |
| dependency | 1 |
| **Total** | **124** (unchanged) |

## Items Deliberately NOT Changed (Flagged for Review)

These were surfaced by the diff but kept out of PR-B for one of three reasons: (a) they are stylistic/typographical and the canonical form is debatable, (b) they sit outside this PR's "department + region" scope, or (c) they are modeling decisions for the maintainer.

### 1. Region `native` typography (3 records)

Both forms appear in official French publications; data.gouv.fr drops the connecting hyphen and uses a straight apostrophe.

| ISO2 | Repo `native`                  | data.gouv.fr `nom`              | Note |
|------|--------------------------------|---------------------------------|------|
| GES  | `Grand-Est`                    | `Grand Est`                     | INSEE prefers the unhyphenated form. |
| PDL  | `Pays-de-la-Loire`             | `Pays de la Loire`              | INSEE prefers no hyphens. |
| PAC  | `Provence-Alpes-Côte-d'Azur`   | `Provence-Alpes-Côte d'Azur`    | INSEE drops the hyphen before *d'Azur* and uses a straight apostrophe. |

These would be safe to align with data.gouv.fr in a follow-up, but coordination with `translations.fr` is recommended.

### 2. Repo records outside the data.gouv.fr feed scope

The feeds only enumerate metropolitan departments, metropolitan regions, and overseas DROM regions. The following 12 FR records are not covered by the feeds and were therefore not validated against an authoritative source in this PR:

| ISO2 | type                                            | name                              | Observation |
|------|-------------------------------------------------|-----------------------------------|-------------|
| 6AE  | European collectivity                           | Alsace                            | Special collectivity formed 2021. |
| CP   | dependency                                      | Clipperton                        | Uninhabited Pacific atoll. |
| 69M  | metropolitan collectivity with special status   | Métropole de Lyon                 | Replaces dept 69 in Rhône metro. |
| 75C  | metropolitan collectivity with special status   | Paris                             | data.gouv.fr lists `code: 75 — Paris` in **departements**; we model it as a special-status metropolitan collectivity. Modeling difference, not a data error. |
| BL   | overseas collectivity                           | Saint-Barthélemy                  | OK. |
| MF   | overseas collectivity                           | Saint-Martin                      | OK. |
| PF   | overseas collectivity                           | French Polynesia                  | `native` correctly French (`Polynésie française`). |
| **PM** | overseas collectivity                         | Saint Pierre and Miquelon         | `native` is currently the English string; the official French is `Saint-Pierre-et-Miquelon`. **Not changed in PR-B** because PM is an overseas collectivity (not a department or region); flagging for PR-D scope. |
| WF   | overseas collectivity                           | Wallis and Futuna                 | `native` is `Wallis et Futuna`; the official French is `Wallis-et-Futuna` (hyphenated). Borderline; flagging. |
| NC   | overseas collectivity with special status       | Nouvelle-Calédonie                | `name` is in French; the canonical English is `New Caledonia`. **Not changed in PR-B** — outside dept/region scope and renaming a top-level subdivision warrants reviewer sign-off. Flag for PR-D. |
| **TF** | overseas territory                            | French Southern and Antarctic Lands | `native` is currently `Terres du sud et de l'Antarctique français`, which is non-standard. The official French name is `Terres australes et antarctiques françaises`. Flagging for PR-D. |

### 3. `fips_code` coverage gap (advisory)

The diff coverage report notes only **27 of 124** FR records have a `fips_code`. data.gouv.fr does not provide FIPS codes (US standard), so this gap cannot be filled from these feeds. Out of scope for PR-B.

### 4. `code: 75 — Paris` "missing" in repo iso2 index (advisory)

data.gouv.fr's departements feed lists Paris with `code: 75`. Our repo stores Paris at `iso2: 75C` with `type: metropolitan collectivity with special status`. This is a deliberate modeling decision (Paris merged its dept and city/commune functions in 2019) — not a data error. Documented here for transparency.

### 5. Possibly stale `timezone` on 973 (out of scope)

Spot-checked while editing: French Guiana's `timezone` is `Europe/Paris`, but the territory is in `America/Cayenne` (UTC−3, no DST). Same potential issue may exist for other DROM. Not changed here — PR-B's scope is metadata polish, not timezone correction. Flag for follow-up.

## Why Reclassify Corse?

Corse is a **collectivité territoriale unique** (since 2018) that exercises both regional and departmental powers within its territory. Wikipedia explicitly notes Corse is "one of the 18 regions of France." data.gouv.fr lists Corse in the **regions** feed, not departments, with regional code `94`. The ISO 3166-2 sub-code `FR-20R` (where `R` indicates *région*) is also consistent with region status.

The repo's previous classification — `metropolitan collectivity with special status` — better describes entities like:
- **Métropole de Lyon** (`69M`): a metropolitan collectivity that replaces dept 69 over the Lyon urban area, while the dept territory continues to exist as `69` for the rest of Rhône. (Currently `69D — Rhône` is *not* in our list because the metro replaced the dept.)
- **Paris** (`75C`): merged commune-and-département entity since 2019.

Corse, by contrast, is a region whose departmental councils (`2A` and `2B`) were merged. The two department codes still exist (data.gouv.fr keeps them as `circonscriptions départementales`) and remain in our repo as `metropolitan department`. Reclassifying Corse as `metropolitan region` aligns with the authoritative source while preserving the dept records for `2A` and `2B`.

## Validation Performed

- `python3 bin/scripts/fixes/france_states_diff.py` — `Department deltas: 0`, `Region deltas: 0`.
- `python3 -m json.tool contributions/states/states.json` — file parses as valid JSON.
- Local FK integrity check: every FR `country_id`/`country_code` pair resolves correctly against `contributions/countries/countries.json`.
- FR record count unchanged: 124 before, 124 after.
- All `id` values still globally unique across `states.json`.
- `.github/scripts/utils.js` `validateRecord(...)` against the 13 touched records: **0 errors**, identical warning footprint to untouched FR records (the warnings are pre-existing schema gaps for `iso3166_2`, `timezone`, `translations`, `population`).

## Files Changed

- `contributions/states/states.json` — 13 records, 14 fields touched.
- `bin/scripts/fixes/france_states_diff.py` — new diagnostic script.
- `.github/fixes-docs/FIX_1352_PR_B_SUMMARY.md` — this document.

## Out of Scope (Other PRs)

- **PR-A** — French city polish in `contributions/cities/FR.json`.
- **PR-D** — Overseas city files (`contributions/cities/PF.json`, `BL.json`, `MF.json`, `NC.json`, `PM.json`, `WF.json`, `TF.json`).
- **Future** — Items 1–5 in "Items Deliberately NOT Changed" above.
