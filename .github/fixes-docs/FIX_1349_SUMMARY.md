# Italy Cities Remap to Provinces / Metropolitan Cities

## Issue Reference
- **GitHub Issue:** [#1349](https://github.com/dr5hn/countries-states-cities-database/issues/1349) — Italy data: cities reported as "totally wrong"
- **Predecessor:** `ITALY_MISSING_METROPOLITAN_CITIES_AND_AUTONOMOUS_PROVINCES.md` (added 13 metropolitan cities + 2 autonomous provinces, deferred the city remap)
- **Date:** 2026-04-25

## Executive Summary
Reassigned **9,828 of 9,947 Italian cities** from the 20 region-level entities to the correct ISO 3166-2 province-level entity (metropolitan city, province, free municipal consortium, autonomous province, or decentralized regional entity).

Before this fix, **0** cities were attached to any of the 14 metropolitan cities. The bulk of cities pointed at regions (Lombardy, Piedmont, Veneto, Tuscany, Lazio, etc.) instead of the more specific province below the region. After this fix:

| Administrative type | Cities |
|---------------------|-------:|
| Metropolitan city          | 1,682 |
| Province                   | 7,337 |
| Autonomous province        | 390   |
| Free municipal consortium  | 176   |
| Decentralized regional entity | 271 |
| Autonomous region (Aosta only) | 91 |
| **Total**                  | **9,947** |

## Mapping source

The authoritative mapping was the official ISTAT comune list:

- **Source:** `https://www.istat.it/storage/codici-unita-amministrative/Elenco-comuni-italiani.csv`
- **Snapshot bundled at:** `bin/scripts/fixes/data/istat-elenco-comuni-italiani.csv`
- **Licence:** ISTAT data is published under CC-BY 3.0 IT.
- **Records:** 7,896 comuni × 26 columns (regione, sigla automobilistica, codice catastale, NUTS codes, etc.).

The join key is **Sigla automobilistica** — the 2-letter province plate code (e.g. `RM` for Rome, `TO` for Turin, `BZ` for Bolzano). It maps 1:1 to our `state.iso2` for every province-level Italian entity.

| ISTAT sigle | Our DB | Notes |
|------------:|-------:|-------|
| 107 distinct sigle | 106 specific entities + 1 autonomous region (Aosta) | Aosta has no province-level entity, so `AO` cities map to the autonomous region (id=1716, iso2="23"). |

## Implementation

`bin/scripts/fixes/italy_remap_cities.py` performs the remap. Resolution order per city:

1. **Name match** (region-validated): the city's `name` is normalised (NFD-folded, lowercased, apostrophe-collapsed) and looked up in an index built from ISTAT's Italian + alternate-language denominations. A candidate is accepted only when its ISTAT region equals the city's current region (walked up via `parent_id` to a region/autonomous-region). This rejects spurious matches like 4 different "San Lorenzo" frazioni snapping to the only "San Lorenzo" comune in Calabria.
2. **English-name aliases**: a small dictionary handles English-only city names that have no ISTAT spelling (`Venice` → `Venezia`, `Florence` → `Firenze`, `Naples` → `Napoli`, `Turin` → `Torino`, `Milan` → `Milano`, `Genoa` → `Genova`, `Rome` → `Roma`, `Padua` → `Padova`, `Mantua` → `Mantova`, `Syracuse` → `Siracusa`).
3. **Conjunction-half match**: comuni with " e " / " ed " conjunctions register secondary keys for each side. This rescues e.g. `Lampedusa` (the city in our DB) → `Lampedusa e Linosa` (the comune in ISTAT).
4. **k-NN proximity vote** (frazioni / hamlets): for cities still unmapped, the script ranks all name-matched cities by haversine distance, takes the 5 nearest (capped at 25 km), and uses an inverse-distance weighted vote to choose a sigla. This is more robust at province borders than picking the single nearest neighbour — Mestre's nearest comune is in Treviso, but its 5-neighbour cluster is dominated by Venice frazioni.

## Counts

```
input              9947
name_unique        7373   exact ISTAT match in same region
name_region          13   multiple ISTAT matches, region tie-break
name_ambiguous       69   matches existed but in another region (rejected -> proximity)
name_conjunction     25   matched via "X e Y" half
no_match           2467   no ISTAT name (frazione / hamlet / historical name)

proximity_assigned 2512   resolved by 5-NN vote within 25 km
proximity_skipped     0   none rejected for being too far

changed            9828   state_id and/or state_code rewritten
unchanged           119   already pointed at the correct province (mostly RA, BT)
unmapped              0   every record reached a final assignment
```

A full structured report is at `bin/scripts/fixes/data/it_remap_report.json`.

## Spot-checks

| City | Before | After |
|------|--------|-------|
| Milan | state_id=1705 (Lombardy region) | state_id=5633 (Milan metropolitan city) |
| Rome  | state_id=1678 (Lazio region)    | state_id=5636 (Rome metropolitan city) |
| Florence | state_id=1664 (Tuscany region) | state_id=5630 (Florence metropolitan city) |
| Naples | state_id=1669 (Campania region) | state_id=5634 (Naples metropolitan city) |
| Venice | state_id=1753 (Veneto region) | state_id=5638 (Venice metropolitan city) |
| Trento | state_id=1725 (Trentino-South Tyrol) | state_id=5640 (Trentino autonomous province) |
| Aosta  | state_id=1716 (Aosta Valley region) | unchanged — no province-level entity for AO |
| Trieste | state_id=1756 (Friuli–Venezia Giulia region) | state_id=1763 (Trieste decentralized regional entity) |
| Siracusa | state_id=1709 (Sicily region) | state_id=1667 (Siracusa free municipal consortium) |

## Edge cases

### Native field is unreliable
Many `native` values in `IT.json` have been corrupted by past machine-translation runs (e.g. `"Pero" → native: "Ma"`, `"Postal" → native: "Postale"`). The script intentionally matches on `name`, not `native`. Fixing `native` is out of scope for this PR but should be tracked separately.

### Lampedusa coordinates
Lampedusa sits at lat 35.5°, south of `country-bounds.json`'s `IT.minLat = 36.65`. This is a pre-existing bounds-data gap, not caused by the remap; the south Italian island chain (Pelagie) genuinely lies south of the standard mainland bounding box.

### Frazioni at province borders
Approximately 30 frazioni near Venice (Mestre, Giudecca, Murano, Lido, Burano, Campalto, Tessera) live within ~10 km of comuni in Treviso province. The 5-NN vote correctly resolves all but **Tessera** (Venice's airport), which still maps to Treviso because its nearest cluster is mixed. This is acceptable but flagged for future refinement.

## Possible duplicates flagged for review (not deleted)

Eight pairs/groups currently mapped to the same comune. **No records were deleted** — these are listed for maintainer review:

| Sigla | Comune | Cities |
|-------|--------|--------|
| CR | Pozzaglio ed Uniti | "Pozzaglio", "Pozzaglio ed Uniti" |
| FI | Capraia e Limite | "Capraia e Limite", "Limite" |
| MN | Sermide e Felonica | "Sermide", "Felonica" |
| NA | Napoli | "Naples", "Napoli" |
| PV | Corteolona e Genzone | "Corteolona", "Genzone" |
| PV | Inverno e Monteleone | "Inverno", "Inverno e Monteleone" |
| SS | Trinità d'Agultu e Vignola | "Trinità d'Agultu", "Trinità d'Agultu e Vignola" |
| TO | Torino | "Torino", "Turin" |

Several of these are conjunction-merger artefacts: ISTAT's modern unified comune name vs. older entries for the constituents. The "Naples"/"Napoli" and "Torino"/"Turin" pairs are language duplicates.

## ISTAT vs our city count gap

ISTAT has 7,896 comuni; our DB has 9,947 cities. The ~2,050-record surplus consists of frazioni (sub-municipal hamlets), historical/merged comuni, and place names. These aren't comuni in their own right but are common in geocoding databases. The remap maps them to their parent comune's sigla via the proximity vote.

## Validation

Local equivalents of `.github/scripts/validate-*` were run after the rewrite:

- ✅ All 9,947 cities pass schema (required fields present, `country_code == "IT"`, `country_id == 107`).
- ✅ Every `state_id` resolves to an IT state in `states.json`.
- ✅ Every `state_code` equals the referenced state's `iso2`.
- ✅ All `wikiDataId` values match `^Q\d+$`.
- ✅ Coordinate bounding-box check: 9,946 / 9,947 within IT bounds (the one exception is Lampedusa, a pre-existing `country-bounds.json` gap).
- ✅ Same-name + ≤5km duplicate scan: 0 hits.
- ✅ JSON is parseable by `python3 -m json.tool`.

## Files Modified

- `contributions/cities/IT.json` — 9,828 records updated (only `state_id` and `state_code` fields).

## Files Added

- `bin/scripts/fixes/italy_remap_cities.py` — reproducible remap script (stdlib only).
- `bin/scripts/fixes/data/istat-elenco-comuni-italiani.csv` — bundled ISTAT snapshot.
- `bin/scripts/fixes/data/it_remap_report.json` — structured report from the run.

## Reproducibility

```bash
# Re-run from scratch (uses bundled CSV by default; --refresh-istat to refetch).
python3 bin/scripts/fixes/italy_remap_cities.py --report bin/scripts/fixes/data/it_remap_report.json
```

The script is idempotent: a second run on already-remapped data produces 0 changes.

## References

- ISO 3166-2:IT: https://www.iso.org/obp/ui#iso:code:3166:IT
- ISTAT Codici delle unità amministrative territoriali: https://www.istat.it/it/archivio/6789
- Wikipedia — Provinces of Italy: https://en.wikipedia.org/wiki/Provinces_of_Italy
- Wikipedia — Metropolitan cities of Italy: https://en.wikipedia.org/wiki/Metropolitan_cities_of_Italy
- Predecessor fix: `.github/fixes-docs/ITALY_MISSING_METROPOLITAN_CITIES_AND_AUTONOMOUS_PROVINCES.md`

---

## Follow-up: drop placeholder "Provincia ..." rows (2026-04-27)

The reporter on #1349 specifically called out "Provincia di Lucca don't have sense to exist". Those rows were not real comuni — they were **province-level placeholder cities** carried over from the pre-#1395 schema, when cities pointed at regions and a separate "Provincia di X" pseudo-city stood in for the province below the region. After the #1395 remap, every real comune resolves directly to its province via `state_id` / `state_code`, so the placeholders are a duplicate concept and have been removed.

### Selection

- **Range:** ids 59104–59190 inclusive (contiguous, no gaps).
- **Count:** 87 rows.
- **Names:** all start with `Provincia ` — covers the standard `Provincia di X` form plus a handful of variants (`Provincia autonoma di Trento`, `Provincia dell' Aquila`, `Provincia Verbano-Cusio-Ossola`).

### Counts

| | Before | After |
|---|--:|--:|
| `IT.json` city records | 9,947 | 9,860 |
| Rows starting with `Provincia ` | 87 | 0 |

(Note: the prompt's expected post-#1479 baseline of 9,941 was off by 6; the correct baseline at the time of this PR was 9,947, confirmed by `git log` and `jq '. \| length'`. Range arithmetic 59190 − 59104 + 1 = 87, not 88.)

### Implementation

`bin/scripts/fixes/italy_drop_provincia_placeholders.py` — defensive double-predicate filter (id range AND name prefix). Refuses to touch rows in the id range that don't match the name prefix (exit 2). Idempotent — second run is a no-op.

### Validation

- ✅ `jq '. | length'` → 9,860.
- ✅ `jq '[.[] | select(.name | startswith("Provincia "))] | length'` → 0.
- ✅ No `parent_id` references to the dropped id range.
- ✅ Neighbour ids 59103 and 59191 preserved.
- ✅ JSON parses cleanly via `python3 -m json.tool`.
- ✅ `normalize_json.py` reports "All records already have IDs and timestamps" — no other fields touched.

### Files

- Modified: `contributions/cities/IT.json` (87 rows removed).
- Added: `bin/scripts/fixes/italy_drop_provincia_placeholders.py`.

### Still open on #1349

Two dedup pairs from the eight flagged in the original remap remain to be merged. They are tracked separately and not closed by this PR.
