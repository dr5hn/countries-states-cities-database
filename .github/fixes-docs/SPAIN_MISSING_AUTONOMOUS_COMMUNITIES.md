# Fix: Missing Spanish Autonomous Communities

## Issue Reference
**Title:** [Data]: Spain autonomous community missing  
**Problem:** Spain was missing 3 autonomous communities according to ISO 3166-2:ES standard

## Countries/Regions Addressed
- Spain (ES)

## Changes Made

### Added 3 Missing Autonomous Communities

According to ISO 3166-2:ES standard, Spain should have 17 autonomous communities + 2 autonomous cities + 50 provinces. The database only had 14 autonomous communities before this fix.

**Missing autonomous communities added:**

1. **Asturias, Principality of** (ES-AS)
   - ISO2: AS
   - ISO 3166-2: ES-AS
   - WikiData ID: Q3934
   - Native: Principado de Asturias
   - Coordinates: 43.36138889, -5.84777778
   - Timezone: Europe/Madrid
   - Note: Previously only existed as province "Asturias" (ES-O)

2. **Cantabria** (ES-CB)
   - ISO2: CB
   - ISO 3166-2: ES-CB
   - WikiData ID: Q3946
   - Native: Cantabria
   - Coordinates: 43.33333333, -4.00000000
   - Timezone: Europe/Madrid
   - Note: Previously only existed as province "Cantabria" (ES-S)

3. **La Rioja** (ES-RI)
   - ISO2: RI
   - ISO 3166-2: ES-RI
   - WikiData ID: Q5727
   - Native: La Rioja
   - Coordinates: 42.25000000, -2.50000000
   - Timezone: Europe/Madrid
   - Note: Previously only existed as province "La Rioja" (ES-LO)

### Before/After Statistics

| Type | Before | After |
|------|--------|-------|
| Autonomous Communities | 14 | 17 ✅ |
| Autonomous Cities | 2 | 2 |
| Provinces | 50 | 50 |
| **Total** | **66** | **69** |

## Validation Steps

### 1. Verified ISO 3166-2:ES Standard
Source: https://www.iso.org/obp/ui#iso:code:3166:ES

**Expected administrative divisions:**
- 17 autonomous communities
- 2 autonomous cities  
- 50 provinces

### 2. Validated with Wikipedia

**Asturias:**
```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Principality of Asturias" \
    --type state \
    --country ES
```
Expected: Article found with WikiData ID Q3934  
Actual: ✅ Confirmed - "Asturias officially the Principality of Asturias, is an autonomous community in northwest Spain."

**Cantabria:**
```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Cantabria" \
    --type state \
    --country ES
```
Expected: Article found with WikiData ID Q3946  
Actual: ✅ Confirmed - "Cantabria is an autonomous community and province in northern Spain."

**La Rioja:**
```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "La Rioja (Spain)" \
    --type state \
    --country ES
```
Expected: Article found with WikiData ID Q5727  
Actual: ✅ Confirmed - "La Rioja is an autonomous community and province in Spain."

### 3. Enriched with Translations

Added translations for all three autonomous communities in 16-18 languages using Wikipedia language links:

**Languages covered:**
Arabic (ar), Bengali (bn), German (de), Spanish (es), French (fr), Hindi (hi), Indonesian (id), Italian (it), Japanese (ja), Korean (ko), Dutch (nl), Polish (pl), Portuguese (pt), Russian (ru), Turkish (tr), Ukrainian (uk), Vietnamese (vi), Chinese (zh)

### 4. Verified Final Count

```bash
cat contributions/states/states.json | jq '[.[] | select(.country_code == "ES")] | group_by(.type) | map({type: .[0].type, count: length})'
```

Expected:
- 17 autonomous communities
- 2 autonomous cities
- 50 provinces

Actual: ✅ Confirmed

## Data Samples

### Asturias, Principality of Entry
```json
{
  "name": "Asturias, Principality of",
  "country_id": 207,
  "country_code": "ES",
  "fips_code": "34",
  "iso2": "AS",
  "iso3166_2": "ES-AS",
  "type": "autonomous community",
  "level": null,
  "parent_id": null,
  "native": "Principado de Asturias",
  "latitude": "43.36138889",
  "longitude": "-5.84777778",
  "timezone": "Europe/Madrid",
  "wikiDataId": "Q3934",
  "population": null,
  "translations": {
    "ar": "أشتورية",
    "bn": "আস্তুরিয়াস",
    "de": "Asturien",
    "es": "Principado de Asturias",
    "fr": "Asturies",
    "hi": "ऑस्टुरियस",
    "id": "Asturias",
    "it": "Asturie",
    "ja": "アストゥリアス州",
    "ko": "아스투리아스 지방",
    "nl": "Asturië",
    "pl": "Asturia",
    "pt": "Astúrias",
    "ru": "Астурия",
    "tr": "Asturias",
    "uk": "Астурія",
    "vi": "Asturias",
    "zh": "阿斯图里亚斯"
  }
}
```

