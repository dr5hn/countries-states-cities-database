# Somalia Missing Regions Fix

## Issue Reference
**Issue:** [Data]: Somalia region missing  
**Problem:** Somalia was missing 2 regions out of the 18 regions listed in ISO 3166-2:SO standard

## Executive Summary
Successfully added the two missing regions (Sool and Woqooyi Galbeed) to Somalia's administrative divisions, bringing the total from 16 to 18 regions, matching the ISO 3166-2:SO standard. Added 5 major cities across the two new regions.

## Country Addressed
- **Country:** Somalia (SO)
- **ISO Code:** SO
- **Country ID:** 203

## Changes Made

### Regions Added

#### 1. Sool Region
- **Name:** Sool
- **ISO 3166-2 Code:** SO-SO
- **ISO2 Code:** SO
- **Region ID:** 5699
- **Native Name:** Sool
- **Coordinates:** 8.396°N, 47.691°E
- **Timezone:** Africa/Mogadishu
- **WikiData ID:** Q848864
- **Type:** region

#### 2. Woqooyi Galbeed Region
- **Name:** Woqooyi Galbeed
- **ISO 3166-2 Code:** SO-WO
- **ISO2 Code:** WO
- **Region ID:** 5700
- **Native Name:** Maroodi Jeex (formerly known as Woqooyi Galbeed, renamed in 2007)
- **Coordinates:** 9.563°N, 44.067°E
- **Timezone:** Africa/Mogadishu
- **WikiData ID:** Q10326669
- **Type:** region
- **Note:** This region was renamed from "Woqooyi Galbeed" to "Maroodi Jeex" in 2007, but the ISO 3166-2 code SO-WO remains unchanged

### Cities Added

#### Sool Region Cities (3)

1. **Las Anod** (Capital of Sool)
   - **ID:** 104821
   - **Native Name:** Laascaanood
   - **Coordinates:** 8.476°N, 47.357°E
   - **WikiData:** Q1017223
   - **State ID:** 5699
   - **State Code:** SO

2. **Aynaba**
   - **ID:** 104822
   - **Native Name:** Caynabo
   - **Coordinates:** 8.950°N, 46.417°E
   - **WikiData:** Q4058907
   - **State ID:** 5699
   - **State Code:** SO

3. **Hudun**
   - **ID:** 104823
   - **Native Name:** Xudun
   - **Coordinates:** 9.154°N, 47.477°E
   - **WikiData:** Q3388333
   - **State ID:** 5699
   - **State Code:** SO

#### Woqooyi Galbeed Region Cities (2)

1. **Hargeisa** (Capital of Woqooyi Galbeed/Maroodi Jeex)
   - **ID:** 104824
   - **Native Name:** Hargeysa
   - **Coordinates:** 9.563°N, 44.067°E
   - **WikiData:** Q168652
   - **State ID:** 5700
   - **State Code:** WO
   - **Note:** Hargeisa is the second-largest city in Somalia

2. **Gabiley**
   - **ID:** 104825
   - **Native Name:** Gabiley
   - **Coordinates:** 9.700°N, 43.624°E
   - **WikiData:** Q1016892
   - **State ID:** 5700
   - **State Code:** WO

## Before/After Counts

### Regions (States)
- **Before:** 16 regions
- **After:** 18 regions
- **Change:** +2 regions (Sool, Woqooyi Galbeed)

### Cities
- **Before:** 46 cities
- **After:** 51 cities
- **Change:** +5 cities (3 in Sool, 2 in Woqooyi Galbeed)

## ISO 3166-2:SO Compliance

All 18 regions now match the ISO 3166-2:SO standard:

