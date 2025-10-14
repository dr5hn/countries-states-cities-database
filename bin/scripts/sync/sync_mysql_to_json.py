#!/usr/bin/env python3
"""
MySQL to JSON Sync Script - Bidirectional Bridge for Local Development

This script syncs data from MySQL database back to contribution JSON files.
It exports ALL columns from MySQL with no exclusions, creating an exact mirror
of the database state in the contributions/ directory.

Features:
    - Exports database schema to bin/db/schema.sql
    - Syncs all tables to contributions/ directory
    - Dynamic column detection (exports all columns from MySQL)
    - Preserves data types (timestamps, JSON, decimals, etc.)

Usage:
    python3 bin/scripts/sync/sync_mysql_to_json.py

Requirements:
    pip install mysql-connector-python
"""

import json
import os
import sys
import argparse
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

    def export_schema(self):
        """Export MySQL schema to bin/db/schema.sql using mysqldump"""
        import subprocess
        print("\n📋 Exporting database schema...")

        schema_file = os.path.join('bin', 'db', 'schema.sql')

        # Ensure directory exists
        os.makedirs(os.path.dirname(schema_file), exist_ok=True)

        # Get connection info
        host = self.conn.server_host
        user = self.conn.user
        database = self.conn.database

        # Tables to export (in correct order respecting foreign keys)
        tables = ['regions', 'subregions', 'countries', 'states', 'cities']

        # Build mysqldump command
        # --no-data: only schema, no data
        # --skip-add-drop-table: we'll add our own DROP statements
        # --single-transaction: consistent snapshot
        cmd = [
            'mysqldump',
            f'--host={host}',
            f'--user={user}',
            '--no-data',
            '--single-transaction',
            '--skip-add-drop-table',
            database
        ]

        # Add specific tables to export
        cmd.extend(tables)

        # Add password if set
        password = self.conn._password
        if password:
            cmd.append(f'--password={password}')

        try:
            # Run mysqldump
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            schema_content = result.stdout

            # Add custom header and DROP statements
            header = [
                "-- " + "=" * 77,
                "-- Database Schema Initialization for World Database",
                "-- " + "=" * 77,
                "-- This file creates all tables with proper structure and relationships.",
                "-- It should be run BEFORE importing data from JSON files.",
                "--",
                "-- Usage:",
                "--   mysql -uroot -p world < bin/db/schema.sql",
                "--",
                "-- Auto-generated by: bin/scripts/sync/sync_mysql_to_json.py (using mysqldump)",
                "-- " + "=" * 77,
                "",
                "SET FOREIGN_KEY_CHECKS=0;",
                "",
                "-- Drop existing tables in reverse dependency order"
            ]

            # Add DROP statements
            for table in reversed(tables):
                header.append(f"DROP TABLE IF EXISTS `{table}`;")

            header.append("")

            # Combine header with schema
            final_content = '\n'.join(header) + '\n' + schema_content

            # Add footer
            final_content += "\nSET FOREIGN_KEY_CHECKS=1;\n"

            # Write to file
            with open(schema_file, 'w', encoding='utf-8') as f:
                f.write(final_content)

            print(f"  ✓ Schema exported to {schema_file}")
            print(f"  📊 {len(tables)} tables: {', '.join(tables)}")

            return schema_file

        except subprocess.CalledProcessError as e:
            print(f"  ❌ mysqldump failed: {e}")
            print(f"  stderr: {e.stderr}")
            raise
        except FileNotFoundError:
            print("  ❌ mysqldump command not found. Please install MySQL client tools.")
            raise

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Sync MySQL database to JSON contribution files"
    )
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')

    args = parser.parse_args()

    print("🔄 MySQL → JSON Sync (Dynamic Schema Detection)\n")
    print("=" * 60)

    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 3 levels: sync/ -> scripts/ -> bin/ -> project_root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(project_root)

    # Initialize sync
    syncer = MySQLToJSONSync(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        # Export schema first
        schema_file = syncer.export_schema()

        # Sync all tables (in order respecting foreign keys)
        regions_count = syncer.sync_regions()
        subregions_count = syncer.sync_subregions()
        countries_count = syncer.sync_countries()
        states_count = syncer.sync_states()
        cities_count = syncer.sync_cities()

        print("\n" + "=" * 60)
        print("✅ Sync complete!")
        print(f"   📋 Schema: {schema_file}")
        print(f"   📍 Regions: {regions_count}")
        print(f"   📍 Subregions: {subregions_count}")
        print(f"   📍 Countries: {countries_count}")
        print(f"   📍 States: {states_count}")
        print(f"   📍 Cities: {cities_count:,}")
        print("\n💡 Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Commit: git add . && git commit -m 'sync: update from MySQL'")

    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        syncer.close()


if __name__ == '__main__':
    main()
