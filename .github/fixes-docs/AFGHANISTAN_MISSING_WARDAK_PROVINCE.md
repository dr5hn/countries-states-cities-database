# Afghanistan Missing Province Fix - Wardak Province

## Issue Reference
**Title:** [Data]: Afghanistan province missing  
**Problem:** Afghanistan was missing 1 province out of the 34 provinces listed in ISO 3166-2:AF standard

## Executive Summary
Successfully added the missing Wardak province (officially "Maidan Wardak Province") to Afghanistan's administrative divisions, bringing the total from 33 to 34 provinces, matching the ISO 3166-2:AF standard.

## Country Addressed
- **Country:** Afghanistan (AF)
- **ISO Code:** AF
- **Country ID:** 1

## Changes Made

### Province Addition
**Added Province:**
- **Name:** Wardak
- **Official Name:** Maidan Wardak Province (میدان وردک)
- **ISO 3166-2 Code:** AF-WAR
- **ISO2 Code:** WAR
- **Province ID:** 5468
- **Coordinates:** 34.30°N, 68.50°E
- **Timezone:** Asia/Kabul
- **WikiData ID:** Q171366

### Cities Added
Added 9 major cities/districts for Wardak province:

1. **Maidan Shahr** (میدان شهر) - Provincial capital
   - ID: 157059
   - Coordinates: 34.38°N, 68.54°E
   - WikiData: Q962619

2. **Chaki Wardak** (چکی وردک)
   - ID: 157060
   - Coordinates: 34.29°N, 68.58°E
   - WikiData: Q5067706

3. **Jalrez** (جلریز)
   - ID: 157061
   - Coordinates: 34.52°N, 68.78°E
   - WikiData: Q6126984

4. **Nerkh** (نرخ)
   - ID: 157062
   - Coordinates: 34.49°N, 68.51°E
   - WikiData: Q6996115

5. **Sayed Abad** (سید آباد)
   - ID: 157063
   - Coordinates: 34.00°N, 68.63°E
   - WikiData: Q7429446

6. **Day Mirdad** (دای میرداد)
   - ID: 157064
   - Coordinates: 34.50°N, 69.00°E
   - WikiData: Q5242583

7. **Hisa-i-Awali Bihsud** (حصه اول بهسود)
   - ID: 157065
   - Coordinates: 34.65°N, 68.18°E
   - WikiData: Q5770082

8. **Markaz-i-Bihsud** (مرکز بهسود)
   - ID: 157066
   - Coordinates: 34.55°N, 67.80°E
   - WikiData: Q6763663

9. **Jaghatu** (جغتو)
   - ID: 157067
   - Coordinates: 34.08°N, 68.45°E
   - WikiData: Q5920788

## Before/After Counts

### Provinces (States)
- **Before:** 33 provinces
- **After:** 34 provinces
- **Change:** +1 province (Wardak)

### Cities
- **Before:** 91 cities
- **After:** 100 cities
- **Change:** +9 cities (all in Wardak province)

## Validation Steps and Results

### 1. Verified Afghanistan Province Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'AF';
# Result: 33

# After fix
mysql> SELECT COUNT(*) FROM states WHERE country_code = 'AF';
# Result: 34
```

### 2. Verified Wardak Province Details
```bash
mysql> SELECT id, name, iso3166_2, iso2 FROM states 
       WHERE country_code = 'AF' AND name = 'Wardak';
# Result:
# id: 5468
# name: Wardak
# iso3166_2: AF-WAR
# iso2: WAR
```

### 3. Verified Afghanistan Cities Count
```bash
# Before fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'AF';
# Result: 91

# After fix
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'AF';
# Result: 100
```

### 4. Verified Wardak Cities
```bash
mysql> SELECT COUNT(*) FROM cities WHERE state_id = 5468;
# Result: 9
```

### 5. JSON File Validation
```bash
# States JSON
python3 -c "
import json
with open('contributions/states/states.json') as f:
    states = json.load(f)
