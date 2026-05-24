# #1039 Postcode Sources Research

Snapshot of public-mirror availability for the postcode importers tracked under
issue [#1039](https://github.com/dr5hn/countries-states-cities-database/issues/1039).
Generated 2026-04-27 after a session-long sweep that took shipped coverage
from ~34 to **74 country/territory codes**.

This is a *research* document, not a checklist of currently-merged data — for
that, see `git log master --oneline | grep 'feat(postcodes/'`. Each tier below
captures whether a clean, redistributable, GeoNames-free GitHub mirror has
been *located*; tier descriptions are about source quality, not about what
has been shipped to `contributions/postcodes/` yet.

## Tier A — High priority: clean source found, ready to ship

| iso2 | Country | Source | Records | Pros | Cons |
|---|---|---|---|---|---|
| **CN** | China | [`mumuy/data_post`](https://github.com/mumuy/data_post) `list.json` | ~22,656 | Comprehensive 6-digit postcode→city map; large mature repo (45 ⭐) | dict-keyed (postcode→single name); no district/province FK in source — need separate prov code map (first 2 digits) |
| **MM** | Myanmar | [`MyanmarPost/MyanmarPostalCode`](https://github.com/MyanmarPost/MyanmarPostalCode) `Myanmar_Locations_Postal_Code_EN.csv` | ~5–10k | **Official MyanmarPost org** — best provenance possible; English+Burmese variants; Region/State + Township + Postcode columns | Verify license file before shipping |
| **MX** | Mexico | [`redrbrt/sepomex-zip-codes`](https://github.com/redrbrt/sepomex-zip-codes) `sepomex_abril-2016.csv` | ~145k | 12MB CSV with Estado/Municipio/Ciudad/Colonia/CP; 45 ⭐ | Snapshot is 2016 — stale; SEPOMEX official feed paywalled |
| **HU** | Hungary | [`pbakondy/hu-postal-codes`](https://github.com/pbakondy/hu-postal-codes) per-city JSONs | ~10k | Active, MIT-style; per-city files (budapest.json 1MB, etc.) | Per-city files — needs aggregate + county FK derivation |
| **HU** | Hungary (alt) | [`ferenci-tamas/IrszHnk`](https://github.com/ferenci-tamas/IrszHnk) `IrszHnk.csv` (400KB) | ~3.5k | Single-file CSV; postal codes paired with town/county | Per-locality not per-street |
| **CA** | Canada | [`rafflebox-technologies-inc/ca-postal-codes`](https://github.com/rafflebox-technologies-inc/ca-postal-codes) | TBD | Public scrape | Source incomplete vs ~870k FSAs+full postcodes; CPC bulk PAID |
| **GB** | UK | [`dwyl/uk-postcodes-latitude-longitude-complete-csv`](https://github.com/dwyl/uk-postcodes-latitude-longitude-complete-csv) | ~2.6M | 15 ⭐; complete as of 2017 | Stale (2017); Royal Mail PAF charges for refreshes |
| **TW** | Taiwan | [`flying-itmen-eagle/eagle-tw-open-data`](https://github.com/flying-itmen-eagle/eagle-tw-open-data) `taiwan_postal_code_information.csv` | ~370 | Government open-data flavour; 3-digit county codes | **Big5 encoding** (mojibake on UTF-8 read — needs `cp950` decode); only county-level, not 5/6-digit |
| **BN** | Brunei | [`xplorasia/brunei-zipcode`](https://github.com/xplorasia/brunei-zipcode) `bn-zipcode.json` (85KB) | ~few hundred | JSON ready to import | Small country, low-volume payoff |

## Tier B — Promising but needs work

| iso2 | Country | Source | Notes |
|---|---|---|---|
| **CZ** | Czech Republic | [`soit-sk/czech_republic_post_codes_2007`](https://github.com/soit-sk/czech_republic_post_codes_2007) | Only ships a Perl scraper for the 2007 stamps DB; would need to run scraper + fetch from Česká pošta b2b (memory: TLS handshake fails) |
| **FI** | Finland | [`launis/areadata`](https://github.com/launis/areadata) | Wrapper, not bulk CSV; Posti's `PCF_*.dat` file is canonical but URL is date-stamped — known difficult per memory |
| **IR** | Iran | `saeidi-dev/Postal-Code-Iran` | Range-based PHP switch only — produces **no canonical list of 10-digit codes**, just prefix→state lookup |
| **TN** | Tunisia | `hajer77/postCodeTunisia-api` | Stub only (8/24 governorates, 9 records) |
| **TZ** | Tanzania | `meshackjr/Tanzania-Postal-Codes-SQL` | Only Dar es Salaam (1/31 regions) |
| **PE** | Peru | `mvegap/ubigeo-peru-select` | UBIGEO admin codes ≠ SERPOST 5-digit postal codes |
| **PA** | Panama | `viquezr-dev/codigos_postales` | GeoJSON ships non-standard alphanumeric (`H1301`/`BA`) — doesn't match `^(\d{5})$` regex |
| **PY** | Paraguay | `3lD4m14n/mapa-codigos-postales-paraguay` | Only ships a 17 MB shapefile zip — needs unpacking + DBF parse |

## Tier C — Confirmed dead-ends (no useful public mirror)

Searched ≥2 query angles each, all returned validators/API wrappers/empty repos.
Full notes and rejection reasons in
`memory/project_1039_postcodes_status.md` under *Dead-end / blocked targets*.

`PK BG LT EE MK BA AL HN ZM NI OM SA IL EG LB JO IQ SN ET CL KR RU UY GT SR LK CU TT KZ BY AM AZ GE`

## Tier D — No postal-code system (CSC `regex` is null, correctly)

`HK SG UAE-partial JM FJ BO GH UG MO` — these countries don't operate a national
postcode system. CSC's `countries.json` already reflects this. Not shippable.

## Tier E — Untried, possibly viable (next session targets)

| iso2 | Country | Notes |
|---|---|---|
| **LU** | Luxembourg | Should be in OpenPLZ; the existing DACH importer (#1431) shipped DE/AT/CH only — extending to LU is low-hanging fruit |
| **AF UZ KG TJ TM** | Afghanistan + Central Asia "Stans" | All have 4-6 digit postal codes; minimal GH presence — needs manual probing of `post.uz` etc. |
| **MV BT** | Maldives / Bhutan | Small markets, postcode systems exist (introduced 2014/2015); GH mirrors not yet found |
| **AE QA BH KW YE** | Gulf | UAE/Qatar no system; BH/KW/YE have systems — limited mirrors |
| **CM CI MA-redo** | French-speaking Africa | Likely scoped to `data.gouv.fr`-style portals; low GH discoverability |

---

## Source-class taxonomy (from `feedback_postcode_pipelines.md`)

When evaluating any new mirror, check it against these tiers (order of
acceptability for #1039):

1. **CC-0 / public domain** — US Census, DK DAWA. No attribution needed.
2. **ODbL** (matches repo licence) — OpenPLZ DACH. Cleanest.
3. **CC-BY** — Australia Post (matthewproctor mirror), Italy Istat. Attribution recorded in `source` column.
4. **etalab-2.0 / NDSAP / Open Government** — France La Poste, India Post. Attribution recorded.
5. **Free redistribution permitted, no formal licence** — Japan Post KEN_ALL, Norway Bring, community mirrors (PL/BR/RO/SK/SI/SE/ES/...). Acceptable but flag in PR.
6. **GeoNames-derived** — *Excluded by user instruction* from the start. matthewproctor/AU and zauberware are partially derived but ship under their own attribution; generally OK.
7. **Paid only** — Royal Mail PAF (UK), Eircode (IE), Deutsche Post full, Correios full BR, SEPOMEX MX, Canada Post bulk. Skip.

## Network access pattern

The harness allows direct `urllib.request.urlopen()` to most domains used
previously (data.gouv.fr, raw.githubusercontent.com, openplzapi.org,
www2.census.gov, www.bring.no, api.dataforsyningen.dk, datanova.laposte.fr,
www.posti.fi, www.post.japanpost.jp, plus all GitHub raw/API endpoints).
New domains may need user authorization. `curl` from Bash is more often
blocked than Python urllib.

## Recommended order if shipping continues

By expected payoff (records × shippability × population):

1. **MM** — official org, ~5-10k codes, ~1-2 hr (clean win)
2. **CN** — 22k codes, ~1.4B people; needs hand-curated 2-digit prefix → province map (34 provinces, mostly direct iso2 numeric match)
3. **MX** — 145k codes, regex `^\d{5}$`, 32 states; data is stale (2016) but useful
4. **HU** — 3.5k codes, single-file CSV ready, county FK derivable
5. **LU** — extend the existing DACH importer; minimal new code
6. **TW** — small (~370 county-level rows) but needs `cp950` decode; politically sensitive (CSC iso2 mapping)
7. **CA** — verify rafflebox volume; CPC paid feed is the alternative
8. **GB** — 2.6M rows is *large*; postcode regex `^[A-Z]{1,2}[0-9R][0-9A-Z]?\s?[0-9][A-Z]{2}$` — verify dataset format against CSC regex first
9. **BN** — small but easy
