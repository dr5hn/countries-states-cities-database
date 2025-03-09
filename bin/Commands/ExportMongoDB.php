<?php

namespace bin\Commands;

use bin\Support\Config;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Filesystem\Filesystem;
use Symfony\Component\Filesystem\Exception\IOExceptionInterface;

class ExportMongoDB extends Command
{
    protected static $defaultName = 'export:mongodb';
    protected static $defaultDescription = 'Export data to MongoDB format';

    private const COLLECTIONS = ['regions', 'subregions', 'countries', 'states', 'cities'];
    private Filesystem $filesystem;
    private array $dataCache = [];

    public function __construct()
    {
        parent::__construct(self::$defaultName);
        $this->filesystem = new Filesystem();
    }

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to MongoDB format');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $rootDir = dirname(PATH_BASE);

        $io->title('Exporting MongoDB data to ' . $rootDir . '/mongodb');

        try {
            // Ensure mongodb directory exists
            if (!$this->filesystem->exists("$rootDir/mongodb")) {
                $this->filesystem->mkdir("$rootDir/mongodb");
                $io->info('Created mongodb directory');
            }

            // First load all data to prepare for relationships
            foreach (self::COLLECTIONS as $collection) {
                $jsonFile = "$rootDir/json/$collection.json";

                if (!$this->filesystem->exists($jsonFile)) {
                    throw new \RuntimeException("JSON file not found: $jsonFile");
                }

                $data = json_decode(file_get_contents($jsonFile), true);
                if (json_last_error() !== JSON_ERROR_NONE) {
                    throw new \RuntimeException("Invalid JSON in $jsonFile: " . json_last_error_msg());
                }

                $this->dataCache[$collection] = $data;
                $io->info("Loaded $collection data: " . count($data) . " records");
            }

            // Process collections
            $this->processRegions($io, $rootDir);
            $this->processSubregions($io, $rootDir);
            $this->processCountries($io, $rootDir);
            $this->processStates($io, $rootDir);
            $this->processCities($io, $rootDir);

            $io->success('MongoDB export completed successfully');
            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }

    private function processRegions(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing regions');

        $regions = $this->dataCache['regions'];
        $processedRegions = [];

        // MongoDB format doesn't need significant modifications for regions
        foreach ($regions as $region) {
            // Convert id to MongoDB _id format
            $processedRegion = $region;
            $processedRegion['_id'] = (int) $region['id'];
            unset($processedRegion['id']);

            // Parse JSON translations if it's a string
            if (isset($processedRegion['translations']) && is_string($processedRegion['translations'])) {
                $processedRegion['translations'] = json_decode($processedRegion['translations'], true);
            }

            $processedRegions[] = $processedRegion;
        }

        $this->saveCollection($rootDir, 'regions', $processedRegions);
        $io->info('Regions exported to MongoDB format');
    }

    private function processSubregions(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing subregions');

        $subregions = $this->dataCache['subregions'];
        $regions = $this->dataCache['regions'];
        $processedSubregions = [];

        // Build region lookup using original id
        $regionLookup = [];
        foreach ($regions as $region) {
            $id = (int) $region['id'];
            $regionLookup[$id] = $region;
        }

        foreach ($subregions as $subregion) {
            // Create a new array for the processed subregion
            $processedSubregion = $subregion;

            // Convert id to MongoDB _id format
            $processedSubregion['_id'] = (int) $subregion['id'];
            unset($processedSubregion['id']);

            // Parse JSON translations if it's a string
            if (isset($processedSubregion['translations']) && is_string($processedSubregion['translations'])) {
                $processedSubregion['translations'] = json_decode($processedSubregion['translations'], true);
            }

            // Add region reference
            if (isset($processedSubregion['region_id'])) {
                $regionId = (int) $processedSubregion['region_id'];
                $processedSubregion['region'] = [
                    '$ref' => 'regions',
                    '$id' => $regionId
                ];

                // Optionally include region name for convenience
                if (isset($regionLookup[$regionId])) {
                    $processedSubregion['region_name'] = $regionLookup[$regionId]['name'];
                }
            }

            $processedSubregions[] = $processedSubregion;
        }

        $this->saveCollection($rootDir, 'subregions', $processedSubregions);
        $io->info('Subregions exported to MongoDB format');

        $this->saveCollection($rootDir, 'subregions', $subregions);
        $io->info('Subregions exported to MongoDB format');
    }

