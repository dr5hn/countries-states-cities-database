# Multi-Level Territories Policy

> **Status:** Active policy. Established as part of [#1352](https://github.com/dr5hn/countries-states-cities-database/issues/1352) (France data, PR-C).
> **Scope:** Explains why some geographical entities appear simultaneously as ISO 3166-1 *countries* and as ISO 3166-2 *subdivisions* of another country in this database, and how downstream consumers should reason about it.

## Background

A handful of overseas / autonomous territories are listed by ISO 3166 at **two levels** at once:

- **ISO 3166-1** assigns them their own two-letter country code (e.g. `MQ` for Martinique).
- **ISO 3166-2** also lists them as subdivisions of a parent state (e.g. `FR-MQ` as a subdivision of France).

This is not an accident or a bug in the standard — it reflects political reality. Martinique *is* an integral region of the French Republic (its residents vote in French national elections, use the euro, and are EU citizens), but it *also* has independent representation at certain international bodies, its own internet TLD, its own currency code in some historical contexts, and so on.

When ISO models a place at two levels, this database does too.

## Policy

**Both representations are kept in sync. Neither is canonical; both are first-class.**

For each multi-level territory:

1. There is a row in `contributions/countries/countries.json` (with its own `id`, `iso2`, `iso3`).
2. There is a row in `contributions/states/states.json` whose `country_code` points at the **parent** state (e.g. `FR`, `US`, `CN`), and whose `iso2` / `state_code` matches the territory.
3. Cities under the territory live in `contributions/cities/<TERRITORY_ISO2>.json` (e.g. `MQ.json`), and reference both their `country_id` (= the territory) and their `state_id` (= the territory-as-subdivision-of-parent).

## The 12 French Overseas Territories

These are the territories covered by this policy under France. All 12 appear as both `FR` subdivisions and as standalone ISO 3166-1 countries.

| ISO 3166-1 | ISO 3166-2 / INSEE | Name (English)                       | `countries.id` | `states.id` | State `type`                                |
| :--------- | :----------------- | :----------------------------------- | -------------: | ----------: | :------------------------------------------ |
| `GF`       | `FR-GF` / `973`    | French Guiana                        |             76 |        4822 | overseas region                             |
| `PF`       | `FR-PF`            | French Polynesia                     |             77 |        4824 | overseas collectivity                       |
| `TF`       | `FR-TF`            | French Southern and Antarctic Lands  |             78 |        5065 | overseas territory                          |
| `GP`       | `FR-GP` / `971`    | Guadeloupe                           |             88 |        4829 | overseas region                             |
| `MQ`       | `FR-MQ` / `972`    | Martinique                           |            138 |        4827 | overseas region                             |
| `YT`       | `FR-YT` / `976`    | Mayotte                              |            141 |        4797 | overseas region                             |
| `NC`       | `FR-NC`            | New Caledonia                        |            157 |        5538 | overseas collectivity with special status   |
| `RE`       | `FR-RE` / `974`    | Réunion                              |            180 |        4823 | overseas region                             |
| `PM`       | `FR-PM`            | Saint Pierre and Miquelon            |            187 |        4821 | overseas collectivity                       |
| `BL`       | `FR-BL`            | Saint-Barthélemy                     |            189 |        4794 | overseas collectivity                       |
| `MF`       | `FR-MF`            | Saint-Martin (French part)           |            190 |        4809 | overseas collectivity                       |
| `WF`       | `FR-WF`            | Wallis and Futuna                    |            243 |        4810 | overseas collectivity                       |

> The five **DROM** (Départements et régions d'outre-mer) — `GF`, `GP`, `MQ`, `RE`, `YT` — currently use **INSEE numeric codes** (`971`–`976`) as their `state_code` in `states.json`, while the overseas collectivities use the ISO 3166-2 alphabetic codes. Aligning the DROM to ISO 3166-2 alphabetic codes is tracked separately and is **out of scope** for this policy doc.

## Why we model both (rationale)

1. **ISO 3166 compliance.** Both representations are present in the standard. Removing either side would make the database fail a strict ISO conformance check that consumers commonly run.
2. **Downstream-consumer compatibility.** A large portion of API and package consumers — including [`@countrystatecity/countries`](https://www.npmjs.com/package/@countrystatecity/countries), [`countrystatecity-countries` (PyPI)](https://pypi.org/project/countrystatecity-countries/), and the [REST API](https://countrystatecity.in/) — filter and key off `country_code`. Code in the wild does things like `country_code === 'MQ'` to fetch all Martinique cities. Deleting `MQ` as a country would break those queries silently.
3. **Routing & locale data.** Phone codes, currencies, TLDs, and timezones often differ between an overseas territory and its metropolitan parent (e.g. `NC` uses `XPF`, not `EUR`; `PF` is `UTC-10`/`-9:30`/`-9`, not `UTC+1`). The country-level row carries that metadata.
4. **Geographic reality at the city level.** Cities physically located in Saint-Denis (Réunion) cannot be in the same bounding box as Paris. The country-level partition keeps coordinate validation (`.github/scripts/validate-coordinates.js`) honest.
5. **Reversibility.** Keeping both is additive. A future maintainer who decides to collapse one side can do so cleanly. The reverse — restoring deleted records and back-filling foreign keys across 153k+ cities — is not cleanly reversible.

In short: removing the country-level record (Option A in #1352) is a **breaking change** to fix a **labelling concern**, and the cost/benefit doesn't justify it.

## How downstream consumers should query

Pick the model that matches the question being asked.

### "Give me everything in the French Republic" (metropolitan + DROM + collectivities)

Use the `FR` country, then traverse via `state_id`:

```sql
SELECT c.*
FROM cities c
JOIN states s ON c.state_id = s.id
WHERE s.country_code = 'FR';   -- includes all 12 overseas territories
```

This works because every overseas territory has a state row whose `country_code = 'FR'`.

### "Give me only Martinique" (the territory in isolation)

Filter by the territory's own ISO 3166-1 country code:

```sql
SELECT * FROM cities WHERE country_code = 'MQ';
```

This is the form most API/SDK consumers already use, and it is the form this policy is designed to preserve.

### "Give me metropolitan France only" (exclude overseas)

Exclude the 12 overseas codes explicitly. The metropolitan vs. overseas split is a political/administrative distinction, not a data-model distinction:

```sql
SELECT * FROM cities
WHERE country_code = 'FR'
  AND state_code NOT IN ('GF','PF','TF','GP','MQ','YT','NC','RE','PM','BL','MF','WF',
                         '971','972','973','974','976');  -- INSEE for DROM
```

> A future cleanup may add a `metropolitan` boolean or `is_overseas` flag on `states` to make this query simpler. Not in scope here.

## Precedent: this is not new

The same dual-representation already applies to several other countries in this database. The `FR` work in #1352 brings France in line with the existing pattern.

| Parent | Territory                                  | `countries.iso2` | `states.id` | Notes                                         |
| :----- | :----------------------------------------- | :--------------- | ----------: | :-------------------------------------------- |
| `CN`   | Hong Kong SAR                              | `HK`             |        2267 | special administrative region                 |
| `CN`   | Macau SAR                                  | `MO`             |        2266 | special administrative region                 |
| `US`   | Puerto Rico                                | `PR`             |        1449 | outlying area                                 |
| `US`   | Guam                                       | `GU`             |        1412 | outlying area                                 |
| `US`   | American Samoa                             | `AS`             |        1424 | outlying area                                 |
| `US`   | Northern Mariana Islands                   | `MP`             |        1431 | outlying area                                 |
| `US`   | U.S. Virgin Islands                        | `VI`             |        1413 | outlying area                                 |
| `US`   | U.S. Minor Outlying Islands                | `UM`             |        1432 | outlying area                                 |
| `NO`   | Svalbard                                   | `SJ` (shared)    |        1013 | arctic region; Jan Mayen is state `1026`      |

### Known gaps (territories *only* modeled as countries)

For honest scoping, the following ISO 3166-1 entries are *not* currently dual-modeled as states of their administering country in this database. They may be candidates for similar treatment in the future, but are **out of scope** for this policy:

| Code   | Name                                  | Administered by      |
| :----- | :------------------------------------ | :------------------- |
| `GL`   | Greenland                             | Denmark (`DK`)       |
| `FO`   | Faroe Islands                         | Denmark (`DK`)       |
| `AW`   | Aruba                                 | Netherlands (`NL`)   |
| `CW`   | Curaçao                               | Netherlands (`NL`)   |
| `SX`   | Sint Maarten (Dutch part)             | Netherlands (`NL`)   |
| `BQ`   | Bonaire, Sint Eustatius and Saba      | Netherlands (`NL`)   |
| `AX`   | Åland Islands                         | Finland (`FI`)       |
| `BV`   | Bouvet Island                         | Norway (`NO`)        |
| `CC`   | Cocos (Keeling) Islands               | Australia (`AU`)     |
| `CX`   | Christmas Island                      | Australia (`AU`)     |
| `NF`   | Norfolk Island                        | Australia (`AU`)     |
| `HM`   | Heard Island and McDonald Islands     | Australia (`AU`)     |
| `GG`   | Guernsey                              | British Crown        |
| `JE`   | Jersey                                | British Crown        |
| `IM`   | Isle of Man                           | British Crown        |

These cases differ from the FR/US/CN ones because each carries its own political nuances (degree of autonomy, EU status, currency union, treaty arrangements). A blanket dual-modeling rule is **not** being adopted here. Each future case should be decided on its own merits, ideally tracked against an explicit issue.

## Future considerations

### Option A (full reclassify) — out of scope, documented for posterity

The original reporter on [#1352](https://github.com/dr5hn/countries-states-cities-database/issues/1352) suggested that Martinique (and by extension the other overseas territories) should be **only** a French region — i.e., delete the country-level row.

We considered this. It was rejected for the rationale-section reasons above. If a future maintainer revisits this decision, the migration would need:

1. A deprecation notice across all consumers (NPM, PyPI, REST API, Export Tool) with a 6+ month lead time.
2. A back-fill migration that rewrites every `cities.country_id` / `cities.country_code` reference for the 12 territories.
3. A versioning strategy on the database (e.g. `world.v2.sql`) so that consumers pinned to the old shape don't break.
4. Updates to `country-bounds.json` and the coordinate validator to handle the new "FR includes both metropolitan and tropical" bounding box (otherwise every Martinique city would fail validation).
5. Coordinated releases with [csc-export-tool](https://github.com/dr5hn/csc-export-tool), [countrystatecity-countries (NPM)](https://github.com/dr5hn/countrystatecity-countries), and [countrystatecity-pypi](https://github.com/dr5hn/countrystatecity-pypi).

That work is large and risky, and the **current dual-representation is internally consistent and ISO-compliant**. There is no functional defect today; only a labelling preference.

### Smaller follow-ups that *are* in scope (separate issues / PRs)

- Align the DROM `state_code` from INSEE numeric (`971`–`976`) to ISO 3166-2 alphabetic (`FR-GF`, `FR-GP`, …).
- Consider an `is_overseas` or `is_dependency` boolean on `states` so the metropolitan/overseas split is a simple filter rather than an explicit `IN (…)` list.
- Decide, case-by-case, whether to dual-model any of the "known gaps" above (Greenland, Aruba, etc.).

## Cross-references

- Issue: [#1352 — France data: missing cities and regions misclassified](https://github.com/dr5hn/countries-states-cities-database/issues/1352)
- Maintainer docs: [`.claude/CLAUDE.md`](.claude/CLAUDE.md) — see the *Important Rules* section.
- Contributor docs: [`contributions/README.md`](contributions/README.md)
- Related ISO standards: [ISO 3166-1](https://www.iso.org/iso-3166-country-codes.html) (countries), [ISO 3166-2](https://www.iso.org/standard/72483.html) (subdivisions).
