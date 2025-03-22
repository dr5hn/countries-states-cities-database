<?php

namespace bin\Commands;

use bin\Support\Config;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Filesystem\Filesystem;
use Symfony\Component\Filesystem\Exception\IOExceptionInterface;

class ExportSqlServer extends Command
{
    protected static $defaultName = 'export:sql-server';
    protected static $defaultDescription = 'Export data to SQL Server format';

    private const TABLES = ['regions', 'subregions', 'countries', 'states', 'cities'];
    private Filesystem $filesystem;

    public function __construct()
    {
        parent::__construct(self::$defaultName);
        $this->filesystem = new Filesystem();
    }

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to SQL Server format');
    }

    private function generateTableSchema(string $table): string
    {
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

        return $schemas[$table] ?? throw new \InvalidArgumentException("Unknown table: $table");
    }

    private function generateSqlServerInsert(string $tableName, array $data): string
    {
        if (empty($data)) {
            return '';
        }

        $columns = array_keys($data[0]);
        $sql = '';

        // Chunk the data into groups of 900 (leaving some margin below the 1000 limit)
        foreach (array_chunk($data, 900) as $chunk) {
            $sql .= "INSERT INTO world.$tableName (" . implode(', ', $columns) . ") VALUES\n";

            $values = array_map(function ($row) use ($columns) {
                return "(" . implode(', ', array_map(function ($column) use ($row) {
                    $value = $row[$column] ?? null;
                    return match (true) {
                        is_string($value) => "N'" . str_replace("'", "''", $value) . "'",
                        is_array($value) => "N'" . str_replace("'", "''", json_encode($value)) . "'",
                        is_null($value) => 'NULL',
                        default => $value,
                    };
                }, $columns)) . ")";
            }, $chunk);

            $sql .= implode(",\n", $values) . ";\n\n";
        }

        return $sql;
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $rootDir = dirname(PATH_BASE);

        $io->title('Exporting SQL Server data to ' . $rootDir);

        // Add a schema creation if it doesn't exist
        $worldSql = "-- Generated at " . date('Y-m-d H:i:s') . "\n\n";
        $worldSql .= "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'world')
        EXEC('CREATE SCHEMA world');\n\n";

        // Add foreign key disabling at the beginning
        $worldSql .= "-- Disable foreign key constraints\n";
        $worldSql .= "EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL';\n\n";

        try {
            foreach (self::TABLES as $table) {
                $io->section("Processing table: $table");

                $jsonFile = "$rootDir/json/$table.json";
                $sqlFile = "$rootDir/sqlserver/$table.sql";

                if (!$this->filesystem->exists($jsonFile)) {
                    throw new \RuntimeException("JSON file not found: $jsonFile");
                }

                $jsonData = json_decode(file_get_contents($jsonFile), true);
                if (json_last_error() !== JSON_ERROR_NONE) {
                    throw new \RuntimeException("Invalid JSON in $jsonFile: " . json_last_error_msg());
                }

                $sql = "-- Table: $table\n\n" .
                    $this->generateTableSchema($table) . "\n\n" .
                    "SET IDENTITY_INSERT world.$table ON;\n\n" .
                    $this->generateSqlServerInsert($table, $jsonData) .
                    "SET IDENTITY_INSERT world.$table OFF;\n\n";

                $this->filesystem->dumpFile($sqlFile, $sql);
                $worldSql .= $sql;

                $io->success("Exported $table to SQL Server format");
            }

            // Add foreign key re-enabling at the end
            $worldSql .= "-- Re-enable foreign key constraints\n";
            $worldSql .= "EXEC sp_MSforeachtable 'ALTER TABLE ? CHECK CONSTRAINT ALL';\n\n";

            $this->filesystem->dumpFile("$rootDir/sqlserver/world.sql", $worldSql);
            $io->success('Successfully generated world.sql');

            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }
}
