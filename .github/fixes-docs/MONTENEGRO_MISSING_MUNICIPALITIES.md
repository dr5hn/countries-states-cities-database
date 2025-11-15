# Montenegro Missing Municipalities Fix

**Issue Reference**: #[issue_number] - Montenegro municipality missing  
**Date**: 2025-11-15  
**Fixed By**: GitHub Copilot

## Problem Statement

Montenegro was missing 3 municipalities from the ISO 3166-2:ME standard. The database had only 22 municipalities when it should have 25 according to the official ISO standard.

### Missing Municipalities
- **Herceg-Novi** (ME-08)
- **Tuzi** (ME-24)
- **Zeta** (ME-25)

## Solution

### 1. Added Municipalities to `contributions/states/states.json`

Added three new municipality entries with complete data:

**Herceg-Novi Municipality (ME-08)**:
- ISO Code: ME-08
- Coordinates: 42.45306°N, 18.53722°E
- Native Name: Херцег Нови
- Timezone: Europe/Podgorica
- WikiData ID: Q187144
- Translations: 14 languages (ar, de, es, fr, hi, it, ja, ko, nl, pl, pt, ru, tr, uk)

**Tuzi Municipality (ME-24)**:
- ISO Code: ME-24
- Coordinates: 42.36667°N, 19.40000°E
- Native Name: Тузи
- Timezone: Europe/Podgorica
- WikiData ID: Q2656869
- Translations: 12 languages (de, es, fr, hi, it, ja, ko, nl, pl, pt, ru, uk)

**Zeta Municipality (ME-25)**:
- ISO Code: ME-25
- Coordinates: 42.40000°N, 19.25000°E
- Native Name: Зета
- Timezone: Europe/Podgorica
- WikiData ID: Q25411815
- Translations: 14 languages (ar, de, es, fr, hi, it, ja, ko, nl, pl, pt, ru, tr, uk)

### 2. Added Cities to `contributions/cities/ME.json`

Added 9 major cities/settlements across the three municipalities:

**Herceg-Novi Municipality (4 cities)**:
1. **Herceg Novi** - 42.45306°N, 18.53722°E (WikiData: Q160115, 14 translations)
2. **Igalo** - 42.45583°N, 18.51667°E (WikiData: Q988315, 7 translations)
3. **Kamenari** - 42.46167°N, 18.68806°E (WikiData: none, 0 translations - no Wikipedia page)
4. **Bijela** - 42.44778°N, 18.65972°E (WikiData: Q808104, 4 translations)

**Tuzi Municipality (3 cities)**:
1. **Tuzi** - 42.36667°N, 19.40000°E (WikiData: Q1020982, 12 translations)
2. **Dinoša** - 42.38333°N, 19.38333°E (WikiData: Q3028133, 2 translations)
3. **Mataguži** - 42.35000°N, 19.41667°E (WikiData: Q2908906, 2 translations)

**Zeta Municipality (2 cities)**:
1. **Golubovci** - 42.36667°N, 19.23333°E (WikiData: Q983622, 9 translations)
2. **Ponari** - 42.40000°N, 19.28333°E (WikiData: Q23932994, 2 translations)

### 3. Data Enrichment Process

The following automated tools were used to ensure data quality:

1. **Import to MySQL**: `import_json_to_mysql.py` - Imported all data and assigned IDs
2. **Timezone Addition**: `add_timezones.py --table both` - Automatically determined IANA timezones from coordinates
3. **Translation Enrichment**: Wikipedia API - Fetched authentic translations from Wikipedia language links
4. **WikiData ID Addition**: Wikipedia API - Obtained WikiData IDs (Q-numbers) for all municipalities and cities
5. **MySQL Sync**: `sync_mysql_to_json.py` - Synced enriched data back to JSON files

## Data Sources

### Primary Sources
- **ISO 3166-2:ME**: https://www.iso.org/obp/ui#iso:code:3166:ME
- **Wikipedia - Municipalities of Montenegro**: https://en.wikipedia.org/wiki/Municipalities_of_Montenegro

### Municipality-Specific Sources
- **Herceg Novi**: https://en.wikipedia.org/wiki/Herceg_Novi_Municipality
- **Tuzi**: https://en.wikipedia.org/wiki/Tuzi_Municipality
- **Zeta**: https://en.wikipedia.org/wiki/Zeta_Municipality

### Coordinate Sources
Coordinates were sourced from Wikipedia articles and cross-referenced with OpenStreetMap data.

## Validation

### Before Fix
```bash
$ jq '.[] | select(.country_code == "ME")' contributions/states/states.json | wc -l
22
```

### After Fix
```bash
$ jq '.[] | select(.country_code == "ME")' contributions/states/states.json | wc -l
25
```

