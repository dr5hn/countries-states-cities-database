# Contributing to Country State City Database

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to Contributing to Country State City Database. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### 🎯 Recommended: Using JSON Contribution Files (Easy for Everyone!)

We've made contributing easier! You can now edit simple JSON files organized by country:

#### Adding or Editing Cities
- **Navigate to** `contributions/cities/` directory
- **Find your country file** (e.g., `US.json` for United States, `IN.json` for India)
- **Add or edit cities** in easy-to-read JSON format

**Adding a NEW city** (omit the `id` field):
```json
{
    "name": "New City",
    "state_id": 1416,
    "state_code": "CA",
    "country_id": 233,
    "country_code": "US",
    "latitude": "37.77490000",
    "longitude": "-122.41940000",
    "timezone": "America/Los_Angeles"
}
```

**Editing an EXISTING city** (keep the `id` field):
```json
{
    "id": 1234,
    "name": "Updated City Name",
    "state_id": 1416,
    ...
}
```

#### Adding or Editing Countries
- Edit `contributions/countries/countries.json`
- Omit `id` field for new countries

#### Adding or Editing States
- Edit `contributions/states/states.json`
- Omit `id` field for new states

**📖 For detailed instructions, see [contributions/README.md](../contributions/README.md)**

#### After Making Changes

**Simply create a pull request!** You don't need to run any build scripts locally.

**What happens next:**
1. Maintainers review your JSON changes
2. GitHub Actions automatically imports to MySQL (IDs are auto-assigned)
3. All export formats are regenerated from the MySQL database
4. Your PR is updated with all export files

**Important for Contributors:**
- ✅ **DO**: Edit JSON files in `contributions/` directory
- ❌ **DON'T**: Edit SQL, CSV, XML, YAML, or other export files (auto-generated)
- ❌ **DON'T**: Edit GeoJSON or TOON format files (auto-generated from database)
- ❌ **DON'T**: Run build scripts or exports locally (GitHub Actions handles this)
- 🔒 **MySQL workflow**: Reserved for repository maintainers only

### Understanding Export Formats

All data you contribute via JSON is automatically exported to **11 different formats**:
- **Core Formats**: JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB, XML, YAML, CSV
- **Geographic Format**: GeoJSON (RFC 7946 standard for mapping applications)
- **AI-Optimized Format**: TOON (Token-Oriented Object Notation - reduces LLM token usage by ~40%)

You don't need to worry about these formats - they're automatically generated from the MySQL database!

## Glance at Table Structure

### regions.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID - omit for new regions (auto-assigned) | Auto
| `name` | string | The official name of the region. Use WikiData or Wikipedia or some other legitimate source. | required
| `translations` | text | JSON object with region name translations |
| `created_at` | timestamp | Optional - Creation timestamp (ISO 8601 format). If omitted, database uses default value. |
| `updated_at` | timestamp | Optional - Last update timestamp (ISO 8601 format). If omitted, database auto-updates. |
| `flag`| boolean | Optional - Auto-managed by system, defaults to 1. Contributors can omit this field. |
| `wikiDataId` | string | The unique ID from wikiData.org |

### subregions.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID - omit for new subregions (auto-assigned) | Auto
| `name` | string | The official name of the subregion. Use WikiData or Wikipedia or some other legitimate source. | required
| `translations` | text | JSON object with subregion name translations |
| `region_id` | integer | Unique id of region from `regions.sql` | required
| `created_at` | timestamp | Optional - Creation timestamp (ISO 8601 format). If omitted, database uses default value. |
| `updated_at` | timestamp | Optional - Last update timestamp (ISO 8601 format). If omitted, database auto-updates. |
| `flag`| boolean | Optional - Auto-managed by system, defaults to 1. Contributors can omit this field. |
| `wikiDataId` | string | The unique ID from wikiData.org |

