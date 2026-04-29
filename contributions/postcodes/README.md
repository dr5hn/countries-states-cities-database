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

Each country file is sourced from one of:

| Source | License | Countries covered |
|--------|---------|-------------------|
| **OpenPLZ API** (https://openplzapi.org) | **ODbL-1.0** (matches this repo) | DE, AT, CH, LI |
| **Wikidata P281** (SPARQL) | **CC-0** | Long tail of states/regions globally |
| **US Census ZCTA** | Public domain | US |
| **India Post pincode CSV** | Open (gov.in) | IN |
| **Japan Post KEN_ALL.csv** | Free (no formal license) | JP |
| **France La Poste** (data.gouv.fr) | etalab-2.0 | FR |
| **Australia Post Boundaries** | CC-BY 4.0 | AU |
| **Statistics Canada FSA** | Open Government | CA |

The `source` field on each record records which pipeline produced it, so attribution can be programmatically assembled at export time.

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
