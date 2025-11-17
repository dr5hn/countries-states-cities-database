# Côte d'Ivoire Administrative Divisions Restructuring

## Issue Reference
**Issue:** [Data]: Côte d'Ivoire remove regions and add 1 missing district  
**Problem:** Côte d'Ivoire's administrative structure did not match ISO 3166-2:CI standard. The database contained 26 entities (2 autonomous districts, 11 districts, 13 regions) but ISO 3166-2:CI specifies only 14 entities (2 autonomous districts, 12 districts).

## Executive Summary
Successfully restructured Côte d'Ivoire's administrative divisions to match the ISO 3166-2:CI standard by:
1. Converting Savanes from region to district (the missing 12th district)
2. Removing 12 obsolete regions
3. Moving 10 cities from Dix-Huit Montagnes region to Montagnes district
4. Adding 10 major cities to the Savanes district

## Country Addressed
- **Country:** Côte d'Ivoire (Ivory Coast)
- **ISO Code:** CI
- **Country ID:** 54

## Changes Made

### 1. Converted Savanes from Region to District
**Before:**
- Name: Savanes
- ID: 2625
- Type: region
- ISO2: 03
- ISO3166-2: CI-03

**After:**
- Name: Savanes
- ID: 2625
- Type: district
- ISO2: SV
- ISO3166-2: CI-SV

### 2. Removed 12 Obsolete Regions
The following regions were removed as they are no longer part of the official administrative structure:

1. **Agnéby** (ID: 2626, ISO2: 16)
2. **Sud-Bandama** (ID: 2628, ISO2: 15)
3. **Moyen-Comoé** (ID: 2630, ISO2: 05)
4. **Marahoué** (ID: 2631, ISO2: 12)
5. **Fromager** (ID: 2633, ISO2: 18)
6. **Bafing** (ID: 2636, ISO2: 17)
7. **Haut-Sassandra** (ID: 2638, ISO2: 02)
8. **Dix-Huit Montagnes** (ID: 2645, ISO2: 06)
9. **Moyen-Cavally** (ID: 2646, ISO2: 19)
10. **Worodougou** (ID: 2649, ISO2: 14)
11. **Sud-Comoé** (ID: 2652, ISO2: 13)
12. **N'zi-Comoé** (ID: 2655, ISO2: 11)

### 3. Moved Cities from Dix-Huit Montagnes to Montagnes
The following 10 cities were reassigned from Dix-Huit Montagnes region (ID: 2645) to Montagnes district (ID: 2629):

1. **Bangolo** (ID: 18874)
2. **Biankouma** (ID: 18875)
3. **Cavally** (ID: 18889)
4. **Danané** (ID: 18893)
5. **Duekoué** (ID: 18897)
6. **Guiglo** (ID: 18907)
7. **Guémon** (ID: 18908)
8. **Man** (ID: 18919)
9. **Tonkpi** (ID: 18936)
10. **Toulépleu Gueré** (ID: 18938)

### 4. Added 10 Cities to Savanes District
Added major cities and administrative subdivisions to the newly converted Savanes district:

1. **Korhogo** (ID: 157179) - District capital
   - Coordinates: 9.45803°N, -5.62961°W
   - WikiData: Q852212

2. **Ferkéssédougou** (ID: 157180)
   - Coordinates: 9.60055°N, -5.19611°W
   - WikiData: Q849717

3. **Boundiali** (ID: 157181)
   - Coordinates: 9.52434°N, -6.48973°W
   - WikiData: Q853434

4. **Ouangolodougou** (ID: 157182)
   - Coordinates: 9.96667°N, -5.15000°W
   - WikiData: Q1788030

5. **Sinématiali** (ID: 157183)
   - Coordinates: 9.58333°N, -5.38333°W
   - WikiData: Q3485315

6. **Tengrela** (ID: 157184)
   - Coordinates: 10.48333°N, -6.40833°W
   - WikiData: Q3517463

7. **Kong** (ID: 157185)
   - Coordinates: 9.15000°N, -4.61667°W
   - WikiData: Q1030062

8. **Poro** (ID: 157186) - Region subdivision
   - Coordinates: 9.36667°N, -5.50000°W
   - WikiData: Q845994

9. **Bagoué** (ID: 157187) - Region subdivision
   - Coordinates: 9.75000°N, -6.50000°W
   - WikiData: Q850122

10. **Tchologo** (ID: 157188) - Region subdivision
    - Coordinates: 9.76667°N, -5.10000°W
    - WikiData: Q845989

## Before/After Counts

### Administrative Divisions
- **Before:** 26 entities (2 autonomous districts, 11 districts, 13 regions)
- **After:** 14 entities (2 autonomous districts, 12 districts, 0 regions)
- **Change:** -12 regions, +1 district (Savanes converted from region)

### Cities
- **Before:** 85 cities
- **After:** 95 cities
- **Change:** +10 cities (added to Savanes district)

