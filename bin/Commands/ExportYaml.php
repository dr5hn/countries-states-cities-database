<?php

namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Filesystem\Filesystem;
use Symfony\Component\Yaml\Yaml;

class ExportYaml extends Command
{
    protected static $defaultName = 'export:yaml';
    protected static $defaultDescription = 'Export data to YAML format';

    private const FILES = [
        'regions' => ['from' => '/json/regions.json', 'to' => '/yml/regions.yml', 'singular' => 'region'],
        'subregions' => ['from' => '/json/subregions.json', 'to' => '/yml/subregions.yml', 'singular' => 'subregion'],
        'countries' => ['from' => '/json/countries.json', 'to' => '/yml/countries.yml', 'singular' => 'country'],
        'states' => ['from' => '/json/states.json', 'to' => '/yml/states.yml', 'singular' => 'state'],
        'cities' => ['from' => '/json/cities.json', 'to' => '/yml/cities.yml', 'singular' => 'city'],
    ];

    private Filesystem $filesystem;

    public function __construct()
    {
        parent::__construct(self::$defaultName);
        $this->filesystem = new Filesystem();
    }

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to YAML format');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $rootDir = dirname(PATH_BASE);

        $io->title('Exporting YAML data to ' . $rootDir);

        try {
            foreach (self::FILES as $root => $config) {
                $io->section("Processing: $root");

                $jsonData = $this->filesystem->exists($rootDir . $config['from'])
                    ? file_get_contents($rootDir . $config['from'])
                    : throw new \RuntimeException("JSON file not found: {$config['from']}");

                $data = json_decode($jsonData, true)
                    ?: throw new \RuntimeException("Invalid JSON in {$config['from']}");

                $yaml = Yaml::dump(
                    [$config['singular'] => $data],
                    7,
                    2,
                    Yaml::DUMP_OBJECT_AS_MAP
                );

                $this->filesystem->dumpFile($rootDir . $config['to'], $yaml);
                $io->success("Exported to {$config['to']}");
            }

            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }
}
