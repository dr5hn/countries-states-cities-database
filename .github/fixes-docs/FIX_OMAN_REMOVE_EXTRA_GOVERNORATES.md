# Fix: Oman - Remove Extra Governorates

## Issue Reference
**Issue**: [Bug]: Oman remove extra governorate
**Date**: November 18, 2025

## Problem Statement
Oman had 13 governorates in the database but should only have 11 according to ISO 3166-2:OM standard.

### Extra Governorates (Removed)
1. **Al Batinah Region** (BA, state_id=3050)
2. **Ash Sharqiyah Region** (SH, state_id=3051)

These were historical regional divisions that have been replaced by more specific North/South governorates.

## Solution

### 1. Cities Reassigned

#### Al Batinah Region → Al Batinah South (BJ)
4 cities moved from state_id 3050 (BA) to state_id 3049 (BJ):
- Barkā'
- Bayt al 'Awābī
- Oman Smart Future City
- Rustaq

#### Ash Sharqiyah Region → Ash Sharqiyah South (SJ)
1 city moved from state_id 3051 (SH) to state_id 3054 (SJ):
- Sur

### 2. States Removed
Removed 2 obsolete governorates from `contributions/states/states.json`:
- Al Batinah Region (OM-BA)
- Ash Sharqiyah Region (OM-SH)

## Final Governorate Structure (11 Total)

According to ISO 3166-2:OM:

| Code | Name | Cities |
|------|------|--------|
| OM-BJ | Al Batinah South (Janub al Batinah) | 4 |
| OM-BS | Al Batinah North (Shamal al Batinah) | 6 |
| OM-BU | Al Buraimi | 1 |
| OM-DA | Ad Dakhiliyah | 6 |
| OM-MA | Muscat (Masqat) | 3 |
| OM-MU | Musandam | 3 |
| OM-SJ | Ash Sharqiyah South (Janub ash Sharqiyah) | 1 |
| OM-SS | Ash Sharqiyah North (Shamal ash Sharqiyah) | 0 |
| OM-WU | Al Wusta | 1 |
| OM-ZA | Ad Dhahirah (Az Zahirah) | 2 |
| OM-ZU | Dhofar (Zufar) | 1 |

**Total**: 11 governorates, 28 cities

## Changes Made

### Files Modified
1. `contributions/cities/OM.json`
   - Updated state_code and state_id for 5 cities

2. `contributions/states/states.json`
   - Removed 2 obsolete governorate entries

3. `bin/db/schema.sql`
   - Updated timestamp (auto-generated during sync)

### Validation Steps
1. ✅ Verified JSON syntax validity
2. ✅ Imported changes to MySQL database
3. ✅ Synced MySQL back to JSON to ensure consistency
4. ✅ Confirmed 11 governorates in database (was 13)
5. ✅ Verified all cities have valid state references
6. ✅ Confirmed no orphaned cities

## Sources
- **ISO 3166-2:OM**: https://www.iso.org/obp/ui#iso:code:3166:OM
- **Wikipedia**: https://en.wikipedia.org/wiki/Governorates_of_Oman

## Notes
- This change aligns the database with the current administrative structure of Oman
- The ISO standard uses asterisks (*) for the 11 official governorates
- Historical regional divisions (BA and SH) were broader administrative areas that have been subdivided
- All city data has been preserved and reassigned to the appropriate South governorate
