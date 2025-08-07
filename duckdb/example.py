#!/usr/bin/env python3
"""
Example usage of the Countries States Cities DuckDB database.

This script demonstrates basic queries and usage patterns.
"""

import duckdb
import sys
import os

def main():
    # Check if database exists
    db_path = 'world.db'
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        print("Please run: python3 ../bin/import_duckdb.py")
        sys.exit(1)
    
    # Connect to the database
    conn = duckdb.connect(db_path)
    
    try:
        print("🌍 Countries States Cities Database - DuckDB Example")
        print("=" * 50)
        
        # Basic statistics
        print("\n📊 Database Statistics:")
        tables = ['regions', 'subregions', 'countries', 'states', 'cities']
        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table.capitalize()}: {count:,} records")
        
        # Example queries
        print("\n🌎 Regions by Country Count:")
        result = conn.execute("""
            SELECT r.name, COUNT(c.id) as country_count 
            FROM regions r 
            LEFT JOIN countries c ON r.id = c.region_id 
            GROUP BY r.id, r.name 
            ORDER BY country_count DESC
        """).fetchall()
        for row in result:
            print(f"  {row[0]}: {row[1]} countries")
        
        print("\n🏙️ Largest Countries by City Count (Top 5):")
        result = conn.execute("""
            SELECT c.name, COUNT(ci.id) as city_count 
            FROM countries c 
            LEFT JOIN cities ci ON c.id = ci.country_id 
            GROUP BY c.id, c.name 
            ORDER BY city_count DESC 
            LIMIT 5
        """).fetchall()
        for row in result:
            print(f"  {row[0]}: {row[1]:,} cities")
        
        print("\n🇺🇸 Sample US Cities:")
        result = conn.execute("""
            SELECT ci.name, s.name as state_name
            FROM cities ci 
            JOIN states s ON ci.state_id = s.id 
            WHERE ci.country_code = 'US' 
            ORDER BY ci.name
            LIMIT 5
        """).fetchall()
        for row in result:
            print(f"  {row[0]}, {row[1]}")
        
        print("\n🔍 Search Example - Cities containing 'New':")
        result = conn.execute("""
            SELECT ci.name, s.name as state_name, c.name as country_name
            FROM cities ci 
            JOIN states s ON ci.state_id = s.id 
            JOIN countries c ON ci.country_id = c.id
            WHERE ci.name ILIKE '%new%'
            ORDER BY c.name, s.name, ci.name
            LIMIT 8
        """).fetchall()
        for row in result:
            print(f"  {row[0]}, {row[1]}, {row[2]}")
        
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()