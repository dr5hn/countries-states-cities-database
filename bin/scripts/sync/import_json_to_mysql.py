#!/usr/bin/env python3
"""
JSON to MySQL Importer - Dynamic Schema Support

This script imports JSON files to MySQL with dynamic column detection.
It auto-detects new columns in JSON and adds them to MySQL schema.

Usage:
    python3 bin/import_json_to_mysql.py

For GitHub Actions (with environment variables):
    python3 bin/import_json_to_mysql.py --host $DB_HOST --user $DB_USER --password $DB_PASSWORD

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

    def __init__(self, host='localhost', user='root', password='root', database='world'):
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

        # Collect all fields from all records
        for record in json_data:
            json_fields.update(record.keys())

        # Find new columns
        new_columns = json_fields - existing_columns

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

        # Detect and add new columns
        new_columns = self.detect_new_columns(table_name, data)
        if new_columns:
            self.add_columns_to_table(table_name, new_columns)

        # Get current column list
        columns = list(self.get_table_columns(table_name).keys())

        # Remove auto-managed columns
        insert_columns = [c for c in columns if c not in ['created_at', 'updated_at', 'flag']]

        # Clear existing data (for full replacement)
        print(f"  🗑️  Truncating existing data...")
        self.cursor.execute(f"SET FOREIGN_KEY_CHECKS=0")
        self.cursor.execute(f"TRUNCATE TABLE {table_name}")
        self.cursor.execute(f"SET FOREIGN_KEY_CHECKS=1")

        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(insert_columns))
        column_names = ', '.join([f'`{c}`' for c in insert_columns])
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        # Batch insert
        batch_size = 1000
        inserted = 0

        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
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
                print(f"  ✓ Inserted {inserted:,} / {len(data):,} records...", end='\r')
            except mysql.connector.Error as e:
                print(f"\n  ❌ Insert failed at record {inserted}: {e}")
                self.conn.rollback()
                raise

        print(f"\n  ✓ Imported {inserted:,} records to '{table_name}'")
        return inserted

    def import_countries(self):
        """Import countries from JSON"""
        json_file = os.path.join('json', 'countries.json')
        return self.import_table('countries', json_file)

    def import_states(self):
        """Import states from JSON"""
        json_file = os.path.join('json', 'states.json')
        return self.import_table('states', json_file)

    def import_cities(self):
        """Import cities from JSON"""
        json_file = os.path.join('json', 'cities.json')
        return self.import_table('cities', json_file)

    def import_regions(self):
        """Import regions from JSON"""
        json_file = os.path.join('json', 'regions.json')
        if os.path.exists(json_file):
            return self.import_table('regions', json_file)
        else:
            print(f"  ⚠ {json_file} not found, skipping")
            return 0

    def import_subregions(self):
        """Import subregions from JSON"""
        json_file = os.path.join('json', 'subregions.json')
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
    parser.add_argument('--password', default='root', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')
    args = parser.parse_args()

    print("📥 JSON → MySQL Import (Dynamic Schema)\n")
    print("=" * 60)

    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
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

        print("\n" + "=" * 60)
        print("✅ Import complete!")
        print(f"   📍 Regions: {regions_count}")
        print(f"   📍 Subregions: {subregions_count}")
        print(f"   📍 Countries: {countries_count}")
        print(f"   📍 States: {states_count}")
        print(f"   📍 Cities: {cities_count:,}")

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
