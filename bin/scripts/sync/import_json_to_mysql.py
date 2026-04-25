#!/usr/bin/env python3
"""
JSON to MySQL Importer - Dynamic Schema Support

This script imports JSON files from the contributions/ directory to MySQL
with dynamic column detection. It auto-detects new columns in JSON and adds
them to MySQL schema.

Source Data:
    - Countries: contributions/countries/countries.json
    - States: contributions/states/states.json
    - Cities: contributions/cities/*.json (209+ country-specific files)

Usage:
    python3 bin/scripts/sync/import_json_to_mysql.py

For GitHub Actions (with environment variables):
    python3 bin/scripts/sync/import_json_to_mysql.py --host $DB_HOST --user $DB_USER --password $DB_PASSWORD

Requirements:
    pip install mysql-connector-python
"""

import json
import os
import sys
import argparse
from typing import List, Dict, Any, Set
import mysql.connector
from datetime import datetime


class JSONToMySQLImporter:
    """Import JSON to MySQL with dynamic schema detection and updates"""

    def __init__(self, host='localhost', user='root', password='', database='world'):
        """Initialize database connection"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                use_unicode=True,
                autocommit=False  # Use transactions
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print(f"✓ Connected to MySQL: {user}@{host}/{database}")
        except mysql.connector.Error as e:
            print(f"❌ MySQL connection failed: {e}")
            sys.exit(1)

    def get_table_columns(self, table_name: str) -> Dict[str, str]:
        """Get existing columns and their types from table"""
        self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = {}
        for row in self.cursor.fetchall():
            columns[row['Field']] = row['Type']
        return columns

    def infer_column_type(self, field_name: str, sample_values: List[Any]) -> str:
        """Infer MySQL column type from JSON field and sample values"""
        # Remove None values
        non_null_values = [v for v in sample_values if v is not None]

        if not non_null_values:
            return "VARCHAR(255) DEFAULT NULL"

        sample = non_null_values[0]

        # Special fields with known types
        if field_name == 'id':
            return "MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT"
        elif field_name.endswith('_id'):
            return "MEDIUMINT UNSIGNED NOT NULL"
        elif field_name.endswith('_code') and len(str(sample)) <= 3:
            return f"VARCHAR(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"
        elif field_name in ['latitude', 'longitude']:
            return "DECIMAL(10,8) DEFAULT NULL" if field_name == 'latitude' else "DECIMAL(11,8) DEFAULT NULL"
        elif field_name in ['timezones', 'translations']:
            return "TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        elif field_name in ['population', 'gdp']:
            return "BIGINT UNSIGNED DEFAULT NULL"
        elif field_name == 'level':
            return "INT DEFAULT NULL"
        elif field_name == 'parent_id':
            return "INT UNSIGNED DEFAULT NULL"

        # Infer from sample value type
        if isinstance(sample, bool):
            return "TINYINT(1) DEFAULT NULL"
        elif isinstance(sample, int):
            return "INT DEFAULT NULL"
        elif isinstance(sample, float):
            return "DECIMAL(15,8) DEFAULT NULL"
        elif isinstance(sample, dict) or isinstance(sample, list):
            return "TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        elif isinstance(sample, str):
            max_len = max(len(str(v)) for v in non_null_values)
            if max_len > 500:
                return "TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            elif max_len > 255:
                return "VARCHAR(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"
            else:
                return "VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"
        else:
            return "VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL"

    def detect_new_columns(self, table_name: str, json_data: List[Dict]) -> Dict[str, str]:
        """Detect new columns in JSON that don't exist in MySQL table"""
        existing_columns = set(self.get_table_columns(table_name).keys())
        json_fields = set()

        # Define table-specific redundant relationship fields that should never be added
        # These fields are redundant because we already have _id and _code fields
        redundant_fields = set()
        if table_name == 'cities':
            redundant_fields = {'country_name', 'state_name'}
        elif table_name == 'states':
            redundant_fields = {'country_name'}

        # Collect all fields from all records
        for record in json_data:
            json_fields.update(record.keys())

        # Find new columns (exclude redundant relationship fields)
        new_columns = json_fields - existing_columns - redundant_fields

        if not new_columns:
            return {}

        # Infer types for new columns
        new_column_types = {}
        for field in new_columns:
            # Collect sample values for this field
            samples = [record.get(field) for record in json_data if field in record][:100]
            column_type = self.infer_column_type(field, samples)
            new_column_types[field] = column_type

        return new_column_types

    def add_columns_to_table(self, table_name: str, new_columns: Dict[str, str]):
        """Add new columns to existing MySQL table"""
        if not new_columns:
            return

        print(f"  📊 Adding {len(new_columns)} new column(s) to '{table_name}':")

        for column_name, column_type in new_columns.items():
            try:
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN `{column_name}` {column_type}"
                self.cursor.execute(alter_sql)
                print(f"     ✓ Added column: {column_name} ({column_type})")
            except mysql.connector.Error as e:
                print(f"     ⚠ Failed to add column '{column_name}': {e}")

        self.conn.commit()

    def prepare_value(self, value: Any, field_name: str) -> Any:
        """Prepare JSON value for MySQL insertion"""
        if value is None:
            # Provide default timestamp for created_at and updated_at if missing (new records)
            # This ensures new contributions get proper timestamps even if contributor forgets them
            if field_name in ('created_at', 'updated_at'):
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return None

        # Convert dict/list to JSON string
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        # Convert boolean to int
        if isinstance(value, bool):
            return 1 if value else 0

        return value

    def import_table(self, table_name: str, json_file: str):
        """Import JSON file to MySQL table with schema auto-detection"""
        print(f"\n📦 Importing {json_file} → {table_name}")

        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data:
            print(f"  ⚠ No data found in {json_file}")
            return 0

        # Separate records with IDs from those without
        records_with_id = [r for r in data if r.get('id') is not None]
        records_without_id = [r for r in data if r.get('id') is None]

        if records_without_id:
            print(f"  ℹ️  Found {len(records_without_id)} records without IDs (will be auto-assigned)")

        # Detect and add new columns
        new_columns = self.detect_new_columns(table_name, data)
        if new_columns:
            self.add_columns_to_table(table_name, new_columns)

        # Get current column list
        all_columns = list(self.get_table_columns(table_name).keys())

        # Define fields to skip during import
        # These are auto-managed by MySQL or redundant relationship fields
        skip_fields = {'flag'}  # flag is auto-managed by MySQL; preserve created_at and updated_at from JSON
        if table_name == 'cities':
            skip_fields.update({'country_name', 'state_name'})
        elif table_name == 'states':
            skip_fields.add('country_name')

        # Build final insert column list:
        # Include all columns from database except skip_fields
        insert_columns = [c for c in all_columns if c not in skip_fields]

        # Clear existing data (for full replacement)
        print(f"  🗑️  Truncating existing data...")
        self.cursor.execute(f"SET FOREIGN_KEY_CHECKS=0")
        self.cursor.execute(f"TRUNCATE TABLE {table_name}")
        self.cursor.execute(f"SET FOREIGN_KEY_CHECKS=1")

        # Insert records with explicit IDs first
        inserted = 0
        if records_with_id:
            print(f"  📝 Inserting {len(records_with_id)} records with explicit IDs...")
            print(f"     Columns: {', '.join(insert_columns)}")
            inserted += self._batch_insert_records(table_name, records_with_id, insert_columns)

        # Insert records without IDs (auto-increment will assign them)
        if records_without_id:
            # Exclude 'id' column for records without IDs
            insert_columns_no_id = [c for c in insert_columns if c != 'id']
            print(f"  📝 Inserting {len(records_without_id)} records without IDs (auto-increment)...")
            print(f"     Columns: {', '.join(insert_columns_no_id)}")
            inserted += self._batch_insert_records(table_name, records_without_id, insert_columns_no_id)

        print(f"  ✓ Imported {inserted:,} records to '{table_name}'")
        return inserted

    def _batch_insert_records(self, table_name: str, records: List[Dict], insert_columns: List[str]) -> int:
        """Helper method to batch insert records with specific columns"""
        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(insert_columns))
        column_names = ', '.join([f'`{c}`' for c in insert_columns])
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        # Batch insert
        batch_size = 1000
        inserted = 0

        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            values = []

            for record in batch:
                row = []
                for col in insert_columns:
                    value = record.get(col)
                    row.append(self.prepare_value(value, col))
                values.append(tuple(row))

            try:
                self.cursor.executemany(insert_sql, values)
                self.conn.commit()
                inserted += len(values)
                print(f"     ✓ Inserted {inserted:,} / {len(records):,} records...", end='\r')
            except mysql.connector.Error as e:
                print(f"\n     ❌ Insert failed at record {inserted}: {e}")
                self.conn.rollback()
                raise

        print()  # New line after progress indicator
        return inserted

    def import_countries(self):
        """Import countries from JSON"""
        json_file = os.path.join('contributions', 'countries', 'countries.json')
        return self.import_table('countries', json_file)

    def import_states(self):
        """Import states from JSON"""
        json_file = os.path.join('contributions', 'states', 'states.json')
        return self.import_table('states', json_file)

    def import_cities(self):
        """Import cities from individual country JSON files"""
        print(f"\n📦 Importing cities from contributions/cities/*.json")

        cities_dir = os.path.join('contributions', 'cities')
        if not os.path.exists(cities_dir):
            print(f"  ❌ Directory not found: {cities_dir}")
            return 0

        # Collect all city JSON files
        city_files = sorted([f for f in os.listdir(cities_dir) if f.endswith('.json')])

        if not city_files:
            print(f"  ⚠ No city JSON files found in {cities_dir}")
            return 0

        print(f"  📂 Found {len(city_files)} country files to process")

        # Load and merge all city data
        all_cities = []
        for city_file in city_files:
            file_path = os.path.join(cities_dir, city_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cities = json.load(f)
                    if isinstance(cities, list):
                        all_cities.extend(cities)
                        print(f"  ✓ Loaded {len(cities):,} cities from {city_file}")
                    else:
                        print(f"  ⚠ Skipping {city_file}: Not a valid array")
            except Exception as e:
                print(f"  ❌ Error loading {city_file}: {e}")

        if not all_cities:
            print(f"  ⚠ No cities loaded from any files")
            return 0

        print(f"\n  📊 Total cities to import: {len(all_cities):,}")

        # Detect and add new columns
        new_columns = self.detect_new_columns('cities', all_cities)
        if new_columns:
            self.add_columns_to_table('cities', new_columns)

        # Get current column list
        all_columns = list(self.get_table_columns('cities').keys())

        # Define fields to skip during import
        # These are auto-managed by MySQL or redundant relationship fields
        skip_fields = {'flag', 'country_name', 'state_name'}  # flag is auto-managed by MySQL; preserve created_at and updated_at from JSON

        # Build final insert column list:
        # Include all columns from database except skip_fields
        insert_columns = [c for c in all_columns if c not in skip_fields]

        # Clear existing data (for full replacement)
        print(f"  🗑️  Truncating existing data...")
        self.cursor.execute(f"SET FOREIGN_KEY_CHECKS=0")
        self.cursor.execute(f"TRUNCATE TABLE cities")
        self.cursor.execute(f"SET FOREIGN_KEY_CHECKS=1")

        # Split records: those with explicit IDs first, then those without
        records_with_id = [r for r in all_cities if r.get('id') is not None]
        records_without_id = [r for r in all_cities if r.get('id') is None]

        inserted = 0

        # Insert records with explicit IDs first
        if records_with_id:
            print(f"  📝 Inserting {len(records_with_id):,} records with explicit IDs...")
            print(f"     Columns: {', '.join(insert_columns)}")
            inserted += self._batch_insert_records('cities', records_with_id, insert_columns)

        # Insert records without IDs (AUTO_INCREMENT assigns them)
        if records_without_id:
            insert_columns_no_id = [c for c in insert_columns if c != 'id']
            print(f"  📝 Inserting {len(records_without_id):,} records without IDs (auto-increment)...")
            print(f"     Columns: {', '.join(insert_columns_no_id)}")
            inserted += self._batch_insert_records('cities', records_without_id, insert_columns_no_id)

        print(f"  ✓ Imported {inserted:,} cities from {len(city_files)} country files")
        return inserted

    def import_postcodes(self):
        """Import postcodes from individual country JSON files (issue #1039)."""
        print(f"\n📦 Importing postcodes from contributions/postcodes/*.json")

        postcodes_dir = os.path.join('contributions', 'postcodes')
        if not os.path.exists(postcodes_dir):
            print(f"  ⚠ Directory not found: {postcodes_dir} (skipping)")
            return 0

        # Skip table if migration hasn't been run yet
        try:
            self.cursor.execute("SHOW TABLES LIKE 'postcodes'")
            if not self.cursor.fetchone():
                print(f"  ⚠ Table 'postcodes' does not exist yet — run migrations first (skipping)")
                return 0
        except mysql.connector.Error as e:
            print(f"  ⚠ Could not verify postcodes table existence: {e} (skipping)")
            return 0

        postcode_files = sorted(
            f for f in os.listdir(postcodes_dir)
            if f.endswith('.json') and f != 'README.md'
        )

        if not postcode_files:
            print(f"  ⚠ No postcode JSON files found in {postcodes_dir}")
            return 0

        print(f"  📂 Found {len(postcode_files)} country files to process")

        all_postcodes = []
        for pf in postcode_files:
            file_path = os.path.join(postcodes_dir, pf)
            try:
                with open(file_path, 'r', encoding='utf-8') as fh:
                    rows = json.load(fh)
                    if isinstance(rows, list):
                        all_postcodes.extend(rows)
                        print(f"  ✓ Loaded {len(rows):,} postcodes from {pf}")
                    else:
                        print(f"  ⚠ Skipping {pf}: Not a valid array")
            except Exception as e:
                print(f"  ❌ Error loading {pf}: {e}")

        if not all_postcodes:
            print(f"  ⚠ No postcodes loaded from any files")
            return 0

        print(f"\n  📊 Total postcodes to import: {len(all_postcodes):,}")

        new_columns = self.detect_new_columns('postcodes', all_postcodes)
        if new_columns:
            self.add_columns_to_table('postcodes', new_columns)

        all_columns = list(self.get_table_columns('postcodes').keys())
        skip_fields = {'flag'}
        insert_columns = [c for c in all_columns if c not in skip_fields]

        print(f"  🗑️  Truncating existing data...")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        self.cursor.execute("TRUNCATE TABLE postcodes")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        records_with_id = [r for r in all_postcodes if r.get('id') is not None]
        records_without_id = [r for r in all_postcodes if r.get('id') is None]

        inserted = 0
        if records_with_id:
            print(f"  📝 Inserting {len(records_with_id):,} records with explicit IDs...")
            inserted += self._batch_insert_records('postcodes', records_with_id, insert_columns)

        if records_without_id:
            insert_columns_no_id = [c for c in insert_columns if c != 'id']
            print(f"  📝 Inserting {len(records_without_id):,} records without IDs (auto-increment)...")
            inserted += self._batch_insert_records('postcodes', records_without_id, insert_columns_no_id)

        print(f"  ✓ Imported {inserted:,} postcodes from {len(postcode_files)} country files")
        return inserted

    def import_regions(self):
        """Import regions from JSON"""
        json_file = os.path.join('contributions', 'regions', 'regions.json')
        if os.path.exists(json_file):
            return self.import_table('regions', json_file)
        else:
            print(f"  ⚠ {json_file} not found, skipping")
            return 0

    def import_subregions(self):
        """Import subregions from JSON"""
        json_file = os.path.join('contributions', 'subregions', 'subregions.json')
        if os.path.exists(json_file):
            return self.import_table('subregions', json_file)
        else:
            print(f"  ⚠ {json_file} not found, skipping")
            return 0

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Import JSON to MySQL with dynamic schema support')
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')
    args = parser.parse_args()

    print("📥 JSON → MySQL Import (Dynamic Schema)\n")
    print("=" * 60)

    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Script is in bin/scripts/sync/, so go up 3 levels to reach project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(project_root)

    # Initialize importer
    importer = JSONToMySQLImporter(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        # Import in order (respecting foreign keys)
        regions_count = importer.import_regions()
        subregions_count = importer.import_subregions()
        countries_count = importer.import_countries()
        states_count = importer.import_states()
        cities_count = importer.import_cities()
        postcodes_count = importer.import_postcodes()

        print("\n" + "=" * 60)
        print("✅ Import complete!")
        print(f"   📍 Regions: {regions_count}")
        print(f"   📍 Subregions: {subregions_count}")
        print(f"   📍 Countries: {countries_count}")
        print(f"   📍 States: {states_count}")
        print(f"   📍 Cities: {cities_count:,}")
        print(f"   📍 Postcodes: {postcodes_count:,}")

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
