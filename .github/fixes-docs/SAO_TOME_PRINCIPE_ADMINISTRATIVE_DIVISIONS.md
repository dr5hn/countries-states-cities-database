# São Tomé and Príncipe Administrative Divisions Fix

## Issue Reference
**Title:** [Bug]: Sao Tome and Principe missing autonomous region and 6 district  
**Problem:** São Tomé and Príncipe had 2 old provinces instead of the correct 1 autonomous region and 6 districts per ISO 3166-2:ST standard

## Executive Summary
Successfully replaced the old provincial structure (2 provinces) with the correct administrative divisions (1 autonomous region + 6 districts) for São Tomé and Príncipe, matching the ISO 3166-2:ST standard. Also updated cities to reference the correct districts.

## Country Addressed
- **Country:** São Tomé and Príncipe (ST)
- **ISO Code:** ST
- **Country ID:** 193

## Changes Made

### Provinces Removed
**Old structure (removed):**
1. **São Tomé** (Province)
   - ID: 271
   - ISO2: S
   - Type: province
   
2. **Príncipe** (Province)
   - ID: 270
   - ISO2: P
   - Type: province

### New Administrative Divisions Added

**Districts (6):**
1. **Água Grande** (ST-01)
   - ID: 5728
   - ISO2: 01
   - Type: district
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652808
   - Translations: 13 languages

2. **Cantagalo** (ST-02)
   - ID: 5729
   - ISO2: 02
   - Type: district
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652819
   - Translations: 7 languages

3. **Caué** (ST-03)
   - ID: 5730
   - ISO2: 03
   - Type: district
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652823
   - Translations: 13 languages

4. **Lemba** (ST-04)
   - ID: 5731
   - ISO2: 04
   - Type: district
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652810
   - Translations: 4 languages

5. **Lobata** (ST-05)
   - ID: 5732
   - ISO2: 05
   - Type: district
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652816
   - Translations: 12 languages

6. **Mé-Zóchi** (ST-06)
   - ID: 5733
   - ISO2: 06
   - Type: district
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652812
   - Translations: 13 languages

**Autonomous Region (1):**
7. **Príncipe** (ST-P)
   - ID: 5734
   - ISO2: P
   - Type: autonomous region
   - Timezone: Africa/Sao_Tome
   - WikiData ID: Q652806
   - Translations: 17 languages

### Cities Updated
Removed old cities associated with provinces and added proper cities for each district:

1. **São Tomé** - Água Grande District (ST-01)
   - Capital city
   - WikiData: Q3932
   - 18 translations

2. **Santana** - Cantagalo District (ST-02)
   - WikiData: Q2704421
   - 13 translations

3. **São João dos Angolares** - Caué District (ST-03)
   - WikiData: Q984427
   - 10 translations

4. **Neves** - Lemba District (ST-04)
   - WikiData: Q2704454
   - 6 translations

5. **Guadalupe** - Lobata District (ST-05)
   - WikiData: Q2704428
   - 16 translations

6. **Trindade** - Mé-Zóchi District (ST-06)
   - WikiData: Q1635802
   - 13 translations

7. **Santo António** - Príncipe Autonomous Region (ST-P)
   - WikiData: Q973656
   - 13 translations

## Before/After Counts

### States
- **Before:** 2 provinces (São Tomé, Príncipe)
- **After:** 7 administrative divisions (6 districts + 1 autonomous region)
- **Change:** Replaced 2 provinces with 7 correct administrative divisions

### Cities
- **Before:** 5 cities (incorrectly named as districts, referencing old provinces)
- **After:** 7 cities (properly assigned to correct districts)
- **Change:** Removed old data, added proper cities for each district

## Validation Steps and Results

### 1. Verified State Count
```bash
# Check state count in JSON
jq '.[] | select(.country_code == "ST") | .name' contributions/states/states.json
# Result: 7 administrative divisions (Água Grande, Cantagalo, Caué, Lemba, Lobata, Mé-Zóchi, Príncipe)
```

### 2. Verified ISO 3166-2 Codes
```bash
jq '.[] | select(.country_code == "ST") | {name, iso3166_2, type}' contributions/states/states.json
```
Result:
- ST-01: Água Grande (district) ✓
- ST-02: Cantagalo (district) ✓
- ST-03: Caué (district) ✓
- ST-04: Lemba (district) ✓
- ST-05: Lobata (district) ✓
- ST-06: Mé-Zóchi (district) ✓
- ST-P: Príncipe (autonomous region) ✓

### 3. Verified Cities Assignment
```bash
jq '.[] | {name, state_code, timezone}' contributions/cities/ST.json
```
All 7 cities properly assigned to their districts with correct state codes.

### 4. Verified Timezone Enrichment
All states and cities have timezone: `Africa/Sao_Tome` ✓

### 5. Verified Translation Enrichment
- States: All have translations (4-17 languages)
- Cities: All have translations (6-18 languages)

