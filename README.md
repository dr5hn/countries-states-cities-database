<div align="center">

![banner](.github/images/banner.png)

# Countries States Cities Database

A comprehensive, community-maintained dataset of **countries, states, cities, and postcodes** — published in 11 formats and free under the [Open Database License](LICENSE) **(attribution required)**.

[![License: ODbL-1.0](https://img.shields.io/badge/License-ODbL--1.0-brightgreen.svg?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dr5hn/countries-states-cities-database.svg?style=flat-square)](https://github.com/dr5hn/countries-states-cities-database/stargazers)
![release](https://img.shields.io/github/v/release/dr5hn/countries-states-cities-database?style=flat-square)
[![NPM](https://img.shields.io/npm/v/@countrystatecity/countries.svg?style=flat-square&label=npm)](https://www.npmjs.com/package/@countrystatecity/countries)
[![PyPI](https://img.shields.io/pypi/v/countrystatecity-countries.svg?style=flat-square&label=pypi)](https://pypi.org/project/countrystatecity-countries/)

</div>

Total Regions : 6 <br>
Total Sub Regions : 22 <br>
Total Countries : 250 <br>
Total States/Regions/Municipalities : 5,299 <br>
Total Cities/Towns/Districts : 153,765 <br>
Total Postcodes : 660,381 (79 countries) <br>
Total Timezones : 427 (100% IANA coverage) <br>
Last Updated On: April 28, 2026

---

## Recommended for production

The two managed products below are the fastest path to shipping. They're actively maintained, billed for sustainability, and back the rest of the ecosystem.

### REST API — `api.countrystatecity.in`

Query countries, states, cities, and postcodes from any language. Free tier for prototyping; paid tiers for production.

```bash
curl https://api.countrystatecity.in/v1/countries/IN/states/MH/cities \
  -H "X-CSCAPI-KEY: $YOUR_API_KEY"
```

[**Get an API key →**](https://countrystatecity.in/) ·
[Documentation](https://docs.countrystatecity.in/) ·
[Interactive playground](https://playground.countrystatecity.in/) ·
[OpenAPI spec](https://github.com/dr5hn/csc-swagger) ·
[Status](https://status.countrystatecity.in/)

### Export Tool — `export.countrystatecity.in`

Build tailored datasets in your browser — pick country, region, format, and field selection, then download.

[**Launch the Export Tool →**](https://export.countrystatecity.in/)

---

## Other ways to use the data

<details>
<summary><strong>NPM (JavaScript / TypeScript)</strong></summary>

```bash
npm install @countrystatecity/countries
```

```js
import { Country, State, City } from '@countrystatecity/countries';
const usStates = State.getStatesOfCountry('US');
```

[GitHub](https://github.com/dr5hn/countrystatecity-countries) ·
[NPM](https://www.npmjs.com/package/@countrystatecity/countries)

</details>

<details>
<summary><strong>PyPI (Python)</strong></summary>

```bash
pip install countrystatecity-countries
```

```python
from countrystatecity_countries import Country, State, City
us_states = State.get_states_of_country('US')
```

[GitHub](https://github.com/dr5hn/countrystatecity-pypi) ·
[PyPI](https://pypi.org/project/countrystatecity-countries/)

</details>

<details>
<summary><strong>Direct download (gzipped exports)</strong></summary>

Every format ships as a `.gz` asset on each [GitHub Release](https://github.com/dr5hn/countries-states-cities-database/releases).

```bash
curl -LO https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/json-cities.json.gz
gunzip json-cities.json.gz
```

Smaller reference files (countries, states, schema) live in the repo. Use `git clone --depth 1` for a fast clone.

</details>

<details>
<summary><strong>Other packages and platforms</strong></summary>

- [`@countrystatecity/countries-browser`](https://github.com/dr5hn/countrystatecity-countries-browser) — CDN-loaded, lazy
- [`@countrystatecity/timezones`](https://github.com/dr5hn/countrystatecity-timezones) — dedicated timezone data
- [Database browser](https://demo.countrystatecity.in/) — query and explore live data
- [Encyclopedia](https://countrystatecity.org/) — country profiles and insights
- [Community Manager](https://manager.countrystatecity.in/) — submit corrections via web UI
- [CLI](https://cli.countrystatecity.in/) — terminal access
- [Kaggle](https://www.kaggle.com/datasets/darshangada/countries-states-cities-database/data) · [Data.world](https://data.world/dr5hn/country-state-city)

</details>

---

## What's in the data

- **250** countries · **5,299** states / regions · **153,765** cities · **100k+** postcodes across ~50 countries
- **19 languages** of country and state names plus native script
- **100% IANA timezone coverage** for cities
- **Validated foreign keys** on every contribution
- **Formats:** JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB, XML, YAML, CSV, GeoJSON, [TOON](https://github.com/toon-format/toon) (LLM-optimised, ~40% fewer tokens than JSON)

| Format | Export time | Size | Compressed |
|---|---:|---:|---:|
| CSV | 1s | 40 MB | 9 MB |
| MongoDB dump | 1s | 30 MB | 20 MB |
| MySQL SQL | 3s | 86 MB | 22 MB |
| JSON | 4s | 271 MB | 18 MB |
| TOON | 5s | 23 MB | 20 MB |
| GeoJSON | 8s | 208 MB | 24 MB |
| XML | 9s | 91 MB | 15 MB |
| YAML | 17s | 68 MB | — |
| SQLite | 45s | 89 MB | — |

---

## Contributing

The easiest way is the [Community Manager](https://manager.countrystatecity.in/) — submit corrections through a web UI with end-to-end tracking.

To edit JSON directly:

1. Fork and clone (`git clone --depth 1`).
2. Edit files under `contributions/cities/`, `contributions/states/`, `contributions/countries/`, or `contributions/postcodes/`.
3. **Required** for new cities: `name`, `state_id`, `state_code`, `country_id`, `country_code`, `latitude`, `longitude`. **Optional**: `timezone`, `wikiDataId`, `native`.
4. **Omit** `id`, `created_at`, `updated_at`, `flag` — auto-managed on import.
5. Open a pull request with a clear data source.

```json
{
  "name": "San Francisco",
  "state_id": 1416,
  "state_code": "CA",
  "country_id": 233,
  "country_code": "US",
  "latitude": "37.77493",
  "longitude": "-122.41942",
  "timezone": "America/Los_Angeles",
  "wikiDataId": "Q62"
}
```

[Contributions guide](contributions/README.md) ·
[Contribution guidelines](.github/CONTRIBUTING.md) ·
[Multi-level territories policy](MULTI_LEVEL_TERRITORIES.md)

> Don't edit the auto-generated directories (`json/`, `csv/`, `xml/`, `yml/`, `sql/`, etc.). They're rebuilt from MySQL on every release.

---

## License and attribution

Licensed under the [Open Database License (ODbL v1.0)](LICENSE). Commercial use, modification, and redistribution all permitted. **Attribution is required**, and derivatives must be shared under the same license.

```
Data by Countries States Cities Database
https://github.com/dr5hn/countries-states-cities-database | ODbL v1.0
```

---

## Support

If this project saves you time, please consider supporting its continued maintenance.

[![Sponsor on GitHub](https://raw.githubusercontent.com/dr5hn/dr5hn/main/.github/resources/github_sponsor_btn.svg)](https://github.com/sponsors/dr5hn)
[![Buy a coffee](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/dr5hn)

You can also [plant a tree](https://ecologi.com/darshangada?r=60f2a36e67efcb18f734ffb8) on behalf of the project.

**Reach out:** gadadarshan [at] gmail [dot] com

<a href="https://github.com/dr5hn/"><img alt="GitHub @dr5hn" src="https://img.shields.io/static/v1?logo=github&message=GitHub&color=black&style=flat-square&label=" /></a>
<a href="https://twitter.com/dr5hn/"><img alt="Twitter @dr5hn" src="https://img.shields.io/static/v1?logo=twitter&message=Twitter&color=black&style=flat-square&label=" /></a>
<a href="https://www.linkedin.com/in/dr5hn/"><img alt="LinkedIn @dr5hn" src="https://img.shields.io/static/v1?logo=linkedin&message=LinkedIn&color=black&style=flat-square&label=" /></a>

### Sponsors

<p align="center">
  <a href="https://cdn.jsdelivr.net/gh/dr5hn/static/sponsors.svg">
    <img src='https://cdn.jsdelivr.net/gh/dr5hn/static/sponsors.svg'/>
  </a>
</p>

## Disclaimer

Community-maintained data may contain errors or lag behind geopolitical changes. Verify critical data with official sources. [Report issues](https://github.com/dr5hn/countries-states-cities-database/issues).

---

<div align="center">

![Repo Activity](https://repobeats.axiom.co/api/embed/635051d1a8be17610a967b7b07b65c0148f13654.svg)

**Thanks to our [contributors](https://github.com/dr5hn/countries-states-cities-database/graphs/contributors).**

<a href="https://github.com/dr5hn/countries-states-cities-database/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=dr5hn/countries-states-cities-database&anon=1" />
</a>

</div>
