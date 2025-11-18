# Fix Summary: Pakistan - Remove Federally Administered Tribal Areas (FATA)

## Issue Reference
**Original Issue:** [Bug]: Pakistan remove extra administered area
**Issue Link:** GitHub Issue (Remove 1 extra administered area - FATA merged with Khyber Pakhtunkhwa)

## Executive Summary

This PR corrects Pakistan's administrative divisions to align with ISO 3166-2:PK standards by removing the deprecated "Federally Administered Tribal Areas" (FATA) and merging its cities into Khyber Pakhtunkhwa province.

### Historical Context

The Federally Administered Tribal Areas (FATA) was a semi-autonomous tribal region in northwestern Pakistan. In 2018, FATA was officially merged with the Khyber Pakhtunkhwa province through the 25th Constitutional Amendment, eliminating it as a separate administrative division.

---

## Changes Made

### Pakistan 🇵🇰

**Problem:** Database contained 8 administrative divisions including the deprecated FATA (PK-TA), which was merged with Khyber Pakhtunkhwa in 2018.

**Solution:** 
1. Removed FATA state record from `contributions/states/states.json`
2. Moved all 8 cities from FATA to Khyber Pakhtunkhwa
3. Updated city records with correct state_id and state_code

**Details:**

**Before:**
- 8 administrative divisions (including deprecated FATA)
- FATA (state_id: 3173, state_code: TA) had 8 cities
- Khyber Pakhtunkhwa (state_id: 3171, state_code: KP) had 49 cities

**After:**
- 7 administrative divisions (per ISO 3166-2:PK)
- FATA removed completely
- Khyber Pakhtunkhwa now has 57 cities (49 + 8 merged)

---

## Current Administrative Structure (ISO 3166-2:PK Compliant)

### 7 Administrative Divisions:

| Code   | Name                     | Type                      | State ID |
|--------|--------------------------|---------------------------|----------|
| PK-JK  | Azad Kashmir             | Administered Area         | 3172     |
| PK-BA  | Balochistan              | Province                  | 3174     |
| PK-GB  | Gilgit-Baltistan         | Administered Area         | 3170     |
| PK-IS  | Islamabad                | Federal Capital Territory | 3169     |
| PK-KP  | Khyber Pakhtunkhwa       | Province                  | 3171     |
| PK-PB  | Punjab                   | Province                  | 3176     |
| PK-SD  | Sindh                    | Province                  | 3175     |

---

## Cities Merged from FATA to Khyber Pakhtunkhwa

The following 8 cities were moved from FATA (state_id: 3173) to Khyber Pakhtunkhwa (state_id: 3171):

1. **Alizai** (id: 85336)
   - Coordinates: 33.53613°N, 70.34607°E
   - Native: علیزئی
   - WikiData: Q2475251

2. **Gulishah Kach** (id: 85458)
   - Coordinates: 32.67087°N, 70.33917°E
   - Native: گلشاہ کیچ
   - WikiData: Q243322

3. **Landi Kotal** (id: 85577)
   - Coordinates: 34.09880°N, 71.14108°E
   - Native: لنڈی کوتل
   - WikiData: Q1803018

4. **Miran Shah** (id: 85611)
   - Coordinates: 33.00059°N, 70.07117°E
   - Native: میران شاہ
   - WikiData: Q124385

5. **North Wazīristān Agency** (id: 85645)
   - Coordinates: 32.95087°N, 69.95764°E
   - Native: شمالی وزیرستان ایجنسی
   - WikiData: Q2579925

6. **Shinpokh** (id: 85717)
   - Coordinates: 34.32959°N, 71.17852°E
   - Native: شن پوکھ
   - WikiData: Q1250069

7. **South Wazīristān Agency** (id: 85728)
   - Coordinates: 32.30397°N, 69.68207°E
   - Native: جنوبی وزیرستان ایجنسی
   - WikiData: Q7635235

8. **Wana** (id: 85764)
   - Coordinates: 32.29889°N, 69.57250°E
   - Native: وانا
   - WikiData: Q1026635

