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


### Germany

Destatis GV-ISys Textkennzeichen describes the municipality's official legal class:
60 → `municipality / Markt`, 61 → `city / kreisfreie Stadt`, 62 → `city / Stadtkreis`,
63 → `city / Stadt`, 64 → `municipality / Gemeinde`, 67 → `city / große Kreisstadt`.
The class follows the Land's municipal law as recorded in the federal register, not a population threshold.
The 30 September 2026 edition and its GV100AD record description are the source of these codes.
Land is level 1; a current Regierungsbezirk adds a tier, as does a Kreis; an independent city skips the Kreis tier.
Gemeindeverbände are cooperative administrative bodies, not an extra territorial tier for these municipality rows.
A missing Kreis link is not filled by this classification patch. Sections and former municipalities cannot borrow a successor's class.
Sources: [Destatis GV-ISys](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/_inhalt.html),
Data licence Germany – attribution – version 2.0 (dl-de/by-2-0).

### Canada

Statistics Canada's census subdivision (CSD) type records the municipal designation adopted by provincial or territorial law;
it also includes statistical equivalents that must not be inferred to be legal municipalities.
For independently bound legal CSDs: CY/C → `city / city`, T/TV → `town / town`, VL → `village / village`,
V → `city / ville`, MÉ → `municipality / municipalité`, MU/M → `municipality / municipality`,
TP → `municipality / township`, CT → `municipality / canton`, P → `municipality / paroisse`,
DM → `municipality / district municipality`, RM → `municipality / rural municipality`,
MD → `municipality / municipal district`, HAM → `locality / hamlet`, SV → `village / summer village`,
SM → `municipality / specialized municipality`.
Unlisted classes, nonmunicipal statistical CSDs and ambiguous former municipalities remain held.
Province/territory is level 1; existing documented level 2 or 3 is retained, otherwise the province/CD/CSD hierarchy gives level 3.
A CSD and its same-named population centre are distinct entities; a CSD total or class is never assigned to the latter.
Sources: [2021 Census Dictionary, CSD](https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/definition-eng.cfm?ID=geo012),
2021 boundary attributes and 2025 CSD register, under the Statistics Canada Open Licence.

### Australia

In `AU.json`, an LGA row is the local-government territory: `municipality` at level 2,
with its jurisdiction-published status in `type_local` (for example City, Shire, Council,
Regional Council, Aboriginal Shire or Municipality). City status on an LGA does not make
it the separate town of that name. Bind a namesake row using its own Wikidata item,
official ABS LGA code/name/state and the unchanged point inside its LGA boundary.
A gazetted populated place is `locality` at level 3, with its gazetteer class in
`type_local`, only when name, state, point and its own place item agree.
The reviewed [AU type ledger](.github/fixes-docs/ledgers/types_au_v5x.jsonl) and
[shared source catalogue](.github/fixes-docs/ledgers/types_au_v5x.sources.json) retain
exact edition, retrieval date, source hash and attribution. Conflicting identity,
former-unit statements or an out-of-boundary point remain held; no coordinate, name,
identifier, parent or table change is authorized by this type correction.

### Mexico

Localidades at level 3 link by `parent_id` to their own level-2 municipio or Mexico City alcaldía city row; an official cabecera point may represent a municipio only when it lies inside that municipio, and its population is the municipio total.

In `MX.json`, `adm1` is a state-capital town, `adm2` a municipal-seat town (GeoNames PPLA2) and
`municipality` the municipal territory itself (GeoNames ADM2), so a municipality and its seat town can both
appear (e.g. Medellín and Medellín de Bravo). To list only settlements in Mexico, leave out `municipality`.

For reviewed rows, INEGI catalogue AMBITO U/R maps to `locality / localidad urbana` or `locality / localidad rural` at level 3; cabecera is a seat role and does not itself establish urban class. A legacy place-typed row is corrected to `municipality / municipio` at level 2 only when its literal v4 own item is the municipio (own P3801 and municipality class), the official code/name/state and current municipal polygon agree, and the unchanged point lies inside that territory. An item naming the seat cannot take its municipality's class.

