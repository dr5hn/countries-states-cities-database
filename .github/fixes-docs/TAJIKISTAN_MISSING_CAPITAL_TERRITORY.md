# Tajikistan Missing Capital Territory Fix - Dushanbe

## Issue Reference
**Issue:** [Data]: Tajikistan capital territory missing  
**Problem:** Tajikistan was missing 1 capital territory out of the 5 administrative divisions listed in ISO 3166-2:TJ standard

## Executive Summary
Successfully added the missing Dushanbe capital territory to Tajikistan's administrative divisions, bringing the total from 4 to 5 divisions, matching the ISO 3166-2:TJ standard. Added Dushanbe city as the capital of the territory with complete timezone and translation enrichment.

## Country Addressed
- **Country:** Tajikistan (TJ)
- **ISO Code:** TJ
- **Country ID:** 217

## Changes Made

### State/Territory Addition
**Added Territory:**
- **Name:** Dushanbe
- **Official Name:** Dushanbe (Душанбе)
- **ISO 3166-2 Code:** TJ-DU
- **ISO2 Code:** DU
- **State ID:** 5706
- **Type:** capital territory
- **Coordinates:** 38.53666667°N, 68.78°E
- **Timezone:** Asia/Dushanbe
- **WikiData ID:** Q9365
- **Translations:** 18 languages (ar, bn, de, es, fr, hi, id, it, ja, ko, nl, pl, pt, ru, tr, uk, vi, zh)

### City Addition
**Added City:**
1. **Dushanbe** (Душанбе) - Capital city
   - ID: 157170
   - State ID: 5706
   - State Code: DU
   - Coordinates: 38.53666667°N, 68.78°E
   - Timezone: Asia/Dushanbe
   - WikiData: Q9365
   - Translations: 18 languages
   - Population: ~1,228,400 (as of February 2023)

## Before/After Counts

### States/Territories
- **Before:** 4 administrative divisions
  1. TJ-RA - Nohiyahoi Tobei Jumhurí (districts under republic administration)
  2. TJ-KT - Khatlon (region)
  3. TJ-GB - Gorno-Badakhshan (autonomous region)
  4. TJ-SU - Sughd (region)
- **After:** 5 administrative divisions
  1. TJ-RA - Nohiyahoi Tobei Jumhurí (districts under republic administration)
  2. TJ-KT - Khatlon (region)
  3. TJ-GB - Gorno-Badakhshan (autonomous region)
  4. TJ-SU - Sughd (region)
  5. TJ-DU - Dushanbe (capital territory) ✅ **NEW**
- **Change:** +1 territory (Dushanbe)

### Cities
- **Before:** 70 cities
- **After:** 71 cities
- **Change:** +1 city (Dushanbe)

## Validation Steps and Results

### 1. Verified Tajikistan State Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'TJ';
# Result: 4

# After fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'TJ';
# Result: 5
```

### 2. Verified Dushanbe Territory Details
```bash
mysql> SELECT id, name, iso3166_2, iso2, type FROM states 
       WHERE country_code = 'TJ' AND name = 'Dushanbe';
# Result:
# id: 5706
# name: Dushanbe
# iso3166_2: TJ-DU
# iso2: DU
# type: capital territory
```

### 3. Verified All 5 ISO Divisions Present
```bash
mysql> SELECT iso3166_2, name, type FROM states 
       WHERE country_code = 'TJ' ORDER BY id;
# Results:
# TJ-RA | Nohiyahoi Tobei Jumhurí | districts under republic administration
# TJ-KT | Khatlon | region
# TJ-GB | Gorno-Badakhshan | autonomous region
# TJ-SU | Sughd | region
# TJ-DU | Dushanbe | capital territory
```

### 4. Verified Tajikistan Cities Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'TJ';
# Result: 70

# After fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'TJ';
# Result: 71
```

### 5. Verified Dushanbe City
```bash
mysql> SELECT id, name, state_code, timezone FROM cities 
       WHERE country_code = 'TJ' AND name = 'Dushanbe';
# Result:
# id: 157170
# name: Dushanbe
# state_code: DU
# timezone: Asia/Dushanbe
```

