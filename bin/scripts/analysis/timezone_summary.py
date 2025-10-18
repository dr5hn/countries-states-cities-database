#!/usr/bin/env python3
"""
Analyze timezone distribution across countries and states.

This script generates a comprehensive summary of:
1. Number of timezones per country
2. Which timezones are used in states
3. State-level timezone utilization statistics
"""

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def load_json(file_path: Path) -> List[Dict]:
    """Load and parse JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_timezones() -> None:
    """Generate timezone analysis report."""
    base_path = Path(__file__).parent.parent.parent.parent

    # Load data
    countries = load_json(base_path / 'contributions' / 'countries' / 'countries.json')
    states = load_json(base_path / 'contributions' / 'states' / 'states.json')

    # Data structures for analysis
    country_timezones = {}  # country_code -> list of timezone names
    country_names = {}  # country_code -> country name
    state_timezones = defaultdict(list)  # country_code -> list of state timezones
    timezone_to_states = defaultdict(int)  # timezone -> count of states using it

    # Process countries
    for country in countries:
        country_code = country['iso2']
        country_names[country_code] = country['name']

        if 'timezones' in country and country['timezones']:
            country_timezones[country_code] = [
                tz['zoneName'] for tz in country['timezones']
            ]
        else:
            country_timezones[country_code] = []

    # Process states
    for state in states:
        country_code = state['country_code']
        timezone = state.get('timezone')

        if timezone:
            state_timezones[country_code].append({
                'state_name': state['name'],
                'timezone': timezone
            })
            timezone_to_states[timezone] += 1

    # Generate report
    print("=" * 100)
    print("TIMEZONE SUMMARY REPORT")
    print("=" * 100)
    print()

    # Overall statistics
    total_countries = len(countries)
    countries_with_timezones = len([c for c in country_timezones.values() if c])
    total_unique_timezones_in_countries = len(set(tz for tzs in country_timezones.values() for tz in tzs))
    total_states = len(states)
    states_with_timezones = len([s for s in states if s.get('timezone')])
    total_unique_timezones_in_states = len(timezone_to_states)

    print("OVERALL STATISTICS")
    print("-" * 100)
    print(f"Total countries: {total_countries}")
    print(f"Countries with timezone data: {countries_with_timezones}")
    print(f"Unique timezones defined in countries: {total_unique_timezones_in_countries}")
    print(f"Total states: {total_states}")
    print(f"States with timezone data: {states_with_timezones} ({states_with_timezones/total_states*100:.1f}%)")
    print(f"Unique timezones used in states: {total_unique_timezones_in_states}")
    print()

    # Country-by-country breakdown
    print("=" * 100)
    print("COUNTRY-BY-COUNTRY BREAKDOWN")
    print("=" * 100)
    print(f"{'Country':<40} {'Code':<6} {'Country TZ':<12} {'States':<10} {'State TZ':<10} {'Coverage':<10}")
    print("-" * 100)

    # Sort by number of states descending
    country_stats = []
    for country_code in sorted(country_timezones.keys(), key=lambda c: country_names.get(c, '')):
        country_name = country_names.get(country_code, 'Unknown')
        num_country_timezones = len(country_timezones[country_code])
        num_states = len([s for s in states if s['country_code'] == country_code])
        num_states_with_tz = len(state_timezones[country_code])
        num_unique_state_timezones = len(set(s['timezone'] for s in state_timezones[country_code]))

        if num_states > 0:
            coverage = f"{num_states_with_tz/num_states*100:.0f}%"
        else:
            coverage = "N/A"

        country_stats.append({
            'name': country_name,
            'code': country_code,
            'country_tz': num_country_timezones,
            'states': num_states,
            'state_tz': num_unique_state_timezones,
            'coverage': coverage,
            'states_with_tz': num_states_with_tz
        })

    # Sort by number of states descending
    country_stats.sort(key=lambda x: x['states'], reverse=True)

    for stat in country_stats[:50]:  # Top 50 countries by number of states
        print(f"{stat['name']:<40} {stat['code']:<6} {stat['country_tz']:<12} {stat['states']:<10} {stat['state_tz']:<10} {stat['coverage']:<10}")

    print()
    print(f"... showing top 50 of {len(country_stats)} countries with states")
    print()

    # Most used timezones in states
    print("=" * 100)
    print("TOP 20 MOST USED TIMEZONES IN STATES")
    print("=" * 100)
    print(f"{'Timezone':<50} {'Number of States':<20}")
    print("-" * 100)

    sorted_timezones = sorted(timezone_to_states.items(), key=lambda x: x[1], reverse=True)
    for timezone, count in sorted_timezones[:20]:
        print(f"{timezone:<50} {count:<20}")

    print()

    # Countries with multiple timezones
    print("=" * 100)
    print("COUNTRIES WITH MULTIPLE TIMEZONES")
    print("=" * 100)

    multi_tz_countries = [(code, tzs) for code, tzs in country_timezones.items() if len(tzs) > 1]
    multi_tz_countries.sort(key=lambda x: len(x[1]), reverse=True)

    for country_code, timezones in multi_tz_countries[:20]:
        country_name = country_names.get(country_code, 'Unknown')
        print(f"\n{country_name} ({country_code}) - {len(timezones)} timezones:")
        for tz in timezones:
            # Count how many states use this timezone
            state_count = sum(1 for s in state_timezones[country_code] if s['timezone'] == tz)
            print(f"  - {tz:<50} ({state_count} states)")

    print()

    # Timezone mismatch analysis
    print("=" * 100)
    print("TIMEZONE MISMATCH ANALYSIS")
    print("=" * 100)
    print("States using timezones not defined in their country's timezone list:")
    print("-" * 100)

    mismatches = []
    for country_code, state_list in state_timezones.items():
        country_tz_list = country_timezones.get(country_code, [])
        for state_info in state_list:
            if state_info['timezone'] not in country_tz_list and country_tz_list:
                mismatches.append({
                    'country': country_names.get(country_code, 'Unknown'),
                    'country_code': country_code,
                    'state': state_info['state_name'],
                    'timezone': state_info['timezone'],
                    'expected': ', '.join(country_tz_list) if country_tz_list else 'None'
                })

    if mismatches:
        print(f"Found {len(mismatches)} potential mismatches:")
        print()
        for mismatch in mismatches[:30]:  # Show first 30
            print(f"Country: {mismatch['country']} ({mismatch['country_code']})")
            print(f"  State: {mismatch['state']}")
            print(f"  Using: {mismatch['timezone']}")
            print(f"  Expected: {mismatch['expected']}")
            print()
    else:
        print("No timezone mismatches found!")

    print()
    print("=" * 100)
    print("END OF REPORT")
    print("=" * 100)


if __name__ == '__main__':
    analyze_timezones()
