# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## States and cities on the wrong time zone

**30 states and 1,069 cities** get the right IANA time zone. They were found by comparing each
state's `timezone` with its own cities' zones and keeping the cases where the UTC offsets differ. #1649 checked each city
against its neighbours; that misses these, because here the wrong zone is shared by a whole state or by most of its
cities.

### States
Twenty-eight Russian federal subjects outside Moscow time were stored as `Europe/Moscow` (Sverdlovsk, Bashkortostan,
Perm, Novosibirsk, Primorsky, Khabarovsk…); each takes its legal zone (tzdata). Kiribati's Gilbert and Line Islands
were both `Pacific/Enderbury` (Phoenix Islands, UTC+13) and Micronesia's Kosrae `Pacific/Chuuk` (UTC+10).

| Country | State | Was | Now |
|---|---|---|---|
| FM | Kosrae | Pacific/Chuuk | Pacific/Kosrae |
| KI | Gilbert | Pacific/Enderbury | Pacific/Tarawa |
| KI | Line | Pacific/Enderbury | Pacific/Kiritimati |
| RU | Altai | Europe/Moscow | Asia/Barnaul |
| RU | Altai | Europe/Moscow | Asia/Barnaul |
| RU | Amur | Europe/Moscow | Asia/Yakutsk |
| RU | Astrakhan | Europe/Moscow | Europe/Astrakhan |
| RU | Bashkortostan | Europe/Moscow | Asia/Yekaterinburg |
| RU | Buryatia | Europe/Moscow | Asia/Irkutsk |
| RU | Chelyabinsk | Europe/Moscow | Asia/Yekaterinburg |
| RU | Jewish | Europe/Moscow | Asia/Vladivostok |
| RU | Kemerovo | Europe/Moscow | Asia/Novokuznetsk |
| RU | Khabarovsk | Europe/Moscow | Asia/Vladivostok |
| RU | Khakassia | Europe/Moscow | Asia/Krasnoyarsk |
| RU | Khanty-Mansi | Europe/Moscow | Asia/Yekaterinburg |
| RU | Kurgan | Europe/Moscow | Asia/Yekaterinburg |
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
| RU | Zabaykalsky | Europe/Moscow | Asia/Chita |

### Cities
In a state with one time zone, a city on another offset takes the state's zone: Western Australia's towns on Sydney
time, Mato Grosso, Mato Grosso do Sul and Rondônia on São Paulo time (all three are UTC−4), Sinaloa on Mexico City time,
Gorontalo on Jakarta time (it is on Makassar time, UTC+8), and the cities of Russian subjects stored on Moscow time. In
British Columbia, Amazonas and Sakha, which span several zones, a city takes the zone of most of its 5 nearest cities
in the state that are on one of the state's zones.

A city is changed only when at least 3 of its 5 nearest cities are filed in the same state, so a record whose point
lies in another state (a filing error, not a zone error) is not touched. That holds back 114 cities, mostly
near a regional border or in remote districts (Western Australia (AU) 15, Krasnoyarsk (RU) 9, Buryatia (RU) 8, Kamchatka (RU) 7, Novosibirsk (RU) 6, Mato Grosso do Sul (BR) 6…).

| Country | State | City zone was | Now | Cities |
|---|---|---|---|---:|
| BR | Mato Grosso | America/Sao_Paulo | America/Cuiaba | 119 |
| AU | Western Australia | Australia/Sydney | Australia/Perth | 106 |
| RU | Altai | Europe/Moscow | Asia/Barnaul | 76 |
| RU | Irkutsk | Europe/Moscow | Asia/Irkutsk | 50 |
| BR | Mato Grosso do Sul | America/Sao_Paulo | America/Campo_Grande | 50 |
| RU | Bashkortostan | Europe/Moscow | Asia/Yekaterinburg | 46 |
| RU | Zabaykalsky | Europe/Moscow | Asia/Chita | 45 |
| BR | Rondônia | America/Sao_Paulo | America/Porto_Velho | 44 |
| RU | Krasnoyarsk | Europe/Moscow | Asia/Krasnoyarsk | 43 |
| RU | Chelyabinsk | Europe/Moscow | Asia/Yekaterinburg | 38 |
| RU | Amur | Europe/Moscow | Asia/Yakutsk | 36 |
| RU | Primorsky | Europe/Moscow | Asia/Vladivostok | 32 |
| RU | Sverdlovsk | Europe/Moscow | Asia/Yekaterinburg | 25 |
| RU | Saratov | Europe/Moscow | Europe/Saratov | 24 |
| RU | Kemerovo | Europe/Moscow | Asia/Novokuznetsk | 23 |
| RU | Tyumen | Europe/Moscow | Asia/Yekaterinburg | 23 |
| RU | Novosibirsk | Europe/Moscow | Asia/Novosibirsk | 23 |
| RU | Orenburg | Europe/Moscow | Asia/Yekaterinburg | 19 |
| RU | Ulyanovsk | Europe/Moscow | Europe/Ulyanovsk | 19 |
| MX | Sinaloa | America/Mexico_City | America/Mazatlan | 18 |
| RU | Khabarovsk | Europe/Moscow | Asia/Vladivostok | 17 |
| RU | Omsk | Europe/Moscow | Asia/Omsk | 17 |
| RU | Perm | Europe/Moscow | Asia/Yekaterinburg | 16 |
| RU | Buryatia | Europe/Moscow | Asia/Irkutsk | 16 |
| RU | Samara | Europe/Moscow | Europe/Samara | 16 |
| RU | Kurgan | Europe/Moscow | Asia/Yekaterinburg | 14 |
| RU | Khakassia | Europe/Moscow | Asia/Krasnoyarsk | 13 |
| RU | Tomsk | Europe/Moscow | Asia/Tomsk | 13 |
| CA | British Columbia | America/Toronto | America/Vancouver | 13 |
| RU | Tuva | Europe/Moscow | Asia/Krasnoyarsk | 10 |
| RU | Jewish | Europe/Moscow | Asia/Vladivostok | 10 |
| RU | Sakha | Europe/Moscow | Asia/Yakutsk | 9 |
| RU | Kamchatka | Europe/Moscow | Asia/Kamchatka | 9 |
| RU | Astrakhan | Europe/Moscow | Europe/Astrakhan | 8 |
| RU | Udmurt | Europe/Moscow | Europe/Samara | 7 |
| BR | Amazonas | America/Sao_Paulo | America/Manaus | 7 |
| RU | Yamalo-Nenets | Europe/Moscow | Asia/Yekaterinburg | 4 |
| RU | Kaliningrad | Europe/Moscow | Europe/Kaliningrad | 4 |
| ID | Gorontalo | Asia/Jakarta | Asia/Makassar | 4 |
| RU | Khanty-Mansi | Europe/Moscow | Asia/Yekaterinburg | 3 |

### Not changed
- **Multi-zone states:** Tennessee, Kentucky, Indiana, Florida, Texas, the Dakotas, Nebraska and Idaho have cities on
  two zones, as they should; so does Tamaulipas (only its border strip follows US daylight saving).
- **Political:** Xinjiang (state `Asia/Urumqi`, cities `Asia/Shanghai`) and Crimea (state `Europe/Kiev`, cities
  `Europe/Simferopol`) are left as they are.
- **Same offset, different name** (e.g. Magadan cities on `Asia/Sakhalin`, Kirov, Volgograd) is not an error in time.

## Rollback
Revert the PR (squash commit). No `id`s change.

## Files Changed
- `contributions/states/states.json` — `timezone` on 30 states
- `contributions/cities/{AU,BR,CA,ID,MX,RU}.json` — `timezone` on 1,069 cities
