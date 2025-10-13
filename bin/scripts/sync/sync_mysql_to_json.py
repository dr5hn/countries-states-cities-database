#!/usr/bin/env python3
"""
MySQL to JSON Sync Script - Bidirectional Bridge for Local Development

This script syncs data from MySQL database back to contribution JSON files.
It exports ALL columns from MySQL with no exclusions, creating an exact mirror
of the database state in the contributions/ directory.

Usage:
    python3 bin/scripts/sync/sync_mysql_to_json.py

Requirements:
    pip install mysql-connector-python
"""

import json
import os
import sys
from typing import List, Dict, Any, Set
import mysql.connector
from collections import OrderedDict


class MySQLToJSONSync:
    """Sync MySQL database to JSON contribution files with dynamic schema detection"""

    def __init__(self, host='localhost', user='root', password='root', database='world'):
        """Initialize database connection"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                use_unicode=True
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print(f"✓ Connected to MySQL database '{database}'")
        except mysql.connector.Error as e:
            print(f"❌ MySQL connection failed: {e}")
            sys.exit(1)

    def get_table_columns(self, table_name: str) -> List[str]:
        """Dynamically detect all columns in a table"""
        self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [row['Field'] for row in self.cursor.fetchall()]
        print(f"  📋 Detected {len(columns)} columns in '{table_name}': {', '.join(columns)}")
        return columns

    def get_excluded_columns(self) -> Set[str]:
        """Columns to exclude from JSON export (internal database fields)"""
        # Export all columns from MySQL to contributions JSON files for exact mirroring
        return set()

    def process_row(self, row: Dict[str, Any], columns: List[str], excluded: Set[str]) -> OrderedDict:
        """Process a database row into JSON-friendly format"""
        from datetime import datetime, date

        result = OrderedDict()

        for col in columns:
            if col in excluded:
                continue

            value = row.get(col)

            # Handle NULL values
            if value is None:
                result[col] = None
                continue

            # Handle datetime fields
            # Convert to ISO 8601 format: "2019-10-05T23:18:06" (without microseconds)
            if isinstance(value, (datetime, date)):
                if isinstance(value, datetime):
                    # Remove microseconds and format as ISO 8601
                    result[col] = value.replace(microsecond=0).isoformat()
                else:
                    result[col] = value.isoformat()
            # Handle JSON text fields (timezones, translations)
            elif col in ['timezones', 'translations'] and isinstance(value, str):
                try:
                    result[col] = json.loads(value)
                except json.JSONDecodeError:
                    result[col] = value
            # Convert Decimal to string for coordinates
            elif col in ['latitude', 'longitude']:
                result[col] = str(value) if value is not None else None
            # Convert integer fields
            elif col == 'id' or col.endswith('_id') or col in ['level', 'population', 'gdp']:
                result[col] = int(value) if value is not None else None
            else:
                result[col] = value

        return result

    def sync_countries(self):
        """Sync countries table to contributions/countries/countries.json"""
        print("\n📦 Syncing countries...")

        columns = self.get_table_columns('countries')
        excluded = self.get_excluded_columns()

        self.cursor.execute("SELECT * FROM countries ORDER BY id")
        rows = self.cursor.fetchall()

        countries = []
        for row in rows:
            countries.append(self.process_row(row, columns, excluded))

        output_file = os.path.join('contributions', 'countries', 'countries.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(countries, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Synced {len(countries)} countries to {output_file}")
        return len(countries)

    def sync_states(self):
        """Sync states table to contributions/states/states.json"""
        print("\n📦 Syncing states...")

        columns = self.get_table_columns('states')
        excluded = self.get_excluded_columns()

        self.cursor.execute("SELECT * FROM states ORDER BY id")
        rows = self.cursor.fetchall()

        states = []
        for row in rows:
            states.append(self.process_row(row, columns, excluded))

        output_file = os.path.join('contributions', 'states', 'states.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(states, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Synced {len(states)} states to {output_file}")
        return len(states)

    def sync_cities(self):
        """Sync cities table to contributions/cities/<COUNTRY_CODE>.json files"""
        print("\n📦 Syncing cities...")

        columns = self.get_table_columns('cities')
        excluded = self.get_excluded_columns()

        # Get all unique country codes
        self.cursor.execute("SELECT DISTINCT country_code FROM cities ORDER BY country_code")
        country_codes = [row['country_code'] for row in self.cursor.fetchall()]

        total_cities = 0
        cities_dir = os.path.join('contributions', 'cities')

        # Ensure cities directory exists
        os.makedirs(cities_dir, exist_ok=True)

        for country_code in country_codes:
            # Fetch all cities for this country
            query = f"SELECT * FROM cities WHERE country_code = %s ORDER BY id"
            self.cursor.execute(query, (country_code,))
            rows = self.cursor.fetchall()

            cities = []
            for row in rows:
                cities.append(self.process_row(row, columns, excluded))

            # Save to country-specific JSON file
            output_file = os.path.join(cities_dir, f'{country_code}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)

            print(f"  ✓ {country_code}: {len(cities):,} cities → {output_file}")
            total_cities += len(cities)

        print(f"\n  ✓ Total: {total_cities:,} cities synced to {len(country_codes)} files")
        return total_cities

    def sync_regions(self):
        """Sync regions table (if you need it in contributions)"""
        print("\n📦 Syncing regions...")

        columns = self.get_table_columns('regions')
        excluded = self.get_excluded_columns()

        self.cursor.execute("SELECT * FROM regions ORDER BY id")
        rows = self.cursor.fetchall()

        regions = []
        for row in rows:
            regions.append(self.process_row(row, columns, excluded))

        # Create regions directory if it doesn't exist
        regions_dir = os.path.join('contributions', 'regions')
        os.makedirs(regions_dir, exist_ok=True)

        output_file = os.path.join(regions_dir, 'regions.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(regions, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Synced {len(regions)} regions to {output_file}")
        return len(regions)

    def sync_subregions(self):
        """Sync subregions table (if you need it in contributions)"""
        print("\n📦 Syncing subregions...")

        columns = self.get_table_columns('subregions')
        excluded = self.get_excluded_columns()

        self.cursor.execute("SELECT * FROM subregions ORDER BY id")
        rows = self.cursor.fetchall()

        subregions = []
        for row in rows:
            subregions.append(self.process_row(row, columns, excluded))

        # Create subregions directory if it doesn't exist
        subregions_dir = os.path.join('contributions', 'subregions')
        os.makedirs(subregions_dir, exist_ok=True)

        output_file = os.path.join(subregions_dir, 'subregions.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(subregions, f, ensure_ascii=False, indent=2)

        print(f"  ✓ Synced {len(subregions)} subregions to {output_file}")
        return len(subregions)

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main execution"""
    print("🔄 MySQL → JSON Sync (Dynamic Schema Detection)\n")
    print("=" * 60)

    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 3 levels: sync/ -> scripts/ -> bin/ -> project_root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(project_root)

    # Initialize sync
    syncer = MySQLToJSONSync(
        host='localhost',
        user='root',
        password='',
        database='world'
    )

    try:
        # Sync all tables
        countries_count = syncer.sync_countries()
        states_count = syncer.sync_states()
        cities_count = syncer.sync_cities()

        # Optional: Sync regions and subregions if needed
        # regions_count = syncer.sync_regions()
        # subregions_count = syncer.sync_subregions()

        print("\n" + "=" * 60)
        print("✅ Sync complete!")
        print(f"   📍 Countries: {countries_count}")
        print(f"   📍 States: {states_count}")
        print(f"   📍 Cities: {cities_count:,}")
        print("\n💡 Next steps:")
        print("   1. Review changes: git diff")
        print("   3. Commit: git add . && git commit -m 'sync: update from MySQL'")

    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        syncer.close()


if __name__ == '__main__':
    main()
