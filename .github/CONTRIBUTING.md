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
Run the build script to generate the database:
```bash
python3 bin/build_from_contributions.py
```

**Note:** SQL files are automatically generated from the JSON contribution files during the build process. Please do not edit SQL files directly.

## Glance at Table Structure

### regions.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the region. Use WikiData or Wikipedia or some other legitimate source. | required
| `translations` | text | An array of region name translations |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| boolean | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### subregions.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the subregion. Use WikiData or Wikipedia or some other legitimate source. | required
| `translations` | text | An array of subregion name translations |
| `region_id` | integer | Unique id of region from `regions.sql` | required
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| boolean | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### countries.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the country. Use WikiData or Wikipedia or some other legitimate source. | required
| `iso3` | string | [ISO3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the country |
| `numeric_code` | string | Source [ISO Official Site](iso.org/obp/ui/#iso:code:3166:NO) |
| `iso2` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the country |
| `phonecode` | string | Phone code of the country |
| `capital` | string | Capital city of the country |
| `currency` | string | Currency code of the country |
| `currency_name` | string | Currency pronunciation of the country |
| `currency_symbol` | string | Currency symbol of the country |
| `tld` | string | Domain code of the country |
| `native` | string | Native name of the country |
| `population` | number | Population of the country - [Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population) |
| `gdp` | number | GDP of the country - [Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)) |
| `region` | string | A region where country belongs to |
| `region_id` | integer | Unique id of region from `regions.sql` |
| `subregion` | string | A subregion where country belongs to |
| `subregion_id` | integer | Unique id of subregion from `subregions.sql` |
| `nationality` | string | Nationality/demonym of the country |
| `timezones` | text | An array of timezones  |
| `translations` | text | An array of country name translations |
| `latitude` | decimal | Latitude coordinates |
| `longitude` | decimal | Longitude coordinates |
| `emoji` | string | A flag emoji icon |
| `emojiU` | string | A flag emoji unicode characters |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| boolean | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### states.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required |
| `name` | string | The official name of the state. Use WikiData or Wikipedia or some other legitimate source. | required |
| `country_id` | integer | Unique id of parent country from `countries.sql` | required |
| `country_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country | required |
| `fips_code` | string |  ISO-3166-2 subdivision code for the state. Can be found in wikipedia articles such as this: [ISO_3166-2:NO](https://en.wikipedia.org/wiki/ISO_3166-2:NO). [FIPS county codes](https://en.wikipedia.org/wiki/FIPS_county_code) were deprecated in 2008, so surely we aren't using them? |
| `iso2` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state |
| `iso3166_2` | string | ISO 3166-2 subdivision code |
| `type` | string | Type of state (province, state etc.) Source [ISO Official Site](iso.org/obp/ui/#iso:code:3166:NO)  |
| `level` | integer | Administrative level of the subdivision |
| `parent_id` | integer | ID of parent administrative division |
| `native` | string | Native name of the state (Google Translate) |
| `latitude` | decimal | Latitude coordinates |
| `longitude` | decimal | Longitude coordinates |
| `timezone` | string | IANA timezone identifier (e.g., America/New_York) |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| boolean | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### cities.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the city. Use WikiData or Wikipedia or some other legitimate source. | required
| `state_id` | integer | Unique id of parent state from `states.sql` | required
| `state_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state | required
| `country_id` | integer | Unique id of parent country from `countries.sql` | required
| `country_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country | required
| `latitude` | decimal | Latitude coordinates | required
| `longitude` | decimal | Longitude coordinates | required
| `timezone` | string | IANA timezone identifier (e.g., America/New_York) |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| boolean | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |
