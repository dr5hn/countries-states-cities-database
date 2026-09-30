# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Country fields out of date

An audit of `countries.json` against Wikidata and the IANA time zone database (tzdata 2026c) found 32 values that are
wrong today. Only those fields change.

### Currency, domain and capital
| Country | Field | Was | Now | Why |
|---|---|---|---|---|
| Congo (CG) | currency, name, symbol | CDF, Congolese Franc, FC | XAF, Central African CFA franc, FCFA | CDF is the DR Congo's franc; the Republic of the Congo uses the CFA franc, as Cameroon and the CAR do in this file |
| Curaçao (CW) | currency, name, symbol | ANG, Netherlands Antillean guilder, ƒ | XCG, Caribbean guilder, Cg | The Caribbean guilder replaced the ANG on 31 March 2025 |
| Sint Maarten (SX) | currency, name, symbol | as Curaçao | as Curaçao | Same currency union |
| Bonaire, Sint Eustatius and Saba (BQ) | tld | .an | .bq | .an (Netherlands Antilles) was retired in 2015; .bq is the ISO-based ccTLD |
| Burundi (BI) | capital | Bujumbura | Gitega | Gitega has been the political capital since 2019 (Bujumbura remains the economic capital) |

### Time zone offsets
The file stores each zone's **standard** (non-daylight) offset: New York is EST (−5), Berlin CET (+1). Two groups
break that:

- **Offsets changed by law since the data was generated:** Kazakhstan moved to UTC+5 (March 2024); Chihuahua and
  Ojinaga to UTC−6 (2022); Jordan and Syria to permanent UTC+3 (2022); Volgograd to UTC+3 (2020); Samoa dropped
  daylight saving (2021); South Sudan to UTC+2 (2021); Nuuk and Scoresbysund to UTC−2 (2023–24); Norfolk Island's
  standard time is UTC+11 (2015); Vostok is UTC+5 and Casey UTC+8.
- **Southern-hemisphere zones stored their summer offset:** Australia (Sydney, Melbourne, Hobart, Adelaide, Broken
  Hill, Lord Howe, Currie, Macquarie), New Zealand (Auckland, Chatham, McMurdo) and Chile (Santiago, Easter Island).

Each new value is checked against tzdata 2026c: it is the zone's smaller 2026 offset (its standard time). The
abbreviation and name follow (e.g. AEDT → AEST); Kazakhstan's garbled "Alma-Ata Time[1" becomes "Kazakhstan Time".

| Country | Zone | gmtOffset was | Now |
|---|---|---:|---:|
| AQ | Antarctica/Casey | 39600 | 28800 |
| AQ | Antarctica/McMurdo | 46800 | 43200 |
| AQ | Antarctica/Vostok | 21600 | 18000 |
| AU | Antarctica/Macquarie | 39600 | 36000 |
| AU | Australia/Adelaide | 37800 | 34200 |
| AU | Australia/Broken_Hill | 37800 | 34200 |
| AU | Australia/Currie | 39600 | 36000 |
| AU | Australia/Hobart | 39600 | 36000 |
| AU | Australia/Lord_Howe | 39600 | 37800 |
| AU | Australia/Melbourne | 39600 | 36000 |
| AU | Australia/Sydney | 39600 | 36000 |
| CL | America/Santiago | −10800 | −14400 |
| CL | Pacific/Easter | −18000 | −21600 |
| GL | America/Nuuk | −10800 | −7200 |
| GL | America/Scoresbysund | −3600 | −7200 |
| JO | Asia/Amman | 7200 | 10800 |
| KZ | Asia/Almaty | 21600 | 18000 |
| KZ | Asia/Qostanay | 21600 | 18000 |
| MX | America/Chihuahua | −25200 | −21600 |
| MX | America/Ojinaga | −25200 | −21600 |
| NZ | Pacific/Auckland | 46800 | 43200 |
| NZ | Pacific/Chatham | 49500 | 45900 |
| NF | Pacific/Norfolk | 43200 | 39600 |
| RU | Europe/Volgograd | 14400 | 10800 |
| WS | Pacific/Apia | 50400 | 46800 |
| SS | Africa/Juba | 10800 | 7200 |
| SY | Asia/Damascus | 7200 | 10800 |

### Also found (not changed here)
- **Debatable:** Palau's capital (Wikidata: Ngerulmud, the seat of government in Melekeok state), Equatorial
  Guinea's (Wikidata: Ciudad de la Paz), Kosovo's iso3 (XKX, used by the EU and others; Wikidata: XKS). Morocco and
  Western Sahara store UTC+1, which they observe most of the year, while tzdata calls UTC+0 standard.
- **Postal codes:** 21 countries' `postal_code_format` and `postal_code_regex` disagree (e.g. Greece's format
  `### ##` vs a regex for five digits with no space; Honduras `#####` vs six digits). Each needs checking against the
  national postal service.
- **Zone ownership:** a few countries list another country's zone (Kosovo Europe/Belgrade, Sint Maarten
  America/Anguilla, Bouvet Island Europe/Oslo); these are tzdata link zones and are left as they are.

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/countries/countries.json` — timezone offsets on 27 zones; currency on 3 countries; tld on 1; capital on 1
