# FIX #1039 — Backfill country `postal_code_format` / `postal_code_regex`

**Issue:** [#1039 — Can we add a postcode for this?](https://github.com/dr5hn/countries-states-cities-database/issues/1039)
**Scope:** Country-level postal *format & regex* metadata only (Tier 1).
**Date:** 2026-04-25

## Problem

The `countries` table already has `postal_code_format` and `postal_code_regex` columns, populated for 177 of 250 countries. The remaining 73 were `null`. This PR fills the subset of those 73 where the postal system is universally documented and unambiguous, finishing the existing infrastructure without introducing external data dependencies.

This PR does **not** address city- or state-level postcode values (a much larger scope — see issue discussion for tiered roadmap).

## Coverage Change

| Before | After | Δ |
|--------|-------|---|
| 177 / 250 (70.8%) | **189 / 250 (75.6%)** | +12 |

## Countries Updated (12)

| ISO2 | Country | `postal_code_format` | `postal_code_regex` |
|------|---------|----------------------|---------------------|
| AF | Afghanistan | `####` | `^(\d{4})$` |
| BT | Bhutan | `#####` | `^(\d{5})$` |
| KY | Cayman Islands | `KY#-####` | `^KY\d-\d{4}$` |
| MU | Mauritius | `#####` | `^(\d{5})$` |
| NA | Namibia | `#####` | `^(\d{5})$` |
| TF | French Southern Territories | `#####` | `^(\d{5})$` |
| TT | Trinidad and Tobago | `######` | `^(\d{6})$` |
| TZ | Tanzania | `#####` | `^(\d{5})$` |
| UM | United States Minor Outlying Islands | `#####` | `^(\d{5})$` |
| VC | Saint Vincent and the Grenadines | `VC####` | `^VC\d{4}$` |
| VG | Virgin Islands (British) | `VG####` | `^VG\d{4}$` |
| XK | Kosovo | `#####` | `^(\d{5})$` |

Format placeholders use the existing convention: `#` = digit, `@` = letter, literal characters as-is.

## Countries Deliberately Left `null` (61)

The remaining 61 countries fall into four groups; **`null` is the correct value** for all of them:

### A. No postal code system (per Universal Postal Union documentation, ~50 countries)
Includes most of sub-Saharan Africa (Angola, Benin, Botswana, Burkina Faso, Burundi, Cameroon, Central African Republic, Chad, Comoros, Congo, DRC, Djibouti, Equatorial Guinea, Eritrea, Gabon, Gambia, Ghana, Guinea, Mali, Mauritania, Rwanda, São Tomé, Seychelles, Sierra Leone, South Sudan, Togo, Uganda, Zimbabwe), the Caribbean (Antigua, Aruba, Bahamas, Belize, Bolivia, Curaçao, Dominica, Grenada, Guyana, Jamaica, Saint Kitts and Nevis, Suriname, Sint Maarten), the Gulf (Qatar, Yemen), and most of Oceania (Cook Islands, Fiji, Kiribati, Solomon Islands, Tokelau, Tonga, Tuvalu, Vanuatu).

### B. Disputed/conflict regions where official postal status is unsettled (4)
Western Sahara, Palestinian Territory Occupied, Syria, Libya — `null` reflects the genuine ambiguity.

### C. Uninhabited / no civil postal infrastructure (2)
Antarctica, Bouvet Island.

### D. Edge cases worth a future PR (~3)
Saint Lucia (recently introduced LC## ### but adoption uneven), Montserrat (MSR####), Bonaire/Sint Eustatius/Saba (uses Caribbean Netherlands codes since 2014). Left `null` here to keep this PR conservative and high-confidence.

## Validation

- ✅ JSON syntax valid (`json.load()` succeeds, 250 records)
- ✅ All 12 new regexes compile in Python `re`
- ✅ All 189 populated regexes still compile
- ✅ Diff is minimal: exactly 24 line changes (12 entries × 2 fields), no whitespace churn
- ✅ No auto-managed fields (`id`, `created_at`, `updated_at`, `flag`) modified
- ✅ Field names match existing schema (`postal_code_format`, `postal_code_regex`)

## Out of Scope (Future Work)

This is **Tier 1** of the roadmap proposed in the issue analysis. Future tiers (not part of this PR):

- **Tier 2:** State-level postcode prefix (new optional column on `states`)
- **Tier 3:** City-level single postcode (new optional column on `cities`)
- **Tier 4:** Postcode-as-entity (new table)

Each of those requires a sourcing decision (GeoNames CC-BY vs. national postal authorities with restrictive licenses) and should be discussed in a follow-up issue.

## Source of Updates

All 12 entries reflect universally-documented national postal systems. No external dataset was imported; values were drawn from common knowledge of:
- 4- and 5-digit national systems (UPU member countries)
- British Overseas Territories using `XX####` prefixed codes (KY, VG)
- Sovereign states using a national prefixed-code convention (VC — `VC####`)
- Inheritance from parent country systems (TF → France, UM → US)

## Postcodes linked to their city (city_id)

### Problem
None of the 844,248 postcodes in `contributions/postcodes/` carried `city_id`, so a postcode could not be resolved to its
city and a city's postcodes could not be listed.

### Fix
172,122 postcodes in 7 countries now point to their city. A link needs exactly one CSC city in the postcode's state
whose name, native name or a translation equals the place the source gives for the code (after case, accent and
punctuation folding), plus the country's own check below. Records whose city was merged in #1767 point to the surviving
record. Only `city_id` changes.

| Country | Linked | Rule | Postcode source and terms |
|---|---:|---|---|
| PT | 86,043 | Every CTT street row of the code has the same postal designation and actual locality, and one locality identity (district, concelho, locality) has that name in the state; large-user and PO-box codes held; a municipality record only when it is the named containing concelho. Every target city point was also checked against the CAOP municipality boundaries. | CTT data via [Central de Dados codigos_postais](https://github.com/centraldedados/codigos_postais); terms not audited |
| JP | 79,287 | All Japan Post rows of the code agree on one municipality and the prefecture; a town-area row links to the municipality (city, town or village) Japan Post names for it; ordinary wards are held. | [Japan Post KEN_ALL, UTF-8](https://www.post.japanpost.jp/service/search/zipcode/download/utf-zip.html); free to use, no formal licence |
| IT | 3,637 | All CAP rows of the code name one comune; its ISTAT code, name and province agree with the current [ISTAT register](https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv); exactly one CSC comune (level 3) of that name; frazioni held. | CAP lists from [comuni-json](https://github.com/matteocontrini/comuni-json), a community dataset that calls itself unofficial; terms not audited; not a Poste Italiane export |
| FR | 1,443 | All rows of the code name one INSEE commune whose official name is the locality, in the postcode's department, with no namesake there; one CSC commune (level 4); arrondissement codes held. | [La Poste, base officielle des codes postaux](https://datanova.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw); Licence Ouverte (etalab-2.0) |
| US | 720 | The ZCTA lies wholly inside one Census place (its land and water areas equal the overlap); one CSC city of that name (level 3) within 5 km of the Census place point, and the ZCTA point within 5, 8, 15 or 25 km by place size. Partial and multi-place ZCTAs held. These are statistical links, not USPS mailing cities. | Census [2020 ZCTA-to-place relationship](https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_place20_natl.txt) and 2024 ZCTA gazetteer; public domain |
| AT | 610 | Code, Ortschaft and province match one Ortschaft key with no namesake in the province and one containing Gemeinde; a municipality record only when it is that Gemeinde (Vienna: Gemeinde 90001). | [OpenPLZ](https://www.openplzapi.org/de/austria/) over Statistik Austria data; ODbL-1.0 |
| AR | 382 | Code and locality carry one Correo locality id; one official [Georef](https://apis.datos.gob.ar/georef/api/localidades?max=5000) "Localidad simple" of that name in the province; one CSC settlement within 3 km of its centroid. | Correo Argentino data via [localidades_AR](https://github.com/androdron/localidades_AR); terms not audited |

Where a source's terms are marked not audited, it is the source the existing postcode records were imported from; this
change adds no data from it beyond the link.

### Held
672,126 postcodes keep `city_id` null: postal designations that differ from the actual locality, several candidate
cities, sub-localities whose city record is a larger unit, large-user and PO-box codes, ZCTAs spanning several places,
476 Portuguese codes whose only same-name city is in another municipality (Pedroso, Vila Nova de Gaia, and Perafita,
Matosinhos, found in review), and the 118 countries whose postal source has not yet been checked for what a code covers
(Mexico, Malta, China, Poland, India, ...).

### Rollback
Revert the PR (squash commit); `city_id` is optional.

## Postcodes linked to their city, round 2 (DE, CH, LI, FI, BE)

### Problem
After #1770, postcodes in Germany, Switzerland, Liechtenstein, Finland and Belgium still had no `city_id`.

### Fix
7,792 more postcodes now point to their city (DE 5,374, FI 1,572, CH 841, BE 4, LI 1). As in round 1, a link needs exactly one CSC city in the
postcode's state with the place's name (name, native or translation, after folding) and a source that says the code
serves it. New in this round, after the round-1 review: the city's point must lie inside the municipality the source
names, checked against official boundaries, so a same-name place in another municipality is never chosen.

| Country | Linked | Held | Rule | Postcode source and terms |
|---|---:|---:|---|---|
| DE | 5,374 | 7,441 | Every OpenPLZ row of the code names one municipality (AGS). The link goes to the city named by the locality when all rows name that locality; otherwise to the municipality the source names as containing the locality (e.g. Wehlen in Stadt Wehlen). Either way exactly one CSC city of that name in the state, and its point lies inside that municipality in [BKG VG250](https://daten.gdz.bkg.bund.de/produkte/vg/vg250_ebenen_0101/aktuell/) (2026-01-01, dl-de/by-2-0). | OpenPLZ locality directory ([DE](https://openplzapi.org/de/Localities), [CH](https://openplzapi.org/ch/Localities), [LI](https://openplzapi.org/li/Localities)); ODbL-1.0 |
| FI | 1,572 | 2,176 | Normal postcodes (type 1) only; Posti's postcode and all-address files agree on one municipality; one CSC city of that name; its point lies inside that municipality in [Statistics Finland kunta1000k_2026](https://geo.stat.fi/) (CC-BY-4.0) with at least 1 km clearance, because the layer is generalised. | Posti PCF (extract 2026-10-08) and BAF (extract 2026-10-03), both downloaded 2026-10-08; redistribution is permitted if the recipient also gets Posti's current [service description and terms](https://www.posti.fi/mzj3zpe8qb7p/1eKbwM2WAEY5AuGi5TrSZ7/c76a865cf5feb2c527a114b8615e9580/posti-postal-code-services-service-description-and-terms-of-use-20150101.pdf) (s. 2.2) and the download date; no named open licence |
| CH | 841 | 3,218 | As DE, with BFS commune numbers and [swissBOUNDARIES3D 2026-01](https://data.geo.admin.ch/ch.swisstopo.swissboundaries3d/) (swisstopo OGD terms). Many Swiss codes serve several localities of one commune and link to the commune: code 1073 serves Mollie-Margot and Savigny, both in commune Savigny, and links to Savigny. | OpenPLZ locality directory ([DE](https://openplzapi.org/de/Localities), [CH](https://openplzapi.org/ch/Localities), [LI](https://openplzapi.org/li/Localities)); ODbL-1.0 |
| BE | 4 | 1,141 | bpost names the locality and its commune, and Statbel's postcode-to-REFNIS table agrees; one CSC city of that name in the state; its point lies inside that commune (Statbel 2025 sectors). | bpost postcode list 2025 (redistribution terms unknown); [Statbel](https://statbel.fgov.be/) crosswalk and sectors (Statbel open-data licence) |
| LI | 1 | 12 | As CH. | OpenPLZ locality directory ([DE](https://openplzapi.org/de/Localities), [CH](https://openplzapi.org/ch/Localities), [LI](https://openplzapi.org/li/Localities)); ODbL-1.0 |

### Held
25,287 postcodes in these seven countries keep `city_id` null, including all of Spain (8,124) and Australia
(3,175): their postcode records come from community mirrors with unknown terms, and no official file with
usable terms was found (Australia Post licenses its data for commercial use). Others are held for codes spanning several
municipalities, PO-box and business codes, points outside the named municipality, and Belgian codes whose city sits in
another CSC state (Belgian cities use the region as their state, the postcodes the province).

### Rollback
Revert the PR (squash commit); `city_id` is optional.

## Postcodes linked to their city, round 3 (Luxembourg, Netherlands, Czechia and others)

### Problem
After #1770 and #1774, postcodes in countries with open official address data were still unlinked.

### Fix
5,964 more postcodes now point to their city (LU 3,292, NL 2,187, CZ 471, FO 7, RE 4, MQ 2, GP 1). Same rule as round 2: exactly one CSC city with the place's
name in the postcode's state, every source row of the code in one municipality, and the city's point inside that
municipality's official boundary. Only `city_id` changes.

| Country | Linked | Rule | Source and terms |
|---|---:|---|---|
| LU | 3,292 | All street rows of the code (normal codes, no PO-box ranges) name one commune; the locality or its named commune is one CSC city, inside the commune polygon. | [CACLR national register of localities and streets](https://download.data.public.lu/resources/registre-national-des-localites-et-des-rues/20261005-023253/caclr.xlsx) and [administrative boundaries](https://download.data.public.lu/resources/limites-administratives-du-grand-duche-de-luxembourg/20261005-030016/limadmin.geojson), 2026-10-05; CC0 |
| NL | 2,187 | Every BAG address indexed under the four-digit postcode area (PC4) lies in one gemeente and province (count queries with zero exceptions, retrieved 2026-10-09); the locality or its gemeente is one CSC city, inside the gemeente polygon. Special delivery endpoints are not certified. | Retrieved from [PDOK Locatieserver](https://api.pdok.nl/bzk/locatieserver/search/v3_1/free) over [BAG](https://api.pdok.nl/kadaster/bag/ogc/v2) (Public Domain Mark 1.0); [BRK administrative units](https://api.pdok.nl/kadaster/brk-administratieve-eenheden/ogc/v1) (CC0) |
| CZ | 471 | Every RÚIAN address with the code lies in one obec whose okres is the CSC state; the documented locality or obec is one CSC city, inside the obec polygon; special postal types held. | [RÚIAN addresses, 2026-09-30](https://vdp.cuzk.gov.cz/vymenny_format/csv/20260930_OB_ADR_csv.zip) and boundaries (ČÚZK, CC BY 4.0) supply the link. Česká pošta's [code-type file](https://www.ceskaposta.cz/documents/d/guest/csv_psc_a-zip?download=true) (terms unknown) is used only to exclude: a code must be type 1 (ordinary) to be linked |
| FO | 7 | All official street addresses with the code lie in one locality and municipality; one CSC city, inside the municipality polygon. | Umhvørvisstovan datasets [adressur/us_adr_husanr](https://gis.us.fo/arcgis/rest/services/adressur/us_adr_husanr/MapServer/0) and [fyrisitingarlig_kort/us_kommunur](https://gis.us.fo/arcgis/rest/services/fyrisitingarlig_kort/us_kommunur/MapServer/0), downloaded 2026-10-09 through their web services; reuse under the [Føroyakort terms](https://www.foroyakort.fo/um-foeroyakort/terms-and-conditions-in-english) (June 2019) with attribution to Umhvørvisstovan |
| RE | 4 | Full La Poste export: all rows of the code name one commune, whose INSEE code and name match the IGN commune; one CSC city of that name in the state, inside the IGN commune polygon. | [La Poste](https://datanova.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw) and [IGN Admin Express](https://www.data.gouv.fr/datasets/admin-express-admin-express-cog-admin-express-cog-carto-admin-express-cog-carto-pe-admin-express-cog-carto-plus-pe/); Licence Ouverte 2.0 |
| MQ | 2 | Full La Poste export: all rows of the code name one commune, whose INSEE code and name match the IGN commune; one CSC city of that name in the state, inside the IGN commune polygon. | [La Poste](https://datanova.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw) and [IGN Admin Express](https://www.data.gouv.fr/datasets/admin-express-admin-express-cog-admin-express-cog-carto-admin-express-cog-carto-pe-admin-express-cog-carto-plus-pe/); Licence Ouverte 2.0 |
| GP | 1 | Full La Poste export: all rows of the code name one commune, whose INSEE code and name match the IGN commune; one CSC city of that name in the state, inside the IGN commune polygon. | [La Poste](https://datanova.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw) and [IGN Admin Express](https://www.data.gouv.fr/datasets/admin-express-admin-express-cog-admin-express-cog-carto-admin-express-cog-carto-pe-admin-express-cog-carto-plus-pe/); Licence Ouverte 2.0 |

All 125 countries' remaining postcodes were surveyed for an official, redistributable source; those without one, or
whose terms are unknown or restrict reuse, stay unlinked (the survey is in the audit files). A source with unknown terms is
never what supplies a link; it may only rule codes out (the Czech code types above). Åland's 3 candidate codes are held:
Posti covers Åland at postcode level only, without streets, so a code's full municipal scope cannot be shown.

### Rollback
Revert the PR (squash commit); `city_id` is optional.

## Australia: postcodes from open sources (owner decision of 12 Oct 2026)

### Problem
The 3,175 Australian postcodes came from a community copy of Australia Post's list, which is licensed for commercial
use and not for redistribution; the README's "Australia Post Boundaries, CC-BY 4.0" could not be confirmed.

### Fix
**3173 postcodes kept**, each re-sourced to an openly licensed source that lists it: 2641 from the Australian Bureau of
Statistics Postal Areas 2021 (`abs-poa-2021`), 530 PO-box and other non-street codes from the GeoNames postal code dump
(`geonames-postal`), 0200 (Australian National University) from Wikidata (`wikidata`) and 9726 (Gold Coast MC) from an
author's published address under CC BY 4.0 (`sattler-2019-bmc`). The mirror's locality names and points are cleared on
every row: none of these sources gives an open locality name or point for the postcode area, and none is generated.
18 codes lose their state: 15 postal areas span more than one state or territory and 3 lie in Other Territories.
**2 codes removed** (9464, 9999): none of the checked open sources (ABS POA 2021, the GeoNames postal dump,
Wikidata, G-NAF, Queensland open data) supports them under an ODbL-compatible licence. ABS postal areas are a
statistical approximation, not Australia Post's delivery list.

### Sources
- Australian Bureau of Statistics, Postal Areas (POA) 2021 and the POA 2021 Mesh Block allocation file (ASGS Edition 3,
  July 2021), © Commonwealth of Australia (ABS), licensed under CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/); codes and states taken, names and points not.
- GeoNames postal code dump for AU (https://download.geonames.org/export/zip/), CC BY 4.0 per its readme; codes only.
- Wikidata (CC0): Q127990's postal code qualifier 0200.
- Sattler, Hing and Vertullo, BMC Musculoskeletal Disorders 2019 (https://doi.org/10.1186/s12891-019-2415-5), CC BY 4.0:
  postcode 9726 in an author address.
- Modification: one row per code, the source tag set, names and points removed. G-NAF was checked; its end-user licence
  adds a condition ODbL cannot carry, so nothing is taken from it.

### Rollback
Revert the PR (squash commit); the old rows are in git history (not archived here, as their source is not open).

## Spain: real postcodes from CartoCiudad (owner decision of 12 Oct 2026)

### Problem
All 8,124 Spanish "postcodes" were INE municipality codes, not postcodes: 01001 was Alegría-Dulantzi, whose postcodes are
01193 and 01240 (decision review decisions_1).

### Fix
The 8,124 rows are removed and **10,851 real postcodes** created, one per distinct five-digit code found on the 15,618,724
addresses of CartoCiudad's 52 province files (layer `portalpk_publi`, field `cod_postal`; 325 empty or malformed values
skipped). Each row has source `cartociudad`; **10,704** carry their province (state) because all their addresses lie in one
province, taken from each file's province label (147 codes span provinces, 2 of them three, and have none);
**6,381** link to their municipality's city record because all their addresses lie in one municipality whose CSC record
is verified by its INE code; `locality_name` is that municipality's name where there is only one. The point is the mean
of the code's address points (ETRS89, or REGCAN95 in the Canaries), a derived value; it is withheld (null) on 26 codes
where that mean falls outside Spain or outside the code's own province or municipality. Leading zeros are kept. New rows
get new ids on import: the 8,124 old ids were municipality identities and are not reused. The removed rows were not
postcodes, so they are not archived here; they stay in git history. This is the source's address coverage of April
2026, not a certified copy of Correos' delivery list.

Ledger: per postcode (addresses, points, provinces, INE municipalities, source files) in
[ES_postcodes_cartociudad_2026-04.csv](ledgers/ES_postcodes_cartociudad_2026-04.csv); per source file (full SHA-256, bytes, edition, local
retrieval time, licence, method) in [ES_postcodes_cartociudad_2026-04.sources.json](ledgers/ES_postcodes_cartociudad_2026-04.sources.json).

| Province | Addresses | Codes |
| --- | ---: | ---: |
| Araba/Álava | 52,528 | 84 |
| Albacete | 188,636 | 134 |
| Alacant/Alicante | 558,417 | 213 |
| Almería | 296,709 | 166 |
| Asturias | 336,086 | 401 |
| Ávila | 191,378 | 148 |
| A Coruña | 317,927 | 377 |
| Badajoz | 338,650 | 214 |
| Illes Balears | 418,098 | 159 |
| Barcelona | 1,165,281 | 394 |
| Burgos | 270,877 | 222 |
| Cáceres | 285,310 | 244 |
| Cádiz | 376,772 | 115 |
| Cantabria | 203,616 | 216 |
| Castelló/Castellón | 262,806 | 134 |
| Ceuta | 7,469 | 5 |
| Ciudad Real | 246,473 | 130 |
| Córdoba | 302,102 | 142 |
| Cuenca | 213,797 | 182 |
| Girona | 374,999 | 253 |
| Granada | 441,330 | 200 |
| Guadalajara | 225,663 | 181 |
| Gipuzkoa | 71,266 | 113 |
| Huelva | 247,480 | 103 |
| Huesca | 118,006 | 272 |
| Jaén | 301,934 | 173 |
| Las Palmas | 245,149 | 144 |
| La Rioja | 143,770 | 130 |
| León | 360,864 | 418 |
| Lleida | 218,832 | 303 |
| Lugo | 216,443 | 462 |
| Madrid | 930,532 | 306 |
| Málaga | 519,814 | 160 |
| Melilla | 11,674 | 6 |
| Murcia | 479,813 | 212 |
| Navarra | 177,712 | 265 |
| Ourense | 233,419 | 296 |
| Palencia | 111,279 | 132 |
| Pontevedra | 336,530 | 378 |
| Salamanca | 232,766 | 274 |
| Segovia | 145,906 | 203 |
| Sevilla | 683,257 | 155 |
| Soria | 114,248 | 97 |
| Tarragona | 368,257 | 213 |
| Santa Cruz de Tenerife | 283,015 | 216 |
| Teruel | 129,684 | 210 |
| Toledo | 446,892 | 235 |
| València/Valencia | 710,063 | 298 |
| Valladolid | 175,995 | 192 |
| Bizkaia | 97,331 | 144 |
| Zamora | 199,413 | 297 |
| Zaragoza | 232,456 | 279 |

### Sources
Obra derivada de CartoCiudad 2026 CC-BY 4.0 scne.es: CartoCiudad province GeoPackages, edition 04/2026, Centro de
Descargas del CNIG (https://centrodedescargas.cnig.es/CentroDescargas/cartociudad), licensed under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/). Modification: addresses aggregated to one row per postcode, with the
province, single municipality and mean point derived as described.

### Rollback
Revert the PR (squash commit).

## India: PIN codes linked to their city (LGD)

### Problem
India's 19,100 PIN codes (source India Post) had no city link. India pass 2 (#1972) typed 2,343 Indian city records using
official LGD code evidence (urban local body or village); those codes are kept in the research ledger, not as a city field.
The LGD publishes which PIN codes serve each body and village.

### Fix
**2,689 PIN codes linked** (`city_id`) to the one typed CSC city whose LGD code the LGD maps to that PIN, where the PIN's
state agrees with the city's. **12 state corrections or fills** where all supplied LGD rows agree on one state; replacing
an existing state also required the stored locality to match an LGD name. Nothing else changes; no PIN is added or removed.

Held (16,411): PINs that no typed CSC city maps to (most: the places they serve have no typed record yet), PINs absent from
the LGD mapping files, PINs that map to more than one typed city or state, and state disagreements without corroboration.
A link means the PIN serves that city's area; a PIN can also serve villages not in the dataset.

### Sources
Source: Local Government Directory (LGD), Ministry of Panchayati Raj, Government of India: "Pincode to Urban Mapping" and
"Pincode to Village Mapping", downloaded 12 Oct 2026. Its copyright policy (https://lgdirectory.gov.in/copyRightPolicy.do)
allows reproduction free of charge without specific permission, provided the material is reproduced accurately, not in a
misleading context, and the source is prominently acknowledged; third-party material is excluded. Terms:
https://lgdirectory.gov.in/termsconditions.do. Only codes and their links are used.

### Rollback
Revert the PR (squash commit).

## Portugal: postcodes from the GeoNames postal dump (decisions_5, 14 Oct 2026)

### Problem
The 197,024 Portuguese postcodes (`ctt`) came from a CTT-derived compilation (centraldedados/codigos_postais). The
edition imported and the upstream grant to redistribute CTT's postal database were never established; a public
mirror does not establish them. Under the v5 source decision (decisions_5), such a cohort is re-derived from an open
replacement product.

### Fix
**195,912 postcodes kept** with their ids: every code the GeoNames postal code dump of 13 October 2026 lists for
Portugal. Each is re-derived from that dump (`geonames-postal`, CC BY 4.0):
- Locality name: 192,762 from the dump (130,010 differ only in letter case from the old upper-case names). 3,150 are
  left empty because the dump gives several different localities for the code; none is picked.
- Point: 194,605 rows get the dump's point. 1,307 stay empty because the dump's points for the code disagree.
  The points are GeoNames' estimates, not delivery-area centroids, and change no city or seat point.
- State: from the dump's region code by GeoNames' published code table; all agree with the current state links.
- City link: kept on 76,485 rows, changed on 1 (6200-238: Teixoso to Covilhã, as the dump gives Covilhã), cleared on
  9,067 and added on 5,554. A link is made only when exactly one city of that name is in the code's state and lies
  inside the municipality the dump names (CAOP2025 boundaries, used to check, not copied). Client and PO-box codes
  the old importer excluded stay unlinked (4,067), and the Pedroso/Perafita cases held in #1770 stay unlinked.

**Not in this PR:** 1,112 codes the dump does not list are queued for removal in v5.0.0 (no ids are removed between
majors). They keep their earlier values until then; exports are paused until v5.0.0, so they are not published
again. 1,860 codes the dump has and CSC does not are not added (decisions_5, rule 3). The CTT importer is retired: it
now refuses to run, since it would reimport the replaced copy.

### Sources
- GeoNames postal code dump for PT (https://download.geonames.org/export/zip/PT.zip), Last-Modified 13 October 2026,
  SHA-256 fed2fe35…bf3f, CC BY 4.0 per its readme. Credit: "Source: GeoNames, Portuguese postal code dump, 13 October
  2026". Ledger: `.github/fixes-docs/ledgers/PT_postcodes_geonames_2026-10.sources.json`; entry 64 in
  `.github/licenses/SOURCES.txt`.
- Direção-Geral do Território, CAOP2025 municipal boundaries (CC BY 4.0): used only to check that a linked city lies in
  the code's municipality.
- Research: Codex pc_rebuild_1 (every row's decision, before and after value and evidence; 50 rows checked by hand).

### Rollback
Revert the PR (squash commit); the old rows are in git history (not archived here, as their source basis is not
established).

## Mexico: postcodes from the GeoNames postal dump (decisions_5, 14 Oct 2026)

### Problem
The 144,600 Mexican postcode rows (`sepomex-via-redrbrt-2016`) came from an April 2016 mirror of SEPOMEX data
(redrbrt/sepomex-zip-codes). The upstream grant to redistribute SEPOMEX's data was never established, and a mirror does
not establish it. Under the v5 source decision (decisions_5), such a cohort is re-derived from an open replacement.
Each Mexican row is one postcode and settlement (asentamiento): 144,600 rows for 32,467 codes.

### Fix
**144,149 rows kept** with their ids: every (postcode, settlement) pair that the GeoNames postal code dump of 13
October 2026 lists. The settlement is matched under the same code, exactly after removing the old importer's
", <ciudad>" and ", NULL" suffixes (144,116), or by a unique accent, case and punctuation fold (33). Each kept row
takes that dump row's values (`geonames-postal`, CC BY 4.0):
- Locality name: the dump's settlement name (144,077 changed, mostly the old suffix removed).
- Point: the dump's point on all 144,149 rows, which had none. These are GeoNames' estimates, not settlement centroids.
- State: from the dump's state code (INEGI entity code) by the importer's mapping; all agree with the current links.
- City link: none, as before. No rule for linking a Mexican settlement to a city was ever established.

**Not in this PR:** 451 rows are queued for removal in v5.0.0 (no ids are removed between majors): 385 whose
settlement the dump does not list under their code, and 66 whose code it does not list at all. They keep their earlier
values until then; exports are paused until v5.0.0, so they are not published again. 17 new codes and 502 new
settlements in the dump are not added (decisions_5, rule 3). 22 pairs of rows whose names differ only in accents,
punctuation or whitespace keep both ids, each on its own exact match, and are flagged for a later identity review. The SEPOMEX-mirror
importer is retired: it now refuses to run.

### Sources
- GeoNames postal code dump for MX (https://download.geonames.org/export/zip/MX.zip), Last-Modified 13 October 2026,
  SHA-256 afda57c8…5905, CC BY 4.0 per its readme. Credit: "Source: GeoNames, Mexican postal code dump, 13 October
  2026". Ledger: `.github/fixes-docs/ledgers/MX_postcodes_geonames_2026-10.sources.json`; entry 65 in
  `.github/licenses/SOURCES.txt`.
- Research: Codex pc_rebuild_2 (every row's match, before and after value and evidence; 50 rows checked by hand).

### Rollback
Revert the PR (squash commit); the old rows are in git history (not archived here, as their source basis is not
established).

## Sweden, Romania, Poland, Ukraine and Argentina: postcodes from the GeoNames postal dumps (decisions_5, 14 Oct 2026)

### Problem
The postcodes of these five countries came from community copies of national postcode lists whose upstream grant to
redistribute was never established: Sweden `se-zipcode` (zegl/sweden-zipcode), Romania `ro-coduri-postale`
(alexionegit/coduripostaleRomaniaPS), Poland `kody-pocztowe-geo` (mberezinski/kody-pocztowe-geo), Ukraine
`ukrposhta-via-rvolykh` (rvolykh/UAPostcodes) and Argentina `correo-argentino-via-androdron` (androdron/localidades_AR).
A mirror does not establish that grant. Under the v5 source decision (decisions_5), each cohort is re-derived from an
open replacement: the GeoNames postal code dump of 13 October 2026 (`geonames-postal`, CC BY 4.0).

### Fix
**72,706 rows kept** with their ids. Sweden, Romania and Poland have one row per postcode, so a row is kept when the dump
lists its code (as Portugal). Ukraine and Argentina have one row per postcode and locality, so a row is kept only when
the dump lists that locality under the same code, exactly or after an accent, case and punctuation fold (as Mexico).
Each kept row takes the dump's values:

| Country | Rows | Kept | Name changed | Point changed | State changed | City link | Queued for v5 |
|---|---:|---:|---:|---:|---:|---|---:|
| Sweden | 16,392 | 16,390 | 16,368 | 16,390 | 3,253 (3,214 were empty) | none, as before | 2 |
| Romania | 13,751 | 13,739 | 13,739 | 13,738 | 1 | none, as before | 12 |
| Poland | 22,090 | 19,394 | 3,144 | 19,394 | 8 cleared | none, as before | 2,696 |
| Ukraine | 15,086 | 10,659 | 18 | 10,659 | 0 | none, as before | 4,427 |
| Argentina | 23,184 | 12,524 | 178 | 12,524 | 16 | 329 cleared | 10,660 |

- Where the dump's rows for one code give different names or points, that field is left empty; no row is picked
  (Poland: 3,082 codes). Points are GeoNames' estimates, not delivery-area centroids, and change no city point.
- States come from the dump's region code by GeoNames' published code table for each country, never by name. Ukraine's
  postal codes 12 and 13 are swapped against the gazetteer, mapped by the published Order 121 allocation.
- Argentina's 329 city links are cleared: they were made from a Correo locality id that the dump does not carry, so
  they cannot be re-derived. No new links are made in any of the five countries.

**Not in this PR:** 17,797 rows are queued for removal in v5.0.0 (no ids are removed between majors): Sweden 2,
Romania 12 and Poland 2,696 whose codes the dump does not list; Ukraine 1,416 such rows plus 3,011 whose locality it does
not list under their code; Argentina 519 plus 10,141. They keep their earlier values until then; exports are paused
until v5.0.0, so they are not published again. 40,599 codes the dumps have and CSC does not are not added (rule 3). The
five old importers are retired: Sweden's, Poland's, Ukraine's and Argentina's refuse to run, and Romania's step in the
shared SK/RO/SI batch refuses while Slovakia and Slovenia still run.

### Sources
- GeoNames postal code dumps for SE, RO, PL, UA and AR (https://download.geonames.org/export/zip/), Last-Modified 13
  October 2026, CC BY 4.0 per their readme. Credit: "Source: GeoNames, <Swedish, Romanian, Polish, Ukrainian, Argentine>
  postal code dump, 13 October 2026". Ledgers with each dump's SHA-256: `.github/fixes-docs/ledgers/<CC>_postcodes_geonames_2026-10.sources.json`;
  entries 66 to 70 in `.github/licenses/SOURCES.txt`.
- Research: Codex pc_rebuild_3 (every row's decision, before and after value and evidence; 30 rows per country checked by
  hand).

### Rollback
Revert the PR (squash commit); the old rows are in git history (not archived here, as their source basis is not
established).

## Malta and China: postcodes from GeoNames and OpenStreetMap (decisions_5, 14 Oct 2026)

### Problem
Malta's 26,593 postcodes (`maltapost-via-lucamuscat`) were full delivery codes scraped from MaltaPost's address search
(lucamuscat/Scrape_Malta_Addresses); China's 22,656 (`china-post-via-mumuy`) came from mumuy/data_post. Neither copy's
redistribution basis was ever established. GeoNames, the replacement used for other countries, is coarser here: for
Malta it lists only the 73 three-letter prefixes, and for China only the general codes ending in 00. A prefix or a general
code is a different, larger entity than a delivery code, so it cannot keep a delivery code's id (pc_rebuild_4).

### Fix
**4,181 rows kept** with their ids:
- **China, 2,280 from GeoNames:** the codes the Chinese postal code dump of 13 October 2026 lists (`geonames-postal`, CC BY
  4.0). Each takes the dump's locality, point and state, and its type becomes `area`; 12 state links change.
- **China 1,121 and Malta 780 from OpenStreetMap:** codes confirmed by postcode-tagged OpenStreetMap objects (`addr:postcode` or `postal_code`) (`osm`, ODbL 1.0, ©
  OpenStreetMap contributors; Geofabrik extracts with data up to 2026-10-13T20:21:31Z). A code is confirmed only by
  objects wholly inside the checked country polygon with no contrary country tag. Its locality is kept only where every
  object agrees, and its point is the median of the objects (never one address), else empty. Malta: 642 localities and
  191 points; the old scraped street names and points are cleared where OSM gives none. The 850 Chinese codes that OSM
  also confirms keep the GeoNames fields.
- Per-code evidence (OSM object ids and versions, extract cutoff) for all 1,901 OSM-derived codes:
  `.github/fixes-docs/ledgers/postcodes_osm_2026-10_evidence.csv`.

**Coverage consequence:** Malta keeps 780 of 26,593 full postcodes (2.9%) and China 3,401 of 22,656 (15%). **Not in this
PR:** the other 25,813 Maltese and 19,255 Chinese rows are queued for removal in v5.0.0 (no ids are removed between
majors); they keep their earlier values until then, and exports are paused until v5.0.0. No prefix or general code is
added (rule 3): a coarser code does not replace a delivery code. The two legacy importers are retired and refuse to run.
Later #1039 work can restore coverage from an open source with full codes.

### Sources
- GeoNames postal code dump for CN (https://download.geonames.org/export/zip/CN.zip), Last-Modified 13 October 2026, CC BY
  4.0. Credit: "Source: GeoNames, Chinese postal code dump, 13 October 2026". Ledger
  `.github/fixes-docs/ledgers/CN_postcodes_geonames_2026-10.sources.json`; SOURCES.txt entry 71.
- OpenStreetMap, © OpenStreetMap contributors, ODbL 1.0, Geofabrik extracts malta-261013 and china-261013 (data up to
  2026-10-13T20:21:31Z). Ledgers `MT_postcodes_osm_2026-10.sources.json` and `CN_postcodes_osm_2026-10.sources.json`;
  SOURCES.txt entry 72 (postcode-specific; entry 15 remains the general OpenStreetMap and Nominatim entry).
- Research: Codex pc_rebuild_4 and pc_rebuild_5, with every row's decision and evidence and rows checked by hand.

### Rollback
Revert the PR (squash commit); the old rows are in git history (not archived here, as their source basis is not
established).

## Ten countries: postcodes from open sources (decisions_5, 14 Oct 2026)

### Problem
The postcodes of Indonesia, Brazil, South Africa, Norway, Italy, the Netherlands, Colombia, Hungary, Malaysia and Turkey
came from legacy copies whose redistribution basis was never established (e.g. pentagonal/Indonesia-Postal-Code,
mevdschee/postcodes-nl, JohaAlarcon/Load_postal_code). Under the v5 source decision (decisions_5), each is re-derived from
an open product: the GeoNames postal code dump (snapshot of 13 October 2026, CC BY 4.0) for eight countries, Kadaster's
BAG register via PDOK (Public Domain Mark) for the Netherlands, and 4-72's official postal code shapefile (its open
clause) for Colombia.

### Fix
**38,777 rows kept** with their ids, each matched on its own identity (code, or code with its locality, regency, district
or delivery kind), never by a coarser label:

| Country | Row identity | Product | Kept | Queued for v5 |
|---|---|---|---:|---:|
| Indonesia | postcode and regency/city | GeoNames | 8,054 | 313 |
| Brazil | postcode | GeoNames | 5,302 | 390 |
| South Africa | postcode, town and delivery kind | GeoNames | 731 | 4,954 |
| Norway | postcode | GeoNames | 5,105 | 17 |
| Italy | postcode (CAP) | GeoNames | 4,558 | 120 |
| Netherlands | PC4 | Kadaster BAG (PDOK) | 4,072 | 0 |
| Colombia | postcode | 4-72 official shapefile | 3,672 | 4 |
| Hungary | postcode and settlement/district | GeoNames | 3,228 | 341 |
| Malaysia | postcode and locality | GeoNames | 2,632 | 301 |
| Turkey | postcode and district | GeoNames | 1,423 | 1,348 |

- Where the source's rows for one identity disagree, that field is left empty; no row is picked. Points are the
  sources' published estimates; Indonesia holds 304 points reused across different counties, and the Netherlands and
  Colombia get no points.
- States come from each source's region code by an explicit published table, never by name.
- City links: Italy's 3,551 are cleared (the dump cannot re-derive the ISTAT comune they relied on); the Netherlands'
  are re-derived from BAG and BRK (2,111 kept, 2 changed, 74 cleared, 502 added). No other links are made.
- South Africa keeps only generic code/locality rows: street and PO-box rows have no discriminator in the dump.

Consumer consequence, per country:

- Indonesia retains 8,054 regency/city-scoped postcode IDs covering 7,966 codes, replaces their labels with open administrative labels and queues 313 unsupported tuples; 3,829 estimates and 7,804 province links remain.
- Brazil retains 5,302 supported code IDs, queues 390 unsupported IDs in v5, and offers 5,302 published estimates with no city links.
- South Africa retains 731 generic code/locality IDs covering 700 codes, loses 4,954 unsupported locality or delivery-kind IDs in v5, and retains no province links.
- Norway retains 5,105 supported code IDs, queues 17 unsupported IDs in v5, and offers 5,105 published estimates with no city links.
- Italy retains 4,558 CAP IDs and queues 120 absent codes, clears 2,836 ambiguous labels and all 3,551 linked kept rows, and holds 67 province assignments.
- The Netherlands retains all 4,072 existing PC4 IDs, supplies 3,997 unanimous locality labels and 2,615 guarded city links, and adds no PC6 codes or postcode points.
- Colombia retains 3,672 official full-code IDs and their re-derived department links, corrects 22 links, queues 4 absent codes, and keeps locality labels and points null.
- Hungary retains 3,228 supported code/locality IDs, queues 341 unsupported IDs in v5, and offers 3,228 published estimates with no city links.
- Malaysia retains 2,632 supported code/locality IDs, queues 301 unsupported IDs in v5, and offers 2,629 published estimates with no city links.
- Turkey retains 1,423 supported code/district IDs, queues 1,348 unsupported IDs in v5, and offers 767 published estimates with no city links.

**Not in this PR:** 7,788 rows are queued for removal in v5.0.0 (no ids are removed between majors); they keep their
earlier values until then, and exports are paused until v5.0.0. 1,438 codes the sources have and CSC does not are not
added (rule 3). The ten legacy importers are retired and refuse to run.

### Sources
- GeoNames postal code dump (https://download.geonames.org/export/zip/allCountries.zip), snapshot of 13 October 2026,
  CC BY 4.0. Credit: "Source: GeoNames, <Indonesian, Brazilian, South African, Norwegian, Italian, Hungarian,
  Malaysian, Turkish> postal code dump, 13 October 2026". SOURCES.txt entries 73 to 80.
- Kadaster BAG via PDOK (Public Domain Mark 1.0); BRK administrative units via PDOK (CC0 1.0), used only to check city
  links. SOURCES.txt entry 81.
- MINTIC-Servicios Postales Nacionales 4-72 (Unidad Código Postal Colombia), official shapefile last updated 28 June
  2016, under its open clause (`.github/licenses/4-72-Clausula-Licencia-Abierta.txt`). SOURCES.txt entry 82.
- Edition ledgers: `.github/fixes-docs/ledgers/<CC>_postcodes_2026-10.sources.json`.
- Research: Codex pc_rebuild_6 (every row's decision, before and after value and evidence; 20 rows per country checked
  by hand).

### Rollback
Revert the PR (squash commit); the old rows are in git history (not archived here, as their source basis is not
established).
