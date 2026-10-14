# Postcodes Contributions

Source-of-truth JSON files for the `postcodes` table introduced in #1039.

One file per country, named by ISO2 code: `LI.json`, `US.json`, `DE.json`, etc.

## Schema

Each record is a JSON object with the following fields:

```json
{
  "code": "9490",
  "country_id": 124,
  "country_code": "LI",
  "state_id": 2257,
  "state_code": "11",
  "city_id": null,
  "locality_name": "Vaduz",
  "type": "full",
  "latitude": "47.14151000",
  "longitude": "9.52154000",
  "source": "openplz",
  "wikiDataId": "Q1844"
}
```

### Field reference

| Field | Required | Notes |
|-------|----------|-------|
| `code` | yes | The postal code value (alphanumeric, country-specific). varchar(20). |
| `country_id` | yes | FK → `countries.id` |
| `country_code` | yes | ISO2, denormalised for fast filtering |
| `state_id` | no | FK → `states.id`. May be `null` for country-only postcodes or postcodes that span multiple states. |
| `state_code` | no | Denormalised state code |
| `city_id` | no | FK → `cities.id`. Often `null`; many postcodes don't map cleanly to existing cities. |
| `locality_name` | no | Human-readable place name (may differ from `cities.name`) |
| `type` | no | Granularity: `full` \| `outward` \| `sector` \| `district` \| `area` |
| `latitude`, `longitude` | no | Centroid of the postcode area, decimal |
| `source` | no | Originating data source — for license/attribution tracking (`openplz`, `wikidata`, `census`, etc.) |
| `wikiDataId` | no | Wikidata Q-ID for cross-referencing |

### Auto-managed fields

**Do NOT include** `id`, `created_at`, `updated_at`, or `flag`. MySQL assigns these.

## Sourcing Plan (Combo B, GeoNames-free)

> **Scope note:** the table below documents only the **original 8 launch sources**.
> Since launch, community-contributed pipelines have added postcodes for
> 100+ more countries — this directory now holds 125 country files with **85
> distinct `source` tag values** in the data. Most of those later tags are
> informal per-contributor pipeline names (e.g. `sepomex-via-redrbrt-2016`,
> `maltapost-via-lucamuscat`) whose licenses are **not yet audited or recorded
> here**. Do not assume a `source` tag not listed below carries an
> ODbL/CC-0/public-domain-equivalent license just because it's in this repo.
>
> **Known risk — Wikipedia/Wikidata conflation:** several small-territory
> files use `source` values like `wikipedia-small-territory` or
> `wikipedia-singleton-territory` (content drawn from Wikipedia, **CC-BY-SA
> 4.0**, share-alike). These are easy to misread as `wikidata` (**CC-0**, no
> attribution/share-alike obligations) in the table below — they are not the
> same license and must not be conflated when assembling attribution.
>
> A full per-`source`-tag license audit — recorded as structured data
> (JSON/YAML), not prose, so a script can consume it reliably — is separate
> follow-up work and has not been done yet. Until that exists, do not build
> an automated attribution-assembly step off this table.

Each of the original 8 launch country files was sourced from one of:

| Source | License | Countries covered |
|--------|---------|-------------------|
| **OpenPLZ API** (https://openplzapi.org) | **ODbL-1.0** (matches this repo) | DE, AT, CH, LI |
| **Wikidata P281** (SPARQL) | **CC-0** | Long tail of states/regions globally |
| **US Census ZCTA** | Public domain | US |
| **India Post pincode CSV** | Open (gov.in) | IN |
| **Japan Post KEN_ALL.csv** | Free (no formal license) | JP |
| **France La Poste** (data.gouv.fr) | etalab-2.0 | FR |
| ~~Australia Post Boundaries~~ (launch claim, never confirmed; see the note below) | — | AU |
| **Statistics Canada FSA** | Open Government | CA |

**Australia (since #1973):** the launch file came from a community copy of Australia Post data that is not licensed
for redistribution, so its names and points were removed. Codes now come from the Australian Bureau of Statistics Postal
Areas 2021 (`abs-poa-2021`; © Commonwealth of Australia (ABS), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)),
the GeoNames postal code dump (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)) and,
for single codes, Wikidata (CC0) and a CC BY 4.0 publication. ABS postal areas are a statistical approximation, not
Australia Post's delivery list.