### Greece

In `GR.json`, `municipality` is a municipal territory (e.g. Lake Plastiras, Pangaio), not a town, and Mount
Athos's monasteries are `religious`. To list only settlements in Greece, leave out `municipality`.

### Netherlands

In `NL.json`, `municipality` is a gemeente. A BAG woonplaats (a named place within a gemeente) is `city` when an official
source names that place itself as a city (the Rijksdienst voor het Cultureel Erfgoed's historic-city inventory or the
municipality's own publication, with no current municipal text calling it a village; see the
[evidence ledger](.github/fixes-docs/ledgers/NL_city_identity_2026-10.csv)), and `locality` otherwise; both keep
`type_local` `woonplaats`. This is a documented identity, not a legal status, as the Netherlands has no statutory city
category today. Older `city` records outside the woonplaats set (Eindhoven, Delft) were not reviewed, so `type = 'city'`
alone is not a complete list of Dutch cities; use the settlement filter below. Most
gemeente records are also the place itself (Haarlem, Hilversum) and belong in a settlement list. Eight records named
"Gemeente …" (Gemeente Groningen, Gemeente Stadskanaal …) are the municipal territory beside a separate record for the
town (Groningen, Stadskanaal). To list only settlements in the Netherlands, leave out the records whose name starts
with "Gemeente ".

### New Zealand

