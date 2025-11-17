# Fix: Botswana Administrative Divisions (ISO 3166-2:BW Compliance)

## Issue Reference
- **Issue**: [Data]: Botswana district, town and city missing
- **Date**: 2025-11-17
- **Source**: ISO 3166-2:BW standard

## Problem Statement

Botswana's administrative divisions were incomplete and contained one incorrect entry:

### Issues Identified
1. **Missing 1 District**: Chobe (BW-CH) was not in the database
2. **Missing 2 Cities**: Francistown (BW-FR) and Gaborone (BW-GA) were not in the database
3. **Missing 4 Towns**: Jwaneng (BW-JW), Lobatse (BW-LO), Selibe Phikwe (BW-SP), and Sowa Town (BW-ST) were not in the database
4. **Incorrect Entry**: Ngamiland (BW-NG) was marked as "city" type but is not a valid administrative division per ISO 3166-2:BW

### Before Fix
- **Total entries**: 10
  - 9 districts
  - 1 incorrect entry (Ngamiland marked as "city")
  - 0 cities
  - 0 towns

### After Fix
- **Total entries**: 16
  - 10 districts (including new Chobe)
  - 2 cities (Francistown, Gaborone)
  - 4 towns (Jwaneng, Lobatse, Selibe Phikwe, Sowa Town)

## Changes Made

### 1. Removed Incorrect Entry
**Ngamiland (BW-NG)**
- **Reason**: Not a valid administrative division per ISO 3166-2:BW
- **Type**: Was incorrectly marked as "city"
- **Action**: Removed from states.json

### 2. Added District

**Chobe (BW-CH)**
- **Type**: District
- **ID**: 5710 (auto-assigned)
- **ISO Code**: BW-CH
- **Coordinates**: -18.50000000, 25.00000000
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q165536
- **Translations**: 11 languages
- **Source**: https://en.wikipedia.org/wiki/Chobe_District

### 3. Added Cities

**Francistown (BW-FR)**
- **Type**: City
- **ID**: 5711 (auto-assigned)
- **ISO Code**: BW-FR
- **Coordinates**: -21.17361111, 27.51250000
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q165422
- **Translations**: 19 languages
- **Source**: https://en.wikipedia.org/wiki/Francistown

**Gaborone (BW-GA)**
- **Type**: City (Capital of Botswana)
- **ID**: 5712 (auto-assigned)
- **ISO Code**: BW-GA
- **Coordinates**: -24.65805556, 25.91222222
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q3919
- **Translations**: 20 languages
- **Source**: https://en.wikipedia.org/wiki/Gaborone

### 4. Added Towns

**Jwaneng (BW-JW)**
- **Type**: Town
- **ID**: 5713 (auto-assigned)
- **ISO Code**: BW-JW
- **Coordinates**: -24.60194444, 24.72833333
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q165954
- **Translations**: 15 languages
- **Source**: https://en.wikipedia.org/wiki/Jwaneng

**Lobatse (BW-LO)**
- **Type**: Town
- **ID**: 5714 (auto-assigned)
- **ISO Code**: BW-LO
- **Coordinates**: -25.21666667, 25.66666667
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q165768
- **Translations**: 19 languages
- **Source**: https://en.wikipedia.org/wiki/Lobatse

**Selibe Phikwe (BW-SP)**
- **Type**: Town
- **ID**: 5715 (auto-assigned)
- **ISO Code**: BW-SP
- **Coordinates**: -21.97583333, 27.84000000
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q141263
- **Translations**: 19 languages
- **Source**: https://en.wikipedia.org/wiki/Selebi-Phikwe

**Sowa Town (BW-ST)**
- **Type**: Town
- **ID**: 5716 (auto-assigned)
- **ISO Code**: BW-ST
- **Coordinates**: -20.56361111, 26.22444444
- **Timezone**: Africa/Gaborone
- **WikiData ID**: Q141310
- **Translations**: 9 languages
- **Source**: https://en.wikipedia.org/wiki/Sowa,_Botswana

