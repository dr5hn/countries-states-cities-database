<?php
require_once 'base.php';

$countryCode = 'SA'; // India
$stateCode = '04';

// Step 1: Find Duplicates
$sql = "SELECT id, name, country_id, state_id FROM cities WHERE country_code='$countryCode' AND state_code='$stateCode' ORDER BY country_id, state_id, name";
$cities = $conn->query($sql);

// Grab the JSON File
$file_name = "data/cities/" . $countryCode . '_' . $stateCode . '.json';

$citiesJson = file_get_contents($file_name);
$citiesArray = json_decode($citiesJson, true);
$citynames = array_column($citiesArray, 'name');
print_r($citynames);

$ids = [];

if ($cities->num_rows > 0) {
    while ($city = $cities->fetch_assoc()) {
        $name = $city['name'];
        $key = array_search($name, $citynames);
        if ($key || $key === 0) {
            // echo $name . ' ' . $key . PHP_EOL;
        } else {
            echo $city['id'] . ' ' . $name . ' not found' . PHP_EOL;
            array_push($ids, $city['id']);
        }
    }

    echo implode(',', $ids);
}

$conn->close();
