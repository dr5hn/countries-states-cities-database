# Changelog

## ⚠️ Notable: Italy city→province remap (PRs #1395, #1397, #1399 — issue #1349)

In April 2026 all 9,947 Italian cities were re-parented from the 20 Italian *region*-level entities (Tuscany, Lombardy, Sicily, etc.) to their correct ISO 3166-2:IT *province*-level entity (Roma → `RM`, Milan → `MI`, Agrigento → `AG`, Bolzano → `BZ`, etc.).

This is the correct administrative model — Italian cities formally belong to provinces / metropolitan cities / autonomous provinces, not to the higher-level regions — and it fixes the long-standing bug where province-level queries (e.g. cities of `IT/AG`) returned empty arrays.

**Behavior change consumers must be aware of:**

- Querying cities by **region**-level `state_code` (`82` Sicily, `25` Lombardy, `52` Tuscany, etc.) now returns `[]`. Region-level rows still exist in `states.json`, but they no longer have any cities directly attached.
- To get all cities of a region, traverse the hierarchy: pull `states.json` rows where `parent_id == <region_id>` (provinces / metropolitan cities of that region), then pull cities whose `state_id` is in that set. The `parent_id` and `level` fields on `states.json` were already correct prior to this change — no schema work required.

**Companion cleanups:**
- `#1397` restored 1,378 corrupted `native` fields on Italian cities (machine-translation artefacts like `Pero` → `Ma`).
- `#1399` dropped 6 duplicate pairs flagged by the remap (Pozzaglio + Pozzaglio ed Uniti, Torino + Turin, Naples + Napoli, etc.); 9,947 → 9,941 IT cities.

Two additional manual consolidations remain open for maintainer signoff: **Sermide e Felonica** (MN) and **Corteolona e Genzone** (PV).

---

## 2026-04
- **2026-04-25** - PR [#1414](https://github.com/dr5hn/countries-states-cities-database/pull/1414): Updated countries (by @dr5hn)
- **2026-04-25** - PR [#1404](https://github.com/dr5hn/countries-states-cities-database/pull/1404): Updated cities, Updated states, Updated countries (CA, PY) (by @github-actions[bot])
- **2026-04-25** - PR [#1391](https://github.com/dr5hn/countries-states-cities-database/pull/1391): Updated countries (by @dr5hn)
- **2026-04-25** - PR [#1390](https://github.com/dr5hn/countries-states-cities-database/pull/1390): Updated states (by @dr5hn)
- **2026-04-25** - PR [#1389](https://github.com/dr5hn/countries-states-cities-database/pull/1389): Updated states (by @Yi-pixel)
- **2026-04-25** - PR [#1388](https://github.com/dr5hn/countries-states-cities-database/pull/1388): Updated cities (CA) (by @dr5hn)
- **2026-04-25** - PR [#1387](https://github.com/dr5hn/countries-states-cities-database/pull/1387): Updated states (by @dr5hn)
- **2026-04-25** - PR [#1386](https://github.com/dr5hn/countries-states-cities-database/pull/1386): Updated states (by @dr5hn)
- **2026-04-25** - PR [#1382](https://github.com/dr5hn/countries-states-cities-database/pull/1382): Updated cities, Updated states (CN) (by @Yi-pixel)
- **2026-04-25** - PR [#1380](https://github.com/dr5hn/countries-states-cities-database/pull/1380): Updated cities (PY) (by @juliomuhlbauer)
- **2026-04-25** - PR [#1381](https://github.com/dr5hn/countries-states-cities-database/pull/1381): Updated cities (PY) (by @juliomuhlbauer)
- **2026-04-25** - PR [#1383](https://github.com/dr5hn/countries-states-cities-database/pull/1383): Updated states (by @mrodal)

## 2026-03
- **2026-03-28** - PR [#1372](https://github.com/dr5hn/countries-states-cities-database/pull/1372): Updated cities (EG, MY, NG, PH, SA) (by @github-actions[bot])
- **2026-03-28** - PR [#1371](https://github.com/dr5hn/countries-states-cities-database/pull/1371): Updated cities (MY) (by @dr5hn)
- **2026-03-28** - PR [#1370](https://github.com/dr5hn/countries-states-cities-database/pull/1370): Updated cities (EG) (by @dr5hn)
- **2026-03-28** - PR [#1369](https://github.com/dr5hn/countries-states-cities-database/pull/1369): Updated cities (NG) (by @dr5hn)
- **2026-03-28** - PR [#1368](https://github.com/dr5hn/countries-states-cities-database/pull/1368): Updated cities (SA) (by @dr5hn)
- **2026-03-28** - PR [#1367](https://github.com/dr5hn/countries-states-cities-database/pull/1367): Updated cities (PH) (by @dr5hn)
- **2026-03-28** - PR [#1366](https://github.com/dr5hn/countries-states-cities-database/pull/1366): Updated cities (SA) (by @dr5hn)
- **2026-03-28** - PR [#1319](https://github.com/dr5hn/countries-states-cities-database/pull/1319): Updated cities (IT) (by @LodiAleardo)
- **2026-03-28** - PR [#1365](https://github.com/dr5hn/countries-states-cities-database/pull/1365): Updated cities (SA, US) (by @github-actions[bot])
- **2026-03-27** - PR [#1359](https://github.com/dr5hn/countries-states-cities-database/pull/1359): Updated cities (IN) (by @Copilot)
- **2026-03-26** - PR [#1343](https://github.com/dr5hn/countries-states-cities-database/pull/1343): Updated cities (SA) (by @JyothsnaMS)
- **2026-03-26** - PR [#1333](https://github.com/dr5hn/countries-states-cities-database/pull/1333): Updated states, Updated countries (by @Copilot)
- **2026-03-26** - PR [#1347](https://github.com/dr5hn/countries-states-cities-database/pull/1347): Updated cities (US) (by @krismach)
- **2026-03-26** - PR [#1341](https://github.com/dr5hn/countries-states-cities-database/pull/1341): Updated cities (SA) (by @milank96)
- **2026-03-26** - PR [#1356](https://github.com/dr5hn/countries-states-cities-database/pull/1356): Updated countries (by @anilkunwar421)

All notable data changes to the Countries States Cities Database will be documented in this file.
This changelog is automatically updated when PRs are merged.