## Validation Steps

### 1. ISO 3166-2:BW Compliance
✅ Verified against official ISO standard at https://www.iso.org/obp/ui#iso:code:3166:BW

All 16 administrative divisions now match the ISO 3166-2:BW standard:
- 10 districts (BW-CE, BW-CH, BW-GH, BW-KG, BW-KL, BW-KW, BW-NE, BW-NW, BW-SE, BW-SO)
- 2 cities (BW-FR, BW-GA)
- 4 towns (BW-JW, BW-LO, BW-SP, BW-ST)

### 2. Data Quality Checks
✅ All entries have required fields:
- name, country_id, country_code, type, latitude, longitude

✅ All entries have enriched data:
- timezone (Africa/Gaborone for all)
- translations (9-20 languages per entry)
- wikiDataId (verified on Wikidata)

✅ All coordinates verified from Wikipedia

### 3. Database Validation
```sql
-- Verify count by type
SELECT type, COUNT(*) 
FROM states 
WHERE country_code = 'BW' 
GROUP BY type 
ORDER BY type;

-- Result:
-- city      | 2
-- district  | 10
-- town      | 4
```

### 4. No Orphaned Cities
✅ Verified that no cities reference the removed Ngamiland (id: 3060)
```bash
jq '.[] | select(.state_id == 3060)' contributions/cities/BW.json
# Result: (empty - no orphaned cities)
```

## Sources
1. **ISO 3166-2:BW**: https://www.iso.org/obp/ui#iso:code:3166:BW
2. **Wikipedia - Botswana**: https://en.wikipedia.org/wiki/Botswana
3. **Wikipedia - Chobe District**: https://en.wikipedia.org/wiki/Chobe_District
4. **Wikipedia - Francistown**: https://en.wikipedia.org/wiki/Francistown
5. **Wikipedia - Gaborone**: https://en.wikipedia.org/wiki/Gaborone
6. **Wikipedia - Jwaneng**: https://en.wikipedia.org/wiki/Jwaneng
7. **Wikipedia - Lobatse**: https://en.wikipedia.org/wiki/Lobatse
8. **Wikipedia - Selebi-Phikwe**: https://en.wikipedia.org/wiki/Selebi-Phikwe
9. **Wikipedia - Sowa**: https://en.wikipedia.org/wiki/Sowa,_Botswana
10. **Wikidata**: https://www.wikidata.org/

## Files Modified
- `contributions/states/states.json`: Removed 1 entry, added 7 entries
- `bin/db/schema.sql`: Auto-updated by sync script

## Technical Details

### Workflow Used
1. ✅ Manually edited `contributions/states/states.json`:
   - Removed Ngamiland (id: 3060)
   - Added 7 new entries (without IDs)
2. ✅ Imported JSON to MySQL to auto-assign IDs
3. ✅ Added timezones using `add_timezones.py --table states`
4. ✅ Added translations using Wikipedia API language links
5. ✅ Re-imported to MySQL to update translations
6. ✅ Validated all changes

### Translation Coverage
All new entries have translations in major languages:
- Arabic (ar), German (de), Spanish (es), French (fr)
- Hindi (hi), Italian (it), Japanese (ja), Korean (ko)
- Dutch (nl), Polish (pl), Portuguese (pt, pt-BR)
- Russian (ru), Turkish (tr), Ukrainian (uk)
- Chinese (zh, zh-CN), Croatian (hr), Persian (fa), Breton (br)

## Summary
This fix brings Botswana's administrative divisions into full compliance with the ISO 3166-2:BW standard by:
- Removing 1 incorrect entry (Ngamiland)
- Adding 1 missing district (Chobe)
- Adding 2 cities (Francistown, Gaborone)
- Adding 4 towns (Jwaneng, Lobatse, Selibe Phikwe, Sowa Town)

All new entries include complete data: coordinates, timezones, WikiData IDs, and translations in 9-20 languages.
