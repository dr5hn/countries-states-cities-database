# 📝 Contributions Directory

This directory contains the source JSON files for contributing to the Countries States Cities Database.

## 📁 Directory Structure

```
contributions/
├── regions/
│   └── regions.json            (6 regions)
├── subregions/
│   └── subregions.json         (22 subregions)
├── countries/
│   └── countries.json          (250 countries)
├── states/
│   └── states.json             (5,000+ states/provinces)
├── cities/
│   ├── AD.json                 (Andorra cities)
│   ├── US.json                 (United States cities)
│   ├── IN.json                 (India cities)
│   └── ...                     (209 country files)
└── sub_localities/
    ├── IN.json                 (India sub-localities)
    ├── US.json                 (United States sub-localities)
    └── ...                     (Sub-localities by country)
```

## 🎯 How to Contribute

### Adding a New City

1. **Find the country file**: Navigate to `contributions/cities/` and open the file for your country (e.g., `US.json` for United States)

2. **Add your city** at the end of the array:

```json
{
    "name": "New City Name",
    "state_id": 1234,
    "state_code": "CA",
    "country_id": 1,
    "country_code": "US",
    "latitude": "37.77490000",
    "longitude": "-122.41940000",
    "timezone": "America/Los_Angeles"
}
```

**⚠️ Important: Do NOT include an `id` field for new cities!** The build system will automatically assign IDs.

### Editing an Existing City

1. **Find the city** in the appropriate country file
2. **Keep the existing `id` field**
3. **Edit the data** you want to change:

```json
{
    "id": 1234,                     ← Keep this unchanged!
    "name": "Updated City Name",    ← Edit as needed
    "state_id": 1234,
    "state_code": "CA",
    ...
}
```

### Adding a New Country

Edit `contributions/countries/countries.json` and add your country:

```json
{
    "name": "New Country",
    "iso2": "NC",
    "iso3": "NCO",
    "capital": "Capital City",
    ...
}
```

**Note:** Omit the `id` field for new countries - it will be auto-assigned.

### Adding a New State/Province

Edit `contributions/states/states.json` and add your state:

```json
{
    "name": "New State",
    "country_id": 1,
    "country_code": "US",
    "state_code": "NS",
    ...
}
```

**Note:** Omit the `id` field for new states - it will be auto-assigned.

### Adding a New Region

Edit `contributions/regions/regions.json` and add your region:

```json
{
    "name": "New Region",
    "translations": {
        "es": "Nueva Región"
    }
}
```

**Note:** Omit the `id` field for new regions - it will be auto-assigned.

### Adding a New Subregion

Edit `contributions/subregions/subregions.json` and add your subregion:

```json
{
    "name": "New Subregion",
    "region_id": 1,
    "translations": {
        "es": "Nueva Subregión"
    }
}
```

**Note:** Omit the `id` field for new subregions - it will be auto-assigned.

### Adding a New Sub-Locality

Sub-localities are neighborhoods or areas within a city (e.g., Andheri in Mumbai, Manhattan in New York).

1. **Find the country file**: Navigate to `contributions/sub_localities/` and open the file for your country (e.g., `IN.json` for India)

2. **Add your sub-locality** at the end of the array:

```json
{
    "name": "Andheri",
    "city_id": 133024,
    "state_id": 4008,
    "state_code": "MH",
    "country_id": 101,
    "country_code": "IN",
    "latitude": "19.11916667",
    "longitude": "72.84694444",
    "timezone": "Asia/Kolkata"
}
```

**⚠️ Important:** 
- Do NOT include an `id` field for new sub-localities! The build system will automatically assign IDs.
- You must provide a valid `city_id` that references the parent city. Find city IDs in the corresponding `contributions/cities/*.json` file.

**Note:** If the country file doesn't exist, create it as an empty array: `[]`

## 🛠️ Submission Process

**For External Contributors:**

Simply create a pull request with your JSON changes! You don't need to run any build scripts locally.

**What happens after you submit:**
1. ✅ Maintainers review your JSON changes
2. ✅ GitHub Actions imports to MySQL (IDs auto-assigned by database)
3. ✅ All export formats (JSON, CSV, SQL, XML, YAML) are regenerated
4. ✅ Your PR is automatically updated with all exports

**Important:**
- ✅ **DO**: Edit JSON files in `contributions/` directory
- ❌ **DON'T**: Edit SQL, CSV, XML, YAML files (auto-generated)
- ❌ **DON'T**: Run build scripts locally (GitHub Actions handles this)
- 🔒 **MySQL workflow**: Reserved for maintainers only

## 📋 Field Reference

