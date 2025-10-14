# Implementation Summary: Special Administrative Regions Support

## Issue Addressed

**Original Issue**: "SARs like Hong Kong and Macau should be a state or a city instead of country. But at the same time, it has a different phonecode, currency, currency_name, currency_symbol, emoji and emojiU. So it is hard to be injected into state since it will lose the details."

## Solution Implemented

We extended the `states` table schema to include **optional** country-level attributes specifically for Special Administrative Regions (SARs), allowing them to be properly classified as states under their parent country while retaining their unique characteristics.

## Changes Made

### 1. Database Schema Extensions

#### Modified Files:
- `sql/schema.sql` - MySQL schema
- `prisma/schema.prisma` - Prisma ORM schema  
- `bin/Commands/ExportSqlServer.php` - SQL Server export schema

#### New Optional Fields Added to `states` Table:
```sql
phonecode      VARCHAR(255) -- Phone dialing code (e.g., "852" for Hong Kong)
currency       VARCHAR(255) -- Currency code (e.g., "HKD")
currency_name  VARCHAR(255) -- Full currency name (e.g., "Hong Kong dollar")
currency_symbol VARCHAR(255) -- Currency symbol (e.g., "$")
emoji          VARCHAR(191) -- Flag emoji (e.g., "🇭🇰")
emojiU         VARCHAR(191) -- Emoji Unicode (e.g., "U+1F1ED U+1F1F0")
```

**Important**: These fields are `NULL` for regular states/provinces and only populated for SARs.

### 2. Data Population

Updated `contributions/states/states.json` with SAR-specific fields:

**Hong Kong SAR (ID: 2267)**:
```json
{
  "id": 2267,
  "name": "Hong Kong SAR",
  "country_id": 45,
  "country_code": "CN",
  "type": "special administrative region",
  "phonecode": "852",
  "currency": "HKD",
  "currency_name": "Hong Kong dollar",
  "currency_symbol": "$",
  "emoji": "🇭🇰",
  "emojiU": "U+1F1ED U+1F1F0"
}
```

**Macau SAR (ID: 2266)**:
```json
{
  "id": 2266,
  "name": "Macau SAR",
  "country_id": 45,
  "country_code": "CN",
  "type": "special administrative region",
  "phonecode": "853",
  "currency": "MOP",
  "currency_name": "Macanese pataca",
  "currency_symbol": "$",
  "emoji": "🇲🇴",
  "emojiU": "U+1F1F2 U+1F1F4"
}
```

### 3. Export Command Updates

Modified `bin/Commands/ExportJson.php` to export the new SAR fields:
- Added SAR fields to states array output
- Added SAR fields to country-state nested array output
- All other export formats (CSV, XML, YAML, MongoDB) automatically inherit from JSON

### 4. Documentation

Created comprehensive documentation:

#### New Documentation Files:
- `docs/SPECIAL_ADMINISTRATIVE_REGIONS.md` - Complete guide on SAR handling
  - Explains the challenge and solution
  - Provides schema reference
  - Includes usage guidelines for contributors and API consumers
  - Documents current SARs (Hong Kong, Macau)
  - Suggests future use cases

#### Updated Documentation:
- `contributions/README.md` - Added State Fields reference table with SAR fields
- `README.md` - Added link to SAR documentation in Contributing section

### 5. Schema Validation

- Changed `states` table `ROW_FORMAT` from `COMPACT` to `DYNAMIC` to accommodate the additional fields
- Validated schema with MySQL 8.0 test database
- Successfully tested insert and query operations with SAR data

## Technical Details

### Data Hierarchy
```
China (country_id: 45)
├── Beijing (state, no SAR fields)
├── Shanghai (state, no SAR fields)
├── Hong Kong SAR (state, WITH SAR fields)
└── Macau SAR (state, WITH SAR fields)
    └── Cities in Macau (reference state_id: 2266)
```

### Backward Compatibility
- Existing states remain unchanged (SAR fields are NULL)
- All existing queries continue to work
- No breaking changes to API or export formats
- Cities in HK/Macau already reference correct state IDs

### Query Examples

**Get all SARs:**
```sql
SELECT * FROM states WHERE type = 'special administrative region';
```

**Get states with their own currencies:**
```sql
SELECT * FROM states WHERE currency IS NOT NULL;
```

**Get all China subdivisions including SARs:**
```sql
SELECT * FROM states WHERE country_id = 45;
```

## Benefits

1. **Geographical Accuracy**: Hong Kong and Macau are correctly represented as parts of China
2. **Data Completeness**: No loss of important attributes (phone codes, currencies, flags)
3. **Standards Compliance**: Maintains ISO 3166-2 compliance
4. **Extensibility**: Can support other SARs and autonomous territories
5. **Backward Compatible**: Existing integrations continue to work

## Future Applications

This schema can accommodate other similar entities:
- Åland Islands (Finland)
- Faroe Islands (Denmark)
- Greenland (Denmark)
- Puerto Rico (USA)
- Other territories with special status

## Files Modified

1. `sql/schema.sql` - Added SAR fields to states table, changed ROW_FORMAT
2. `prisma/schema.prisma` - Added SAR fields to State model
3. `bin/Commands/ExportSqlServer.php` - Added SAR fields to SQL Server schema
4. `bin/Commands/ExportJson.php` - Added SAR fields to JSON export
5. `contributions/states/states.json` - Populated SAR data for HK and Macau
6. `contributions/README.md` - Added State Fields documentation
7. `README.md` - Added link to SAR documentation

## Files Created

1. `docs/SPECIAL_ADMINISTRATIVE_REGIONS.md` - Comprehensive SAR documentation

## Testing

- [x] Schema syntax validated with MySQL 8.0
- [x] Test insert and query operations successful
- [x] JSON data validated and populated correctly
- [x] Export command modifications verified
- [x] Documentation reviewed for completeness

## Validation Steps for Maintainers

1. Import the updated schema to MySQL
2. Run the JSON import script to populate SAR data
3. Run export commands to generate all formats
4. Verify Hong Kong and Macau states include SAR fields in exports
5. Verify regular states have NULL SAR fields in exports

## Notes

- Hong Kong and Macau entries still exist in the `countries` table (IDs 98 and 128) for backward compatibility
- New integrations should use the state entries under China (IDs 2267 and 2266)
- The solution follows the "One China" principle while respecting the autonomy and unique characteristics of SARs
- This approach is politically neutral and focuses on accurate data representation

## References

- Issue: "Special Administrative Regions representation"
- ISO 3166-2: Standard for subdivision codes
- WikiData Q8646 (Hong Kong), Q14773 (Macau)
