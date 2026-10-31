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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from city_states import check_counties, check_references  # noqa: E402
import mysql.connector
from datetime import datetime

# Link columns as declared in bin/db/schema.sql, used when an older database lacks one. They are resolved before any
# sample: data cannot relax a required link or tighten an optional one. ('*', field) applies to every table.
LINK_TYPES = {
    ('*', 'country_id'): "MEDIUMINT UNSIGNED NOT NULL",
    ('countries', 'region_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
    ('countries', 'subregion_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
    ('subregions', 'region_id'): "MEDIUMINT UNSIGNED NOT NULL",
    ('states', 'parent_id'): "INT UNSIGNED DEFAULT NULL",
    ('counties', 'state_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",   # null for a county of several regions (v5)
    ('counties', 'parent_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
    ('cities', 'state_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
    ('cities', 'county_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
    ('cities', 'parent_id'): "INT UNSIGNED DEFAULT NULL",
    ('postcodes', 'state_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
    ('postcodes', 'city_id'): "MEDIUMINT UNSIGNED DEFAULT NULL",
}


def retired_id_floor(migrations_dir=os.path.join('migrations')):
    """Highest id per table that the id ledger retired or reserved, so auto-assigned ids never reuse one.

    Reads removal events and every removal_batch row (shared old_table, row old_id) from events.jsonl,
    and {table, id} rows from reserved_ids.jsonl when they
    exist. A malformed line stops the import: guessing past it could hand a retired id to a new record."""
    floor = {}
    for name, tkey, ikey in (('events.jsonl', 'old_table', 'old_id'), ('reserved_ids.jsonl', 'table', 'id')):
        path = os.path.join(migrations_dir, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    sys.exit(f"❌ {path}:{n} is not JSON ({e}); fix the ledger line before importing")
                if not isinstance(row, dict):
                    sys.exit(f"❌ {path}:{n} is not a JSON object; fix the ledger line before importing")
                if name == 'events.jsonl':
                    kind = row.get('event_type', 'removal')
                    if kind in ('identity', 'restoration'):
                        continue   # they retire nothing
                    if kind not in ('removal', 'removal_batch'):
                        sys.exit(f"❌ {path}:{n} has unknown event_type {kind!r}; fix the ledger line before importing")
                rows = row.get('rows') if name == 'events.jsonl' and row.get('event_type') == 'removal_batch' else [row]
                if not isinstance(rows, list) or not rows:
                    sys.exit(f"❌ {path}:{n} row 0: batch rows must be a nonempty list")
                for i, item in enumerate(rows, 1):
                    table = row.get(tkey)
                    rid = item.get(ikey) if isinstance(item, dict) else None
                    if not isinstance(table, str) or type(rid) is not int or rid <= 0:
                        sys.exit(f"❌ {path}:{n} row {i} needs {tkey} and a positive integer {ikey}; fix the ledger line before importing")
                    floor[table] = max(floor.get(table, 0), rid)
    return floor


MIGRATION_20261015 = ("counties need migration 20261015000000 (county_states, nullable county state); run migration "
                      "20261015000000 before importing a county of several regions")


def load_rows(path):
    """The array of records in one contributions file; an unreadable file or another shape is refused by name."""
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            rows = json.load(fh)
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Cannot load {path}: {e}") from e
    if not isinstance(rows, list):
        raise ValueError(f"Cannot load {path}: expected an array of records")
    return rows


def reference_rows():
    """Countries, states and every city from contributions/, for the reference checks."""
    cities_dir = os.path.join('contributions', 'cities')
    return (load_rows(os.path.join('contributions', 'countries', 'countries.json')),
            load_rows(os.path.join('contributions', 'states', 'states.json')),
            [c for f in sorted(os.listdir(cities_dir)) if f.endswith('.json') for c in load_rows(os.path.join(cities_dir, f))])


class JSONToMySQLImporter:
    """Import JSON to MySQL with dynamic schema detection and updates"""

    id_floor: Dict[str, int] = {}   # per table, from the id ledger; __init__ reads it (tests may build without it)

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
            self.id_floor = retired_id_floor()
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

    def infer_column_type(self, field_name: str, sample_values: List[Any], table_name: str = '') -> str:
        """Infer MySQL column type from JSON field and sample values; declared link columns win over samples"""
        declared = LINK_TYPES.get((table_name, field_name)) or LINK_TYPES.get(('*', field_name))
        if declared:
            return declared
        if field_name == 'parent_id':
            return "INT UNSIGNED DEFAULT NULL"   # optional by definition: a top-level record has no parent

        # Remove None values
        non_null_values = [v for v in sample_values if v is not None]

        # Another link column is nullable when some record has no value for it (every record is sampled, an omitted
        # key counting as no value)
        if field_name.endswith('_id') and len(non_null_values) < len(sample_values):
            return "MEDIUMINT UNSIGNED DEFAULT NULL"

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
        elif table_name == 'counties':
            redundant_fields = {'country_name', 'state_name', 'states'}   # states: rows of county_states, not a column
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
            # Links are checked on every record (a record without the key has no link); other types on a sample
            if field.endswith('_id'):
                samples = [record.get(field) for record in json_data]
            else:
                samples = [record.get(field) for record in json_data if field in record][:100]
            column_type = self.infer_column_type(field, samples, table_name)
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
        if table_name in ('cities', 'counties'):
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
        if 'id' not in insert_columns and self.id_floor.get(table_name):
            # Auto-assigned ids start above every id the ledger retired or reserved; InnoDB also stays above max(id)
            self.cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = {self.id_floor[table_name] + 1}")
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

    def reset_tables(self):
        """Clear dependent tables first for a full import, including optional datasets."""
        self.cursor.execute("SHOW TABLES")
        existing = {next(iter(row.values())) for row in self.cursor.fetchall()}
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        try:
            for table in ('postcodes', 'cities', 'county_states', 'counties', 'states', 'countries', 'subregions', 'regions'):
                if table in existing:
                    self.cursor.execute(f"TRUNCATE TABLE {table}")
        finally:
            self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")

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

    def preflight_city_states(self):
        """Check every city's state pair against canonical countries and states before any table is reset."""
        countries, states, cities = reference_rows()
        errors = check_references(countries, states, cities)
        if errors:
            raise ValueError(f"{len(errors)} reference problems (countries, states or city state pairs): " + '; '.join(errors[:20]))
        # a stateless city needs the v5 migration: nullable state columns and the pair check
        if any(c.get('state_id') is None for c in cities):
            self.cursor.execute("SHOW COLUMNS FROM cities WHERE Field IN ('state_id', 'state_code')")
            strict = [r['Field'] for r in self.cursor.fetchall() if r['Null'] != 'YES']
            if strict:
                raise ValueError(f"cities.{', '.join(strict)} cannot be null yet; run migration 20261014000000 before importing a city with no state")
        print(f"  ✓ Countries, states and city state pairs checked ({len(cities):,} cities)")

    def preflight_counties(self):
        """Load every county file before any database reset or county truncation."""
        print(f"\n📦 Importing counties from contributions/counties/*.json")

        counties_dir = os.path.join('contributions', 'counties')
        try:
            os.stat(counties_dir)
        except FileNotFoundError:
            print(f"  ⚠ Directory not found: {counties_dir} (skipping)")
            return []

        # Only a genuinely absent table is optional; database errors are fatal. An older database may skip counties
        # only while no county needs the v5 schema: a county of several regions refuses before any reset.
        self.cursor.execute("SHOW TABLES LIKE 'counties'")
        if not self.cursor.fetchone():
            if self.counties_need_regions(counties_dir):
                raise ValueError(MIGRATION_20261015)
            print("  ⚠ Table 'counties' does not exist yet — run migrations first (skipping)")
            return []

        county_files = sorted(
            f for f in os.listdir(counties_dir)
            if f.endswith('.json') and f != 'README.md'
        )

        if not county_files:
            print(f"  ⚠ No county JSON files found in {counties_dir}")
            return []

        print(f"  📂 Found {len(county_files)} country files to process")

        all_counties = []
        for pf in county_files:
            file_path = os.path.join(counties_dir, pf)
            try:
                with open(file_path, 'r', encoding='utf-8') as fh:
                    rows = json.load(fh)
            except (OSError, UnicodeError, json.JSONDecodeError) as e:
                raise ValueError(f"Cannot load county file {file_path}: {e}") from e
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError(f"Cannot load county file {file_path}: expected an array of records")
            all_counties.extend(rows)
            print(f"  ✓ Loaded {len(rows):,} counties from {pf}")

        if any(r.get('parent_id') is not None and r.get('id') is None for r in all_counties):
            raise ValueError('Counties with parent_id must have an explicit id')
        countries, states, cities = reference_rows()
        errors = check_counties(countries, states, all_counties, cities)
        if errors:
            raise ValueError(f"{len(errors)} county reference problems (county states or city county links): " + '; '.join(errors[:20]))
        # a county of several regions needs the v5 migration: nullable county state and the county_states table
        if any(r.get('state_id') is None for r in all_counties):
            self.cursor.execute("SHOW TABLES LIKE 'county_states'")
            migrated = self.cursor.fetchone() is not None
            self.cursor.execute("SHOW COLUMNS FROM counties WHERE Field IN ('state_id', 'state_code')")
            nullable = {r['Field']: r['Null'] for r in self.cursor.fetchall()}
            if not migrated or nullable != {'state_id': 'YES', 'state_code': 'YES'}:   # both columns, both nullable
                raise ValueError(MIGRATION_20261015)
        return all_counties

    @staticmethod
    def counties_need_regions(counties_dir):
        """Whether any readable county file holds a county of several regions (null state or a states list). Used only
        when the counties table is absent; an unreadable file is skipped there, as the whole dataset is."""
        for name in sorted(f for f in os.listdir(counties_dir) if f.endswith('.json')):
            try:
                rows = load_rows(os.path.join(counties_dir, name))
            except ValueError:
                continue
            if any(isinstance(r, dict) and (r.get('state_id') is None or r.get('states') is not None) for r in rows):
                return True
        return False

    def import_counties(self, all_counties=None):
        """Import preflighted counties, or preflight first when called directly."""
        if all_counties is None:
            all_counties = self.preflight_counties()
        if not all_counties:
            return 0
        print(f"\n  📊 Total counties to import: {len(all_counties):,}")

        new_columns = self.detect_new_columns('counties', all_counties)
        if new_columns:
            self.add_columns_to_table('counties', new_columns)

        all_columns = list(self.get_table_columns('counties').keys())
        skip_fields = {'flag', 'country_name', 'state_name', 'states'}
        insert_columns = [c for c in all_columns if c not in skip_fields]

        parents = [(r['parent_id'], r['id']) for r in all_counties if r.get('parent_id') is not None and r.get('id') is not None]
        insert_columns = [c for c in insert_columns if c != 'parent_id']

        print(f"  🗑️  Truncating existing data...")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        self.cursor.execute("TRUNCATE TABLE counties")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")

        records_with_id = [r for r in all_counties if r.get('id') is not None]
        records_without_id = [r for r in all_counties if r.get('id') is None]

        inserted = 0
        if records_with_id:
            print(f"  📝 Inserting {len(records_with_id):,} records with explicit IDs...")
            inserted += self._batch_insert_records('counties', records_with_id, insert_columns)

        if records_without_id:
            insert_columns_no_id = [c for c in insert_columns if c != 'id']
            print(f"  📝 Inserting {len(records_without_id):,} records without IDs (auto-increment)...")
            inserted += self._batch_insert_records('counties', records_without_id, insert_columns_no_id)

        if parents:
            self.cursor.executemany("UPDATE counties SET parent_id = %s WHERE id = %s", parents)
            self.conn.commit()

        # A county of several regions: one county_states row per listed region (checked in the preflight)
        relation = sorted((r['id'], e['state_id']) for r in all_counties if r.get('states') for e in r['states'])
        self.cursor.execute("SHOW TABLES LIKE 'county_states'")
        if self.cursor.fetchone() is not None:
            self.cursor.execute("DELETE FROM county_states")
            if relation:
                self.cursor.executemany("INSERT INTO county_states (county_id, state_id) VALUES (%s, %s)", relation)
            self.conn.commit()
            print(f"  ✓ Linked {len({c for c, _ in relation}):,} counties to {len(relation):,} regions")

        print(f"  ✓ Imported {inserted:,} counties")
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
        county_data = importer.preflight_counties()
        importer.preflight_city_states()   # before any reset: a bad state pair leaves the database untouched
        importer.reset_tables()
        # Import in order (respecting foreign keys)
        regions_count = importer.import_regions()
        subregions_count = importer.import_subregions()
        countries_count = importer.import_countries()
        states_count = importer.import_states()
        counties_count = importer.import_counties(county_data)
        cities_count = importer.import_cities()
        postcodes_count = importer.import_postcodes()

        print("\n" + "=" * 60)
        print("✅ Import complete!")
        print(f"   📍 Regions: {regions_count}")
        print(f"   📍 Subregions: {subregions_count}")
        print(f"   📍 Countries: {countries_count}")
        print(f"   📍 States: {states_count}")
        print(f"   📍 Counties: {counties_count:,}")
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
