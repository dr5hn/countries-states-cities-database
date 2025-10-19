#!/usr/bin/env python3
"""
Timezone Management Tool - Add, Fix, and Validate Timezones

This script manages timezone data for cities and states in the MySQL database.
It uses country-aware logic to assign correct IANA timezone identifiers.

Features:
    - Add timezones to new records (NULL timezone)
    - Fix incorrect timezones (Etc/GMT, wrong country)
    - Validate timezone data quality
    - Respect country boundaries and political timezone choices

Usage:
    # Add timezones to records without them
    python3 bin/scripts/validation/add_timezones.py

    # Fix ALL timezones (including incorrect ones)
    python3 bin/scripts/validation/add_timezones.py --fix-all

    # Validate timezone data
    python3 bin/scripts/validation/add_timezones.py --validate

    # Custom database credentials (for GitHub Actions)
    python3 bin/scripts/validation/add_timezones.py --host localhost --user root --password root --database world

Options:
    --table TABLE       Process 'cities', 'states', or 'both' (default: both)
    --batch-size N      Process N records at a time (default: 1000)
    --limit N           Process only N records total (for testing)
    --dry-run           Don't save changes to database
    --fix-all           Re-process ALL records, not just NULL/Etc timezones
    --validate          Run timezone validation checks only

Requirements:
    pip install mysql-connector-python timezonefinder
"""

import argparse
import sys
import json
from typing import Optional, Tuple, Dict, List
import mysql.connector
from timezonefinder import TimezoneFinder


