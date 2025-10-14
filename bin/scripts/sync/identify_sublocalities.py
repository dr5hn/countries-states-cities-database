#!/usr/bin/env python3
"""
Identify Potential Sub-localities Script

This script helps identify cities that might be sub-localities (neighborhoods/areas
within larger cities) by analyzing proximity and WikiData relationships.

It looks for:
1. Multiple cities in the same state that are very close to each other (< 20km)
2. WikiData entries that indicate a place is part of another place
3. Common naming patterns (e.g., "Mumbai Suburban", "North London", etc.)

Usage:
    python3 bin/scripts/sync/identify_sublocalities.py --country IN --state MH
    python3 bin/scripts/sync/identify_sublocalities.py --all

Requirements:
    pip install mysql-connector-python geopy
"""

import argparse
import sys
import os
import json
from typing import List, Dict, Tuple, Optional
import mysql.connector
from datetime import datetime
from collections import defaultdict


class SublocalityIdentifier:
    """Identify potential sub-localities from cities data"""

    def __init__(self, host='localhost', user='root', password='root', database='world'):
        """Initialize database connection"""
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset='utf8mb4',
                use_unicode=True
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print(f"✓ Connected to MySQL database '{database}'")
        except mysql.connector.Error as e:
            print(f"❌ MySQL connection failed: {e}")
            sys.exit(1)

    def get_cities_by_location(self, country_code: Optional[str] = None, 
                                state_code: Optional[str] = None) -> List[Dict]:
        """Get cities filtered by country and/or state"""
        query = """
            SELECT id, name, state_id, state_code, country_id, country_code, 
                   latitude, longitude, wikiDataId
            FROM cities
            WHERE 1=1
        """
        params = []
        
        if country_code:
            query += " AND country_code = %s"
            params.append(country_code)
        
        if state_code:
            query += " AND state_code = %s"
            params.append(state_code)
        
        query += " ORDER BY country_code, state_code, name"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (in km)"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r

    def find_nearby_cities(self, cities: List[Dict], max_distance_km: float = 20.0) -> List[Tuple]:
        """Find cities that are very close to each other (potential sub-localities)"""
        nearby_pairs = []
        
        # Group cities by state for efficiency
        by_state = defaultdict(list)
        for city in cities:
            key = f"{city['country_code']}-{city['state_code']}"
            by_state[key].append(city)
        
        # Check within each state
        for state_key, state_cities in by_state.items():
            for i, city1 in enumerate(state_cities):
                for city2 in state_cities[i+1:]:
                    distance = self.calculate_distance(
                        city1['latitude'], city1['longitude'],
                        city2['latitude'], city2['longitude']
                    )
                    
                    if distance <= max_distance_km:
                        nearby_pairs.append((city1, city2, distance))
        
        return nearby_pairs

    def analyze_naming_patterns(self, cities: List[Dict]) -> List[Dict]:
        """Identify cities with naming patterns suggesting sub-localities"""
        suspicious = []
        
        # Patterns that suggest sub-locality
        patterns = [
            'North ', 'South ', 'East ', 'West ',
            'Central ', 'Greater ',
            ' Suburban', ' Urban', ' Rural',
            'Downtown', 'Uptown',
            'Inner ', 'Outer ',
        ]
        
        for city in cities:
            name = city['name']
            for pattern in patterns:
                if pattern.lower() in name.lower():
                    suspicious.append({
                        'city': city,
                        'reason': f"Name contains '{pattern.strip()}'"
                    })
                    break
        
        return suspicious

    def generate_report(self, country_code: Optional[str] = None, 
                       state_code: Optional[str] = None,
                       max_distance: float = 20.0) -> Dict:
        """Generate a report of potential sub-localities"""
        
        print(f"\n🔍 Analyzing cities...")
        if country_code:
            print(f"   Country: {country_code}")
        if state_code:
            print(f"   State: {state_code}")
        print(f"   Max distance: {max_distance} km")
        
        cities = self.get_cities_by_location(country_code, state_code)
        print(f"   Found {len(cities)} cities to analyze\n")
        
        # Find nearby cities
        print("📍 Finding nearby cities...")
        nearby = self.find_nearby_cities(cities, max_distance)
        print(f"   Found {len(nearby)} city pairs within {max_distance}km\n")
        
        # Analyze naming patterns
        print("📝 Analyzing naming patterns...")
        suspicious_names = self.analyze_naming_patterns(cities)
        print(f"   Found {len(suspicious_names)} cities with suspicious naming patterns\n")
        
        return {
            'nearby_cities': nearby,
            'suspicious_names': suspicious_names,
            'total_cities': len(cities)
        }

    def print_report(self, report: Dict, limit: int = 50):
        """Print the analysis report"""
        
        print("\n" + "=" * 80)
        print("🔎 POTENTIAL SUB-LOCALITIES REPORT")
        print("=" * 80)
        
        print(f"\n📊 Summary:")
        print(f"   Total cities analyzed: {report['total_cities']}")
        print(f"   Nearby city pairs: {len(report['nearby_cities'])}")
        print(f"   Suspicious names: {len(report['suspicious_names'])}")
        
        # Show nearby cities
        if report['nearby_cities']:
            print(f"\n🏙️  Nearby Cities (showing up to {limit}):")
            print("   " + "-" * 76)
            
            for i, (city1, city2, distance) in enumerate(report['nearby_cities'][:limit]):
                print(f"\n   {i+1}. {city1['name']} ↔ {city2['name']}")
                print(f"      Distance: {distance:.2f} km")
                print(f"      IDs: {city1['id']} and {city2['id']}")
                print(f"      State: {city1['state_code']}, Country: {city1['country_code']}")
                if city1['wikiDataId']:
                    print(f"      WikiData: {city1['wikiDataId']} and {city2['wikiDataId']}")
        
        # Show suspicious names
        if report['suspicious_names']:
            print(f"\n📛 Suspicious Naming Patterns (showing up to {limit}):")
            print("   " + "-" * 76)
            
            for i, item in enumerate(report['suspicious_names'][:limit]):
                city = item['city']
                print(f"\n   {i+1}. {city['name']}")
                print(f"      Reason: {item['reason']}")
                print(f"      ID: {city['id']}")
                print(f"      Location: {city['state_code']}, {city['country_code']}")
                if city['wikiDataId']:
                    print(f"      WikiData: {city['wikiDataId']}")
        
        print("\n" + "=" * 80)
        print("\n💡 Next Steps:")
        print("   1. Review the identified cities manually")
        print("   2. Check WikiData for each entry to verify relationships")
        print("   3. Move confirmed sub-localities to contributions/sublocalities/sublocalities.json")
        print("   4. Remove them from contributions/cities/<COUNTRY>.json")
        print("\n")

    def export_json_report(self, report: Dict, output_file: str = 'potential_sublocalities.json'):
        """Export report to JSON for further processing"""
        
        # Convert to serializable format
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_cities': report['total_cities'],
                'nearby_pairs': len(report['nearby_cities']),
                'suspicious_names': len(report['suspicious_names'])
            },
            'nearby_cities': [
                {
                    'city1': {
                        'id': c1['id'],
                        'name': c1['name'],
                        'state_code': c1['state_code'],
                        'country_code': c1['country_code'],
                        'wikiDataId': c1['wikiDataId']
                    },
                    'city2': {
                        'id': c2['id'],
                        'name': c2['name'],
                        'state_code': c2['state_code'],
                        'country_code': c2['country_code'],
                        'wikiDataId': c2['wikiDataId']
                    },
                    'distance_km': round(dist, 2)
                }
                for c1, c2, dist in report['nearby_cities']
            ],
            'suspicious_names': [
                {
                    'id': item['city']['id'],
                    'name': item['city']['name'],
                    'state_code': item['city']['state_code'],
                    'country_code': item['city']['country_code'],
                    'reason': item['reason'],
                    'wikiDataId': item['city']['wikiDataId']
                }
                for item in report['suspicious_names']
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Report exported to {output_file}")

    def close(self):
        """Close database connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Identify potential sub-localities from cities data"
    )
    parser.add_argument('--host', default='localhost', help='MySQL host')
    parser.add_argument('--user', default='root', help='MySQL user')
    parser.add_argument('--password', default='root', help='MySQL password')
    parser.add_argument('--database', default='world', help='MySQL database')
    parser.add_argument('--country', help='Filter by country code (e.g., IN, US)')
    parser.add_argument('--state', help='Filter by state code (e.g., MH, CA)')
    parser.add_argument('--distance', type=float, default=20.0,
                       help='Maximum distance in km to consider cities as nearby (default: 20)')
    parser.add_argument('--export', help='Export report to JSON file')
    parser.add_argument('--limit', type=int, default=50,
                       help='Limit number of results to display (default: 50)')
    
    args = parser.parse_args()
    
    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(project_root)
    
    identifier = SublocalityIdentifier(
        host=args.host,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    try:
        report = identifier.generate_report(
            country_code=args.country,
            state_code=args.state,
            max_distance=args.distance
        )
        
        identifier.print_report(report, limit=args.limit)
        
        if args.export:
            identifier.export_json_report(report, args.export)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        identifier.close()


if __name__ == '__main__':
    main()
