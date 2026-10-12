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
   own `parent_id` and `level`. Counties carry a `state_id` the same way. Where a documented national reform has
   replaced the units ISO 3166-2 still lists, `state_id` follows the current national unit: the fix summary records the
   reform's date and sources and a dated old-to-new crosswalk of codes, names, scope and ISO mapping, marking any code
   the project assigned itself, and the state `type` uses the national category (an exception to rule 5). Vietnam since
   July 2025: 34 provincial states at level 1, communes, wards and special zones (`municipality / xã | phường | đặc khu`)
   at level 2 with no district tier; a former city keeps its own urban-place record rather than becoming a same-named
   new ward.
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
6. **A section keeps its official parent, or uses a documented urban-containment parent.** A neighbourhood, barrio,
   bairro, community area or barangay may be a `section`. In a statutory hierarchy a section keeps its official depth
   and its `parent_id` is its verified immediate parent in cities, or null when that parent is missing or in another
   dataset; a known tier is never skipped (a Philippine barangay under its city or municipality). A section can have
   its own elected government and official code: `section` says the unit sits inside a city or municipality, not that
   it has no government. **Urban-containment model:** for neighbourhoods a city publishes as parts of itself, the fix
   summary may record that the city is their parent, with `level` one below the city. This is a documented exception to
   rules 3 and 4, recorded per city (US neighbourhoods in #1967; Montevideo, a city at level 2 with its barrios at level
   3 under it). Adding municipio or ward records later does not silently replace these urban parents; that ancestry is
   documented separately. A city spanning several units is not by itself a reason to use this model.
7. **An intermediate unit and its place can both be kept, when both are verified.** Rules 1-2 decide where a unit goes;
   basic municipalities are not duplicated into counties. Where a unit is also a place people know as a city, as
   Indonesia's kota and China's county-level cities and urban districts, the unit goes in counties (matched to its
   official code in a source ledger) and an existing, verified city, seat town or urban part stays in cities, linked
   through `county_id` to its county in the same state. A place record is never created from a unit's name alone; it
   keeps its own identity and level (a kota city and its county are both level 2, the city's `parent_id` null under a
   state). A kota's city and county may share its own Wikidata item and a point that suits both; distinct places never
   share an item. Kecamatan, when added, sit at level 3, and desa and kelurahan are not linked straight to a kota.
8. **Points come from open sources, with a ledger.** `latitude` and `longitude` are copied only from an openly
   licensed source (Wikidata P625, CC0; GeoNames, CC BY 4.0; OpenStreetMap, ODbL; an official register under CC BY or
   OGL, naming its jurisdiction and version) or a source whose legal basis for copying is documented, and lie inside the
   record's own unit. A point checked by hand is still a copy of its source. Official geometry with no open licence or
   documented legal basis is used only for reference checks: no point is copied or generated from it. Each fix summary
   links a per-record ledger (record id, source feature and URL, edition, retrieval time and hash, method, licence or
   legal basis). Attribution, licence and modification notices travel with the exports, API and package documentation;
   OSM reuse also meets ODbL share-alike. Legacy points with unresolved rights stay listed as holds until replaced.

### City `type` values for countries that have been moved

| `type` | Meaning | `type_local` examples |
| --- | --- | --- |
| `municipality` | basic unit of local government (a territory in MX and GR, see [TYPE_FIELD.md](TYPE_FIELD.md)) | commune (FR), comune (IT), Gemeinde (DE), municipio (ES), município (BR), gmina (PL) |
| `city` | a place with official city status, or where the country has no finer category | Stadt (DE), city (US), shahr (IR) |
| `town` | an official town category | town (US), oraș (RO) |
| `village` | an official village category | village (US), sat (RO) |
| `locality` | a named populated place without its own government | census-designated place (US), localidad (MX) |
| `section` | a part of a municipality or city kept as its own record (rule 6) | commune déléguée (FR), barrio (ES), community area (US, Chicago), barangay (PH) |

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
China's prefectures and counties are still city records; they move to counties, with real cities kept as city
records under rule 7, starting with a pilot). Counties go into MySQL and the exports first (#1303 phase
2b); then countries are moved one at a time, matched to their official register by code, starting with France. Each
country's changes are documented under [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643).
