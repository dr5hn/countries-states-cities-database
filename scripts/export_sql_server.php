<?php
require_once 'vendor/base.php';

function generateTableSchema($table) {
    $schemas = [
        'regions' => "
IF OBJECT_ID('world.regions', 'U') IS NOT NULL DROP TABLE world.regions;
CREATE TABLE world.regions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    translations NVARCHAR(MAX),
    created_at DATETIME2 NULL,
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    flag BIT NOT NULL DEFAULT 1,
    wikiDataId NVARCHAR(255) NULL
);",
        'subregions' => "
IF OBJECT_ID('world.subregions', 'U') IS NOT NULL DROP TABLE world.subregions;
CREATE TABLE world.subregions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    translations NVARCHAR(MAX),
    region_id INT NOT NULL,
    created_at DATETIME2 NULL,
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    flag BIT NOT NULL DEFAULT 1,
    wikiDataId NVARCHAR(255) NULL,
    CONSTRAINT FK_subregions_regions FOREIGN KEY (region_id) REFERENCES world.regions(id)
);",
        'countries' => "
IF OBJECT_ID('world.countries', 'U') IS NOT NULL DROP TABLE world.countries;
CREATE TABLE world.countries (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    iso3 NCHAR(3) NULL,
    numeric_code NCHAR(3) NULL,
    iso2 NCHAR(2) NULL,
    phonecode NVARCHAR(255) NULL,
    capital NVARCHAR(255) NULL,
    currency NVARCHAR(255) NULL,
    currency_name NVARCHAR(255) NULL,
    currency_symbol NVARCHAR(255) NULL,
    tld NVARCHAR(255) NULL,
    native NVARCHAR(255) NULL,
    region NVARCHAR(255) NULL,
    region_id INT NULL,
    subregion NVARCHAR(255) NULL,
    subregion_id INT NULL,
    nationality NVARCHAR(255) NULL,
    timezones NVARCHAR(MAX),
    translations NVARCHAR(MAX),
    latitude DECIMAL(10,8) NULL,
    longitude DECIMAL(11,8) NULL,
    emoji NVARCHAR(191) NULL,
    emojiU NVARCHAR(191) NULL,
    created_at DATETIME2 NULL,
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    flag BIT NOT NULL DEFAULT 1,
    wikiDataId NVARCHAR(255) NULL,
    CONSTRAINT FK_countries_regions FOREIGN KEY (region_id) REFERENCES world.regions(id),
    CONSTRAINT FK_countries_subregions FOREIGN KEY (subregion_id) REFERENCES world.subregions(id)
);",
        'states' => "
IF OBJECT_ID('world.states', 'U') IS NOT NULL DROP TABLE world.states;
CREATE TABLE world.states (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    country_id INT NOT NULL,
    country_code NCHAR(2) NOT NULL,
    fips_code NVARCHAR(255) NULL,
    iso2 NVARCHAR(255) NULL,
    type NVARCHAR(191) NULL,
    latitude DECIMAL(10,8) NULL,
    longitude DECIMAL(11,8) NULL,
    created_at DATETIME2 NULL,
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    flag BIT NOT NULL DEFAULT 1,
    wikiDataId NVARCHAR(255) NULL,
    CONSTRAINT FK_states_countries FOREIGN KEY (country_id) REFERENCES world.countries(id)
);",
        'cities' => "
IF OBJECT_ID('world.cities', 'U') IS NOT NULL DROP TABLE world.cities;
CREATE TABLE world.cities (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    state_id INT NOT NULL,
    state_code NVARCHAR(255) NOT NULL,
    country_id INT NOT NULL,
    country_code NCHAR(2) NOT NULL,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT '2014-01-01 12:01:01',
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    flag BIT NOT NULL DEFAULT 1,
    wikiDataId NVARCHAR(255) NULL,
    CONSTRAINT FK_cities_states FOREIGN KEY (state_id) REFERENCES world.states(id),
    CONSTRAINT FK_cities_countries FOREIGN KEY (country_id) REFERENCES world.countries(id)
);"
    ];

    return $schemas[$table];
}

function generateSqlServerInsert($tableName, $data) {
    $columns = implode(', ', array_keys($data[0]));
    $sql = "INSERT INTO world.$tableName ($columns) VALUES\n";

    foreach ($data as $row) {
        $values = array_map(function($value) {
            if (is_string($value)) {
                return "N'" . str_replace("'", "''", $value) . "'";
            } elseif ($value === null) {
                return 'NULL';
            } elseif (is_array($value)) {
                return "N'" . str_replace("'", "''", json_encode($value)) . "'";
            } else {
                return $value;
            }
        }, $row);
        $sql .= "(" . implode(', ', $values) . "),\n";
    }

    return rtrim($sql, ",\n") . ";\n\n";
}

$rootDir = dirname(dirname(__FILE__));

$tables = ['regions', 'subregions', 'countries', 'states', 'cities'];

// Generate world.sql with schema creation
$worldSql = "
-- Create schema if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'world')
BEGIN
    EXEC('CREATE SCHEMA world')
END
GO
";

foreach ($tables as $table) {
    $jsonFile = $rootDir . "/json/$table.json";
    $sqlFile = $rootDir . "/sqlserver/$table.sql";

    $jsonData = json_decode(file_get_contents($jsonFile), true);

    $sql = "-- Table: $table\n\n";
    $sql .= generateTableSchema($table) . "\n\n";
    $sql .= "SET IDENTITY_INSERT world.$table ON;\n\n";
    $sql .= generateSqlServerInsert($table, $jsonData);
    $sql .= "SET IDENTITY_INSERT world.$table OFF;\n\n";

    file_put_contents($sqlFile, $sql);

    echo "SQL Server export completed for $table\n";

    // Add to world.sql
    $worldSql .= $sql;
}

// Save world.sql
file_put_contents($rootDir . "/sqlserver/world.sql", $worldSql);

echo "All SQL Server exports completed, including world.sql\n";
