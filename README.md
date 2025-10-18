![banner](https://github.com/dr5hn/countries-states-cities-database/raw/master/.github/images/banner.png)


# 🌍 Countries States Cities Database
[![License: ODbL-1.0](https://img.shields.io/badge/License-ODbL--1.0-brightgreen.svg)](https://github.com/dr5hn/countries-states-cities-database/blob/master/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/dr5hn/countries-states-cities-database.svg?style=flat-square)](https://github.com/dr5hn/countries-states-cities-database/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/dr5hn/countries-states-cities-database.svg?style=flat-square)](https://github.com/dr5hn/countries-states-cities-database/network)
![release](https://img.shields.io/github/v/release/dr5hn/countries-states-cities-database?style=flat-square)
![size](https://img.shields.io/github/repo-size/dr5hn/countries-states-cities-database?label=size&style=flat-square)

Full Database of city state country available in JSON, MYSQL, PSQL, SQLITE, SQLSERVER, XML, YAML, MONGODB & CSV format.
All Countries, States & Cities are Covered & Populated with Different Combinations & Versions.

## Why Choose This Database?

* ✅ **Most Comprehensive** - 151,024+ cities from 250 countries, continuously updated by active community
* ✅ **Timezone Support** - IANA timezone identifiers for all states and cities based on geographic coordinates
* ✅ **Multilingual Support** - Built-in translations for countries, states, and cities in 19 languages (Arabic, Chinese, Dutch, French, German, Hindi, Italian, Japanese, Korean, Persian, Polish, Portuguese, Russian, Spanish, Turkish, Ukrainian, and more)
* ✅ **Multiple Integration Options** - NPM package, REST API, Export Tool, or direct downloads
* ✅ **Production Ready** - Trusted by thousands of developers worldwide in live applications
* ✅ **Always Up-to-Date** - Monthly updates with community contributions and data verification
* ✅ **Every Format You Need** - JSON, SQL, MongoDB, CSV, XML, YAML - use what fits your stack
* ✅ **100% Free & Open Source** - ODbL licensed with no usage restrictions
* ✅ **Developer Friendly** - Install via NPM in 1 minute or integrate API in 5 minutes
* ✅ **Battle-Tested Data** - 92%+ accuracy, verified by community across 250 countries

Save hundreds of hours collecting and maintaining geographical data. Get accurate, structured, ready-to-use data right now.

## Table of Contents
- [CSC Platform Ecosystem](#-csc-platform-ecosystem)
- [Choose Your Integration Method](#-choose-your-integration-method)
- [NPM Package](#-npm-package)
- [API](#api-)
- [Export Tool](#️-export-tool)
- [Available Formats](#available-formats)
- [Distribution Files Info](#distribution-files-info)
- [Demo](#demo)
- [Insights](#insights)
- [Import MongoDB](#import-mongodb)
- [Export to DuckDB](#export-to-duckdb)
- [License](#-license)
- [Contributing](#contributing)
- [Repo Activity](#repo-activity)
- [Sponsors](#sponsors)
- [Make the world more Greener](#make-the-world-more-greener-)
- [Available On Multiple Platforms](#-available-on-multiple-platforms)
- [Follow me at](#follow-me-at)
- [Support My Work](#️-support-my-work)
- [Suggestions / Feedbacks](#suggestions--feedbacks)
- [Disclaimer](#disclaimer)

## 🌐 CSC Platform Ecosystem

Easily access all the tools and services in the Countries States Cities platform:

| Tool            | Description                                      | Link                                      |
|-----------------|--------------------------------------------------|-------------------------------------------|
| **NPM Package**   | Official JavaScript/TypeScript package           | [@countrystatecity/countries](https://www.npmjs.com/package/@countrystatecity/countries) |
| **Documentation** | Complete API documentation and guides           | [docs.countrystatecity.in](https://docs.countrystatecity.in/) |
| **Demo Database** | Browse the full database online                  | [demo.countrystatecity.in](https://demo.countrystatecity.in/) |
| **API Service**   | Programmatic access to countries, states, cities | [countrystatecity.in](https://countrystatecity.in/)           |
| **Export Tool**   | Export data in multiple formats                  | [export.countrystatecity.in](https://export.countrystatecity.in/) |
| **Update Tool**   | Submit and track data change requests            | [manager.countrystatecity.in](https://manager.countrystatecity.in/) |
| **Status Page**   | Real-time service uptime and incidents           | [status.countrystatecity.in](https://status.countrystatecity.in/) |

## 🔄 Choose Your Integration Method

Not sure which solution fits your needs? Here's a quick comparison:

| Feature | NPM Package | REST API | Export Tool | Direct Download |
|---------|-------------|----------|-------------|-----------------|
| **Setup Time** | < 1 minute | < 5 minutes | < 2 minutes | Immediate |
| **Best For** | JavaScript/TypeScript apps | Any language, production apps | Custom datasets | One-time use, legacy systems |
| **Data Updates** | Manual (update package) | Automatic & real-time | On-demand | Manual download |
| **Works Offline** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Bundle Impact** | ~15-50 MB | None (API calls) | Varies | Varies |
| **Rate Limits** | None | Yes (by plan) | None | None |
| **Latest Data** | On package update | Always current | Current at export | Current at download |
| **Custom Filtering** | Code-based | API parameters | Web interface | Manual processing |
| **Cost** | Free | Free tier + paid plans | Free + paid credits | Free |
| **TypeScript Support** | ✅ Full types included | Via client libs | N/A | N/A |

### 🎯 Recommended Usage

**Choose NPM Package when:**
- ✅ Building forms with static dropdowns (shipping address, user registration)
- ✅ Working offline or with poor connectivity
- ✅ Small to medium projects with infrequent data changes
- ✅ Want zero latency (no network calls needed)
- ✅ Need to minimize hosting costs
- ✅ Using JavaScript/TypeScript/Node.js

**Choose REST API when:**
- ✅ Need real-time updates (new cities/states added regularly)
- ✅ Building multi-platform apps (iOS, Android, Web)
- ✅ Want smaller app bundle sizes
- ✅ Require guaranteed uptime & SLA
- ✅ Need advanced features (fuzzy search, autocomplete, geocoding)
- ✅ Enterprise applications with high traffic
- ✅ Using any programming language

**Choose Export Tool when:**
- ✅ Need specific countries or regions only
- ✅ Want custom data formats or structures
- ✅ Building analytics or one-time reports
- ✅ Require data transformation before use
- ✅ Testing or prototyping new features

**Choose Direct Download when:**
- ✅ Legacy systems or specific database requirements
- ✅ Need complete database dumps
- ✅ Working with SQL databases directly
- ✅ One-time import for internal tools

**Pro Tip:** Many developers start with the **NPM package** for rapid prototyping, then switch to the **REST API** for production when they need real-time updates and additional features! 🚀

## 📦 NPM Package

**Official JavaScript/TypeScript Package for Node.js and Browser**

We've launched an official NPM package that makes it incredibly easy to integrate this database into your JavaScript/TypeScript projects!

```bash
npm install @countrystatecity/countries
```

**Features:**
- 🚀 **Zero Dependencies** - Lightweight and fast
- 📘 **TypeScript Support** - Full type definitions included
- 🌐 **Works Everywhere** - Node.js, React, Vue, Angular, Next.js, and more
- 🔍 **Smart Filtering** - Built-in methods to query countries, states, and cities
- 💾 **Offline First** - No API calls required, all data bundled
- 🎯 **Tree-shakeable** - Import only what you need

**Quick Example:**
```javascript
import { Country, State, City } from '@countrystatecity/countries';

// Get all countries
const countries = Country.getAllCountries();

// Get states of a specific country
const usStates = State.getStatesOfCountry('US');

// Get cities of a specific state
const californiaCities = City.getCitiesOfState('US', 'CA');
```

📖 **[View Full Documentation on NPM](https://www.npmjs.com/package/@countrystatecity/countries)**

📂 **[Source Code on GitHub](https://github.com/dr5hn/countrystatecity)**

## API 🚀

🎉 Introducing **REST API** for Countries States Cities Database.

[API Documentation](https://docs.countrystatecity.in/)

[![banner](.github/images/api.png)](https://countrystatecity.in/)

## 🛠️ Export Tool

🎯 **Transform your data with our powerful export tool!**

Looking to export the Countries States Cities database in your preferred format? Our dedicated export tool makes it easy to convert and download data in multiple formats with just a few clicks.

**[Try the Export Tool](https://export.countrystatecity.in/)** - Export data in JSON, CSV, XML, YAML, and more!

[![banner](.github/images/export-tool.png)](https://export.countrystatecity.in/)

### Features:
- **Multiple Export Formats**: JSON, CSV, XML, YAML, and more
- **Flexible Data Selection**: Choose specific countries, states, or cities
- **Custom Filtering**: Filter by regions, subregions, or specific criteria
- **Bulk Downloads**: Export large datasets efficiently
- **Real-time Processing**: Get your data instantly
- **User-friendly Interface**: Simple and intuitive design

Perfect for developers, researchers, and businesses who need clean, structured geographical data for their applications.

## Available Formats

- JSON
- MYSQL
- PSQL
- SQLITE
- SQLSERVER
- MONGODB
- XML
- YAML
- CSV

**Note:** DuckDB format is available via manual conversion from SQLite files. See the [Export to DuckDB](#export-to-duckdb) section for instructions.

## Distribution Files Info

| File                       | JSON | MYSQL | PSQL | SQLITE | SQLSERVER | MONGODB | XML | YAML | CSV |
| :------------------------- | :--- | :---- | :--- | :----- | :-------- | :------ | :-- | :--- | :-- |
| Regions                    | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | ✅  | ✅   | ✅  |
| Subregions                 | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | ✅  | ✅   | ✅  |
| Countries                  | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | ✅  | ✅   | ✅  |
| States                     | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | ✅  | ✅   | ✅  |
| Cities                     | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | ✅  | ✅   | ✅  |
| **Sublocalities** 🆕       | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | ✅  | ✅   | ✅  |
| Country+States             | ✅   | NA    | NA   | NA     | NA        | NA      | NA  | NA   | NA  |
| Country+Cities             | ✅   | NA    | NA   | NA     | NA        | NA      | NA  | NA   | NA  |
| Country+State+Cities/World | ✅   | ✅    | ✅   | ✅     | ✅        | ✅      | NA  | NA   | NA  |

**New:** Sublocalities (neighborhoods, districts, areas within cities) are now available as a separate dataset with proper parent-city relationships. See [SUBLOCALITIES.md](docs/SUBLOCALITIES.md) for details.


## Demo

https://dr5hn.github.io/countries-states-cities-database/

## Insights

Total Regions : 6 <br>
Total Sub Regions : 22 <br>
Total Countries : 250 <br>
Total States/Regions/Municipalities : 5,038 <br>
Total Cities/Towns/Districts : 151,024 <br>
**Total Sublocalities/Neighborhoods : 0** 🆕 <br>

Last Updated On : 16th Oct 2025

> **Note:** The sublocalities feature is newly added to help properly categorize neighborhoods, districts, and areas within cities (such as Bandra in Mumbai, Manhattan in New York). See [docs/SUBLOCALITIES.md](docs/SUBLOCALITIES.md) for details on how to contribute sub-locality data.

## Import MongoDB

How to import MongoDB database?

```bash
# First extract the tar.gz file
tar -xzvf world-mongodb-dump.tar.gz

# Then restore the MongoDB dump
mongorestore --host localhost:27017 --db world mongodb-dump/world
```

## Export to DuckDB

Want to export the database to DuckDB format? You can easily convert the existing SQLite files to DuckDB format using our conversion script.

### Prerequisites

First, install DuckDB Python package:

```bash
pip install duckdb
```

### Convert SQLite to DuckDB

Use the provided conversion script to convert SQLite files to DuckDB format:

```bash
# Convert the complete world database
python3 bin/scripts/export/import_duckdb.py --input sqlite/world.sqlite3 --output duckdb/world.db

# Convert individual table databases
python3 bin/scripts/export/import_duckdb.py --input sqlite/regions.sqlite3 --output duckdb/regions.db
python3 bin/scripts/export/import_duckdb.py --input sqlite/subregions.sqlite3 --output duckdb/subregions.db
python3 bin/scripts/export/import_duckdb.py --input sqlite/countries.sqlite3 --output duckdb/countries.db
python3 bin/scripts/export/import_duckdb.py --input sqlite/states.sqlite3 --output duckdb/states.db
python3 bin/scripts/export/import_duckdb.py --input sqlite/cities.sqlite3 --output duckdb/cities.db
```

The conversion script will create DuckDB database files that maintain the same structure and data as the original SQLite files, optimized for analytical workloads.

## 📄 License

**Open Database License (ODbL)** - Free to use, share, and adapt!

This database is 100% free and open source with no restrictions on commercial use.

### What You Can Do:
* ✅ **Use commercially** - Build and sell products using this data
* ✅ **Modify freely** - Adapt and transform data for your needs
* ✅ **Share openly** - Distribute to others without limitations
* ✅ **Private use** - Use internally within your organization

### Simple Requirements:
📝 **Attribute** - Credit this project in your documentation
🔄 **Share-alike** - If you distribute a modified database, use the same license

### Quick Attribution:
```
Data provided by Countries States Cities Database
https://github.com/dr5hn/countries-states-cities-database
Licensed under ODbL v1.0
```

**Full License Details:**
- [Open Database License (ODbL)](https://github.com/dr5hn/countries-states-cities-database/blob/master/LICENSE) - Database structure and compilation
- [Database Contents License](https://github.com/dr5hn/countries-states-cities-database/blob/master/.github/CONTENT_LICENSE) - Individual data records

💡 **TL;DR:** Use it freely for any purpose, just give credit and keep derivatives open!

## Contributing

👍🎉 First off, thanks for your interest in contributing! 🎉👍

### Using Our Database Update Tool

We've launched a dedicated web tool to make contributing to this database easier than ever!

**[CSC Update Tool](https://manager.countrystatecity.in/)** - Our official tool to submit database change requests

[![banner](.github/images/update-tool.png)](https://manager.countrystatecity.in/)

The update tool allows you to:

- Browse and search through all regions, subregions, countries, states, and cities
- Easily identify and correct outdated or inaccurate data
- Submit change requests through a streamlined review process
- Track the status of your submissions

### Alternative Manual Process

If you prefer to contribute directly through GitHub, you can use our **simplified JSON contribution workflow**:

#### 🎯 JSON-based Contributions for External Contributors

1. **Fork** the repository and clone it to your local machine
2. **Make changes** to the data in the `contributions/` directory:
   - **Cities**: Edit country-specific files in `contributions/cities/` (e.g., `US.json`, `IN.json`)
   - **States**: Edit `contributions/states/states.json`
   - **Countries**: Edit `contributions/countries/countries.json`
3. **Add new records** without an `id` field - IDs will be auto-assigned by the database during import
4. **Create a pull request** with a clear description of your changes

**📖 See [contributions/README.md](contributions/README.md) for detailed examples and field reference**

#### What Happens After Your PR?

1. Your PR is reviewed by maintainers
2. GitHub Actions automatically imports your changes to MySQL (IDs are assigned)
3. All export formats (JSON, CSV, SQL, XML, YAML, etc.) are regenerated from MySQL
4. The PR is updated with all export files

#### Why JSON for Contributors?
- ✅ **Easy to edit** - Clear, readable format
- ✅ **Organized by country** - Find cities quickly
- ✅ **No local setup needed** - Just edit JSON and submit PR
- ✅ **Better for Git** - Clearer diffs and easier reviews
- ✅ **Non-technical friendly** - Anyone can contribute!

**Important Notes:**
- ✅ **Contributors**: Only edit JSON files in `contributions/` directory
- ❌ **Do NOT edit**: SQL, CSV, XML, YAML, or other export files - these are auto-generated
- ❌ **Do NOT run**: Build scripts or exports locally - GitHub Actions handles this
- 🔒 **MySQL workflow**: Reserved for repository maintainers only

---

Please ensure your contributions align with our data standards and formatting. You can find the detailed contribution guidelines [here](https://github.com/dr5hn/countries-states-cities-database/blob/master/.github/CONTRIBUTING.md).

We review all submissions carefully to maintain data quality and appreciate your help in making this database more accurate and comprehensive.

## Repo Activity

![Repo Activity](https://repobeats.axiom.co/api/embed/635051d1a8be17610a967b7b07b65c0148f13654.svg "Repobeats analytics image")

As always, thanks to our amazing contributors!

<a href="https://github.com/dr5hn/countries-states-cities-database/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=dr5hn/countries-states-cities-database&anon=1" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## Sponsors

<p align="center">
  <a href="https://cdn.jsdelivr.net/gh/dr5hn/static/sponsors.svg">
    <img src='https://cdn.jsdelivr.net/gh/dr5hn/static/sponsors.svg'/>
  </a>
</p>

## Make the world more Greener 🌴

Contribute towards better earth [**buy the world a tree**](https://ecologi.com/darshangada?r=60f2a36e67efcb18f734ffb8)

## 🌐 Available On Multiple Platforms

Find and use this dataset across the web - choose the platform that fits your workflow:

| Platform | Best For | Access |
|----------|----------|--------|
| 📊 **[Kaggle Dataset](https://www.kaggle.com/datasets/darshangada/countries-states-cities-database/data)** | Data science, ML projects, notebooks | [Download on Kaggle](https://www.kaggle.com/datasets/darshangada/countries-states-cities-database/data) |
| 🗃️ **[Data.world](https://data.world/dr5hn/country-state-city)** | Data collaboration, business analytics | [View on Data.world](https://data.world/dr5hn/country-state-city) |
| 📦 **[NPM Registry](https://www.npmjs.com/package/@countrystatecity/countries)** | JavaScript/TypeScript developers | `npm install @countrystatecity/countries` |
| 🐙 **[GitHub](https://github.com/dr5hn/countries-states-cities-database)** | Contributors, raw files, issue tracking | [View Repository](https://github.com/dr5hn/countries-states-cities-database) |
| 🌍 **[API Service](https://countrystatecity.in/)** | Production apps, real-time access | [Get API Key](https://countrystatecity.in/) |
| 🛠️ **[Export Tool](https://export.countrystatecity.in/)** | Custom exports, specific formats | [Launch Tool](https://export.countrystatecity.in/) |
| 📊 **[Status Page](https://status.countrystatecity.in/)** | Service uptime monitoring, incidents | [Check Status](https://status.countrystatecity.in/) |


## Follow me at

<a href="https://github.com/dr5hn/"><img alt="Github @dr5hn" src="https://img.shields.io/static/v1?logo=github&message=Github&color=black&style=flat-square&label=" /></a> <a href="https://twitter.com/dr5hn/"><img alt="Twitter @dr5hn" src="https://img.shields.io/static/v1?logo=twitter&message=Twitter&color=black&style=flat-square&label=" /></a> <a href="https://www.linkedin.com/in/dr5hn/"><img alt="LinkedIn @dr5hn" src="https://img.shields.io/static/v1?logo=linkedin&message=LinkedIn&color=black&style=flat-square&label=&link=https://twitter.com/dr5hn" /></a>

## 🙋‍♂️ Support My Work

[![Github Sponsorship](https://raw.githubusercontent.com/dr5hn/dr5hn/main/.github/resources/github_sponsor_btn.svg)](https://github.com/sponsors/dr5hn)

[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/dr5hn)

## Suggestions / Feedbacks

```
Suggestions & Feedbacks are Most Welcome
gadadarshan[at]gmail[dot]com
```

## Disclaimer

Please note that while every effort has been made to ensure the accuracy and completeness of the Countries States Cities Database, it may still contain errors or omissions. The database is continuously being refined and improved based on user feedback and contributions.

Contributors are encouraged to review the Contribution Guidelines and follow the specified guidelines for updating and correcting data in the database. However, due to the collaborative nature of the project, we cannot guarantee the absolute accuracy or reliability of the information provided.

The Countries States Cities Database is made available under the Open Database License, and any rights in individual contents of the database are licensed under the Database Contents License. Users are responsible for independently verifying the data and using it at their own discretion.

We appreciate the efforts of contributors in identifying and addressing issues in the database, and we encourage users to report any inaccuracies or suggest improvements through creating issues. However, please note that the database may not always reflect the latest geopolitical changes or political status.

It is recommended that users consult official sources and corroborate the data from the Countries States Cities Database with other reliable references for critical applications or decision-making processes.

By accessing and using the Countries States Cities Database, users acknowledge and agree to the aforementioned disclaimer and the terms of the Open Database License and the Database Contents License.

That's all Folks. Enjoy.
