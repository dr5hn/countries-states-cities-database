#!/usr/bin/env python3
"""
JSON Normalizer - Auto-fill missing IDs and timestamps

This script helps contributors (including GitHub Copilot) normalize JSON files
by auto-assigning IDs and timestamps for new records.

Usage:
    # Normalize a single city file
    python3 bin/scripts/sync/normalize_json.py contributions/cities/US.json

    # Normalize states file
    python3 bin/scripts/sync/normalize_json.py contributions/states/states.json

    # Normalize all city files
    python3 bin/scripts/sync/normalize_json.py contributions/cities/*.json

What it does:
    1. Reads existing records from MySQL to get next available ID
    2. For records without 'id': assigns next sequential ID
    3. For records without 'created_at': adds current timestamp
    4. For records without 'updated_at': adds current timestamp
    5. Updates JSON file in place

Requirements:
    pip install mysql-connector-python
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import mysql.connector


class JSONNormalizer:
    """Normalize JSON files by auto-filling missing fields"""

    def __init__(self, host='localhost', user='root', password='root', database='world'):
        """Initialize database connection to fetch current IDs"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                use_unicode=True
            )
            self.cursor = self.cursor = self.conn.cursor(dictionary=True)
            print(f"✓ Connected to MySQL: {user}@{host}/{database}")
        except mysql.connector.Error as e:
            print(f"⚠ MySQL connection failed: {e}")
            print("  Will assign IDs starting from 1 (no database verification)")
            self.conn = None
            self.cursor = None

    def get_next_id(self, table_name: str) -> int:
        """Get next available ID from MySQL table"""
        if not self.cursor:
            return 1

        try:
            self.cursor.execute(f"SELECT MAX(id) as max_id FROM {table_name}")
            result = self.cursor.fetchone()
            max_id = result['max_id'] if result and result['max_id'] else 0
            return max_id + 1
        except mysql.connector.Error as e:
            print(f"⚠ Could not fetch max ID from {table_name}: {e}")
            return 1

    def normalize_records(self, records: List[Dict], table_name: str) -> tuple[List[Dict], int]:
        """
        Normalize records by auto-filling missing fields

        Returns:
            (normalized_records, count_of_changes)
        """
        next_id = self.get_next_id(table_name)
        changes = 0
        current_time = datetime.now().isoformat(timespec='seconds')  # ISO 8601 format

        for record in records:
            changed = False

            # Auto-assign ID if missing
            if 'id' not in record or record['id'] is None:
                record['id'] = next_id
                next_id += 1
                changed = True

            # Auto-assign created_at if missing
            if 'created_at' not in record or record['created_at'] is None:
                record['created_at'] = current_time
                changed = True

            # Auto-assign updated_at if missing
            if 'updated_at' not in record or record['updated_at'] is None:
                record['updated_at'] = current_time
                changed = True

            if changed:
                changes += 1

        return records, changes

    def detect_table_from_path(self, file_path: str) -> Optional[str]:
        """Detect table name from file path"""
        file_path = file_path.lower()

        if 'cities' in file_path:
            return 'cities'
        elif 'states' in file_path:
            return 'states'
        elif 'countries' in file_path:
            return 'countries'
        elif 'regions' in file_path:
            return 'regions'
        elif 'subregions' in file_path:
            return 'subregions'

        return None

    def normalize_file(self, file_path: str) -> bool:
        """
        Normalize a single JSON file

        Returns:
            True if file was modified, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False

        # Detect table type
        table_name = self.detect_table_from_path(file_path)
        if not table_name:
            print(f"⚠ Could not detect table type from path: {file_path}")
            print("  Expected path containing: cities, states, countries, regions, or subregions")
            return False

        print(f"\n📝 Normalizing {file_path} ({table_name} table)")

        # Load JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Failed to read JSON: {e}")
            return False

        if not isinstance(data, list):
            print(f"❌ Expected JSON array, got {type(data).__name__}")
            return False

        if not data:
            print(f"  ℹ️  File is empty (no records)")
            return False

        # Normalize records
        normalized_data, changes = self.normalize_records(data, table_name)

        if changes == 0:
            print(f"  ✓ All {len(data)} records already have IDs and timestamps")
            return False

        # Write back to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(normalized_data, f, ensure_ascii=False, indent=2)
            print(f"  ✓ Updated {changes} / {len(data)} records")
            print(f"  ✓ File saved: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to write JSON: {e}")
            return False

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Normalize JSON files by auto-assigning IDs and timestamps',
        epilog='Example: python3 bin/scripts/sync/normalize_json.py contributions/cities/US.json'
    )
    parser.add_argument('files', nargs='+', help='JSON file(s) to normalize')
    parser.add_argument('--host', default='localhost', help='MySQL host (default: localhost)')
    parser.add_argument('--user', default='root', help='MySQL user (default: root)')
    parser.add_argument('--password', default='root', help='MySQL password (default: root)')
    parser.add_argument('--database', default='world', help='MySQL database (default: world)')
    args = parser.parse_args()

    print("🔧 JSON Normalizer - Auto-fill IDs and Timestamps\n")
    print("=" * 60)

    # Initialize normalizer
    normalizer = JSONNormalizer(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        modified_count = 0
        for file_path in args.files:
            if normalizer.normalize_file(file_path):
                modified_count += 1

        print("\n" + "=" * 60)
        if modified_count > 0:
            print(f"✅ Normalized {modified_count} / {len(args.files)} file(s)")
            print("\n💡 Next steps:")
            print("   1. Review the changes: git diff")
            print("   2. Test import: python3 bin/scripts/sync/import_json_to_mysql.py")
            print("   3. Commit changes: git add . && git commit -m 'feat: add new records'")
        else:
            print(f"✓ All {len(args.files)} file(s) already normalized")

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        normalizer.close()


if __name__ == '__main__':
    main()
