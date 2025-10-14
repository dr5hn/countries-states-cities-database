#!/usr/bin/env python3
"""
Add Timezone Data to Cities using Latitude/Longitude

This script populates the timezone field for cities in the MySQL database
using their latitude and longitude coordinates. It uses the timezonefinder
library to determine IANA timezone identifiers from geographic coordinates.

Usage:
    python3 bin/scripts/sync/add_city_timezones.py

For custom database credentials:
    python3 bin/scripts/sync/add_city_timezones.py --host localhost --user root --password root --database world

Options:
    --batch-size N      Process N cities at a time (default: 1000)
    --limit N           Process only N cities total (for testing)
    --dry-run           Don't save changes to database

Requirements:
    pip install mysql-connector-python timezonefinder
"""

import argparse
import sys
from typing import Optional, Tuple
import mysql.connector
from timezonefinder import TimezoneFinder


class CityTimezoneUpdater:
    """Add timezone data to cities using lat/lng coordinates"""

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

    def get_cities_without_timezone(self, limit: Optional[int] = None) -> list:
        """Get all cities that don't have timezone data"""
        query = """
            SELECT id, name, latitude, longitude, country_code, state_code
            FROM cities
            WHERE timezone IS NULL AND latitude IS NOT NULL AND longitude IS NOT NULL
        """
        if limit:
            query += f" LIMIT {limit}"

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_timezone_from_coords(self, latitude: float, longitude: float) -> Optional[str]:
        """Get IANA timezone identifier from latitude/longitude"""
        try:
            # Convert to float if they're Decimal
            lat = float(latitude)
            lng = float(longitude)

            # Get timezone
            tz = self.tf.timezone_at(lat=lat, lng=lng)
            return tz
        except Exception as e:
            print(f"  ⚠️  Error getting timezone for ({latitude}, {longitude}): {e}")
            return None

    def update_city_timezone(self, city_id: int, timezone: str) -> bool:
        """Update timezone for a single city"""
        try:
            query = "UPDATE cities SET timezone = %s WHERE id = %s"
            self.cursor.execute(query, (timezone, city_id))
            return True
        except mysql.connector.Error as e:
            print(f"  ❌ Error updating city {city_id}: {e}")
            return False

    def process_cities(self, batch_size: int = 1000, limit: Optional[int] = None, dry_run: bool = False):
        """Process all cities and add timezone data"""
        print("\n🔍 Finding cities without timezone data...")

        cities = self.get_cities_without_timezone(limit=limit)
        total_cities = len(cities)

        if total_cities == 0:
            print("✓ All cities already have timezone data!")
            return

        print(f"📊 Found {total_cities:,} cities without timezone data")

        if dry_run:
            print("🚫 DRY RUN MODE - No changes will be saved\n")

        processed = 0
        updated = 0
        skipped = 0
        batch_updates = []

        for i, city in enumerate(cities, 1):
            city_id = city['id']
            name = city['name']
            lat = city['latitude']
            lng = city['longitude']
            country = city['country_code']
            state = city['state_code']

            # Get timezone
            tz = self.get_timezone_from_coords(lat, lng)

            if tz:
                batch_updates.append((tz, city_id))
                updated += 1

                # Progress indicator
                if i % 100 == 0 or i == 1:
                    print(f"  [{i:,}/{total_cities:,}] {name}, {state}, {country} → {tz}")
            else:
                skipped += 1
                if skipped <= 10:  # Only show first 10 failures
                    print(f"  ⚠️  [{i:,}/{total_cities:,}] {name}, {state}, {country} - No timezone found")

            # Batch update
            if len(batch_updates) >= batch_size or i == total_cities:
                if not dry_run and batch_updates:
                    try:
                        query = "UPDATE cities SET timezone = %s WHERE id = %s"
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
        print(f"📊 Summary:")
        print(f"  Total cities processed: {total_cities:,}")
        print(f"  Successfully updated: {updated:,}")
        print(f"  Skipped (no timezone): {skipped:,}")
        if dry_run:
            print(f"  ⚠️  Changes not saved (dry run mode)")
        else:
            print(f"  ✅ Changes saved to database")
        print(f"{'=' * 60}\n")

    def close(self):
        """Close database connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Add timezone data to cities using lat/lng coordinates"
    )
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='root', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Number of cities to process in each batch')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of cities to process (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Do not save changes to database')

    args = parser.parse_args()

    updater = CityTimezoneUpdater(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )

    try:
        updater.process_cities(
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
