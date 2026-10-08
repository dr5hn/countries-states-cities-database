# Administrative Structure Policy

> **Status:** Active policy, decided by the maintainer on 8 October 2026 under
> [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643).
> **Scope:** what `state_id`, `county_id`, `level`, `parent_id`, `type` and `type_local` mean for states, counties and
> cities, so every country's records follow that country's own administrative structure. The current city `type`
> values and how to filter settlements are described in [TYPE_FIELD.md](TYPE_FIELD.md).

## Why

Countries are organised differently: France has régions, départements, arrondissements and communes; Germany has
Länder, Kreise and Gemeinden; the United States has states, counties and places. A random accuracy sample in October
2026 found city locations, names and time zones over 97% correct, but `type` right for only 16% of cities and the
unit above a city recorded for only 23%. These rules say how each field captures the official structure.

## Three datasets

| Dataset | Holds | Example (France) |
| --- | --- | --- |
| `contributions/states/` | ISO 3166-2 subdivisions | région, département |
| `contributions/counties/` | official units between the state and the municipality that ISO 3166-2 does not list | arrondissement |
| `contributions/cities/` | municipalities, settlements and parts of them | commune, commune déléguée |

The counties dataset was started for US counties in
[#1303](https://github.com/dr5hn/countries-states-cities-database/issues/1303) and is extended to every country.
Counties reach MySQL and every export format in #1303 phase 2b, with optional city `county_id` links.
API support and country-by-country link population follow separately.

## The rules

1. **`state_id` is the smallest ISO 3166-2 unit that contains the place.** For France that is the département, for
   Spain and Italy the province. The units above it (région, comunidad autónoma) are linked through the states'
   own `parent_id` and `level`. Counties carry a `state_id` the same way.
2. **Official units that ISO 3166-2 does not list are county records.** Arrondissements, Kreise, US counties and
   similar units go in `contributions/counties/<country>.json`. A city links to the county that contains it through
   `county_id` (nullable, added with #1303 phase 2b). Counties that ISO lists, such as Ireland's, stay states.
3. **`level` is the depth in the country's official hierarchy**, with 1 directly under the country. It has the same
   meaning in all three datasets: in France a région is 1, a département 2, an arrondissement 3, a commune 4, a
   commune déléguée 5.
4. **`parent_id` points to the unit directly above within the same dataset.** A state points to the state above it,
   a county to the county above it (where a country has two county tiers), and a city to the city above it (a
   commune déléguée to its commune). It is null when the unit directly above is in another dataset.
5. **`type` is a standard English term; `type_local` is the official local term.** City and county `type` values come
   from the lists below, so apps can compare countries; `type_local` keeps the country's own word. For states `type`
   stays the ISO 3166-2 category and `type_local` holds the national term.

### City `type` values for countries that have been moved

| `type` | Meaning | `type_local` examples |
| --- | --- | --- |
| `municipality` | basic unit of local government (a territory in MX and GR, see [TYPE_FIELD.md](TYPE_FIELD.md)) | commune (FR), comune (IT), Gemeinde (DE), municipio (ES), município (BR), gmina (PL) |
| `city` | a place with official city status, or where the country has no finer category | Stadt (DE), city (US), shahr (IR) |
| `town` | an official town category | town (US), oraș (RO) |
| `village` | an official village category | village (US), sat (RO) |
| `locality` | a named populated place without its own government | census-designated place (US), localidad (MX) |
| `section` | a part of a municipality kept as its own record | commune déléguée (FR), barrio (ES) |

### County `type` values

| `type` | Meaning | `type_local` examples |
| --- | --- | --- |
| `county` | a county | county (US) |
| `parish`, `borough`, `census area` | US county-equivalents already in the dataset | parish (LA), borough (AK) |
| `administrative district` | any other unit between the state and the municipality | arrondissement (FR), Kreis (DE), raion (RU), tehsil (IN) |

A new value needs a maintainer decision and an entry here.

## Example: Strasbourg, once France is moved

Today Strasbourg (id 47110) is a city typed `adm1` with no `level`; this is the target.

| Record | Dataset | `type` | `type_local` | `level` | Linked to |
| --- | --- | --- | --- | --- | --- |
| Grand-Est (FR-GES) | states | metropolitan region | région | 1 | — |
| Bas-Rhin (FR-67) | states | metropolitan department | département | 2 | `parent_id` → Grand-Est |
| Arrondissement de Strasbourg | counties | administrative district | arrondissement | 3 | `state_id` → Bas-Rhin |
| Strasbourg | cities | municipality | commune | 4 | `state_id` → Bas-Rhin, `county_id` → Arrondissement de Strasbourg |

## Rollout

Existing records still carry older values (many cities say `city` or `adm1`–`adm5`, most states have no `level`, and
China's prefectures and counties are still city records). Counties go into MySQL and the exports first (#1303 phase
2b); then countries are moved one at a time, matched to their official register by code, starting with France. Each
country's changes are documented under [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643).
