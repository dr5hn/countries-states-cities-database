# Iraq - Adding Missing Kurdistan Region (Iqlim Kurdistan)

## Issue Reference
**GitHub Issue:** [Data]: Iraq region missing  
**Problem:** Iraq was missing the Kurdistan Region (Iqlim Kurdistan / IQ-KR) which is listed in ISO 3166-2:IQ standard as a region type administrative division.

## Countries/Regions Addressed
- Iraq (IQ)

## Changes Made

### Added Kurdistan Region State/Region
- **Before count:** 18 states/governorates for Iraq
- **After count:** 19 states/regions for Iraq
- **Fields added:** Complete state entry with id, timezone, translations, wikiDataId, coordinates

### State Entry Details
```json
{
  "id": 5625,
  "name": "Iqlim Kurdistan",
  "country_id": 104,
  "country_code": "IQ",
  "fips_code": null,
  "iso2": "KR",
  "iso3166_2": "IQ-KR",
  "type": "region",
  "level": null,
  "parent_id": null,
  "native": "ھەرێمی کوردستان",
  "latitude": "36.18333333",
  "longitude": "44.00000000",
  "timezone": "Asia/Baghdad",
  "translations": {
    "ar": "إقليم كردستان العراق",
    "bn": "ইরাকি কুর্দিস্তান",
    "de": "Autonome Region Kurdistan",
    "es": "Kurdistán iraquí",
    "fr": "Kurdistan irakien",
    "hi": "इराकी कुर्दिस्तान",
    "id": "Daerah Kurdistan",
    "it": "Regione del Kurdistan",
    "ja": "クルディスタン地域",
    "ko": "쿠르드 자치구",
    "nl": "Koerdische Autonome Regio",
    "pl": "Kurdystan (region autonomiczny)",
    "pt": "Curdistão iraquiano",
    "ru": "Регион Курдистан",
    "tr": "Kürdistan Bölgesel Yönetimi",
    "uk": "Іракський Курдистан",
    "vi": "Kurdistan thuộc Iraq",
    "zh": "伊拉克库尔德斯坦"
  },
  "wikiDataId": "Q205047",
  "population": null,
  "created_at": "2025-11-15T04:58:00",
  "updated_at": "2025-11-15T04:58:00",
  "flag": 1
}
```

## Validation Steps

### 1. ISO 3166-2:IQ Standard Verification
**Source:** https://www.iso.org/obp/ui#iso:code:3166:IQ

**Expected result:** ISO standard lists 18 governorates + 1 region (IQ-KR: Iqlim Kurdistan)

**Actual result:** ✅ Verified - ISO 3166-2:IQ includes:
- 18 governorates (type: governorate)
- 1 region: IQ-KR (Iqlim Kurdistan, type: region)

### 2. Wikipedia Validation
**Command:**
```bash
python3 bin/scripts/validation/wikipedia_validator.py \
    --entity "Kurdistan Region" \
    --type state \
    --country IQ
```

**Expected result:** Validate existence, coordinates, and WikiData ID

**Actual result:** ✅ Validated
- **Wikipedia article:** https://en.wikipedia.org/wiki/Kurdistan_Region
- **WikiData ID:** Q205047
- **Summary:** Semi-autonomous federal region of Iraq comprising Erbil, Sulaymaniyah, Duhok, and Halabja governorates
- **Coordinates:** 36.183333, 44.0

### 3. WikiData Verification
**Source:** https://www.wikidata.org/wiki/Q205047

**Verified:**
- ✅ Official name: Kurdistan Region / Iqlim Kurdistan
- ✅ Native name (Kurdish): ھەرێمی کوردستان
- ✅ Arabic name: إقليم كردستان العراق
- ✅ Coordinates: 36.183333°N, 44°E
- ✅ ISO code: IQ-KR
- ✅ Type: Autonomous region

### 4. Translation Verification
**Sources:** Wikipedia language links, WikiData

