# Serbia Missing Administrative Divisions Fix

## Issue Reference
**Issue:** [Data]: Serbia autonomous province and district missing
**Link:** https://github.com/dr5hn/countries-states-cities-database/issues/[issue_number]
**Problem:** Serbia was missing 1 autonomous province and 5 districts according to ISO 3166-2:RS standard

## Countries/Regions Addressed
- Serbia (RS)

## Changes Made

### Summary
Added 6 missing administrative divisions to Serbia to match ISO 3166-2:RS standard:
- **Before:** 26 administrative divisions (1 city + 1 autonomous province + 24 districts)
- **After:** 32 administrative divisions (1 city + 2 autonomous provinces + 29 districts)

### Administrative Divisions Added

#### 1. Kosovo-Metohija (RS-KM) - Autonomous Province
```json
{
  "id": 5688,
  "name": "Kosovo-Metohija",
  "iso3166_2": "RS-KM",
  "type": "province",
  "native": "Косово и Метохија",
  "latitude": "42.66666667",
  "longitude": "21.16666667",
  "timezone": "Europe/Belgrade",
  "translations": {
    "ar": "مقاطعة كوسوفو وميتوهيا ذاتية الحكم",
    "de": "Kosovo und Metochien",
    "es": "Provincia Autónoma de Kosovo y Metojia",
    "fr": "Kosovo-et-Métochie",
    "ja": "コソボ・メトヒヤ自治州"
    // ... 14 languages total
  }
}
```

#### 2. Kosovo District (RS-25)
```json
{
  "id": 5689,
  "name": "Kosovo",
  "iso3166_2": "RS-25",
  "type": "district",
  "native": "Косово",
  "latitude": "42.66333333",
  "longitude": "21.16222222",
  "translations": {
    "ar": "كوسوفو",
    "de": "Kosovo",
    "ja": "コソボ"
    // ... 18 languages total
  }
}
```

#### 3. Peć District (RS-26)
```json
{
  "id": 5690,
  "name": "Peć",
  "iso3166_2": "RS-26",
  "type": "district",
  "native": "Пећ",
  "latitude": "42.66000000",
  "longitude": "20.28800000",
  "translations": {
    "ar": "بيخا",
    "de": "Peja",
    "ja": "ペーチ"
    // ... 15 languages total
  }
}
```

#### 4. Prizren District (RS-27)
```json
{
  "id": 5691,
  "name": "Prizren",
  "iso3166_2": "RS-27",
  "type": "district",
  "native": "Призрен",
  "latitude": "42.21277778",
  "longitude": "20.73916667",
  "translations": {
    "ar": "برزرين",
    "de": "Prizren",
    "ja": "プリズレン"
    // ... 16 languages total
  }
}
```

#### 5. Kosovska Mitrovica District (RS-28)
```json
{
  "id": 5692,
  "name": "Kosovska Mitrovica",
  "iso3166_2": "RS-28",
  "type": "district",
  "native": "Косовска Митровица",
  "latitude": "42.88333333",
  "longitude": "20.86666667",
  "translations": {
    "ar": "ميتروفيتسا",
    "de": "Mitrovica (Kosovo)",
    "ja": "コソフスカ・ミトロヴィツァ"
    // ... 15 languages total
  }
}
```

#### 6. Kosovo-Pomoravlje District (RS-29)
```json
{
  "id": 5693,
  "name": "Kosovo-Pomoravlje",
  "iso3166_2": "RS-29",
  "type": "district",
  "native": "Косовско-Поморавље",
  "latitude": "42.53330000",
  "longitude": "21.56670000",
  "translations": {
    "ru": "Косовское Поморавье",
    "de": "Kosovo-Pomoravlje",
    "ja": "コソボ・ポモラヴリェ"
    // ... 13 languages total
  }
}
```

## Validation Steps

### 1. Verify ISO 3166-2:RS Standard Compliance
**Source:** https://www.iso.org/obp/ui#iso:code:3166:RS

Checked that all 32 divisions match ISO standard:
- ✅ 1 city (RS-00 Belgrade)
- ✅ 2 autonomous provinces (RS-VO Vojvodina, RS-KM Kosovo-Metohija)
- ✅ 29 districts (RS-01 through RS-29, excluding already numbered)

### 2. Wikipedia Verification
**Sources:**
- https://en.wikipedia.org/wiki/Administrative_districts_of_Serbia
- https://en.wikipedia.org/wiki/Autonomous_Province_of_Kosovo_and_Metohija

Verified:
- ✅ All names match Serbian administrative structure
- ✅ Coordinates verified from Wikipedia API
- ✅ Native names confirmed (Cyrillic script)

