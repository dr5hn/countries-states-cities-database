-- Migration script to populate the v2 schema with properly organized data
-- This script identifies and corrects the data incoherence issues

-- First, copy regions (continents) - these are correct as is
INSERT INTO regions_v2 (id, name, translations, created_at, updated_at, flag, wikiDataId)
SELECT id, name, translations, created_at, updated_at, flag, wikiDataId
FROM regions;

-- Copy subregions - these are correct as is  
INSERT INTO subregions_v2 (id, name, region_id, translations, created_at, updated_at, flag, wikiDataId)
SELECT id, name, region_id, translations, created_at, updated_at, flag, wikiDataId
FROM subregions;

-- Copy countries - these are correct as is
INSERT INTO countries_v2 (id, name, iso3, numeric_code, iso2, phonecode, capital, currency, currency_name, currency_symbol, tld, native, region_id, subregion_id, nationality, timezones, translations, latitude, longitude, emoji, emojiU, created_at, updated_at, flag, wikiDataId)
SELECT id, name, iso3, numeric_code, iso2, phonecode, capital, currency, currency_name, currency_symbol, tld, native, region_id, subregion_id, nationality, timezones, translations, latitude, longitude, emoji, emojiU, created_at, updated_at, flag, wikiDataId
FROM countries;

-- Copy states - BUT exclude entries that are actually cities
-- This addresses the Belgium "Antwerp" and Albania issues
INSERT INTO states_v2 (id, name, country_id, country_code, fips_code, iso2, type, native, latitude, longitude, created_at, updated_at, flag, wikiDataId)
SELECT id, name, country_id, country_code, fips_code, iso2, type, native, latitude, longitude, created_at, updated_at, flag, wikiDataId
FROM states 
WHERE NOT (
    -- Belgium: Exclude "Antwerp" province as it's actually a city
    (country_id = 22 AND name = 'Antwerp' AND type = 'province')
    
    -- Albania: Exclude duplicate "Tirana" district (keep the county)
    OR (country_id = 3 AND name = 'Tirana' AND type = 'district')
    
    -- Albania: Exclude "Kavajë District" as it's actually a city
    OR (country_id = 3 AND name = 'Kavajë' AND type = 'district')
    
    -- Add more misclassified entries as identified
    -- We can expand this list based on further analysis
);

-- Copy cities from the original cities table
-- Correct the state_id references for misclassified entries
INSERT INTO cities_v2 (id, name, country_id, country_code, state_id, state_code, latitude, longitude, created_at, updated_at, flag, wikiDataId)
SELECT 
    id, 
    name, 
    country_id, 
    country_code,
    CASE 
        -- Belgium: For Antwerpen city, link to Flanders region instead of Antwerp province
        WHEN country_id = 22 AND name = 'Antwerpen' THEN 1373  -- Flanders region
        
        -- Albania: For Tirana city, link to Tirana County instead of Tirana District
        WHEN country_id = 3 AND name = 'Tirana' THEN 615  -- Tirana County
        
        -- Default: keep existing state_id if it exists in states_v2
        ELSE state_id
    END as state_id,
    state_code, 
    latitude, 
    longitude, 
    created_at, 
    updated_at, 
    flag, 
    wikiDataId
FROM cities
WHERE state_id IN (SELECT id FROM states_v2)  -- Only include cities with valid state references
   OR country_id IN (22, 3);  -- Include Belgium and Albania cities for special handling

-- Add former "states" that are actually cities to the cities_v2 table
-- Belgium: Add Antwerp as a city
INSERT INTO cities_v2 (name, country_id, country_code, state_id, state_code, latitude, longitude, created_at, updated_at, flag, wikiDataId)
SELECT 
    name,
    country_id,
    country_code,
    1373 as state_id,  -- Flanders region
    'VLG' as state_code,
    latitude,
    longitude,
    created_at,
    updated_at,
    flag,
    wikiDataId
FROM states 
WHERE country_id = 22 AND name = 'Antwerp' AND type = 'province';

-- Albania: Add Kavajë as a city
INSERT INTO cities_v2 (name, country_id, country_code, state_id, state_code, latitude, longitude, created_at, updated_at, flag, wikiDataId)
SELECT 
    name,
    country_id,
    country_code,
    615 as state_id,  -- Tirana County (or find the appropriate county)
    'TI' as state_code,
    latitude,
    longitude,
    created_at,
    updated_at,
    flag,
    wikiDataId
FROM states 
WHERE country_id = 3 AND name = 'Kavajë' AND type = 'district';

-- Identify and create towns from cities that are actually districts/municipalities
-- Belgium: Borgerhout should be a town within Antwerp city
-- First, find if Borgerhout exists in cities and should be moved to towns

-- For now, let's create a sample entry to demonstrate the concept
-- This would be expanded based on detailed data analysis

-- Example: If we had Borgerhout as a city linked to Flanders, 
-- we would move it to towns_v2 as a district of Antwerp city
-- INSERT INTO towns_v2 (name, city_id, type, latitude, longitude, created_at, updated_at, flag, wikiDataId)
-- SELECT 
--     'Borgerhout',
--     (SELECT id FROM cities_v2 WHERE name = 'Antwerpen' AND country_id = 22) as city_id,
--     'district',
--     latitude,
--     longitude,
--     created_at,
--     updated_at,
--     flag,
--     wikiDataId
-- FROM cities 
-- WHERE name = 'Borgerhout' AND country_id = 22;

-- Albania: Handle "Bashkia Kavajë" and similar entities
-- These would typically be moved to places_v2 as they are administrative units within cities

-- Create view for backward compatibility
CREATE VIEW countries_states_cities_v2 AS
SELECT 
    c.id as country_id,
    c.name as country_name,
    c.iso2 as country_code,
    s.id as state_id,
    s.name as state_name,
    s.state_code,
    ct.id as city_id,
    ct.name as city_name,
    ct.latitude,
    ct.longitude
FROM countries_v2 c
LEFT JOIN states_v2 s ON c.id = s.country_id
LEFT JOIN cities_v2 ct ON s.id = ct.state_id
ORDER BY c.name, s.name, ct.name;