### City Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `id` | Auto | Unique identifier (omit for new cities) | `1234` |
| `name` | ✅ Yes | Official city name | `"San Francisco"` |
| `state_id` | ✅ Yes | ID of parent state | `1416` |
| `state_code` | ✅ Yes | ISO code of parent state | `"CA"` |
| `country_id` | ✅ Yes | ID of parent country | `233` |
| `country_code` | ✅ Yes | ISO2 code of parent country | `"US"` |
| `latitude` | ✅ Yes | Latitude coordinate | `"37.77490000"` |
| `longitude` | ✅ Yes | Longitude coordinate | `"-122.41940000"` |
| `timezone` | No | IANA timezone | `"America/Los_Angeles"` |
| `translations` | No | Name translations object | `{"es": "San Francisco"}` |
| `wikiDataId` | No | WikiData identifier | `"Q62"` |
| `created_at` | No | Creation timestamp (ISO 8601) | `"2019-10-05T23:18:06"` |
| `updated_at` | No | Last update timestamp (ISO 8601) | `"2025-10-08T14:42:36"` |
| `flag` | Auto | Active status flag (managed by system) | `1` |

**Note:** The `created_at` and `updated_at` fields are optional. If omitted, MySQL will use default values. When provided, use ISO 8601 format with "T" separator.

### Sub-Locality Fields

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `id` | Auto | Unique identifier (omit for new sub-localities) | `1234` |
| `name` | ✅ Yes | Official sub-locality name | `"Andheri"` |
| `city_id` | ✅ Yes | ID of parent city | `133024` |
| `state_id` | ✅ Yes | ID of parent state | `4008` |
| `state_code` | ✅ Yes | ISO code of parent state | `"MH"` |
| `country_id` | ✅ Yes | ID of parent country | `101` |
| `country_code` | ✅ Yes | ISO2 code of parent country | `"IN"` |
| `latitude` | ✅ Yes | Latitude coordinate | `"19.11916667"` |
| `longitude` | ✅ Yes | Longitude coordinate | `"72.84694444"` |
| `native` | No | Native name | `"अंधेरी"` |
| `timezone` | No | IANA timezone | `"Asia/Kolkata"` |
| `translations` | No | Name translations object | `{"es": "Andheri"}` |
| `wikiDataId` | No | WikiData identifier | `"Q12413015"` |
| `created_at` | No | Creation timestamp (ISO 8601) | `"2021-06-06T13:17:48"` |
| `updated_at` | No | Last update timestamp (ISO 8601) | `"2025-10-09T10:30:49"` |
| `flag` | Auto | Active status flag (managed by system) | `1` |

### Finding City IDs

To find the correct `city_id` for a sub-locality:

1. Open `contributions/cities/<COUNTRY_CODE>.json` (e.g., `IN.json` for India)
2. Search for the parent city name
3. Use the `id` value

Example:
```json
{
  "id": 133024,
  "name": "Mumbai",
  "state_id": 4008,
  "state_code": "MH",
  "country_id": 101,
  "country_code": "IN"
}
```

### Finding State IDs

To find the correct `state_id` and `state_code`:

1. Open `contributions/states/states.json`
2. Search for your state name
3. Use the `id` and `iso2` values

Example:
```json
{
  "id": 1416,
  "name": "California",
  "country_id": 233,
  "country_code": "US",
  "state_code": "CA",
  "iso2": "US-CA"
}
```

### Finding Country IDs

To find the correct `country_id` and `country_code`:

1. Open `contributions/countries/countries.json`
2. Search for your country name
3. Use the `id` and `iso2` values

Example:
```json
{
  "id": 233,
  "name": "United States",
  "iso2": "US",
  "iso3": "USA"
}
```

## ✅ Best Practices

1. **Always validate your JSON** - Use a JSON validator before submitting
2. **One change at a time** - Make focused contributions for easier review
3. **Use official sources** - Reference WikiData, Wikipedia, or official government sources
4. **Keep formatting** - Maintain the indentation (2 spaces) and structure
5. **Validate JSON** - Ensure your JSON is valid before submitting

## 🤝 Submitting Your Contribution

1. **Fork** the repository
2. **Make your changes** in the `contributions/` directory
3. **Commit your changes** with a clear message
4. **Create a pull request** with a description of what you changed
5. **Wait for GitHub Actions** to run - it will automatically generate all exports

## 📞 Need Help?

- Check the main [CONTRIBUTING.md](../.github/CONTRIBUTING.md) for detailed guidelines
- Open an issue if you have questions
- Use the [CSC Update Tool](https://manager.countrystatecity.in/) for a web-based alternative

Thank you for contributing! 🙏
