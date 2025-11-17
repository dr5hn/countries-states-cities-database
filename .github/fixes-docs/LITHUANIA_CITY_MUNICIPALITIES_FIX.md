# Lithuania City Municipalities Fix

## Issue Reference
**Issue:** [Data]: Lithuania missing city municipality
**Problem:** Lithuania was missing 7 city municipalities according to ISO 3166-2:LT standard. The database had 45 district municipalities instead of the correct structure: 7 city municipalities and 44 district municipalities.

## Countries/Regions Addressed
- Lithuania (LT)

## Changes Made

### Added 7 City Municipalities
According to ISO 3166-2:LT, Lithuania has a specific administrative structure with city municipalities (miestas) that are distinct from district municipalities.

**Converted 5 existing entries from district municipality to city municipality:**
1. LT-02 - Alytus → Alytaus miestas (state_id: 1605)
2. LT-15 - Kaunas → Kauno miestas (state_id: 1580)
3. LT-31 - Palanga → Palangos miestas (state_id: 1588)
4. LT-43 - Šiauliai → Šiaulių miestas (state_id: 1609)
5. LT-57 - Vilnius → Vilniaus miestas (state_id: 1606)

**Added 2 new city municipalities:**
6. LT-20 - Klaipėdos miestas (new entry)
7. LT-32 - Panevėžio miestas (new entry)

### Added 4 District Municipalities
To maintain the correct structure, added 4 district municipalities that exist separately from the city municipalities:

1. LT-03 - Alytus (district municipality)
2. LT-16 - Kaunas (district municipality)
3. LT-44 - Šiauliai (district municipality)
4. LT-58 - Vilnius (district municipality)

### Municipality Count Changes
**Before:**
- Counties: 10 ✓
- District municipalities: 45 ❌
- Municipalities: 9 ✓
- City municipalities: 0 ❌
- **Total: 64**

**After:**
- Counties: 10 ✓
- District municipalities: 44 ✓
- Municipalities: 9 ✓
- City municipalities: 7 ✓
- **Total: 70** (matches ISO 3166-2:LT)

### Fields Updated
For each converted/added entry:
- `type`: Changed to "city municipality" or added as "district municipality"
- `name`: Updated to include "miestas" suffix for city municipalities
- `native`: Updated to match new name
- `translations`: Added/preserved translations for all entries
- `wikiDataId`: Updated/added WikiData identifiers
- `timezone`: Added "Europe/Vilnius" for all entries
- `iso3166_2`: ISO codes properly assigned
- `parent_id`: Set to appropriate county ID

## Validation Steps

### 1. ISO Code Verification
```bash
python3 /tmp/check_iso_codes.py
```
**Expected result:** All 70 ISO codes present (10 counties + 7 city municipalities + 44 district municipalities + 9 municipalities)
**Actual result:** ✅ All 70 codes present, 0 missing, 0 extra

### 2. Municipality Type Count
```bash
jq '[.[] | select(.country_code == "LT")] | group_by(.type) | map({type: .[0].type, count: length})' contributions/states/states.json
```
**Expected result:**
- city municipality: 7
- county: 10
- district municipality: 44
- municipality: 9

**Actual result:** ✅ Matches expected

### 3. Verify City Municipality Structure
Each major city now has the proper administrative structure:
- **Alytus**: County (LT-AL), City Municipality (LT-02), District Municipality (LT-03)
- **Kaunas**: County (LT-KU), City Municipality (LT-15), District Municipality (LT-16)
- **Klaipėda**: County (LT-KL), City Municipality (LT-20), District Municipality (LT-21)
- **Panevėžys**: County (LT-PN), City Municipality (LT-32), District Municipality (LT-33)
- **Šiauliai**: County (LT-SA), City Municipality (LT-43), District Municipality (LT-44)
- **Vilnius**: County (LT-VL), City Municipality (LT-57), District Municipality (LT-58)
- **Palanga**: City Municipality (LT-31) only - no district municipality

## Data Samples

