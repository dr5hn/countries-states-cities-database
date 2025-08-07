# DuckDB Database

This directory contains the Countries States Cities database in DuckDB format.

## About DuckDB

[DuckDB](https://duckdb.org/) is an in-process analytical database management system that is designed to be fast, reliable, and easy to use. It provides excellent compression and query performance for analytical workloads.

## Files

- `world.db` - The complete database with all tables (regions, subregions, countries, states, cities)

## Benefits of DuckDB Format

- **Compact Size**: ~51% smaller than SQLite format (9.3 MB vs 19.0 MB)
- **Fast Analytics**: Optimized for analytical queries and aggregations
- **Easy Integration**: Can be used with Python, R, Java, and other languages
- **SQL Compatible**: Standard SQL interface
- **Global ID Support**: Optional WikiData-like global sequence IDs with proper foreign key mapping

## Generation

The DuckDB database is generated from the SQLite database using the enhanced import script:

```bash
python3 bin/import_duckdb.py
```

### Script Options

- `--global-ids`: Use global sequence IDs (WikiData-like) with proper foreign key mapping
- `--enhanced`: Use enhanced conversion with pandas for better performance (requires pandas and inflect)
- `--output`: Specify output database path (default: ./duckdb/world.db)
- `--input`: Specify input SQLite database path (default: ./sqlite/world.sqlite3)

### Example Usage

```bash
# Generate standard DuckDB database
python3 bin/import_duckdb.py

# Generate with global sequence IDs (WikiData-like approach)
python3 bin/import_duckdb.py --global-ids --output duckdb/world_global_ids.db

# Use enhanced conversion with pandas for better performance
python3 bin/import_duckdb.py --enhanced --output duckdb/world_enhanced.db

# Combine all features: enhanced mode with global IDs
python3 bin/import_duckdb.py --enhanced --global-ids --output duckdb/world_full.db

# Custom paths
python3 bin/import_duckdb.py --input custom.sqlite3 --output custom.db
```

## Database Schema

The database contains the same schema as the SQLite version with the following tables:

- **regions** (6 records) - Continental regions
- **subregions** (22 records) - Sub-continental regions  
- **countries** (250 records) - Countries with detailed information
- **states** (5,134 records) - States/provinces/regions within countries
- **cities** (151,901 records) - Cities with coordinates and references

## Using the Database

### Python Example

```python
import duckdb

# Connect to the database
conn = duckdb.connect('duckdb/world.db')

# Query examples
regions = conn.execute("SELECT * FROM regions").fetchall()
countries_in_asia = conn.execute("SELECT name FROM countries WHERE region = 'Asia'").fetchall()
cities_in_us = conn.execute("SELECT name FROM cities WHERE country_code = 'US' LIMIT 10").fetchall()

conn.close()
```



### CLI Example

```bash
# Install DuckDB CLI
# Query the database
duckdb duckdb/world.db -c "SELECT COUNT(*) as total_cities FROM cities"
duckdb duckdb/world.db -c "SELECT region, COUNT(*) as country_count FROM countries GROUP BY region"
```

## Technical Notes

- **Timestamp Handling**: The script handles timestamp conversion issues between SQLite and DuckDB by using current timestamps to avoid conversion errors
- **Global ID Mapping**: When using `--global-ids`, the script maintains proper foreign key relationships by mapping all IDs to a global sequence (similar to WikiData approach)
- **Enhanced Mode**: Using `--enhanced` flag with pandas provides better performance and more robust data handling
- **Table Optimization**: Tables are sorted by primary key for better query performance (more efficient than indexes for DuckDB)
- **Data Integrity**: All foreign key relationships are preserved from the original SQLite database

## Script Improvements

This script incorporates improvements inspired by the community script shared in [GitHub issue #948](https://github.com/adsharma/truth-serum/blob/main/truth/import_cities.py), including:

- Better timestamp handling to avoid SQLite→DuckDB conversion errors
- Proper global sequence ID mapping with foreign key updates
- Enhanced conversion mode using pandas for better performance
- Improved error handling and robustness

## Data Source

This DuckDB database is generated from the SQLite database which is part of the Countries States Cities Database project. The data is regularly updated and maintained.

Last Updated: August 2025