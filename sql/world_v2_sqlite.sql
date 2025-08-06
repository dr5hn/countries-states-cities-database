-- SQLite-compatible version of the v2 schema for testing
-- This converts MySQL-specific syntax to SQLite

-- Drop existing tables if they exist
DROP TABLE IF EXISTS places_v2;
DROP TABLE IF EXISTS towns_v2;
DROP TABLE IF EXISTS cities_v2;
DROP TABLE IF EXISTS states_v2;
DROP TABLE IF EXISTS countries_v2;
DROP TABLE IF EXISTS subregions_v2;
DROP TABLE IF EXISTS regions_v2;

-- Regions (Continents)
CREATE TABLE regions_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  translations TEXT,
  created_at TIMESTAMP DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL
);

-- Subregions
CREATE TABLE subregions_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  region_id INTEGER NOT NULL,
  translations TEXT,
  created_at TIMESTAMP DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL,
  FOREIGN KEY (region_id) REFERENCES regions_v2(id)
);

-- Countries
CREATE TABLE countries_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  iso3 TEXT,
  numeric_code TEXT,
  iso2 TEXT,
  phonecode TEXT,
  capital TEXT,
  currency TEXT,
  currency_name TEXT,
  currency_symbol TEXT,
  tld TEXT,
  native TEXT,
  region_id INTEGER NOT NULL,
  subregion_id INTEGER,
  nationality TEXT,
  timezones TEXT,
  translations TEXT,
  latitude REAL,
  longitude REAL,
  emoji TEXT,
  emojiU TEXT,
  created_at TIMESTAMP DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL,
  FOREIGN KEY (region_id) REFERENCES regions_v2(id),
  FOREIGN KEY (subregion_id) REFERENCES subregions_v2(id)
);

-- States (Provinces/Regions) - Only actual administrative divisions
CREATE TABLE states_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  country_id INTEGER NOT NULL,
  country_code TEXT NOT NULL,
  fips_code TEXT,
  iso2 TEXT,
  type TEXT, -- e.g., province, region, state
  native TEXT,
  latitude REAL,
  longitude REAL,
  created_at TIMESTAMP DEFAULT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL,
  FOREIGN KEY (country_id) REFERENCES countries_v2(id)
);

-- Cities - Only actual cities
CREATE TABLE cities_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  country_id INTEGER NOT NULL,
  country_code TEXT NOT NULL,
  state_id INTEGER, -- Nullable for cities without state subdivision
  state_code TEXT,
  latitude REAL NOT NULL,
  longitude REAL NOT NULL,
  created_at TIMESTAMP DEFAULT '2014-01-01 12:01:01',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL,
  FOREIGN KEY (state_id) REFERENCES states_v2(id),
  FOREIGN KEY (country_id) REFERENCES countries_v2(id)
);

-- Towns (Districts/Municipalities within cities)
CREATE TABLE towns_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  city_id INTEGER NOT NULL,
  type TEXT, -- e.g., district, municipality, borough
  latitude REAL,
  longitude REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL,
  FOREIGN KEY (city_id) REFERENCES cities_v2(id)
);

-- Places (Smaller localities within towns)
CREATE TABLE places_v2 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  town_id INTEGER NOT NULL,
  type TEXT, -- e.g., neighborhood, locality, hamlet
  latitude REAL,
  longitude REAL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  flag INTEGER DEFAULT 1,
  wikiDataId TEXT DEFAULT NULL,
  FOREIGN KEY (town_id) REFERENCES towns_v2(id)
);

-- Test data migration (sample)
-- Copy regions
INSERT INTO regions_v2 (id, name, translations, created_at, updated_at, flag, wikiDataId)
SELECT id, name, translations, created_at, updated_at, flag, wikiDataId
FROM regions;

-- Copy subregions  
INSERT INTO subregions_v2 (id, name, region_id, translations, created_at, updated_at, flag, wikiDataId)
SELECT id, name, region_id, translations, created_at, updated_at, flag, wikiDataId
FROM subregions;

-- Copy countries
INSERT INTO countries_v2 (id, name, iso3, numeric_code, iso2, phonecode, capital, currency, currency_name, currency_symbol, tld, native, region_id, subregion_id, nationality, timezones, translations, latitude, longitude, emoji, emojiU, created_at, updated_at, flag, wikiDataId)
SELECT id, name, iso3, numeric_code, iso2, phonecode, capital, currency, currency_name, currency_symbol, tld, native, region_id, subregion_id, nationality, timezones, translations, latitude, longitude, emoji, emojiU, created_at, updated_at, flag, wikiDataId
FROM countries;

-- Copy states (excluding misclassified entries)
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
);

-- Basic validation queries
-- These will be used to test the migration
.print "=== V2 Schema Validation ==="
.print "Regions count:"
SELECT COUNT(*) FROM regions_v2;

.print "Countries count:"
SELECT COUNT(*) FROM countries_v2;

.print "States count (should be less than original):"
SELECT COUNT(*) FROM states_v2;

.print "Belgium states (should not include Antwerp):"
SELECT name, type FROM states_v2 WHERE country_id = 22 ORDER BY name;

.print "Albania Tirana states (should be only 1):"
SELECT name, type FROM states_v2 WHERE country_id = 3 AND name = 'Tirana';

.print "Albania Kavajë in states (should be empty):"
SELECT name, type FROM states_v2 WHERE country_id = 3 AND name = 'Kavajë';