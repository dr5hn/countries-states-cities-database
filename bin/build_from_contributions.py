#!/usr/bin/env python3
"""
Build combined JSON files from contributions directory.
- Combines all country-wise city files
- Auto-assigns IDs to new records (those without 'id' field)
- Generates final JSON files in json/ directory
"""

import json
import os
import glob
from typing import List, Dict

def load_json_file(file_path: str) -> List[Dict]:
    """Load and parse a JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path: str, data: List[Dict], indent: int = 2):
    """Save data to JSON file with formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

def build_countries():
    """Build countries.json from contributions"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'contributions', 'countries', 'countries.json')
    output_file = os.path.join(base_dir, 'json', 'countries.json')

    print("📦 Building countries.json...")
    countries = load_json_file(input_file)

    # Find max ID
    max_id = max((c.get('id', 0) for c in countries), default=0)
    next_id = max_id + 1

    # Assign IDs to new records
    new_count = 0
    for country in countries:
        if 'id' not in country or country['id'] is None:
            country['id'] = next_id
            next_id += 1
            new_count += 1

    save_json_file(output_file, countries)
    print(f"  ✓ {len(countries)} countries ({new_count} new IDs assigned)")
    return countries

def build_states():
    """Build states.json from contributions"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'contributions', 'states', 'states.json')
    output_file = os.path.join(base_dir, 'json', 'states.json')

    print("📦 Building states.json...")
    states = load_json_file(input_file)

    # Find max ID
    max_id = max((s.get('id', 0) for s in states), default=0)
    next_id = max_id + 1

    # Assign IDs to new records
    new_count = 0
    for state in states:
        if 'id' not in state or state['id'] is None:
            state['id'] = next_id
            next_id += 1
            new_count += 1

    save_json_file(output_file, states)
    print(f"  ✓ {len(states)} states ({new_count} new IDs assigned)")
    return states

def build_cities():
    """Build cities.json from all country files in contributions"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, 'contributions', 'cities')
    output_file = os.path.join(base_dir, 'json', 'cities.json')

    print("📦 Building cities.json...")

    # Get all country JSON files
    country_files = sorted(glob.glob(os.path.join(input_dir, '*.json')))
    print(f"  Found {len(country_files)} country files")

    # Combine all cities
    all_cities = []
    for country_file in country_files:
        cities = load_json_file(country_file)
        all_cities.extend(cities)

    print(f"  Total cities before ID assignment: {len(all_cities)}")

    # Find max ID
    max_id = 0
    for city in all_cities:
        city_id = city.get('id')
        if city_id is not None and isinstance(city_id, int):
            max_id = max(max_id, city_id)

    next_id = max_id + 1
    print(f"  Max existing ID: {max_id}, next available ID: {next_id}")

    # Assign IDs to new records
    new_count = 0
    for city in all_cities:
        if 'id' not in city or city['id'] is None or city['id'] == 'NEW':
            city['id'] = next_id
            next_id += 1
            new_count += 1

    # Sort by ID for consistency
    all_cities.sort(key=lambda x: x.get('id', 0))

    save_json_file(output_file, all_cities)
    print(f"  ✓ {len(all_cities):,} cities ({new_count} new IDs assigned)")

    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"  📊 File size: {file_size_mb:.1f} MB")

    return all_cities

def main():
    """Main build process"""
    print("🏗️  Building database from contributions...\n")

    try:
        countries = build_countries()
        states = build_states()
        cities = build_cities()

        print(f"\n✅ Build complete!")
        print(f"   📍 Countries: {len(countries)}")
        print(f"   📍 States: {len(states)}")
        print(f"   📍 Cities: {len(cities):,}")
        print(f"\n💡 Next: Run export scripts to generate SQL, CSV, etc.")

    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        raise

if __name__ == '__main__':
    main()
