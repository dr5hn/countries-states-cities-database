# France Missing Overseas Collectivity - New Caledonia

## Issue Reference
**Title:** [Bug]: France missing overseas collectivity with special status  
**Problem:** France was missing Nouvelle-Calédonie (New Caledonia), an overseas collectivity with special status, from its administrative divisions

## Executive Summary
Successfully added the missing Nouvelle-Calédonie (New Caledonia) overseas collectivity with special status to France's administrative divisions, bringing the total from 123 to 124 states/territories, improving compliance with ISO 3166-2:FR standard.

## Country Addressed
- **Country:** France (FR)
- **ISO Code:** FR
- **Country ID:** 75

## Changes Made

### State/Territory Addition
**Added State:**
- **Name:** Nouvelle-Calédonie
- **English Name:** New Caledonia
- **ISO 3166-2 Code:** FR-NC
- **ISO2 Code:** NC
- **State ID:** 5538
- **Type:** overseas collectivity with special status
- **Coordinates:** -21.25°S, 165.30°E
- **Timezone:** Pacific/Noumea (UTC+11)
- **WikiData ID:** Q33788
- **Translations:** 18 languages (ar, bn, de, es, fr, hi, id, it, ja, ko, nl, pl, pt, ru, tr, uk, vi, zh)

### Cities Added
Added 1 major city for New Caledonia:

1. **Nouméa** - Capital and largest city
   - ID: 157075
   - Coordinates: -22.2758°S, 166.458°E
   - Timezone: Pacific/Noumea
   - WikiData: Q9733
   - Translations: 17 languages

## Before/After Counts

### States/Territories
- **Before:** 5071 French administrative divisions
- **After:** 5072 French administrative divisions
- **Change:** +1 territory (Nouvelle-Calédonie)

### Cities
- **Before:** 10243 French cities
- **After:** 10244 French cities
- **Change:** +1 city (Nouméa)

## Validation Steps and Results

### 1. Verified France State Count
```bash
# Before fix
jq '[.[] | select(.country_code == "FR")] | length' contributions/states/states.json
# Result: 123

# After fix
jq '[.[] | select(.country_code == "FR")] | length' contributions/states/states.json
# Result: 124
```

### 2. Verified New Caledonia State Details
```bash
mysql> SELECT id, name, iso3166_2, iso2, type, timezone FROM states 
       WHERE country_code = 'FR' AND name = 'Nouvelle-Calédonie';
# Result:
# id: 5538
# name: Nouvelle-Calédonie
# iso3166_2: FR-NC
# iso2: NC
# type: overseas collectivity with special status
# timezone: Pacific/Noumea
```

### 3. Verified France Cities Count
```bash
# Before fix
jq 'length' contributions/cities/FR.json
# Result: 10243

# After fix
jq 'length' contributions/cities/FR.json
# Result: 10244
```

### 4. Verified Nouméa City
```bash
mysql> SELECT id, name, state_code, timezone FROM cities 
       WHERE country_code = 'FR' AND name = 'Nouméa';
# Result:
# id: 157075
# name: Nouméa
# state_code: NC
# timezone: Pacific/Noumea
```