**Verified translations in 18 languages:**
- Arabic (ar): إقليم كردستان العراق
- Bengali (bn): ইরাকি কুর্দিস্তান
- German (de): Autonome Region Kurdistan
- Spanish (es): Kurdistán iraquí
- French (fr): Kurdistan irakien
- Hindi (hi): इराकी कुर्दिस्तान
- Indonesian (id): Daerah Kurdistan
- Italian (it): Regione del Kurdistan
- Japanese (ja): クルディスタン地域
- Korean (ko): 쿠르드 자치구
- Dutch (nl): Koerdische Autonome Regio
- Polish (pl): Kurdystan (region autonomiczny)
- Portuguese (pt): Curdistão iraquiano
- Russian (ru): Регион Курдистан
- Turkish (tr): Kürdistan Bölgesel Yönetimi
- Ukrainian (uk): Іракський Курдистан
- Vietnamese (vi): Kurdistan thuộc Iraq
- Chinese (zh): 伊拉克库尔德斯坦

### 5. Timezone Verification
**Expected:** Asia/Baghdad (Iraq uses a single timezone)
**Actual:** ✅ Asia/Baghdad

### 6. State Count Verification
**Command:**
```bash
jq '[.[] | select(.country_code == "IQ")] | length' contributions/states/states.json
```

**Expected result:** 19 (18 governorates + 1 region)
**Actual result:** ✅ 19

### 7. JSON Validation
**Command:**
```bash
jq empty contributions/states/states.json
```

**Expected result:** No errors
**Actual result:** ✅ JSON is valid

## Data Samples

### Complete Iraq States List (19 total)
1. Al Anbar (AN) - governorate
2. Al Muthanna (MU) - governorate
3. Al-Qādisiyyah (QA) - governorate
4. Babylon (BB) - governorate
5. Baghdad (BG) - governorate
6. Basra (BA) - governorate
7. Dhi Qar (DQ) - governorate
8. Diyala (DI) - governorate
9. Dohuk (DA) - governorate
10. Erbil (AR) - governorate
11. **Iqlim Kurdistan (KR) - region** ← NEW
12. Karbala (KA) - governorate
13. Kirkuk (KI) - governorate
14. Maysan (MA) - governorate
15. Najaf (NA) - governorate
16. Nineveh (NI) - governorate
17. Saladin (SD) - governorate
18. Sulaymaniyah (SU) - governorate
19. Wasit (WA) - governorate

## Administrative Structure Notes

The Kurdistan Region (Iqlim Kurdistan) is a semi-autonomous federal region that administratively encompasses the following governorates:
- Erbil Governorate (state_id: 3968)
- Sulaymaniyah Governorate (state_id: 3969)
- Dohuk Governorate (state_id: 3967)
- Halabja Governorate (if added in the future)

Cities within these governorates are already properly assigned to their respective governorates in the database (135 cities total for Iraq). The Kurdistan Region acts as a higher-level administrative division but cities are maintained at the governorate level as per standard geographical database practices.

## References
- **ISO 3166-2:IQ:** https://www.iso.org/obp/ui#iso:code:3166:IQ
- **Wikipedia:** https://en.wikipedia.org/wiki/Kurdistan_Region
- **WikiData:** https://www.wikidata.org/wiki/Q205047
- **Wikipedia Iraq:** https://en.wikipedia.org/wiki/Iraq

## Impact
- ✅ Database now fully compliant with ISO 3166-2:IQ standard
- ✅ All 19 administrative divisions of Iraq represented (18 governorates + 1 region)
- ✅ No breaking changes - only addition of new state/region
- ✅ Data quality improvements: Complete entry with timezone, 18 translations, WikiData ID
- ✅ Existing city assignments remain unchanged (cities properly assigned to governorates)

## Data Quality Metrics
- **Timezone:** ✅ Complete (Asia/Baghdad)
- **Translations:** ✅ Complete (18 languages)
- **WikiData ID:** ✅ Complete (Q205047)
- **Native name:** ✅ Complete (ھەرێمی کوردستان)
- **Coordinates:** ✅ Complete (36.18333333, 44.00000000)
- **ISO codes:** ✅ Complete (iso2: KR, iso3166_2: IQ-KR)
- **Type:** ✅ Correctly set (region)
