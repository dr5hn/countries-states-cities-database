# Italy Missing Metropolitan Cities and Autonomous Provinces - Fix

## Issue Reference
**GitHub Issue:** [Data]: Italy metropolitan city and autonomous province missing  
**Problem:** Italy was missing 13 metropolitan cities and 2 autonomous provinces according to ISO 3166-2:IT standard

## Countries/Regions Addressed
- **Country:** Italy (IT)
- **Total states added:** 15 (13 metropolitan cities + 2 autonomous provinces)

## Changes Made

### Before
- **Metropolitan cities:** 1 (only Palermo)
- **Autonomous provinces:** 0
- **Total Italian administrative divisions:** 111

### After
- **Metropolitan cities:** 14 (ISO standard ✓)
- **Autonomous provinces:** 2 (ISO standard ✓)
- **Total Italian administrative divisions:** 126 (ISO standard ✓)

### Fields Added to Each State
All 15 new states include complete data:
- ✅ `name` - Official English name
- ✅ `native` - Native Italian name
- ✅ `iso2` - 2-letter ISO code
- ✅ `iso3166_2` - Full ISO 3166-2 code
- ✅ `country_id` - 107 (Italy)
- ✅ `country_code` - IT
- ✅ `type` - "metropolitan city" or "autonomous province"
- ✅ `level` - 1
- ✅ `parent_id` - Reference to parent region
- ✅ `latitude` - Decimal coordinates
- ✅ `longitude` - Decimal coordinates
- ✅ `timezone` - Europe/Rome
- ✅ `wikiDataId` - WikiData identifier
- ✅ `translations` - 11 languages (ar, de, es, fr, hi, it, ja, ko, pt, ru, zh)
- ✅ `fips_code` - 16 (Italy FIPS code)

## Metropolitan Cities Added

### 1. Bari (IT-BA)
- **Native:** Bari
- **Parent Region:** Apulia (IT-75, id: 1688)
- **Coordinates:** 41.11714300, 16.87187200
- **WikiData:** Q18684135
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 2. Bologna (IT-BO)
- **Native:** Bologna
- **Parent Region:** Emilia-Romagna (IT-45, id: 1773)
- **Coordinates:** 44.49488700, 11.34262100
- **WikiData:** Q18288155
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 3. Cagliari (IT-CA)
- **Native:** Cagliari
- **Parent Region:** Sardinia (IT-88, id: 1715)
- **Coordinates:** 39.22380400, 9.12166700
- **WikiData:** Q18241891
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 4. Catania (IT-CT)
- **Native:** Catania
- **Parent Region:** Sicily (IT-82, id: 1709)
- **Coordinates:** 37.50287800, 15.08704200
- **WikiData:** Q18241870
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 5. Florence (IT-FI)
- **Native:** Firenze
- **Parent Region:** Tuscany (IT-52, id: 1664)
- **Coordinates:** 43.76923100, 11.25588400
- **WikiData:** Q18288162
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 6. Genoa (IT-GE)
- **Native:** Genova
- **Parent Region:** Liguria (IT-42, id: 1768)
- **Coordinates:** 44.41149100, 8.93285900
- **WikiData:** Q18288197
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 7. Messina (IT-ME)
- **Native:** Messina
- **Parent Region:** Sicily (IT-82, id: 1709)
- **Coordinates:** 38.19395000, 15.55256200
- **WikiData:** Q18241892
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 8. Milan (IT-MI)
- **Native:** Milano
- **Parent Region:** Lombardy (IT-25, id: 1705)
- **Coordinates:** 45.46679400, 9.19007200
- **WikiData:** Q18288187
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 9. Naples (IT-NA)
- **Native:** Napoli
- **Parent Region:** Campania (IT-72, id: 1669)
- **Coordinates:** 40.85177700, 14.26811700
- **WikiData:** Q18241895
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 10. Reggio Calabria (IT-RC)
- **Native:** Reggio Calabria
- **Parent Region:** Calabria (IT-78, id: 1703)
- **Coordinates:** 38.10882200, 15.64392200
- **WikiData:** Q18241896
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 11. Rome (IT-RM)
- **Native:** Roma
- **Parent Region:** Lazio (IT-62, id: 1678)
- **Coordinates:** 41.89277000, 12.48366000
- **WikiData:** Q18288203
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 12. Turin (IT-TO)
- **Native:** Torino
- **Parent Region:** Piedmont (IT-21, id: 1702)
- **Coordinates:** 45.07049600, 7.68682200
- **WikiData:** Q18288204
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 13. Venice (IT-VE)
- **Native:** Venezia
- **Parent Region:** Veneto (IT-34, id: 1753)
- **Coordinates:** 45.43409700, 12.33890600
- **WikiData:** Q18288217
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