### 6. JSON File Validation
```bash
# States JSON
jq '[.[] | select(.country_code == "TJ")] | length' contributions/states/states.json
# Output: 5

# Verify Dushanbe state
jq '.[] | select(.country_code == "TJ" and .name == "Dushanbe")' contributions/states/states.json
# Output: Complete state object with all fields

# Cities JSON
jq 'length' contributions/cities/TJ.json
# Output: 71

# Verify Dushanbe city
jq '.[] | select(.name == "Dushanbe")' contributions/cities/TJ.json
# Output: Complete city object with all fields
```

### 7. Wikipedia Validation
```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Dushanbe" \
    --type city \
    --country TJ \
    --output /tmp/dushanbe_validation.json

# Results:
# ✅ Found article: Dushanbe
# ✅ WikiData ID: Q9365
# ✅ Coordinates: 38.53666667, 68.78
# ✅ Description: "capital and largest city of Tajikistan"
```

### 8. Timezone Enrichment
```bash
python3 bin/scripts/validation/add_timezones.py \
    --host localhost --user root --password root --database world \
    --table states

# Results for Dushanbe state:
# Dushanbe, TJ: NULL → Asia/Dushanbe ✅

python3 bin/scripts/validation/add_timezones.py \
    --host localhost --user root --password root --database world \
    --table cities

# Results for Dushanbe city:
# Dushanbe, DU, TJ: NULL → Asia/Dushanbe ✅
```

