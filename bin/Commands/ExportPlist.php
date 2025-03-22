<?php

namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Console\Style\SymfonyStyle;

class ExportPlist extends Command
{
    protected static $defaultName = 'export:plist';
    protected static $defaultDescription = 'Export data to PLIST format';

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to PLIST format using Python script');
    }

    public function __construct()
    {
        parent::__construct(self::$defaultName);
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $rootDir = dirname(PATH_BASE);

        $io = new SymfonyStyle($input, $output);
        $io->title('Exporting PLIST data to ' . $rootDir);

        // Using Symfony Process component for better process handling
        $process = new Process(['python3', $rootDir . '/bin/export_plist.py']);
        $process->setTimeout(3600); // 1 hour timeout for large datasets

        try {
            $process->mustRun(function ($type, $buffer) use ($output) {
                if (Process::ERR === $type) {
                    $output->writeln("<error>$buffer</error>");
                } else {
                    $output->writeln($buffer);
                }
            });

            return Command::SUCCESS;
        } catch (ProcessFailedException $exception) {
            $output->writeln("<error>Failed to execute Python script: {$exception->getMessage()}</error>");
            return Command::FAILURE;
        }
    }
}
