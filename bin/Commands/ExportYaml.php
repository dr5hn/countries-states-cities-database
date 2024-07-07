<?php


namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Yaml\Yaml;

class ExportYaml  extends Command
{
    protected static $defaultName = 'export:export-yaml';

    protected function execute(InputInterface $input, OutputInterface $output)
    {

        $rootDir = PATH_BASE . '../..';

        $files = array(
            'regions' => array(
                'from' => '/regions.json',
                'to' => '/yml/regions.yml',
                'singular' => 'region',
            ),
            'subregions' => array(
                'from' => '/subregions.json',
                'to' => '/yml/subregions.yml',
                'singular' => 'subregion',
            ),
            'countries' => array(
                'from' => '/countries.json',
                'to' => '/yml/countries.yml',
                'singular' => 'country',
            ),
            'states' => array(
                'from' => '/states.json',
                'to' => '/yml/states.yml',
                'singular' => 'state',
            ),
            'cities' => array(
                'from' => '/cities.json',
                'to' => '/yml/cities.yml',
                'singular' => 'city',
            ),
            'states_cities' => array(
                'from' => '/states+cities.json',
                'to' => '/yml/states+cities.yml',
                'singular' => 'state_city',
            ),
            'countries_states' => array(
                'from' => '/countries+states.json',
                'to' => '/yml/countries+states.yml',
                'singular' => 'country_state',
            ),
            'countries_cities' => array(
                'from' => '/countries+cities.json',
                'to' => '/yml/countries+cities.yml',
                'singular' => 'country_city',
            ),
            'countries_states_cities' => array(
                'from' => '/countries+states+cities.json',
                'to' => '/yml/countries+states+cities.yml',
                'singular' => 'country_state_city',
            ),
        );

        foreach ($files as $root => $v) {
            $json = file_get_contents($rootDir . $v['from']);

            $csc = array($v['singular'] => json_decode($json));

            // Converts PHP Array to YAML
            $yml = Yaml::dump($csc, 7, 2, Yaml::DUMP_OBJECT_AS_MAP);

            $fp = fopen($rootDir . $v['to'], 'w'); // Writing YAML to File
            fwrite($fp, $yml);
            fclose($fp);

            $output->writeln( 'YAML Exported to ' . $rootDir . $v['to'] );
        }

        return 1;
    }
}