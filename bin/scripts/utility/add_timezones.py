#!/usr/bin/env python3
"""
Add Timezone Data to Cities and States using Latitude/Longitude

This script populates the timezone field for cities and/or states in the MySQL database
using their latitude and longitude coordinates. It uses the timezonefinder
library to determine IANA timezone identifiers from geographic coordinates.

Usage:
    python3 bin/scripts/utility/add_timezones.py

For custom database credentials:
    python3 bin/scripts/utility/add_timezones.py --host localhost --user root --password root --database world

Options:
    --table TABLE       Process 'cities', 'states', or 'both' (default: both)
    --batch-size N      Process N records at a time (default: 1000)
    --limit N           Process only N records total (for testing)
    --dry-run           Don't save changes to database

Requirements:
    pip install mysql-connector-python timezonefinder
"""

import argparse
import sys
from typing import Optional, Tuple
import mysql.connector
from timezonefinder import TimezoneFinder


class TimezoneUpdater:
    """Add timezone data to cities and states using lat/lng coordinates"""

    def __init__(self, host='localhost', user='root', password='root', database='world'):
        """Initialize database connection and timezone finder"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                use_unicode=True,
                autocommit=False
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print(f"✓ Connected to MySQL: {user}@{host}/{database}")
        except mysql.connector.Error as e:
            print(f"❌ MySQL connection failed: {e}")
            sys.exit(1)

        # Initialize timezone finder
        print("📍 Loading timezone data...")
        self.tf = TimezoneFinder()
        print("✓ Timezone finder ready")

    def get_records_without_timezone(self, table: str, limit: Optional[int] = None) -> list:
        """Get all records from the specified table that don't have timezone data"""
        if table not in ['cities', 'states']:
            raise ValueError(f"Invalid table: {table}. Must be 'cities' or 'states'")

        # Different field names for different tables
        if table == 'cities':
            fields = "id, name, latitude, longitude, country_code, state_code"
        else:  # states
            fields = "id, name, latitude, longitude, country_code, NULL as state_code"

        query = f"""
            SELECT {fields}
            FROM {table}
            WHERE timezone IS NULL AND latitude IS NOT NULL AND longitude IS NOT NULL
        """
        if limit:
            query += f" LIMIT {limit}"

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_cities_without_timezone(self, limit: Optional[int] = None) -> list:
        """Backward compatibility wrapper - Get all cities that don't have timezone data"""
        return self.get_records_without_timezone('cities', limit)

    def get_timezone_from_coords(self, latitude: float, longitude: float) -> Optional[str]:
        """Get IANA timezone identifier from latitude/longitude"""
        try:
            # Convert to float if they're Decimal
            lat = float(latitude)
            lng = float(longitude)

            # Get timezone
            tz = self.tf.timezone_at(lat=lat, lng=lng)

            # Filter out generic Etc/GMT timezones (not location-specific IANA timezones)
            # These are used for oceanic/remote locations and should not be assigned to cities
            # They're fixed offset zones without daylight saving or real-world location context
            if tz and tz.startswith('Etc/GMT'):
                return None

            return tz
        except Exception as e:
            print(f"  ⚠️  Error getting timezone for ({latitude}, {longitude}): {e}")
            return None

    def update_record_timezone(self, table: str, record_id: int, timezone: str) -> bool:
        """Update timezone for a single record in the specified table"""
        if table not in ['cities', 'states']:
            raise ValueError(f"Invalid table: {table}. Must be 'cities' or 'states'")

        try:
            query = f"UPDATE {table} SET timezone = %s WHERE id = %s"
            self.cursor.execute(query, (timezone, record_id))
            return True
        except mysql.connector.Error as e:
            print(f"  ❌ Error updating {table[:-1]} {record_id}: {e}")
            return False

    def update_city_timezone(self, city_id: int, timezone: str) -> bool:
        """Backward compatibility wrapper - Update timezone for a single city"""
        return self.update_record_timezone('cities', city_id, timezone)

    def process_table(self, table: str, batch_size: int = 1000, limit: Optional[int] = None, dry_run: bool = False):
        """Process all records in the specified table and add timezone data"""
        if table not in ['cities', 'states']:
            raise ValueError(f"Invalid table: {table}. Must be 'cities' or 'states'")

        record_type = table[:-1]  # 'cities' -> 'city', 'states' -> 'state'

        print(f"\n🔍 Finding {table} without timezone data...")

        records = self.get_records_without_timezone(table, limit=limit)
        total_records = len(records)

        if total_records == 0:
            print(f"✓ All {table} already have timezone data!")
            return

        print(f"📊 Found {total_records:,} {table} without timezone data")

        if dry_run:
            print("🚫 DRY RUN MODE - No changes will be saved\n")

        processed = 0
        updated = 0
        skipped = 0
        batch_updates = []

        for i, record in enumerate(records, 1):
            record_id = record['id']
            name = record['name']
            lat = record['latitude']
            lng = record['longitude']
            country = record['country_code']
            state = record.get('state_code', '')

            # Get timezone
            tz = self.get_timezone_from_coords(lat, lng)

            if tz:
                batch_updates.append((tz, record_id))
                updated += 1

                # Progress indicator
                if i % 100 == 0 or i == 1:
                    location_info = f"{name}, {state}, {country}" if state else f"{name}, {country}"
                    print(f"  [{i:,}/{total_records:,}] {location_info} → {tz}")
            else:
                skipped += 1
                if skipped <= 10:  # Only show first 10 failures
                    location_info = f"{name}, {state}, {country}" if state else f"{name}, {country}"
                    print(f"  ⚠️  [{i:,}/{total_records:,}] {location_info} - No timezone found")

            # Batch update
            if len(batch_updates) >= batch_size or i == total_records:
                if not dry_run and batch_updates:
                    try:
                        query = f"UPDATE {table} SET timezone = %s WHERE id = %s"
                        self.cursor.executemany(query, batch_updates)
                        self.conn.commit()
                        print(f"  ✓ Committed batch of {len(batch_updates)} updates")
                    except mysql.connector.Error as e:
                        print(f"  ❌ Batch update failed: {e}")
                        self.conn.rollback()
                        return

                batch_updates = []
                processed += len(batch_updates) if not dry_run else 0

        # Summary
        print(f"\n{'=' * 60}")
        print(f"📊 Summary for {table}:")
        print(f"  Total {table} processed: {total_records:,}")
        print(f"  Successfully updated: {updated:,}")
        print(f"  Skipped (no timezone): {skipped:,}")
        if dry_run:
            print(f"  ⚠️  Changes not saved (dry run mode)")
        else:
            print(f"  ✅ Changes saved to database")
        print(f"{'=' * 60}\n")

    def process_cities(self, batch_size: int = 1000, limit: Optional[int] = None, dry_run: bool = False):
        """Backward compatibility wrapper - Process all cities and add timezone data"""
        return self.process_table('cities', batch_size=batch_size, limit=limit, dry_run=dry_run)

    def close(self):
        """Close database connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Add timezone data to cities and/or states using lat/lng coordinates"
    )
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='root', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')
    parser.add_argument('--table', default='both', choices=['cities', 'states', 'both'],
                        help='Process cities, states, or both (default: cities)')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Number of records to process in each batch')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of records to process (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Do not save changes to database')

    args = parser.parse_args()

    updater = TimezoneUpdater(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        if args.table == 'both':
            # Process cities first
            print("=" * 60)
            print("Processing CITIES")
            print("=" * 60)
            updater.process_table(
                'cities',
                batch_size=args.batch_size,
                limit=args.limit,
                dry_run=args.dry_run
            )

            # Then process states
            print("\n" + "=" * 60)
            print("Processing STATES")
            print("=" * 60)
            updater.process_table(
                'states',
                batch_size=args.batch_size,
                limit=args.limit,
                dry_run=args.dry_run
            )
        else:
            updater.process_table(
                args.table,
                batch_size=args.batch_size,
                limit=args.limit,
                dry_run=args.dry_run
            )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        updater.close()


if __name__ == '__main__':
    main()
