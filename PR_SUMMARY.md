# Pull Request: Special Administrative Regions (SARs) Support

## Problem Statement

The issue raised concerns about how Special Administrative Regions like Hong Kong and Macau were represented in the database:

> "SARs like Hong Kong and Macau should be a state or a city instead of country. But at the same time, it has a different phonecode, currency, currency_name, currency_symbol, emoji and emojiU. So it is hard to be injected into state since it will lose the details."

## Solution Overview

We extended the `states` table to include **optional** country-level fields specifically for Special Administrative Regions. This allows SARs to:
- Be correctly classified as states under their parent country (China)
- Retain all their unique attributes (phone codes, currencies, flags)
- Maintain backward compatibility with existing data

## Technical Implementation

### Schema Changes

Added 6 new optional fields to the `states` table:

```sql
phonecode      VARCHAR(255) -- Phone code (e.g., "852" for Hong Kong)
currency       VARCHAR(255) -- Currency code (e.g., "HKD")
currency_name  VARCHAR(255) -- Full currency name
currency_symbol VARCHAR(255) -- Currency symbol (e.g., "$")
emoji          VARCHAR(191) -- Flag emoji (e.g., "🇭🇰")
emojiU         VARCHAR(191) -- Emoji Unicode representation
```

**Important**: These fields are `NULL` for regular states and only populated for SARs.

### Data Structure

**Before:**
```json
// Hong Kong as a country (ID: 98)
{
  "name": "Hong Kong S.A.R.",
  "phonecode": "852",
  "currency": "HKD",
  "emoji": "🇭🇰"
}

// Hong Kong as a state (ID: 2267) - missing attributes
{
  "name": "Hong Kong SAR",
  "country_id": 45,
  "country_code": "CN"
  // ❌ Missing: phonecode, currency, emoji
}
```

**After:**
```json
// Hong Kong as a state (ID: 2267) - complete attributes
{
  "name": "Hong Kong SAR",
  "country_id": 45,
  "country_code": "CN",
  "type": "special administrative region",
  "phonecode": "852",       // ✅ Added
  "currency": "HKD",        // ✅ Added
  "currency_name": "Hong Kong dollar", // ✅ Added
  "currency_symbol": "$",   // ✅ Added
  "emoji": "🇭🇰",           // ✅ Added
  "emojiU": "U+1F1ED U+1F1F0" // ✅ Added
}
```

## Files Changed

### Schema Files (4)
1. `sql/schema.sql` - MySQL schema with new fields
2. `prisma/schema.prisma` - Prisma ORM schema
3. `bin/Commands/ExportSqlServer.php` - SQL Server export
4. `bin/Commands/ExportJson.php` - JSON export with SAR fields

### Data Files (1)
5. `contributions/states/states.json` - Populated Hong Kong and Macau SAR data

### Documentation (3)
6. `contributions/README.md` - Added State Fields reference
7. `README.md` - Added link to SAR documentation
8. `docs/SPECIAL_ADMINISTRATIVE_REGIONS.md` - Complete technical guide
9. `docs/SAR_VISUALIZATION.md` - Visual before/after comparison
10. `IMPLEMENTATION_SUMMARY.md` - Implementation details

### Testing (1)
11. `scripts/validate_sar.py` - Validation script

## Current SARs

### Hong Kong SAR (ID: 2267)
- Country: China (ID: 45)
- Phone code: +852
- Currency: HKD (Hong Kong dollar)
- Flag: 🇭🇰

### Macau SAR (ID: 2266)
- Country: China (ID: 45)
- Phone code: +853
- Currency: MOP (Macanese pataca)
- Flag: 🇲🇴

## Testing & Validation

### Validation Script
Run `python3 scripts/validate_sar.py` to validate:
```
✓ All validations PASSED

SAR Implementation is correct:
  - Hong Kong SAR has all required fields
  - Macau SAR has all required fields
  - Both are correctly linked to China (country_id: 45)
  - Regular states don't have SAR fields
```

### Database Testing
- Schema validated with MySQL 8.0
- Tested INSERT and SELECT operations
- Verified row format (DYNAMIC) handles field count

### Export Testing
- JSON export includes SAR fields
- CSV, XML, YAML exports inherit from JSON
- SQL Server schema updated

## Query Examples

### Get all SARs
```sql
SELECT id, name, phonecode, currency, emoji
FROM states 
WHERE type = 'special administrative region';
```

### Get all China subdivisions
```sql
SELECT id, name, type, phonecode, currency
FROM states 
WHERE country_id = 45
ORDER BY name;
-- Returns regular provinces (no SAR fields) and SARs (with SAR fields)
```

### Get states with own currencies
```sql
SELECT id, name, country_code, currency
FROM states 
WHERE currency IS NOT NULL;
-- Returns only SARs
```

## Benefits

✅ **Geographically Accurate**: SARs properly classified under parent country
✅ **Data Complete**: No loss of important attributes
✅ **Backward Compatible**: Existing queries continue to work
✅ **Extensible**: Can support future SARs and autonomous territories
✅ **Standards Compliant**: Follows ISO 3166-2 subdivision standards
✅ **Politically Neutral**: Respects autonomy while showing relationships

## Future Applications

This schema can accommodate other similar entities:
- **Åland Islands** (Finland)
- **Faroe Islands** (Denmark)
- **Greenland** (Denmark)
- **Puerto Rico** (USA)
- Other autonomous territories with distinct attributes

## Documentation

All documentation is comprehensive and includes:

1. **[SPECIAL_ADMINISTRATIVE_REGIONS.md](docs/SPECIAL_ADMINISTRATIVE_REGIONS.md)**
   - Technical overview
   - Schema reference
   - Implementation details
   - Usage guidelines
   - Query examples

2. **[SAR_VISUALIZATION.md](docs/SAR_VISUALIZATION.md)**
   - Visual before/after comparison
   - Data hierarchy diagram
   - Field comparison table
   - Query examples with results

3. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)**
   - Complete change log
   - Validation steps
   - Maintainer notes

## Breaking Changes

**None** - This is a backward-compatible extension:
- Existing states are unchanged (SAR fields are NULL)
- All existing queries continue to work
- No modifications to existing data required
- Optional fields can be safely ignored if not needed

## Migration Path

For existing databases:

1. Run the updated schema (adds new columns)
2. Import updated states.json (populates SAR data)
3. Re-run exports to include SAR fields

No data migration scripts needed - the changes are additive.

## Conclusion

This implementation solves the original issue by allowing Hong Kong and Macau to be properly represented as states under China while retaining all their unique characteristics. The solution is technically sound, well-documented, tested, and ready for production use.
