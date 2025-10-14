# Fix: Ethiopia Missing States (Sidama and Southwest Ethiopia Peoples)

## Issue Reference
- **Issue**: [Data]: Ethiopia state missing
- **Reporter**: Community
- **Date**: 2025-10-14

## Executive Summary
Added two missing regional states to Ethiopia's administrative divisions to match the ISO 3166-2:ET standard. Ethiopia now has the complete set of 13 administrative divisions (11 regional states + 2 administrations).

## Problem Description
The database had only 11 out of 13 Ethiopian administrative divisions according to ISO 3166-2:ET standard. Two recently formed regional states were missing:
1. **Sidama** (ET-SI) - Regional State
2. **Southwest Ethiopia Peoples** (ET-SW) - Regional State

## Changes Made

### States Added

#### 1. Sidama Regional State (ET-SI)
- **Name**: Sidama
- **ISO Code**: ET-SI
- **Type**: Regional State
- **Capital**: Hawassa
- **Coordinates**: 6.5°N, 38.5°E
- **Timezone**: Africa/Addis_Ababa
- **WikiData ID**: Q30107894
- **Formation Date**: 2020 (separated from Southern Nations, Nationalities and Peoples Region)
- **Source**: https://en.wikipedia.org/wiki/Sidama_Region

#### 2. Southwest Ethiopia Peoples Regional State (ET-SW)
- **Name**: Southwest Ethiopia Peoples
- **ISO Code**: ET-SW
- **Type**: Regional State
- **Capital**: Bonga
- **Coordinates**: 7.3°N, 36.2°E
- **Timezone**: Africa/Addis_Ababa
- **WikiData ID**: Q105085548
- **Formation Date**: 2021 (separated from Southern Nations, Nationalities and Peoples Region)
- **Source**: https://en.wikipedia.org/wiki/South_West_Ethiopia_Peoples%27_Region

### Complete List of Ethiopian Administrative Divisions (After Fix)

| Code | Name | Type |
|------|------|------|
| ET-AA | Addis Ababa | Administration |
| ET-AF | Afar | Regional State |
| ET-AM | Amhara | Regional State |
| ET-BE | Benishangul-Gumuz | Regional State |
| ET-DD | Dire Dawa | Administration |
| ET-GA | Gambela Peoples | Regional State |
| ET-HA | Harari People | Regional State |
| ET-OR | Oromia | Regional State |
| ET-SI | **Sidama** | **Regional State** ← NEW |
| ET-SN | Southern Nations, Nationalities and Peoples | Regional State |
| ET-SO | Somali | Regional State |
| ET-SW | **Southwest Ethiopia Peoples** | **Regional State** ← NEW |
| ET-TI | Tigrai | Regional State |

**Total**: 11 Regional States + 2 Administrations = **13 Administrative Divisions** ✅

## Validation

### Before Fix
```bash
jq '[.[] | select(.country_code == "ET")] | length' contributions/states/states.json
# Output: 11
```

### After Fix
```bash
jq '[.[] | select(.country_code == "ET")] | length' contributions/states/states.json
# Output: 13
```

### ISO 3166-2:ET Compliance
All 13 administrative divisions from ISO 3166-2:ET are now present in the database.

## Cities Note

### Cities Currently in SNNPR That May Need Reassignment

Several cities are currently assigned to Southern Nations, Nationalities and Peoples Region (ET-SN) that may belong to the new regions:

#### Potential Sidama Region Cities (Based on Coordinates)
- Hawassa (capital) - 7.06°N, 38.48°E
- Dīla - 6.42°N, 38.32°E
- Hāgere Selam - 6.48°N, 38.52°E
- Yirga 'Alem - 6.75°N, 38.42°E
- Wendo - 6.60°N, 38.42°E
- Leku - 6.87°N, 38.44°E
- Sidama Zone - 6.72°N, 38.45°E

#### Potential Southwest Ethiopia Peoples Cities (Based on Coordinates)
- Bonga (capital) - 7.28°N, 36.23°E
- Mīzan Teferī - 6.99°N, 35.59°E
- Tippi - 7.20°N, 35.45°E
- Bench Maji Zone - 6.46°N, 35.31°E
- Sheka Zone - 7.56°N, 35.40°E

**Note**: City reassignments should be done in a future PR after the new states are imported to MySQL and assigned IDs. The cities need to be updated with the correct `state_id` values once available.

## Implementation Details

### File Modified
- `contributions/states/states.json`

### Approach
- Added two new state entries without `id` field (will be auto-assigned during MySQL import)
- Included comprehensive translations for 18 languages
- Used WikiData IDs for reference
- Set proper timezone (Africa/Addis_Ababa)
- Followed existing data structure and conventions

### Data Sources
- ISO 3166-2:ET standard: https://www.iso.org/obp/ui#iso:code:3166:ET
- Wikipedia - Regions of Ethiopia: https://en.wikipedia.org/wiki/Regions_of_Ethiopia
- Wikipedia - Sidama Region: https://en.wikipedia.org/wiki/Sidama_Region
- Wikipedia - Southwest Ethiopia Peoples Region: https://en.wikipedia.org/wiki/South_West_Ethiopia_Peoples%27_Region

## Future Work
1. After MySQL import assigns IDs to new states, reassign cities from SNNPR to their correct regions
2. Add additional cities for these regions if needed
3. Verify administrative boundaries based on official sources

## Testing
- ✅ JSON syntax validation passed
- ✅ Total state count increased from 11 to 13
- ✅ All ISO codes properly formatted (ET-SI, ET-SW)
- ✅ No duplicate ISO codes
- ✅ Translations included for consistency
- ✅ WikiData IDs verified

## Conclusion
Ethiopia's administrative divisions are now complete and compliant with ISO 3166-2:ET standard. The database accurately represents all 13 administrative divisions as of 2025.
