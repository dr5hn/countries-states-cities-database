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

**Andorra (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Andorra retains 7 same-scope postcode IDs (7 codes), queues 0 IDs for v5, retains 7 fresh labels, 7 source-supported point pairs and 7 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/AD_postcodes_2026-10.sources.json`.

**Anguilla (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Anguilla retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/AI_postcodes_2026-10.sources.json`.

**American Samoa (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). American Samoa retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/AS_postcodes_2026-10.sources.json`.

**Barbados (final rebuild, October 2026):** the earlier `shipping-market-caribbean-seeder` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Barbados retains 0 same-scope postcode IDs (0 codes), queues 19 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/BB_postcodes_2026-10.sources.json`.

**Bangladesh (final rebuild, October 2026):** the earlier `bangladesh-post-via-saaiful` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Bangladesh retains 1274 same-scope postcode IDs (1274 codes), queues 79 IDs for v5, retains 1274 fresh labels, 1274 source-supported point pairs and 1274 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/BD_postcodes_2026-10.sources.json`.

**Belgium (final rebuild, October 2026):** the earlier `bpost` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Belgium retains 1145 same-scope postcode IDs (1145 codes), queues 0 IDs for v5, retains 623 fresh labels, 629 source-supported point pairs and 1145 state links, and clears 4 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/BE_postcodes_2026-10.sources.json`.

**Saint-Barthelemy (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Saint-Barthelemy retains 0 same-scope postcode IDs (0 codes), queues 1 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/BL_postcodes_2026-10.sources.json`.

**Bermuda (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Bermuda retains 11 same-scope postcode IDs (11 codes), queues 0 IDs for v5, retains 8 fresh labels, 9 source-supported point pairs and 1 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/BM_postcodes_2026-10.sources.json`.

**Brunei (final rebuild, October 2026):** the earlier `brunei-post-via-xplorasia` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Brunei retains 0 same-scope postcode IDs (0 codes), queues 547 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/BN_postcodes_2026-10.sources.json`.

**Canada (final rebuild, October 2026):** the earlier `statscan-fsa-via-inkjet` copy had no established
redistribution basis. Row identity: `fsa_code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Canada retains 1645 same-scope postcode IDs (1645 codes), queues 0 IDs for v5, retains 1644 fresh labels, 1645 source-supported point pairs and 1645 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/CA_postcodes_2026-10.sources.json`.

**Cocos (Keeling) Islands (final rebuild, October 2026):** the earlier `australia-post-via-matthewproctor` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Cocos (Keeling) Islands retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/CC_postcodes_2026-10.sources.json`.

**Costa Rica (final rebuild, October 2026):** the earlier `correos-de-costa-rica-via-llperez` copy had no established
redistribution basis. Row identity: `code_district_canton`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Costa Rica retains 439 same-scope postcode IDs (439 codes), queues 42 IDs for v5, retains 439 fresh labels, 439 source-supported point pairs and 439 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/CR_postcodes_2026-10.sources.json`.

**Christmas Island (final rebuild, October 2026):** the earlier `australia-post-via-matthewproctor` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Christmas Island retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/CX_postcodes_2026-10.sources.json`.

**Cyprus (final rebuild, October 2026):** the earlier `cyprus-post-via-georgioupanayiotis` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Cyprus retains 808 same-scope postcode IDs (807 codes), queues 17 IDs for v5, retains 808 fresh labels, 808 source-supported point pairs and 808 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/CY_postcodes_2026-10.sources.json`.

**Czech Republic (final rebuild, October 2026):** the earlier `ceska-posta-via-1nfinity84` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Czech Republic retains 2644 same-scope postcode IDs (2644 codes), queues 51 IDs for v5, retains 1140 fresh labels, 1246 source-supported point pairs and 2525 state links, and clears 466 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/CZ_postcodes_2026-10.sources.json`.

**Denmark (final rebuild, October 2026):** the earlier `dawa` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Denmark retains 1089 same-scope postcode IDs (1089 codes), queues 0 IDs for v5, retains 1089 fresh labels, 1089 source-supported point pairs and 1089 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/DK_postcodes_2026-10.sources.json`.

**Dominican Republic (final rebuild, October 2026):** the earlier `inposdom-via-manuelpgs` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Dominican Republic retains 483 same-scope postcode IDs (188 codes), queues 1837 IDs for v5, retains 483 fresh labels, 458 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/DO_postcodes_2026-10.sources.json`.

**Algeria (final rebuild, October 2026):** the earlier `algerie-poste-via-badre429` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Algeria retains 27 same-scope postcode IDs (27 codes), queues 1514 IDs for v5, retains 27 fresh labels, 25 source-supported point pairs and 24 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/DZ_postcodes_2026-10.sources.json`.

**Ecuador (final rebuild, October 2026):** the earlier `correos-del-ecuador-via-danielparsdq` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Ecuador retains 1181 same-scope postcode IDs (1181 codes), queues 24 IDs for v5, retains 1181 fresh labels, 1181 source-supported point pairs and 1181 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/EC_postcodes_2026-10.sources.json`.

**Falkland Islands (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Falkland Islands retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/FK_postcodes_2026-10.sources.json`.

**Micronesia (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Micronesia retains 4 same-scope postcode IDs (4 codes), queues 0 IDs for v5, retains 4 fresh labels, 0 source-supported point pairs and 4 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/FM_postcodes_2026-10.sources.json`.

**United Kingdom (final rebuild, October 2026):** the earlier `ordnance-survey-via-dwyl` copy had no established
redistribution basis. Row identity: `postal_area_prefix`. Recorded replacement: OS Code-Point Open
(OS [OGL v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/); OS, Royal Mail and ONS credits in the distribution notice). United Kingdom retains 120 same-scope postcode IDs (120 codes), queues 4 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GB_postcodes_2026-10.sources.json`.

**French Guiana (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). French Guiana retains 3 same-scope postcode IDs (3 codes), queues 0 IDs for v5, retains 3 fresh labels, 3 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GF_postcodes_2026-10.sources.json`.

**Guernsey (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Guernsey retains 0 same-scope postcode IDs (0 codes), queues 10 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GG_postcodes_2026-10.sources.json`.

**Gibraltar (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Gibraltar retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GI_postcodes_2026-10.sources.json`.

**Greenland (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Greenland retains 10 same-scope postcode IDs (10 codes), queues 0 IDs for v5, retains 10 fresh labels, 10 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GL_postcodes_2026-10.sources.json`.

**Guadeloupe (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Guadeloupe retains 4 same-scope postcode IDs (4 codes), queues 0 IDs for v5, retains 4 fresh labels, 4 source-supported point pairs and 0 state links, and clears 1 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GP_postcodes_2026-10.sources.json`.

**Greece (final rebuild, October 2026):** the earlier `elta-via-MentatInnovations` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Greece retains 1204 same-scope postcode IDs (1204 codes), queues 46 IDs for v5, retains 43 fresh labels, 57 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GR_postcodes_2026-10.sources.json`.

**South Georgia (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). South Georgia retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/GS_postcodes_2026-10.sources.json`.

**Croatia (final rebuild, October 2026):** the earlier `hrvatska-posta-via-mislavcimpersak` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Croatia retains 283 same-scope postcode IDs (283 codes), queues 622 IDs for v5, retains 283 fresh labels, 283 source-supported point pairs and 283 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/HR_postcodes_2026-10.sources.json`.

**Man (Isle of) (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Man (Isle of) retains 0 same-scope postcode IDs (0 codes), queues 13 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/IM_postcodes_2026-10.sources.json`.

**British Indian Ocean Territory (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). British Indian Ocean Territory retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/IO_postcodes_2026-10.sources.json`.

**Iran (final rebuild, October 2026):** the earlier `iran-post-via-saeidi-dev` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Iran retains 0 same-scope postcode IDs (0 codes), queues 193 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/IR_postcodes_2026-10.sources.json`.

**Iceland (final rebuild, October 2026):** the earlier `iceaddr` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Iceland retains 195 same-scope postcode IDs (195 codes), queues 0 IDs for v5, retains 195 fresh labels, 195 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/IS_postcodes_2026-10.sources.json`.

**Jersey (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Jersey retains 0 same-scope postcode IDs (0 codes), queues 5 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/JE_postcodes_2026-10.sources.json`.

**Kenya (final rebuild, October 2026):** the earlier `posta-kenya-via-njoguamos` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Kenya retains 555 same-scope postcode IDs (555 codes), queues 75 IDs for v5, retains 555 fresh labels, 555 source-supported point pairs and 555 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/KE_postcodes_2026-10.sources.json`.

**Cambodia (final rebuild, October 2026):** the earlier `cambodia-post-via-seanghay` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Cambodia retains 0 same-scope postcode IDs (0 codes), queues 1640 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/KH_postcodes_2026-10.sources.json`.

**Cayman Islands (final rebuild, October 2026):** the earlier `shipping-market-caribbean-seeder` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Cayman Islands retains 0 same-scope postcode IDs (0 codes), queues 9 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/KY_postcodes_2026-10.sources.json`.

**Liechtenstein (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Liechtenstein retains 13 same-scope postcode IDs (13 codes), queues 0 IDs for v5, retains 13 fresh labels, 13 source-supported point pairs and 13 state links, and clears 1 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/LI_postcodes_2026-10.sources.json`.

**Sri Lanka (final rebuild, October 2026):** the earlier `sri-lanka-post-via-madurapa` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Sri Lanka retains 1781 same-scope postcode IDs (1779 codes), queues 272 IDs for v5, retains 1781 fresh labels, 1781 source-supported point pairs and 1781 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/LK_postcodes_2026-10.sources.json`.

**Latvia (final rebuild, October 2026):** the earlier `latvijas-pasts-via-IcebergBuilder` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Latvia retains 670 same-scope postcode IDs (670 codes), queues 1 IDs for v5, retains 234 fresh labels, 322 source-supported point pairs and 639 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/LV_postcodes_2026-10.sources.json`.

**Monaco (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Monaco retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MC_postcodes_2026-10.sources.json`.

**Moldova (final rebuild, October 2026):** the earlier `posta-moldovei-via-vasilcovsky` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Moldova retains 1052 same-scope postcode IDs (807 codes), queues 264 IDs for v5, retains 1052 fresh labels, 1052 source-supported point pairs and 919 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MD_postcodes_2026-10.sources.json`.

**Saint-Martin (French part) (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Saint-Martin (French part) retains 0 same-scope postcode IDs (0 codes), queues 1 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MF_postcodes_2026-10.sources.json`.

**Madagascar (final rebuild, October 2026):** the earlier `paositra-malagasy-via-rasolofonirina` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Madagascar retains 0 same-scope postcode IDs (0 codes), queues 111 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MG_postcodes_2026-10.sources.json`.

**Marshall Islands (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Marshall Islands retains 2 same-scope postcode IDs (2 codes), queues 0 IDs for v5, retains 2 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MH_postcodes_2026-10.sources.json`.

**Myanmar (final rebuild, October 2026):** the earlier `myanmar-post-official` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Myanmar retains 0 same-scope postcode IDs (0 codes), queues 17331 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MM_postcodes_2026-10.sources.json`.

**Mongolia (final rebuild, October 2026):** the earlier `mongol-shuudan-via-bekkaze` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Mongolia retains 0 same-scope postcode IDs (0 codes), queues 2605 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MN_postcodes_2026-10.sources.json`.

**Northern Mariana Islands (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Northern Mariana Islands retains 3 same-scope postcode IDs (3 codes), queues 0 IDs for v5, retains 3 fresh labels, 3 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MP_postcodes_2026-10.sources.json`.

**Martinique (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Martinique retains 4 same-scope postcode IDs (4 codes), queues 0 IDs for v5, retains 3 fresh labels, 3 source-supported point pairs and 0 state links, and clears 2 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MQ_postcodes_2026-10.sources.json`.

**Mauritius (final rebuild, October 2026):** the earlier `mauritius-post-via-Samimveza` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Mauritius retains 2 same-scope postcode IDs (2 codes), queues 1872 IDs for v5, retains 2 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MU_postcodes_2026-10.sources.json`.

**Mozambique (final rebuild, October 2026):** the earlier `correios-mocambique-via-PauloPhagula` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Mozambique retains 0 same-scope postcode IDs (0 codes), queues 161 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/MZ_postcodes_2026-10.sources.json`.

**Namibia (final rebuild, October 2026):** the earlier `nampost-via-kuberkode` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Namibia retains 0 same-scope postcode IDs (0 codes), queues 149 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/NA_postcodes_2026-10.sources.json`.

**New Caledonia (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). New Caledonia retains 3 same-scope postcode IDs (3 codes), queues 0 IDs for v5, retains 3 fresh labels, 3 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/NC_postcodes_2026-10.sources.json`.

**Norfolk Island (final rebuild, October 2026):** the earlier `australia-post-via-matthewproctor` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Norfolk Island retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/NF_postcodes_2026-10.sources.json`.

**Nigeria (final rebuild, October 2026):** the earlier `nipost-via-ifeLight` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Nigeria retains 0 same-scope postcode IDs (0 codes), queues 3728 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/NG_postcodes_2026-10.sources.json`.

**Nepal (final rebuild, October 2026):** the earlier `nepal-post-via-sprupak07` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Nepal retains 2 same-scope postcode IDs (2 codes), queues 915 IDs for v5, retains 2 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/NP_postcodes_2026-10.sources.json`.

**Nauru (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Nauru retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/NR_postcodes_2026-10.sources.json`.

**Panama (final rebuild, October 2026):** the earlier `correos-panama-via-viquezr` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Panama retains 0 same-scope postcode IDs (0 codes), queues 87 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PA_postcodes_2026-10.sources.json`.

**Peru (final rebuild, October 2026):** the earlier `serpost-via-peru-pe-cpn` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Peru retains 2669 same-scope postcode IDs (2669 codes), queues 0 IDs for v5, retains 773 fresh labels, 829 source-supported point pairs and 2669 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PE_postcodes_2026-10.sources.json`.

**French Polynesia (final rebuild, October 2026):** the earlier `wikipedia-pf-archipelago-anchor` copy had no established
redistribution basis. Row identity: `code_anchor_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). French Polynesia retains 2 same-scope postcode IDs (2 codes), queues 3 IDs for v5, retains 2 fresh labels, 2 source-supported point pairs and 2 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PF_postcodes_2026-10.sources.json`.

**Philippines (final rebuild, October 2026):** the earlier `phlpost-via-jayson-panganiban` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Philippines retains 1373 same-scope postcode IDs (1254 codes), queues 18 IDs for v5, retains 1373 fresh labels, 1373 source-supported point pairs and 994 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PH_postcodes_2026-10.sources.json`.

**Saint Pierre and Miquelon (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Saint Pierre and Miquelon retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PM_postcodes_2026-10.sources.json`.

**Pitcairn Island (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Pitcairn Island retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PN_postcodes_2026-10.sources.json`.

**Palau (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Palau retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PW_postcodes_2026-10.sources.json`.

**Paraguay (final rebuild, October 2026):** the earlier `dinacopa-via-3lD4m14n` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Paraguay retains 0 same-scope postcode IDs (0 codes), queues 8644 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/PY_postcodes_2026-10.sources.json`.

**Reunion (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Reunion retains 4 same-scope postcode IDs (4 codes), queues 0 IDs for v5, retains 4 fresh labels, 4 source-supported point pairs and 0 state links, and clears 4 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/RE_postcodes_2026-10.sources.json`.

**Serbia (final rebuild, October 2026):** the earlier `posta-srbije-via-nebjak` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Serbia retains 1066 same-scope postcode IDs (1066 codes), queues 104 IDs for v5, retains 1066 fresh labels, 1066 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/RS_postcodes_2026-10.sources.json`.

**Saint Helena (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Saint Helena retains 0 same-scope postcode IDs (0 codes), queues 3 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SH_postcodes_2026-10.sources.json`.

**Slovenia (final rebuild, October 2026):** the earlier `postcode-si` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Slovenia retains 517 same-scope postcode IDs (517 codes), queues 5 IDs for v5, retains 517 fresh labels, 517 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SI_postcodes_2026-10.sources.json`.

**Svalbard and Jan Mayen Islands (final rebuild, October 2026):** the earlier `bring-via-sj-mirror` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Svalbard and Jan Mayen Islands retains 8 same-scope postcode IDs (8 codes), queues 0 IDs for v5, retains 8 fresh labels, 8 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SJ_postcodes_2026-10.sources.json`.

**Slovakia (final rebuild, October 2026):** the earlier `psc-json` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Slovakia retains 1307 same-scope postcode IDs (1307 codes), queues 5 IDs for v5, retains 535 fresh labels, 560 source-supported point pairs and 1303 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SK_postcodes_2026-10.sources.json`.

**San Marino (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). San Marino retains 9 same-scope postcode IDs (9 codes), queues 0 IDs for v5, retains 2 fresh labels, 6 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SM_postcodes_2026-10.sources.json`.

**Somalia (final rebuild, October 2026):** the earlier `somali-postal-code-explorer` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Somalia retains 0 same-scope postcode IDs (0 codes), queues 67 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SO_postcodes_2026-10.sources.json`.

**El Salvador (final rebuild, October 2026):** the earlier `correos-el-salvador-via-micryptosv` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). El Salvador retains 0 same-scope postcode IDs (0 codes), queues 262 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/SV_postcodes_2026-10.sources.json`.

**Turks and Caicos Islands (final rebuild, October 2026):** the earlier `wikipedia-singleton-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Turks and Caicos Islands retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/TC_postcodes_2026-10.sources.json`.

**Thailand (final rebuild, October 2026):** the earlier `thai-post-via-chawatvish` copy had no established
redistribution basis. Row identity: `code_district_with_published_native_alias`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Thailand retains 587 same-scope postcode IDs (557 codes), queues 602 IDs for v5, retains 587 fresh labels, 570 source-supported point pairs and 587 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/TH_postcodes_2026-10.sources.json`.

**Tunisia (final rebuild, October 2026):** the earlier `la-poste-tunisienne-via-jenhani-chedli` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Tunisia retains 8 same-scope postcode IDs (8 codes), queues 4860 IDs for v5, retains 8 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/TN_postcodes_2026-10.sources.json`.

**Trinidad and Tobago (final rebuild, October 2026):** the earlier `shipping-market-caribbean-seeder` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: OpenStreetMap validated country screen
([ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/); credit "© OpenStreetMap contributors", [copyright](https://www.openstreetmap.org/copyright)). Trinidad and Tobago retains 0 same-scope postcode IDs (0 codes), queues 26 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/TT_postcodes_2026-10.sources.json`.

**Taiwan (final rebuild, October 2026):** the earlier `chunghwa-post-via-eagle-tw-open-data` copy had no established
redistribution basis. Row identity: `code_district_county_bilingual`. Recorded replacement: Chunghwa Post 25489 + checking bilingual KML 37759
(Chunghwa Post datasets [25489](https://data.gov.tw/dataset/25489) and [37759](https://data.gov.tw/dataset/37759), [OGDL-Taiwan 1.0](https://data.gov.tw/license)). Taiwan retains 332 same-scope postcode IDs (332 codes), queues 39 IDs for v5, retains 332 fresh labels, 332 source-supported point pairs and 332 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/TW_postcodes_2026-10.sources.json`.

**Tanzania (final rebuild, October 2026):** the earlier `tanzania-napa-via-msuluzya` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Tanzania retains 0 same-scope postcode IDs (0 codes), queues 3684 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/TZ_postcodes_2026-10.sources.json`.

**Uruguay (final rebuild, October 2026):** the earlier `correo-uruguayo-via-ale-uy` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Uruguay retains 1964 same-scope postcode IDs (122 codes), queues 0 IDs for v5, retains 1964 fresh labels, 1964 source-supported point pairs and 1964 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/UY_postcodes_2026-10.sources.json`.

**Vatican City State (Holy See) (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Vatican City State (Holy See) retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/VA_postcodes_2026-10.sources.json`.

**Saint Vincent and the Grenadines (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Saint Vincent and the Grenadines retains 0 same-scope postcode IDs (0 codes), queues 4 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/VC_postcodes_2026-10.sources.json`.

**Venezuela (final rebuild, October 2026):** the earlier `ipostel-via-JhonnelN` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Venezuela retains 0 same-scope postcode IDs (0 codes), queues 1187 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/VE_postcodes_2026-10.sources.json`.

**Virgin Islands (British) (final rebuild, October 2026):** the earlier `wikipedia-small-territory` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Virgin Islands (British) retains 0 same-scope postcode IDs (0 codes), queues 7 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/VG_postcodes_2026-10.sources.json`.

**Vietnam (final rebuild, October 2026):** the earlier `vnpost-via-navuitag` copy had no established
redistribution basis. Row identity: `code_locality`. Recorded replacement: none established in bounded screen
(no suitable acquired product with an established distribution basis; the bounded research gaps remain holds). Vietnam retains 0 same-scope postcode IDs (0 codes), queues 63 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/VN_postcodes_2026-10.sources.json`.

**Wallis and Futuna Islands (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Wallis and Futuna Islands retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 1 fresh labels, 1 source-supported point pairs and 1 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/WF_postcodes_2026-10.sources.json`.

**Mayotte (final rebuild, October 2026):** the earlier `manual` copy had no established
redistribution basis. Row identity: `code`. Recorded replacement: GeoNames postal snapshot 13 October 2026
(GeoNames [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); credit "Source: GeoNames"). Mayotte retains 1 same-scope postcode IDs (1 codes), queues 0 IDs for v5, retains 0 fresh labels, 0 source-supported point pairs and 0 state links, and clears 0 existing city links on kept rows. Queued rows keep their current values until the v5 ledger.
Edition ledger: `.github/fixes-docs/ledgers/YT_postcodes_2026-10.sources.json`.

Final-rebuild distribution notices are carried verbatim in `.github/licenses/pc_rebuild_7-distribution-notices.txt`. They include the source
editions, changes by CSC, licence links and reuse terms. No new codes, postcode IDs or city links are added.

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
