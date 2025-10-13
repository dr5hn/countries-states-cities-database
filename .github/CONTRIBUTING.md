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
- ❌ **DON'T**: Run build scripts or exports locally (GitHub Actions handles this)
- 🔒 **MySQL workflow**: Reserved for repository maintainers only

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
| `country_id` | integer | Unique id of parent country from `countries.sql` | required |
| `country_code` | string | ISO2 code of the parent country | required |
| `fips_code` | string | ISO-3166-2 subdivision code for the state |
| `iso2` | string | ISO2 code of the parent state |
| `iso3166_2` | string | ISO 3166-2 subdivision code |
| `type` | string | Type of state (province, state, etc.) |
| `level` | integer | Administrative level of the subdivision |
| `parent_id` | integer | ID of parent administrative division |
| `native` | string | Native name of the state |
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
| `timezone` | string | IANA timezone identifier (e.g., America/New_York) |
| `translations` | text | JSON object with name translations |
| `created_at` | timestamp | Optional - Creation timestamp (ISO 8601 format). If omitted, database uses default value. |
| `updated_at` | timestamp | Optional - Last update timestamp (ISO 8601 format). If omitted, database auto-updates. |
| `flag`| boolean | Optional - Auto-managed by system, defaults to 1. Contributors can omit this field. |
| `wikiDataId` | string | The unique ID from wikiData.org |
