<?php

// Require Array2XML class which takes a PHP array and changes it to XML
require_once 'vendor/base.php';

$rootDir = dirname(dirname(__FILE__));
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
);

foreach ($files as $root => $v) :
    // Gets JSON file
    $json = file_get_contents($rootDir . $v['from']);

    $csc = json_decode($json, true);

    $fp = fopen($rootDir . $v['to'], 'w'); // Putting Array to XML

    // Loop through the associative array.
    fputcsv($fp, array_keys($csc[0]));
    foreach ($csc as $row) :
        // Write the row to the CSV file.
        if(is_array($row['timezones'])) {
            $row['timezones'] = json_encode($row['timezones']);
            $row['timezones'] = preg_replace('/"/', "'", $row['timezones']);
            $row['timezones'] = preg_replace("/'([a-zA-Z]+[a-zA-Z0-9_]*)':/", '$1:', $row['timezones']);
        }
        fputcsv($fp, $row);
    endforeach;

    fclose($fp);

    echo 'CSV Exported to ' . $rootDir . $v['to'] . PHP_EOL;
endforeach;
