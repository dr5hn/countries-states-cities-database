# Sierra Leone Missing Province Fix - North Western Province

## Issue Reference
**Title:** [Data]: Sierra Leone province missing  
**Problem:** Sierra Leone was missing 1 province out of the 4 provinces and 1 area listed in ISO 3166-2:SL standard

## Executive Summary
Successfully added the missing North Western Province to Sierra Leone's administrative divisions, bringing the total from 4 to 5 administrative divisions (4 provinces + 1 area), matching the ISO 3166-2:SL standard. The province was created in 2017 from the Northern Province and consists of three districts: Kambia, Port Loko, and Karene.

## Country Addressed
- **Country:** Sierra Leone (SL)
- **ISO Code:** SL
- **Country ID:** 198

## Changes Made

### Province Addition
**Added Province:**
- **Name:** North Western
- **Official Name:** North West Province / North Western Province
- **ISO 3166-2 Code:** SL-NW
- **ISO2 Code:** NW
- **Province ID:** 5697
- **Type:** province
- **Coordinates:** 8.76666667°N, 12.78750000°W (Port Loko as center)
- **Timezone:** Africa/Freetown
- **WikiData ID:** Q43371075
- **Translations:** 7 languages (de, es, fr, ja, pt, ru, zh-CN)
- **Created:** 2017 (split from Northern Province)

### Cities Added
Added 1 new city - the provincial capital:

1. **Port Loko** - Provincial capital
   - ID: 157163
   - Coordinates: 8.76666667°N, 12.78750000°W
   - WikiData: Q1635196
   - Translations: 10 languages

### Cities Reassigned
Reassigned 5 cities from Northern Province (SL-N, state_id=911) to North Western Province (SL-NW, state_id=5697):

1. **Kambia** - District capital
   - Coordinates: 9.12504°N, 12.91816°W
   - WikiData: Q1722889
   - Translations: 19 languages

2. **Kamakwie** - District capital (Karene District)
   - Coordinates: 9.49689°N, 12.24061°W
   - WikiData: Q6355344
   - Translations: 19 languages

3. **Lunsar**
   - Coordinates: 8.68439°N, 12.53499°W
   - WikiData: Q995392
   - Translations: 19 languages

4. **Pepel**
   - Coordinates: 8.58611°N, 13.05444°W
   - WikiData: Q3466506
   - Translations: 19 languages

5. **Rokupr**
   - Coordinates: 8.67121°N, 12.38497°W
   - WikiData: Q927464
   - Translations: 19 languages

## Before/After Counts

### Provinces (States)
- **Before:** 4 administrative divisions (3 provinces + 1 area)
  - Northern, Southern, Eastern, Western
- **After:** 5 administrative divisions (4 provinces + 1 area)
  - Northern, Southern, Eastern, Western, **North Western**
- **Change:** +1 province (North Western)

### Cities by Province
**North Western Province (NEW):**
- **Total:** 6 cities
- Port Loko (capital), Kambia, Kamakwie, Lunsar, Pepel, Rokupr

**Northern Province:**
- **Before:** 30 cities
- **After:** 25 cities
- **Change:** -5 cities (reassigned to North Western)

**Total Sierra Leone Cities:**
- **Before:** 90 cities
- **After:** 91 cities
- **Change:** +1 city (Port Loko added)

## Validation Steps and Results

### 1. Verified Sierra Leone Province Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'SL';
# Result: 4

# After fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'SL';
# Result: 5
```

### 2. Verified North Western Province Details
```bash
mysql> SELECT id, name, iso3166_2, iso2 FROM states 
       WHERE country_code = 'SL' AND name = 'North Western';
# Result:
# id: 5697
# name: North Western
# iso3166_2: SL-NW
# iso2: NW
```

### 3. Verified Sierra Leone Cities Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'SL';
# Result: 90

# After fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'SL';
# Result: 91
```

### 4. Verified North Western Cities
```bash
mysql> SELECT COUNT(*) FROM cities WHERE state_id = 5697;
# Result: 6

mysql> SELECT name FROM cities WHERE state_id = 5697 ORDER BY name;
# Result:
# Kamakwie
# Kambia
# Lunsar
# Pepel
# Port Loko
# Rokupr
```

