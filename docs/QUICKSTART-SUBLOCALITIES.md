# Quick Start: Using the Sub-localities Feature

This guide shows you how to use the new sub-localities feature to properly categorize neighborhoods and districts within cities.

## 🎯 What are Sub-localities?

Sub-localities are neighborhoods, districts, or areas within a larger city:
- ✅ **Bandra** (part of Mumbai, India)
- ✅ **Manhattan** (part of New York, USA)
- ✅ **Montmartre** (part of Paris, France)
- ❌ **NOT** independent cities or towns

## 🔍 Step 1: Identify Sub-localities

Use the identification script to find potential sub-localities:

```bash
# For Mumbai area (India, Maharashtra state)
python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH --password root

# For all of India
python3 bin/scripts/sync/identify_sublocalities.py --country IN --password root

# Export results to JSON for review
python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH --export mumbai_review.json
```

The script will show:
- Cities very close to each other (< 20km by default)
- Cities with naming patterns like "Suburban", "North", "East"
- WikiData IDs for verification

## ✅ Step 2: Verify with WikiData

For each potential sub-locality, check WikiData:

1. Visit `https://www.wikidata.org/wiki/Q257622` (replace with the WikiData ID)
2. Look for "part of" (P361) or "located in" (P131) properties
3. If it says "part of Mumbai" → It's a sub-locality!
4. If it's independent → Keep it as a city

## 📝 Step 3: Add to Sublocalities JSON

### Find the Parent City ID

Look in `contributions/cities/IN.json` for Mumbai:
```json
{
  "id": 133024,
  "name": "Mumbai",
  ...
}
```

### Add to `contributions/sublocalities/sublocalities.json`

```json
[
  {
    "name": "Bandra",
    "city_id": 133024,
    "state_id": 4008,
    "state_code": "MH",
    "country_id": 101,
    "country_code": "IN",
    "latitude": "19.05444444",
    "longitude": "72.84055556",
    "native": "बांद्रा",
    "timezone": "Asia/Kolkata",
    "translations": {
      "hi": "बांद्रा",
      "mr": "बांद्रा"
    },
    "wikiDataId": "Q257622"
  }
]
```

**Important:** 
- ❌ Do NOT include `"id"` field (auto-generated)
- ✅ DO include all location data from the original city entry
- ✅ DO add `"city_id"` pointing to parent city

## 🗑️ Step 4: Remove from Cities

If the entry was in `contributions/cities/IN.json`, remove it:

```json
// REMOVE entries like this from cities:
{
  "id": 147697,
  "name": "Bandra",
  ...
}
```

## 💾 Step 5: Commit and Push

```bash
git add contributions/sublocalities/sublocalities.json
git add contributions/cities/IN.json
git commit -m "Move Bandra from cities to sub-localities of Mumbai"
git push
```

GitHub Actions will automatically:
1. Import to MySQL database
2. Export to all formats (JSON, CSV, XML, YAML, MongoDB, SQL Server)
3. Update the pull request

## 🧪 Testing Locally (Optional)

If you have MySQL installed:

```bash
# 1. Create database and load schema
mysql -uroot -proot -e "CREATE DATABASE world;"
mysql -uroot -proot world < sql/schema.sql

# 2. Import your changes
python3 bin/scripts/sync/import_json_to_mysql.py --password root

# 3. Verify
mysql -uroot -proot -e "SELECT * FROM world.sublocalities WHERE name='Bandra';"
```

## 📊 Example: Mumbai Sub-localities

Here are confirmed Mumbai sub-localities to move:

| Name | Current ID | WikiData | Move to Sublocalities |
|------|-----------|----------|---------------------|
| Andheri | 147680 | Q12413015 | ✅ Yes |
| Bandra | 147697 | Q257622 | ✅ Yes |
| Borivali | 147715 | Q4945504 | ✅ Yes |
| Chembur | 147723 | Q251170 | ✅ Yes |
| Colaba | 147728 | Q3632559 | ✅ Yes |
| Dharavi | 147737 | Q649632 | ✅ Yes |
| Juhu | 147768 | Q674362 | ✅ Yes |
| Powai | 133484 | Q13118508 | ✅ Yes |
| Worli | 147939 | Q1934607 | ✅ Yes |

All should have `"city_id": 133024` (Mumbai)

## 🎓 Tips

1. **Batch Processing**: You can add multiple sub-localities in one PR
2. **Keep Coordinates**: Always preserve latitude, longitude, timezone
3. **Translations**: Preserve all translation data
4. **WikiData**: Always verify with WikiData before making changes
5. **Consistency**: If parent is "Mumbai", don't use "Bombay" for sub-localities

## 📚 Full Documentation

For complete details, see:
- [docs/SUBLOCALITIES.md](../docs/SUBLOCALITIES.md) - Complete guide
- [contributions/README.md](../contributions/README.md) - Field reference
- [README.md](../README.md) - Project overview

## ❓ Need Help?

- Check WikiData for "part of" relationships
- Run the identification script with different distance parameters
- Open an issue if you're unsure about a specific case

## 🙏 Thank You!

Your contributions help improve data quality for thousands of developers worldwide!
