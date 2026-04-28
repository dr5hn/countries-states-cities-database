<div align="center">

![banner](.github/images/banner.png)

# Countries States Cities Database

A comprehensive, community-maintained dataset of **countries, states, cities, and postcodes** — published in 11 formats and free under the [Open Database License](LICENSE).

[![License: ODbL-1.0](https://img.shields.io/badge/License-ODbL--1.0-brightgreen.svg?style=flat-square)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dr5hn/countries-states-cities-database.svg?style=flat-square)](https://github.com/dr5hn/countries-states-cities-database/stargazers)
![release](https://img.shields.io/github/v/release/dr5hn/countries-states-cities-database?style=flat-square)
[![NPM](https://img.shields.io/npm/v/@countrystatecity/countries.svg?style=flat-square&label=npm)](https://www.npmjs.com/package/@countrystatecity/countries)
[![PyPI](https://img.shields.io/pypi/v/countrystatecity-countries.svg?style=flat-square&label=pypi)](https://pypi.org/project/countrystatecity-countries/)

[**API**](https://countrystatecity.in/) ·
[**NPM**](https://www.npmjs.com/package/@countrystatecity/countries) ·
[**Demo**](https://demo.countrystatecity.in/) ·
[**Docs**](https://docs.countrystatecity.in/) ·
[**Playground**](https://playground.countrystatecity.in/) ·
[**Export Tool**](https://export.countrystatecity.in/)

</div>

<sub>
Total Regions : 6 <br>
Total Sub Regions : 22 <br>
Total Countries : 250 <br>
Total States/Regions/Municipalities : 5,299 <br>
Total Cities/Towns/Districts : 153,765 <br>
Total Timezones : 427 (100% IANA coverage) <br>
Last Updated On: April 28, 2026
</sub>

---

## Overview

- **250** countries · **5,299** states · **153,765** cities · **100k+** postcodes across ~50 countries
- **11 formats** — JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB, XML, YAML, CSV, GeoJSON, TOON
- **19 languages** of country and state names plus native script
- **100% IANA timezone coverage** for cities
- **Validated foreign keys** on every PR — no orphans
- **ODbL-licensed** — commercial use, modification, and redistribution all allowed

---

## Quick start

### JavaScript / TypeScript

```bash
npm install @countrystatecity/countries
```

```js
import { Country, State, City } from '@countrystatecity/countries';

const usStates = State.getStatesOfCountry('US');
const sf = City.getCitiesOfState('US', 'CA').find(c => c.name === 'San Francisco');
```

Zero dependencies, TypeScript-first, tree-shakeable, works offline.
[GitHub](https://github.com/dr5hn/countrystatecity-countries) ·
[NPM](https://www.npmjs.com/package/@countrystatecity/countries)

### Python

```bash
pip install countrystatecity-countries
```

```python
from countrystatecity_countries import Country, State, City

us_states = State.get_states_of_country('US')
```

Plays well with Django, Flask, FastAPI.
[GitHub](https://github.com/dr5hn/countrystatecity-pypi) ·
[PyPI](https://pypi.org/project/countrystatecity-countries/)

### REST API

```bash
curl https://api.countrystatecity.in/v1/countries/IN/states/MH/cities \
  -H "X-CSCAPI-KEY: $YOUR_API_KEY"
```

Use from any language.
[Get a key](https://countrystatecity.in/) ·
[Docs](https://docs.countrystatecity.in/) ·
[Playground](https://playground.countrystatecity.in/) ·
[OpenAPI spec](https://github.com/dr5hn/csc-swagger) ·
[Status](https://status.countrystatecity.in/)

### Direct download

Every format ships as a gzipped asset on each
[GitHub Release](https://github.com/dr5hn/countries-states-cities-database/releases).

```bash
curl -LO https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/json-cities.json.gz
gunzip json-cities.json.gz
```

Smaller reference files (countries, states, schema) live in the repo.
Use `git clone --depth 1` for a fast clone.

### Custom slices

The [Export Tool](https://export.countrystatecity.in/) builds tailored datasets —
pick by region, country, or format with custom field selection.

---

## Ecosystem

### Data products

| Product | Use case | Links |
|---|---|---|
| `@countrystatecity/countries` (NPM) | JavaScript / TypeScript apps, offline use | [npmjs](https://www.npmjs.com/package/@countrystatecity/countries) · [GitHub](https://github.com/dr5hn/countrystatecity-countries) |
| `countrystatecity-countries` (PyPI) | Python apps | [pypi](https://pypi.org/project/countrystatecity-countries/) · [GitHub](https://github.com/dr5hn/countrystatecity-pypi) |
| `@countrystatecity/countries-browser` | CDN-loaded, lazy, no bundled data | [GitHub](https://github.com/dr5hn/countrystatecity-countries-browser) |
| `@countrystatecity/timezones` | Dedicated timezone data | [GitHub](https://github.com/dr5hn/countrystatecity-timezones) |
| Raw exports (this repo) | SQL / CSV / JSON / etc. | [Releases](https://github.com/dr5hn/countries-states-cities-database/releases) |

### Services

| Service | Use case | Link |
|---|---|---|
| REST API | Production apps in any language | [countrystatecity.in](https://countrystatecity.in/) |
| API documentation | Endpoints, parameters, examples | [docs.countrystatecity.in](https://docs.countrystatecity.in/) |
| Interactive playground | Try requests live in Swagger UI | [playground.countrystatecity.in](https://playground.countrystatecity.in/) |
| OpenAPI specification | Generate SDKs in any language | [csc-swagger](https://github.com/dr5hn/csc-swagger) |
| Status page | Uptime and incident history | [status.countrystatecity.in](https://status.countrystatecity.in/) |

### Tools

| Tool | Use case | Link |
|---|---|---|
| Export Tool | Slice the database by country / region / format | [export.countrystatecity.in](https://export.countrystatecity.in/) |
| Database browser | Query and explore live data | [demo.countrystatecity.in](https://demo.countrystatecity.in/) |
| Encyclopedia | Country profiles and geographical insights | [countrystatecity.org](https://countrystatecity.org/) |
| Community Manager | Submit data corrections via web UI | [manager.countrystatecity.in](https://manager.countrystatecity.in/) |
| Command line interface | Query CSC data from your terminal | [cli.countrystatecity.in](https://cli.countrystatecity.in/) |

### Also distributed via

[Kaggle](https://www.kaggle.com/datasets/darshangada/countries-states-cities-database/data) — data-science notebooks ·
[Data.world](https://data.world/dr5hn/country-state-city) — analytics platforms

---

## Available formats

**Core (every release):**
JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB, XML, YAML, CSV.

**Specialty:**

- **GeoJSON** — RFC 7946, Point geometry. Drops into Leaflet, Mapbox, PostGIS.
- **[TOON](https://github.com/toon-format/toon)** — Token-Oriented Object Notation,
  ~40% fewer tokens than JSON for LLM context windows.
- **DuckDB** — convert SQLite via [`bin/scripts/export/import_duckdb.py`](bin/scripts/export/import_duckdb.py)
  for analytics workloads.

**Coverage matrix:**

| Table | Per-table file | Combined file |
|---|---|---|
| Regions, Subregions, Countries, States, Cities | All formats | — |
| Postcodes (~50 countries) | All formats | — |
| Country + States, Country + Cities | JSON only | — |
| Full world (Country + State + Cities) | — | JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB |

---

## Performance

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

**API response times (typical):** countries 50ms · states 180ms · cities by state 80ms · search 120ms.

**Picking a format:**

- Web / mobile → JSON or CSV
- Direct database import → MySQL, PostgreSQL, SQLite, SQL Server
- Maps / GIS → GeoJSON
- AI / LLM context → TOON
- Analytics / OLAP → SQLite or DuckDB

---

## Repository architecture

Two-phase build. JSON in version control, MySQL as the canonical store,
every format auto-regenerated.

```
contributions/  →  [Python import]  →  MySQL  →  [PHP export]  →  json/, csv/, xml/, sql/, ...
```

- **Contributors** edit JSON in `contributions/`. GitHub Actions re-imports,
  exports every format, and uploads `.gz` assets to a Release.
- **Maintainers** can also work SQL-first — `sync_mysql_to_json.py` rewrites
  the contributions tree from MySQL.
- **Users** download the format they want; they're all in sync per release.

Every PR runs schema, cross-reference, coordinate-bounds, and duplicate
validators. Full build and maintenance reference:
[`.claude/CLAUDE.md`](.claude/CLAUDE.md).

---

## Contributing

The easiest way is the [Community Manager](https://manager.countrystatecity.in/) —
browse, search, and submit corrections through a web UI with end-to-end tracking.

To edit JSON directly:

1. Fork and clone the repository (`git clone --depth 1` is fastest).
2. Edit files under `contributions/cities/`, `contributions/states/`,
   `contributions/countries/`, or `contributions/postcodes/`.
3. **Required** for new cities: `name`, `state_id`, `state_code`, `country_id`,
   `country_code`, `latitude`, `longitude`. **Optional**: `timezone`, `wikiDataId`, `native`.
4. **Omit** `id`, `created_at`, `updated_at`, `flag` — auto-managed by MySQL on import.
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

> Don't edit the auto-generated directories (`json/`, `csv/`, `xml/`, `yml/`,
> `sql/`, etc.). They're rebuilt from MySQL on every release.

---

## Optional snippets

### MongoDB import

```bash
curl -LO https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/mongodb-world-mongodb-dump.tar.gz
tar -xzvf mongodb-world-mongodb-dump.tar.gz
mongorestore --host localhost:27017 --db world mongodb-dump/world
```

### SQLite to DuckDB

```bash
pip install duckdb
python3 bin/scripts/export/import_duckdb.py \
  --input sqlite/world.sqlite3 \
  --output duckdb/world.db
```

---

## License and attribution

Licensed under the [Open Database License (ODbL v1.0)](LICENSE).
Use commercially, modify, redistribute — give credit and keep derivatives open.

```
Data by Countries States Cities Database
https://github.com/dr5hn/countries-states-cities-database | ODbL v1.0
```

## Disclaimer

Community-maintained data may contain errors or lag behind geopolitical
changes. Verify critical data with official sources.
[Report issues](https://github.com/dr5hn/countries-states-cities-database/issues).

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

---

<div align="center">

![Repo Activity](https://repobeats.axiom.co/api/embed/635051d1a8be17610a967b7b07b65c0148f13654.svg)

**Thanks to our [contributors](https://github.com/dr5hn/countries-states-cities-database/graphs/contributors).**

<a href="https://github.com/dr5hn/countries-states-cities-database/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=dr5hn/countries-states-cities-database&anon=1" />
</a>

<sub>Made with <a href="https://contrib.rocks">contrib.rocks</a></sub>

</div>