### 9. Translation Enrichment
```bash
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code TJ

# Results:
# ✅ Added translations for Dushanbe: 18 languages

python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/TJ.json \
    --type city

# Results:
# ✅ Added translations for Dushanbe: 18 languages
```

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5706,
  "name": "Dushanbe",
  "country_id": 217,
  "country_code": "TJ",
  "fips_code": null,
  "iso2": "DU",
  "iso3166_2": "TJ-DU",
  "type": "capital territory",
  "level": null,
  "parent_id": null,
  "native": "Душанбе",
  "latitude": "38.53666667",
  "longitude": "68.78000000",
  "timezone": "Asia/Dushanbe",
  "translations": {
    "ar": "دوشنبة",
    "bn": "দুশান্‌বে",
    "de": "Duschanbe",
    "es": "Dusambé",
    "fr": "Douchanbé",
    "hi": "दुशान्बे",
    "id": "Dushanbe",
    "it": "Dušanbe",
    "ja": "ドゥシャンベ",
    "ko": "두샨베",
    "nl": "Doesjanbe",
    "pl": "Duszanbe",
    "pt": "Duxambé",
    "ru": "Душанбе",
    "tr": "Duşanbe",
    "uk": "Душанбе",
    "vi": "Dushanbe",
    "zh": "杜尚别"
  },
  "created_at": "2025-11-17T12:01:20",
  "updated_at": "2025-11-17T12:03:11",
  "flag": 1,
  "wikiDataId": "Q9365",
  "population": null
}
```

### City Entry (TJ.json)
```json
{
  "id": 157170,
  "name": "Dushanbe",
  "state_id": 5706,
  "state_code": "DU",
  "country_id": 217,
  "country_code": "TJ",
  "latitude": "38.53666667",
  "longitude": "68.78000000",
  "native": "Душанбе",
  "timezone": "Asia/Dushanbe",
  "translations": {
    "ar": "دوشنبة",
    "bn": "দুশান্‌বে",
    "de": "Duschanbe",
    "es": "Dusambé",
    "fr": "Douchanbé",
    "hi": "दुशान्बे",
    "id": "Dushanbe",
    "it": "Dušanbe",
    "ja": "ドゥシャンベ",
    "ko": "두샨베",
    "nl": "Doesjanbe",
    "pl": "Duszanbe",
    "pt": "Duxambé",
    "ru": "Душанбе",
    "tr": "Duşanbe",
    "uk": "Душанбе",
    "vi": "Dushanbe",
    "zh": "杜尚别"
  },
  "created_at": "2025-11-17T12:05:27",
  "updated_at": "2025-11-17T12:05:36",
  "flag": 1,
  "wikiDataId": "Q9365"
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added Dushanbe capital territory
2. `contributions/cities/TJ.json` - Added Dushanbe city

### Workflow Followed
1. Added Dushanbe territory to `contributions/states/states.json` (without ID)
2. Ran `import_json_to_mysql.py` to import territory and auto-assign ID (5706)
3. Ran `sync_mysql_to_json.py` to sync ID back to JSON
4. Ran `add_timezones.py --table states` to add timezone to Dushanbe state
5. Ran `sync_mysql_to_json.py` to sync timezone to JSON
6. Ran `translation_enricher.py` to add 18 language translations to state
7. Added Dushanbe city to `contributions/cities/TJ.json` (without ID)
8. Ran `import_json_to_mysql.py` to import city and auto-assign ID (157170)
9. Ran `add_timezones.py --table cities` to add timezone to Dushanbe city
10. Ran `sync_mysql_to_json.py` to sync city ID and timezone to JSON
11. Ran `translation_enricher.py` to add 18 language translations to city
12. Ran `import_json_to_mysql.py` to finalize all changes in MySQL

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py \
    --host localhost --user root --password root --database world

# Sync MySQL back to JSON (updates IDs)
python3 bin/scripts/sync/sync_mysql_to_json.py \
    --host localhost --user root --password root --database world

# Add timezones (MySQL-based)
python3 bin/scripts/validation/add_timezones.py \
    --host localhost --user root --password root --database world \
    --table states

python3 bin/scripts/validation/add_timezones.py \
    --host localhost --user root --password root --database world \
    --table cities

# Add translations (JSON-based)
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code TJ

python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/TJ.json \
    --type city

# Wikipedia validation
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Dushanbe" \
    --type city \
    --country TJ

# Verification queries
mysql -uroot -proot world -e "SELECT COUNT(*) FROM states WHERE country_code = 'TJ';"
mysql -uroot -proot world -e "SELECT COUNT(*) FROM cities WHERE country_code = 'TJ';"
mysql -uroot -proot world -e "SELECT id, name, iso3166_2 FROM states WHERE country_code = 'TJ';"
```

## References
- **ISO 3166-2:TJ Standard:** https://www.iso.org/obp/ui#iso:code:3166:TJ
- **Wikipedia - Tajikistan:** https://en.wikipedia.org/wiki/Tajikistan
- **Wikipedia - Dushanbe:** https://en.wikipedia.org/wiki/Dushanbe
- **WikiData - Dushanbe:** https://www.wikidata.org/wiki/Q9365

## ISO 3166-2:TJ Compliance

According to ISO 3166-2:TJ, Tajikistan has 5 administrative divisions:

| Type | Code | Name | Status |
|------|------|------|--------|
| capital territory | TJ-DU | Dushanbe | ✅ Added |
| region | TJ-KT | Khatlon | ✅ Existing |
| autonomous region | TJ-GB | Kuhistoni Badakhshon | ✅ Existing |
| region | TJ-SU | Sughd | ✅ Existing |
| districts under republic administration | TJ-RA | Nohiyahoi Tobei Jumhuri | ✅ Existing |

**✅ All 5 ISO 3166-2:TJ divisions are now present in the database**

## Impact
- **API Changes:** None - backward compatible addition
- **Breaking Changes:** None
- **Data Quality Improvements:**
  - Complete ISO 3166-2:TJ compliance (5/5 divisions)
  - Added capital city with full metadata
  - Timezone information (Asia/Dushanbe)
  - Multi-language translations (18 languages)
  - WikiData integration (Q9365)
  - Geographic coordinates verified from Wikipedia

## Data Quality Features
✅ Matches ISO 3166-2:TJ standard (5 divisions)  
✅ Includes official native name in Cyrillic (Душанбе)  
✅ WikiData ID verified (Q9365)  
✅ Follows existing data structure and formatting  
✅ Proper timezone assigned (Asia/Dushanbe)  
✅ Coordinates verified from Wikipedia API (38.53666667°N, 68.78°E)  
✅ Complete translation coverage (18 languages)  
✅ Auto-generated IDs via MySQL AUTO_INCREMENT  
✅ Proper foreign key relationships maintained  
✅ Consistent with other capital territories in database
