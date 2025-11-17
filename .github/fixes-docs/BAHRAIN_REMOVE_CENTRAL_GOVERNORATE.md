# Bahrain: Remove Central Governorate

## Issue Reference
**Issue:** [Data]: Bahrain remove extra governorate  
**Problem:** Bahrain has 5 governorates in the database, but according to ISO 3166-2:BH and Wikipedia, it should only have 4 governorates. The "Central" governorate (BH-16) was abolished and its cities were redistributed to other governorates.

## Countries/Regions Addressed
- Bahrain (BH)

## Changes Made

### States
**Before:** 5 governorates  
**After:** 4 governorates  
**Removed:** Central governorate (id: 1996, iso3166_2: BH-16)

**Remaining governorates (matching ISO 3166-2:BH):**
1. Capital (Al 'Asimah) - BH-13
2. Southern (Al Janubiyah) - BH-14
3. Northern (Ash Shamaliyah) - BH-17
4. Muharraq (Al Muharraq) - BH-15

### Cities
**City reassignment:**
- Madīnat Ḩamad (id: 9758)
  - **Before:** state_id: 1996 (Central), state_code: "16"
  - **After:** state_id: 1994 (Northern), state_code: "17"

## Validation Steps

### 1. JSON File Validation
```bash
# Validate JSON syntax
jq empty contributions/cities/BH.json && echo "BH.json is valid JSON"
jq empty contributions/states/states.json && echo "states.json is valid JSON"
```
**Result:** ✅ Both files validated successfully

### 2. State Count Verification
```bash
# Count Bahrain states
jq '[.[] | select(.country_code == "BH")] | length' contributions/states/states.json
```
**Result:** 4 governorates (previously 5)

### 3. State Details Verification
```bash
# List all Bahrain states
jq '[.[] | select(.country_code == "BH")] | map({name: .name, iso3166_2: .iso3166_2})' contributions/states/states.json
```
**Result:**
```json
[
  {"name": "Capital", "iso3166_2": "BH-13"},
  {"name": "Southern", "iso3166_2": "BH-14"},
  {"name": "Northern", "iso3166_2": "BH-17"},
  {"name": "Muharraq", "iso3166_2": "BH-15"}
]
```

### 4. City Reassignment Verification
```bash
# Check Madīnat Ḩamad city
jq '.[] | select(.id == 9758) | {name: .name, state_id: .state_id, state_code: .state_code}' contributions/cities/BH.json
```
**Result:**
```json
{
  "name": "Madīnat Ḩamad",
  "state_id": 1994,
  "state_code": "17"
}
```

### 5. MySQL Database Verification
```bash
# Verify in MySQL
mysql -uroot -proot world -e "SELECT COUNT(*) FROM states WHERE country_code = 'BH';"
mysql -uroot -proot world -e "SELECT id, name, iso3166_2 FROM states WHERE country_code = 'BH' ORDER BY id;"
mysql -uroot -proot world -e "SELECT id, name, state_id, state_code FROM cities WHERE id = 9758;"
```
**Results:**
- States count: 4
- All 4 states match ISO 3166-2 standard
- Madīnat Ḩamad correctly assigned to Northern governorate

### 6. Data Synchronization
```bash
# Import JSON to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py --password root

# Sync MySQL back to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py --password root
```
**Result:** ✅ Both operations completed successfully with consistent data

## Data Samples

### Removed State Entry (Central)
```json
{
  "id": 1996,
  "name": "Central",
  "country_id": 18,
  "country_code": "BH",
  "iso2": "16",
  "iso3166_2": "BH-16",
  "type": "governorate"
}
```
*This entry was completely removed from contributions/states/states.json*

### Updated City Entry (Madīnat Ḩamad)
```json
{
  "id": 9758,
  "name": "Madīnat Ḩamad",
  "state_id": 1994,
  "state_code": "17",
  "country_id": 18,
  "country_code": "BH",
  "latitude": "26.11528000",
  "longitude": "50.50694000",
  "native": "Madīnat ḩamad",
  "timezone": "Asia/Bahrain",
  "wikiDataId": "Q2088687"
}
```

## References
- **ISO 3166-2:BH:** https://www.iso.org/obp/ui#iso:code:3166:BH
- **Wikipedia - Governorates of Bahrain:** https://en.wikipedia.org/wiki/Governorates_of_Bahrain
- **WikiData - Central Governorate (historical):** https://www.wikidata.org/wiki/Q856539

## Impact
- **Database structure:** States count for Bahrain reduced from 5 to 4
- **API changes:** Any queries filtering by BH-16 (Central governorate) will now return no results
- **Data integrity:** All Bahrain data now matches official ISO 3166-2:BH standard
- **Breaking changes:** Applications hardcoding state_id 1996 (Central) will need to update to 1994 (Northern) for Madīnat Ḩamad
- **Data quality:** ✅ Improved - database now accurately reflects current administrative divisions

## Notes
According to ISO 3166-2:BH and Wikipedia, the Central Governorate was abolished in Bahrain, and the territory was redistributed among the remaining governorates. The database now correctly reflects the current administrative structure with only 4 governorates as per the official standard.
