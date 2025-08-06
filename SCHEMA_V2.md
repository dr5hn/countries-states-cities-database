# Countries States Cities Database v2.0

## Overview

This document describes the v2.0 schema for the Countries States Cities Database, designed to address the data incoherence issues identified in the original schema.

## Problems Addressed

### 1. Belgium Data Issues
- **Problem**: "Antwerp" was incorrectly listed as a province in the `states` table
- **Problem**: "Borgerhout" (a district of Antwerp) was linked to Flanders region instead of Antwerp city
- **Solution**: Antwerp is now correctly classified as a city, with proper hierarchical relationships

### 2. Albania Data Issues
- **Problem**: Duplicate entries like "Tirana County" and "Tirana District" in states table
- **Problem**: "Kavajë District" was in states table when it should be a city
- **Problem**: "Bashkia Kavajë" is not a city/state but a smaller administrative unit
- **Solution**: Proper classification with only "Tirana County" in states, and appropriate city/town hierarchy

### 3. General Hierarchical Issues
- **Problem**: Lack of proper parent-child relationships for city districts and towns
- **Problem**: Mixed classification of geographical entities
- **Solution**: Clear hierarchy with dedicated tables for each level

## New Schema Structure

### Hierarchical Levels

```
regions_v2 (continents)
  └── subregions_v2
      └── countries_v2
          └── states_v2 (provinces/regions)
              └── cities_v2
                  └── towns_v2 (districts/municipalities)
                      └── places_v2 (neighborhoods/localities)
```

### Table Definitions

#### 1. `regions_v2` (Continents)
- Same as original `regions` table
- Represents major continental divisions

#### 2. `subregions_v2` 
- Same as original `subregions` table
- Regional subdivisions within continents

#### 3. `countries_v2`
- Same as original `countries` table  
- Sovereign nations and territories

#### 4. `states_v2` (Provinces/Regions)
- **Cleaned version** of original `states` table
- Contains ONLY actual administrative divisions (provinces, regions, states)
- **Excludes**: Cities that were misclassified as states

#### 5. `cities_v2` (Cities)
- Contains actual cities and major urban areas
- **Includes**: Former "states" that are actually cities (e.g., Antwerp, Kavajë)
- **state_id**: Nullable for cities without state subdivision
- Proper parent relationship to states

#### 6. `towns_v2` (Districts/Municipalities) - NEW
- Districts, municipalities, boroughs within cities
- **Examples**: Borgerhout (district of Antwerp), Manhattan (borough of New York)
- Parent relationship to cities

#### 7. `places_v2` (Localities) - NEW
- Smaller localities within towns
- **Examples**: Neighborhoods, hamlets, small communities
- Parent relationship to towns

## Migration Process

### Data Classification Rules

1. **States Table Cleanup**:
   - Remove entries where `type = 'city'` or `type = 'municipality'`
   - Remove known misclassified entries (Antwerp province, Kavajë district, duplicate Tirana district)

2. **Cities Table Enhancement**:
   - Add former "states" that are actually cities
   - Fix state_id references for proper hierarchy
   - Ensure all cities link to valid states

3. **New Tables Population**:
   - Move city districts to `towns_v2`
   - Move smaller localities to `places_v2`

### Specific Fixes Applied

#### Belgium
```sql
-- Move Antwerp from states to cities
-- Link Antwerp city to Flanders region (1373)
-- Future: Move Borgerhout from cities to towns under Antwerp
```

#### Albania  
```sql
-- Remove duplicate "Tirana District" from states
-- Keep only "Tirana County" in states
-- Move "Kavajë" from states to cities
-- Future: Handle "Bashkia Kavajë" as administrative subdivision
```

## Backward Compatibility

### Compatibility View
```sql
CREATE VIEW countries_states_cities_v2 AS
SELECT 
    c.id as country_id,
    c.name as country_name,
    s.id as state_id, 
    s.name as state_name,
    ct.id as city_id,
    ct.name as city_name
FROM countries_v2 c
LEFT JOIN states_v2 s ON c.id = s.country_id  
LEFT JOIN cities_v2 ct ON s.id = ct.state_id;
```

### Migration Strategy
1. Deploy v2 schema alongside v1 (no breaking changes)
2. Update export processes to support both versions
3. Provide migration period for API users
4. Eventually deprecate v1 schema

## Validation

### Test Queries
```sql
-- Verify Antwerp is correctly classified
SELECT * FROM cities_v2 WHERE name = 'Antwerp' AND country_id = 22;

-- Verify no duplicate Tirana in states  
SELECT COUNT(*) FROM states_v2 WHERE name = 'Tirana' AND country_id = 3;

-- Check referential integrity
SELECT COUNT(*) FROM cities_v2 c 
LEFT JOIN states_v2 s ON c.state_id = s.id 
WHERE c.state_id IS NOT NULL AND s.id IS NULL;
```

## Benefits

1. **Data Accuracy**: Proper classification of geographical entities
2. **Hierarchical Clarity**: Clear parent-child relationships
3. **Extensibility**: Support for city districts and smaller localities
4. **Consistency**: Standardized approach across all countries
5. **API Improvement**: Better structured data for applications

## Implementation Files

- `sql/world_v2.sql` - New schema definition
- `sql/migration_v2.sql` - Data migration script  
- `sql/validation_v2.sql` - Validation queries
- `test_v2_schema.sh` - Test script
- `SCHEMA_V2.md` - This documentation

## Future Enhancements

1. Complete analysis of all countries for misclassified entries
2. Population of towns_v2 and places_v2 tables
3. Enhanced export formats supporting hierarchical queries
4. API endpoints for new hierarchical structure
5. Data validation automation

## Usage Examples

### Get all cities in a state
```sql
SELECT * FROM cities_v2 WHERE state_id = 1373; -- Flanders, Belgium
```

### Get hierarchical structure
```sql  
SELECT 
    r.name as region,
    c.name as country, 
    s.name as state,
    ct.name as city,
    t.name as town
FROM regions_v2 r
JOIN countries_v2 c ON r.id = c.region_id
JOIN states_v2 s ON c.id = s.country_id  
JOIN cities_v2 ct ON s.id = ct.state_id
LEFT JOIN towns_v2 t ON ct.id = t.city_id
WHERE c.id = 22; -- Belgium
```

### Find cities without state subdivision
```sql
SELECT * FROM cities_v2 WHERE state_id IS NULL;
```