class TimezoneUpdater:
    """Add timezone data to cities and states using lat/lng coordinates"""

    def __init__(self, host='localhost', user='root', password='', database='world'):
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

        # Load country timezone mappings for country-aware timezone selection
        print("🌍 Loading country timezone definitions...")
        self.country_timezones = self.load_country_timezones()
        print(f"✓ Loaded timezones for {len(self.country_timezones)} countries")

    def load_country_timezones(self) -> Dict[str, List[str]]:
        """Load timezone definitions for each country from the database"""
        country_tz_map = {}

        query = "SELECT iso2, timezones FROM countries"
        self.cursor.execute(query)
        countries = self.cursor.fetchall()

        for country in countries:
            country_code = country['iso2']
            timezones_json = country['timezones']

            if timezones_json:
                try:
                    timezones = json.loads(timezones_json) if isinstance(timezones_json, str) else timezones_json
                    tz_names = [tz['zoneName'] for tz in timezones if 'zoneName' in tz]
                    country_tz_map[country_code] = tz_names
                except (json.JSONDecodeError, TypeError) as e:
                    country_tz_map[country_code] = []
            else:
                country_tz_map[country_code] = []

        return country_tz_map

    def get_records_without_timezone(self, table: str, limit: Optional[int] = None, fix_all: bool = False) -> list:
        """
        Get records from the specified table that need timezone updates

        Args:
            table: 'cities' or 'states'
            limit: Maximum number of records to return
            fix_all: If True, get ALL records (not just NULL/Etc timezones)

        Returns:
            List of records needing timezone updates
        """
        if table not in ['cities', 'states']:
            raise ValueError(f"Invalid table: {table}. Must be 'cities' or 'states'")

        # Different field names for different tables
        if table == 'cities':
            fields = "id, name, latitude, longitude, country_code, state_code, timezone"
        else:  # states
            fields = "id, name, latitude, longitude, country_code, NULL as state_code, timezone"

        if fix_all:
            # Get ALL records with coordinates (for fixing incorrect timezones)
            query = f"""
                SELECT {fields}
                FROM {table}
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            """
        else:
            # Only get records without timezone or with Etc/GMT timezones
            query = f"""
                SELECT {fields}
                FROM {table}
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                AND (timezone IS NULL OR timezone LIKE 'Etc/%')
            """

        if limit:
            query += f" LIMIT {limit}"

        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_cities_without_timezone(self, limit: Optional[int] = None) -> list:
        """Backward compatibility wrapper - Get all cities that don't have timezone data"""
        return self.get_records_without_timezone('cities', limit)

    def get_timezone_from_coords(self, latitude: float, longitude: float, country_code: str = None) -> Optional[str]:
        """
        Get IANA timezone identifier from latitude/longitude with country-aware logic

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            country_code: ISO2 country code (optional but recommended for accuracy)

        Returns:
            Best matching timezone or None
        """
        try:
            # Convert to float if they're Decimal
            lat = float(latitude)
            lng = float(longitude)

            # Get timezone from coordinates
            tz = self.tf.timezone_at(lat=lat, lng=lng)

            # If no country code provided, use basic logic
            if not country_code:
                # Filter out generic Etc/GMT timezones
                if tz and tz.startswith('Etc/GMT'):
                    return None
                return tz

            # Country-aware logic
            if not tz or tz.startswith('Etc/GMT'):
                # timezonefinder returned invalid timezone, use country's primary timezone
                country_tzs = self.country_timezones.get(country_code, [])
                if country_tzs:
                    return self._get_primary_timezone(country_tzs, country_code)
                return None

            # Check if the timezone belongs to this country
            country_tzs = self.country_timezones.get(country_code, [])

            if tz in country_tzs:
                # Perfect match - timezone is in the country's list
                return tz

            # Timezone doesn't match country - find best alternative
            if country_tzs:
                # For multi-timezone countries, use geographic matching
                if len(country_tzs) > 1:
                    return self._match_timezone_by_geography(lat, lng, country_tzs, country_code)
                else:
                    # Single timezone country
                    return country_tzs[0]

            # No country timezones defined, return what timezonefinder gave us
            # but filter out Etc/GMT
            if tz.startswith('Etc/GMT'):
                return None
            return tz

        except Exception as e:
            print(f"  ⚠️  Error getting timezone for ({latitude}, {longitude}): {e}")
            return None

    def _get_primary_timezone(self, timezones: List[str], country_code: str) -> str:
        """Get the primary (most common) timezone for a country"""
        # Special cases for known multi-timezone countries
        primary_tz_map = {
            'ES': 'Europe/Madrid',
            'PT': 'Europe/Lisbon',
            'US': 'America/New_York',
            'CA': 'America/Toronto',
            'RU': 'Europe/Moscow',
            'BR': 'America/Sao_Paulo',
            'AU': 'Australia/Sydney',
            'MX': 'America/Mexico_City',
            'FR': 'Europe/Paris',
            'GB': 'Europe/London',
        }

        if country_code in primary_tz_map and primary_tz_map[country_code] in timezones:
            return primary_tz_map[country_code]

        return timezones[0] if timezones else None

    def _match_timezone_by_geography(self, lat: float, lng: float,
                                     country_tzs: List[str], country_code: str) -> str:
        """
        Match timezone by geographic location for multi-timezone countries

        Strategy:
        1. Use timezonefinder to get timezone from coordinates
        2. If that timezone is in the country's official list, use it (works for most countries)
        3. Apply special geographic rules for edge cases (Spain, Portugal, etc.)
        4. Fall back to primary timezone
        """

        # First, try timezonefinder and check if result is in country's timezone list
        # This handles USA, Canada, Russia, Australia, Brazil, etc. automatically!
        tz_from_coords = self.tf.timezone_at(lat=lat, lng=lng)
        if tz_from_coords and tz_from_coords in country_tzs:
            return tz_from_coords

        # If timezonefinder didn't give us a valid country timezone,
        # apply special geographic rules for known edge cases

        # Spain: Special handling for territories that might get wrong timezone from timezonefinder
        if country_code == 'ES':
            # Canary Islands: longitude < -13
            if lng < -13:
                return 'Atlantic/Canary'
            # Ceuta/Melilla: North Africa enclaves (very specific coordinates)
            # Ceuta: ~35.89°N, -5.32°W; Melilla: ~35.29°N, -2.94°W
            elif 35.2 < lat < 36.0 and -5.5 < lng < -2.8:
                return 'Africa/Ceuta'
            else:
                return 'Europe/Madrid'

        # Portugal: Special handling for island territories
        if country_code == 'PT':
            # Azores: longitude < -25
            if lng < -25:
                return 'Atlantic/Azores'
            # Madeira: latitude 32-33, longitude -17 to -16
            elif 32 < lat < 33.5 and -17.5 < lng < -16:
                return 'Atlantic/Madeira'
            else:
                return 'Europe/Lisbon'

        # For all other countries, return primary timezone as fallback
        # This shouldn't happen often since timezonefinder is pretty accurate
        return self._get_primary_timezone(country_tzs, country_code)

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

    def process_table(self, table: str, batch_size: int = 1000, limit: Optional[int] = None, dry_run: bool = False, fix_all: bool = False):
        """Process all records in the specified table and add/fix timezone data"""
        if table not in ['cities', 'states']:
            raise ValueError(f"Invalid table: {table}. Must be 'cities' or 'states'")

        record_type = table[:-1]  # 'cities' -> 'city', 'states' -> 'state'

        if fix_all:
            print(f"\n🔧 Fixing ALL {table} timezones (country-aware)...")
        else:
            print(f"\n🔍 Finding {table} without timezone data...")

        records = self.get_records_without_timezone(table, limit=limit, fix_all=fix_all)
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
            old_tz = record.get('timezone')

            # Get timezone with country-aware logic
            new_tz = self.get_timezone_from_coords(lat, lng, country)

            if new_tz:
                # Only update if timezone changed (or was NULL)
                if new_tz != old_tz:
                    batch_updates.append((new_tz, record_id))
                    updated += 1

                    # Progress indicator - show changes
                    if updated <= 20 or i % 1000 == 0:
                        location_info = f"{name}, {state}, {country}" if state else f"{name}, {country}"
                        change_msg = f"{old_tz or 'NULL'} → {new_tz}"
                        print(f"  [{i:,}/{total_records:,}] {location_info}: {change_msg}")
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
        description="Timezone Management Tool - Add, fix, and validate timezone data"
    )
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')
    parser.add_argument('--table', default='both', choices=['cities', 'states', 'both'],
                        help='Process cities, states, or both (default: both)')
    parser.add_argument('--batch-size', type=int, default=1000,
                        help='Number of records to process in each batch')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of records to process (for testing)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Do not save changes to database')
    parser.add_argument('--fix-all', action='store_true',
                        help='Re-process ALL records, not just NULL/Etc timezones (fixes incorrect country assignments)')
    parser.add_argument('--validate', action='store_true',
                        help='Run validation checks only (no updates)')

    args = parser.parse_args()

    # Validation mode - just check data quality
    if args.validate:
        print("=" * 80)
        print("TIMEZONE VALIDATION MODE")
        print("=" * 80)
        print("\nℹ️  Checking timezone data quality...")
        print("   Run: python3 bin/scripts/validation/validate_timezones.py --check-cities")
        print("   for full validation report")
        return

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
                dry_run=args.dry_run,
                fix_all=args.fix_all
            )

            # Then process states
            print("\n" + "=" * 60)
            print("Processing STATES")
            print("=" * 60)
            updater.process_table(
                'states',
                batch_size=args.batch_size,
                limit=args.limit,
                dry_run=args.dry_run,
                fix_all=args.fix_all
            )
        else:
            updater.process_table(
                args.table,
                batch_size=args.batch_size,
                limit=args.limit,
                dry_run=args.dry_run,
                fix_all=args.fix_all
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
