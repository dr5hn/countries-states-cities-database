# The `cities.type` field

Every city record carries an optional `type` field describing what kind of
place it is. This page explains where the values come from, what each one
means, and how to filter the dataset down to genuine settlements.

> **Why this exists:** `type` is inherited from the upstream
> [GeoNames](https://www.geonames.org/) feature classification. It mixes two
> different ideas — *what a place is* (`city`, `town`, `village`) and *what
> administrative role it fills* (`adm2`, `county`, `parish`). The same place
> can be tagged either way depending on whether it is also the seat of an
> administrative division. For example, **Dallas** is `adm2` because it is the
> seat of Dallas County, and major Australian cities are `adm1` because they
> are seats of state-level governments. Cleanup of this inconsistency is
> tracked in [#1303](https://github.com/dr5hn/countries-states-cities-database/issues/1303).

## Moving to official categories

Countries are being moved, one at a time, to their official administrative categories
([ADMINISTRATIVE_STRUCTURE.md](ADMINISTRATIVE_STRUCTURE.md)): city `type` becomes a standard English term
(`municipality`, `city`, `town`, `village`, `locality`, `section`), a new `type_local` field keeps the official local
term (commune, Gemeinde, municipio), and units between the state and the municipality (arrondissements, Kreise,
counties) move to the separate `contributions/counties/` dataset. Until a country is moved, its records keep the
values below.

## All values

There are **35 distinct values** across **156,025** city rows. Counts are a
snapshot (2026-05-24) and drift as the data evolves — treat them as
approximate.

| `type` | Count | Settlement? | Meaning |
|---|---:|:---:|---|
| `city` | 96,098 | ✅ | Actual settlements |
| `adm2` | 20,796 | ✅ | 2nd-order admin division — usually a real city that is also a county/district seat (e.g. Dallas) |
| `adm3` | 15,774 | ✅ | Mostly real municipalities/communes (small towns) tagged with their admin role |
| `section` | 5,346 | ✅ | Suburbs and districts of larger cities |
| `county` | 4,409 | ❌ | County-level admin unit — not a settlement |
| `adm4` | 3,909 | ✅ | Similar mix to `adm3` |
| `adm1` | 3,505 | ✅ | 1st-order admin division — usually a state/region seat (e.g. major AU cities) |
| `district` | 2,381 | ✅ | District-level populated place |
| _(null)_ | 1,900 | ⚠️ | No type assigned — see [Records with no type](#records-with-no-type) |
| `regency` | 390 | ❌ | Indonesian *kabupaten* — admin division |
| `prefecture` | 369 | ❌ | Prefecture-level admin division |
| `locality` | 319 | ✅ | Named populated place |
| `capital` | 281 | ✅ | National/regional capital |
| `municipality` | 209 | ✅ | Municipality |
| `parish` | 80 | ❌ | Louisiana-style parish (= county) |
| `banner` | 52 | ❌ | Inner Mongolia *banner* — admin division |
| `town` | 48 | ✅ | Town |
| `province` | 36 | ❌ | Province-level admin division |
| `adm5` | 16 | ✅ | 5th-order admin division (populated) |
| `abandoned` | 15 | ❌ | Abandoned place — not a live settlement |
| `cities` | 13 | ✅ | Data artifact of `city` |
| `area` | 12 | ❌ | Generic administrative area |
| `village` | 10 | ✅ | Village |
| `historical` | 9 | ❌ | Historical place — not a live settlement |
| `settlement` | 9 | ✅ | Settlement |
| `oblast` | 8 | ❌ | Oblast — admin division |
| `gov_seat` | 6 | ✅ | Government seat (populated) |
| `special municipality` | 6 | ✅ | Special municipality |
| `administrative zone` | 5 | ❌ | Administrative zone |
| `region` | 4 | ❌ | Region-level admin division |
| `destroyed` | 3 | ❌ | Destroyed place — not a live settlement |
| `township` | 3 | ✅ | Township |
| `religious` | 2 | ❌ | Religious site — not a settlement |
| `subdistrict` | 1 | ✅ | Subdistrict (populated) |
| `historical_capital` | 1 | ❌ | Former capital — not a live settlement |


### Mexico

In `MX.json`, `adm1` is a state-capital town, `adm2` a municipal-seat town (GeoNames PPLA2) and
`municipality` the municipal territory itself (GeoNames ADM2), so a municipality and its seat town can both
appear (e.g. Medellín and Medellín de Bravo). To list only settlements in Mexico, leave out `municipality`.

### Greece

In `GR.json`, `municipality` is a municipal territory (e.g. Lake Plastiras, Pangaio), not a town, and Mount
Athos's monasteries are `religious`. To list only settlements in Greece, leave out `municipality`.

### Netherlands

In `NL.json`, `municipality` is a gemeente and `locality` a BAG woonplaats (a named place within a gemeente). Most
gemeente records are also the place itself (Haarlem, Hilversum) and belong in a settlement list. Eight records named
"Gemeente …" (Gemeente Groningen, Gemeente Stadskanaal …) are the municipal territory beside a separate record for the
town (Groningen, Stadskanaal). To list only settlements in the Netherlands, leave out the records whose name starts
with "Gemeente ".

## Filtering to genuine settlements

For use cases like *"find the nearest city, town, or village to a location"*,
exclude the admin-only and non-place types. An **exclusion list** is more
robust than an include list, because any new settlement-style value added in
future is kept by default.

**Exclude these types:**

```
county, regency, prefecture, parish, banner, province, area, oblast,
administrative zone, region, abandoned, historical, destroyed, religious,
historical_capital
```

In Mexico and Greece, also exclude `municipality` (the municipal territory; see [Mexico](#mexico), [Greece](#greece)).
In the Netherlands, exclude the records named "Gemeente …" (see [Netherlands](#netherlands)).

### SQL

```sql
SELECT *
FROM cities
WHERE (
  type IS NULL          -- keep null-type rows (see "Records with no type")
  OR type NOT IN (
    'county', 'regency', 'prefecture', 'parish', 'banner', 'province',
    'area', 'oblast', 'administrative zone', 'region',
    'abandoned', 'historical', 'destroyed', 'religious', 'historical_capital'
  )
)
AND (country_code NOT IN ('MX', 'GR') OR type IS NULL OR type <> 'municipality')  -- MX/GR municipality = territory
AND NOT (country_code = 'NL' AND name LIKE 'Gemeente %')  -- NL municipal territory beside its town
AND latitude IS NOT NULL
AND longitude IS NOT NULL;
```

> **Note on `NULL`:** `type NOT IN (...)` evaluates to `UNKNOWN` (not `TRUE`)
> for rows where `type` is `NULL`, so it would silently drop them. The
> explicit `type IS NULL OR ...` keeps null-type rows, matching the
> JavaScript filter below. Drop the `type IS NULL` clause if you'd rather
> exclude them.

### JavaScript

```js
const EXCLUDED_TYPES = new Set([
  'county', 'regency', 'prefecture', 'parish', 'banner', 'province',
  'area', 'oblast', 'administrative zone', 'region',
  'abandoned', 'historical', 'destroyed', 'religious', 'historical_capital',
]);

const settlements = cities.filter(
  (c) => !EXCLUDED_TYPES.has(c.type)
    && !(['MX', 'GR'].includes(c.country_code) && c.type === 'municipality') // MX/GR municipality = territory
    && !(c.country_code === 'NL' && c.name.startsWith('Gemeente ')) // NL municipal territory beside its town
    && c.latitude != null && c.longitude != null
);
```

This keeps all `city`/`adm*`/`town`/`village`/`section`/`locality`-style rows
(including admin seats like Dallas and Sydney) while dropping pure
administrative units and defunct places.

### Records with no type

About **1,900** rows have a `null` type. They are a mix of legitimate places
and unclassified entries. For strict settlement queries, the safest signal is
the presence of valid coordinates (`latitude`/`longitude` not null), and —
where available — a non-null `population`.

## Related

- [#1303 — Counties should be returned separately from cities](https://github.com/dr5hn/countries-states-cities-database/issues/1303) (tracking the cleanup)
- [Administrative structure policy](ADMINISTRATIVE_STRUCTURE.md) (official categories, `type_local`, `level`, `parent_id`, the counties dataset)
- [Multi-level territories policy](MULTI_LEVEL_TERRITORIES.md)
