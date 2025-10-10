#!/usr/bin/env python3
"""
Split cities.json into country-wise JSON files.
Each country gets its own file in contributions/cities/
"""

import json
import os
from collections import defaultdict

def split_cities_by_country():
    """Split cities.json into separate files by country code"""

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'json', 'cities.json')
    output_dir = os.path.join(base_dir, 'contributions', 'cities')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Reading {input_file}...")

    # Read cities.json
    with open(input_file, 'r', encoding='utf-8') as f:
        cities = json.load(f)

    print(f"Total cities: {len(cities)}")

    # Group cities by country code
    cities_by_country = defaultdict(list)
    for city in cities:
        country_code = city.get('country_code', 'UNKNOWN')
        cities_by_country[country_code].append(city)

    print(f"Countries found: {len(cities_by_country)}")

    # Write each country to a separate file
    for country_code, country_cities in sorted(cities_by_country.items()):
        output_file = os.path.join(output_dir, f"{country_code}.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(country_cities, f, ensure_ascii=False, indent=2)

        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"  ✓ {country_code}.json - {len(country_cities):,} cities ({file_size_mb:.1f} MB)")

    print(f"\n✅ Successfully split {len(cities):,} cities into {len(cities_by_country)} country files")
    print(f"📁 Output directory: {output_dir}")

if __name__ == '__main__':
    split_cities_by_country()