### 5. JSON File Validation
```bash
# States JSON
jq '.[] | select(.name == "Nouvelle-Calédonie")' contributions/states/states.json | jq '{id, name, iso3166_2, type, timezone, translations}'
# Output:
# {
#   "id": 5538,
#   "name": "Nouvelle-Calédonie",
#   "iso3166_2": "FR-NC",
#   "type": "overseas collectivity with special status",
#   "timezone": "Pacific/Noumea",
#   "translations": { (18 languages) }
# }

# Cities JSON
jq '.[] | select(.name == "Nouméa")' contributions/cities/FR.json | jq '{id, name, state_code, timezone, translations}'
# Output:
# {
#   "id": 157075,
#   "name": "Nouméa",
#   "state_code": "NC",
#   "timezone": "Pacific/Noumea",
#   "translations": { (17 languages) }
# }
```

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5538,
  "name": "Nouvelle-Calédonie",
  "country_id": 75,
  "country_code": "FR",
  "fips_code": null,
  "iso2": "NC",
  "iso3166_2": "FR-NC",
  "type": "overseas collectivity with special status",
  "level": null,
  "parent_id": null,
  "native": "Nouvelle-Calédonie",
  "latitude": "-21.25000000",
  "longitude": "165.30000000",
  "timezone": "Pacific/Noumea",
  "translations": {
    "ar": "كاليدونيا الجديدة",
    "bn": "নতুন ক্যালিডোনিয়া",
    "de": "Neukaledonien",
    "es": "Nueva Caledonia",
    "fr": "Nouvelle-Calédonie",
    "hi": "नया कैलेडोनिया",
    "id": "Kaledonia Baru",
    "it": "Nuova Caledonia",
    "ja": "ニューカレドニア",
    "ko": "누벨칼레도니",
    "nl": "Nieuw-Caledonië (gebiedsdeel)",
    "pl": "Nowa Kaledonia",
    "pt": "Nova Caledónia",
    "ru": "Новая Каледония",
    "tr": "Yeni Kaledonya",
    "uk": "Нова Каледонія",
    "vi": "Nouvelle-Calédonie",
    "zh": "新喀里多尼亞"
  },
  "created_at": "2025-10-28T07:00:02",
  "updated_at": "2025-10-28T07:01:29",
  "flag": 1,
  "wikiDataId": "Q33788",
  "population": null
}
```

### City Entry (FR.json)
```json
{
  "id": 157075,
  "name": "Nouméa",
  "state_id": 5538,
  "state_code": "NC",
  "country_id": 75,
  "country_code": "FR",
  "latitude": "-22.27580000",
  "longitude": "166.45800000",
  "native": "Nouméa",
  "timezone": "Pacific/Noumea",
  "translations": {
    "ar": "نوميا",
    "bn": "নুমেয়া",
    "de": "Nouméa",
    "es": "Numea",
    "fr": "Nouméa",
    "id": "Nouméa",
    "it": "Numea",
    "ja": "ヌメア",
    "ko": "누메아",
    "nl": "Nouméa (stad)",
    "pl": "Numea",
    "pt": "Numeá",
    "ru": "Нумеа",
    "tr": "Nouméa",
    "uk": "Нумеа",
    "vi": "Nouméa",
    "zh": "努美阿"
  },
  "created_at": "2025-10-28T07:04:44",
  "updated_at": "2025-10-28T07:04:44",
  "flag": 1,
  "wikiDataId": "Q9733"
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added Nouvelle-Calédonie state entry
2. `contributions/cities/FR.json` - Added Nouméa city entry

### Workflow Followed
1. Added Nouvelle-Calédonie to `contributions/states/states.json` (without ID, timezone, translations)
2. Ran `import_json_to_mysql.py` to import state and auto-assign ID (5538)
3. Ran `add_timezones.py` to auto-populate timezone field
4. Manually corrected timezone from "Europe/Paris" to "Pacific/Noumea" (UTC+11)
5. Ran `translation_enricher.py` to fetch 18 language translations from Wikipedia
6. Ran `sync_mysql_to_json.py` to sync updates back to JSON
7. Added Nouméa city to `contributions/cities/FR.json` (without ID)
8. Ran `import_json_to_mysql.py` to import city and auto-assign ID (157075)
9. Ran `add_timezones.py` for city, then manually corrected to Pacific/Noumea
10. Ran `translation_enricher.py` to fetch 17 language translations
11. Ran `sync_mysql_to_json.py` to sync final updates

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py --host localhost --user root --password root --database world

# Add timezone automatically
python3 bin/scripts/validation/add_timezones.py --host localhost --user root --password root --database world --table both

# Manual timezone correction (automatic detection gave wrong timezone)
mysql -uroot -proot world -e "UPDATE states SET timezone='Pacific/Noumea' WHERE id=5538;"
mysql -uroot -proot world -e "UPDATE cities SET timezone='Pacific/Noumea' WHERE id=157075;"

# Add translations from Wikipedia
python3 bin/scripts/validation/translation_enricher.py --file contributions/states/states.json --type state --country-code FR
python3 bin/scripts/validation/translation_enricher.py --file contributions/cities/FR.json --type city

# Sync MySQL back to JSON (updates all fields)
python3 bin/scripts/sync/sync_mysql_to_json.py --host localhost --user root --password root --database world

# Verification queries
mysql -uroot -proot world -e "SELECT id, name, timezone FROM states WHERE name='Nouvelle-Calédonie';"
mysql -uroot -proot world -e "SELECT id, name, timezone FROM cities WHERE name='Nouméa';"
```

## References
- **ISO 3166-2:FR Standard:** https://www.iso.org/obp/ui#iso:code:3166:FR
- **Wikipedia - New Caledonia:** https://en.wikipedia.org/wiki/New_Caledonia
- **Wikipedia - Nouméa:** https://en.wikipedia.org/wiki/Noumea
- **WikiData - New Caledonia:** https://www.wikidata.org/wiki/Q33788
- **WikiData - Nouméa:** https://www.wikidata.org/wiki/Q9733
- **Issue Report:** References ISO 3166-2:FR standard listing FR-NC as "Overseas Collectivity with Special Status"

## Compliance
✅ Matches ISO 3166-2:FR standard (FR-NC)  
✅ Includes proper native name (Nouvelle-Calédonie)  
✅ All entries have WikiData IDs  
✅ Follows existing data structure and formatting  
✅ Includes capital city (Nouméa)  
✅ Proper timezone (Pacific/Noumea, UTC+11) assigned  
✅ Coordinates verified from Wikipedia  
✅ Complete translations in 17-18 major languages  
✅ Uses "overseas collectivity with special status" type designation

## Notes
- New Caledonia is a sui generis collectivity located in the southwest Pacific Ocean
- The territory uses the Pacific/Noumea timezone (UTC+11)
- The automatic timezone detection tools initially gave "Europe/Paris" which had to be manually corrected
- New Caledonia has a special political status with a degree of autonomy
- The territory held independence referendums in 2018, 2020, and 2021, voting to remain part of France