In `NZ.json`, settlements have no legal status. `type_local` keeps Stats NZ's 2026 urban-rural class and `type` follows
it: a major or large urban area is `city`, a medium or small urban area is `town`, a rural settlement is `locality` and a
suburb is `section`. A place the New Zealand Geographic Board lists as an official town (LINZ NZ Place Names, feature
type Town) or that its council names as a town is at least `town`, whatever its size class (Fairlie, Waiouru). The
classes are statistical sizes, not city status. District and city councils are county records (#2006).

### South Africa

In `ZA.json`, places have no legal town or city status. A place matched to a Statistics South Africa Census 2011 main
place is `locality` with `type_local` `main place`: a statistical class, not a legal status or a population threshold.
Local municipalities stored as cities are `municipality / local municipality` at level 3. Metropolitan and district
municipalities are county records; rows for them in `ZA.json` are typed `county` and wait for removal in v5.0.0.

### Kazakhstan

In `KZ.json`, the category is the one in the KATO classifier: `city / қала`, `town / кент`, `village / ауыл`. Cities
of republican significance are at level 1, of regional significance at 2 and of district significance at 3. A town or
village is at 3, or at 4 when it lies in a rural okrug; a "conditional" city or village administration in KATO is not
a unit and adds no level. Districts (аудан) are county records; rows for districts in `KZ.json` are typed `county`, and
their removal is queued for a major release. Where a district row and a county record share the district's own
Wikidata item, they are the same entity. `county_id` is the containing district, so a village in a rural okrug (level 4) links to
its district (level 2); `parent_id` is the record directly above, and is empty when that tier has no record.

### Tanzania

In `TZ.json`, a record that is itself a city, municipal or town council is `municipality` at level 2 with the
council's Swahili category (`Halmashauri ya Jiji`, `Halmashauri ya Manispaa`, `Halmashauri ya Mji`). A record of the
town or city a council is named after is not the council: it keeps its own identity and is not typed until a register
of settlements binds it. Levels follow the census hierarchy: region 1, district or council
2, division 3, ward (`section / kata`) 4. Rows for districts are typed `county / wilaya` at level 2, and their removal is
queued for a major release; Tanzania has no county records yet.

### United States

For reviewed US places, `type` follows the Census Bureau's official legal/statistical
area description (LSAD), rather than population size or county-seat status:
LSAD 25 is `city / city`, 43 `town / town`, 47 `village / village`, and
21 `borough / borough`. A census-designated place (LSAD 57, FUNCSTAT S) is
`locality / census designated place`, including large CDPs. Puerto Rico's
statistical places have LSAD 55 (`comunidad`) or 62 (`zona urbana`); all Puerto Rico
rows remain held here because municipio versus town identity is not proved.
Functioning minor civil divisions use their own legal category: towns, cities,
boroughs and villages as above; townships and plantations use `municipality`
with `type_local` `township` or `plantation`. These reviewed entities are level 3
under the state/county framework. GNIS populated-place names alone do not establish
legal incorporation or authorize a containing town's population.

A village or CDP inside a same-named town is a separate entity. Each binding must
agree with its row's own Wikidata GNIS (P590), FIPS (P774), or explicit instance
class (P31), without a conflicting identifier. Rows without an item cannot bind
a county subdivision with a nearby same-named place or CDP. Ambiguous matches,
duplicate keys on one Census entity, special consolidated governments and unproved
legacy identities stay held; this convention does not assert that every existing
US row is reviewed. Population 2020 is the count of the bound entity itself.
A missing county link is filled only when the whole entity belongs to one county.
See the [2024 Gazetteer LSAD and FUNCSTAT fields](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_place_national.zip),
[Census LSAD definitions](https://www.census.gov/library/reference/code-lists/legal-status-codes.html)
and the [per-record evidence ledger](.github/fixes-docs/ledgers/us_places_v5x.jsonl).

### Uruguay

In `UY.json`, a centro poblado's legal category maps to `city / ciudad`, `town / villa` or
`village / pueblo`; the existing `town / pueblo` spelling of the English category is corrected only
on independently bound rows. A census locality without an established finer legal category is
`locality / localidad`. These are categories, never population thresholds. The open INE
*Toponimia y categorización jurídica oficial de las localidades* register is historical (2004,
georeferenced 2025), so it alone does not establish a place's current legal status. Legislative
category acts, for example [Law 12,297 (25 de Agosto)](https://www.impo.com.uy/bases/leyes/12297-1956),
provide the legal basis for these terms. The [evidence ledger](.github/fixes-docs/ledgers/uy_types_v5x.jsonl)
keeps each applied category and any field held for further legal review.
A `municipality / municipio` denotes the territorial local-government unit established under
[Law 19,272](https://www.impo.com.uy/bases/leyes/19272-2014), at level 2 beneath the departamento
(level 1). Its seat locality is a different entity; locality census counts are never municipal counts.
A locality wholly within one municipio has level 3; a locality outside the municipal layer has
level 2. Partial overlaps and localities crossing municipios have their level held for review.
The documented Montevideo urban-containment model keeps the city at level 2 and its official
`section / barrio` records at level 3, with Montevideo as their city parent. Barrios are not
independent census localities and do not receive Montevideo's total population.
`parent_id` should identify the verified immediate same-dataset parent, or be null when that
parent has no record. This patch makes no ancestry changes; containment alone is not a reviewed parent link. Legacy `adm1` rows remain held where their unit/place identity
cannot be reconciled under the published model; no unit is relabelled as its seat.
Population uses INE's `POB_TOT_23`: persons enumerated by the census operation or administrative
enumeration, excluding people experiencing street homelessness. It is not the departamento total.
INE permits free reuse with source attribution in the dataset's embedded metadata; the ledger
retains that notice, the Uruguay Open Data Licence reference, edition, retrieval time and checksums.

### Ukraine

For independently bound Ukrainian rows, the Ministry's KATOTTH codifier
(7 July 2026, Order 1321; original Order 290 of 26 November 2020,
category appendix in the edition of Order 48 of 19 January 2024) maps
M (М) to `city / місто`, X (Х) to `town / селище`, and C (С) to
`village / село`. The codifier uses Latin category letters. X is the current
settlement category, including former urban-type settlements; an old urban-type
label alone does not establish today's category.
Ordinary settlements are level 4: oblast 1, raion 2, hromada 3, settlement 4.
K is `city / місто, що має спеціальний статус` at level 1 (Kyiv or Sevastopol).
B, район у місті, maps to `section / район у місті`; a district directly
under a special-status city is level 2. P, район, belongs in counties at level 2;
H, територіальна громада, is the basic municipality at level 3; O denotes
an oblast or the Autonomous Republic of Crimea at level 1 in states.
These unit categories never authorize replacing a unit with its seat.
Legacy or reformed units whose v4 scope is unproved remain held in this regular release.
Only type, local type and level change; the territorial policy and stored membership stay in force.
The [compact ledger](.github/fixes-docs/ledgers/types_ua_v5x.jsonl) records applied bindings and official-bound holds.
Sources: [Ministry codifier and category appendix](https://mininfra.gov.ua/diialnist/rozvytok-mistsevoho-samovriaduvannia/kodyfikator-administratyvno-terytorialnykh-odynyts-ta-terytorii-terytorialnykh-hromad),
CC BY 4.0. Wikidata's KATOTTH property is P9435, and KOATUU is P1077.

### Portugal

Reviewed concelhos use `municipality / município` at level 2; current freguesias
use `section / freguesia` at level 3, beneath the district or autonomous region
(level 1) and municipality (level 2). A freguesia is a territorial unit with its
own government, not automatically its same-named settlement.
Legal cidades use `city / cidade` and vilas `town / vila`, at level 3 under
PT.json's existing place convention; lugares use `locality / lugar` at level 4.
Legal place status does not establish that the place is a civil parish.
A cidade or vila requires its dated elevation law; population and administrative-seat
status do not determine the category. Santa Catarina da Serra is a vila under
[Lei n.º 65/2001, de 12 de julho](https://files.diariodarepublica.pt/1s/2001/07/160a00/42374237.pdf).
A municipality and its seat can share a name: the row's own Wikidata item,
own P6324 (DICOFRE) code, official CAOP name/district and containing boundary
decide its identity. A former parish cannot borrow a current successor's class.
Conflicting codes, ambiguous identities, and unproved literal v4 continuity remain held.
Only type, local type and level change; existing ancestry and membership are retained.
The [compact ledger](.github/fixes-docs/ledgers/types_pt_v5x.jsonl) records changed rows
and holds with an official binding; its adjacent sources registry records revisions,
editions, licence notices, retrieval dates and exact response hashes.
Source: DGT [CAOP2025](https://www.dgterritorio.gov.pt/atividades/cartografia/cartografia-tematica/caop),
licence **CC-BY 4.0**. DGT's exact licence statement is preserved in the sources registry:
reuse is free, with attribution to Direção-Geral do Território. Island containment uses
Esri Portugal's CAOP2025 mirror under CC-BY-4.0; no geometry or points are copied into rows.

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
In Vietnam, also exclude `municipality`: since the July 2025 reform it is a commune, ward or special zone (`xã`, `phường`,
`đặc khu`) directly under the province, a territory formed from several old units; former cities and towns stay as
`city` / `đô thị loại II` and `town` / `đô thị loại III` urban places (#1977).
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
AND (country_code NOT IN ('MX', 'GR', 'VN') OR type IS NULL OR type <> 'municipality')  -- MX/GR/VN municipality = territory
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
    && !(['MX', 'GR', 'VN'].includes(c.country_code) && c.type === 'municipality') // MX/GR/VN municipality = territory
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
- [Disputed and special territories](DISPUTED_AND_SPECIAL_TERRITORIES.md)

### China city hierarchy depth

CN city `level` follows depth in the official hierarchy: prefecture 2, county-level unit 3, township 4.
County-level units directly under a province-level municipality or a province are 2 (for example the districts and counties of Beijing, Tianjin, Shanghai and Chongqing, and Hainan's directly administered county-level cities and counties); their townships are 3, as are townships directly under no-county prefectures such as Dongguan and Zhongshan.
Unproved tiers, own-item/type conflicts and excluded territories remain held in the [per-record ledger](.github/fixes-docs/ledgers/cn_levels_v5x.jsonl).
Where any row of a linked prefecture group was not proved, the whole group keeps its older levels (prefecture 1, county-level 2) for now, so no parent link skips or repeats a level; 58 of the 335 prefecture rows are in such groups, including Jiayuguan, whose three districts were abolished in 2019, and Jiangmen, Dongguan and Zhongshan in Guangdong.
