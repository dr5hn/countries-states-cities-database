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

**Sweden (since October 2026):** the earlier SE rows came from a copy of the postcode list (zegl/sweden-zipcode) whose
redistribution basis was not established. Names, points and states now come from the GeoNames postal code dump of
13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)). Credit: "Source:
GeoNames, Swedish postal code dump, 13 October 2026". A row is kept when the dump lists its code. A field the dump's rows disagree on is left
empty. Edition ledger: `.github/fixes-docs/ledgers/SE_postcodes_geonames_2026-10.sources.json`. 2 rows the
dump does not list are queued for removal in v5.0.0; they keep their earlier values until then.

**Romania (since October 2026):** the earlier RO rows came from a copy of the postcode list (alexionegit/coduripostaleRomaniaPS) whose
redistribution basis was not established. Names, points and states now come from the GeoNames postal code dump of
13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)). Credit: "Source:
GeoNames, Romanian postal code dump, 13 October 2026". A row is kept when the dump lists its code. A field the dump's rows disagree on is left
empty. Edition ledger: `.github/fixes-docs/ledgers/RO_postcodes_geonames_2026-10.sources.json`. 12 rows the
dump does not list are queued for removal in v5.0.0; they keep their earlier values until then. The dump writes
Romanian with the legacy cedilla letters ş ţ Ş Ţ; CSC stores them as the correct comma-below ș ț Ș Ț, and changes
nothing else in a label.

**Poland (since October 2026):** the earlier PL rows came from a copy of the postcode list (mberezinski/kody-pocztowe-geo) whose
redistribution basis was not established. Names, points and states now come from the GeoNames postal code dump of
13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)). Credit: "Source:
GeoNames, Polish postal code dump, 13 October 2026". A row is kept when the dump lists its code. A field the dump's rows disagree on is left
empty. Edition ledger: `.github/fixes-docs/ledgers/PL_postcodes_geonames_2026-10.sources.json`. 2,696 rows the
dump does not list are queued for removal in v5.0.0; they keep their earlier values until then.

**Ukraine (since October 2026):** the earlier UA rows came from a copy of the postcode list (rvolykh/UAPostcodes) whose
redistribution basis was not established. Names, points and states now come from the GeoNames postal code dump of
13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)). Credit: "Source:
GeoNames, Ukrainian postal code dump, 13 October 2026". Each row is one postcode and locality; a row is kept only when the dump lists its locality under the same code
(exactly, or after an accent, case and punctuation fold). A field the dump's rows disagree on is left
empty. Edition ledger: `.github/fixes-docs/ledgers/UA_postcodes_geonames_2026-10.sources.json`. 4,427 rows the
dump does not list are queued for removal in v5.0.0; they keep their earlier values until then.

**Argentina (since October 2026):** the earlier AR rows came from a copy of the postcode list (androdron/localidades_AR) whose
redistribution basis was not established. Names, points and states now come from the GeoNames postal code dump of
13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt)). Credit: "Source:
GeoNames, Argentine postal code dump, 13 October 2026". Each row is one postcode and locality; a row is kept only when the dump lists its locality under the same code
(exactly, or after an accent, case and punctuation fold). A field the dump's rows disagree on is left
empty. City links are cleared: the dump has no Correo locality id to re-derive them. Edition ledger: `.github/fixes-docs/ledgers/AR_postcodes_geonames_2026-10.sources.json`. 10,660 rows the
dump does not list are queued for removal in v5.0.0; they keep their earlier values until then.

**Malta (since October 2026):** the earlier MT rows were full delivery codes (`AAA NNNN`) scraped from MaltaPost's
address search (lucamuscat/Scrape_Malta_Addresses), whose redistribution basis was not established. No complete nationwide open listing of Malta's full codes
was verified; GeoNames has only the 73 three-letter prefixes, a different and larger entity. OpenStreetMap provides
partial full-code observations. So only the 780 codes
that OpenStreetMap (`osm`; © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright); Geofabrik
extracts with data up to 2026-10-13T20:21:31Z) confirm are kept: a code is confirmed by postcode-tagged OpenStreetMap
objects (addr:postcode or postal_code) inside Malta, its locality is kept only where those objects agree, and its point is their median (else empty).
**Coverage consequence:** Malta keeps 780 of its 26,593 full postcodes (2.9%); the other 25,813 are queued for removal in
v5.0.0 and keep their earlier values until then. Per-code evidence (OSM object ids and versions):
`.github/fixes-docs/ledgers/postcodes_osm_2026-10_evidence.csv`; edition ledger:
`.github/fixes-docs/ledgers/MT_postcodes_osm_2026-10.sources.json`.

**China (since October 2026):** the earlier CN rows (mumuy/data_post) had no established redistribution basis. GeoNames
lists only China's general codes, ending in 00: the 2,280 CSC codes it lists keep their ids and take its name, point and
state (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt); credit "Source: GeoNames,
Chinese postal code dump, 13 October 2026"), with type `area`. 1,121 more codes are confirmed by OpenStreetMap (`osm`; © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright); Geofabrik
extracts with data up to 2026-10-13T20:21:31Z), by the
same rule as Malta. **Coverage consequence:** China keeps 3,401 of its 22,656 postcodes (15%); the other 19,255 are
queued for removal in v5.0.0 and keep their earlier values until then. Edition ledgers:
`.github/fixes-docs/ledgers/CN_postcodes_geonames_2026-10.sources.json` and `CN_postcodes_osm_2026-10.sources.json`; OSM
evidence as for Malta.