### 3. Database Validation
```bash
# Count Serbia administrative divisions
jq '[.[] | select(.country_code == "RS")] | length' contributions/states/states.json
# Result: 32 ✅

# Verify by type
jq '[.[] | select(.country_code == "RS")] | group_by(.type) | map({type: .[0].type, count: length})' contributions/states/states.json
# Result: 
# - city: 1
# - district: 29
# - province: 2
# ✅ Matches ISO standard
```

### 4. Translation Enrichment
```bash
# Run translation enricher
python3 bin/scripts/validation/translation_enricher.py \
  --file contributions/states/states.json \
  --type state \
  --country-code RS \
  --force-update

# Statistics:
# Total records: 32
# Translations added: 6 ✅
# Translations updated: 26 🔄
```

### 5. MySQL Import/Export Validation
```bash
# Import to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py --host 127.0.0.1 --user root --password root
# ✅ States: 5227 (was 5221, added 6)

# Sync back to JSON to assign IDs
python3 bin/scripts/sync/sync_mysql_to_json.py --host 127.0.0.1 --user root --password root
# ✅ All 6 new entries now have auto-assigned IDs (5688-5693)
```

## Data Quality

All 6 new administrative divisions include:
- ✅ `id` - Auto-assigned by MySQL
- ✅ `name` - Official English name
- ✅ `native` - Native name in Cyrillic script
- ✅ `country_id` - Foreign key (196 for Serbia)
- ✅ `country_code` - ISO 2-letter code (RS)
- ✅ `iso2` - Administrative code
- ✅ `iso3166_2` - Full ISO code (RS-XX)
- ✅ `type` - province or district
- ✅ `latitude` - Decimal coordinates
- ✅ `longitude` - Decimal coordinates
- ✅ `timezone` - IANA timezone (Europe/Belgrade)
- ✅ `translations` - 13-18 languages per entry
- ✅ `created_at` - Auto-managed timestamp
- ✅ `updated_at` - Auto-managed timestamp
- ✅ `flag` - Auto-managed (value: 1)

## Political Context

**Note:** These administrative divisions are part of Serbia's official administrative structure according to Serbian law and the ISO 3166-2 standard. The territory of Kosovo declared independence in 2008 and is recognized by 108 UN members, but Serbia still considers it an autonomous province. This database follows the ISO 3166-2 standard which reflects Serbia's legal position.

The five Kosovo-related districts (RS-25, RS-26, RS-27, RS-28, RS-29) and the Kosovo-Metohija autonomous province (RS-KM) are included to ensure:
1. Compliance with ISO 3166-2:RS standard
2. Completeness of Serbia's claimed administrative structure
3. Consistency with other international databases

## References

### Official Standards
- ISO 3166-2:RS: https://www.iso.org/obp/ui#iso:code:3166:RS

### Wikipedia Sources
- Administrative districts of Serbia: https://en.wikipedia.org/wiki/Administrative_districts_of_Serbia
- Autonomous Province of Kosovo and Metohija: https://en.wikipedia.org/wiki/Autonomous_Province_of_Kosovo_and_Metohija
- Kosovo District: https://en.wikipedia.org/wiki/Kosovo_District
- Peć District (Serbia): https://en.wikipedia.org/wiki/Peć_District_(Serbia)
- Prizren District (Serbia): https://en.wikipedia.org/wiki/Prizren_District_(Serbia)
- Kosovska Mitrovica District (Serbia): https://en.wikipedia.org/wiki/Kosovska_Mitrovica_District_(Serbia)
- Kosovo-Pomoravlje District: https://en.wikipedia.org/wiki/Kosovo-Pomoravlje_District

### Wikipedia API Coordinates
- Autonomous Province of Kosovo and Metohija: 42.66666667, 21.16666667
- Kosovo District (Pristina): 42.66333333, 21.16222222
- Prizren District: 42.21277778, 20.73916667
- Kosovska Mitrovica District: 42.88333333, 20.86666667
- Kosovo-Pomoravlje District: 42.53330000, 21.56670000

## Impact

### Database Changes
- ✅ Total states increased from 5,221 to 5,227
- ✅ Serbia administrative divisions complete (32 total)
- ✅ All entries have full translations and metadata
- ✅ No breaking changes to API structure

### Compliance
- ✅ Now fully compliant with ISO 3166-2:RS
- ✅ Matches official Serbian administrative structure
- ✅ Consistent with Wikipedia and other geographic databases

## Files Modified
- `contributions/states/states.json` - Added 6 new administrative divisions
- `bin/db/schema.sql` - Updated via MySQL sync (auto-generated)

## Next Steps
No further action needed. The database now contains all 32 administrative divisions for Serbia as specified in ISO 3166-2:RS.
