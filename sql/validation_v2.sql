-- Validation script for the v2 schema
-- This script verifies data integrity and identifies remaining issues

-- Test 1: Check that misclassified entries are properly fixed
-- Belgium: Verify Antwerp is no longer in states_v2 but exists in cities_v2
SELECT 
    'Belgium Antwerp Test' as test_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM states_v2 WHERE country_id = 22 AND name = 'Antwerp') 
        THEN 'FAIL: Antwerp still in states'
        WHEN EXISTS (SELECT 1 FROM cities_v2 WHERE country_id = 22 AND name = 'Antwerp')
        THEN 'PASS: Antwerp correctly in cities'
        ELSE 'FAIL: Antwerp not found in cities'
    END as result;

-- Test 2: Albania Tirana duplicates
SELECT 
    'Albania Tirana Test' as test_name,
    CASE 
        WHEN (SELECT COUNT(*) FROM states_v2 WHERE country_id = 3 AND name = 'Tirana') = 1
        THEN 'PASS: Only one Tirana in states (county)'
        ELSE 'FAIL: Multiple or no Tirana entries in states'
    END as result;

-- Test 3: Albania Kavajë classification
SELECT 
    'Albania Kavajë Test' as test_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM states_v2 WHERE country_id = 3 AND name = 'Kavajë')
        THEN 'FAIL: Kavajë still in states'
        WHEN EXISTS (SELECT 1 FROM cities_v2 WHERE country_id = 3 AND name = 'Kavajë')
        THEN 'PASS: Kavajë correctly in cities'
        ELSE 'FAIL: Kavajë not found in cities'
    END as result;

-- Test 4: Check referential integrity
SELECT 
    'Referential Integrity Test' as test_name,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM cities_v2 c 
            LEFT JOIN states_v2 s ON c.state_id = s.id 
            WHERE c.state_id IS NOT NULL AND s.id IS NULL
        )
        THEN 'FAIL: Cities with invalid state references'
        ELSE 'PASS: All city state references are valid'
    END as result;

-- Test 5: Count comparisons
SELECT 'Data Count Comparison' as test_name, 'Original vs V2' as result;

SELECT 
    'Original regions' as table_name, 
    COUNT(*) as count 
FROM regions
UNION ALL
SELECT 
    'V2 regions' as table_name, 
    COUNT(*) as count 
FROM regions_v2
UNION ALL
SELECT 
    'Original countries' as table_name, 
    COUNT(*) as count 
FROM countries
UNION ALL
SELECT 
    'V2 countries' as table_name, 
    COUNT(*) as count 
FROM countries_v2
UNION ALL
SELECT 
    'Original states' as table_name, 
    COUNT(*) as count 
FROM states
UNION ALL
SELECT 
    'V2 states' as table_name, 
    COUNT(*) as count 
FROM states_v2
UNION ALL
SELECT 
    'Original cities' as table_name, 
    COUNT(*) as count 
FROM cities
UNION ALL
SELECT 
    'V2 cities' as table_name, 
    COUNT(*) as count 
FROM cities_v2;

-- Test 6: Identify remaining problematic entries
-- Find states that might actually be cities (by analyzing type and level)
SELECT 
    'Potential misclassified states' as analysis,
    country_id,
    name,
    type,
    level,
    parent_id
FROM states_v2 
WHERE type IN ('city', 'municipality', 'district', 'town')
   OR name LIKE '%City%'
   OR name LIKE '%Municipality%'
ORDER BY country_id, name
LIMIT 20;

-- Test 7: Find cities that might actually be towns/districts
SELECT 
    'Potential towns in cities table' as analysis,
    c.country_id,
    c.name as city_name,
    s.name as state_name,
    c.name
FROM cities_v2 c
JOIN states_v2 s ON c.state_id = s.id
WHERE c.name LIKE '%District%'
   OR c.name LIKE '%Municipality%'
   OR c.name LIKE '%Borough%'
   OR c.name LIKE '%Ward%'
ORDER BY c.country_id, s.name, c.name
LIMIT 20;