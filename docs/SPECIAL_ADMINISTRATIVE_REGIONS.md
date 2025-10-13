# Special Administrative Regions (SARs)

## Overview

This document explains how Special Administrative Regions (SARs) like Hong Kong and Macau are handled in the Countries States Cities Database.

## The Challenge

Special Administrative Regions present a unique challenge in geographical databases:

1. **Political Status**: Hong Kong and Macau are officially part of China
2. **Autonomy**: They have their own phone codes, currencies, flags, and other distinct attributes
3. **Data Structure**: Traditional hierarchical models (Country → State → City) don't accommodate entities that need both state-level classification AND country-level attributes

## The Solution

We've extended the `states` table to include optional country-level fields specifically for SARs. This allows SARs to:

- Be correctly classified as states/provinces under their parent country (China)
- Retain their unique attributes (phone code, currency, flag, etc.)
- Maintain data integrity across all export formats

### Extended State Schema

The `states` table now includes these **optional** fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `phonecode` | VARCHAR(255) | Phone dialing code | `"852"` (Hong Kong) |
| `currency` | VARCHAR(255) | Currency code (ISO 4217) | `"HKD"` |
| `currency_name` | VARCHAR(255) | Full currency name | `"Hong Kong dollar"` |
| `currency_symbol` | VARCHAR(255) | Currency symbol | `"$"` |
| `emoji` | VARCHAR(191) | Flag emoji | `"🇭🇰"` |
| `emojiU` | VARCHAR(191) | Emoji Unicode representation | `"U+1F1ED U+1F1F0"` |

**Important**: These fields are `NULL` for regular states and only populated for Special Administrative Regions.

## Implementation Details

### Database Schema

#### MySQL Schema (sql/schema.sql)
```sql
CREATE TABLE `states` (
  ...
  `phonecode` varchar(255) DEFAULT NULL COMMENT 'For Special Administrative Regions',
  `currency` varchar(255) DEFAULT NULL COMMENT 'For Special Administrative Regions',
  `currency_name` varchar(255) DEFAULT NULL COMMENT 'For Special Administrative Regions',
  `currency_symbol` varchar(255) DEFAULT NULL COMMENT 'For Special Administrative Regions',
  `emoji` varchar(191) DEFAULT NULL COMMENT 'For Special Administrative Regions',
  `emojiU` varchar(191) DEFAULT NULL COMMENT 'For Special Administrative Regions',
  ...
);
```

#### Prisma Schema (prisma/schema.prisma)
```prisma
model State {
  ...
  phonecode      String?   @db.VarChar(255)
  currency       String?   @db.VarChar(255)
  currencyName   String?   @map("currency_name") @db.VarChar(255)
  currencySymbol String?   @map("currency_symbol") @db.VarChar(255)
  emoji          String?   @db.VarChar(191)
  emojiU         String?   @db.VarChar(191)
  ...
}
```

### Current SARs in the Database

#### Hong Kong SAR
```json
{
  "id": 2267,
  "name": "Hong Kong SAR",
  "country_id": 45,
  "country_code": "CN",
  "iso2": "HK",
  "type": "special administrative region",
  "phonecode": "852",
  "currency": "HKD",
  "currency_name": "Hong Kong dollar",
  "currency_symbol": "$",
  "emoji": "🇭🇰",
  "emojiU": "U+1F1ED U+1F1F0"
}
```

#### Macau SAR
```json
{
  "id": 2266,
  "name": "Macau SAR",
  "country_id": 45,
  "country_code": "CN",
  "iso2": "MO",
  "type": "special administrative region",
  "phonecode": "853",
  "currency": "MOP",
  "currency_name": "Macanese pataca",
  "currency_symbol": "$",
  "emoji": "🇲🇴",
  "emojiU": "U+1F1F2 U+1F1F4"
}
```

## Data Organization

### Country Entry for China
```json
{
  "id": 45,
  "name": "China",
  "iso2": "CN",
  "phonecode": "86",
  "currency": "CNY",
  "currency_name": "Chinese yuan"
}
```

### States of China (Including SARs)
- **Regular provinces**: Beijing, Shanghai, Guangdong, etc. (no SAR fields)
- **Special Administrative Regions**:
  - Hong Kong SAR (with SAR fields populated)
  - Macau SAR (with SAR fields populated)

### Cities
Cities in Hong Kong and Macau are stored with:
- `country_id`: 45 (China)
- `country_code`: "CN"
- `state_id`: 2267 (Hong Kong SAR) or 2266 (Macau SAR)
- `state_code`: "HK" or "MO"

## Export Formats

All export formats (JSON, CSV, XML, YAML, SQL Server, MongoDB) support the extended schema:

### JSON Export Example
```json
{
  "id": 2267,
  "name": "Hong Kong SAR",
  "country_id": 45,
  "country_code": "CN",
  "phonecode": "852",
  "currency": "HKD",
  "emoji": "🇭🇰"
}
```

### SQL Server Export
The SQL Server export includes the new fields in the CREATE TABLE statement.

## Usage Guidelines

### For Contributors

When adding a new Special Administrative Region:

1. Add the entry to `contributions/states/states.json`
2. Set `type` to `"special administrative region"`
3. Include the SAR-specific fields:
   - `phonecode`
   - `currency`
   - `currency_name`
   - `currency_symbol`
   - `emoji`
   - `emojiU`

Example:
```json
{
  "name": "New SAR",
  "country_id": 45,
  "country_code": "CN",
  "iso2": "XX",
  "type": "special administrative region",
  "phonecode": "XXX",
  "currency": "XXX",
  "currency_name": "Currency Name",
  "currency_symbol": "$",
  "emoji": "🏴",
  "emojiU": "U+1F3F4"
}
```

### For API Consumers

When querying states:
- Regular states will have `phonecode`, `currency`, etc. as `null`
- SARs will have these fields populated
- Use the `type` field to identify SARs: `type === "special administrative region"`

Example Query Pattern:
```sql
-- Get all SARs
SELECT * FROM states WHERE type = 'special administrative region';

-- Get states with their own currencies (SARs)
SELECT * FROM states WHERE currency IS NOT NULL;

-- Get all subdivisions of China including SARs
SELECT * FROM states WHERE country_id = 45;
```

## Benefits of This Approach

1. **Geographical Accuracy**: SARs are correctly represented as subdivisions of their parent country
2. **Data Completeness**: No loss of important attributes (phone codes, currencies, flags)
3. **Backward Compatibility**: Existing queries and exports continue to work
4. **Flexibility**: Can accommodate other similar entities (e.g., autonomous regions, territories with special status)
5. **Standards Compliance**: Maintains ISO 3166-2 compliance for subdivisions

## Future Considerations

This schema can be extended to support other similar entities:

- **Åland Islands** (FI) - Autonomous region of Finland
- **Faroe Islands** (FO) - Autonomous territory of Denmark
- **Greenland** (GL) - Autonomous territory of Denmark
- **Puerto Rico** (PR) - US territory
- Other territories and autonomous regions with distinct attributes

## Related Documentation

- [Contributions Guide](../contributions/README.md) - How to add or modify data
- [Schema Reference](../sql/schema.sql) - Complete database schema
- [Export Commands](../bin/Commands/) - Export implementations

## References

- [ISO 3166-1](https://www.iso.org/iso-3166-country-codes.html) - Country codes
- [ISO 3166-2](https://www.iso.org/standard/72483.html) - Subdivision codes
- [WikiData: Hong Kong](https://www.wikidata.org/wiki/Q8646)
- [WikiData: Macau](https://www.wikidata.org/wiki/Q14773)