**Indonesia (since October 2026):** the earlier ID rows came from a legacy copy (pentagonal/Indonesia-Postal-Code) whose
redistribution basis was not established. Each row is one postcode and regency/city; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Indonesian postal code dump, 13 October 2026"). Indonesia retains 8,054 regency/city-scoped postcode IDs covering 7,966 codes, replaces their labels with open administrative labels and queues 313 unsupported tuples; 3,829 estimates and 7,804 province links remain. Edition ledger:
`.github/fixes-docs/ledgers/ID_postcodes_2026-10.sources.json`.

**Brazil (since October 2026):** the earlier BR rows came from a legacy copy (Maahzuka/database-CEPS) whose
redistribution basis was not established. Each row is one postcode; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Brazilian postal code dump, 13 October 2026"). Brazil retains 5,302 supported code IDs, queues 390 unsupported IDs in v5, and offers 5,302 published estimates with no city links. Edition ledger:
`.github/fixes-docs/ledgers/BR_postcodes_2026-10.sources.json`.

**South Africa (since October 2026):** the earlier ZA rows came from a legacy copy (raramuridesign-cc/South-African-Postal-Codes) whose
redistribution basis was not established. Each row is one postcode, town and delivery kind; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, South African postal code dump, 13 October 2026"). South Africa retains 731 generic code/locality IDs covering 700 codes, loses 4,954 unsupported locality or delivery-kind IDs in v5, and retains no province links. Edition ledger:
`.github/fixes-docs/ledgers/ZA_postcodes_2026-10.sources.json`.

**Norway (since October 2026):** the earlier NO rows came from a legacy copy (Bring's postnummerregister) whose
redistribution basis was not established. Each row is one postcode; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Norwegian postal code dump, 13 October 2026"). Norway retains 5,105 supported code IDs, queues 17 unsupported IDs in v5, and offers 5,105 published estimates with no city links. Edition ledger:
`.github/fixes-docs/ledgers/NO_postcodes_2026-10.sources.json`.

**Italy (since October 2026):** the earlier IT rows came from a legacy copy (matteocontrini/comuni-json) whose
redistribution basis was not established. Each row is one postcode (CAP); supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Italian postal code dump, 13 October 2026"). Italy retains 4,558 CAP IDs and queues 120 absent codes, clears 2,836 ambiguous labels and all 3,551 linked kept rows, and holds 67 province assignments. Edition ledger:
`.github/fixes-docs/ledgers/IT_postcodes_2026-10.sources.json`.

**Netherlands (since October 2026):** the earlier NL rows came from a legacy copy (mevdschee/postcodes-nl) whose
redistribution basis was not established. Each row is one four-digit postcode (PC4); supported rows are now re-derived from
Kadaster's BAG register through PDOK (`kadaster-bag`; [Public Domain Mark 1.0](https://creativecommons.org/publicdomain/mark/1.0/);
credit "Source: Kadaster, BAG, via PDOK"), with BRK municipality boundaries (CC0) used only to check city links. The Netherlands retains all 4,072 existing PC4 IDs, supplies 3,997 unanimous locality labels and 2,615 guarded city links, and adds no PC6 codes or postcode points. Edition ledger:
`.github/fixes-docs/ledgers/NL_postcodes_2026-10.sources.json`.

**Colombia (since October 2026):** the earlier CO rows came from a legacy copy (JohaAlarcon/Load_postal_code) whose
redistribution basis was not established. Each row is one postcode; supported rows are now re-derived from
4-72's official postal code product (`4-72-official`; its open clause, kept in `.github/licenses/4-72-Clausula-Licencia-Abierta.txt`;
credit "Fuente: MINTIC-Servicios Postales Nacionales 4-72 (Unidad Código Postal Colombia)";
download object HTTP Last-Modified: 28 June 2016; DBF header last update: 2013-10-07;
original XML metadata date fields and SHA-256 retained in the notice and ledger;
these source metadata timestamps do not certify current postal routing). Colombia retains 3,672 official full-code IDs and their re-derived department links, corrects 22 links, queues 4 absent codes, and keeps locality labels and points null. Edition ledger:
`.github/fixes-docs/ledgers/CO_postcodes_2026-10.sources.json`.

**Hungary (since October 2026):** the earlier HU rows came from a legacy copy (ferenci-tamas/IrszHnk) whose
redistribution basis was not established. Each row is one postcode and settlement/district; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Hungarian postal code dump, 13 October 2026"). Hungary retains 3,228 supported code/locality IDs, queues 341 unsupported IDs in v5, and offers 3,228 published estimates with no city links. Edition ledger:
`.github/fixes-docs/ledgers/HU_postcodes_2026-10.sources.json`.

**Malaysia (since October 2026):** the earlier MY rows came from a legacy copy (AsyrafHussin/malaysia-postcodes) whose
redistribution basis was not established. Each row is one postcode and locality; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Malaysian postal code dump, 13 October 2026"). Malaysia retains 2,632 supported code/locality IDs, queues 301 unsupported IDs in v5, and offers 2,629 published estimates with no city links. Edition ledger:
`.github/fixes-docs/ledgers/MY_postcodes_2026-10.sources.json`.

**Turkey (since October 2026):** the earlier TR rows came from a legacy copy (muratgozel/turkey-neighbourhoods) whose
redistribution basis was not established. Each row is one postcode and district; supported rows are now re-derived from
the GeoNames postal code dump of 13 October 2026 (`geonames-postal`; [CC BY 4.0](https://download.geonames.org/export/zip/readme.txt);
credit "Source: GeoNames, Turkish postal code dump, 13 October 2026"). Turkey retains 1,423 supported code/district IDs, queues 1,348 unsupported IDs in v5, and offers 767 published estimates with no city links. Edition ledger:
`.github/fixes-docs/ledgers/TR_postcodes_2026-10.sources.json`.

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
