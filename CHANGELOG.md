# Changelog

## v3.2 — 2026-04-27

Major data-correction release. Behaviour changes for FR/IT consumers — see notable callouts below.

**Highlights:**
- France mainland city remap region → department: 8,727 cities re-parented from 13 metropolitan regions to their correct INSEE department (#1352 PR-E, #1484). Allier (`03`), Manche (`50`), and 95 other departments now return their cities; querying by region code (`ARA`, `IDF`, `NOR`, …) now returns `[]`.
- France mainland: +455 missing communes added from data.gouv.fr (Cherbourg-en-Cotentin, Évry-Courcouronnes, Saint-Ouen-sur-Seine, …) automatically remapped to the correct department (#1352 PR-A, #1394).
- France overseas: 9 new state records + 31 city files for GF / BL / MF / PM / TF (#1352 PR-D, #1400).
- Italy cleanup: dropped 88 placeholder "Provincia di X" pseudo-cities (#1349, #1482) and merged two ISTAT-canonical comune dedup pairs — Sermide e Felonica (MN), Corteolona e Genzone (PV) (#1349, #1481).
- States `level` normalised across all FR + IT entities: `level=1` = region, `level=2` = department / province (#1489). Downstream consumers can now filter by `level` reliably.
- Postcodes: bulk imports for KH, VE, MG, MZ, MU, MT, BN, HU, CN, MM, LU and more, completing roughly 50 country-postcode datasets under #1039.
- Export pipeline: postcode export files (json/xml/yml/sqlite/sqlserver/csv) now gzip-compressed and routed to GitHub Releases; raw versions gitignored to keep the repo manageable (#1490).

---

## ⚠️ Notable: France city→department remap (PRs #1394, #1484 — issue #1352)

In April 2026 all 9,182 mainland French cities (8,727 existing + 455 newly added) were re-parented from the 13 ISO 3166-2:FR *region*-level entities (`ARA` Auvergne-Rhône-Alpes, `IDF` Île-de-France, `NOR` Normandie, etc.) to their correct INSEE *department*-level entity (`03` Allier, `13` Bouches-du-Rhône, `2A`/`2B` Corse, `75C` Paris, etc.).

This is the FR equivalent of the IT region→province remap shipped earlier in April. It fixes the long-standing bug where department-level queries (e.g. cities of `FR/03`) returned empty arrays despite both the country and department codes being valid.

**Behaviour change consumers must be aware of:**

- Querying cities by **region**-level `state_code` (`ARA`, `IDF`, `NOR`, `PDL`, `NAQ`, `BRE`, `OCC`, `GES`, `CVL`, `BFC`, `HDF`, `PAC`, `20R`) now returns `[]`. Region-level rows still exist in `states.json` but they no longer have any cities directly attached.
- To get all cities of a region, traverse the hierarchy: pull `states.json` rows where `parent_id == <region_id>` (departments of that region), then pull cities whose `state_id` is in that set.

**Companion changes:**
- `#1393` (PR-B) restored corrupted `native` field values on FR states (machine-translation artefacts like `Ain` → `Se faire`, `Aude` → `entendus`).
- `#1400` (PR-D) added the 5 missing FR-overseas city files (GF, BL, MF, PM, TF) plus their parent state records — modelled under each territory's own ISO 3166-1 country code, mirroring the existing MQ/GP/RE/YT/NC convention.
- `#1392` (PR-C) added `MULTI_LEVEL_TERRITORIES.md` documenting the dual-representation of overseas territories.
- `#1489` normalised the `level` field across FR + IT states so consumers can filter `level=1` (region) vs `level=2` (department/province).

---

## ⚠️ Notable: Italy city→province remap (PRs #1395, #1397, #1399 — issue #1349)

In April 2026 all 9,947 Italian cities were re-parented from the 20 Italian *region*-level entities (Tuscany, Lombardy, Sicily, etc.) to their correct ISO 3166-2:IT *province*-level entity (Roma → `RM`, Milan → `MI`, Agrigento → `AG`, Bolzano → `BZ`, etc.).

This is the correct administrative model — Italian cities formally belong to provinces / metropolitan cities / autonomous provinces, not to the higher-level regions — and it fixes the long-standing bug where province-level queries (e.g. cities of `IT/AG`) returned empty arrays.

**Behavior change consumers must be aware of:**

- Querying cities by **region**-level `state_code` (`82` Sicily, `25` Lombardy, `52` Tuscany, etc.) now returns `[]`. Region-level rows still exist in `states.json`, but they no longer have any cities directly attached.
- To get all cities of a region, traverse the hierarchy: pull `states.json` rows where `parent_id == <region_id>` (provinces / metropolitan cities of that region), then pull cities whose `state_id` is in that set. The `parent_id` and `level` fields on `states.json` were already correct prior to this change — no schema work required.

**Companion cleanups:**
- `#1397` restored 1,378 corrupted `native` fields on Italian cities (machine-translation artefacts like `Pero` → `Ma`).
- `#1399` dropped 6 duplicate pairs flagged by the remap (Pozzaglio + Pozzaglio ed Uniti, Torino + Turin, Naples + Napoli, etc.); 9,947 → 9,941 IT cities.

Two additional manual consolidations remain open for maintainer signoff: **Sermide e Felonica** (MN) and **Corteolona e Genzone** (PV). _(Resolved 2026-04-27 in #1481.)_

---

## 2026-04
- **2026-04-27** - PR [#1490](https://github.com/dr5hn/countries-states-cities-database/pull/1490): fix(export): gzip postcode files + gitignore raw versions (by @dr5hn)
- **2026-04-27** - PR [#1489](https://github.com/dr5hn/countries-states-cities-database/pull/1489): fix(FR/IT): normalise state.level field for region/department hierarchy (by @dr5hn)
- **2026-04-27** - PR [#1487](https://github.com/dr5hn/countries-states-cities-database/pull/1487): feat(postcodes/BN): import 547 Brunei Postal Services codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1486](https://github.com/dr5hn/countries-states-cities-database/pull/1486): feat(postcodes/HU): import 3,569 Magyar Posta codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1485](https://github.com/dr5hn/countries-states-cities-database/pull/1485): feat(postcodes/CN): import 22,656 China Post codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1484](https://github.com/dr5hn/countries-states-cities-database/pull/1484): feat(FR): remap mainland cities region→department (#1352 PR-E) (by @dr5hn)
- **2026-04-27** - PR [#1483](https://github.com/dr5hn/countries-states-cities-database/pull/1483): feat(postcodes/MM): import 17,331 Myanmar Post codes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1482](https://github.com/dr5hn/countries-states-cities-database/pull/1482): fix(IT): drop 88 placeholder Provincia rows (#1349 follow-up) (by @dr5hn)
- **2026-04-27** - PR [#1481](https://github.com/dr5hn/countries-states-cities-database/pull/1481): fix(IT): merge 2 dedup pairs flagged by #1395 remap (#1349 follow-up) (by @dr5hn)
- **2026-04-27** - PR [#1480](https://github.com/dr5hn/countries-states-cities-database/pull/1480): feat(postcodes/KH): bulk-import 1,640 Cambodia postcodes via Cambodia Post (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1478](https://github.com/dr5hn/countries-states-cities-database/pull/1478): feat(postcodes/VE): bulk-import 1,187 Venezuela postcodes via IPOSTEL (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1476](https://github.com/dr5hn/countries-states-cities-database/pull/1476): feat(postcodes/MG): bulk-import 111 Madagascar postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1474](https://github.com/dr5hn/countries-states-cities-database/pull/1474): feat(postcodes/MZ): bulk-import 161 Mozambique postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1473](https://github.com/dr5hn/countries-states-cities-database/pull/1473): feat(postcodes/MU): bulk-import 1,874 Mauritius postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1472](https://github.com/dr5hn/countries-states-cities-database/pull/1472): feat(postcodes/MT): bulk-import 26,593 Malta postcodes (#1039) (by @dr5hn)
- **2026-04-27** - PR [#1400](https://github.com/dr5hn/countries-states-cities-database/pull/1400): feat(FR-overseas): populate missing city files for GF, BL, MF, PM, TF (#1352 PR-D) (by @dr5hn)
- **2026-04-27** - PR [#1394](https://github.com/dr5hn/countries-states-cities-database/pull/1394): feat(FR): diff cities against data.gouv.fr, add missing metropolitan communes (#1352 PR-A) (by @dr5hn)
- **2026-04-27** - PR [#1393](https://github.com/dr5hn/countries-states-cities-database/pull/1393): feat(FR): polish department + region metadata vs data.gouv.fr (#1352 PR-B) (by @dr5hn)
- **2026-04-27** - PR [#1392](https://github.com/dr5hn/countries-states-cities-database/pull/1392): docs: multi-level territories policy (FR overseas, dual representation) (#1352 PR-C) (by @dr5hn)
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

