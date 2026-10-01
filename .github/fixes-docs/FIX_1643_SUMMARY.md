# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## States and cities on the wrong time zone

**95 states and 1,535 cities** get the right IANA time zone. #1649 checked each city against its neighbours;
that misses these, because here the wrong zone is shared by a whole state, most of its cities, or a whole country.

### States (95)
- **Russia (27):** federal subjects outside Moscow time were stored as `Europe/Moscow`; each takes its legal zone.
- **Papua New Guinea (21):** every province was on `Pacific/Bougainville` (UTC+11); only Bougainville uses it, the
  rest of the country is on `Pacific/Port_Moresby` (UTC+10).
- **Indonesia (17):** provinces on central time (WITA, UTC+8: Nusa Tenggara, Sulawesi, South/East/North
  Kalimantan) or eastern time (WIT, UTC+9: North Maluku and the five newer Papua provinces) were stored as
  `Asia/Jakarta` (UTC+7); Maluku and Papua already had `Asia/Jayapura`.
- **DR Congo (16):** the eastern provinces (Kivu, Katanga, Kasaï, Ituri, Uélé, Maniema, Tshopo…) were on
  `Africa/Kinshasa` (UTC+1); they are on `Africa/Lubumbashi` (UTC+2).
- **Mongolia (5):** Khovd, Uvs and Bayan-Ölgii are on `Asia/Hovd` (UTC+7) in tzdata. Zavkhan and Govi-Altai follow
  tzdata too (a #1643 decision): both states move from the `Asia/Choibalsan` alias to `Asia/Ulaanbaatar` (UTC+8), and
  their two cities, Uliastay and Altai, from `Asia/Hovd`. Mongolia's standards agency lists the two aimags on UTC+7;
  tzdata follows the observed UTC+8 and records the conflict.
- **French Polynesia (4):** the Austral, Leeward, Windward and Tuamotu-Gambier groups were on `Pacific/Gambier`
  (UTC−9); they are on Tahiti time (UTC−10), except the Gambier Islands themselves.
- **Kiribati (2), Micronesia (2), Greenland (1):** Gilbert and Line Islands had the Phoenix Islands' zone; Kosrae
  and Pohnpei had Chuuk's (UTC+10, they are UTC+11); Qeqertalik (west coast) had Danmarkshavn's UTC+0.

| Country | State | Was | Now |
|---|---|---|---|
| CD | Bas-Uélé | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Haut-Katanga | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Haut-Lomami | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Haut-Uélé | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Ituri | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Kasaï Central | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Kasaï Oriental | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Kasaï | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Lomami | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Lualaba | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Maniema | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Nord-Kivu | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Sankuru | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Sud-Kivu | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Tanganyika | Africa/Kinshasa | Africa/Lubumbashi |
| CD | Tshopo | Africa/Kinshasa | Africa/Lubumbashi |
| FM | Kosrae | Pacific/Chuuk | Pacific/Kosrae |
| FM | Pohnpei | Pacific/Chuuk | Pacific/Pohnpei |
| GL | Qeqertalik | America/Danmarkshavn | America/Nuuk |
| ID | Kalimantan Timur | Asia/Jakarta | Asia/Makassar |
| ID | Kalimantan Selatan | Asia/Jakarta | Asia/Makassar |
| ID | Kalimantan Utara | Asia/Jakarta | Asia/Makassar |
| ID | Maluku Utara | Asia/Jakarta | Asia/Jayapura |
| ID | Nusa Tenggara Barat | Asia/Jakarta | Asia/Makassar |
| ID | Nusa Tenggara Timur | Asia/Jakarta | Asia/Makassar |
| ID | Nusa Tenggara | Asia/Jakarta | Asia/Makassar |
| ID | Papua Barat | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Barat Daya | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Pegunungan | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Selatan | Asia/Jakarta | Asia/Jayapura |
| ID | Papua Tengah | Asia/Jakarta | Asia/Jayapura |
| ID | Sulawesi Utara | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Tenggara | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Selatan | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Barat | Asia/Jakarta | Asia/Makassar |
| ID | Sulawesi Tengah | Asia/Jakarta | Asia/Makassar |
| KI | Gilbert | Pacific/Enderbury | Pacific/Tarawa |
| KI | Line | Pacific/Enderbury | Pacific/Kiritimati |
| MN | Khovd | Asia/Choibalsan | Asia/Hovd |
| MN | Uvs | Asia/Choibalsan | Asia/Hovd |
| MN | Bayan-Ölgii | Asia/Choibalsan | Asia/Hovd |
| PF | Austral Islands | Pacific/Gambier | Pacific/Tahiti |
| PF | Leeward Islands | Pacific/Gambier | Pacific/Tahiti |
| PF | Tuamotu-Gambier | Pacific/Gambier | Pacific/Tahiti |
| PF | Windward Islands | Pacific/Gambier | Pacific/Tahiti |
| PG | Chimbu | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Central | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | East New Britain | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Eastern Highlands | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Enga | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | East Sepik | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Gulf | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Hela | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Jiwaka | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Milne Bay | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Morobe | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Madang | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Manus | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Port Moresby | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | New Ireland | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Oro | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Sandaun | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Southern Highlands | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | West New Britain | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Western Highlands | Pacific/Bougainville | Pacific/Port_Moresby |
| PG | Western | Pacific/Bougainville | Pacific/Port_Moresby |
| RU | Altai Republic | Europe/Moscow | Asia/Barnaul |
| RU | Altai Krai | Europe/Moscow | Asia/Barnaul |
| RU | Amur | Europe/Moscow | Asia/Yakutsk |
| RU | Astrakhan | Europe/Moscow | Europe/Astrakhan |
| RU | Bashkortostan | Europe/Moscow | Asia/Yekaterinburg |
| RU | Buryatia | Europe/Moscow | Asia/Irkutsk |
| RU | Chelyabinsk | Europe/Moscow | Asia/Yekaterinburg |
| RU | Kemerovo | Europe/Moscow | Asia/Novokuznetsk |
| RU | Kurgan | Europe/Moscow | Asia/Yekaterinburg |
| RU | Khabarovsk | Europe/Moscow | Asia/Vladivostok |
| RU | Khanty-Mansi | Europe/Moscow | Asia/Yekaterinburg |
| RU | Khakassia | Europe/Moscow | Asia/Krasnoyarsk |
| RU | Novosibirsk | Europe/Moscow | Asia/Novosibirsk |
| RU | Orenburg | Europe/Moscow | Asia/Yekaterinburg |
| RU | Perm | Europe/Moscow | Asia/Yekaterinburg |
| RU | Primorsky | Europe/Moscow | Asia/Vladivostok |
| RU | Sakha | Europe/Moscow | Asia/Yakutsk |
| RU | Saratov | Europe/Moscow | Europe/Saratov |
| RU | Sverdlovsk | Europe/Moscow | Asia/Yekaterinburg |
| RU | Tomsk | Europe/Moscow | Asia/Tomsk |
| RU | Tuva | Europe/Moscow | Asia/Krasnoyarsk |
| RU | Tyumen | Europe/Moscow | Asia/Yekaterinburg |
| RU | Udmurt | Europe/Moscow | Europe/Samara |
| RU | Ulyanovsk | Europe/Moscow | Europe/Ulyanovsk |
| RU | Yamalo-Nenets | Europe/Moscow | Asia/Yekaterinburg |
| RU | Jewish | Europe/Moscow | Asia/Vladivostok |
| RU | Zabaykalsky | Europe/Moscow | Asia/Chita |

### Cities (1,535)
- **Single-zone states:** a city on another offset takes the state's zone (Western Australia's towns on Sydney
  time; Mato Grosso, Mato Grosso do Sul, Rondônia and Acre on São Paulo time; Sinaloa; the Indonesian, Papua New
  Guinean, Congolese and Russian cases above). Western Australia's Eucla area (east of 125.5°E, UTC+8:45) is excluded.
