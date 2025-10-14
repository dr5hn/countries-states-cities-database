# Alternative Solution: Single JSON Field for SAR Metadata

## Problem with Current Approach
Adding 6 new columns (phonecode, currency, currency_name, currency_symbol, emoji, emojiU) to the states table for just 2 Special Administrative Regions creates unnecessary schema complexity.

## Proposed Alternative: Single JSON Field

### Schema Change
Instead of 6 columns, add **one** column:

```sql
-- Instead of:
phonecode VARCHAR(255)
currency VARCHAR(255)
currency_name VARCHAR(255)
currency_symbol VARCHAR(255)
emoji VARCHAR(191)
emojiU VARCHAR(191)

-- Use:
sar_metadata JSON DEFAULT NULL
```

### Data Structure

**Hong Kong SAR:**
```json
{
  "id": 2267,
  "name": "Hong Kong SAR",
  "country_id": 45,
  "country_code": "CN",
  "type": "special administrative region",
  "sar_metadata": {
    "phonecode": "852",
    "currency": "HKD",
    "currency_name": "Hong Kong dollar",
    "currency_symbol": "$",
    "emoji": "🇭🇰",
    "emojiU": "U+1F1ED U+1F1F0"
  }
}
```

**Regular State (Beijing):**
```json
{
  "id": 3318,
  "name": "Beijing",
  "country_id": 45,
  "country_code": "CN",
  "type": "municipality",
  "sar_metadata": null  // NULL - no storage overhead
}
```

### Benefits

1. **Minimal Schema Impact**: Only 1 column instead of 6
2. **No Storage Overhead**: NULL for 5,071 regular states
3. **Flexible**: Easy to add more SAR attributes without schema changes
4. **Clean Queries**: Can still query SARs: `WHERE sar_metadata IS NOT NULL`
5. **JSON Support**: MySQL 5.7+, PostgreSQL 9.2+ have excellent JSON support

### Query Examples

```sql
-- Get all SARs
SELECT * FROM states WHERE sar_metadata IS NOT NULL;

-- Get SAR phone code
SELECT name, sar_metadata->>'$.phonecode' as phonecode 
FROM states 
WHERE sar_metadata IS NOT NULL;

-- Get SARs with specific currency
SELECT * FROM states 
WHERE JSON_EXTRACT(sar_metadata, '$.currency') = 'HKD';
```

### Export Example

```json
{
  "id": 2267,
  "name": "Hong Kong SAR",
  "phonecode": "852",  // Extracted from sar_metadata for flat exports
  "currency": "HKD",
  "emoji": "🇭🇰"
}
```

### Implementation Files to Change

1. `sql/schema.sql` - Change to single JSON column
2. `prisma/schema.prisma` - Change to `sar_metadata Json?`
3. `bin/Commands/ExportSqlServer.php` - Change to JSON column
4. `bin/Commands/ExportJson.php` - Extract JSON fields for flat export
5. `contributions/states/states.json` - Nest SAR fields in `sar_metadata` object

### Migration Path

For existing databases with the 6-column approach:

```sql
-- Create new column
ALTER TABLE states ADD COLUMN sar_metadata JSON;

-- Migrate data
UPDATE states 
SET sar_metadata = JSON_OBJECT(
  'phonecode', phonecode,
  'currency', currency,
  'currency_name', currency_name,
  'currency_symbol', currency_symbol,
  'emoji', emoji,
  'emojiU', emojiU
)
WHERE phonecode IS NOT NULL;

-- Drop old columns
ALTER TABLE states 
DROP COLUMN phonecode,
DROP COLUMN currency,
DROP COLUMN currency_name,
DROP COLUMN currency_symbol,
DROP COLUMN emoji,
DROP COLUMN emojiU;
```

## Other Alternatives

### Option 2: Keep Current Dual Representation
- Hong Kong and Macau remain as both countries AND states
- Document this as intentional for backward compatibility
- No schema changes needed
- Users can choose which representation to use

### Option 3: Separate SAR Table
- Create `sar_attributes` table with 1:1 relationship
- More normalized but adds complexity
- Requires JOIN for every SAR query

### Option 4: Extend Translations Field
- Store SAR metadata in existing `translations` JSON field
- No schema changes at all
- Could be confusing since translations are language-specific

## Recommendation

**Single JSON field (Option 1)** provides the best balance:
- Minimal schema impact (1 column vs 6)
- No storage overhead for regular states
- Maintains data completeness for SARs
- Future-proof and flexible