### Verification of New Municipalities
```bash
$ jq '.[] | select(.country_code == "ME" and (.iso3166_2 | IN("ME-08", "ME-24", "ME-25"))) | {name, iso3166_2, timezone}' contributions/states/states.json

{
  "name": "Herceg-Novi",
  "iso3166_2": "ME-08",
  "timezone": "Europe/Podgorica"
}
{
  "name": "Tuzi",
  "iso3166_2": "ME-24",
  "timezone": "Europe/Podgorica"
}
{
  "name": "Zeta",
  "iso3166_2": "ME-25",
  "timezone": "Europe/Podgorica"
}
```

### Database Statistics
- **Total States/Municipalities**: 5,218 (was 5,215)
- **Montenegro Municipalities**: 25 (was 22)
- **Total Cities**: 150,962 (was 150,953)
- **Montenegro Cities**: 43 (was 34)

## Files Changed

### Direct Changes
1. `contributions/states/states.json` - Added 3 municipalities
2. `contributions/cities/ME.json` - Added 9 cities
3. `bin/db/schema.sql` - Auto-updated by sync script

### Quality Metrics

**Municipality Data Quality**:
- ✅ All 3 municipalities have ISO 3166-2 codes
- ✅ All 3 municipalities have accurate coordinates
- ✅ All 3 municipalities have timezones
- ✅ All 3 municipalities have native names (Cyrillic script)
- ✅ All 3 municipalities have WikiData IDs
- ✅ All 3 municipalities have translations (12-14 languages each)

**City Data Quality**:
- ✅ All 9 cities have accurate coordinates
- ✅ All 9 cities have timezones
- ✅ All 9 cities have state_id and state_code
- ✅ 8/9 cities have WikiData IDs (1 city has no WikiData page)
- ✅ 8/9 cities have translations (1 city lacks Wikipedia page)
- ✅ All 9 cities have native names

## Translation Coverage

| Municipality/City | Languages | Sample Languages |
|-------------------|-----------|------------------|
| Herceg-Novi | 14 | ar, de, es, fr, it, ja, ko, nl, pl, pt, ru, tr, uk, zh |
| Tuzi | 12 | de, es, fr, hi, it, ja, ko, nl, pl, pt, ru, uk |
| Zeta | 14 | ar, de, es, fr, it, ja, ko, nl, pl, pt, ru, tr, uk, zh |
| Herceg Novi (city) | 14 | ar, de, es, fr, it, ja, ko, nl, pl, pt, ru, tr, uk, zh |
| Igalo | 7 | de, es, fr, it, ja, nl, ru |
| Golubovci | 9 | es, fr, it, ja, ko, nl, pl, ru, uk |

**Note**: Kamenari does not have a Wikipedia page and therefore has no translations.

## Compliance

This fix brings the Montenegro dataset into full compliance with:
- ✅ ISO 3166-2:ME (25 municipalities)
- ✅ Repository data quality standards (timezone + translations)
- ✅ Geographic accuracy (verified coordinates)
- ✅ Multilingual support (Wikipedia-sourced translations)

## Testing

### Manual Verification Steps Performed
1. ✅ Verified all 25 municipalities are present in states.json
2. ✅ Verified all ISO codes match ISO 3166-2:ME standard
3. ✅ Verified coordinates are accurate (cross-referenced with Wikipedia)
4. ✅ Verified all new entries have timezones
5. ✅ Verified all new entries have translations
6. ✅ Verified MySQL import successful (150,962 cities)
7. ✅ Verified MySQL sync back to JSON successful

### Database Queries
```sql
-- Verify Montenegro municipalities count
SELECT COUNT(*) FROM states WHERE country_code = 'ME';
-- Result: 25

-- Verify new municipalities exist
SELECT id, name, iso3166_2, timezone FROM states 
WHERE country_code = 'ME' AND iso3166_2 IN ('ME-08', 'ME-24', 'ME-25');
-- Results:
-- 5682, Herceg-Novi, ME-08, Europe/Podgorica
-- 5683, Tuzi, ME-24, Europe/Podgorica
-- 5684, Zeta, ME-25, Europe/Podgorica

-- Verify cities for new municipalities
SELECT COUNT(*) FROM cities WHERE country_code = 'ME' AND state_code IN ('08', '24', '25');
-- Result: 9
```

## Notes

- All coordinates are in decimal degrees format (WGS84)
- Timezones automatically detected using timezonefinder library
- Translations sourced from Wikipedia language links (authentic, community-maintained)
- WikiData IDs obtained from Wikipedia pages and cross-referenced with WikiData
- Native names use Cyrillic script (Montenegrin standard)
- One city (Kamenari) has no Wikipedia/WikiData page, thus no WikiData ID or translations - this is acceptable

## Related Issues

This fix addresses the issue raised regarding Montenegro missing 3 municipalities according to ISO 3166-2:ME standard.

---

**Summary**: Successfully added 3 missing Montenegro municipalities (Herceg-Novi, Tuzi, Zeta) and 9 associated cities with complete metadata including timezones and multilingual translations, bringing the total to 25 municipalities in full compliance with ISO 3166-2:ME.