- **Elsewhere:** a city whose offset differs from its state's zone, while at least 4 of its 5 nearest same-state
  cities are on the state's offset, takes their zone (e.g. Sonora on Mexico City time, Alberta on Toronto time).
  Multi-zone areas keep their cities, since there the neighbours share the city's offset.
- **By hand:** British Columbia's Central Coast and Port McNeill (Vancouver), Peace River (Dawson Creek), Elkford
  (Edmonton); Amazonas' central and northern municipalities (Manaus) and Atalaia do Norte, Envira and Ipixuna (Eirunepé,
  UTC−5); Sakha's Moscow-time cities in Yakutsk-time districts (Yakutsk).
- **Guard:** a city is changed only when at least 3 of its 5 nearest same-country cities are filed in the same state.
  This does not catch a batch filed in the wrong state together: the review found two such records moved across a
  zone line (Milpillas, Puente de Camotlán) and they are left as they were.

| Country | State | City zone was | Now | Cities |
|---|---|---|---|---:|
| BR | Mato Grosso | America/Sao_Paulo | America/Cuiaba | 121 |
| AU | Western Australia | Australia/Sydney | Australia/Perth | 118 |
| RU | Altai Krai | Europe/Moscow | Asia/Barnaul | 67 |
| BR | Mato Grosso do Sul | America/Sao_Paulo | America/Campo_Grande | 56 |
| RU | Irkutsk | Europe/Moscow | Asia/Irkutsk | 53 |
| RU | Bashkortostan | Europe/Moscow | Asia/Yekaterinburg | 49 |
| RU | Krasnoyarsk | Europe/Moscow | Asia/Krasnoyarsk | 49 |
| RU | Zabaykalsky | Europe/Moscow | Asia/Chita | 46 |
| BR | Rondônia | America/Sao_Paulo | America/Porto_Velho | 45 |
| RU | Chelyabinsk | Europe/Moscow | Asia/Yekaterinburg | 43 |
| RU | Amur | Europe/Moscow | Asia/Yakutsk | 38 |
| RU | Primorsky | Europe/Moscow | Asia/Vladivostok | 33 |
| RU | Sakha | Europe/Moscow | Asia/Yakutsk | 29 |
| RU | Novosibirsk | Europe/Moscow | Asia/Novosibirsk | 28 |
| RU | Saratov | Europe/Moscow | Europe/Saratov | 25 |
| RU | Sverdlovsk | Europe/Moscow | Asia/Yekaterinburg | 25 |
| RU | Kemerovo | Europe/Moscow | Asia/Novokuznetsk | 24 |
| RU | Tyumen | Europe/Moscow | Asia/Yekaterinburg | 23 |
| RU | Orenburg | Europe/Moscow | Asia/Yekaterinburg | 22 |
| RU | Buryatia | Europe/Moscow | Asia/Irkutsk | 21 |
| RU | Ulyanovsk | Europe/Moscow | Europe/Ulyanovsk | 21 |
| ID | Nusa Tenggara Timur | Asia/Jakarta | Asia/Makassar | 18 |
| ID | Sulawesi Selatan | Asia/Jakarta | Asia/Makassar | 18 |
| MX | Sinaloa | America/Mexico_City | America/Mazatlan | 18 |
| RU | Khabarovsk | Europe/Moscow | Asia/Vladivostok | 18 |
| RU | Kurgan | Europe/Moscow | Asia/Yekaterinburg | 18 |
| RU | Perm | Europe/Moscow | Asia/Yekaterinburg | 18 |
| RU | Omsk | Europe/Moscow | Asia/Omsk | 17 |
| BR | Amazonas | America/Sao_Paulo | America/Manaus | 16 |
| ID | Sulawesi Tenggara | Asia/Jakarta | Asia/Makassar | 16 |
| RU | Kamchatka | Europe/Moscow | Asia/Kamchatka | 16 |
| RU | Samara | Europe/Moscow | Europe/Samara | 16 |
| RU | Tomsk | Europe/Moscow | Asia/Tomsk | 16 |
| CA | British Columbia | America/Toronto | America/Vancouver | 15 |
| PF | Tuamotu-Gambier | Pacific/Gambier | Pacific/Tahiti | 15 |
| RU | Khakassia | Europe/Moscow | Asia/Krasnoyarsk | 13 |
| RU | Tuva | Europe/Moscow | Asia/Krasnoyarsk | 12 |
| MX | Sonora | America/Mexico_City | America/Hermosillo | 11 |
| PF | Windward Islands | Pacific/Gambier | Pacific/Tahiti | 11 |
| RU | Altai Republic | Europe/Moscow | Asia/Barnaul | 11 |
| BR | Acre | America/Sao_Paulo | America/Rio_Branco | 10 |
| ID | Sulawesi Tengah | Asia/Jakarta | Asia/Makassar | 10 |
| KI | Gilbert | Pacific/Enderbury | Pacific/Tarawa | 10 |
| RU | Jewish | Europe/Moscow | Asia/Vladivostok | 10 |
| ID | Kalimantan Selatan | Asia/Jakarta | Asia/Makassar | 9 |
| ID | Sulawesi Utara | Asia/Jakarta | Asia/Makassar | 9 |
| PG | Morobe | Pacific/Bougainville | Pacific/Port_Moresby | 9 |
| ID | Maluku | Asia/Jakarta | Asia/Jayapura | 8 |
| ID | Papua | Asia/Jakarta | Asia/Jayapura | 8 |
| RU | Astrakhan | Europe/Moscow | Europe/Astrakhan | 8 |
| RU | Udmurt | Europe/Moscow | Europe/Samara | 8 |
| FM | Pohnpei | Pacific/Chuuk | Pacific/Pohnpei | 7 |
| ID | Maluku Utara | Asia/Jakarta | Asia/Jayapura | 7 |
| ID | Papua Pegunungan | Asia/Jakarta | Asia/Jayapura | 7 |
| PG | Eastern Highlands | Pacific/Bougainville | Pacific/Port_Moresby | 7 |
| CA | Alberta | America/Toronto | America/Edmonton | 6 |
| ID | Kalimantan Timur | Asia/Jakarta | Asia/Makassar | 6 |
| ID | Papua Tengah | Asia/Jakarta | Asia/Jayapura | 6 |
| ID | Sulawesi Barat | Asia/Jakarta | Asia/Makassar | 6 |
| MX | Baja California | America/Mexico_City | America/Tijuana | 6 |
| PF | Leeward Islands | Pacific/Gambier | Pacific/Tahiti | 6 |
| PG | Chimbu | Pacific/Bougainville | Pacific/Port_Moresby | 6 |
| ID | Gorontalo | Asia/Jakarta | Asia/Makassar | 5 |
| ID | Papua Barat Daya | Asia/Jakarta | Asia/Jayapura | 5 |
| PF | Austral Islands | Pacific/Gambier | Pacific/Tahiti | 5 |
| PG | Enga | Pacific/Bougainville | Pacific/Port_Moresby | 5 |
| PG | Madang | Pacific/Bougainville | Pacific/Port_Moresby | 5 |
| RU | Chukotka | Europe/Moscow | Asia/Anadyr | 5 |
| RU | Yamalo-Nenets | Europe/Moscow | Asia/Yekaterinburg | 5 |
| CA | Saskatchewan | America/Toronto | America/Regina | 4 |
| ID | Kalimantan Utara | Asia/Jakarta | Asia/Makassar | 4 |
| ID | Nusa Tenggara Barat | Asia/Jakarta | Asia/Makassar | 4 |
| ID | Papua Barat | Asia/Jakarta | Asia/Jayapura | 4 |
| ID | Papua Selatan | Asia/Jakarta | Asia/Jayapura | 4 |
| MX | Baja California Sur | America/Mexico_City | America/Mazatlan | 4 |
| MX | Quintana Roo | America/Mexico_City | America/Cancun | 4 |
| PG | Central | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| PG | Milne Bay | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| PG | Sandaun | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| PG | Western Highlands | Pacific/Bougainville | Pacific/Port_Moresby | 4 |
| RU | Kaliningrad | Europe/Moscow | Europe/Kaliningrad | 4 |
| RU | Khanty-Mansi | Europe/Moscow | Asia/Yekaterinburg | 4 |
| BR | Amazonas | America/Sao_Paulo | America/Eirunepe | 3 |
| CA | Manitoba | America/Toronto | America/Winnipeg | 3 |
| MX | Nayarit, Bahía de Banderas (3 filed under Jalisco) | America/Mazatlan | America/Bahia_Banderas | 6 |
| MN | Zavkhan, Govi-Altai | Asia/Hovd | Asia/Ulaanbaatar | 2 |
| BR | Amazonas (Lábrea) | America/Sao_Paulo | America/Manaus | 1 |
| GL | Avannaata (Qaanaaq) | America/Danmarkshavn | America/Nuuk | 1 |
| PG | Hela | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| PG | Jiwaka | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| PG | Southern Highlands | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| PG | Western | Pacific/Bougainville | Pacific/Port_Moresby | 3 |
| ID | Bali | Asia/Jakarta | Asia/Makassar | 2 |
| MN | Khovd | Asia/Choibalsan | Asia/Hovd | 2 |
| PG | East New Britain | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | Gulf | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | New Ireland | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | Oro | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| PG | West New Britain | Pacific/Bougainville | Pacific/Port_Moresby | 2 |
| BR | Roraima | America/Sao_Paulo | America/Boa_Vista | 1 |
| CA | British Columbia | America/Toronto | America/Dawson_Creek | 1 |
| CA | British Columbia | America/Toronto | America/Edmonton | 1 |
| CD | Lualaba | Africa/Kinshasa | Africa/Lubumbashi | 1 |
| FM | Kosrae | Pacific/Chuuk | Pacific/Kosrae | 1 |
| PF | Marquesas Islands | Pacific/Gambier | Pacific/Marquesas | 1 |
| PG | Manus | Pacific/Bougainville | Pacific/Port_Moresby | 1 |
| PG | Port Moresby | Pacific/Bougainville | Pacific/Port_Moresby | 1 |

