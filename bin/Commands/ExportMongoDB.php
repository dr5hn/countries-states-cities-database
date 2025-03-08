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

        // MongoDB format doesn't need significant modifications for regions
        foreach ($regions as &$region) {
            // Convert id to MongoDB _id format
            $region['_id'] = (int) $region['id'];
            unset($region['id']);

            // Parse JSON translations if it's a string
            if (isset($region['translations']) && is_string($region['translations'])) {
                $region['translations'] = json_decode($region['translations'], true);
            }
        }

        $this->saveCollection($rootDir, 'regions', $regions);
        $io->info('Regions exported to MongoDB format');
    }

    private function processSubregions(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing subregions');

        $subregions = $this->dataCache['subregions'];
        $regions = $this->dataCache['regions'];

        // Build region lookup
        $regionLookup = [];
        foreach ($regions as $region) {
            $regionLookup[$region['_id']] = $region;
        }

        foreach ($subregions as &$subregion) {
            // Convert id to MongoDB _id format
            $subregion['_id'] = (int) $subregion['id'];
            unset($subregion['id']);

            // Parse JSON translations if it's a string
            if (isset($subregion['translations']) && is_string($subregion['translations'])) {
                $subregion['translations'] = json_decode($subregion['translations'], true);
            }

            // Add region reference
            if (isset($subregion['region_id'])) {
                $regionId = (int) $subregion['region_id'];
                $subregion['region'] = [
                    '$ref' => 'regions',
                    '$id' => $regionId
                ];

                // Optionally include region name for convenience
                if (isset($regionLookup[$regionId])) {
                    $subregion['region_name'] = $regionLookup[$regionId]['name'];
                }
            }
        }

        $this->saveCollection($rootDir, 'subregions', $subregions);
        $io->info('Subregions exported to MongoDB format');
    }

    private function processCountries(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing countries');

        $countries = $this->dataCache['countries'];

        foreach ($countries as &$country) {
            // Convert id to MongoDB _id format
            $country['_id'] = (int) $country['id'];
            unset($country['id']);

            // Parse JSON strings
            if (isset($country['translations']) && is_string($country['translations'])) {
                $country['translations'] = json_decode($country['translations'], true);
            }

            if (isset($country['timezones']) && is_string($country['timezones'])) {
                $country['timezones'] = json_decode($country['timezones'], true);
            }

            // Add region reference
            if (isset($country['region_id'])) {
                $country['region'] = [
                    '$ref' => 'regions',
                    '$id' => (int) $country['region_id']
                ];
            }

            // Add subregion reference
            if (isset($country['subregion_id'])) {
                $country['subregion'] = [
                    '$ref' => 'subregions',
                    '$id' => (int) $country['subregion_id']
                ];
            }
        }

        $this->saveCollection($rootDir, 'countries', $countries);
        $io->info('Countries exported to MongoDB format');
    }

    private function processStates(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing states');

        $states = $this->dataCache['states'];

        foreach ($states as &$state) {
            // Convert id to MongoDB _id format
            $state['_id'] = (int) $state['id'];
            unset($state['id']);

            // Add country reference
            if (isset($state['country_id'])) {
                $state['country'] = [
                    '$ref' => 'countries',
                    '$id' => (int) $state['country_id']
                ];
            }
        }

        $this->saveCollection($rootDir, 'states', $states);
        $io->info('States exported to MongoDB format');
    }

    private function processCities(SymfonyStyle $io, string $rootDir): void
    {
        $io->section('Processing cities');

        $cities = $this->dataCache['cities'];

        foreach ($cities as &$city) {
            // Convert id to MongoDB _id format
            $city['_id'] = (int) $city['id'];
            unset($city['id']);

            // Add state reference
            if (isset($city['state_id'])) {
                $city['state'] = [
                    '$ref' => 'states',
                    '$id' => (int) $city['state_id']
                ];
            }

            // Add country reference
            if (isset($city['country_id'])) {
                $city['country'] = [
                    '$ref' => 'countries',
                    '$id' => (int) $city['country_id']
                ];
            }

            // Convert coordinates to GeoJSON format for MongoDB geospatial queries
            if (isset($city['latitude']) && isset($city['longitude'])) {
                $city['location'] = [
                    'type' => 'Point',
                    'coordinates' => [(float) $city['longitude'], (float) $city['latitude']]
                ];
            }
        }

        $this->saveCollection($rootDir, 'cities', $cities);
        $io->info('Cities exported to MongoDB format');
    }

    private function saveCollection(string $rootDir, string $collection, array $data): void
    {
        $outputFile = "$rootDir/mongodb/$collection.json";
        $this->filesystem->dumpFile($outputFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }
}
