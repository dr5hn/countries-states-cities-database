# Fix Summary: Data-correctness audit of cities

## Issue Reference
**Original Issue:** [#1643](https://github.com/dr5hn/countries-states-cities-database/issues/1643) — repo-wide audit of
`contributions/` for wrong coordinates, wrong states, timezones, duplicates and regions stored as cities.

Each finding is verified against an independent source before any change. Fixes land in small PRs, one section each.

## Cities with the wrong clock time

### How they were found
1. **Country check.** Every city's timezone is one the IANA zone table (`zone.tab`) lists for its country, allowing
   for backward-compatible alias names — except four: three defensible edge cases (an Antarctic station and
   Tromelin under the French Southern Territories, Nouméa under France) and *Walpole Island*, Ontario, which used
   the US zone `America/Detroit`.
2. **Neighbour check** in countries with several zones: 157 cities whose timezone differs from all ten nearest
   same-country cities, which agree with each other. 95 of them only differ in the zone's *name* (Sydney vs
   Melbourne, Mérida vs Mexico City — same clock time) and are left alone. 48 have a different **UTC offset** in
   January or July. Two of those are in Mato Grosso do Sul, where `America/Campo_Grande` is right and the
   neighbours are across the state line; they are left alone. Crimea (Kyiv vs Simferopol) is a political choice
   and is excluded.
3. **State check.** For every remaining city, the proposed zone is also the majority zone of the other cities in
   its own state (47 of 47).

### Fix
**47 cities** take their state's zone. Only `timezone` changes.

| Country | State | Records | Was | Now | Cities |
|---|---|---:|---|---|---|
| AU | WA | 17 | `Australia/Sydney` | `Australia/Perth` | Albany, Armadale, Bayswater, Capel, Coolgardie, Dardanup, Gosnells, Kalamunda, Kwinana, Malaga, Muchea, Munster, Murray, Serpentine-Jarrahdale, Stoneville, Subiaco, Swan |
| MX | SIN | 8 | `America/Mexico_City` | `America/Mazatlan` | Alfonso G. Calderón Velarde, El Dorado, Elota, Mazatlán, Navolato, Oso Viejo, Sinaloa, Villa Juárez |
| MX | BCN | 3 | `America/Mexico_City` | `America/Tijuana` | Lázaro Cárdenas, Mexicali, Tijuana |
| RU | SVE | 3 | `Europe/Moscow` | `Asia/Yekaterinburg` | Revda, Tugulym, Yekaterinburg |
| CA | AB | 2 | `America/Toronto` | `America/Edmonton` | Fort Saskatchewan, Millet |
| CA | BC | 2 | `America/Toronto` | `America/Vancouver` | Salt Spring Island, White Rock |
| CA | MB | 2 | `America/Toronto` | `America/Winnipeg` | De Salaberry, West St. Paul |
| MX | SON | 2 | `America/Mexico_City` | `America/Hermosillo` | Campo Sesenta, Sinahuiza |
| CA | ON | 1 | `America/Detroit` | `America/Toronto` | Walpole Island |
| ID | NB | 1 | `Asia/Jakarta` | `Asia/Makassar` | Lombok Utara |
| KI | G | 1 | `Pacific/Enderbury` | `Pacific/Tarawa` | Maiana |
| MX | ROO | 1 | `America/Mexico_City` | `America/Cancun` | Othón P. Blanco |
| RU | IRK | 1 | `Europe/Moscow` | `Asia/Irkutsk` | Tulun |
| RU | KEM | 1 | `Europe/Moscow` | `Asia/Novokuznetsk` | Gur’yevsk |
| RU | NVS | 1 | `Europe/Moscow` | `Asia/Novosibirsk` | Iskitimskiy Rayon |
| RU | SAM | 1 | `Europe/Moscow` | `Europe/Samara` | Bogatyr’ |

## Rollback
Revert the commit. No `id`s change.

## Files Changed
- `contributions/cities/{AU,CA,ID,KI,MX,RU}.json` — `timezone` on 47 records
