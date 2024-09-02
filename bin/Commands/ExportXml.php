<?php


namespace bin\Commands;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Spatie\ArrayToXml\ArrayToXml;

class ExportXml extends Command
{
    protected static $defaultName = 'export:export-xml';

    protected function execute(InputInterface $input, OutputInterface $output)
    {

        $rootDir = PATH_BASE . '../..';
        $files = array(
            'regions' => array(
                'from' => '/regions.json',
                'to' => '/xml/regions.xml',
                'singular' => 'region',
            ),
            'subregions' => array(
                'from' => '/subregions.json',
                'to' => '/xml/subregions.xml',
                'singular' => 'subregion',
            ),
            'countries' => array(
                'from' => '/countries.json',
                'to' => '/xml/countries.xml',
                'singular' => 'country',
            ),
            'states' => array(
                'from' => '/states.json',
                'to' => '/xml/states.xml',
                'singular' => 'state',
            ),
            'cities' => array(
                'from' => '/cities.json',
                'to' => '/xml/cities.xml',
                'singular' => 'city',
            ),
            'states_cities' => array(
                'from' => '/states+cities.json',
                'to' => '/xml/states+cities.xml',
                'singular' => 'state_city',
            ),
            'countries_states' => array(
                'from' => '/countries+states.json',
                'to' => '/xml/countries+states.xml',
                'singular' => 'country_state',
            ),
            'countries_cities' => array(
                'from' => '/countries+cities.json',
                'to' => '/xml/countries+cities.xml',
                'singular' => 'country_city',
            ),
            'countries_states_cities' => array(
                'from' => '/countries+states+cities.json',
                'to' => '/xml/countries+states+cities.xml',
                'singular' => 'country_state_city',
            ),
        );

        foreach ($files as $root => $v) {
            // Gets JSON file
            $json = file_get_contents($rootDir . $v['from']);

            $csc = array($v['singular'] => json_decode($json, true));

            // Converts PHP Array to XML with the root element being 'root-element-here'
            $xml = ArrayToXml::convert(
                $csc,
                $root,
                false,
                'UTF-8',
                '1.0',
                ['formatOutput' => true]
            );

            $fp = fopen($rootDir . $v['to'], 'w'); // Writing XML to File
            fwrite($fp, $xml);
            fclose($fp);

            $output->writeln('XML Exported to ' . $rootDir . $v['to'] ) ;
        }

        return 1;

    }


}