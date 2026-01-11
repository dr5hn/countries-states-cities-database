# Malaysia Selangor Cities Update

## Issue Reference
**Issue:** [Bug]: Update Malaysia state and Selangor towns data  
**Problem:** The current Malaysia Selangor data was incomplete. Missing 43 towns/cities from Selangor state.

## Countries/Regions Addressed
- **Country:** Malaysia (MY)
- **State:** Selangor (state_code: 10)

## Changes Made

### Cities Added
- **Before count:** 25 Selangor cities
- **After count:** 68 Selangor cities
- **Cities added:** 43 new cities
- **Fields added:** timezone, translations (for 25 cities)
- **Coordinate updates:** 3 cities (Banting, Puchong, Sungai Besar)

### New Cities List
1. Ampang Jaya
2. Assam Jawa
3. Bandar Baru Selayang
4. Bandar Kundang
5. Bangi
6. Batang Kali
7. Batu Caves
8. Beranang
9. Bestari Jaya
10. Broga
11. Bukit Rotan
12. Cyberjaya
13. Gombak
14. Jenjarom
15. Kajang
16. Kampung Kuantan
17. Kapar
18. Kuala Kubu Bharu
19. Kuala Sungai Buloh
20. Lagong
21. Meru
22. Mutiara Damansara
23. Padang Jawa
24. Pandamaran
25. Paya Jaras
26. Port Klang
27. Sabak
28. Salak Tinggi
29. Sekinchan
30. Selayang
31. Sepang
32. Seri Kembangan
33. Sungai Air Tawar
34. Sungai Buaya
35. Sungai Burong
36. Sungai Choh
37. Sungai Pelek
38. Sungai Pelong
39. Sungai Tengi
40. Taman Melawati
41. Taman Tasik Semenyih
42. Teluk Datok
43. Ulu Yam

### Coordinate Updates
Three existing cities had their coordinates updated to match the source data:

1. **Banting**
   - Old: 2.81360000, 101.50185000
   - New: 2.81209800, 101.50255500

2. **Puchong**
   - Old: 3.03270000, 101.61880000
   - New: 3.00980000, 101.61800000

3. **Sungai Besar**
   - Old: 3.67460000, 100.98670000
   - New: 3.35000000, 101.25000000

### Existing Cities (No Changes)
The following 5 cities already existed with matching coordinates:
- Kuala Selangor
- Kuang
- Rawang
- Semenyih
- Tanjung Sepat

## Validation Steps

### 1. Data Import and Timezone Enrichment
```bash
# Import JSON to MySQL
python3 bin/scripts/sync/import_json_to_mysql.py --host localhost --user root --password root

# Add timezones to all new cities
python3 bin/scripts/validation/add_timezones.py --table cities --user root --password root
```

**Result:** Successfully added timezone `Asia/Kuala_Lumpur` to all 43 new cities.

### 2. Translation Enrichment
```bash
# Add translations from Wikipedia
python3 bin/scripts/validation/translation_enricher.py --file contributions/cities/MY.json --type city
```

**Result:** 
- Translations added: 25 cities (58% success rate)
- No translations found: 18 cities (smaller towns without Wikipedia articles)
- Languages covered: ar, bn, de, es, fr, hi, id, it, ja, ko, nl, pl, pt, ru, tr, uk, vi, zh

### 3. Sync Back to JSON
```bash
# Sync MySQL to JSON
python3 bin/scripts/sync/sync_mysql_to_json.py --host localhost --user root --password root
```

**Result:** All cities now have assigned IDs, timezones, and available translations.

### 4. Final Verification
```bash
# Count Selangor cities
jq '[.[] | select(.state_code == "10" and .country_code == "MY")] | length' contributions/cities/MY.json
# Result: 68

# Verify timezone for new cities
jq '[.[] | select(.state_code == "10" and .country_code == "MY" and .timezone == "Asia/Kuala_Lumpur")] | length' contributions/cities/MY.json
# Result: 68 (all have timezone)

# Check translation coverage
jq '[.[] | select(.state_code == "10" and .country_code == "MY" and (.translations != null and .translations != {}))] | length' contributions/cities/MY.json
# Result: 50 (73% have translations)
```

## Data Samples

### City Entry with Full Data (Kajang)
```json
{
  "id": 160571,
  "name": "Kajang",
  "state_id": 1944,
  "state_code": "10",
  "country_id": 132,
  "country_code": "MY",
  "latitude": "2.98330000",
  "longitude": "101.78780000",
  "timezone": "Asia/Kuala_Lumpur",
  "translations": {
    "fr": "Kajang (Selangor)",
    "id": "Kajang, Malaysia",
    "it": "Kajang",
    "ko": "카장",
    "nl": "Kajang",
    "pl": "Kajang-Sungai Chua",
    "ru": "Каджанг",
    "tr": "Kajang",
    "vi": "Kajang",
    "zh": "加影"
  }
}
```

### City Entry (Port Klang)
```json
{
  "id": 160584,
  "name": "Port Klang",
  "state_id": 1944,
  "state_code": "10",
  "country_id": 132,
  "country_code": "MY",
  "latitude": "3.00507000",
  "longitude": "101.40887000",
  "timezone": "Asia/Kuala_Lumpur",
  "translations": {
    "ar": "ميناء كلاغ",
    "bn": "পোর্ট ক্লাং",
    "de": "Port Klang",
    "es": "Puerto Klang",
    "fr": "Port Klang",
    "hi": "पोर्ट क्लैंग",
    "ja": "ポートクラン",
    "ko": "클랑항",
    "pt": "Port Klang",
    "ru": "Порт-Кланг",
    "tr": "Klang Limanı",
    "zh": "巴生港"
  }
}
```

### City Entry (Cyberjaya)
```json
{
  "id": 160568,
  "name": "Cyberjaya",
  "state_id": 1944,
  "state_code": "10",
  "country_id": 132,
  "country_code": "MY",
  "latitude": "2.92000000",
  "longitude": "101.65000000",
  "timezone": "Asia/Kuala_Lumpur"
}
```

## References
- **Source:** [Wikipedia - Category:Towns in Selangor](https://en.wikipedia.org/wiki/Category:Towns_in_Selangor)
- **State Information:** [Selangor on Wikipedia](https://en.wikipedia.org/wiki/Selangor)
- **WikiData:** [Selangor (Q189710)](https://www.wikidata.org/wiki/Q189710)

## Impact

### Data Quality Improvements
- ✅ **172% increase** in Selangor city coverage (25 → 68 cities)
- ✅ All new cities have timezone information
- ✅ 58% of new cities have translations (25/43)
- ✅ Coordinates updated for 3 existing cities to match authoritative source

### Coverage by District
The updated data now includes cities from various Selangor districts:
- **Gombak:** Batu Caves, Selayang, Rawang, Kuala Sungai Buloh
- **Hulu Selangor:** Kuala Kubu Bharu, Batang Kali
- **Kuala Selangor:** Kuala Selangor, Bestari Jaya, Sekinchan
- **Petaling:** Cyberjaya, Puchong, Seri Kembangan, Subang Jaya
- **Sepang:** Sepang, Salak Tinggi
- **Klang:** Port Klang, Kapar
- **Hulu Langat:** Kajang, Bangi, Semenyih, Beranang

### API Changes
- No breaking changes
- New cities are added with proper foreign key relationships
- All data follows existing schema

### No Known Issues
All cities imported successfully with proper validation.
