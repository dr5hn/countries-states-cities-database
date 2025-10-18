# Sub-localities Feature

This document explains the sub-localities feature, which allows proper categorization of neighborhoods, districts, and areas within cities (such as Bandra in Mumbai, Manhattan in New York).

## 📋 Overview

Sub-localities are geographic areas that exist within a city. They are distinct from independent cities or towns. Examples include:

- **Mumbai, India**: Bandra, Andheri, Borivali, Powai, etc.
- **New York, USA**: Manhattan, Brooklyn, Queens, The Bronx, Staten Island
- **London, UK**: Westminster, Camden, Southwark, etc.
- **Paris, France**: Le Marais, Montmartre, Latin Quarter, etc.

Previously, many sub-localities were incorrectly stored as separate cities in the database. This feature introduces a dedicated `sublocalities` table with proper relationships to parent cities.

## 🗄️ Database Schema

The `sublocalities` table has the following structure:

```sql
CREATE TABLE `sublocalities` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `city_id` mediumint unsigned NOT NULL,        -- Foreign key to cities table
  `state_id` mediumint unsigned NOT NULL,
  `state_code` varchar(255) NOT NULL,
  `country_id` mediumint unsigned NOT NULL,
  `country_code` char(2) NOT NULL,
  `latitude` decimal(10,8) NOT NULL,
  `longitude` decimal(11,8) NOT NULL,
  `native` varchar(255) DEFAULT NULL,
  `timezone` varchar(255) DEFAULT NULL,
  `translations` text,
  `created_at` timestamp NOT NULL DEFAULT '2014-01-01 06:31:01',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag` tinyint(1) NOT NULL DEFAULT '1',
  `wikiDataId` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `sublocalities_ibfk_1` FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`),
  CONSTRAINT `sublocalities_ibfk_2` FOREIGN KEY (`state_id`) REFERENCES `states` (`id`),
  CONSTRAINT `sublocalities_ibfk_3` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`)
)
```

## 📁 Data Structure

### Contributions JSON

Sub-localities are stored in `contributions/sublocalities/sublocalities.json`:

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

### Export Formats

Sub-localities are exported to all standard formats:

- **JSON**: `json/sublocalities.json`
- **CSV**: `csv/sublocalities.csv`
- **XML**: `xml/sublocalities.xml`
- **YAML**: `yml/sublocalities.yml`
- **MongoDB**: `mongodb/sublocalities.json`
- **SQL Server**: `sqlserver/sublocalities.sql`

## 🔧 Tools and Scripts

### 1. Identify Sub-localities

Use the identification script to find cities that might actually be sub-localities:

```bash
# Analyze all cities in India, Maharashtra state
python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH

# Analyze with custom distance threshold (default is 20km)
python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH --distance 15

# Export results to JSON for further processing
python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH --export mumbai_analysis.json

