# Contributing to Country State City Database

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to Contributing to Country State City Database. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?
### Fixing Data By Yourself
If you want to fix some data and raise a pull request
- To fix cities records, update the `sql/world.sql` > cities Table.
- To fix states/provinces records, update the `sql/world.sql` > states Table.
- To fix countries records, update the `sql/world.sql` > countries Table.
- To fix regions records, update the `sql/world.sql` > regions Table.
- To fix subregions records, update the `sql/world.sql` > subregions Table.

## Glance at Table Structure

### regions.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the region. Use WikiData or Wikipedia or some other legitimate source. | required
| `translations` | text | An array of region name translations |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### subregions.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the subregion. Use WikiData or Wikipedia or some other legitimate source. | required
| `translations` | text | An array of subregion name translations |
| `region_id` | string | Unique id of region from `regions.sql` |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### countries.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | ------------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the country. Use WikiData or Wikipedia or some other legitimate source. | required
| `iso2` |char | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state |
| `iso3` | char | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country |
| `numeric_code` | char | Source [ISO Official Site](iso.org/obp/ui/#iso:code:3166:NO) |
| `phonecode` | string | Phone code of the country |
| `currency` | string | Currency code of the country |
| `currency_name` | string | Currency pronounciation of the country |
| `currency_symbol` | string | Currency symbol of the country |
| `tld` | string | Domain code of the country |
| `native` | string | Native name of the country |
| `region` | string | A region where country belongs to |
| `region_id` | string | Unique id of region from `regions.sql` |
| `subregion` | string | A subregion where country belongs to |
| `subregion_id` | string | Unique id of subregion from `subregions.sql` |
| `timezones` | text | An array of timezones  |
| `translations` | text | An array of country name translations |
| `latitude` | float | Google Maps |
| `longitude` | float | Google Maps |
| `emoji` | float | A flag emoji icon |
| `emojiU` | float | A flag emoji unicode characters |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### states.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required |
| `name` | string | The official name of the state. Use WikiData or Wikipedia or some other legitimate source. | required |
| `country_id` | integer | Unique id of parent country from `countries.sql` | required |
| `country_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country | required |
| `fips_code` | string |  ISO-3166-2 subdivision code for the state. Can be found in wikipedia articles such as this: [ISO_3166-2:NO](https://en.wikipedia.org/wiki/ISO_3166-2:NO). [FIPS county codes](https://en.wikipedia.org/wiki/FIPS_county_code) were deprecated in 2008, so surely we aren't using them? |
| `iso2` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state |
| `type` | string | Type of state (province, state etc.) Source [ISO Official Site](iso.org/obp/ui/#iso:code:3166:NO)  |
| `latitude` | float | Google Maps |
| `longitude` | float | Google Maps |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |

### cities.sql
| Column | Data type | Explanation | Required |
| ----------------- | --------------- | -------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. | required
| `name` | string | The official name of the city. Use WikiData or Wikipedia or some other legitimate source. | required
| `state_id` | integer | Unique id of parent state from `states.sql` | required
| `state_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state | required
| `country_id` | integer | Unique id of parent country from `countries.sql` | required
| `country_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country | required
| `latitude` | float | Google Maps |
| `longitude` | float | Google Maps |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID from wikiData.org |
