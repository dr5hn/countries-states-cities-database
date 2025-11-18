# Maldives Administrative Divisions Fix - ISO 3166-2:MV Compliance

## Issue Reference
**Title:** [Bug]: Maldives remove province  
**Problem:** Maldives had 5 extra provinces that are not part of the ISO 3166-2:MV standard. According to ISO, Maldives should have only 2 cities and 19 administrative atolls.

## Countries/Regions Addressed
- Maldives (MV)

## Changes Made

### 1. Removed 5 Non-Standard Provinces

The following provinces were removed as they are not part of ISO 3166-2:MV:

| ID | Name | ISO Code | Type |
|---|---|---|---|
| 2589 | North Central | MV-NC | Province |
| 2593 | Upper South | MV-US | Province |
| 2604 | Central | MV-CE | Province |
| 2605 | South | MV-SU | Province |
| 2606 | South Central | MV-SC | Province |

### 2. Changed Malé from Administrative Atoll to City

- **State:** Malé (ID: 2609)
- **Before:** Type = "administrative atoll"
- **After:** Type = "city"
- **ISO Code:** MV-MLE
- **Justification:** According to ISO 3166-2:MV, Malé is classified as a City, not an administrative atoll

### 3. Added Missing Baa Atoll (South Maalhosmadulu)

This atoll was completely missing from the database:

- **Name:** Baa
- **ISO Code:** MV-20
- **Type:** Administrative Atoll
- **ID:** 5727 (auto-assigned by MySQL)
- **Coordinates:** 5.13333333, 72.95000000
- **WikiData ID:** Q949513
- **Timezone:** Indian/Maldives
- **Native Name:** ބ އަތޮޅު
- **Translations:** Added 14 languages (ar, de, es, fr, id, it, ko, nl, pl, pt, ru, zh, ja, hi)

### 4. Moved Mahibadhoo City

The city Mahibadhoo was assigned to the now-removed "South Central" province and needed to be reassigned:

- **City:** Mahibadhoo (ID: 67934)
- **Before:** state_id = 2606 (South Central, SC)
- **After:** state_id = 2600 (Alif Dhaal, 00)
- **Justification:** South Central province was removed; Mahibadhoo belongs to Alif Dhaal atoll

### Summary Statistics

| Metric | Before | After | Change |
|---|---|---|---|
| Total Maldives States | 25 | 21 | -4 |
| Cities | 1 | 2 | +1 |
| Administrative Atolls | 19 | 19 | 0 |
| Provinces | 5 | 0 | -5 |

**Net Effect:** Removed 5 provinces, added 1 missing atoll, changed 1 atoll to city = -4 total states

## Validation Steps

### 1. Verified ISO 3166-2:MV Compliance

Cross-referenced all administrative divisions against the official ISO standard from https://www.iso.org/obp/ui#iso:code:3166:MV

**ISO 3166-2:MV Divisions (21 total):**

| Code | Name | Type | Status |
|---|---|---|---|
| MV-01 | Addu City | City | ✓ |
| MV-02 | North Ari Atoll (Alif Alif) | Administrative Atoll | ✓ |
| MV-03 | Faadhippolhu (Lhaviyani) | Administrative Atoll | ✓ |
| MV-04 | Felidhu Atoll (Vaavu) | Administrative Atoll | ✓ |
| MV-05 | Hahdhunmathi (Laamu) | Administrative Atoll | ✓ |
| MV-07 | North Thiladhunmathi (Haa Alif) | Administrative Atoll | ✓ |
| MV-08 | Kolhumadulu (Thaa) | Administrative Atoll | ✓ |
| MV-12 | Mulaku Atoll (Meemu) | Administrative Atoll | ✓ |
| MV-13 | North Maalhosmadulu (Raa) | Administrative Atoll | ✓ |
| MV-14 | North Nilandhe Atoll (Faafu) | Administrative Atoll | ✓ |
| MV-17 | South Nilandhe Atoll (Dhaalu) | Administrative Atoll | ✓ |
| MV-20 | South Maalhosmadulu (Baa) | Administrative Atoll | ✓ **ADDED** |
| MV-23 | South Thiladhunmathi (Haa Dhaalu) | Administrative Atoll | ✓ |
| MV-24 | North Miladhunmadulu (Shaviyani) | Administrative Atoll | ✓ |
| MV-25 | South Miladhunmadulu (Noonu) | Administrative Atoll | ✓ |
| MV-26 | Male Atoll (Kaafu) | Administrative Atoll | ✓ |
| MV-27 | North Huvadhu Atoll (Gaafu Alif) | Administrative Atoll | ✓ |
| MV-28 | South Huvadhu Atoll (Gaafu Dhaalu) | Administrative Atoll | ✓ |
| MV-29 | Fuvammulah (Gnaviyani) | Administrative Atoll | ✓ |
| MV-00 | South Ari Atoll (Alif Dhaal) | Administrative Atoll | ✓ |
| MV-MLE | Male | City | ✓ |

### 2. MySQL Database Verification

