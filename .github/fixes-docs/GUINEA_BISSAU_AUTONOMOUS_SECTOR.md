# Guinea-Bissau Autonomous Sector Fix

## Issue Reference
- **Issue**: Guinea-Bissau autonomous sector missing
- **ISO 3166-2 Reference**: https://www.iso.org/obp/ui#iso:code:3166:GW
- **Wikipedia Reference**: https://en.wikipedia.org/wiki/Guinea-Bissau

## Problem
Guinea-Bissau was missing the Bissau autonomous sector (GW-BS) from its administrative divisions. According to ISO 3166-2:GW, Guinea-Bissau consists of:
- 8 regions
- 3 provinces
- 1 autonomous sector (Bissau SAB)

The database only had the 8 regions and 3 provinces.

## Solution

### Added State Entry
Added **Bissau** autonomous sector to `contributions/states/states.json`:
- **ID**: 5553 (auto-assigned by MySQL)
- **Name**: Bissau
- **ISO Code**: GW-BS
- **Type**: autonomous sector
- **Country**: Guinea-Bissau (GW, ID: 93)
- **Coordinates**: 11.85°N, 15.56667°W
- **Timezone**: Africa/Bissau
- **WikiData ID**: Q3739
- **Translations**: Added for 19 languages

### Added City Entry
Added **Bissau** city to `contributions/cities/GW.json`:
- **ID**: 157090 (auto-assigned by MySQL)
- **Name**: Bissau
- **State**: Bissau autonomous sector (BS, ID: 5553)
- **Country**: Guinea-Bissau (GW, ID: 93)
- **Coordinates**: 11.85°N, 15.56667°W
- **Timezone**: Africa/Bissau
- **WikiData ID**: Q3739
- **Translations**: Added for 19 languages

## Validation

### Before
```bash
$ jq '.[] | select(.country_code == "GW") | .type' contributions/states/states.json | sort | uniq -c
      3 "province"
      8 "region"
```

Total: 11 administrative divisions

### After
```bash
$ jq '.[] | select(.country_code == "GW") | .type' contributions/states/states.json | sort | uniq -c
      1 "autonomous sector"
      3 "province"
      8 "region"
```

Total: 12 administrative divisions ✅

### Guinea-Bissau Cities
- **Before**: 14 cities
- **After**: 15 cities (added Bissau capital city)

## Data Quality
All entries include:
- ✅ Required fields (name, country_id, country_code, coordinates)
- ✅ Timezone (Africa/Bissau)
- ✅ Translations (19 languages)
- ✅ WikiData ID (Q3739)
- ✅ Native name

## Changes Made
1. **contributions/states/states.json**: Added Bissau autonomous sector entry
2. **contributions/cities/GW.json**: Added Bissau city entry
3. **MySQL database**: Imported and synced to assign IDs and timestamps

## References
- ISO 3166-2:GW: https://www.iso.org/obp/ui#iso:code:3166:GW
- Wikipedia - Regions of Guinea-Bissau: https://en.wikipedia.org/wiki/Regions_of_Guinea-Bissau
- WikiData - Bissau: https://www.wikidata.org/wiki/Q3739
