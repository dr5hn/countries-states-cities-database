# Bosnia and Herzegovina: Remove Extra Cantons

## Issue Reference
**Issue:** [Data]: Bosnia and Herzegovina remove extra canton  
**Problem:** Bosnia and Herzegovina has 13 administrative divisions in the database, but according to ISO 3166-2:BA, it should only have 3: 1 district (Brčko) and 2 entities (Federation of Bosnia and Herzegovina, Republika Srpska). The 10 cantons are subdivisions of the Federation entity and should not be listed as top-level administrative divisions.

## Countries/Regions Addressed
- Bosnia and Herzegovina (BA)

## Changes Made

### States
**Before:** 13 administrative divisions (1 district + 2 entities + 10 cantons)  
**After:** 3 administrative divisions (1 district + 2 entities)  

**Removed cantons (10):**
1. Tuzla (id: 461, BA-03)
2. Central Bosnia (id: 462, BA-06)
3. Herzegovina-Neretva (id: 463, BA-07)
4. Posavina (id: 464, BA-02)
5. Una-Sana (id: 465, BA-01)
6. Sarajevo (id: 466, BA-09)
7. Zenica-Doboj (id: 468, BA-04)
8. West Herzegovina (id: 469, BA-08)
9. Canton 10 (id: 471, BA-10)
10. Bosnian Podrinje (id: 472, BA-05)

**Remaining administrative divisions (matching ISO 3166-2:BA):**
1. Brčko district - BA-BRC (id: 460, type: district)
2. Federation of Bosnia and Herzegovina - BA-BIH (id: 467, type: entity)
3. Republika Srpska - BA-SRP (id: 470, type: entity)

### Cities
**No city reassignment needed:**
- All 232 cities in BA.json already reference only the 3 valid state IDs (460, 467, 470)
- No cities were using the canton state IDs that were removed
- No orphaned cities after canton removal

## Validation Steps

### 1. JSON File Validation
```bash
# Validate JSON syntax
jq empty contributions/states/states.json && echo "states.json is valid JSON"
jq empty contributions/cities/BA.json && echo "BA.json is valid JSON"
```
**Result:** ✅ Both files validated successfully

### 2. State Count Verification
```bash
# Count Bosnia and Herzegovina states
jq '[.[] | select(.country_code == "BA")] | length' contributions/states/states.json
```
**Result:** 3 administrative divisions (previously 13)

### 3. State Details Verification
```bash
# List all Bosnia and Herzegovina administrative divisions
jq '[.[] | select(.country_code == "BA")] | map({id: .id, name: .name, type: .type, iso3166_2: .iso3166_2})' contributions/states/states.json
```
**Result:**
```json
[
  {
    "id": 460,
    "name": "Brčko",
    "type": "district",
    "iso3166_2": "BA-BRC"
  },
  {
    "id": 467,
    "name": "Federation of Bosnia and Herzegovina",
    "type": "entity",
    "iso3166_2": "BA-BIH"
  },
  {
    "id": 470,
    "name": "Republika Srpska",
    "type": "entity",
    "iso3166_2": "BA-SRP"
  }
]
```

### 4. City Reference Verification
```bash
# Get unique state IDs referenced by cities
jq '[.[] | .state_id] | unique | sort' contributions/cities/BA.json

# Verify valid state IDs
jq '[.[] | select(.country_code == "BA") | .id] | sort' contributions/states/states.json
```
**Result:**
- Cities reference: [460, 467, 470]
- Valid state IDs: [460, 467, 470]
- ✅ All city references are valid (no orphaned cities)

### 5. Total State Count
```bash
# Count total states in database
jq 'length' contributions/states/states.json
```
**Result:** 5,216 states (previously 5,226 - reduced by 10)

## Data Samples

### Example of Removed Canton Entry (Tuzla)
```json
{
  "id": 461,
  "name": "Tuzla",
  "country_id": 28,
  "country_code": "BA",
  "fips_code": "BRC",
  "iso2": "03",
  "iso3166_2": "BA-03",
  "type": "canton",
  "level": null,
  "parent_id": null,
  "native": "Tuzla",
  "latitude": "44.53842300",
  "longitude": "18.66709200",
  "timezone": "Europe/Sarajevo",
  "wikiDataId": "Q18252"
}
```
*This entry and 9 other cantons were completely removed from contributions/states/states.json*

### Retained Entity Entry (Federation of Bosnia and Herzegovina)
```json
{
  "id": 467,
  "name": "Federation of Bosnia and Herzegovina",
  "country_id": 28,
  "country_code": "BA",
  "fips_code": "01",
  "iso2": "BIH",
  "iso3166_2": "BA-BIH",
  "type": "entity",
  "level": null,
  "parent_id": null,
  "native": "Federacija Bosne i Hercegovine",
  "latitude": "43.91674100",
  "longitude": "17.54820720",
  "timezone": "Europe/Sarajevo",
  "wikiDataId": "Q11198"
}
```

## References
- **ISO 3166-2:BA:** https://www.iso.org/obp/ui#iso:code:3166:BA
- **Wikipedia - Subdivisions of Bosnia and Herzegovina:** https://en.wikipedia.org/wiki/Bosnia_and_Herzegovina
- **WikiData - Federation of Bosnia and Herzegovina:** https://www.wikidata.org/wiki/Q11198
- **WikiData - Republika Srpska:** https://www.wikidata.org/wiki/Q11196
- **WikiData - Brčko District:** https://www.wikidata.org/wiki/Q209896

## Impact
- **Database structure:** States count for Bosnia and Herzegovina reduced from 13 to 3
- **Total states:** Global state count reduced from 5,226 to 5,216
- **API changes:** Any queries filtering by canton codes (BA-01 through BA-10) will now return no results
- **Data integrity:** All Bosnia and Herzegovina data now matches official ISO 3166-2:BA standard
- **Breaking changes:** Applications referencing removed canton state IDs (461-466, 468-469, 471-472) will need to update to entity IDs (467 or 470) or district ID (460)
- **Data quality:** ✅ Improved - database now accurately reflects ISO 3166-2 standard administrative divisions
- **Cities impact:** ✅ No impact - all 232 cities were already referencing the correct entities/district

## Notes
According to ISO 3166-2:BA standard, Bosnia and Herzegovina has only 3 first-level administrative divisions:
1. **Brčko District (BA-BRC)** - Special administrative unit with its own government
2. **Federation of Bosnia and Herzegovina (BA-BIH)** - One of two entities, which is internally divided into 10 cantons
3. **Republika Srpska (BA-SRP)** - The other entity

The 10 cantons (Una-Sana, Posavina, Tuzla, Zenica-Doboj, Bosnian Podrinje, Central Bosnia, Herzegovina-Neretva, West Herzegovina, Sarajevo, and Canton 10) are second-level subdivisions within the Federation entity and should not be included as top-level administrative divisions in this database. This fix aligns the database with the official ISO 3166-2:BA standard.
