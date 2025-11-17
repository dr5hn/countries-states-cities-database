# Slovenia Missing Urban Municipality Fix - Velenje

## Issue Reference
**Title:** [Data]: Slovenia urban municipality missing  
**Problem:** Slovenia was missing 1 urban municipality out of the 12 urban municipalities listed in ISO 3166-2:SI standard

## Executive Summary
Successfully added the missing Velenje urban municipality to Slovenia's administrative divisions, bringing the total from 11 to 12 urban municipalities, matching the ISO 3166-2:SI standard.

## Country Addressed
- **Country:** Slovenia (SI)
- **ISO Code:** SI
- **Country ID:** 201

## Changes Made

### Urban Municipality Addition
**Added Urban Municipality:**
- **Name:** Velenje
- **Official Name:** Mestna občina Velenje (Urban Municipality of Velenje)
- **ISO 3166-2 Code:** SI-133
- **ISO2 Code:** 133
- **State ID:** 5698
- **Type:** urban municipality
- **Coordinates:** 46.36666667°N, 15.13333333°E
- **Timezone:** Europe/Ljubljana
- **WikiData ID:** Q3441849

### City Added
Added the main city of Velenje:

**Velenje** - Municipal seat
- **ID:** 157163
- **State ID:** 5698
- **Coordinates:** 46.36250000°N, 15.11444444°E
- **Timezone:** Europe/Ljubljana
- **WikiData ID:** Q15928
- **Native Name:** Velenje
- **German Name:** Wöllan (historical)

## Before/After Counts

### States (Municipalities)
- **Before:** 211 total (200 municipalities + 11 urban municipalities)
- **After:** 212 total (200 municipalities + 12 urban municipalities)
- **Change:** +1 urban municipality (Velenje)

### Cities
- **Before:** 311 Slovenian cities
- **After:** 312 Slovenian cities
- **Change:** +1 city (Velenje)

## Validation Steps and Results

### 1. Verified Slovenia Municipality Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'SI';
# Result: 211

# After fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'SI';
# Result: 212
```

### 2. Verified Urban Municipalities Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM states 
       WHERE country_code = 'SI' AND type = 'urban municipality';
# Result: 11

# After fix
mysql> SELECT COUNT(*) FROM states 
       WHERE country_code = 'SI' AND type = 'urban municipality';
# Result: 12
```

### 3. Verified Velenje Details
```bash
mysql> SELECT id, name, iso3166_2, iso2, type FROM states 
       WHERE country_code = 'SI' AND name = 'Velenje';
# Result:
# id: 5698
# name: Velenje
# iso3166_2: SI-133
# iso2: 133
# type: urban municipality
```

### 4. Verified All 12 Urban Municipalities
```bash
mysql> SELECT name, iso2 FROM states 
       WHERE country_code = 'SI' AND type = 'urban municipality' 
       ORDER BY name;
# Results (all 12):
# 1. Celje (011)
# 2. Koper (050)
# 3. Kranj (052)
# 4. Krško (054)
# 5. Ljubljana (061)
# 6. Maribor (070)
# 7. Murska Sobota (080)
# 8. Nova Gorica (084)
# 9. Novo Mesto (085)
# 10. Ptuj (096)
# 11. Slovenj Gradec (112)
# 12. Velenje (133) ✓ NEW
```

### 5. Verified Velenje City
```bash
mysql> SELECT id, name, state_id FROM cities 
       WHERE country_code = 'SI' AND name = 'Velenje';
# Result:
# id: 157163
# name: Velenje
# state_id: 5698
```

