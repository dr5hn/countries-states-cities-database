#!/usr/bin/env python3
"""
Validate and Report on Timezone Data Quality

This script checks for timezone issues in countries, states, and cities.
It can be used to audit the data and identify any remaining inconsistencies.

Usage:
    python3 bin/scripts/utility/validate_timezones.py
    python3 bin/scripts/utility/validate_timezones.py --fix-states

Options:
    --fix-states    Generate SQL to fix problematic state timezones
    --check-cities  Also check cities data (requires MySQL connection)
"""

import json
import argparse
from typing import Set, Dict, List
from collections import defaultdict

def load_json(filepath: str) -> List[Dict]:
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_country_timezones() -> Set[str]:
    """Extract all unique timezones from countries"""
    countries = load_json('contributions/countries/countries.json')
    timezones = set()

    for country in countries:
        if 'timezones' in country and country['timezones']:
            for tz in country['timezones']:
                if isinstance(tz, dict) and 'zoneName' in tz:
                    timezones.add(tz['zoneName'])

    return timezones

def get_state_timezones() -> Dict[str, List[Dict]]:
    """Extract all timezones from states, grouped by timezone name"""
    states = load_json('contributions/states/states.json')
    timezone_map = defaultdict(list)

    for state in states:
        if 'timezone' in state and state['timezone']:
            timezone_map[state['timezone']].append({
                'id': state.get('id'),
                'name': state.get('name'),
                'country': state.get('country_code'),
                'lat': state.get('latitude'),
                'lng': state.get('longitude')
            })

    return dict(timezone_map)

def validate_iana_timezone(tz_name: str) -> bool:
    """Check if timezone is a valid IANA timezone"""
    try:
        import pytz
        pytz.timezone(tz_name)
        return True
    except:
        # pytz not installed or invalid timezone
        return not tz_name.startswith('Etc/GMT')

def main():
    parser = argparse.ArgumentParser(
        description="Validate timezone data quality"
    )
    parser.add_argument('--fix-states', action='store_true',
                       help='Generate SQL to fix problematic states')
    parser.add_argument('--check-cities', action='store_true',
                       help='Also check cities (requires MySQL)')

    args = parser.parse_args()

    print("=" * 80)
    print("TIMEZONE DATA QUALITY VALIDATION")
    print("=" * 80)
    print()

    # Get timezone data
    country_tzs = get_country_timezones()
    state_tzs = get_state_timezones()

    print(f"📊 Data Summary:")
    print(f"  Countries: {len(country_tzs)} unique timezones")
    print(f"  States: {len(state_tzs)} unique timezones")
    print()

    # Check 1: Etc/GMT timezones in states
    print("=" * 80)
    print("CHECK 1: Problematic Etc/ Timezones in States")
    print("=" * 80)

    etc_timezones = {tz: states for tz, states in state_tzs.items()
                     if tz.startswith('Etc/')}

    if etc_timezones:
        print(f"⚠️  Found {len(etc_timezones)} Etc/ timezone(s):")
        print()

        for tz, states in etc_timezones.items():
            print(f"  {tz}:")
            for state in states:
                print(f"    - {state['name']} ({state['country']}) [ID: {state['id']}]")
            print()

        if args.fix_states:
            print("Suggested SQL fixes:")
            print("-" * 80)
            for tz, states in etc_timezones.items():
                for state in states:
                    # Try to determine correct timezone
                    print(f"-- {state['name']} ({state['country']})")
                    print(f"UPDATE states SET timezone = '???' WHERE id = {state['id']};")
                    print()
    else:
        print("✅ No Etc/ timezones found in states")
    print()

    # Check 2: States timezones not in countries
    print("=" * 80)
    print("CHECK 2: State Timezones Not in Country Definitions")
    print("=" * 80)

    states_not_in_countries = set(state_tzs.keys()) - country_tzs

    if states_not_in_countries:
        print(f"⚠️  Found {len(states_not_in_countries)} timezone(s) in states but not in countries:")
        print()

        for tz in sorted(states_not_in_countries):
            states = state_tzs[tz]
            print(f"  {tz}: ({len(states)} state(s))")
            for state in states[:3]:  # Show first 3
                print(f"    - {state['name']} ({state['country']})")
            if len(states) > 3:
                print(f"    ... and {len(states) - 3} more")
            print()
    else:
        print("✅ All state timezones exist in country definitions")
    print()

    # Check 3: Invalid IANA timezones
    print("=" * 80)
    print("CHECK 3: Invalid or Deprecated Timezones")
    print("=" * 80)

    invalid_states = []
    for tz, states in state_tzs.items():
        if not validate_iana_timezone(tz):
            invalid_states.extend([(tz, state) for state in states])

    if invalid_states:
        print(f"⚠️  Found {len(invalid_states)} state(s) with invalid timezones:")
        print()

        for tz, state in invalid_states:
            print(f"  {state['name']} ({state['country']}): {tz}")
    else:
        print("✅ All state timezones are valid IANA identifiers")
    print()

    # Check 4: Cities (if requested)
    if args.check_cities:
        print("=" * 80)
        print("CHECK 4: City Timezone Issues")
        print("=" * 80)

        try:
            import mysql.connector
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='world'
            )
            cursor = conn.cursor(dictionary=True)

            # Check for Etc/GMT timezones in cities
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM cities
                WHERE timezone LIKE 'Etc/GMT%'
            """)
            etc_count = cursor.fetchone()['count']

            if etc_count > 0:
                print(f"⚠️  Found {etc_count} cities with Etc/GMT timezones")
                print("   Run: UPDATE cities SET timezone = NULL WHERE timezone LIKE 'Etc/GMT%';")
            else:
                print("✅ No Etc/GMT timezones in cities")

            # Check for NULL timezones
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM cities
                WHERE timezone IS NULL
            """)
            null_count = cursor.fetchone()['count']

            print(f"ℹ️  {null_count} cities have NULL timezone (can be populated with add_timezones.py)")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"⚠️  Could not connect to MySQL: {e}")
            print("   Skipping city checks")

        print()

    # Summary
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)

    issues = 0
    if etc_timezones:
        issues += len(etc_timezones)
    if states_not_in_countries:
        issues += len(states_not_in_countries)
    if invalid_states:
        issues += len(invalid_states)

    if issues == 0:
        print("✅ No timezone issues found!")
        print("   All timezones are properly formatted IANA identifiers")
    else:
        print(f"⚠️  Found {issues} issue(s) requiring attention")
        print("   See details above")
    print()

if __name__ == '__main__':
    main()