### Cantabria Entry
```json
{
  "name": "Cantabria",
  "country_id": 207,
  "country_code": "ES",
  "fips_code": "39",
  "iso2": "CB",
  "iso3166_2": "ES-CB",
  "type": "autonomous community",
  "level": null,
  "parent_id": null,
  "native": "Cantabria",
  "latitude": "43.33333333",
  "longitude": "-4.00000000",
  "timezone": "Europe/Madrid",
  "wikiDataId": "Q3946",
  "population": null,
  "translations": {
    "ar": "قنطبرية",
    "bn": "কান্তাব্রিয়া",
    "de": "Kantabrien",
    "es": "Cantabria",
    "fr": "Cantabrie",
    "hi": "कैंटाब्रिया",
    "id": "Cantabria",
    "it": "Cantabria",
    "ja": "カンタブリア州",
    "ko": "칸타브리아 지방",
    "nl": "Cantabrië",
    "pl": "Kantabria",
    "pt": "Cantábria",
    "ru": "Кантабрия",
    "tr": "Kantabria",
    "uk": "Кантабрія",
    "vi": "Cantabria"
  }
}
```

### La Rioja Entry
```json
{
  "name": "La Rioja",
  "country_id": 207,
  "country_code": "ES",
  "fips_code": "27",
  "iso2": "RI",
  "iso3166_2": "ES-RI",
  "type": "autonomous community",
  "level": null,
  "parent_id": null,
  "native": "La Rioja",
  "latitude": "42.25000000",
  "longitude": "-2.50000000",
  "timezone": "Europe/Madrid",
  "wikiDataId": "Q5727",
  "population": null,
  "translations": {
    "ar": "منطقة لا ريوخا",
    "de": "La Rioja",
    "es": "La Rioja",
    "fr": "La Rioja",
    "hi": "ला रियोजा",
    "id": "La Rioja",
    "it": "La Rioja",
    "ja": "ラ・リオハ州",
    "ko": "라리오하 지방",
    "nl": "La Rioja",
    "pl": "La Rioja",
    "pt": "La Rioja",
    "ru": "Ла-Риоха",
    "tr": "La Rioja",
    "uk": "Ла-Ріоха",
    "vi": "La Rioja",
    "zh": "拉里奥哈"
  }
}
```

## Key Distinctions

### Autonomous Community vs Province
In Spain's administrative structure:
- **Autonomous Community** (comunidad autónoma): First-level administrative division with its own government
- **Province** (provincia): Traditional administrative division, some coincide with autonomous communities

For Asturias, Cantabria, and La Rioja:
- Each is both an autonomous community AND a province
- The autonomous community entry (ES-AS, ES-CB, ES-RI) represents the political entity
- The province entry (ES-O, ES-S, ES-LO) represents the traditional division

This dual nature is similar to other Spanish regions like:
- Community of Madrid (ES-MD) and Madrid province (ES-M)
- Region of Murcia (ES-MC) and Murcia province (ES-MU)

## References
- Wikipedia: https://en.wikipedia.org/wiki/Autonomous_communities_of_Spain
- Wikipedia - Asturias: https://en.wikipedia.org/wiki/Asturias
- Wikipedia - Cantabria: https://en.wikipedia.org/wiki/Cantabria
- Wikipedia - La Rioja: https://en.wikipedia.org/wiki/La_Rioja_(Spain)
- WikiData - Asturias: https://www.wikidata.org/wiki/Q3934
- WikiData - Cantabria: https://www.wikidata.org/wiki/Q3946
- WikiData - La Rioja: https://www.wikidata.org/wiki/Q5727
- ISO 3166-2:ES: https://www.iso.org/obp/ui#iso:code:3166:ES

## Impact
- ✅ Database now complies with ISO 3166-2:ES standard
- ✅ All 17 autonomous communities of Spain are now represented
- ✅ Improved data completeness for Spanish administrative divisions
- ✅ Added rich metadata including WikiData IDs, coordinates, timezones, and translations
- ✅ No breaking changes - only additions to the dataset
- ✅ Maintains consistency with existing Spain data structure

## Data Quality
All new entries include:
- ✅ Official names verified against Wikipedia
- ✅ Native language names
- ✅ WikiData IDs for authoritative cross-referencing
- ✅ Precise coordinates from WikiData
- ✅ IANA timezone identifiers
- ✅ Translations in 16-18 major world languages
- ✅ ISO 3166-2 codes
- ✅ Proper type classification (autonomous community)
