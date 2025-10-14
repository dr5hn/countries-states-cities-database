# Timezone Handling Guide

## Overview

This document explains the timezone handling strategy for countries, states, and cities in this database.

## IANA Timezone Standards

This database uses **IANA timezone identifiers** (also known as Olson database or tz database). These are the standard timezone identifiers like:
- `America/New_York`
- `Europe/London`
- `Asia/Tokyo`

## Problematic Timezones: Etc/GMT*

### What are Etc/GMT timezones?

The `Etc/GMT±N` timezones (e.g., `Etc/GMT+5`, `Etc/GMT-3`) are **fixed offset timezones** that:
- Have no real-world location association
- Don't observe daylight saving time
- Are primarily used in systems/software, not for geographic locations
- Have **reversed signs** (Etc/GMT+5 is actually UTC-5, which is confusing!)

### Why we filter them out

**TimezoneFinder library** returns `Etc/GMT*` timezones for:
- Remote oceanic locations (e.g., Baker Island → `Etc/GMT+12`)
- Locations in international waters
- Very remote islands without proper timezone definition

**Problem**: These are not proper location-based timezones and create inconsistencies.

**Solution**: The `add_timezones.py` script now filters out `Etc/GMT*` timezones and leaves the field NULL if no proper IANA timezone is found.

### Special Cases

#### Etc/UTC
`Etc/UTC` is sometimes legitimate for:
- True UTC locations (some research stations)
- Coordinated Universal Time zones

**Current handling**: We also filter this out to maintain consistency. If a location truly needs UTC, it should use a proper IANA timezone like `Atlantic/Reykjavik` or similar.

## Timezone Data Structure

### Countries
Countries store timezones as an **array of timezone objects**:

```json
{
  "name": "United States",
  "timezones": [
    {
      "zoneName": "America/New_York",
      "gmtOffset": -18000,
      "gmtOffsetName": "UTC-05:00",
      "abbreviation": "EST",
      "tzName": "Eastern Standard Time"
    },
    {
      "zoneName": "America/Chicago",
      "gmtOffset": -21600,
      "gmtOffsetName": "UTC-06:00",
      "abbreviation": "CST",
      "tzName": "Central Standard Time"
    }
  ]
}
```

### States
States store a **single timezone string**:

```json
{
  "name": "California",
  "timezone": "America/Los_Angeles"
}
```

### Cities
Cities store a **single timezone string**:

```json
{
  "name": "San Francisco",
  "timezone": "America/Los_Angeles"
}
```

## Best Practices

### For Contributors

#### Adding New Cities
1. **Include timezone if known**: Use proper IANA identifier
   ```json
   {
     "name": "Paris",
     "timezone": "Europe/Paris"
   }
   ```

2. **Omit if uncertain**: Leave out the timezone field
   ```json
   {
     "name": "New City"
     // no timezone field
   }
   ```
   The `add_timezones.py` script can populate it later.

3. **Never use Etc/GMT timezones**: These are not location-specific
   ```json
   // ❌ WRONG
   "timezone": "Etc/GMT-5"

   // ✅ CORRECT
   "timezone": "America/New_York"
   ```

#### Adding New States
1. Use the primary timezone for the state
2. For states spanning multiple timezones, use the one covering the capital or largest city
3. Verify against IANA timezone database

#### Adding New Countries
1. Include ALL timezones used in the country
2. Each timezone should have complete information (name, offset, abbreviation)
3. Verify against authoritative sources

### For Maintainers

#### Populating Missing Timezones
```bash
# Test first with dry-run (cities only)
python3 bin/scripts/utility/add_timezones.py --table cities --limit 100 --dry-run

# Test with states
python3 bin/scripts/utility/add_timezones.py --table states --limit 100 --dry-run

# Run for both cities and states
python3 bin/scripts/utility/add_timezones.py --table both

# Sync back to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py
```

#### Cleaning Up Bad Timezones

If `Etc/GMT*` timezones have already been added to the database:

```sql
-- Find cities with Etc/GMT timezones
SELECT id, name, country_code, timezone
FROM cities
WHERE timezone LIKE 'Etc/GMT%';

-- Set them to NULL so they can be re-processed
UPDATE cities
SET timezone = NULL
WHERE timezone LIKE 'Etc/GMT%' AND timezone != 'Etc/UTC';

-- Or just remove all Etc/ timezones
UPDATE cities
SET timezone = NULL
WHERE timezone LIKE 'Etc/%';
```

For states:
```sql
-- Find states with Etc/ timezones
SELECT id, name, country_code, timezone
FROM states
WHERE timezone LIKE 'Etc/%';

-- Clean them up (requires manual review for proper timezone)
-- UPDATE states SET timezone = 'America/Curacao' WHERE id = 1234;
```

#### Validating Timezones

```bash
# Create a validation script
python3 bin/scripts/utility/validate_timezones.py
```

Look for:
- Any `Etc/GMT*` timezones in production data
- Timezones that don't exist in IANA database
- Inconsistencies between parent/child relationships

## Common Timezone Mappings

### Legacy → Current IANA

Some old or unofficial timezones should be mapped to official ones:

| ❌ Invalid/Deprecated | ✅ Correct IANA Timezone |
|----------------------|--------------------------|
| `America/Kralendijk` | `America/Curacao` |
| `US/Eastern` | `America/New_York` |
| `US/Central` | `America/Chicago` |
| `US/Mountain` | `America/Denver` |
| `US/Pacific` | `America/Los_Angeles` |
| `US/Alaska` | `America/Anchorage` |
| `US/Aleutian` | `America/Adak` |

Note: `US/*` timezones are links/aliases that still work but canonical names are preferred.

## Tools & Resources

### IANA Timezone Database
- Official source: https://www.iana.org/time-zones
- List of timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

### Python Tools
- `timezonefinder`: Lat/lng → timezone lookup
- `pytz`: Timezone validation and conversion
- `zoneinfo`: Built-in Python 3.9+ timezone handling

### Validation
```python
import pytz

def is_valid_iana_timezone(tz_name):
    """Check if timezone is valid IANA timezone"""
    try:
        pytz.timezone(tz_name)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False

# Usage
is_valid_iana_timezone("America/New_York")  # True
is_valid_iana_timezone("Etc/GMT+5")  # True (but we filter it)
is_valid_iana_timezone("America/Kralendijk")  # False
```

## FAQ

**Q: Why does TimezoneFinder return Etc/GMT for some locations?**
A: For locations in international waters or very remote areas without a defined timezone, the library falls back to fixed-offset Etc/GMT zones. We filter these out.

**Q: What should I do if a city has no timezone after running the script?**
A: Check if:
1. The coordinates are correct
2. The location is in international waters
3. Consider using the parent state or country timezone as a fallback

**Q: Can I use UTC offset like "+05:00" instead of timezone name?**
A: No. Always use IANA timezone identifiers. Offsets don't capture daylight saving time and other timezone rules.

**Q: What about Antarctica research stations?**
A: Antarctica has proper IANA timezones:
- `Antarctica/McMurdo`
- `Antarctica/Palmer`
- `Antarctica/Rothera`
- etc.

**Q: Should I include historic timezone changes?**
A: No. This database represents current timezone assignments. The IANA database itself handles historical changes.

## Summary

✅ **DO**:
- Use proper IANA timezone identifiers
- Verify timezones against official sources
- Filter out `Etc/GMT*` timezones
- Leave timezone NULL if uncertain

❌ **DON'T**:
- Use `Etc/GMT*` for cities or states
- Use deprecated timezone names
- Use UTC offsets instead of timezone names
- Guess timezones without verification
