# Saudi Arabia Missing City Fix - Shaqra, Riyadh Province

## Issue Reference
**Title:** [Bug]: Missing Location - Shaqra, Riyadh, Saudi Arabia  
**Problem:** The city of Shaqra was missing from the Riyadh Province in Saudi Arabia

## Executive Summary
Successfully added the missing city of Shaqra to the Riyadh Province (state_id: 2849) of Saudi Arabia.

## Country Addressed
- **Country:** Saudi Arabia (SA)
- **ISO Code:** SA
- **Country ID:** 194

## Changes Made

### City Addition
**File:** `contributions/cities/SA.json`

**Added City:**
- **Name:** Shaqra
- **Native Name:** شقراء
- **State:** Riyadh Province
- **State ID:** 2849
- **State Code:** 01
- **Coordinates:** 25.24833333°N, 45.25277778°E
- **Timezone:** Asia/Riyadh
- **WikiData ID:** Q97291341

## Validation

### Source
- Wikipedia: https://en.wikipedia.org/wiki/Shaqra_(Saudi_Arabia)
- WikiData: https://www.wikidata.org/wiki/Q97291341

### Verification
- Shaqra is a town in central Saudi Arabia, approximately 190 km north-west of Riyadh
- Coordinates confirmed via Wikipedia: 25.248°N, 45.253°E
- Belongs to Riyadh Province (state_id: 2849, iso2: 01, iso3166_2: SA-01)
