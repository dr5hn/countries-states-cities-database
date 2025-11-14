# Equatorial Guinea Missing Province Fix - Djibloho Province

## Issue Reference
**Title:** [Data]: Equatorial Guinea province missing  
**Problem:** Equatorial Guinea was missing 1 province out of the 10 administrative divisions listed in ISO 3166-2:GQ standard

## Executive Summary
Successfully added the missing Djibloho province to Equatorial Guinea's administrative divisions, bringing the total from 9 to 10 divisions (8 provinces + 2 regions), matching the ISO 3166-2:GQ standard. Also added 2 cities for the new province.

## Country Addressed
- **Country:** Equatorial Guinea (GQ)
- **ISO Code:** GQ
- **Country ID:** 67

## Changes Made

### Province Addition
**Added Province:**
- **Name:** Djibloho
- **Official Name:** Administrative City of Djibloho (Ciudad administrativa de Djibloho)
- **ISO 3166-2 Code:** GQ-DJ
- **ISO2 Code:** DJ
- **Province ID:** 5551
- **Coordinates:** 1.60°N, 10.80°E
- **Timezone:** Africa/Malabo
- **WikiData ID:** Q28814758
- **Type:** province
- **Established:** 2017 (carved out of Wele-Nzas province)

### Cities Added
Added 2 cities for Djibloho province:

1. **Ciudad de la Paz** (City of Peace) - Provincial capital
   - ID: 157084
   - Also known as: Oyala, Djibloho
   - Coordinates: 1.59°N, 10.82°E
   - WikiData: Q1140136
   - Note: Being built to replace Malabo as national capital

2. **Mengomeyén**
   - ID: 157085
   - Coordinates: 1.68°N, 10.90°E
   - Note: Near the new airport

## Before/After Counts

### Provinces and Regions (States)
- **Before:** 9 administrative divisions (7 provinces + 2 regions)
- **After:** 10 administrative divisions (8 provinces + 2 regions)
- **Change:** +1 province (Djibloho)

### Cities
- **Before:** 24 cities
- **After:** 26 cities
- **Change:** +2 cities (both in Djibloho province)

## Validation Steps and Results

### 1. Verified Equatorial Guinea Province Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'GQ';
# Result: 9

# After fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'GQ';
# Result: 10
```

### 2. Verified Province and Region Types
```bash
mysql> SELECT COUNT(*), type FROM states WHERE country_code = 'GQ' GROUP BY type;
# Result:
# 8 provinces
# 2 regions
```

### 3. Verified Djibloho Province Details
```bash
mysql> SELECT id, name, iso3166_2, iso2 FROM states 
       WHERE country_code = 'GQ' AND name = 'Djibloho';
# Result:
# id: 5551
# name: Djibloho
# iso3166_2: GQ-DJ
# iso2: DJ
```

### 4. Verified Equatorial Guinea Cities Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'GQ';
# Result: 24

# After fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'GQ';
# Result: 26
```

### 5. Verified Djibloho Cities
```bash
mysql> SELECT COUNT(*) FROM cities WHERE state_id = 5551;
# Result: 2
```

