<?php
require_once 'vendor/base.php';

$i = 0;
$j = 0;
$k = 0;

$countriesArray = array();
$statesArray = array();
$citiesArray = array();

$rootDir = dirname(dirname(__FILE__));

// Fetching All Countries
$sql = "SELECT * FROM countries";
$result = $conn->query($sql);
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        // Pushing it into Fresh Array
        $countriesArray[$i]['isoCode'] = $row['iso2'];
        $countriesArray[$i]['name'] = $row['name'];
        $countriesArray[$i]['phonecode'] = $row['phonecode'];
        $countriesArray[$i]['flag'] = $row['emoji'];
        $countriesArray[$i]['currency'] = $row['currency'];
        $countriesArray[$i]['latitude'] = $row['latitude'];
        $countriesArray[$i]['longitude'] = $row['longitude'];
        $countriesArray[$i]['timezones'] = json_decode($row['timezones'], true);

        $i++;
    }
}

// Fetching all States
$sql = "SELECT * FROM states";
$result = $conn->query($sql);
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        // Pushing it into Fresh Array
        $statesArray[$j]['name'] = $row['name'];
        $statesArray[$j]['isoCode'] = $row['iso2'];
        $statesArray[$j]['countryCode'] = $row['country_code'];
        $statesArray[$j]['latitude'] = $row['latitude'];
        $statesArray[$j]['longitude'] = $row['longitude'];

        $j++;
    }
}

// Fetching all Cities
$sql = "SELECT * FROM cities";
$result = $conn->query($sql);
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        // Pushing it into Fresh Array
        $citiesArray[$k]['name'] = $row['name'];
        $citiesArray[$k]['countryCode'] = $row['country_code'];
        $citiesArray[$k]['stateCode'] = $row['state_code'];
        $citiesArray[$k]['latitude'] = $row['latitude'];
        $citiesArray[$k]['longitude'] = $row['longitude'];

        $k++;
    }
}

echo 'Total Countries Count : '.count($countriesArray).PHP_EOL;
echo 'Total States Count : '.count($statesArray).PHP_EOL;
echo 'Total Cities Count : '.count($citiesArray).PHP_EOL;

// print_r($countriesArray);
$exportTo = $rootDir . '/csc/country.json';
$fp = fopen($exportTo, 'w'); // Putting Array to JSON
fwrite($fp, json_encode($countriesArray,  JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($statesArray);
$exportTo = $rootDir . '/csc/state.json';
$fp = fopen($exportTo, 'w'); // Putting Array to JSON
fwrite($fp, json_encode($statesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($citiesArray);
$exportTo = $rootDir . '/csc/city.json';
$fp = fopen($exportTo, 'w'); // Putting Array to JSON
fwrite($fp, json_encode($citiesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

$conn->close();