**Spain (since #1974):** the earlier ES rows held INE municipality codes, not postcodes, and were replaced. Codes come
from CartoCiudad's province address files, edition 04/2026 (`cartociudad`; Centro de Descargas del CNIG,
https://centrodedescargas.cnig.es/CentroDescargas/cartociudad, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).
Credit: "Obra derivada de CartoCiudad 2026 CC-BY 4.0 scne.es". Modification: addresses aggregated to one row per postcode
with its province, single municipality and mean point; per-code ledger in
`.github/fixes-docs/ledgers/ES_postcodes_cartociudad_2026-04.csv`. This is the source's observed address coverage, not
Correos' delivery list.

**Portugal (since October 2026):** the earlier PT rows came from a CTT-derived compilation whose redistribution basis
was not established. Locality names and points now come from the GeoNames postal code dump of 13 October 2026
(`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)). Credit: "Source: GeoNames,
Portuguese postal code dump, 13 October 2026". Modification: only codes CSC already had are kept; a code whose dump rows
give different localities or points has that field left empty; regions are mapped to CSC states by GeoNames' published
code table; city links are rebuilt only where one same-named city lies inside the code's municipality. Points are
GeoNames' estimates, not delivery-area centroids. Edition ledger:
`.github/fixes-docs/ledgers/PT_postcodes_geonames_2026-10.sources.json`. 1,112 codes the dump does not list are queued
for removal in v5.0.0; they keep their earlier values until then.

**Mexico (since October 2026):** the earlier MX rows came from a 2016 mirror of SEPOMEX data whose redistribution basis
was not established. Each row is one postcode and settlement (asentamiento). Names and points now come from the GeoNames
postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)).
Credit: "Source: GeoNames, Mexican postal code dump, 13 October 2026". Modification: a row is kept only when the dump
lists its settlement under the same code (exactly, or after an accent, case and punctuation fold); it takes that
row's name, point and state. Points are GeoNames' estimates. Edition ledger:
`.github/fixes-docs/ledgers/MX_postcodes_geonames_2026-10.sources.json`. 451 rows whose settlement or code the dump
does not list are queued for removal in v5.0.0; they keep their earlier values until then.

The `source` field on each record records which pipeline produced it. For the
125 country files now present, that field is **not yet** sufficient on its
own to programmatically assemble attribution — see the scope note above.

## Adding a Country

1. Source the data from one of the providers above (or another with a compatible license — ODbL, CC-0, CC-BY, etalab, or public domain).
2. Transform into the JSON shape above. Each row needs `code`, `country_id`, `country_code` at minimum.
3. Resolve `country_id` from `contributions/countries/countries.json` (look up by `iso2`).
4. Resolve `state_id` from `contributions/states/states.json` where possible (fuzzy match on state name; leave `null` if uncertain).
5. Set `source` to the pipeline name (e.g. `openplz`).
6. Save as `contributions/postcodes/{ISO2}.json`.
7. Open a PR. The PR validator will check FK integrity and basic schema.

## Out of Scope

- **Edits to existing `cities` / `states` / `countries` records** — postcodes are additive only.
- **Filling every postcode worldwide** — start with countries that have clean, redistributable data. Skip UK Royal Mail PAF, Eircode, Deutsche Post (paid/restricted).
- **Address-level data** — this repo is geographic, not address-level. Postcodes are the leaf granularity.

See `.github/fixes-docs/FIX_1039_POSTCODES_TABLE.md` for the architecture decision record.
