![banner](.github/images/banner.png)

# 🌍 Countries States Cities Database

[![License: ODbL-1.0](https://img.shields.io/badge/License-ODbL--1.0-brightgreen.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dr5hn/countries-states-cities-database.svg?style=flat-square)](https://github.com/dr5hn/countries-states-cities-database/stargazers)
![release](https://img.shields.io/github/v/release/dr5hn/countries-states-cities-database?style=flat-square)
![size](https://img.shields.io/github/repo-size/dr5hn/countries-states-cities-database?label=size&style=flat-square)

Comprehensive geographical database — countries, states, cities, and **postcodes** for ~50 countries — published in 11 formats (JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB, XML, YAML, CSV, GeoJSON, TOON). Updated monthly. Free under [ODbL](LICENSE).

<sub>
Total Regions : 6 <br>
Total Sub Regions : 22 <br>
Total Countries : 250 <br>
Total States/Regions/Municipalities : 5,299 <br>
Total Cities/Towns/Districts : 153,765 <br>
Total Timezones : 427 (100% IANA coverage) <br>
Last Updated On: April 28, 2026
</sub>

> **What's new in [v3.2](https://github.com/dr5hn/countries-states-cities-database/releases/tag/v3.2)** (April 2026): France & Italy cities re-parented from regions to departments/provinces (FR/03 Allier and IT/AG Agrigento now resolve correctly); +486 missing French communes; FR-overseas territories (GF, BL, MF, PM, TF) populated; FR + IT state `level` field normalised; postcode bulk imports for ~12 new countries (CN, MM, MT, MU, HU, LU, KH, VE, …). See the [CHANGELOG](CHANGELOG.md) for behaviour-change notes.

## Quick Start

Pick whichever fits your stack:

| Method | Install | Best for |
|---|---|---|
| **NPM** | `npm install @countrystatecity/countries` | JS/TS apps, offline use |
| **PyPI** | `pip install countrystatecity-countries` | Python, Django, Flask |
| **REST API** | [Get API key](https://countrystatecity.in/) | Production apps, any language |
| **Direct download** | [Releases](https://github.com/dr5hn/countries-states-cities-database/releases/latest) | SQL imports, one-off use |
| **Export tool** | [export.countrystatecity.in](https://export.countrystatecity.in/) | Custom regional/country slices |

```js
// NPM example
import { Country, State, City } from '@countrystatecity/countries';
const usStates = State.getStatesOfCountry('US');
```

```bash
# Direct download — large files ship as .gz on Releases
curl -LO https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/json-cities.json.gz
gunzip json-cities.json.gz
```

> **Cloning?** Use `git clone --depth 1` — large exports live on [Releases](https://github.com/dr5hn/countries-states-cities-database/releases), not in git history.

## Available Formats

**Core:** JSON · MySQL · PostgreSQL · SQLite · SQL Server · MongoDB · XML · YAML · CSV
**Geographic:** GeoJSON (RFC 7946, Point geometry)
**AI/LLM:** [TOON](https://github.com/toon-format/toon) (~40% fewer tokens than JSON)
**Convert-on-demand:** DuckDB — see [scripts/export/import_duckdb.py](bin/scripts/export/import_duckdb.py)

| Table | Per-table file | World file |
|---|---|---|
| Regions / Subregions / Countries / States / Cities | All formats | — |
| Postcodes (~50 countries) | All formats | — |
| Country + States / Country + Cities | JSON only | — |
| Country + States + Cities | — | JSON, MySQL, PostgreSQL, SQLite, SQL Server, MongoDB |

## Performance

| Format | Export | Size | .gz |
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

**Recommendations:** JSON/CSV for web · SQL/SQLite for direct DB import · GeoJSON for Leaflet/Mapbox/PostGIS · TOON for LLM context windows.

## Demo & Docs

- **Live demo:** [dr5hn.github.io/countries-states-cities-database](https://dr5hn.github.io/countries-states-cities-database/)
- **Browse data:** [demo.countrystatecity.in](https://demo.countrystatecity.in/)
- **API docs:** [docs.countrystatecity.in](https://docs.countrystatecity.in/) · [Playground](https://playground.countrystatecity.in/) · [OpenAPI spec](https://github.com/dr5hn/csc-swagger)
- **Status:** [status.countrystatecity.in](https://status.countrystatecity.in/)
- **CLI:** [cli.countrystatecity.in](https://cli.countrystatecity.in/)
- **Encyclopedia:** [countrystatecity.org](https://countrystatecity.org/)

## Repository Architecture

Two-phase build: JSON in version control → MySQL canonical → all formats regenerated.

```
contributions/  →  [Python import]  →  MySQL  →  [PHP export]  →  json/, csv/, xml/, sql/, …
```

- **Contributors** edit JSON in `contributions/`. GitHub Actions regenerates everything else.
- **Maintainers** treat MySQL as the single source of truth; dynamic schema detection keeps JSON ↔ MySQL in sync.
- **Users** download whichever format they want — all guaranteed in sync per release.

See [.claude/CLAUDE.md](.claude/CLAUDE.md) for the full build/maintenance reference.

## Contributing

**Easy way:** the [Community Manager](https://manager.countrystatecity.in/) — browse, search, and submit data change requests through a web UI.

[![Community Manager](.github/images/update-tool.png)](https://manager.countrystatecity.in/)

**Manual way:** edit JSON in `contributions/` directly.

1. Fork & clone (`--depth 1` recommended).
2. Edit files under `contributions/cities/`, `contributions/states/`, `contributions/countries/`, or `contributions/postcodes/`.
3. **Required fields** for new cities: `name`, `state_id`, `state_code`, `country_id`, `country_code`, `latitude`, `longitude`. Optional: `timezone`, `wikiDataId`.
4. **Omit** `id`, `created_at`, `updated_at`, `flag` — auto-managed by MySQL on import.
5. Open a PR with a clear data source.

```json
{
  "name": "San Francisco",
  "state_id": 1416,
  "state_code": "CA",
  "country_id": 233,
  "country_code": "US",
  "latitude": "37.77493",
  "longitude": "-122.41942",
  "timezone": "America/Los_Angeles"
}
```

📖 [contributions/README.md](contributions/README.md) · [Contribution Guidelines](.github/CONTRIBUTING.md) · [Multi-Level Territories Policy](MULTI_LEVEL_TERRITORIES.md)

> Don't edit auto-generated dirs (`json/`, `csv/`, `xml/`, `yml/`, `sql/`, etc.) — they're regenerated from MySQL by GitHub Actions.

## Optional: MongoDB import

```bash
curl -LO https://github.com/dr5hn/countries-states-cities-database/releases/latest/download/mongodb-world-mongodb-dump.tar.gz
tar -xzvf mongodb-world-mongodb-dump.tar.gz
mongorestore --host localhost:27017 --db world mongodb-dump/world
```

## Optional: SQLite → DuckDB

```bash
pip install duckdb
python3 bin/scripts/export/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db
```

## Also available on

[Kaggle](https://www.kaggle.com/datasets/darshangada/countries-states-cities-database/data) · [Data.world](https://data.world/dr5hn/country-state-city) · [NPM](https://www.npmjs.com/package/@countrystatecity/countries) · [PyPI](https://pypi.org/project/countrystatecity-countries/)

## License

[Open Database License (ODbL v1.0)](LICENSE) — use commercially, modify, redistribute. Just give credit and keep derivatives open.

```
Data by Countries States Cities Database
https://github.com/dr5hn/countries-states-cities-database | ODbL v1.0
```

## Disclaimer

Community-maintained data may contain errors or lag behind geopolitical changes. Verify critical data with official sources. [Report issues](https://github.com/dr5hn/countries-states-cities-database/issues).

## Support

[![Sponsor](https://raw.githubusercontent.com/dr5hn/dr5hn/main/.github/resources/github_sponsor_btn.svg)](https://github.com/sponsors/dr5hn) [![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/dr5hn) · Plant a tree: [ecologi.com/darshangada](https://ecologi.com/darshangada?r=60f2a36e67efcb18f734ffb8) · Reach out: gadadarshan[at]gmail[dot]com

<a href="https://github.com/dr5hn/"><img alt="Github @dr5hn" src="https://img.shields.io/static/v1?logo=github&message=Github&color=black&style=flat-square&label=" /></a> <a href="https://twitter.com/dr5hn/"><img alt="Twitter @dr5hn" src="https://img.shields.io/static/v1?logo=twitter&message=Twitter&color=black&style=flat-square&label=" /></a> <a href="https://www.linkedin.com/in/dr5hn/"><img alt="LinkedIn @dr5hn" src="https://img.shields.io/static/v1?logo=linkedin&message=LinkedIn&color=black&style=flat-square&label=" /></a>

---

![Repo Activity](https://repobeats.axiom.co/api/embed/635051d1a8be17610a967b7b07b65c0148f13654.svg)

Thanks to our [contributors](https://github.com/dr5hn/countries-states-cities-database/graphs/contributors) ❤️
