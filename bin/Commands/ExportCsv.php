<?php

namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Filesystem\Filesystem;

class ExportCsv extends Command
{
    protected static $defaultName = 'export:csv';
    protected static $defaultDescription = 'Export data to CSV format';

    private const FILES = [
        'countries' => ['from' => '/json/countries.json', 'to' => '/csv/countries.csv'],
        'states' => ['from' => '/json/states.json', 'to' => '/csv/states.csv'],
        'cities' => ['from' => '/json/cities.json', 'to' => '/csv/cities.csv'],
        'regions' => ['from' => '/json/regions.json', 'to' => '/csv/regions.csv'],
        'subregions' => ['from' => '/json/subregions.json', 'to' => '/csv/subregions.csv'],
    ];

    private const TRANSLATION_FILES = [
        'countries' => ['from' => '/json/countries.json', 'place_type' => 'country'],
        'states' => ['from' => '/json/states.json', 'place_type' => 'state'],
        'cities' => ['from' => '/json/cities.json', 'place_type' => 'city'],
        'regions' => ['from' => '/json/regions.json', 'place_type' => 'region'],
        'subregions' => ['from' => '/json/subregions.json', 'place_type' => 'subregion'],
    ];

    private Filesystem $filesystem;

    public function __construct()
    {
        parent::__construct(self::$defaultName);
        $this->filesystem = new Filesystem();
    }

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to CSV format');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $rootDir = dirname(PATH_BASE);

        $io->title('Exporting CSV data to ' . $rootDir);

        try {
            foreach (self::FILES as $root => $v) {
                $io->section("Processing: $root");

                $jsonData = $this->filesystem->exists($rootDir . $v['from'])
                    ? file_get_contents($rootDir . $v['from'])
                    : throw new \RuntimeException("JSON file not found: {$v['from']}");

                $csc = json_decode($jsonData, true)
                    ?: throw new \RuntimeException("Invalid JSON in {$v['from']}");

                $fp = fopen($rootDir . $v['to'], 'w');

                // Set headings
                $headings = $csc[0];
                unset($headings['translations']);
                fputcsv($fp, array_keys($headings));

                // Write data
                foreach ($csc as $row) {
                    if (!empty($row['timezones'])) {
                        $row['timezones'] = json_encode($row['timezones']);
                        $row['timezones'] = preg_replace('/"/', "'", $row['timezones']);
                        $row['timezones'] = preg_replace("/'([a-zA-Z]+[a-zA-Z0-9_]*)':/", '$1:', $row['timezones']);
                    }
                    unset($row['translations']);
                    fputcsv($fp, $row);
                }

                fclose($fp);
                $io->success("Exported $root to CSV");
            }

            // Export translations
            $io->section("Processing: translations");
            $this->exportTranslations($rootDir, $io);

            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }

    private function exportTranslations(string $rootDir, SymfonyStyle $io): void
    {
        $translationsCsvPath = $rootDir . '/csv/translations.csv';
        $fp = fopen($translationsCsvPath, 'w');

        // Write CSV headers
        fputcsv($fp, ['place_id', 'place_type', 'language', 'translation']);

        // Process each file type that has translations
        foreach (self::TRANSLATION_FILES as $root => $config) {
            $jsonData = $this->filesystem->exists($rootDir . $config['from'])
                ? file_get_contents($rootDir . $config['from'])
                : throw new \RuntimeException("JSON file not found: {$config['from']}");

            $data = json_decode($jsonData, true)
                ?: throw new \RuntimeException("Invalid JSON in {$config['from']}");

            foreach ($data as $item) {
                if (isset($item['translations']) && is_array($item['translations'])) {
                    $placeId = $item['id'];
                    $placeType = $config['place_type'];

                    foreach ($item['translations'] as $language => $translation) {
                        fputcsv($fp, [$placeId, $placeType, $language, $translation]);
                    }
                }
            }
        }

        fclose($fp);
        $io->success("Exported translations to CSV");
    }
}