### countries.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID - omit for new countries (auto-assigned) | Auto
| `name` | string | The official name of the country. Use WikiData or Wikipedia or some other legitimate source. | required
| `iso3` | string | [ISO3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the country |
| `numeric_code` | string | Numeric ISO code - Source [ISO Official Site](iso.org/obp/ui/#iso:code:3166:NO) |
| `iso2` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the country |
| `phonecode` | string | Phone code of the country |
| `capital` | string | Capital city of the country |
| `currency` | string | Currency code of the country |
| `currency_name` | string | Currency name of the country |
| `currency_symbol` | string | Currency symbol of the country |
| `tld` | string | Domain code of the country |
| `native` | string | Native name of the country |
| `population` | integer | Population of the country - [Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population) |
| `gdp` | integer | GDP of the country - [Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)) |
| `region` | string | A region where country belongs to |
| `region_id` | integer | Unique id of region from `regions.sql` |
| `subregion` | string | A subregion where country belongs to |
| `subregion_id` | integer | Unique id of subregion from `subregions.sql` |
| `nationality` | string | Nationality/demonym of the country |
| `timezones` | text | JSON array of timezones  |
| `translations` | text | JSON object with country name translations |
| `latitude` | decimal | Latitude coordinates |
| `longitude` | decimal | Longitude coordinates |
| `emoji` | string | A flag emoji icon |
| `emojiU` | string | A flag emoji unicode characters |
| `created_at` | timestamp | Optional - Creation timestamp (ISO 8601 format). If omitted, database uses default value. |
| `updated_at` | timestamp | Optional - Last update timestamp (ISO 8601 format). If omitted, database auto-updates. |
| `flag`| boolean | Optional - Auto-managed by system, defaults to 1. Contributors can omit this field. |
| `wikiDataId` | string | The unique ID from wikiData.org |

### states.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | -------------- |
| `id` | integer | Unique ID - omit for new states (auto-assigned) | Auto |
| `name` | string | The official name of the state. Use WikiData or Wikipedia or some other legitimate source. | required |
| `state_code` | string | State/province code (e.g., "CA" for California) | required |
| `country_id` | integer | Unique id of parent country from `countries.sql` | required |
| `country_code` | string | ISO2 code of the parent country | required |
| `fips_code` | string | ISO-3166-2 subdivision code for the state |
| `iso2` | string | ISO2 code of the parent state |
| `iso3166_2` | string | ISO 3166-2 subdivision code |
| `type` | string | Type of state (province, state, region, etc.) |
| `level` | integer | Administrative level of the subdivision |
| `parent_id` | integer | ID of parent administrative division |
| `native` | string | Native name of the state |
| `population` | integer | Population of the state - [Wikipedia](https://en.wikipedia.org/wiki/List_of_states_by_population) |
| `latitude` | decimal | Latitude coordinates |
| `longitude` | decimal | Longitude coordinates |
| `timezone` | string | IANA timezone identifier (e.g., America/New_York) |
| `translations` | text | JSON object with name translations |
| `created_at` | timestamp | Optional - Creation timestamp (ISO 8601 format). If omitted, database uses default value. |
| `updated_at` | timestamp | Optional - Last update timestamp (ISO 8601 format). If omitted, database auto-updates. |
| `flag`| boolean | Optional - Auto-managed by system, defaults to 1. Contributors can omit this field. |
| `wikiDataId` | string | The unique ID from wikiData.org |

### cities.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | -------------- |
| `id` | integer | Unique ID - omit for new cities (auto-assigned) | Auto
| `name` | string | The official name of the city. Use WikiData or Wikipedia or some other legitimate source. | required
| `state_id` | integer | Unique id of parent state from `states.sql` | required
| `state_code` | string | ISO code of the parent state | required
| `country_id` | integer | Unique id of parent country from `countries.sql` | required
| `country_code` | string | ISO2 code of the parent country | required
| `latitude` | decimal | Latitude coordinates | required
| `longitude` | decimal | Longitude coordinates | required
| `native` | string | Native name of the city |
| `population` | integer | Population of the city - [Wikipedia](https://en.wikipedia.org/wiki/List_of_cities_by_population) |
| `type` | string | Type of settlement (city, town, village, etc.) |
| `level` | integer | Administrative level |
| `parent_id` | integer | ID of parent administrative division |
| `timezone` | string | IANA timezone identifier (e.g., America/New_York) - **REQUIRED for all cities** |
| `translations` | text | JSON object with name translations |
| `created_at` | timestamp | Optional - Creation timestamp (ISO 8601 format). If omitted, database uses default value. |
| `updated_at` | timestamp | Optional - Last update timestamp (ISO 8601 format). If omitted, database auto-updates. |
| `flag`| boolean | Optional - Auto-managed by system, defaults to 1. Contributors can omit this field. |
| `wikiDataId` | string | The unique ID from wikiData.org |

## Data Quality Guidelines

### Required Data Standards

#### Timezone Information (Critical!)
- **100% of cities MUST have valid IANA timezone identifiers**
- Use tools like [TimeZoneDB](https://timezonedb.com/) or [GeoNames](https://www.geonames.org/) to find correct timezones
- Format: `Continent/City` (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`)
- **Why it matters**: This database maintains 100% timezone coverage - don't break it!

#### Coordinates Accuracy
- Use precise decimal coordinates (minimum 5 decimal places recommended)
- Verify coordinates using Google Maps, OpenStreetMap, or official sources
- Format:
  - Latitude: -90 to +90 (negative = South, positive = North)
  - Longitude: -180 to +180 (negative = West, positive = East)

#### Naming Conventions
- Use official, commonly recognized names in English
- Add native names in the `native` field
- Use proper capitalization (e.g., "New York" not "new york")
- Avoid abbreviations unless officially used (e.g., "St." in "St. Louis" is acceptable)

### Data Sources

**Recommended Sources (in priority order):**
1. **Official Government Websites** - Most authoritative
2. **WikiData** ([wikidata.org](https://www.wikidata.org/)) - Structured, multilingual data
3. **Wikipedia** - Well-sourced, community-verified
4. **GeoNames** ([geonames.org](https://www.geonames.org/)) - Comprehensive geographic database
5. **OpenStreetMap** - Community-maintained geographic data

**Always include source in your PR description!**

### Common Mistakes to Avoid

❌ **Don't Do This:**
- Adding cities without timezone information
- Using approximate coordinates (e.g., country center for city location)
- Copying data without verification
- Adding duplicate entries (check first!)
- Using non-standard timezone names (e.g., "PST" instead of "America/Los_Angeles")

✅ **Do This Instead:**
- Research proper IANA timezone for each city
- Use precise coordinates for the city center or main landmark
- Verify data from multiple reliable sources
- Search existing data before adding new entries
- Use official IANA timezone database format

### Population Data (Optional but Recommended)

When adding population data:
- Use recent census data or official estimates
- Include source year if possible in PR description
- Round to reasonable precision (avoid false precision)
- **Format**: Integer (e.g., `1000000` not `"1,000,000"`)

### How to Find Foreign Keys

**Finding State IDs:**
```bash
# Search in contributions/states/states.json
grep -A 5 '"name": "California"' contributions/states/states.json
```

**Finding Country IDs:**
```bash
# Search in contributions/countries/countries.json
grep -A 5 '"name": "United States"' contributions/countries/countries.json
```

Or use the [CSC Update Tool](https://manager.countrystatecity.in/) which automatically looks up IDs for you!

## Pull Request Guidelines

### Before Submitting

- [ ] Data verified from authoritative sources
- [ ] Timezone validated using IANA timezone database
- [ ] Coordinates checked on a map
- [ ] No duplicate entries
- [ ] Source included in PR description
- [ ] Only JSON files in `contributions/` edited

### PR Description Template

```markdown
## Summary
[Brief description of changes]

## Type of Change
- [ ] New city/state/country
- [ ] Update existing data
- [ ] Fix incorrect data
- [ ] Add missing fields

## Data Sources
- Source 1: [URL]
- Source 2: [URL]

## Checklist
- [ ] Timezones verified
- [ ] Coordinates verified
- [ ] Data sources cited
- [ ] No duplicate entries
```

### Review Process

1. **Automated Checks**: GitHub Actions validates JSON format
2. **Data Import**: Your changes are imported to MySQL
3. **Export Generation**: All 11 formats regenerated
4. **Maintainer Review**: Human review of data quality and sources
5. **Merge**: Changes go live in next release!

## Need Help?

### Tools & Resources
- **[CSC Update Tool](https://manager.countrystatecity.in/)** - Easiest way to contribute (GUI)
- **[API Documentation](https://docs.countrystatecity.in/)** - Explore existing data
- **[Demo Database](https://demo.countrystatecity.in/)** - Browse online
- **[IANA Timezone Database](https://www.iana.org/time-zones)** - Official timezone reference

### Questions?
- Open a [GitHub Discussion](https://github.com/dr5hn/countries-states-cities-database/discussions)
- Check existing [Issues](https://github.com/dr5hn/countries-states-cities-database/issues)
- Review [contributions/README.md](../contributions/README.md) for detailed examples

## Recognition

All contributors are recognized in our [README](../README.md) and commit history. Thank you for helping maintain the most comprehensive open geographical database! 🌍
