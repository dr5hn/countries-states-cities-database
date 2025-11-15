# Libya Missing Al Butnan Populare Fix

## Issue Reference
**Issue:** [Data]: Libya popularate missing  
**Problem:** Libya was missing 1 out of 22 popularates according to ISO 3166-2:LY standard. The database had 21 popularates while the ISO standard requires 22.

## Countries/Regions Addressed
- Libya (LY)

## Changes Made

### State Addition
**Al Butnan Populare (LY-BU)**

Before:
- Libya states count: 21
- Missing: Al Butnan (Butnan District)

After:
- Libya states count: 22 ✅
- All ISO 3166-2:LY popularates present ✅

#### Al Butnan State Details
```json
{
  "id": 5641,
  "name": "Al Butnan",
  "country_id": 124,
  "country_code": "LY",
  "iso2": "BU",
  "iso3166_2": "LY-BU",
  "type": "popularate",
  "native": "البطنان",
  "latitude": "30.00000000",
  "longitude": "24.00000000",
  "timezone": "Africa/Tripoli",
  "translations": {
    "ar": "شعبية البطنان",
    "de": "Munizip al-Butnan",
    "es": "Distrito de Al Butnan",
    "fr": "Al Boutnan",
    "id": "Butnan",
    "it": "Distretto di al-Butnan",
    "ja": "ブトナーン県",
    "ko": "부트난주",
    "nl": "Al Butnan",
    "pl": "Al-Butnan",
    "pt": "Butnane",
    "ru": "Эль-Бутнан",
    "tr": "Butnân (il)",
    "uk": "Ель-Бутнан (муніципалітет)",
    "zh": "布特南省"
  },
  "wikiDataId": "Q25931"
}
```

### Cities Addition
**3 major cities added for Al Butnan district**

Before:
- Libya cities count: 51
- Butnan District cities: 0

After:
- Libya cities count: 54 ✅
- Butnan District cities: 3 ✅

#### 1. Tobruk (Capital)
```json
{
  "id": 157091,
  "name": "Tobruk",
  "state_id": 5641,
  "state_code": "BU",
  "country_id": 124,
  "country_code": "LY",
  "latitude": "32.07611111",
  "longitude": "23.96138889",
  "native": "طبرق",
  "timezone": "Africa/Tripoli",
  "translations": {
    "ar": "طبرق",
    "bn": "তোবরুক",
    "de": "Tobruk",
    "es": "Tobruk",
    "fr": "Tobrouk",
    "id": "Thubruq",
    "it": "Tobruch",
    "ja": "トブルク",
    "ko": "투브루크",
    "nl": "Tobroek",
    "pl": "Tobruk",
    "pt": "Tobruque",
    "ru": "Тобрук",
    "tr": "Tobruk",
    "uk": "Тобрук",
    "vi": "Tobruk",
    "zh": "图卜鲁格"
  },
  "wikiDataId": "Q182092"
}
```

#### 2. Bardia
```json
{
  "id": 157092,
  "name": "Bardia",
  "state_id": 5641,
  "state_code": "BU",
  "country_id": 124,
  "country_code": "LY",
  "latitude": "31.76000000",
  "longitude": "25.07500000",
  "native": "البردية",
  "timezone": "Africa/Tripoli",
  "translations": {
    "ar": "البردية",
    "de": "Bardia",
    "es": "Bardia",
    "fr": "Bardiyah",
    "pt": "Bardia",
    "ru": "Бардия",
    "zh": "班迪亚"
  },
  "wikiDataId": "Q141687"
}
```

#### 3. Jaghbub
```json
{
  "id": 157093,
  "name": "Jaghbub",
  "state_id": 5641,
  "state_code": "BU",
  "country_id": 124,
  "country_code": "LY",
  "latitude": "29.74250000",
  "longitude": "24.51694444",
  "native": "الجغبوب",
  "timezone": "Africa/Tripoli",
  "translations": {
    "ar": "الجغبوب",
    "de": "Al-Dschaghbub",
    "es": "Al Jaghbub",
    "fr": "Jaghboub",
    "it": "Giarabub",
    "ja": "ジャグブーブ",
    "ko": "자그부브",
    "pt": "Jaghbub",
    "ru": "Джагбуб",
    "zh": "杰格卜卜"
  },
  "wikiDataId": "Q284251"
}
```

## Validation Steps

### 1. Wikipedia Validation
```bash
# Validated Al Butnan District
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Butnan District" \
    --type state \
    --country LY \
    --output /tmp/butnan_report.json
```

**Expected result:** Found article with WikiData ID Q25931  
**Actual result:** ✅ Found "Butnan District" with correct WikiData ID

```bash
# Validated Tobruk city
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Tobruk" \
    --type city \
    --country LY \
    --output /tmp/tobruk_report.json
```

**Expected result:** Found article with WikiData ID Q182092  
**Actual result:** ✅ Found "Tobruk" with correct WikiData ID

