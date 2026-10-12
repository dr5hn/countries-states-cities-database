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
skipped). Each row has source `cartociudad`; **10,675** carry their province (state) because all their addresses lie in one
province (176 codes span two provinces and have none); **6,313** link to their municipality's city record because all
their addresses lie in one municipality whose CSC record is verified by its INE code; `locality_name` is that
municipality's name where there is only one. The point is the mean of the code's address points (ETRS89, or REGCAN95 in
the Canaries), a derived value. Leading zeros are kept. New rows get their ids on import. The removed rows were not
postcodes, so they are not archived here; they stay in git history.

Per-postcode ledger (addresses, provinces, INE municipalities): [ES_postcodes_cartociudad_2026-04.csv](ledgers/ES_postcodes_cartociudad_2026-04.csv).

| Province file | Addresses | Codes | SHA-256 |
| --- | ---: | ---: | --- |
| ALAVA | 52,528 | 84 | `1aa868bca107fb09…` |
| ALBACETE | 188,636 | 134 | `2cb0a5c102ba5580…` |
| ALICANTE | 558,417 | 213 | `832cb97543a19226…` |
| ALMERIA | 296,709 | 166 | `514440306cc7a743…` |
| ASTURIAS | 336,086 | 401 | `51769566d87c49c7…` |
| AVILA | 191,378 | 148 | `e291f83a403e4d8c…` |
| A_CORUNA | 317,927 | 377 | `8f6d92669e76bf59…` |
| BADAJOZ | 338,650 | 214 | `ea92b9f68ff4bb24…` |
| BALEARES | 418,098 | 159 | `9d04c9f1544c5095…` |
| BARCELONA | 1,165,281 | 394 | `02d0467ae327cd8d…` |
| BURGOS | 270,877 | 222 | `de2c6fc414f7b6f5…` |
| CACERES | 285,310 | 244 | `7b6c914e085b5877…` |
| CADIZ | 376,772 | 115 | `d0987a18be27cada…` |
| CANTABRIA | 203,616 | 216 | `3023a148b8a58e75…` |
| CASTELLON | 262,806 | 134 | `0a7969df94ba5259…` |
| CEUTA | 7,469 | 5 | `f1a69367295364a4…` |
| CIUDAD_REAL | 246,473 | 130 | `595b17942d1ba5ae…` |
| CORDOBA | 302,102 | 142 | `783115d1bea83d18…` |
| CUENCA | 213,797 | 182 | `edd45b3d95a282c7…` |
| GIRONA | 374,999 | 253 | `372115ef433c67f4…` |
| GRANADA | 441,330 | 200 | `9a62e8b256e2d310…` |
| GUADALAJARA | 225,663 | 181 | `ff6b0be5607a0770…` |
| GUIPUZCOA | 71,266 | 113 | `7d14178d399f48e6…` |
| HUELVA | 247,480 | 103 | `74fbfbcaf51c57ef…` |
| HUESCA | 118,006 | 272 | `776b7ad0463b50fe…` |
| JAEN | 301,934 | 173 | `5abc21fd6603152f…` |
| LAS_PALMAS | 245,149 | 144 | `d7034840e1c4f147…` |
| LA_RIOJA | 143,770 | 130 | `47aafcfd3f1c056e…` |
| LEON | 360,864 | 418 | `5ffa5c9614a59725…` |
| LLEIDA | 218,832 | 303 | `8e5eca4a9b6a54d5…` |
| LUGO | 216,443 | 462 | `3d2d91c3923b9500…` |
| MADRID | 930,532 | 306 | `78ccfc557dbf72aa…` |
| MALAGA | 519,814 | 160 | `0e93e8e5fdf42bb9…` |
| MELILLA | 11,674 | 6 | `b8b27aca6e76cd7f…` |
| MURCIA | 479,813 | 212 | `87aa80d3fc1cb7b2…` |
| NAVARRA | 177,712 | 265 | `9da824010261454a…` |
| OURENSE | 233,419 | 296 | `fd12e96f6e8ea400…` |
| PALENCIA | 111,279 | 132 | `12fb806d53690413…` |
| PONTEVEDRA | 336,530 | 378 | `8ad77902ddfc593a…` |
| SALAMANCA | 232,766 | 274 | `8dda47787b867bb2…` |
| SEGOVIA | 145,906 | 203 | `fe7b386a3c33a49c…` |
| SEVILLA | 683,257 | 155 | `1d0feef80cf1a596…` |
| SORIA | 114,248 | 97 | `dcc75aa273669665…` |
| TARRAGONA | 368,257 | 213 | `7aa8f388d52d4b4c…` |
| TENERIFE | 283,015 | 216 | `7defaf4a20773e86…` |
| TERUEL | 129,684 | 210 | `1dd0fb2402a118ed…` |
| TOLEDO | 446,892 | 235 | `8f383a826a4bcb7a…` |
| VALENCIA | 710,063 | 298 | `c3e61fb9c4e7fea8…` |
| VALLADOLID | 175,995 | 192 | `27ffb166f9bac4fd…` |
| VIZCAYA | 97,331 | 144 | `a0901f84d3090de2…` |
| ZAMORA | 199,413 | 297 | `3733959648c0e92c…` |
| ZARAGOZA | 232,456 | 279 | `b48b914c9958e03a…` |

### Sources
Obra derivada de CartoCiudad 2026 CC-BY 4.0 scne.es: CartoCiudad province GeoPackages, edition 04/2026, Centro de
Descargas del CNIG (https://centrodedescargas.cnig.es/CentroDescargas/cartociudad), licensed under CC BY 4.0
(https://creativecommons.org/licenses/by/4.0/). Modification: addresses aggregated to one row per postcode, with the
province, single municipality and mean point derived as described.

### Rollback
Revert the PR (squash commit).