af = [s for s in states if s['country_code'] == 'AF']
print(f'Afghanistan provinces: {len(af)}')
wardak = [s for s in af if 'wardak' in s['name'].lower()]
print(f'Wardak found: {len(wardak) > 0}')
"
# Output:
# Afghanistan provinces: 34
# Wardak found: True

# Cities JSON
python3 -c "
import json
with open('contributions/cities/AF.json') as f:
    cities = json.load(f)
print(f'Afghanistan cities: {len(cities)}')
wardak = [c for c in cities if c['state_id'] == 5468]
print(f'Wardak cities: {len(wardak)}')
"
# Output:
# Afghanistan cities: 100
# Wardak cities: 9
```

## Data Samples

### State Entry (states.json)
```json
{
  "id": 5468,
  "name": "Wardak",
  "country_id": 1,
  "country_code": "AF",
  "fips_code": null,
  "iso2": "WAR",
  "iso3166_2": "AF-WAR",
  "type": "province",
  "level": null,
  "parent_id": null,
  "native": "میدان وردک",
  "latitude": "34.30000000",
  "longitude": "68.50000000",
  "timezone": "Asia/Kabul",
  "translations": {},
  "created_at": "2025-10-16T12:11:41",
  "updated_at": "2025-10-16T12:11:41",
  "flag": 1,
  "wikiDataId": "Q171366",
  "population": null
}
```

### Sample City Entry (AF.json)
```json
{
  "id": 157059,
  "name": "Maidan Shahr",
  "state_id": 5468,
  "state_code": "WAR",
  "country_id": 1,
  "country_code": "AF",
  "latitude": "34.38000000",
  "longitude": "68.54000000",
  "native": "میدان شهر",
  "timezone": "Asia/Kabul",
  "translations": {},
  "created_at": "2025-10-16T12:17:28",
  "updated_at": "2025-10-16T12:17:28",
  "flag": 1,
  "wikiDataId": "Q962619"
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added Wardak province entry
2. `contributions/cities/AF.json` - Added 9 cities for Wardak province

### Workflow Followed
1. Added Wardak province to `contributions/states/states.json` (without ID)
2. Ran `import_json_to_mysql.py` to import province and auto-assign ID
3. Ran `sync_mysql_to_json.py` to sync ID back to JSON
4. Added 9 cities for Wardak to `contributions/cities/AF.json` (without IDs)
5. Inserted cities directly to MySQL
6. Ran `sync_mysql_to_json.py` to sync city IDs back to JSON

### Commands Used
```bash
# Import JSON to MySQL (generates IDs)
python3 bin/scripts/sync/import_json_to_mysql.py --host localhost --user root --password root --database world

# Sync MySQL back to JSON (updates IDs)
python3 bin/scripts/sync/sync_mysql_to_json.py --host localhost --user root --password root --database world

# Verification queries
mysql -uroot -proot world -e "SELECT COUNT(*) FROM states WHERE country_code = 'AF';"
mysql -uroot -proot world -e "SELECT COUNT(*) FROM cities WHERE country_code = 'AF';"
mysql -uroot -proot world -e "SELECT COUNT(*) FROM cities WHERE state_id = 5468;"
```

## References
- **ISO 3166-2:AF Standard:** https://www.iso.org/obp/ui#iso:code:3166:AF
- **Wikipedia - Provinces of Afghanistan:** https://en.wikipedia.org/wiki/Provinces_of_Afghanistan
- **Wikipedia - Maidan Wardak Province:** https://en.wikipedia.org/wiki/Maidan_Wardak_Province
- **WikiData - Wardak:** https://www.wikidata.org/wiki/Q171366
- **WikiData - Maidan Shahr:** https://www.wikidata.org/wiki/Q962619

## Compliance
✅ Matches ISO 3166-2:AF standard (34 provinces)  
✅ Includes official native names in Dari/Pashto  
✅ All entries have proper WikiData IDs  
✅ Follows existing data structure and formatting  
✅ Includes provincial capital and major districts  
✅ Proper timezone (Asia/Kabul) assigned  
✅ Coordinates verified from multiple sources