### 2. ISO 3166-2 Compliance Check
Verified all 22 popularates from ISO 3166-2:LY standard:
- ✅ LY-BU - Al Butnan (ADDED)
- ✅ LY-JA - Al Jabal al Akhdar
- ✅ LY-JG - Al Jabal al Gharbi
- ✅ LY-JI - Al Jafarah
- ✅ LY-JU - Al Jufrah
- ✅ LY-KF - Al Kufrah
- ✅ LY-MJ - Al Marj
- ✅ LY-MB - Al Marqab
- ✅ LY-WA - Al Wahat
- ✅ LY-NQ - An Nuqat al Khams
- ✅ LY-ZA - Az Zawiyah
- ✅ LY-BA - Banghazi
- ✅ LY-DR - Darnah
- ✅ LY-GT - Ghat
- ✅ LY-MI - Misratah
- ✅ LY-MQ - Murzuq
- ✅ LY-NL - Nalut
- ✅ LY-SB - Sabha
- ✅ LY-SR - Surt
- ✅ LY-WD - Wadi al Hayat
- ✅ LY-WS - Wadi ash Shati'
- ✅ LY-TB - Tarabulus

**Result:** All 22 popularates present ✅

### 3. Database Validation
```bash
# Check Libya states count
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM states WHERE country_code = 'LY';"
```

**Expected:** 22 states  
**Actual:** 22 states ✅

```bash
# Check Libya cities count
mysql -uroot -proot -e "USE world; SELECT COUNT(*) FROM cities WHERE country_code = 'LY';"
```

**Expected:** 54 cities  
**Actual:** 54 cities ✅

```bash
# Verify Al Butnan state
mysql -uroot -proot -e "USE world; SELECT name, iso2, timezone, wikiDataId FROM states WHERE country_code = 'LY' AND iso2 = 'BU';"
```

**Expected:** Al Butnan with timezone Africa/Tripoli and WikiData Q25931  
**Actual:** ✅ Confirmed

```bash
# Verify Butnan cities
mysql -uroot -proot -e "USE world; SELECT name, timezone, wikiDataId FROM cities WHERE country_code = 'LY' AND state_code = 'BU';"
```

**Expected:** 3 cities (Tobruk, Bardia, Jaghbub) with timezone Africa/Tripoli  
**Actual:** ✅ All 3 cities present with correct data

### 4. Timezone Enrichment
```bash
# Added timezones to state
python3 bin/scripts/validation/add_timezones.py --table states --password root
```

**Result:** ✅ Al Butnan assigned Africa/Tripoli timezone

```bash
# Added timezones to cities
python3 bin/scripts/validation/add_timezones.py --table cities --password root
```

**Result:** ✅ All 3 Butnan cities assigned Africa/Tripoli timezone

### 5. Translation Enrichment
```bash
# Added translations to state
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/states/states.json \
    --type state \
    --country-code LY
```

**Result:** ✅ Al Butnan enriched with 15 language translations

```bash
# Added translations to cities
python3 bin/scripts/validation/translation_enricher.py \
    --file contributions/cities/LY.json \
    --type city
```

**Result:** ✅ All 3 Butnan cities enriched with translations (17, 7, and 10 languages respectively)

### 6. JSON Structure Validation
```bash
# Verify JSON syntax is valid
jq 'length' contributions/states/states.json
jq 'length' contributions/cities/LY.json
```

**Result:** ✅ Both files have valid JSON syntax

## References

### Official Sources
- **ISO 3166-2:LY**: https://www.iso.org/obp/ui#iso:code:3166:LY
  - Official ISO standard listing all 22 popularates of Libya

### Wikipedia Sources
- **Butnan District**: https://en.wikipedia.org/wiki/Butnan_District
  - WikiData: https://www.wikidata.org/wiki/Q25931
  - Coordinates: 30°N 24°E
  - Capital: Tobruk

- **Tobruk**: https://en.wikipedia.org/wiki/Tobruk
  - WikiData: https://www.wikidata.org/wiki/Q182092
  - Coordinates: 32.076111°N, 23.961389°E
  - Population: ~120,000 (2011)

- **Bardia**: https://en.wikipedia.org/wiki/Bardia
  - WikiData: https://www.wikidata.org/wiki/Q141687
  - Coordinates: 31.76°N, 25.075°E
  - Mediterranean seaport near Egyptian border

- **Jaghbub**: https://en.wikipedia.org/wiki/Jaghbub
  - WikiData: https://www.wikidata.org/wiki/Q284251
  - Coordinates: 29.7425°N, 24.516944°E
  - Desert oasis village

## Impact

### Data Quality Improvements
- ✅ Libya now compliant with ISO 3166-2:LY standard (all 22 popularates present)
- ✅ Added comprehensive data for Al Butnan populare:
  - Timezone information (Africa/Tripoli)
  - Native name (البطنان)
  - 15 language translations
  - WikiData reference (Q25931)
- ✅ Added 3 major cities in Al Butnan district with complete metadata:
  - All have timezone information
  - All have native names in Arabic
  - All have WikiData references
  - All have multilingual translations (7-17 languages)
  - All have accurate coordinates from Wikipedia

### API Changes
- `GET /states?country=LY` now returns 22 states instead of 21
- `GET /cities?country=LY` now returns 54 cities instead of 51
- New state code available: `BU` for Al Butnan
- 3 new cities accessible via API

### Breaking Changes
- None - purely additive changes

### Database Statistics
- Total states: 5174 → 5175 (+1)
- Total cities: 150,906 → 150,909 (+3)
- Libya states: 21 → 22 (+1)
- Libya cities: 51 → 54 (+3)
