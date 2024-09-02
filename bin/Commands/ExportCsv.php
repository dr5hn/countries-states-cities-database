<?php


namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;

class ExportCsv extends Command
{
    protected static $defaultName = 'export:export-csv';

    protected function execute(InputInterface $input, OutputInterface $output)
    {

        $rootDir = PATH_BASE . '../..';

        $files = array(
            'countries' => array(
                'from' => '/countries.json',
                'to' => '/csv/countries.csv',
            ),
            'states' => array(
                'from' => '/states.json',
                'to' => '/csv/states.csv',
            ),
            'cities' => array(
                'from' => '/cities.json',
                'to' => '/csv/cities.csv',
            ),
            'regions' => array(
                'from' => '/regions.json',
                'to' => '/csv/regions.csv',
            ),
            'subregions' => array(
                'from' => '/subregions.json',
                'to' => '/csv/subregions.csv',
            ),
        );

        foreach ($files as $root => $v) {
            // Gets JSON file
            $json = file_get_contents($rootDir . $v['from']);

            $csc = json_decode($json, true);

            $fp = fopen($rootDir . $v['to'], 'w'); // Putting Array to XML

            // Set headings
            $headings = $csc[0];

            // No translations please.
            unset($headings['translations']);
            fputcsv($fp, array_keys($headings));

            // Loop through the associative array.
            foreach ($csc as $row) {
                // Update timezones to make readable
                if (!empty($row['timezones'])) {
                    $row['timezones'] = json_encode($row['timezones']);
                    $row['timezones'] = preg_replace('/"/', "'", $row['timezones']);
                    $row['timezones'] = preg_replace("/'([a-zA-Z]+[a-zA-Z0-9_]*)':/", '$1:', $row['timezones']);
                }

                // No translations please.
                unset($row['translations']);

                // Write the row to the CSV file.
                fputcsv($fp, $row);
            };

            fclose($fp);

            $output->writeln( 'CSV Exported to ' . $rootDir . $v['to'] );
        }

        return 1;
    }

}