### Not changed
- **Uncertain:** Sakha's cities in the Verkhoyansk, Oymyakon and Kolyma areas (three zones).
- **Amazonas** follows IANA's east/west geography, the Tabatinga–Porto Acre line of Decree 2,784/1913 and Law
  12,876/2013 (the 1913 regulation puts both endpoints in the eastern zone): Itamarati, Tabatinga and Lábrea take
  `America/Manaus`. A 2019 Ministry of Education (ENEM) notice groups 13 Amazonas municipalities with Acre's time,
  including Boca do Acre and Jutaí, which IANA explicitly places in the east; that conflict is recorded, not resolved.
- **Multi-zone by design:** US states split between zones (Tennessee, Kentucky, Indiana, Florida, Texas, the Dakotas,
  Nebraska, Kansas, Idaho, Arizona's Navajo Nation) and Mexico's US-border strip (Coahuila, Nuevo León, Tamaulipas,
  Chihuahua).
- **Political:** Xinjiang (state `Asia/Urumqi`, cities `Asia/Shanghai`) and Crimea (state `Europe/Kiev`, cities
  `Europe/Simferopol`).
- **Same offset, different name** (Magadan on `Asia/Sakhalin`, Kirov, Volgograd, Cyprus's `Asia/Famagusta`,
  Uzbekistan's `Asia/Samarkand`, Palestine's Gaza/Hebron, Mongolia's `Asia/Choibalsan`) is not an error in time.

### Independent review
Round 1 was reviewed: all 30 states correct (the 27 Russian mappings checked against Russian law and tzdata) and 360
of 1,069 cities checked by OpenStreetMap, all correct. Round 2 (from that review's findings) was reviewed in full (all 459 new cities with OpenStreetMap): 455 correct;
the 2 wrong and 2 uncertain cities and two Mongolian aimags were corrected as described above. A second (Codex)
review found the three Bahía de Banderas records filed under Jalisco given Mexico City's zone (their municipality
has its own, `America/Bahia_Banderas`) and Lábrea left on São Paulo time; both are fixed, with three more Bahía de
Banderas records, Qaanaaq and the two Mongolian aimags' cities.

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/states/states.json` — `timezone` on 95 states
- `contributions/cities/*.json` (13 countries) — `timezone` on 1,535 cities