| ISO Code | Region Name | Status |
|----------|-------------|--------|
| SO-AW | Awdal | ✅ Existing |
| SO-BK | Bakool | ✅ Existing |
| SO-BN | Banaadir | ✅ Existing |
| SO-BR | Bari | ✅ Existing |
| SO-BY | Bay | ✅ Existing |
| SO-GA | Galguduud | ✅ Existing |
| SO-GE | Gedo | ✅ Existing |
| SO-HI | Hiiraan (as "Hiran") | ✅ Existing |
| SO-JD | Jubbada Dhexe (as "Middle Juba") | ✅ Existing |
| SO-JH | Jubbada Hoose (as "Lower Juba") | ✅ Existing |
| SO-MU | Mudug | ✅ Existing |
| SO-NU | Nugaal (as "Nugal") | ✅ Existing |
| SO-SA | Sanaag | ✅ Existing |
| SO-SD | Shabeellaha Dhexe (as "Middle Shebelle") | ✅ Existing |
| SO-SH | Shabeellaha Hoose (as "Lower Shebelle") | ✅ Existing |
| SO-SO | Sool | ✅ **ADDED** |
| SO-TO | Togdheer | ✅ Existing |
| SO-WO | Woqooyi Galbeed | ✅ **ADDED** |

## Validation Steps

### 1. Verified Somalia Region Count
```bash
jq '[.[] | select(.country_code == "SO")] | length' contributions/states/states.json
# Result: 18 (was 16)
```

### 2. Verified New Regions
```bash
jq '[.[] | select(.country_code == "SO" and (.name == "Sool" or .name == "Woqooyi Galbeed"))]' contributions/states/states.json
# Result: Returns both new regions with proper metadata
```

### 3. Verified Somalia Cities Count
```bash
jq 'length' contributions/cities/SO.json
# Result: 51 (was 46)
```

### 4. Verified Cities for New Regions
```bash
jq '[.[] | select(.state_id == 5699 or .state_id == 5700)]' contributions/cities/SO.json
# Result: Returns 5 cities (3 for Sool, 2 for Woqooyi Galbeed)
```

### 5. ISO 3166-2 Compliance Check
```bash
jq '[.[] | select(.country_code == "SO")] | sort_by(.iso3166_2) | .[] | .iso3166_2' contributions/states/states.json
# Result: All 18 ISO codes match the standard
```

## Data Samples

### Sool Region Entry (states.json)
```json
{
  "name": "Sool",
  "country_id": 203,
  "country_code": "SO",
  "fips_code": null,
  "iso2": "SO",
  "iso3166_2": "SO-SO",
  "type": "region",
  "level": null,
  "parent_id": null,
  "native": "Sool",
  "latitude": "8.39611111",
  "longitude": "47.69138889",
  "timezone": "Africa/Mogadishu",
  "translations": {},
  "created_at": "2025-11-17T04:43:03",
  "updated_at": "2025-11-17T04:43:03",
  "flag": 1,
  "wikiDataId": "Q848864",
  "population": null,
  "id": 5699
}
```

### Woqooyi Galbeed Region Entry (states.json)
```json
{
  "name": "Woqooyi Galbeed",
  "country_id": 203,
  "country_code": "SO",
  "fips_code": null,
  "iso2": "WO",
  "iso3166_2": "SO-WO",
  "type": "region",
  "level": null,
  "parent_id": null,
  "native": "Maroodi Jeex",
  "latitude": "9.56305556",
  "longitude": "44.06750000",
  "timezone": "Africa/Mogadishu",
  "translations": {},
  "created_at": "2025-11-17T04:43:03",
  "updated_at": "2025-11-17T04:43:03",
  "flag": 1,
  "wikiDataId": "Q10326669",
  "population": null,
  "id": 5700
}
```

### Sample City Entry - Las Anod (SO.json)
```json
{
  "name": "Las Anod",
  "state_id": 5699,
  "state_code": "SO",
  "country_id": 203,
  "country_code": "SO",
  "latitude": "8.47600000",
  "longitude": "47.35700000",
  "native": "Laascaanood",
  "wikiDataId": "Q1017223",
  "id": 104821,
  "timezone": "Africa/Mogadishu",
  "translations": {},
  "created_at": "2025-11-17T04:43:46",
  "updated_at": "2025-11-17T04:43:46",
  "flag": 1
}
```

### Sample City Entry - Hargeisa (SO.json)
```json
{
  "name": "Hargeisa",
  "state_id": 5700,
  "state_code": "WO",
  "country_id": 203,
  "country_code": "SO",
  "latitude": "9.56305556",
  "longitude": "44.06750000",
  "native": "Hargeysa",
  "wikiDataId": "Q168652",
  "id": 104824,
  "timezone": "Africa/Mogadishu",
  "translations": {},
  "created_at": "2025-11-17T04:43:46",
  "updated_at": "2025-11-17T04:43:46",
  "flag": 1
}
```

