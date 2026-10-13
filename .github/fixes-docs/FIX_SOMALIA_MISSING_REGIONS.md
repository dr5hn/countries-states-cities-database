# Somalia Missing Regions Fix

## Issue Reference
**Issue:** [Data]: Somalia region missing  
**Problem:** Somalia was missing 2 regions out of the 18 regions listed in ISO 3166-2:SO standard

> **Note (13 October 2026):** the five cities' current ids are 160112-160116. The original merge (#1265) gave
> them 157165-157169, and they had become 160112-160116 by #1289. The ids first written here, 104821-104825,
> belong to Suriname records and must not be used for these cities.

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
- **Native Name:** Maroodi Jeex (the name the Somaliland administration uses; ISO 3166-2 lists SO-WO as Woqooyi Galbeed)
- **Coordinates:** 9.563°N, 44.067°E
- **Timezone:** Africa/Mogadishu
- **WikiData ID:** Q10326669
- **Type:** region
- **Note:** Whether Maroodi Jeex covers the same ground as ISO's Woqooyi Galbeed is under review; the record stays under Somalia (SO). See [DISPUTED_AND_SPECIAL_TERRITORIES.md](../../DISPUTED_AND_SPECIAL_TERRITORIES.md)

### Cities Added

#### Sool Region Cities (3)

1. **Las Anod** (Capital of Sool)
   - **ID:** 160112
   - **Native Name:** Laascaanood
   - **Coordinates:** 8.476°N, 47.357°E
   - **WikiData:** Q1017223
   - **State ID:** 5699
   - **State Code:** SO

2. **Aynaba**
   - **ID:** 160113
   - **Native Name:** Caynabo
   - **Coordinates:** 8.950°N, 46.417°E
   - **WikiData:** Q4058907
   - **State ID:** 5699
   - **State Code:** SO

3. **Hudun**
   - **ID:** 160114
   - **Native Name:** Xudun
   - **Coordinates:** 9.154°N, 47.477°E
   - **WikiData:** Q3388333
   - **State ID:** 5699
   - **State Code:** SO

#### Woqooyi Galbeed Region Cities (2)

1. **Hargeisa** (Capital of Woqooyi Galbeed/Maroodi Jeex)
   - **ID:** 160115
   - **Native Name:** Hargeysa
   - **Coordinates:** 9.563°N, 44.067°E
   - **WikiData:** Q168652
   - **State ID:** 5700
   - **State Code:** WO
   - **Note:** Hargeisa is the second-largest city in Somalia

2. **Gabiley**
   - **ID:** 160116
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
  "id": 160112,
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
  "id": 160115,
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
6. Assigned city IDs (see the note at the top for their actual ids)
7. Added proper timezone (Africa/Mogadishu) for all entries
8. Validated JSON structure and data completeness

### ID Assignment
- **State IDs:** Manually assigned sequential IDs (5699, 5700) after finding max existing ID (5698)
- **City IDs:** current ids 160112-160116; the original merge used 157165-157169 (see the note at the top). The
  104821-104825 first written here were never their ids.
- **Timestamps:** Auto-generated in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)

### Translation Note
The original note described automatic Wikipedia enrichment. From 13 October 2026, new or reviewed translations follow
the attested same-place rule in [contributions/README.md](../../contributions/README.md#names-native-names-and-translations).
Do not rerun `translation_enricher.py` until its sources and identity checks are reviewed.

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

### Woqooyi Galbeed naming and catalogue scope
State 5700 keeps the ISO catalogue name Woqooyi Galbeed and code SO-WO. Its `native` value is Maroodi Jeex, a name used
by the Somaliland administration. Whether that administrative unit covers the same ground as the ISO unit is under
review; the value is not treated as proof of a rename with unchanged boundaries.

### Territorial context
The database stores these regional catalogue entries and their places under SO. This does not decide recognition,
sovereignty or present control; ISO catalogue names, locally used names and current boundaries are checked separately.
See [Disputed and special territories](../../DISPUTED_AND_SPECIAL_TERRITORIES.md).

## Compliance Checklist

✅ Matches ISO 3166-2:SO standard (18 regions)  
✅ Includes proper WikiData IDs for all new entries  
✅ Follows existing data structure and formatting  
✅ Includes regional capitals (Las Anod, Hargeisa)  
✅ Proper timezone (Africa/Mogadishu) assigned  
✅ Coordinates verified from Wikipedia  
✅ Native names included for all entries  
✅ JSON structure validated  
⏳ Further translations need attested same-place names under the current contribution rule

## Further work
This is a historical import note. Further corrections follow the current contribution, naming, source-rights and
release rules; the old automated translation-enrichment plan is superseded.
