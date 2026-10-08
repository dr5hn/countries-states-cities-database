# Administrative Structure Policy

> **Status:** Active policy, decided by the maintainer on 8 October 2026 under
> [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643).
> **Scope:** what `state_id`, `level`, `parent_id`, `type` and `type_local` mean for states and cities, so every
> country's records follow that country's own administrative structure. The current `type` values and how to filter
> settlements are described in [TYPE_FIELD.md](TYPE_FIELD.md).

## Why

Countries are organised differently: France has régions, départements, arrondissements and communes; Germany has
Länder, Kreise and Gemeinden; the United States has states, counties and places. A random accuracy sample in October
2026 found city locations, names and time zones over 97% correct, but `type` right for only 16% of cities and the
unit above a city recorded for only 23%. These rules say how each field captures the official structure.

## The rules

1. **`state_id` is the smallest ISO 3166-2 unit that contains the place.** For France that is the département, for
   Spain and Italy the province. The units above it (région, comunidad autónoma) are linked through the states'
   own `parent_id` and `level`.
2. **`level` is the depth in the country's official hierarchy**, with 1 directly under the country. It has the same
   meaning in states and cities: in France a région is 1, a département 2, an arrondissement 3, a commune 4 (a
   commune déléguée 5).
3. **Official units that ISO 3166-2 does not list are city records.** Arrondissements, Kreise, US counties and similar
   units between the state and the municipality are stored in `contributions/cities/` with the type
   `administrative district` or `county`, their `level`, and `parent_id` links. ISO 3166-2 units always stay in
   `contributions/states/`. Apps that want places only leave these types out (see [TYPE_FIELD.md](TYPE_FIELD.md)),
   which also returns counties separately from cities
   ([#1303](https://github.com/dr5hn/countries-states-cities-database/issues/1303)).
4. **`parent_id` points to the unit directly above, in the same table.** A state points to the state above it. A city
   points to the city record above it (an administrative district, or the municipality for a sub-municipal unit). It
   is null when the unit directly above is the record's state.
5. **`type` is a standard English term; `type_local` is the official local term.** For cities `type` comes from the
   list below, so apps can compare countries; `type_local` keeps the country's own word. For states `type` stays the
   ISO 3166-2 category and `type_local` holds the national term.

### City `type` values for countries that have been moved

| `type` | Meaning | Place or unit | `type_local` examples |
| --- | --- | --- | --- |
| `municipality` | basic unit of local government | place, except where [TYPE_FIELD.md](TYPE_FIELD.md) notes a territory (MX, GR) | commune (FR), comune (IT), Gemeinde (DE), municipio (ES), município (BR), gmina (PL) |
| `city` | a place with official city status, or where the country has no finer category | place | Stadt (DE), city (US), shahr (IR) |
| `town` | an official town category | place | town (US), oraș (RO) |
| `village` | an official village category | place | village (US), sat (RO) |
| `locality` | a named populated place without its own government | place | census-designated place (US), localidad (MX) |
| `section` | a part of a municipality kept as its own record | place | commune déléguée (FR), barrio (ES) |
| `administrative district` | an administrative unit between the state and the municipality | unit | arrondissement (FR), Kreis (DE), raion (RU), tehsil (IN) |
| `county` | a county | unit | county (US, IE) |

A new value needs a maintainer decision and an entry here and in [TYPE_FIELD.md](TYPE_FIELD.md).

## Example: Strasbourg, once France is moved

Today Strasbourg (id 47110) is typed `adm1` with no `level`; this is the target.

| Record | Table | `type` | `type_local` | `level` | Linked to |
| --- | --- | --- | --- | --- | --- |
| Grand-Est (FR-GES) | states | metropolitan region | région | 1 | — |
| Bas-Rhin (FR-67) | states | metropolitan department | département | 2 | `parent_id` → Grand-Est |
| Arrondissement de Strasbourg | cities | administrative district | arrondissement | 3 | `state_id` → Bas-Rhin |
| Strasbourg | cities | municipality | commune | 4 | `state_id` → Bas-Rhin, `parent_id` → Arrondissement de Strasbourg |

## Rollout

Existing records still carry older values (many cities say `city` or `adm1`–`adm5`, and most states have no `level`).
Countries are moved to these rules one at a time, matched to their official register by code, starting with France;
each country's changes are documented under [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643).
