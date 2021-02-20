<?php
require_once 'base.php';

$countryId = 101; // India

// Step 1: Find Duplicates
$sql = "SELECT name, country_id, state_id FROM cities WHERE country_id=$countryId ORDER BY country_id, state_id, name";
$cities = $conn->query($sql);

if ($cities->num_rows > 0) {
    while ($city = $cities->fetch_assoc()) {
        $countryId = (int)$city['country_id'];
        $stateId = (int)$city['state_id'];
        // $name = $city['name'];
        $name = implode('%', str_split($city['name']));
        $sqld = "SELECT id, name FROM cities WHERE country_id=$countryId AND state_id=$stateId AND name LIKE '".$name."' ORDER BY id";
        $cityResult = $conn->query($sqld);
        if ($cityResult->num_rows > 1) {
            echo 'Checking for: '.$city['name'].PHP_EOL;
            echo '-----------'.PHP_EOL;
            echo 'SQL: '.$sqld.PHP_EOL;
            echo 'Found Duplicate....'.PHP_EOL;
            while ($cr = $cityResult->fetch_assoc()) {
                // Write what to do with duplicate
                echo 'Duplicate Name & ID: '.$cr["name"].' ['.$cr["id"].']'.PHP_EOL;
            }
            echo ''.PHP_EOL.PHP_EOL;
        }
    }
}

$conn->close();