### 5. JSON File Validation
```bash
# States JSON
python3 -c "
import json
with open('contributions/states/states.json') as f:
    states = json.load(f)
sl = [s for s in states if s['country_code'] == 'SL']
print(f'Sierra Leone states: {len(sl)}')
nw = [s for s in sl if 'north western' in s['name'].lower()]
print(f'North Western found: {len(nw) > 0}')
"
# Output:
# Sierra Leone states: 5
# North Western found: True

# Cities JSON
python3 -c "
import json
with open('contributions/cities/SL.json') as f:
    cities = json.load(f)
print(f'Sierra Leone cities: {len(cities)}')
nw = [c for c in cities if c['state_id'] == 5697]
print(f'North Western cities: {len(nw)}')
"
# Output:
# Sierra Leone cities: 91
# North Western cities: 6
```

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5697,
  "name": "North Western",
  "country_id": 198,
  "country_code": "SL",
  "fips_code": null,
  "iso2": "NW",
  "iso3166_2": "SL-NW",
  "type": "province",
  "level": null,
  "parent_id": null,
  "native": "North Western",
  "latitude": "8.76666667",
  "longitude": "-12.78750000",
  "timezone": "Africa/Freetown",
  "translations": {
    "de": "North West Province",
    "es": "Provincia del Noroeste",
    "fr": "Province du Nord-Ouest",
    "ja": "北西部州",
    "pt": "Província do Noroeste",
    "ru": "Северо-Западная провинция",
    "zh-CN": "西北省"
  },
  "created_at": "2025-11-17T03:57:58",
  "updated_at": "2025-11-17T04:01:43",
  "flag": 1,
  "wikiDataId": "Q43371075",
  "population": null
}
```

### Sample City Entry (SL.json)
```json
{
  "id": 157163,
  "name": "Port Loko",
  "state_id": 5697,
  "state_code": "NW",
  "country_id": 198,
  "country_code": "SL",
  "latitude": "8.76666667",
  "longitude": "-12.78750000",
  "native": "Port Loko",
  "timezone": "Africa/Freetown",
  "translations": {
    "de": "Port Loko",
    "es": "Port Loko",
    "fr": "Port Loko",
    "it": "Port Loko",
    "ja": "ポート・ロコ",
    "nl": "Port Loko (stad)",
    "pl": "Port Loko",
    "pt": "Port Loko",
    "ru": "Порт-Локо",
    "zh-CN": "洛科港"
  },
  "created_at": "2025-11-17T03:59:50",
  "updated_at": "2025-11-17T04:00:45",
  "flag": 1,
  "wikiDataId": "Q1635196"
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added North Western province entry
2. `contributions/cities/SL.json` - Added Port Loko city, reassigned 5 cities

### Workflow Followed
1. Added North Western province to `contributions/states/states.json` (without ID)
2. Ran `import_json_to_mysql.py` to import province and auto-assign ID (5697)
3. Ran `sync_mysql_to_json.py` to sync ID back to JSON
4. Added Port Loko city and reassigned 5 cities in MySQL
5. Added translations from Wikipedia for state and city
6. Added WikiData IDs (Q43371075 for state, Q1635196 for Port Loko)
7. Ran `sync_mysql_to_json.py` to sync all changes back to JSON

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py \
  --host localhost --user root --password root --database world

# Add Port Loko and reassign cities
mysql -uroot -proot world -e "
  INSERT INTO cities (name, state_id, state_code, country_id, country_code, 
    latitude, longitude, native, timezone, translations, wikiDataId, 
    created_at, updated_at, flag)
  VALUES ('Port Loko', 5697, 'NW', 198, 'SL', '8.76666667', '-12.78750000', 
    'Port Loko', 'Africa/Freetown', '{}', NULL, NOW(), NOW(), 1);
  
  UPDATE cities SET state_id = 5697, state_code = 'NW' 
  WHERE country_code = 'SL' 
  AND name IN ('Kambia', 'Kamakwie', 'Lunsar', 'Pepel', 'Rokupr');
"

# Add translations
mysql -uroot -proot world -e "
  UPDATE cities SET translations = JSON_OBJECT(
    'de', 'Port Loko', 'es', 'Port Loko', 'fr', 'Port Loko',
    'it', 'Port Loko', 'ja', 'ポート・ロコ', 'nl', 'Port Loko (stad)',
    'pl', 'Port Loko', 'pt', 'Port Loko', 'ru', 'Порт-Локо',
    'zh-CN', '洛科港'
  )
  WHERE name = 'Port Loko' AND country_code = 'SL';
  
  UPDATE states SET translations = JSON_OBJECT(
    'de', 'North West Province', 'es', 'Provincia del Noroeste',
    'fr', 'Province du Nord-Ouest', 'ja', '北西部州',
    'pt', 'Província do Noroeste', 'ru', 'Северо-Западная провинция',
    'zh-CN', '西北省'
  )
  WHERE name = 'North Western' AND country_code = 'SL';
"

# Add WikiData IDs
mysql -uroot -proot world -e "
  UPDATE cities SET wikiDataId = 'Q1635196' 
  WHERE name = 'Port Loko' AND country_code = 'SL';
  
  UPDATE states SET wikiDataId = 'Q43371075' 
  WHERE name = 'North Western' AND country_code = 'SL';
"

# Sync MySQL back to JSON (updates IDs, translations, WikiData)
python3 bin/scripts/sync/sync_mysql_to_json.py \
  --host localhost --user root --password root --database world

# Verification queries
mysql -uroot -proot world -e "
  SELECT COUNT(*) FROM states WHERE country_code = 'SL';
  SELECT COUNT(*) FROM cities WHERE country_code = 'SL';
  SELECT COUNT(*) FROM cities WHERE state_id = 5697;
"
```

## Historical Context

The North Western Province was created in **2017** as a new administrative division by splitting from the Northern Province. This change reflected Sierra Leone's administrative restructuring following the country's 2017 constitutional review.

The province consists of three districts:
1. **Kambia District** (capital: Kambia)
2. **Port Loko District** (capital: Port Loko)
3. **Karene District** (capital: Kamakwie)

Port Loko serves as the provincial capital and is strategically important as it's located on major transportation routes.

## References
- **ISO 3166-2:SL Standard:** https://www.iso.org/obp/ui#iso:code:3166:SL
- **Wikipedia - North West Province:** https://en.wikipedia.org/wiki/North_West_Province,_Sierra_Leone
- **Wikipedia - Subdivisions of Sierra Leone:** https://en.wikipedia.org/wiki/Subdivisions_of_Sierra_Leone
- **WikiData - North Western Province:** https://www.wikidata.org/wiki/Q43371075
- **WikiData - Port Loko:** https://www.wikidata.org/wiki/Q1635196

## Compliance
✅ Matches ISO 3166-2:SL standard (4 provinces + 1 area)  
✅ All entries have proper WikiData IDs  
✅ Includes official native names  
✅ Follows existing data structure and formatting  
✅ Includes provincial capital and major cities  
✅ Proper timezone (Africa/Freetown) assigned  
✅ Coordinates verified from Wikipedia  
✅ Translations from Wikipedia in 7-19 languages  
✅ Cities correctly reassigned from Northern to North Western Province
