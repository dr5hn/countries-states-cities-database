#!/usr/bin/env python3

"""
DuckDB Import Script for Countries States Cities Database

This script converts the SQLite database to DuckDB format with efficiency optimizations.
Handles timestamp conversion issues and provides global ID option with proper foreign key mapping.

Based on the original script and improvements suggested in:
https://github.com/adsharma/truth-serum/blob/main/truth/import_cities.py
"""

import sqlite3
import duckdb
import argparse
import sys
import os
from datetime import datetime
try:
    import pandas as pd
    import inflect
    PANDAS_AVAILABLE = True
    p = inflect.engine()
except ImportError:
    PANDAS_AVAILABLE = False

def get_existing_tables(sqlite_conn):
    """Get list of tables that actually exist in the SQLite database"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    # Return tables in dependency order, but only if they exist
    all_tables = ['regions', 'subregions', 'countries', 'states', 'cities']
    return [table for table in all_tables if table in existing_tables]

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

def convert_with_pandas_global_ids(args, sqlite_conn, duck_conn):
    """Enhanced conversion using pandas with proper global ID mapping and foreign key updates"""
    if not PANDAS_AVAILABLE:
        print("Warning: pandas not available, falling back to basic conversion")
        return convert_basic(args, sqlite_conn, duck_conn)
    
    print("Using enhanced conversion with pandas and proper global ID mapping...")
    
    # Get tables that actually exist in the SQLite database
    tables = get_existing_tables(sqlite_conn)
    print(f"Found tables: {tables}")
    
    # Create global sequence in DuckDB
    try:
        duck_conn.execute("CREATE SEQUENCE global_sequence START 1")
    except Exception as e:
        print(f"Note: Global sequence creation info: {e}")
    
    # Dictionary to store old_id -> new_id mappings for each table
    id_mappings = {table: {} for table in tables}
    current_id = 1
    
    # First pass: Read data and create ID mappings
    print("Pass 1: Creating global ID mappings...")
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
        for old_id in df["id"]:
            id_mappings[table][old_id] = current_id
            current_id += 1
        print(f"  {table}: mapped {len(df)} IDs")
    
    # Second pass: Create tables and insert data with updated IDs
    print("Pass 2: Creating tables and inserting data...")
    for table in tables:
        # Get original schema
        cursor = sqlite_conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        create_stmt = cursor.fetchone()[0]
        
        # Modify schema for DuckDB
        create_stmt = create_stmt.replace("AUTOINCREMENT", "DEFAULT nextval('global_sequence')")
        create_stmt = create_stmt.replace("MEDIUMINT", "INTEGER")
        
        # Create table
        duck_conn.execute(create_stmt)
        print(f"  Created table: {table}")
        
        # Read and transform data
        df = pd.read_sql_query(f"SELECT * FROM {table}", sqlite_conn)
        
        # Update IDs with global mappings
        df["id"] = df["id"].map(id_mappings[table])
        
        # Fix timestamps - set to current time to avoid conversion issues
        if 'created_at' in df.columns:
            df["created_at"] = pd.Timestamp.now()
        if 'updated_at' in df.columns:
            df["updated_at"] = pd.Timestamp.now()
        
        # Update foreign key references
        for col in df.columns:
            if col.endswith("_id") and col != "id":
                # Determine referenced table
                ref_table = None
                if col == "region_id":
                    ref_table = "regions"
                elif col == "subregion_id":
                    ref_table = "subregions"
                elif col == "country_id":
                    ref_table = "countries"
                elif col == "state_id":
                    ref_table = "states"
                elif col == "parent_id" and table == "states":
                    ref_table = "states"
                
                # Update foreign key with new global ID
                if ref_table and ref_table in id_mappings:
                    df[col] = df[col].map(lambda x: id_mappings[ref_table].get(x, x) if pd.notna(x) else x)
        
        # Insert data using pandas integration
        duck_conn.execute(f"INSERT INTO {table} SELECT * FROM df")
        
        count = duck_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: inserted {count:,} rows")
    
    return tables

def convert_basic(args, sqlite_conn, duck_conn):
    """Basic conversion method (fallback when pandas not available)"""
    print("Using basic conversion method...")
    
    # Get tables that actually exist in the SQLite database
    tables = get_existing_tables(sqlite_conn)
    print(f"Found tables: {tables}")
    
    # Create tables and insert data
    print("Creating tables and inserting data...")
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
                
                # Handle timestamps - use current time to avoid conversion issues
                if 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
                    if value and str(value) != 'CURRENT_TIMESTAMP':
                        # Use current timestamp to avoid conversion issues
                        converted_row[i] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            converted_rows.append(converted_row)
        
        # Bulk insert using executemany for efficiency
        if converted_rows:
            placeholders = ', '.join(['?' for _ in column_names])
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            duck_conn.executemany(insert_sql, converted_rows)
        
        # Verify
        count = duck_conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Inserted {count} rows")
    
    return tables

def optimize_tables(duck_conn, tables):
    """Optimize tables by sorting by primary key for better performance"""
    print("\nOptimizing tables (sorting by primary key)...")
    for table in tables:
        try:
            # Sort table by primary key (id) for better query performance
            # This is more efficient than indexes for DuckDB
            duck_conn.execute(f"CREATE TABLE {table}_sorted AS SELECT * FROM {table} ORDER BY id")
            duck_conn.execute(f"DROP TABLE {table}")
            duck_conn.execute(f"ALTER TABLE {table}_sorted RENAME TO {table}")
            print(f"  Optimized table: {table}")
        except Exception as e:
            print(f"Table optimization warning for {table}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Convert SQLite database to DuckDB format')
    parser.add_argument('--global-ids', action='store_true', 
                       help='Use global sequence IDs (WikiData-like) with proper foreign key mapping')
    parser.add_argument('--enhanced', action='store_true',
                       help='Use enhanced conversion with pandas (requires pandas and inflect)')
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
    if args.global_ids:
        print("Using global sequence IDs with foreign key mapping")
    if args.enhanced and PANDAS_AVAILABLE:
        print("Using enhanced conversion with pandas")
    elif args.enhanced and not PANDAS_AVAILABLE:
        print("Warning: Enhanced mode requested but pandas not available, using basic mode")
    
    # Connect to databases
    sqlite_conn = sqlite3.connect(args.input)
    duck_conn = duckdb.connect(args.output)
    
    try:
        # Choose conversion method
        if args.enhanced and args.global_ids and PANDAS_AVAILABLE:
            tables = convert_with_pandas_global_ids(args, sqlite_conn, duck_conn)
        else:
            tables = convert_basic(args, sqlite_conn, duck_conn)
        
        # Optimize tables by sorting for performance  
        optimize_tables(duck_conn, tables)
        
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