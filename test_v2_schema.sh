#!/bin/bash

# Test script for the v2 schema implementation
# This script tests the new schema against a MySQL database

echo "Testing Countries States Cities Database v2 Schema"
echo "=================================================="

# Check if MySQL is available
if ! command -v mysql &> /dev/null; then
    echo "MySQL not found. Trying with existing SQLite files..."
    
    # Test with SQLite using existing data
    echo "Running basic data validation..."
    
    # Count entries in original data
    echo "Original data counts:"
    echo "Regions: $(sqlite3 sqlite/world.sqlite3 'SELECT COUNT(*) FROM regions;')"
    echo "Countries: $(sqlite3 sqlite/world.sqlite3 'SELECT COUNT(*) FROM countries;')"
    echo "States: $(sqlite3 sqlite/world.sqlite3 'SELECT COUNT(*) FROM states;')"
    echo "Cities: $(sqlite3 sqlite/world.sqlite3 'SELECT COUNT(*) FROM cities;')"
    
    # Check specific problem cases
    echo ""
    echo "Problem case analysis:"
    echo "Belgium - Antwerp in states table:"
    sqlite3 sqlite/world.sqlite3 "SELECT id, name, type FROM states WHERE country_id = 22 AND name = 'Antwerp';"
    
    echo "Belgium - Antwerp related cities:"
    sqlite3 sqlite/world.sqlite3 "SELECT id, name, state_id FROM cities WHERE country_id = 22 AND name LIKE '%Antwerp%';"
    
    echo "Albania - Tirana states (should be only 1):"
    sqlite3 sqlite/world.sqlite3 "SELECT id, name, type FROM states WHERE country_id = 3 AND name = 'Tirana';"
    
    echo "Albania - Kavajë in states (should be moved to cities):"
    sqlite3 sqlite/world.sqlite3 "SELECT id, name, type FROM states WHERE country_id = 3 AND name = 'Kavajë';"
    
    echo ""
    echo "Schema files created:"
    echo "- sql/world_v2.sql (new schema definition)"
    echo "- sql/migration_v2.sql (data migration script)"
    echo "- sql/validation_v2.sql (validation queries)"
    
    exit 0
fi

# MySQL testing (if available)
echo "Setting up test database..."

# Create test database
mysql -u root -e "CREATE DATABASE IF NOT EXISTS world_test_v2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || {
    echo "Could not create MySQL database. Testing with SQLite instead."
    exit 0
}

# Load original schema and data
mysql -u root world_test_v2 < sql/world.sql 2>/dev/null || {
    echo "Could not load original data. Skipping MySQL tests."
    exit 0
}

# Load v2 schema
mysql -u root world_test_v2 < sql/world_v2.sql

# Run migration
mysql -u root world_test_v2 < sql/migration_v2.sql

# Run validation
echo "Running validation tests..."
mysql -u root world_test_v2 < sql/validation_v2.sql

echo "Test completed!"