### 6. JSON File Validation
```bash
# States JSON
python3 -c "
import json
with open('contributions/states/states.json') as f:
    states = json.load(f)
gq = [s for s in states if s['country_code'] == 'GQ']
print(f'Equatorial Guinea states: {len(gq)}')
djibloho = [s for s in gq if 'djibloho' in s['name'].lower()]
print(f'Djibloho found: {len(djibloho) > 0}')
provinces = [s for s in gq if s['type'] == 'province']
regions = [s for s in gq if s['type'] == 'region']
print(f'Provinces: {len(provinces)}, Regions: {len(regions)}')
"
# Output:
# Equatorial Guinea states: 10
# Djibloho found: True
# Provinces: 8, Regions: 2

# Cities JSON
python3 -c "
import json
with open('contributions/cities/GQ.json') as f:
    cities = json.load(f)
print(f'Equatorial Guinea cities: {len(cities)}')
djibloho = [c for c in cities if c['state_id'] == 5551]
print(f'Djibloho cities: {len(djibloho)}')
"
# Output:
# Equatorial Guinea cities: 26
# Djibloho cities: 2
```

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5551,
  "name": "Djibloho",
  "country_id": 67,
  "country_code": "GQ",
  "fips_code": null,
  "iso2": "DJ",
  "iso3166_2": "GQ-DJ",
  "type": "province",
  "level": null,
  "parent_id": null,
  "native": "Djibloho",
  "latitude": "1.60000000",
  "longitude": "10.80000000",
  "timezone": "Africa/Malabo",
  "translations": {
    "zh": "吉布劳",
    "ko": "지블로호",
    "ja": "ジブロホ県",
    "pl": "Djibloho",
    "fr": "Djibloho",
    "zh-CN": "吉布劳省",
    "es": "Provincia de Djibloho",
    "de": "Djibloho",
    "fa": "دجیبلوهو",
    "ru": "Джиблохо",
    "el": "Ντζιμπλόχο"
  },
  "created_at": "2025-11-14T14:34:22",
  "updated_at": "2025-11-14T14:34:22",
  "flag": 1,
  "wikiDataId": "Q28814758",
  "population": null
}
```

### Sample City Entry (GQ.json)
```json
{
  "id": 157084,
  "name": "Ciudad de la Paz",
  "state_id": 5551,
  "state_code": "DJ",
  "country_id": 67,
  "country_code": "GQ",
  "latitude": "1.58888889",
  "longitude": "10.82250000",
  "native": "Ciudad de la Paz",
  "timezone": "Africa/Malabo",
  "translations": {
    "es": "Ciudad de la Paz",
    "fr": "Ciudad de la Paz",
    "de": "Ciudad de la Paz",
    "ja": "シウダー・デ・ラ・パス",
    "zh-CN": "和平城",
    "ru": "Сьюдад-де-ла-Пас",
    "ar": "سيوداد دي لا باز"
  },
  "created_at": "2025-11-14T14:39:31",
  "updated_at": "2025-11-14T14:39:31",
  "flag": 1,
  "wikiDataId": "Q1140136"
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added Djibloho province entry
2. `contributions/cities/GQ.json` - Added 2 cities for Djibloho province
3. `bin/db/schema.sql` - Updated via sync

### Workflow Followed
1. Added Djibloho province to `contributions/states/states.json` (without ID)
2. Ran `import_json_to_mysql.py` to import province and auto-assign ID
3. Ran `sync_mysql_to_json.py` to sync ID back to JSON
4. Inserted 2 cities for Djibloho directly to MySQL
5. Ran `sync_mysql_to_json.py` to sync city data back to JSON

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py --host localhost --user root --password root --database world

# Sync MySQL back to JSON (updates IDs)
python3 bin/scripts/sync/sync_mysql_to_json.py --host localhost --user root --password root --database world

# Verification queries
mysql -uroot -proot world -e "SELECT COUNT(*) FROM states WHERE country_code = 'GQ';"
mysql -uroot -proot world -e "SELECT COUNT(*) FROM cities WHERE country_code = 'GQ';"
mysql -uroot -proot world -e "SELECT COUNT(*) FROM cities WHERE state_id = 5551;"
```

## Complete List of Equatorial Guinea Administrative Divisions

### Provinces (8)
1. **Annobón** (GQ-AN) - Island province
2. **Bioko Norte** (GQ-BN) - Northern Bioko Island
3. **Bioko Sur** (GQ-BS) - Southern Bioko Island
4. **Centro Sur** (GQ-CS) - Central South mainland
5. **Djibloho** (GQ-DJ) - **NEW** - Future capital region
6. **Kié-Ntem** (GQ-KN) - Northern mainland
7. **Litoral** (GQ-LI) - Coastal mainland (includes Bata)
8. **Wele-Nzas** (GQ-WN) - Eastern mainland

### Regions (2)
1. **Insular** (GQ-I) - Island region (covers Bioko and Annobón)
2. **Río Muni** (GQ-C) - Mainland region

## References
- **ISO 3166-2:GQ Standard:** https://www.iso.org/obp/ui#iso:code:3166:GQ
- **Wikipedia - Equatorial Guinea:** https://en.wikipedia.org/wiki/Equatorial_Guinea
- **Wikipedia - Djibloho:** https://en.wikipedia.org/wiki/Djibloho
- **Wikipedia - Ciudad de la Paz:** https://en.wikipedia.org/wiki/Ciudad_de_la_Paz
- **WikiData - Djibloho Province:** https://www.wikidata.org/wiki/Q28814758
- **WikiData - Ciudad de la Paz:** https://www.wikidata.org/wiki/Q1140136

## Historical Context
Djibloho was formally established as a province in 2017, carved out of the Wele-Nzas province. The capital, Ciudad de la Paz (formerly known as Oyala), is being built to replace Malabo as Equatorial Guinea's national capital. The new city is located on the mainland (Río Muni), in contrast to Malabo which is on Bioko Island.

## Compliance
✅ Matches ISO 3166-2:GQ standard (8 provinces + 2 regions)  
✅ Includes official names in Spanish  
✅ All entries have proper WikiData IDs  
✅ Follows existing data structure and formatting  
✅ Includes provincial capital and major settlement  
✅ Proper timezone (Africa/Malabo) assigned  
✅ Coordinates verified from Wikipedia and official sources  
✅ Translations in multiple languages (10+ languages for province)
