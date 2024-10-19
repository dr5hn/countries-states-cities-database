<?php

// Require Array2XML class which takes a PHP array and changes it to XML
require_once 'vendor/base.php';

use Spatie\ArrayToXml\ArrayToXml;

$rootDir = dirname(dirname(__FILE__));
$files = array(
    'regions' => array(
        'from' => '/json/regions.json',
        'to' => '/xml/regions.xml',
        'singular' => 'region',
    ),
    'subregions' => array(
        'from' => '/json/subregions.json',
        'to' => '/xml/subregions.xml',
        'singular' => 'subregion',
    ),
    'countries' => array(
        'from' => '/json/countries.json',
        'to' => '/xml/countries.xml',
        'singular' => 'country',
    ),
    'states' => array(
        'from' => '/json/states.json',
        'to' => '/xml/states.xml',
        'singular' => 'state',
    ),
    'cities' => array(
        'from' => '/json/cities.json',
        'to' => '/xml/cities.xml',
        'singular' => 'city',
    )
);

foreach ($files as $root => $v) :
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

    echo 'XML Exported to ' . $rootDir . $v['to'] . PHP_EOL;
endforeach;
