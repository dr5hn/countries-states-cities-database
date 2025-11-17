# Taiwan Missing Counties - Chiayi County and Hsinchu County

## Issue Reference
**GitHub Issue:** Taiwan county missing  
**Problem:** Taiwan was missing 2 counties according to ISO 3166-2:TW standard. The database had only 11 counties instead of 13.

## Countries/Regions Addressed
- Taiwan (TW)

## Changes Made

### Missing Counties Identified
According to ISO 3166-2:TW, Taiwan should have:
- 3 cities
- 6 special municipalities
- 13 counties

The database previously had:
- 3 cities ✓
- 6 special municipalities ✓
- 11 counties ✗ (missing 2)

### Missing Counties
1. **Chiayi County** (TW-CYQ) - Distinct from Chiayi City (TW-CYI)
2. **Hsinchu County** (TW-HSQ) - Distinct from Hsinchu City (TW-HSZ)

### 1. Added Chiayi County
**Before:** Did not exist (only Chiayi City existed)  
**After:** Added as separate county entry

```json
{
  "id": 5704,
  "name": "Chiayi County",
  "country_id": 216,
  "country_code": "TW",
  "fips_code": "03",
  "iso2": "CYQ",
  "iso3166_2": "TW-CYQ",
  "type": "county",
  "native": "嘉義縣",
  "latitude": "23.49620556",
  "longitude": "120.64187500",
  "timezone": "Asia/Taipei",
  "wikiDataId": "Q166977",
  "translations": {
    "ar": "مقاطعة شياي",
    "de": "Landkreis Chiayi",
    "es": "Condado de Chiayi",
    "fr": "Comté de Chiayi",
    "hi": "चियायी काउंटी",
    "id": "Kabupaten Chiayi",
    "it": "Contea di Chiayi",
    "ja": "嘉義県",
    "ko": "자이현",
    "nl": "Chiayi",
    "pl": "Powiat Chiayi",
    "pt": "Condado de Chiayi",
    "ru": "Цзяи",
    "tr": "Chiayi İlçesi",
    "uk": "Цзяї",
    "vi": "Huyện Gia Nghĩa"
  }
}
```

**Fields added:**
- Complete ISO codes (iso2: CYQ, iso3166_2: TW-CYQ)
- Timezone: Asia/Taipei
- WikiData ID: Q166977
- Native name: 嘉義縣
- Translations: 16 languages
- Coordinates from Wikipedia

### 2. Added Hsinchu County
**Before:** Did not exist (only Hsinchu City existed)  
**After:** Added as separate county entry

```json
{
  "id": 5705,
  "name": "Hsinchu County",
  "country_id": 216,
  "country_code": "TW",
  "fips_code": "03",
  "iso2": "HSQ",
  "iso3166_2": "TW-HSQ",
  "type": "county",
  "native": "新竹縣",
  "latitude": "24.83333333",
  "longitude": "121.01472222",
  "timezone": "Asia/Taipei",
  "wikiDataId": "Q74054",
  "translations": {
    "ar": "مقاطعة هسينشو",
    "de": "Landkreis Hsinchu",
    "es": "Condado de Hsinchu",
    "fr": "Comté de Hsinchu",
    "hi": "ज़िंचु काउंटी",
    "id": "Kabupaten Hsinchu",
    "it": "Contea di Hsinchu",
    "ja": "新竹県",
    "ko": "신주현",
    "nl": "Hsinchu",
    "pl": "Powiat Hsinchu",
    "pt": "Condado de Hsinchu",
    "ru": "Синьчжу",
    "tr": "Hsinchu İlçesi",
    "uk": "Сіньчжу",
    "vi": "Tân Trúc"
  }
}
```

**Fields added:**
- Complete ISO codes (iso2: HSQ, iso3166_2: TW-HSQ)
- Timezone: Asia/Taipei
- WikiData ID: Q74054
- Native name: 新竹縣
- Translations: 16 languages
- Coordinates from Wikipedia

### 3. Updated Existing Cities
Fixed incorrect state_id references for cities that were already in the database but pointing to the wrong parent (city instead of county):

- **Chiayi County city** (id: 109005): Updated state_id from 3408 (Chiayi City) to 5704 (Chiayi County)
- **Hsinchu city** (id: 109010): Updated state_id from 3417 (Hsinchu City) to 5705 (Hsinchu County)

### 4. Added New Cities

#### Chiayi County Cities (3 new)
1. **Budai** (布袋鎮)
   - ID: 109042
   - WikiData: Q715867
   - Coordinates: 23.36°N, 120.17°E

2. **Dalin** (大林鎮)
   - ID: 109043
   - WikiData: Q718381
   - Coordinates: 23.599°N, 120.47°E

3. **Minxiong** (民雄鄉)
   - ID: 109044
   - WikiData: Q713803
   - Coordinates: 23.550°N, 120.446°E

#### Hsinchu County Cities (2 new)
1. **Zhubei** (竹北市)
   - ID: 109045
   - WikiData: Q29624
   - Coordinates: 24.833°N, 121.012°E

