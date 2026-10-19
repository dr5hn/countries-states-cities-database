# Counties and intermediate administrative units

One JSON array per country in `<ISO2>.json`, following
[Administrative Structure Policy](../../ADMINISTRATIVE_STRUCTURE.md). This dataset holds official units between
an ISO 3166-2 state and a municipality: US counties and equivalents, French arrondissements, German Kreise, and
similar units. ISO-listed subdivisions stay in `states`; settlements stay in `cities`.

| Field | Shape | Rule |
| --- | --- | --- |
| `id` | positive integer | Assigned by MySQL; retain it on existing records. Omit on new records. |
| `name` | string, max 255 | Required. |
| `state_id`, `state_code` | positive integer, string | Required keys; the smallest containing ISO 3166-2 state and its code. Both `null` only for a county of several regions (v5.0.0, below). |
| `states` | list of `{state_id, state_code}` | Only on a county of several regions: every region it lies in, two or more, in `state_id` order. Absent on every other county. |
| `country_id`, `country_code` | positive integer, ISO2 string | Required; must match the state. |
| `type`, `type_local` | nullable string, max 191 | Standard English term and official local term. See the policy's allowed county types. |
| `level` | nullable integer | Depth in the country's official hierarchy, starting at 1. |
| `parent_id` | nullable positive integer | Another county directly above this unit; null when its parent is a state. |
| `latitude`, `longitude` | decimal strings | Required representative point inside the unit (copied from an open source, not necessarily a calculated centroid), within −90…90 and −180…180. |
| `native` | nullable string, max 255 | Native name. |
| `population` | nullable nonnegative integer | Population when known. |
| `timezone` | nullable string, max 255 | IANA timezone. |
| `translations` | nullable object | Language codes mapped to translated names. Stored as text in MySQL. |
| `wikiDataId` | nullable string | Wikidata Q-ID. |
| `created_at`, `updated_at`, `flag` | database-managed | Omit on new contributions. |

A city may carry a nullable **`county_id`**. Its county must exist in this directory and have the same `state_id`,
`country_id`, and `country_code` as the city; for a county of several regions the city's `state_id` must be one of
the county's `states`. Omit the field or use null when no link has been established; do not
infer links from names alone. Deleting a county sets its city links and child counties' `parent_id` to null.
The SQL Server export uses a noncascading parent FK; clear child parent links before deleting a parent there.
County IDs are globally unique across country files and independent of city IDs. Counties with a `parent_id`
need an explicit ID; the importer assigns IDs to new root counties before cities are imported.

Phase 2b assigns IDs to the existing 3,081 US records without changing their data. No city links are populated yet.
It does not complete Alaska coverage or replace historical county-equivalents; those remain separate data fixes.

**Counties of several regions (v5.0.0, decision B6).** A unit that lies in two or more ISO 3166-2 states, such as
New Zealand's district councils that cross regional boundaries, is one county record with `state_id` and
`state_code` both `null` and its regions listed in `states`:

```json
{"id": 14023, "name": "Waitomo District", "state_id": null, "state_code": null,
 "states": [{"state_id": 4060, "state_code": "MWT"}, {"state_id": 4061, "state_code": "WKO"}], ...}
```

It needs an explicit id. Its seat never decides where it is filed. In MySQL the list is the `county_states` table, one
row per `(county_id, state_id)`; the importer writes it and the sync rebuilds `states` from it. To list a state's
counties, include those whose `states` name it.

Import order is regions → subregions → countries → states → counties → cities → postcodes. County JSON exports
are flat `json/counties.json`; every export format provides a separate counties dataset. Reverse sync preserves
existing contribution field order, omitted nullable fields, and trailing-newline style while adding IDs. Older
inputs with no counties table or source file remain supported.
