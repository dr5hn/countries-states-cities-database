<?php
# https://symfony.com/doc/current/components/yaml.html#dump-support

require_once 'vendor/base.php';

use Symfony\Component\Yaml\Yaml;

$rootDir = dirname(dirname(__FILE__));
$files = array(
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

foreach ($files as $root => $v) :
    // Gets JSON file
    $json = file_get_contents($rootDir . $v['from']);

    $csc = array($v['singular'] => json_decode($json));

    // Converts PHP Array to YAML
    $yml = Yaml::dump($csc, 7, 2, Yaml::DUMP_OBJECT_AS_MAP);

    $fp = fopen($rootDir . $v['to'], 'w'); // Writing YAML to File
    fwrite($fp, $yml);
    fclose($fp);

    echo 'YAML Exported to ' . $rootDir . $v['to'] . PHP_EOL;
endforeach;