2. **Hukou** (湖口鄉)
   - ID: 109046
   - WikiData: Q153830
   - Coordinates: 24.90°N, 121.05°E

All new cities include:
- Proper state_id references
- Native Chinese names
- Timezone (Asia/Taipei)
- WikiData IDs
- Basic translations (Chinese)

## Validation Steps

### 1. Verified ISO 3166-2:TW Standard
```bash
# Checked official ISO page
# https://www.iso.org/obp/ui#iso:code:3166:TW
# Confirmed TW-CYQ and TW-HSQ are official county codes
```
**Result:** ✅ Both counties confirmed in ISO standard

### 2. Wikipedia Validation
```bash
# Chiayi County
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Chiayi County" \
    --type state \
    --country TW

# Hsinchu County  
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Hsinchu County" \
    --type state \
    --country TW
```
**Result:** ✅ Both articles found with coordinates and WikiData IDs

### 3. Translation Enrichment
```bash
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code TW \
    --force-update
```
**Result:** ✅ 16 languages added for each county

### 4. State Count Verification
```bash
# Before: 20 Taiwan states
# After: 22 Taiwan states

cat contributions/states/states.json | jq '[.[] | select(.country_code == "TW")] | group_by(.type) | map({type: .[0].type, count: length})'
```
**Result:**
```json
[
  {"type": "city", "count": 3},
  {"type": "county", "count": 13},
  {"type": "special municipality", "count": 6}
]
```
✅ Matches ISO 3166-2:TW exactly

### 5. City Count Verification
```bash
# Taiwan cities before: 35
# Taiwan cities after: 40

# Chiayi County cities: 4
# Hsinchu County cities: 3
```
**Result:** ✅ All cities properly assigned to counties with correct state_ids

## Data Quality

### Complete Data Coverage
- ✅ All counties have ISO 3166-2 codes
- ✅ All counties have WikiData IDs
- ✅ All counties have timezones
- ✅ All counties have native names
- ✅ All counties have translations (16 languages)
- ✅ All counties have precise coordinates
- ✅ All cities have WikiData IDs
- ✅ All cities have correct parent county references

### Translation Coverage
Each county includes translations in:
- Arabic (ar)
- German (de)
- Spanish (es)
- French (fr)
- Hindi (hi)
- Indonesian (id)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Dutch (nl)
- Polish (pl)
- Portuguese (pt)
- Russian (ru)
- Turkish (tr)
- Ukrainian (uk)
- Vietnamese (vi)

## References

### Wikipedia Articles
- [Chiayi County](https://en.wikipedia.org/wiki/Chiayi_County) - English Wikipedia
- [Hsinchu County](https://en.wikipedia.org/wiki/Hsinchu_County) - English Wikipedia
- [Counties of Taiwan](https://en.wikipedia.org/wiki/Counties_of_Taiwan) - Overview

### WikiData
- [Q166977](https://www.wikidata.org/wiki/Q166977) - Chiayi County
- [Q74054](https://www.wikidata.org/wiki/Q74054) - Hsinchu County
- [Q715867](https://www.wikidata.org/wiki/Q715867) - Budai Township
- [Q718381](https://www.wikidata.org/wiki/Q718381) - Dalin Township
- [Q713803](https://www.wikidata.org/wiki/Q713803) - Minxiong Township
- [Q29624](https://www.wikidata.org/wiki/Q29624) - Zhubei City
- [Q153830](https://www.wikidata.org/wiki/Q153830) - Hukou Township

### Official Standards
- [ISO 3166-2:TW](https://www.iso.org/obp/ui#iso:code:3166:TW) - Official ISO subdivision codes for Taiwan

## Impact

### API Changes
- ✅ 2 new state entries (Chiayi County, Hsinchu County)
- ✅ 5 new city entries
- ✅ 2 updated city entries (corrected state_id references)

### Breaking Changes
- ⚠️ Applications filtering by state count may need updates (20 → 22 states)
- ⚠️ Cities previously under wrong state_id now corrected (may affect existing queries)

### Data Quality Improvements
- ✅ Taiwan now complies with ISO 3166-2:TW standard
- ✅ Complete administrative division coverage
- ✅ Proper separation of cities vs counties (Chiayi City ≠ Chiayi County)
- ✅ All entries enriched with translations and metadata
- ✅ WikiData integration for all new entries

## Before/After Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Taiwan States (Total) | 20 | 22 | +2 |
| Counties | 11 | 13 | +2 |
| Cities (administrative) | 3 | 3 | 0 |
| Special Municipalities | 6 | 6 | 0 |
| Taiwan Cities (data entries) | 35 | 40 | +5 |
| Chiayi County cities | 1* | 4 | +3 |
| Hsinchu County cities | 1* | 3 | +2 |

\* Previously incorrectly assigned to city parent instead of county parent

## Conclusion

This fix brings the Taiwan administrative divisions into full compliance with the ISO 3166-2:TW standard by adding the two missing counties (Chiayi County and Hsinchu County) that were distinct from their namesake cities. All new entries include complete metadata, translations, and proper WikiData integration following the repository's best practices.