## Technical Implementation

### Files Modified
1. `contributions/states/states.json` - Added 2 region entries (Sool and Woqooyi Galbeed)
2. `contributions/cities/SO.json` - Added 5 city entries (3 for Sool, 2 for Woqooyi Galbeed)

### Workflow Followed
1. Researched missing regions from ISO 3166-2:SO standard and Wikipedia
2. Collected coordinates and WikiData IDs from Wikipedia API
3. Added region entries to `contributions/states/states.json`
4. Manually assigned IDs (5699 for Sool, 5700 for Woqooyi Galbeed)
5. Researched and added major cities for each region
6. Assigned city IDs (104821-104825)
7. Added proper timezone (Africa/Mogadishu) for all entries
8. Validated JSON structure and data completeness

### ID Assignment
- **State IDs:** Manually assigned sequential IDs (5699, 5700) after finding max existing ID (5698)
- **City IDs:** Manually assigned sequential IDs (104821-104825) after finding max existing ID (104820)
- **Timestamps:** Auto-generated in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)

### Translation Note
- Translations were left empty (`{}`) to be populated by the automated GitHub Actions workflow
- The workflow will run `translation_enricher.py` to fetch translations from Wikipedia

## References

### Official Sources
- **ISO 3166-2:SO Standard:** https://www.iso.org/obp/ui#iso:code:3166:SO
- **Administrative Divisions of Somalia:** https://en.wikipedia.org/wiki/Administrative_divisions_of_Somalia

### Region-Specific Sources
- **Sool Region:** https://en.wikipedia.org/wiki/Sool
- **Woqooyi Galbeed/Maroodi Jeex:** https://en.wikipedia.org/wiki/Maroodi_Jeex

### City Sources
- **Las Anod:** https://en.wikipedia.org/wiki/Las_Anod
- **Hargeisa:** https://en.wikipedia.org/wiki/Hargeisa
- **Aynaba:** https://www.wikidata.org/wiki/Q4058907
- **Hudun:** https://www.wikidata.org/wiki/Q3388333
- **Gabiley:** https://www.wikidata.org/wiki/Q1016892

### WikiData Sources
- **Sool Region:** https://www.wikidata.org/wiki/Q848864
- **Woqooyi Galbeed/Maroodi Jeex:** https://www.wikidata.org/wiki/Q10326669
- **Las Anod:** https://www.wikidata.org/wiki/Q1017223
- **Hargeisa:** https://www.wikidata.org/wiki/Q168652

## Historical Notes

### Woqooyi Galbeed Naming
The region "Woqooyi Galbeed" (meaning "North West" in Somali) was officially renamed to "Maroodi Jeex" in 2007. However:
- The ISO 3166-2 code **SO-WO** remains unchanged
- Some international organizations (OCHA, FAO) still use "Woqooyi Galbeed"
- For consistency with ISO 3166-2:SO, the database uses "Woqooyi Galbeed" as the primary name
- The native name field contains "Maroodi Jeex" to reflect current usage

### Political Context
Both Sool and Woqooyi Galbeed/Maroodi Jeex regions are part of the disputed territory between Somalia and Somaliland. This database follows the ISO 3166-2:SO standard which lists them as regions of Somalia.

## Compliance Checklist

✅ Matches ISO 3166-2:SO standard (18 regions)  
✅ Includes proper WikiData IDs for all new entries  
✅ Follows existing data structure and formatting  
✅ Includes regional capitals (Las Anod, Hargeisa)  
✅ Proper timezone (Africa/Mogadishu) assigned  
✅ Coordinates verified from Wikipedia  
✅ Native names included for all entries  
✅ JSON structure validated  
⏳ Translations to be added by automated workflow

## Next Steps

The following will be handled by the GitHub Actions workflow:
1. Run `import_json_to_mysql.py` to import new data to MySQL
2. Run `add_timezones.py` to verify timezone data (already set correctly)
3. Run `sync_mysql_to_json.py` to sync any updates back to JSON
4. Run `translation_enricher.py` to add translations from Wikipedia
5. Final validation and export generation
