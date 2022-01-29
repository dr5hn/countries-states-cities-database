# Contributing to Country State City Database

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to Contributing to Country State City Database. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

### Reporting Data Related Issues
- Raise an issue for data errors.
- Mark those issues with a `bug` label.

### Suggesting Enhancements
- Raise an Issue for suggesting enhancements.
- Mark those issues with a `enhancement` label.

### Fixing Data By Yourself
If you want to fix some data and raise a pull request
- To fix cities records - You need to update `sql/cities.sql` and `sql/world.sql`.
- To fix states/regions records - You need to update `sql/states.sql` and `sql/world.sql`
- To fix countries records - You need to update `sql/countries.sql` and `sql/world.sql`

## Glance at Table Structure

`id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `iso3` char(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numeric_code` char(3) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `iso2` char(2) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phonecode` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `capital` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `currency` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `currency_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `currency_symbol` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tld` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `native` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `region` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subregion` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `timezones` text COLLATE utf8mb4_unicode_ci,
  `translations` text COLLATE utf8mb4_unicode_ci,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `emoji` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `emojiU` varchar(191) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag` tinyint(1) NOT NULL DEFAULT '1',


### countries.sql
| Column | Data type | Explanation |
| ----------------- | --------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. |
| `name` | string | The official name of the state. Use WikiData or Wikipedia or some other legitimate source. |
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
| `subregion` | string | A subregion where country belongs to |
| `timezones` | text | An array of timezones  |
| `translations` | text | An array of country name translations |
| `latitude` | float | Google Maps |
| `longitude` | float | Google Maps |
| `emoji` | float | A flag emoji icon |
| `emojiU` | float | A flag emoji unicode characters |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID for this state on wikiData |

### states.sql
| Column | Data type | Explanation |
| ----------------- | --------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. |
| `name` | string | The official name of the state. Use WikiData or Wikipedia or some other legitimate source. |
| `country_id` | integer | Unique id of parent country from `countries.sql` |
| `country_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country |
| `fips_code` | string |  ISO-3166-2 subdivision code for the state. Can be found in wikipedia articles such as this: [ISO_3166-2:NO](https://en.wikipedia.org/wiki/ISO_3166-2:NO). [FIPS county codes](https://en.wikipedia.org/wiki/FIPS_county_code) were deprecated in 2008, so surely we aren't using them? |
| `iso2` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state |
| `type` | string | Type of state (province, state etc.) Source [ISO Official Site](iso.org/obp/ui/#iso:code:3166:NO)  |
| `latitude` | float | Google Maps |
| `longitude` | float | Google Maps |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID for this state on wikiData |

### cities.sql
| Column | Data type | Explanation |
| ----------------- | --------------- | -------------- |
| `id` | integer | Unique ID used internally, just increment by one when adding entries to the list. |
| `name` | string | The official name of the state. Use WikiData or Wikipedia or some other legitimate source. |
| `state_id` | integer | Unique id of parent state from `states.sql` |
| `state_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent state |
| `country_id` | integer | Unique id of parent country from `countries.sql` |
| `country_code` | string | [ISO3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code of the parent country |
| `latitude` | float | Google Maps |
| `longitude` | float | Google Maps |
| `created_at` | timestamp | Set it using NOW() |
| `updated_at` | timestamp | Automatically Updated |
| `flag`| tinyint | 1/0 (automatically set to 1 by default)|
| `wikiDataId` | string | The unique ID for this state on wikiData |