## Autonomous Provinces Added

### 14. South Tyrol (IT-BZ)
- **Native:** Bolzano (also known as Alto Adige in Italian, Südtirol in German)
- **Parent Region:** Trentino-South Tyrol (IT-32, id: 1725)
- **Coordinates:** 46.49933500, 11.35662200
- **WikiData:** Q15124
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

### 15. Trentino (IT-TN)
- **Native:** Trento
- **Parent Region:** Trentino-South Tyrol (IT-32, id: 1725)
- **Coordinates:** 46.06787800, 11.12108300
- **WikiData:** Q16290
- **Timezone:** Europe/Rome
- **Translations:** 11 languages

## Validation Steps

### 1. Verify ISO 3166-2:IT Compliance
```bash
# Check current counts by type
jq '[.[] | select(.country_code == "IT")] | group_by(.type) | map({type: .[0].type, count: length})' \
  contributions/states/states.json
```
**Expected Result:** 
- 15 regions ✓
- 80 provinces ✓
- 6 free municipal consortiums ✓
- 14 metropolitan cities ✓
- 2 autonomous provinces ✓
- 5 autonomous regions ✓
- 4 decentralized regional entities ✓

**Actual Result:** All counts match ISO standard ✓

### 2. Verify Data Completeness
```bash
# Check Milan metropolitan city as example
jq '[.[] | select(.iso3166_2 == "IT-MI")] | .[0]' contributions/states/states.json
```
**Expected Fields:**
- name, native, iso2, iso3166_2
- country_id, country_code
- type, level, parent_id
- latitude, longitude
- timezone, wikiDataId
- translations (at least 10+ languages)

**Actual Result:** All required fields present ✓

### 3. Verify Timezone Consistency
```bash
# All Italian states should have Europe/Rome timezone
jq '[.[] | select(.country_code == "IT" and (.iso3166_2 | test("IT-BA|IT-BO|IT-CA|IT-CT|IT-FI|IT-GE|IT-ME|IT-MI|IT-NA|IT-RC|IT-RM|IT-TO|IT-VE|IT-BZ|IT-TN")))] | .[].timezone' \
  contributions/states/states.json | sort | uniq
```
**Expected Result:** "Europe/Rome" only  
**Actual Result:** All 15 states have "Europe/Rome" timezone ✓

### 4. Verify Translations
```bash
# Check that all new states have translations
jq '[.[] | select(.country_code == "IT" and (.iso3166_2 | test("IT-BA|IT-BO|IT-CA|IT-CT|IT-FI|IT-GE|IT-ME|IT-MI|IT-NA|IT-RC|IT-RM|IT-TO|IT-VE|IT-BZ|IT-TN")))] | map({name: .name, translation_count: (.translations | length)})' \
  contributions/states/states.json
```
**Expected Result:** Each state has 11 translations  
**Actual Result:** All states have 11 translations (ar, de, es, fr, hi, it, ja, ko, pt, ru, zh) ✓

### 5. Verify WikiData IDs
All WikiData IDs verified against https://www.wikidata.org/:
- Q18684135 (Bari) ✓
- Q18288155 (Bologna) ✓
- Q18241891 (Cagliari) ✓
- Q18241870 (Catania) ✓
- Q18288162 (Florence) ✓
- Q18288197 (Genoa) ✓
- Q18241892 (Messina) ✓
- Q18288187 (Milan) ✓
- Q18241895 (Naples) ✓
- Q18241896 (Reggio Calabria) ✓
- Q18288203 (Rome) ✓
- Q18288204 (Turin) ✓
- Q18288217 (Venice) ✓
- Q15124 (South Tyrol) ✓
- Q16290 (Trentino) ✓

## Data Sample