```bash
# Check Maldives state count by type
mysql> SELECT COUNT(*) as count, type FROM states WHERE country_code = 'MV' GROUP BY type;
+-------+----------------------+
| count | type                 |
+-------+----------------------+
|    19 | administrative atoll |
|     2 | city                 |
+-------+----------------------+
```

### 3. JSON File Verification

```bash
# Verify states.json has correct count
$ jq '[.[] | select(.country_code == "MV")] | length' contributions/states/states.json
21

# Verify no provinces remain
$ jq '[.[] | select(.country_code == "MV" and .type == "province")] | length' contributions/states/states.json
0

# Verify Baa atoll was added
$ jq '.[] | select(.country_code == "MV" and .iso2 == "20") | {name, iso2, type, wikiDataId}' contributions/states/states.json
{
  "name": "Baa",
  "iso2": "20",
  "type": "administrative atoll",
  "wikiDataId": "Q949513"
}
```

### 4. Wikipedia Validation for Baa Atoll

- **Wikipedia Article:** https://en.wikipedia.org/wiki/Baa_Atoll
- **WikiData ID:** Q949513
- **Coordinates Verified:** 5.13333333, 72.95 (from Wikipedia API)
- **Also Known As:** Southern Maalhosmadulu Atoll, Maalhosmadulu Dhekunuburi
- **Notable:** UNESCO World Biosphere Reserve since June 2011

## Data Samples

### Removed Province Entry (Example: South Central)

```json
{
  "id": 2606,
  "name": "South Central",
  "country_id": 133,
  "country_code": "MV",
  "iso2": "SC",
  "iso3166_2": "MV-SC",
  "type": "province"
}
```
**Status:** ❌ REMOVED (not in ISO 3166-2:MV)

### Added Baa Atoll Entry

```json
{
  "id": 5727,
  "name": "Baa",
  "country_id": 133,
  "country_code": "MV",
  "fips_code": "",
  "iso2": "20",
  "iso3166_2": "MV-20",
  "type": "administrative atoll",
  "level": 4,
  "parent_id": null,
  "native": "ބ އަތޮޅު",
  "latitude": "5.13333333",
  "longitude": "72.95000000",
  "timezone": "Indian/Maldives",
  "translations": {
    "ar": "آتول با",
    "de": "Baa (Malediven)",
    "es": "Atolón Baa",
    "fr": "Baa (atoll)",
    "id": "Atol Baa",
    "it": "Atollo Baa",
    "ko": "바 환초",
    "nl": "Baa-atol",
    "pl": "Baa",
    "pt": "Baa",
    "ru": "Баа",
    "zh": "巴環礁",
    "ja": "バー環礁",
    "hi": "बा एटोल"
  },
  "wikiDataId": "Q949513"
}
```
**Status:** ✅ ADDED (was missing from database)

### Updated Malé Entry

```json
{
  "id": 2609,
  "name": "Malé",
  "country_id": 133,
  "country_code": "MV",
  "iso2": "MLE",
  "iso3166_2": "MV-MLE",
  "type": "city"
}
```
**Status:** ✅ UPDATED (changed from "administrative atoll" to "city")

### Updated Mahibadhoo City Entry

```json
{
  "id": 67934,
  "name": "Mahibadhoo",
  "state_id": 2600,
  "state_code": "00",
  "country_id": 133,
  "country_code": "MV"
}
```
**Status:** ✅ UPDATED (moved from state_id 2606/SC to 2600/00)

## References

- **ISO 3166-2:MV Official Page:** https://www.iso.org/obp/ui#iso:code:3166:MV
- **Wikipedia - Baa Atoll:** https://en.wikipedia.org/wiki/Baa_Atoll
- **WikiData - Baa Atoll:** https://www.wikidata.org/wiki/Q949513
- **Wikipedia - Administrative divisions of the Maldives:** https://en.wikipedia.org/wiki/Administrative_divisions_of_the_Maldives

## Impact

### Breaking Changes
- **States Removed:** 5 province states (IDs: 2589, 2593, 2604, 2605, 2606) are no longer in the database
- **Type Changed:** Malé (ID: 2609) changed from "administrative atoll" to "city"
- **State Assignment Changed:** Mahibadhoo city (ID: 67934) reassigned from state 2606 to 2600

### API Impact
- Applications relying on the removed province IDs will need to update their references
- Filters for "province" type in Maldives will return empty results
- Malé is now properly categorized as a city

### Data Quality Improvements
- ✅ Full compliance with ISO 3166-2:MV standard
- ✅ Added missing Baa Atoll (19th administrative atoll)
- ✅ Corrected Malé classification from atoll to city
- ✅ All 21 ISO-defined administrative divisions now present
- ✅ Removed non-standard province classifications
- ✅ Proper city reassignment after province removal

## Files Modified

1. `contributions/states/states.json` - Removed 5 provinces, added Baa atoll, updated Malé type
2. `contributions/cities/MV.json` - Updated Mahibadhoo city's state assignment
3. MySQL `states` table - Synced changes via import/sync scripts

## Tools Used

- Python scripts for JSON manipulation
- Wikipedia API for Baa Atoll verification and translations
- MySQL import/sync scripts for database consistency
- ISO 3166-2:MV official standard for validation
