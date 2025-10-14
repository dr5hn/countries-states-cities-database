# SAR Data Structure Visualization

## Before: The Problem

```
Countries Table:
┌────────────────────────────────────────────────────────┐
│ id: 45, name: China                                    │
│ phonecode: 86, currency: CNY, emoji: 🇨🇳              │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ id: 98, name: Hong Kong S.A.R.                        │
│ phonecode: 852, currency: HKD, emoji: 🇭🇰             │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ id: 128, name: Macau S.A.R.                           │
│ phonecode: 853, currency: MOP, emoji: 🇲🇴             │
└────────────────────────────────────────────────────────┘

States Table (old):
┌────────────────────────────────────────────────────────┐
│ id: 2267, name: Hong Kong SAR                         │
│ country_id: 45, country_code: CN                       │
│ ❌ Missing: phonecode, currency, emoji                 │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ id: 2266, name: Macau SAR                             │
│ country_id: 45, country_code: CN                       │
│ ❌ Missing: phonecode, currency, emoji                 │
└────────────────────────────────────────────────────────┘

Problem: SARs represented as both countries AND states,
         but states lacked important attributes
```

## After: The Solution

```
Countries Table (unchanged):
┌────────────────────────────────────────────────────────┐
│ id: 45, name: China                                    │
│ phonecode: 86, currency: CNY, emoji: 🇨🇳              │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ id: 98, name: Hong Kong S.A.R.                        │
│ (kept for backward compatibility)                      │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ id: 128, name: Macau S.A.R.                           │
│ (kept for backward compatibility)                      │
└────────────────────────────────────────────────────────┘

States Table (enhanced):
┌────────────────────────────────────────────────────────┐
│ id: 2267, name: Hong Kong SAR                         │
│ country_id: 45, country_code: CN                       │
│ type: special administrative region                    │
│ ✅ phonecode: 852                                      │
│ ✅ currency: HKD                                       │
│ ✅ currency_name: Hong Kong dollar                     │
│ ✅ currency_symbol: $                                  │
│ ✅ emoji: 🇭🇰                                          │
│ ✅ emojiU: U+1F1ED U+1F1F0                            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ id: 2266, name: Macau SAR                             │
│ country_id: 45, country_code: CN                       │
│ type: special administrative region                    │
│ ✅ phonecode: 853                                      │
│ ✅ currency: MOP                                       │
│ ✅ currency_name: Macanese pataca                      │
│ ✅ currency_symbol: $                                  │
│ ✅ emoji: 🇲🇴                                          │
│ ✅ emojiU: U+1F1F2 U+1F1F4                            │
└────────────────────────────────────────────────────────┘

Regular States (SAR fields are NULL):
┌────────────────────────────────────────────────────────┐
│ id: 3318, name: Beijing                               │
│ country_id: 45, country_code: CN                       │
│ type: municipality                                     │
│ phonecode: NULL                                        │
│ currency: NULL                                         │
│ emoji: NULL                                            │
└────────────────────────────────────────────────────────┘

Solution: SARs now have complete data as states under China
```

## Data Hierarchy

```
🌏 China (Country)
├── 📍 Beijing (Regular State - no SAR fields)
├── 📍 Shanghai (Regular State - no SAR fields)
├── 📍 Guangdong (Regular State - no SAR fields)
│
├── 🏴 Hong Kong SAR (Special State - with SAR fields)
│   ├── phonecode: 852
│   ├── currency: HKD 💵
│   ├── emoji: 🇭🇰
│   └── 🏙️ Cities (27 cities)
│       ├── Central
│       ├── Kowloon
│       └── ...
│
└── 🏴 Macau SAR (Special State - with SAR fields)
    ├── phonecode: 853
    ├── currency: MOP 💵
    ├── emoji: 🇲🇴
    └── 🏙️ Cities
```

## Schema Comparison

### States Table Fields

| Field | Regular States | SARs | Description |
|-------|---------------|------|-------------|
| `id` | ✅ Required | ✅ Required | Unique identifier |
| `name` | ✅ Required | ✅ Required | State name |
| `country_id` | ✅ Required | ✅ Required | Parent country |
| `country_code` | ✅ Required | ✅ Required | ISO2 code |
| `type` | ✅ Optional | ✅ "special administrative region" | Division type |
| `iso2` | ✅ Optional | ✅ Required | State ISO code |
| `phonecode` | ❌ NULL | ✅ **"852"** | **SAR field** |
| `currency` | ❌ NULL | ✅ **"HKD"** | **SAR field** |
| `currency_name` | ❌ NULL | ✅ **"Hong Kong dollar"** | **SAR field** |
| `currency_symbol` | ❌ NULL | ✅ **"$"** | **SAR field** |
| `emoji` | ❌ NULL | ✅ **"🇭🇰"** | **SAR field** |
| `emojiU` | ❌ NULL | ✅ **"U+1F1ED U+1F1F0"** | **SAR field** |

## Query Examples

### Get All China Subdivisions

```sql
SELECT id, name, type, phonecode, currency, emoji
FROM states 
WHERE country_id = 45
ORDER BY name;

-- Results include both regular states and SARs:
-- Beijing (NULL, NULL, NULL)
-- Hong Kong SAR (852, HKD, 🇭🇰)
-- Macau SAR (853, MOP, 🇲🇴)
-- Shanghai (NULL, NULL, NULL)
```

### Get Only SARs

```sql
SELECT id, name, phonecode, currency, emoji
FROM states 
WHERE type = 'special administrative region';

-- Results:
-- Hong Kong SAR (852, HKD, 🇭🇰)
-- Macau SAR (853, MOP, 🇲🇴)
```

### Get States with Own Currencies

```sql
SELECT id, name, country_code, currency, currency_name
FROM states 
WHERE currency IS NOT NULL;

-- Results include all SARs with unique currencies
```

## Benefits Summary

✅ **Geographically Accurate**: SARs properly classified under parent country
✅ **Data Complete**: No loss of important attributes
✅ **Backward Compatible**: Existing queries still work
✅ **Extensible**: Can support other autonomous regions
✅ **Standards Compliant**: Follows ISO 3166-2
✅ **Politically Neutral**: Respects autonomy while showing relationships

## Files You Need to Know

- `sql/schema.sql` - Database schema with new fields
- `contributions/states/states.json` - State data including SARs
- `docs/SPECIAL_ADMINISTRATIVE_REGIONS.md` - Complete documentation
- `bin/Commands/ExportJson.php` - Export with SAR fields
