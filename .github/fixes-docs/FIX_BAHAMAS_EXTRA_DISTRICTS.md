# Fix: Bahamas - Remove Extra Districts to Match ISO 3166

## Issue Reference
Related to issue: [Data]: Bahamas remove extra district

## Problem Statement
The database contained 42 states/districts for the Bahamas (BS), but according to ISO 3166-2:BS standard, the Bahamas should have only 32 administrative divisions (31 districts + 1 island).

### Source References
- **ISO 3166-2:BS**: https://www.iso.org/obp/ui#iso:code:3166:BS
- **Wikipedia - The Bahamas**: https://en.wikipedia.org/wiki/The_Bahamas
- **Wikipedia - Local Government**: https://en.wikipedia.org/wiki/Local_government_in_the_Bahamas#Districts

## Changes Made

### 1. Removed 11 Extra Districts (No Cities Associated)
The following districts were not part of the official ISO 3166-2 standard and were removed:

| ID   | Name                              | ISO2 | Reason                                    |
|------|-----------------------------------|------|-------------------------------------------|
| 3594 | Nichollstown and Berry Islands    | NB   | Duplicate; "Berry Islands" (BY) exists    |
| 3595 | Green Turtle Cay                  | GT   | Not in ISO standard                       |
| 3597 | Governor's Harbour                | GH   | Not in ISO standard (locality, not district) |
| 3598 | High Rock                         | HR   | Not in ISO standard                       |
| 3604 | Marsh Harbour                     | MH   | Not in ISO standard (locality, not district) |
| 3606 | Sandy Point                       | SP   | Not in ISO standard (locality, not district) |
| 3618 | Kemps Bay                         | KB   | Not in ISO standard                       |
| 3619 | Fresh Creek                       | FC   | Not in ISO standard                       |
| 3620 | San Salvador and Rum Cay          | SR   | Not in ISO standard; separate entries exist |
| 3623 | Rock Sound                        | RS   | Not in ISO standard (locality, not district) |
| 3628 | Acklins and Crooked Islands       | AC   | Not in ISO standard; separate entries exist |

**Verification**: None of these removed districts had any cities associated with them.

### 2. Renamed 3 Districts to Match ISO 3166-2
Updated district names to match official ISO nomenclature:

| Old Name              | New Name                      | ISO2 | Cities |
|----------------------|-------------------------------|------|--------|
| Crooked Island       | Crooked Island and Long Cay   | CK   | 1      |
| Freeport             | City of Freeport              | FP   | 2      |
| San Salvador Island  | San Salvador                  | SS   | 1      |

### 3. Added 1 Missing District
Added the missing district from ISO 3166-2:

| ID   | Name           | ISO2 | Latitude    | Longitude    | Timezone        | WikiData ID |
|------|----------------|------|-------------|--------------|-----------------|-------------|
| 5717 | Moore's Island | MI   | 25.86666700 | -77.96666700 | America/Nassau  | Q2702345    |

**Translations Added**: 20 languages (ar, br, de, es, fa, fi, fr, hi, hr, it, ja, ko, nl, pl, pt, pt-BR, ru, tr, uk, zh-CN)

## Final State Count
- **Before**: 42 states/districts
- **After**: 32 states/districts (31 districts + 1 island)
- **Change**: -10 net (11 removed, 1 added)

## Complete List of Bahamas States (ISO 3166-2 Compliant)

| ISO2 | Name                          | Type     |
|------|-------------------------------|----------|
| AK   | Acklins                       | District |
| BI   | Bimini                        | District |
| BP   | Black Point                   | District |
| BY   | Berry Islands                 | District |
| CE   | Central Eleuthera             | District |
| CI   | Cat Island                    | District |
| CK   | Crooked Island and Long Cay   | District |
| CO   | Central Abaco                 | District |
| CS   | Central Andros                | District |
| EG   | East Grand Bahama             | District |
| EX   | Exuma                         | District |
| FP   | City of Freeport              | District |
| GC   | Grand Cay                     | District |
| HI   | Harbour Island                | District |
| HT   | Hope Town                     | District |
| IN   | Inagua                        | District |
| LI   | Long Island                   | District |
| MC   | Mangrove Cay                  | District |
| MG   | Mayaguana                     | District |
| MI   | Moore's Island                | District |
| NE   | North Eleuthera               | District |
| NO   | North Abaco                   | District |
| NP   | New Providence                | Island   |
| NS   | North Andros                  | District |
| RC   | Rum Cay                       | District |
| RI   | Ragged Island                 | District |
| SA   | South Andros                  | District |
| SE   | South Eleuthera               | District |
| SO   | South Abaco                   | District |
| SS   | San Salvador                  | District |
| SW   | Spanish Wells                 | District |
| WG   | West Grand Bahama             | District |

## Validation Steps

### 1. JSON File Validation
```bash
# Count Bahamas states in JSON
jq '[.[] | select(.country_code == "BS")] | length' contributions/states/states.json
# Output: 32 ✓

# Verify Moore's Island was added
jq '.[] | select(.iso2 == "MI" and .country_code == "BS")' contributions/states/states.json
# Output: Found with ID 5717 ✓
```

### 2. MySQL Database Validation
```bash
# Import JSON to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py --password root

# Count Bahamas states in MySQL
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM states WHERE country_code = 'BS';"
# Output: 32 ✓

# List all Bahamas states
mysql -uroot -proot -e "USE world; SELECT iso2, name FROM states WHERE country_code = 'BS' ORDER BY iso2;"
# Output: 32 rows matching ISO 3166-2 ✓
```

### 3. Sync Back to JSON
```bash
# Sync MySQL back to JSON (ensures consistency)
python3 bin/scripts/sync/sync_mysql_to_json.py --password root
# Output: 5227 total states, 32 Bahamas states ✓
```

## Impact Analysis
- **States/Districts**: Reduced from 42 to 32 (corrected to ISO 3166-2 standard)
- **Cities**: No cities were affected (removed districts had 0 cities)
- **Data Quality**: Improved alignment with international standards
- **Breaking Changes**: None for API consumers (removed entries were not being used)

## Technical Details

### Files Modified
- `contributions/states/states.json` - Main states data file

### Database Schema
- All timezone data validated and preserved
- Foreign key relationships maintained
- Auto-increment IDs properly assigned

### Tools Used
1. `import_json_to_mysql.py` - Import JSON to MySQL
2. `add_timezones.py` - Verify timezone data
3. `sync_mysql_to_json.py` - Sync MySQL back to JSON

## Conclusion
The Bahamas states/districts data has been successfully corrected to align with the ISO 3166-2:BS standard. The database now contains exactly 32 administrative divisions as specified by the official ISO standard, with proper naming conventions and complete metadata.

All changes have been validated through the full JSON → MySQL → JSON workflow to ensure data integrity and consistency.