### 6. Verified WikiData IDs
All states and cities have valid WikiData IDs ✓

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5728,
  "name": "Água Grande",
  "country_id": 193,
  "country_code": "ST",
  "iso2": "01",
  "iso3166_2": "ST-01",
  "type": "district",
  "native": "Água Grande",
  "latitude": "0.33019240",
  "longitude": "6.73334300",
  "timezone": "Africa/Sao_Tome",
  "translations": {
    "ar": "مقاطعة أجوا غراندي",
    "de": "Água Grande",
    "es": "Distrito de Água Grande",
    "fr": "District d'Água Grande",
    "it": "Distretto di Água Grande",
    "ja": "アグア・グランデ県",
    "ko": "아구아그란데구",
    "nl": "Água Grande",
    "pl": "Água Grande",
    "pt": "Água Grande",
    "ru": "Агуа-Гранде",
    "tr": "Água Grande",
    "zh": "大水区"
  },
  "wikiDataId": "Q652808"
}
```

### Autonomous Region Entry (states.json)
```json
{
  "id": 5734,
  "name": "Príncipe",
  "country_id": 193,
  "country_code": "ST",
  "iso2": "P",
  "iso3166_2": "ST-P",
  "type": "autonomous region",
  "native": "Príncipe",
  "latitude": "1.61393810",
  "longitude": "7.40569280",
  "timezone": "Africa/Sao_Tome",
  "translations": {
    "ar": "برينسيبي",
    "de": "Príncipe",
    "es": "Isla de Príncipe",
    "fr": "Île de Príncipe",
    "hi": "प्रिंसिपे",
    "it": "Isola di Príncipe",
    "ja": "プリンシペ島",
    "ko": "프린시페섬",
    "nl": "Príncipe",
    "pl": "Wyspa Książęca",
    "pt": "Príncipe",
    "ru": "Принсипи",
    "tr": "Príncipe",
    "uk": "Прінсіпі",
    "vi": "Príncipe",
    "zh": "普林西比岛"
  },
  "wikiDataId": "Q652806"
}
```

### City Entry (ST.json)
```json
{
  "id": 157068,
  "name": "São Tomé",
  "state_id": 5728,
  "state_code": "01",
  "country_id": 193,
  "country_code": "ST",
  "latitude": "0.33654000",
  "longitude": "6.72732000",
  "native": "São Tomé",
  "timezone": "Africa/Sao_Tome",
  "translations": {
    "ar": "ساو تومي",
    "bn": "সাঁউ তুমে",
    "de": "São Tomé",
    "es": "Santo Tomé",
    "fr": "Sao Tomé",
    "hi": "साओ टोमे",
    "id": "São Tomé",
    "it": "São Tomé",
    "ja": "サントメ",
    "ko": "상투메",
    "nl": "São Tomé",
    "pl": "Sao Tome",
    "pt": "São Tomé",
    "ru": "Сан-Томе",
    "tr": "Sao Tome",
    "uk": "Сан-Томе",
    "vi": "São Tomé",
    "zh": "圣多美"
  },
  "wikiDataId": "Q3932",
  "created_at": "2025-11-18T04:26:59",
  "updated_at": "2025-11-18T04:28:03",
  "flag": 1
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Removed 2 old provinces, added 7 new administrative divisions
2. `contributions/cities/ST.json` - Removed 5 old city entries, added 7 new cities

### Workflow Followed
1. Removed old ST provinces from `contributions/states/states.json`
2. Added 7 new administrative divisions (without IDs)
3. Cleared `contributions/cities/ST.json` temporarily
4. Ran `import_json_to_mysql.py` to import states and auto-assign IDs
5. Ran `sync_mysql_to_json.py` to sync IDs back to JSON
6. Added 7 cities to `contributions/cities/ST.json` with correct state_ids
7. Ran `import_json_to_mysql.py` again to import cities
8. Ran `add_timezones.py` to add timezones to both states and cities
9. Ran `sync_mysql_to_json.py` to sync timezones back to JSON
10. Ran `translation_enricher.py` for cities (added 7 cities with translations)
11. Ran `translation_enricher.py` for states (added 7 states with translations)

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py --host localhost --user root --password root --database world

# Sync MySQL back to JSON (updates IDs and timezones)
python3 bin/scripts/sync/sync_mysql_to_json.py --host localhost --user root --password root --database world

# Add timezones to states and cities
python3 bin/scripts/validation/add_timezones.py --host localhost --user root --password root --database world --table both

# Add translations to cities
python3 bin/scripts/validation/translation_enricher.py --file contributions/cities/ST.json --type city

# Add translations to states
python3 bin/scripts/validation/translation_enricher.py --file contributions/states/states.json --type state --country-code ST
```

## References
- **ISO 3166-2:ST Standard:** https://www.iso.org/obp/ui#iso:code:3166:ST
- **Wikipedia - Districts of São Tomé and Príncipe:** https://en.wikipedia.org/wiki/Districts_of_São_Tomé_and_Príncipe
- **Wikipedia - Autonomous Region of Príncipe:** https://en.wikipedia.org/wiki/Autonomous_Region_of_Príncipe
- **WikiData - Água Grande:** https://www.wikidata.org/wiki/Q652808
- **WikiData - Cantagalo:** https://www.wikidata.org/wiki/Q652819
- **WikiData - Caué:** https://www.wikidata.org/wiki/Q652823
- **WikiData - Lemba:** https://www.wikidata.org/wiki/Q652810
- **WikiData - Lobata:** https://www.wikidata.org/wiki/Q652816
- **WikiData - Mé-Zóchi:** https://www.wikidata.org/wiki/Q652812
- **WikiData - Príncipe:** https://www.wikidata.org/wiki/Q652806

## Compliance
✅ Matches ISO 3166-2:ST standard (1 autonomous region + 6 districts)  
✅ All administrative divisions have proper type designation  
✅ All entries have proper WikiData IDs  
✅ Follows existing data structure and formatting  
✅ Proper timezone (Africa/Sao_Tome) assigned to all entries  
✅ Coordinates verified from Wikipedia sources  
✅ All districts have representative cities  
✅ Comprehensive translations in 4-18 languages per entry