### City Municipality Entry Example
```json
{
  "id": 1605,
  "name": "Alytaus miestas",
  "country_id": 126,
  "country_code": "LT",
  "iso2": "02",
  "iso3166_2": "LT-02",
  "type": "city municipality",
  "level": 1,
  "parent_id": 1574,
  "native": "Alytaus miestas",
  "latitude": "54.39246770",
  "longitude": "24.10876070",
  "timezone": "Europe/Vilnius",
  "translations": {
    "br": "Alytus",
    "ko": "알리투스",
    "pt-BR": "Alytus",
    "de": "Alytus",
    "es": "Alytus",
    "fr": "Alytus",
    "ja": "アリートゥス",
    "ru": "Алитус",
    "ar": "أليتوس"
  },
  "wikiDataId": "Q928864"
}
```

### New City Municipality Entry
```json
{
  "name": "Klaipėdos miestas",
  "country_id": 126,
  "country_code": "LT",
  "iso2": "20",
  "iso3166_2": "LT-20",
  "type": "city municipality",
  "level": 1,
  "parent_id": 1600,
  "native": "Klaipėdos miestas",
  "latitude": "55.70329430",
  "longitude": "21.14427950",
  "timezone": "Europe/Vilnius",
  "translations": {
    "br": "Klaipėda",
    "ko": "클라이페다",
    "de": "Klaipėda",
    "ru": "Клайпеда",
    "ar": "كلايبيدا"
  },
  "wikiDataId": "Q928918"
}
```

### District Municipality Entry
```json
{
  "name": "Kaunas",
  "country_id": 126,
  "country_code": "LT",
  "iso2": "16",
  "iso3166_2": "LT-16",
  "type": "district municipality",
  "level": 1,
  "parent_id": 1556,
  "native": "Kaunas",
  "latitude": "54.89821390",
  "longitude": "23.90448170",
  "timezone": "Europe/Vilnius",
  "translations": {
    "br": "Kaunas",
    "ko": "카우나스",
    "de": "Kaunas",
    "ru": "Каунас",
    "ar": "كاوناس"
  },
  "wikiDataId": "Q928949"
}
```

## References
- **ISO 3166-2:LT:** https://www.iso.org/obp/ui#iso:code:3166:LT
- **Wikipedia - Lithuania:** https://en.wikipedia.org/wiki/Lithuania
- **Wikipedia - Municipalities of Lithuania:** https://en.wikipedia.org/wiki/Municipalities_of_Lithuania
- **WikiData - Alytus city municipality:** https://www.wikidata.org/wiki/Q928864
- **WikiData - Kaunas city municipality:** https://www.wikidata.org/wiki/Q928938
- **WikiData - Klaipėda city municipality:** https://www.wikidata.org/wiki/Q928918
- **WikiData - Palanga city municipality:** https://www.wikidata.org/wiki/Q3685410
- **WikiData - Panevėžys city municipality:** https://www.wikidata.org/wiki/Q928992
- **WikiData - Šiauliai city municipality:** https://www.wikidata.org/wiki/Q928995
- **WikiData - Vilnius city municipality:** https://www.wikidata.org/wiki/Q923117

## Impact
- **API changes:** 
  - 6 new state entries added (2 city municipalities + 4 district municipalities)
  - 5 existing entries changed type from "district municipality" to "city municipality"
  - Names updated for 5 entries to include "miestas" suffix
- **Breaking changes:** None - only additions and type corrections
- **Data quality improvements:**
  - ✅ Lithuania now complies with ISO 3166-2:LT standard
  - ✅ All 70 administrative divisions properly categorized
  - ✅ All entries have timezone information
  - ✅ All entries have translations
  - ✅ All entries have WikiData IDs
  - ✅ Proper parent-child relationships established

## Notes
- The distinction between "city municipality" (miestas) and "district municipality" is important in Lithuanian administrative structure
- City municipalities are urban cores with city status
- District municipalities are larger administrative areas that may include rural areas
- Some major cities (Alytus, Kaunas, Šiauliai, Vilnius) have BOTH a city municipality AND a district municipality with the same name but different ISO codes
- Palanga is unique - it only has a city municipality (LT-31) without a separate district municipality
- After MySQL import, city references may need to be updated to point to the correct city municipality IDs
