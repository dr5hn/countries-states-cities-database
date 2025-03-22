<?php

namespace bin\Commands;

use bin\Support\Config;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Filesystem\Filesystem;

class ExportCscNpm extends Command
{
    protected static $defaultName = 'export:csc-npm';
    protected static $defaultDescription = 'Export data for NPM package format';

    private Filesystem $filesystem;

    public function __construct()
    {
        parent::__construct(self::$defaultName);
        $this->filesystem = new Filesystem();
    }

    protected function configure(): void
    {
        $this->setHelp('This command exports the database in NPM package format');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $db = Config::getConfig()->getDB();
        $rootDir = dirname(PATH_BASE);

        $io->title('Exporting NPM package data to ' . $rootDir);

        try {
            $cscDir = $rootDir . '/csc';
            $this->filesystem->mkdir($cscDir, 0755);

            // Reference to ExportCscNpm.php lines 24-80 for data fetching logic

            foreach (['country', 'state', 'city'] as $type) {
                $arrayName = "{$type}Array";
                $exportTo = "$cscDir/$type.json";

                $this->filesystem->dumpFile(
                    $exportTo,
                    json_encode($$arrayName, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL
                );

                $io->success("Exported $type to $exportTo");
            }

            $db->close();
            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }
}
