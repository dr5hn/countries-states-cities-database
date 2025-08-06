#!/usr/bin/env python3

"""
DuckDB Import Script for Countries States Cities Database - Simplified Version

This script converts the SQLite database to DuckDB format with efficiency optimizations.
Handles timestamp conversion issues and provides global ID option.
"""

import sqlite3
import duckdb
import argparse
import sys
import os
from datetime import datetime

def create_table_ddl(table_name, columns_info):
    """Create DuckDB DDL for a table"""
    type_mapping = {
        'INTEGER': 'INTEGER',
        'MEDIUMINT': 'INTEGER', 
        'TINYINT': 'TINYINT',
        'VARCHAR': 'VARCHAR',
        'CHARACTER': 'VARCHAR',
        'CHAR': 'VARCHAR',
        'TEXT': 'TEXT',
        'DECIMAL': 'DECIMAL',
        'DATETIME': 'TIMESTAMP',
        'TIMESTAMP': 'TIMESTAMP'
    }
    
    columns = []
    for col_info in columns_info:
        col_name = col_info[1]
        sqlite_type = col_info[2].upper()
        not_null = col_info[3] == 1
        is_pk = col_info[5] == 1
        
        # Map type
        duckdb_type = 'VARCHAR'  # default
        for sql_type, duck_type in type_mapping.items():
            if sql_type in sqlite_type:
                duckdb_type = duck_type
                break
        
        # Build column definition
        col_def = f"{col_name} {duckdb_type}"
        if is_pk:
            col_def += " PRIMARY KEY"
        elif not_null and col_name not in ['created_at', 'updated_at']:
            col_def += " NOT NULL"
            
        columns.append(col_def)
    
    return f"CREATE TABLE {table_name} ({', '.join(columns)})"

def main():
    parser = argparse.ArgumentParser(description='Convert SQLite database to DuckDB format')
    parser.add_argument('--global-ids', action='store_true', help='Use global sequence IDs')
    parser.add_argument('--output', default='./duckdb/world.db', help='Output DuckDB path')
    parser.add_argument('--input', default='./sqlite/world.sqlite3', help='Input SQLite path')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found")
        sys.exit(1)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    if os.path.exists(args.output):
        os.remove(args.output)
    
    print(f"Converting {args.input} to {args.output}")
    
    # Connect to databases
    sqlite_conn = sqlite3.connect(args.input)
    duck_conn = duckdb.connect(args.output)
    
    try:
        # Get tables in dependency order
        tables = ['regions', 'subregions', 'countries', 'states', 'cities']
        
        global_id = 0
        
        for table_name in tables:
            print(f"\nProcessing {table_name}...")
            
            # Get schema
            cursor = sqlite_conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()
            
            # Create table
            ddl = create_table_ddl(table_name, columns_info)
            print(f"Creating table: {ddl}")
            duck_conn.execute(ddl)
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            print(f"Copying {len(rows)} rows...")
            
            # Convert data
            column_names = [col[1] for col in columns_info]
            converted_rows = []
            
            for row in rows:
                converted_row = list(row)
                
                for i, (value, col_info) in enumerate(zip(converted_row, columns_info)):
                    col_name = col_info[1]
                    col_type = col_info[2].upper()
                    
                    # Handle global IDs
                    if args.global_ids and col_name == 'id':
                        global_id += 1
                        converted_row[i] = global_id
                    
                    # Handle timestamps - convert to proper format for DuckDB
                    elif 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
                        if value and str(value) != 'CURRENT_TIMESTAMP':
                            try:
                                # Parse and reformat timestamp
                                if isinstance(value, str):
                                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                                        try:
                                            dt = datetime.strptime(value, fmt)
                                            converted_row[i] = dt.strftime('%Y-%m-%d %H:%M:%S')
                                            break
                                        except ValueError:
                                            continue
                                    else:
                                        # Default if parsing fails
                                        converted_row[i] = '2014-01-01 12:01:01'
                            except:
                                converted_row[i] = '2014-01-01 12:01:01'
                
                converted_rows.append(converted_row)
            
            # Bulk insert using executemany for efficiency
            if converted_rows:
                placeholders = ', '.join(['?' for _ in column_names])
                insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                duck_conn.executemany(insert_sql, converted_rows)
            
            # Verify
            count = duck_conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"Inserted {count} rows")
        
        # Add indexes
        print("\nCreating indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_cities_state_id ON cities(state_id)",
            "CREATE INDEX IF NOT EXISTS idx_cities_country_id ON cities(country_id)",
            "CREATE INDEX IF NOT EXISTS idx_states_country_id ON states(country_id)",
            "CREATE INDEX IF NOT EXISTS idx_countries_region_id ON countries(region_id)",
            "CREATE INDEX IF NOT EXISTS idx_countries_subregion_id ON countries(subregion_id)",
            "CREATE INDEX IF NOT EXISTS idx_subregions_region_id ON subregions(region_id)"
        ]
        
        for idx_sql in indexes:
            try:
                duck_conn.execute(idx_sql)
            except Exception as e:
                print(f"Index creation warning: {e}")
        
        # Final stats
        print("\n=== Conversion Complete ===")
        for table in tables:
            count = duck_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count:,} records")
        
        # File size comparison
        sqlite_size = os.path.getsize(args.input)
        duck_size = os.path.getsize(args.output)
        reduction = (1 - duck_size / sqlite_size) * 100
        
        print(f"\nFile sizes:")
        print(f"SQLite: {sqlite_size / (1024*1024):.1f} MB")
        print(f"DuckDB: {duck_size / (1024*1024):.1f} MB")
        print(f"Reduction: {reduction:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        sqlite_conn.close()
        duck_conn.close()
    
    print(f"\nDuckDB database created successfully: {args.output}")

if __name__ == "__main__":
    main()