    private function processCountries(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing countries');

        $countries = $this->dataCache['countries'];
        $processedCountries = [];

        foreach ($countries as $country) {
            // Create a new array for the processed country
            $processedCountry = $country;

            // Convert id to MongoDB _id format
            $processedCountry['_id'] = (int) $country['id'];
            unset($processedCountry['id']);

            // Parse JSON strings
            if (isset($processedCountry['translations']) && is_string($processedCountry['translations'])) {
                $processedCountry['translations'] = json_decode($processedCountry['translations'], true);
            }

            if (isset($processedCountry['timezones']) && is_string($processedCountry['timezones'])) {
                $processedCountry['timezones'] = json_decode($processedCountry['timezones'], true);
            }

            // Add region reference
            if (isset($processedCountry['region_id'])) {
                $processedCountry['region'] = [
                    '$ref' => 'regions',
                    '$id' => (int) $processedCountry['region_id']
                ];
            }

            // Add subregion reference
            if (isset($processedCountry['subregion_id'])) {
                $processedCountry['subregion'] = [
                    '$ref' => 'subregions',
                    '$id' => (int) $processedCountry['subregion_id']
                ];
            }

            $processedCountries[] = $processedCountry;
        }

        $this->saveCollection($rootDir, 'countries', $processedCountries);
        $io->info('Countries exported to MongoDB format');
    }

    private function processStates(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing states');

        $states = $this->dataCache['states'];
        $processedStates = [];

        foreach ($states as $state) {
            // Create a new array for the processed state
            $processedState = $state;

            // Convert id to MongoDB _id format
            $processedState['_id'] = (int) $state['id'];
            unset($processedState['id']);

            // Add country reference
            if (isset($processedState['country_id'])) {
                $processedState['country'] = [
                    '$ref' => 'countries',
                    '$id' => (int) $processedState['country_id']
                ];
            }

            $processedStates[] = $processedState;
        }

        $this->saveCollection($rootDir, 'states', $processedStates);
        $io->info('States exported to MongoDB format');
    }

    private function processCities(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing cities');

        $cities = $this->dataCache['cities'];
        $processedCities = [];

        foreach ($cities as $city) {
            // Create a new array for the processed city
            $processedCity = $city;

            // Convert id to MongoDB _id format
            $processedCity['_id'] = (int) $city['id'];
            unset($processedCity['id']);

            // Add state reference
            if (isset($processedCity['state_id'])) {
                $processedCity['state'] = [
                    '$ref' => 'states',
                    '$id' => (int) $processedCity['state_id']
                ];
            }

            // Add country reference
            if (isset($processedCity['country_id'])) {
                $processedCity['country'] = [
                    '$ref' => 'countries',
                    '$id' => (int) $processedCity['country_id']
                ];
            }

            // Convert coordinates to GeoJSON format for MongoDB geospatial queries
            if (isset($processedCity['latitude']) && isset($processedCity['longitude'])) {
                $processedCity['location'] = [
                    'type' => 'Point',
                    'coordinates' => [(float) $processedCity['longitude'], (float) $processedCity['latitude']]
                ];
            }

            $processedCities[] = $processedCity;
        }

        $this->saveCollection($rootDir, 'cities', $processedCities);
        $io->info('Cities exported to MongoDB format');
    }

    private function saveCollection(string $rootDir, string $collection, array $data): void
    {
        $outputFile = "$rootDir/mongodb/$collection.json";
        $this->filesystem->dumpFile($outputFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }
}
