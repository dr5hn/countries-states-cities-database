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

            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }
}