# Show more results
python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH --limit 100
```

The script identifies potential sub-localities by:
- Finding cities very close to each other (< 20km by default)
- Detecting naming patterns (e.g., "Mumbai Suburban", "North Delhi")
- Analyzing WikiData relationships

### 2. Import Sub-localities to MySQL

After adding sub-localities to `contributions/sublocalities/sublocalities.json`:

```bash
python3 bin/scripts/sync/import_json_to_mysql.py
```

This imports all data including the new sub-localities table.

### 3. Export Sub-localities from MySQL

To sync data back from MySQL to JSON:

```bash
python3 bin/scripts/sync/sync_mysql_to_json.py
```

### 4. Export to All Formats

To export sub-localities to all supported formats:

```bash
cd bin
php console export:json      # Exports to JSON
php console export:csv        # Exports to CSV
php console export:xml        # Exports to XML
php console export:yaml       # Exports to YAML
php console export:mongodb    # Exports to MongoDB
php console export:sql-server # Exports to SQL Server
```

## 📝 How to Add Sub-localities

### Step 1: Identify Sub-localities

Use the identification script or manually review your data to identify entries that should be sub-localities rather than cities.

### Step 2: Find Parent City ID

Look up the parent city in `contributions/cities/<COUNTRY_CODE>.json`:

```json
{
  "id": 133024,
  "name": "Mumbai",
  "state_id": 4008,
  "state_code": "MH",
  "country_id": 101,
  "country_code": "IN",
  ...
}
```

### Step 3: Add to Sublocalities JSON

Add the sub-locality to `contributions/sublocalities/sublocalities.json`:

```json
{
  "name": "Bandra",
  "city_id": 133024,           // Mumbai's ID
  "state_id": 4008,
  "state_code": "MH",
  "country_id": 101,
  "country_code": "IN",
  "latitude": "19.05444444",
  "longitude": "72.84055556",
  "timezone": "Asia/Kolkata",
  "wikiDataId": "Q257622"
}
```

**Important**: Omit the `id` field - it will be auto-assigned by MySQL.

### Step 4: Remove from Cities (if applicable)

If the entry was previously in the cities list, remove it from `contributions/cities/<COUNTRY_CODE>.json`.

### Step 5: Commit and Push

```bash
git add contributions/sublocalities/sublocalities.json
git add contributions/cities/IN.json  # If you removed entries
git commit -m "Add Bandra as sub-locality of Mumbai"
git push
```

GitHub Actions will automatically:
1. Import the data to MySQL
2. Export to all formats
3. Update the pull request

## 🔍 Example: Mumbai Sub-localities

Mumbai has many well-known areas that were previously listed as separate cities:

| Sub-locality | WikiData ID | Should be under |
|-------------|-------------|-----------------|
| Bandra | Q257622 | Mumbai (Q1156) |
| Andheri | Q12413015 | Mumbai (Q1156) |
| Borivali | Q4945504 | Mumbai (Q1156) |
| Powai | Q13118508 | Mumbai (Q1156) |
| Juhu | Q674362 | Mumbai (Q1156) |
| Colaba | Q3632559 | Mumbai (Q1156) |
| Dharavi | Q649632 | Mumbai (Q1156) |

These should be moved from `cities` to `sublocalities` with `city_id = 133024` (Mumbai's ID).

## 🎯 Best Practices

1. **Verify WikiData**: Always check WikiData to confirm if a place is actually a sub-locality or an independent city.

2. **Use the Identification Script**: Run the script to get suggestions, but manually verify each result.

3. **Preserve Data**: When moving entries from cities to sub-localities, preserve all fields (coordinates, timezone, translations, etc.).

4. **Document Changes**: In commit messages, explain why something is being categorized as a sub-locality.

5. **Consistency**: Use consistent naming - if the parent city is "Mumbai", don't use "Bombay" for sub-localities.

## 📊 Database Relationships

```
countries (1) ──┐
                ├──> states (N) ──┐
                │                  ├──> cities (N) ──> sublocalities (N)
                │                  │
                └──────────────────┘
```

Each sub-locality:
- MUST have a parent city (`city_id`)
- MUST have the same state and country as its parent city
- Should be geographically within or very close to its parent city

## 🐛 Troubleshooting

### Script says "Table 'sublocalities' does not exist"

The table needs to be created in MySQL first:

```bash
mysql -uroot -proot world < sql/schema.sql
```

### Import fails with "Foreign key constraint"

Ensure:
1. The parent `city_id` exists in the cities table
2. The `state_id` and `country_id` match valid entries
3. Import is done in correct order (cities before sublocalities)

### Identification script shows no results

Try:
- Increasing the `--distance` parameter
- Running without filters (`--country` or `--state`) to see global patterns
- Checking if MySQL connection is successful

## 🚀 Future Enhancements

Potential improvements for the sub-localities feature:

1. **Hierarchical Sub-localities**: Support for nested sub-localities (e.g., a neighborhood within a district)
2. **Automated Classification**: ML model to automatically suggest sub-locality classifications
3. **Batch Migration Tool**: Automated tool to move multiple entries from cities to sub-localities
4. **Validation Rules**: Ensure sub-localities are geographically within their parent city boundaries

## 📚 References

- [WikiData Documentation](https://www.wikidata.org/)
- [IANA Timezone Database](https://www.iana.org/time-zones)
- [Contributing Guidelines](../contributions/README.md)
- [GitHub Issue #XXX](https://github.com/dr5hn/countries-states-cities-database/issues/XXX) - Original request

## 🤝 Contributing

If you identify sub-localities that should be moved from the cities table, please:

1. Run the identification script
2. Manually verify the suggestions
3. Create a pull request with the changes
4. Include evidence (WikiData links, maps, etc.) in the PR description

Thank you for helping improve the database quality! 🙏