### Example: Milan Metropolitan City
```json
{
  "name": "Milan",
  "country_id": 107,
  "country_code": "IT",
  "fips_code": "16",
  "iso2": "MI",
  "iso3166_2": "IT-MI",
  "type": "metropolitan city",
  "level": 1,
  "parent_id": 1705,
  "native": "Milano",
  "latitude": "45.46679400",
  "longitude": "9.19007200",
  "wikiDataId": "Q18288187",
  "timezone": "Europe/Rome",
  "translations": {
    "ar": "ميلانو",
    "de": "Mailand",
    "es": "Milán",
    "fr": "Milan",
    "hi": "मिलान",
    "it": "Milano",
    "ja": "ミラノ",
    "ko": "밀라노",
    "pt": "Milão",
    "ru": "Милан",
    "zh": "米兰"
  }
}
```

### Example: South Tyrol Autonomous Province
```json
{
  "name": "South Tyrol",
  "country_id": 107,
  "country_code": "IT",
  "fips_code": "16",
  "iso2": "BZ",
  "iso3166_2": "IT-BZ",
  "type": "autonomous province",
  "level": 1,
  "parent_id": 1725,
  "native": "Bolzano",
  "latitude": "46.49933500",
  "longitude": "11.35662200",
  "wikiDataId": "Q15124",
  "timezone": "Europe/Rome",
  "translations": {
    "ar": "تيرول الجنوبية",
    "de": "Südtirol",
    "es": "Tirol del Sur",
    "fr": "Tyrol du Sud",
    "hi": "दक्षिण टिरोल",
    "it": "Alto Adige",
    "ja": "南チロル",
    "ko": "남티롤",
    "pt": "Tirol do Sul",
    "ru": "Южный Тироль",
    "zh": "南蒂罗尔"
  }
}
```

## References

### ISO Standard
- **ISO 3166-2:IT:** https://www.iso.org/obp/ui#iso:code:3166:IT
- Official standard defining Italian administrative divisions

### Wikipedia Articles
- **Italy:** https://en.wikipedia.org/wiki/Italy
- **Metropolitan Cities of Italy:** https://en.wikipedia.org/wiki/Metropolitan_cities_of_Italy
- **Provinces of Italy:** https://en.wikipedia.org/wiki/Provinces_of_Italy
- **ISO 3166-2:IT:** https://en.wikipedia.org/wiki/ISO_3166-2:IT

### WikiData Entities
All 15 states verified against WikiData:
- Metropolitan cities: Q18684135, Q18288155, Q18241891, Q18241870, Q18288162, Q18288197, Q18241892, Q18288187, Q18241895, Q18241896, Q18288203, Q18288204, Q18288217
- Autonomous provinces: Q15124, Q16290

## Impact

### Data Quality Improvements
- ✅ **ISO 3166-2 Compliance:** Italy now fully complies with ISO 3166-2:IT standard
- ✅ **Complete Administrative Coverage:** All 126 Italian administrative divisions now present
- ✅ **High Data Quality:** All new states include timezone, translations, WikiData IDs, and complete metadata
- ✅ **Geographic Accuracy:** Coordinates verified against Wikipedia and WikiData

### API Changes
- **Non-breaking change:** New states added to existing data structure
- **Filter compatibility:** Existing filters by type, region, etc. will work correctly
- **State count:** Italy now returns 126 states instead of 111

### Database Statistics
| Administrative Type | Count |
|---------------------|-------|
| Regions | 15 |
| Provinces | 80 |
| Free Municipal Consortiums | 6 |
| Metropolitan Cities | 14 |
| Autonomous Provinces | 2 |
| Autonomous Regions | 5 |
| Decentralized Regional Entities | 4 |
| **Total** | **126** |

## Notes

### Translation Quality
- Translations sourced from Wikipedia language links
- 11 languages provided for each state (Arabic, German, Spanish, French, Hindi, Italian, Japanese, Korean, Portuguese, Russian, Chinese)
- Native names reflect official Italian designations

### Special Cases
- **South Tyrol (IT-BZ):** Bilingual region with German name "Südtirol" and Italian name "Alto Adige"
- **Trentino (IT-TN):** Autonomous province within Trentino-South Tyrol autonomous region

### Future Enhancements
- Cities for these metropolitan cities will be added in a follow-up (cities currently exist but may need state_id updates)
- Population data can be added when available from official sources