---

## Validation

### Database Integrity
- ✅ Pakistan now has exactly 7 administrative divisions (per ISO 3166-2:PK)
- ✅ All 8 former FATA cities successfully merged to Khyber Pakhtunkhwa
- ✅ No cities reference the deleted FATA state (state_id: 3173)
- ✅ All state_code values updated from "TA" to "KP"
- ✅ All foreign key references (country_id, state_id) remain valid
- ✅ JSON structure valid and consistent

### MySQL Database
- ✅ States table: 7 Pakistan states (confirmed via query)
- ✅ Cities table: 0 cities with state_id 3173 (FATA removed)
- ✅ Cities table: 57 cities with state_id 3171 (Khyber Pakhtunkhwa)
- ✅ Import/Export sync successful

### ISO 3166-2 Compliance
- ✅ Matches official ISO 3166-2:PK subdivision codes
- ✅ Aligns with Pakistan's 2018 constitutional amendment
- ✅ Reflects current administrative reality

---

## Technical Implementation

### Files Modified
1. **contributions/states/states.json**
   - Removed: 1 state (FATA, id: 3173)
   - Pakistan states: 8 → 7

2. **contributions/cities/PK.json**
   - Updated: 8 cities (changed state_id from 3173 to 3171)
   - Updated: 8 cities (changed state_code from "TA" to "KP")
   - Total Pakistan cities: 457 (unchanged)

### Commands Used
```bash
# Update cities from FATA to Khyber Pakhtunkhwa
jq 'map(if .state_id == 3173 then .state_id = 3171 | .state_code = "KP" else . end)' \
  contributions/cities/PK.json > /tmp/PK_updated.json

# Remove FATA state
jq 'map(select(.id != 3173))' contributions/states/states.json > /tmp/states_updated.json

# Import to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py --password root

# Sync back to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py --password root
```

---

## Sources & References

- **ISO 3166-2:PK:** https://www.iso.org/obp/ui#iso:code:3166:PK
- **Wikipedia - Pakistan:** https://en.wikipedia.org/wiki/Pakistan
- **Wikipedia - FATA:** https://en.wikipedia.org/wiki/Federally_Administered_Tribal_Areas
- **25th Constitutional Amendment (2018):** https://en.wikipedia.org/wiki/Twenty-fifth_Amendment_to_the_Constitution_of_Pakistan

---

## Quality Assurance

### Pre-Fix Verification
```sql
-- Before: 8 Pakistan states
SELECT COUNT(*) FROM states WHERE country_code = 'PK';  -- Result: 8

-- Before: 8 FATA cities
SELECT COUNT(*) FROM cities WHERE state_id = 3173;  -- Result: 8

-- Before: 49 Khyber Pakhtunkhwa cities
SELECT COUNT(*) FROM cities WHERE state_id = 3171;  -- Result: 49
```

### Post-Fix Verification
```sql
-- After: 7 Pakistan states
SELECT COUNT(*) FROM states WHERE country_code = 'PK';  -- Result: 7

-- After: 0 FATA cities
SELECT COUNT(*) FROM cities WHERE state_id = 3173;  -- Result: 0

-- After: 57 Khyber Pakhtunkhwa cities
SELECT COUNT(*) FROM cities WHERE state_id = 3171;  -- Result: 57
```

---

## Impact Assessment

- **Data Accuracy:** ✅ High - Aligns with official ISO 3166-2 standards
- **Breaking Changes:** ⚠️ Minimal - Applications relying on FATA state_id 3173 will need updates
- **Migration Path:** State_id 3173 removed; use state_id 3171 (Khyber Pakhtunkhwa) instead
- **API Impact:** State queries for PK-TA will return no results (expected)

---

## Conclusion

This fix ensures the database accurately reflects Pakistan's current administrative structure as defined by ISO 3166-2:PK and the 2018 constitutional amendment merging FATA with Khyber Pakhtunkhwa. All 8 cities previously assigned to FATA are now correctly associated with Khyber Pakhtunkhwa province.
