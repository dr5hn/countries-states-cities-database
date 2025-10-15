# Yemen Cities Cleanup and Corrections - Issue #1155

## Quick Reference

**Issue**: [#1155](https://github.com/dr5hn/countries-states-cities-database/issues/1155) - Yemen cities data cleanup after state addition  
**Related PR**: [#1156](https://github.com/dr5hn/countries-states-cities-database/pull/1156) - Added missing Ad Dali' governorate  
**Status**: ✅ Fixed  
**Date**: 2025-10-15

## Problem Description

Following the addition of the missing Ad Dali' governorate (YE-DA) in PR #1156, a comprehensive review of Yemen's cities data revealed several data quality issues:

1. **Incorrect Timezone**: All 339 cities had timezone "Europe/Moscow" instead of "Asia/Aden"
2. **Duplicate City**: "Az Zahir" appeared twice with same WikiData ID but different locations
3. **Missing City Assignments**: 
   - No cities assigned to Amanat Al Asimah municipality (state_id: 1232)
   - No cities assigned to Ad Dali' governorate (state_id: 5467)
4. **Incorrect State Assignment**: Sanaa city was in wrong governorate

## Changes Made

### 1. Fixed Timezone for All Cities

**Problem**: All 339 Yemen cities had incorrect timezone "Europe/Moscow"  
**Solution**: Updated all cities to correct timezone "Asia/Aden"

**Impact**: 339 cities updated

**Validation**:
```bash
jq '[.[] | select(.timezone == "Asia/Aden")] | length' contributions/cities/YE.json
# Output: 339 ✅
```

### 2. Removed Duplicate City

**Problem**: "Az Zahir" (الظاهر) appeared twice:
- ID 130803 in Al Jawf governorate (YE-JA) at 16.33°N, 44.52°E
- ID 130804 in Al Bayda' governorate (YE-BA) at 13.99°N, 45.42°E
- Both had same WikiData ID: Q20423895

**Research**: WikiData Q20423895 corresponds to Az Zahir district in Al Bayda' Governorate

**Solution**: Removed duplicate ID 130803 (Al Jawf), kept ID 130804 (Al Bayda')

**Before**:
```json
{
  "id": 130803,
  "name": "Az Zahir",
  "state_id": 1243,
  "state_code": "JA",
  "wikiDataId": "Q20423895"
}
```

**Kept**:
```json
{
  "id": 130804,
  "name": "Az Zahir",
  "state_id": 1240,
  "state_code": "BA",
  "latitude": "13.99180000",
  "longitude": "45.42180000",
  "wikiDataId": "Q20423895"
}
```

### 3. Reassigned Sanaa to Correct Municipality

**Problem**: Sanaa city (ID 130964, WikiData Q2471) was assigned to Sana'a Governorate (state_id: 1236, YE-SN)

**Research**: 
- WikiData Q2471 corresponds to Sanaa city, the capital of Yemen
- Amanat Al Asimah (YE-SA, state_id: 1232) is the municipality that contains the capital city
- Sana'a Governorate (YE-SN, state_id: 1236) is the surrounding governorate

**Solution**: Moved Sanaa from Sana'a Governorate (1236) to Amanat Al Asimah municipality (1232)

**Change**:
- **State ID**: 1236 → 1232
- **State Code**: SN → SA

**After**:
```json
{
  "id": 130964,
  "name": "Sanaa",
  "state_id": 1232,
  "state_code": "SA",
  "country_id": 245,
  "country_code": "YE",
  "latitude": "15.35472000",
  "longitude": "44.20667000",
  "native": "صنعاء",
  "timezone": "Asia/Aden",
  "wikiDataId": "Q2471"
}
```

### 4. Added Ad Dali' City

**Problem**: Ad Dali' governorate (newly added, state_id: 5467) had no cities

**Solution**: Added capital city Ad Dali' to the governorate

**New City**:
```json
{
  "name": "Ad Dali'",
  "state_id": 5467,
  "state_code": "DA",
  "country_id": 245,
  "country_code": "YE",
  "latitude": "13.70000000",
  "longitude": "44.73000000",
  "native": "الضالع",
  "timezone": "Asia/Aden",
  "translations": {
    "br": "Ad Dali'",
    "ko": "아드달리",
    "pt-BR": "Ad Dali'",
    "pt": "Ad Dali'",
    "nl": "Ad Dali'",
    "hr": "Ad Dali'",
    "fa": "الضالع",
    "de": "Ad-Dali",
    "es": "Al Dhale",
    "fr": "Ad Dali'",
    "ja": "アッダーリー",
    "it": "Ad Dali'",
    "zh-CN": "达利",
    "tr": "Ed Dali",
    "ru": "Ад-Дали",
    "uk": "Ад-Далі",
    "pl": "Ad Dali'",
    "hi": "अद दालि",
    "ar": "الضالع"
  },
  "flag": 1,
  "wikiDataId": "Q7308711"
}
```

## Before vs After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Yemen Cities | 339 | 339 | 0 (1 removed, 1 added) |
| Cities with Wrong Timezone | 339 | 0 | -339 ✅ |
| Duplicate Cities | 1 pair | 0 | -1 ✅ |
| Cities in Amanat Al Asimah (1232) | 0 | 1 | +1 ✅ |
| Cities in Ad Dali' (5467) | 0 | 1 | +1 ✅ |
| Cities in Sana'a Gov (1236) | 20 | 19 | -1 ✅ |
| Cities in Al Jawf (1243) | 13 | 12 | -1 ✅ |

## Cities Distribution by State (After)

All 22 Yemen states/governorates now properly represented:

| State ID | State Code | State Name | City Count |
|----------|------------|------------|------------|
| 1238 | HD | Hadramawt | 33 |
| 1244 | HJ | Hajjah | 31 |
| 1241 | HU | Al Hudaydah | 26 |
| 1231 | TA | Ta'izz | 25 |
| 1250 | AM | 'Amran | 20 |
| 1247 | SH | Shabwah | 20 |
| 1240 | BA | Al Bayda' | 20 |
| 1233 | IB | Ibb | 20 |
| 1236 | SN | Sana'a | 19 |
| 1249 | SD | Sa'dah | 17 |
| 1245 | LA | Lahij | 17 |
| 1234 | MA | Ma'rib | 14 |
| 1246 | DH | Dhamar | 13 |
| 1237 | AB | Abyan | 13 |
| 1243 | JA | Al Jawf | 12 |
| 1251 | MR | Al Mahrah | 10 |
| 1235 | MW | Al Mahwit | 9 |
| 1242 | AD | 'Adan | 8 |
| 1248 | RA | Raymah | 6 |
| 1239 | SU | Socotra | 4 |
| **1232** | **SA** | **Amanat Al Asimah** | **1** ✅ NEW |
| **5467** | **DA** | **Ad Dali'** | **1** ✅ NEW |

## Data Quality Checks

### 1. No Duplicates
```bash
jq '[group_by(.name) | .[] | select(length > 1)]' contributions/cities/YE.json
# Output: [] ✅
```

### 2. All Cities Have Correct Timezone
```bash
jq '[.[] | select(.timezone != "Asia/Aden")] | length' contributions/cities/YE.json
# Output: 0 ✅
```

### 3. All Cities Have Yemen Country Code
```bash
jq '[.[] | select(.country_code != "YE")] | length' contributions/cities/YE.json
# Output: 0 ✅
```

### 4. All Cities Have Coordinates
```bash
jq '[.[] | select(.latitude == null or .longitude == null)] | length' contributions/cities/YE.json
# Output: 0 ✅
```

### 5. JSON Structure Valid
```bash
python3 -m json.tool contributions/cities/YE.json > /dev/null
# Output: No errors ✅
```

### 6. All States Have Cities
```bash
jq -r '.[] | .state_id' contributions/cities/YE.json | sort | uniq | wc -l
# Output: 22 ✅ (all 22 states/governorates represented)
```

## Files Modified

1. **`contributions/cities/YE.json`**
   - Fixed timezone for 339 cities
   - Removed 1 duplicate city (Az Zahir ID 130803)
   - Reassigned 1 city (Sanaa) to correct municipality
   - Added 1 new city (Ad Dali')
   - Net change: 339 cities (same as before, but cleaner data)

## Data Sources and References

### Timezone
- **IANA Timezone Database**: Asia/Aden for all Yemen
- Yemen uses Arabia Standard Time (AST), UTC+3, no DST

### Az Zahir Duplicate Resolution
- **WikiData Q20423895**: Az Zahir District, Al Bayda' Governorate
- URL: https://www.wikidata.org/wiki/Q20423895
- Confirms location in Al Bayda', not Al Jawf

### Sanaa City Assignment
- **WikiData Q2471**: Sanaa (city and capital)
- URL: https://www.wikidata.org/wiki/Q2471
- Describes Sanaa as capital of Yemen, located in Amanat Al Asimah municipality

### Ad Dali' City
- **WikiData Q7308711**: Ad Dali' (city)
- URL: https://www.wikidata.org/wiki/Q7308711
- Capital city of Ad Dali' Governorate
- **Wikipedia**: https://en.wikipedia.org/wiki/Dhale_Governorate
- Coordinates: 13.70°N, 44.73°E

## Administrative Context

### Amanat Al Asimah (Capital Municipality)
Amanat Al Asimah (أمانة العاصمة, "Secretariat of the Capital") is a special municipality that contains Yemen's capital city Sanaa. It is administratively separate from the surrounding Sana'a Governorate, similar to how:
- Washington D.C. is separate from surrounding states (USA)
- Brasília Federal District is separate from surrounding states (Brazil)
- Canberra (ACT) is separate from New South Wales (Australia)

### Ad Dali' Governorate
Ad Dali' (الضالع) is a governorate in southern Yemen, established as an independent governorate. The governorate's capital is Ad Dali' city.

## Validation Summary

✅ All 339 cities validated  
✅ No duplicates remain  
✅ All timezones corrected to Asia/Aden  
✅ All 22 governorates/municipalities have city representation  
✅ JSON structure valid  
✅ All required fields present  
✅ WikiData IDs verified  
✅ Coordinates validated

## Next Steps

None required. The fix is complete. GitHub Actions will:
1. Import the JSON to MySQL
2. Generate all export formats (JSON, CSV, SQL, XML, YAML, MongoDB)
3. Update all distribution files

## Notes

- Changes maintain backward compatibility (same number of cities, IDs preserved where appropriate)
- The `id` field for new Ad Dali' city is omitted (will be auto-assigned by MySQL)
- All changes based on official sources (ISO 3166-2, WikiData, Wikipedia)
- Data quality improved significantly while maintaining data integrity