### 6. JSON File Validation
```bash
# States JSON
python3 -c "
import json
with open('contributions/states/states.json') as f:
    states = json.load(f)
si = [s for s in states if s['country_code'] == 'SI']
urban = [s for s in si if s['type'] == 'urban municipality']
print(f'Slovenia municipalities: {len(si)}')
print(f'Urban municipalities: {len(urban)}')
velenje = [s for s in si if s['name'] == 'Velenje']
print(f'Velenje found: {len(velenje) > 0}')
"
# Output:
# Slovenia municipalities: 212
# Urban municipalities: 12
# Velenje found: True

# Cities JSON
python3 -c "
import json
with open('contributions/cities/SI.json') as f:
    cities = json.load(f)
print(f'Slovenia cities: {len(cities)}')
velenje = [c for c in cities if c['state_id'] == 5698]
print(f'Velenje cities: {len(velenje)}')
"
# Output:
# Slovenia cities: 312
# Velenje cities: 1
```

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5698,
  "name": "Velenje",
  "country_id": 201,
  "country_code": "SI",
  "fips_code": "133",
  "iso2": "133",
  "iso3166_2": "SI-133",
  "type": "urban municipality",
  "level": null,
  "parent_id": null,
  "native": "Velenje",
  "latitude": "46.36666667",
  "longitude": "15.13333333",
  "timezone": "Europe/Ljubljana",
  "translations": {
    "ar": "فيلينيه",
    "de": "Velenje",
    "es": "Velenje",
    "fa": "ولنیه",
    "fr": "Velenje",
    "hr": "Velenje",
    "it": "Velenje",
    "ja": "ヴェレニエ",
    "ko": "벨레네",
    "nl": "Velenje (stad)",
    "pl": "Velenje",
    "pt": "Velenje",
    "pt-BR": "Velenje",
    "ru": "Веленье",
    "tr": "Velenje",
    "uk": "Веленє",
    "zh-CN": "韋萊涅",
    "br": "Velenje"
  },
  "created_at": "2025-11-17T04:15:15",
  "updated_at": "2025-11-17T04:15:15",
  "flag": 1,
  "wikiDataId": "Q3441849",
  "population": null
}
```

### City Entry (SI.json)
```json
{
  "id": 157163,
  "name": "Velenje",
  "state_id": 5698,
  "state_code": "133",
  "country_id": 201,
  "country_code": "SI",
  "latitude": "46.36250000",
  "longitude": "15.11444444",
  "native": "Velenje",
  "timezone": "Europe/Ljubljana",
  "translations": {
    "ar": "فيلينيه",
    "de": "Velenje",
    "es": "Velenje",
    "fa": "ولنیه",
    "fr": "Velenje",
    "hr": "Velenje",
    "it": "Velenje",
    "ja": "ヴェレニエ",
    "ko": "벨레네",
    "nl": "Velenje (stad)",
    "pl": "Velenje",
    "pt": "Velenje",
    "pt-BR": "Velenje",
    "ru": "Веленье",
    "tr": "Velenje",
    "uk": "Веленє",
    "zh-CN": "韋萊涅",
    "br": "Velenje"
  },
  "created_at": "2025-11-17T04:16:42",
  "updated_at": "2025-11-17T04:16:42",
  "flag": 1,
  "wikiDataId": "Q15928"
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added Velenje urban municipality entry
2. `contributions/cities/SI.json` - Added Velenje city

### Workflow Followed
1. Researched Velenje using Wikipedia API to gather accurate data
2. Fetched translations from Wikipedia language links (18 languages)
3. Added Velenje urban municipality to `contributions/states/states.json` (without ID)
4. Enriched with timezone (Europe/Ljubljana) and translations
5. Ran `import_json_to_mysql.py` to import municipality and auto-assign ID
6. Ran `sync_mysql_to_json.py` to sync ID back to JSON
7. Added Velenje city to `contributions/cities/SI.json` (without ID)
8. Ran `import_json_to_mysql.py` to import city and auto-assign ID
9. Ran `sync_mysql_to_json.py` to sync city ID back to JSON

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py --host 127.0.0.1 --user root --password root --database world

# Sync MySQL back to JSON (updates IDs)
python3 bin/scripts/sync/sync_mysql_to_json.py --host 127.0.0.1 --user root --password root --database world

# Verification queries
mysql -uroot -proot world -e "SELECT COUNT(*) FROM states WHERE country_code = 'SI';"
mysql -uroot -proot world -e "SELECT COUNT(*) FROM states WHERE country_code = 'SI' AND type = 'urban municipality';"
mysql -uroot -proot world -e "SELECT id, name, type FROM states WHERE country_code = 'SI' AND name = 'Velenje';"
```

## Data Enrichment

### Translation Coverage
All entries include translations in **18 languages**:
- Arabic (ar)
- German (de)
- Spanish (es)
- Persian (fa)
- French (fr)
- Croatian (hr)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Dutch (nl)
- Polish (pl)
- Portuguese (pt, pt-BR)
- Russian (ru)
- Turkish (tr)
- Ukrainian (uk)
- Chinese (zh-CN)
- Breton (br)

### WikiData Integration
- **Municipality WikiData ID:** Q3441849 - [Urban Municipality of Velenje](https://www.wikidata.org/wiki/Q3441849)
- **City WikiData ID:** Q15928 - [Velenje city](https://www.wikidata.org/wiki/Q15928)

### Timezone
Both entries properly configured with **Europe/Ljubljana** timezone, which is the standard timezone for Slovenia.

## Geographic Details

### Velenje Urban Municipality
- **Region:** Traditional Styria (Štajerska)
- **Statistical Region:** Savinja Statistical Region
- **Location:** Eastern Slovenia, Šalek Valley
- **Established:** 1994 (as urban municipality)
- **Area:** Bounded by Kamnik-Savinja Alps (west) and Pohorje Mountains (east)

### Velenje City
- **Rank:** 6th largest city in Slovenia
- **Historical Names:** Wöllan (German, historical); Titovo Velenje (1981-1990)
- **First Mentioned:** 1264 as "Weln"
- **Modern City Established:** September 20, 1959
- **Known For:** Coal mining (Velenje Coal Mine, opened 1875), Gorenje headquarters

## Additional Settlements in Velenje Municipality

According to Wikipedia, the Urban Municipality of Velenje includes 25 settlements in addition to the municipal seat:

1. Arnače
2. Bevče
3. Črnova
4. Hrastovec
5. Janškovo Selo
6. Kavče
7. Laze
8. Lipje
9. Lopatnik
10. Lopatnik pri Velenju
11. Ložnica
12. Paka pri Velenju
13. Paški Kozjak
14. Pirešica
15. Plešivec
16. Podgorje
17. Podkraj pri Velenju
18. Prelska
19. Šenbric
20. Silova
21. Škale
22. Škalske Cirkovce
23. Šmartinske Cirkovce
24. Vinska Gora

Note: These smaller settlements have not been added to the database in this fix, focusing on the main city only.

## References
- **ISO 3166-2:SI Standard:** https://www.iso.org/obp/ui#iso:code:3166:SI
- **Wikipedia - Municipalities of Slovenia:** https://en.wikipedia.org/wiki/Municipalities_of_Slovenia
- **Wikipedia - Urban Municipality of Velenje:** https://en.wikipedia.org/wiki/Urban_Municipality_of_Velenje
- **Wikipedia - Velenje (city):** https://en.wikipedia.org/wiki/Velenje
- **WikiData - Urban Municipality:** https://www.wikidata.org/wiki/Q3441849
- **WikiData - Velenje City:** https://www.wikidata.org/wiki/Q15928

## Compliance
✅ Matches ISO 3166-2:SI standard (12 urban municipalities)  
✅ Includes official native names in Slovene  
✅ All entries have proper WikiData IDs  
✅ Follows existing data structure and formatting  
✅ Includes municipal seat  
✅ Proper timezone (Europe/Ljubljana) assigned  
✅ Coordinates verified from Wikipedia  
✅ Comprehensive translations (18 languages)  
✅ Enriched with timezone and translations following best practices