### Final Structure (14 Districts)
**Autonomous Districts (2):**
1. Abidjan (CI-AB)
2. Yamoussoukro (CI-YM)

**Districts (12):**
1. Bas-Sassandra (CI-BS)
2. Comoé (CI-CM)
3. Denguélé (CI-DN)
4. Gôh-Djiboua (CI-GD)
5. Lacs (CI-LC)
6. Lagunes (CI-LG)
7. Montagnes (CI-MG)
8. Sassandra-Marahoué (CI-SM)
9. Savanes (CI-SV) ← **Converted from region**
10. Vallée du Bandama (CI-VB)
11. Woroba (CI-WR)
12. Zanzan (CI-ZZ)

## Validation Steps and Results

### 1. Verified Administrative Structure in MySQL
```bash
mysql> SELECT type, COUNT(*) as count FROM states 
       WHERE country_code = 'CI' GROUP BY type;
```
**Result:**
- Districts: 12
- Autonomous districts: 2
- Regions: 0
- **Total: 14** ✅

### 2. Verified Savanes District Conversion
```bash
mysql> SELECT id, name, iso2, iso3166_2, type 
       FROM states WHERE country_code = 'CI' AND name = 'Savanes';
```
**Result:**
- ID: 2625
- ISO2: SV (changed from 03)
- ISO3166-2: CI-SV (changed from CI-03)
- Type: district (changed from region) ✅

### 3. Verified Savanes District Cities
```bash
mysql> SELECT COUNT(*) FROM cities 
       WHERE country_code = 'CI' AND state_id = 2625;
```
**Result:** 10 cities ✅

### 4. Verified Montagnes District Cities
```bash
mysql> SELECT COUNT(*) FROM cities 
       WHERE country_code = 'CI' AND state_id = 2629;
```
**Result:** 10 cities (moved from Dix-Huit Montagnes) ✅

### 5. Verified No Cities Left in Removed Regions
```bash
mysql> SELECT COUNT(*) FROM cities 
       WHERE state_id IN (2626, 2628, 2630, 2631, 2633, 2636, 2638, 2645, 2646, 2649, 2652, 2655);
```
**Result:** 0 cities ✅

### 6. Verified Total City Count
```bash
mysql> SELECT COUNT(*) FROM cities WHERE country_code = 'CI';
```
**Result:** 95 cities (85 existing + 10 new) ✅

### 7. JSON File Validation
```bash
# States validation
jq '[.[] | select(.country_code == "CI")] | length' contributions/states/states.json
# Result: 14

# Cities validation
jq 'length' contributions/cities/CI.json
# Result: 95

# Savanes verification
jq '.[] | select(.id == 2625)' contributions/states/states.json
# Confirms: type = "district", iso2 = "SV"
```

## Data Quality Enhancements

### Timezone
All 10 new cities in Savanes district have timezone: `Africa/Abidjan`

### Translations
Translations were automatically enriched using the translation_enricher.py tool. All new cities have translations in multiple languages including:
- French (fr)
- Spanish (es)
- Italian (it)
- German (de)
- Russian (ru)

### WikiData Integration
All new cities have verified WikiData IDs linking to authoritative sources.

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Modified Savanes entry, removed 12 regions
2. `contributions/cities/CI.json` - Updated 10 cities, added 10 new cities

### Workflow Followed
```bash
# 1. Modified states and cities in JSON
python3 /tmp/update_cote_divoire.py

# 2. Normalized JSON to assign IDs
python3 bin/scripts/sync/normalize_json.py \
    --host localhost --user root --password root --database world \
    contributions/cities/CI.json

# 3. Imported to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py \
    --host localhost --user root --password root --database world

# 4. Added translations
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/CI.json --type city

# 5. Synced back to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py \
    --host localhost --user root --password root --database world
```

## References
- **ISO 3166-2:CI Standard:** https://www.iso.org/obp/ui#iso:code:3166:CI
- **Wikipedia - Côte d'Ivoire:** https://en.wikipedia.org/wiki/Ivory_Coast
- **Wikipedia - Districts of Côte d'Ivoire:** https://en.wikipedia.org/wiki/Districts_of_Ivory_Coast
- **Wikipedia - Savanes District:** https://en.wikipedia.org/wiki/Savanes_District
- **WikiData - Savanes:** https://www.wikidata.org/wiki/Q853460
- **WikiData - Korhogo:** https://www.wikidata.org/wiki/Q852212

## Compliance
✅ Matches ISO 3166-2:CI standard (14 districts: 2 autonomous + 12 regular)  
✅ All districts have correct ISO codes (CI-AB, CI-BS, CI-CM, etc.)  
✅ No obsolete regions remain in the database  
✅ All cities properly assigned to correct districts  
✅ Dix-Huit Montagnes cities successfully moved to Montagnes district  
✅ Savanes district populated with 10 major cities  
✅ All entries have proper WikiData IDs  
✅ Translations added for new cities  
✅ Proper timezone assigned (Africa/Abidjan)  
✅ Follows existing data structure and formatting
