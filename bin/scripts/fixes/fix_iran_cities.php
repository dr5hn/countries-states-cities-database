<?php
require_once 'base.php';

$iranProvinces = file_get_contents("data/IR_provinces.json");
$iranProArray = json_decode($iranProvinces, true);

$iranCities = file_get_contents("data/cities/IR_cities.json");
$iranCityArray = json_decode($iranCities, true);

foreach ($iranProArray as $pro) :
    $filterCities = array_filter($iranCityArray, function ($city) use ($pro) {
        return $city['province_id'] === $pro['id'];
        // return $city['province_id'] === $pro['id'] && $pro['og_id'] === 3936;
    });
    // print_r($filterCities);

    $state_id = $pro['og_id'];
    $state_code = $pro['og_code'];
    echo PHP_EOL . 'StateID: ' . $state_id . PHP_EOL;
    echo '-----------' . PHP_EOL;

    foreach ($filterCities as $city) :
        $name = $city['en_name'];
        $sqld = "SELECT id, name, wikiDataId FROM cities WHERE country_id=103 AND state_id=$state_id AND name='".$name."' ORDER BY id";

        echo 'Checking for: ' . $name . PHP_EOL;
        echo '-----------' . PHP_EOL;

        $cityResult = $conn->query($sqld);
        if ($cityResult->num_rows > 0) {
            // echo 'SQL: ' . $sqld . PHP_EOL;
            // echo 'Found Duplicate....' . PHP_EOL;
            // while ($cr = $cityResult->fetch_assoc()) {
                // Write what to do with duplicate
                // echo 'Duplicate Name & ID: ' . $cr["name"] . ' [' . $cr["id"] . ']' . ' [' . $cr["wikiDataId"] . ']' . PHP_EOL;
            // }
        } else {
            echo 'Not Found... Needs Creating...' . PHP_EOL;
            extract($city);
            $en_name = mysqli_real_escape_string($conn, $en_name);

            $sql = "INSERT INTO cities (name, state_id, state_code, country_id, country_code, latitude, longitude, created_at, wikiDataId) VALUES ('$en_name', '$state_id', '$state_code', '103', 'IR', '$latitude', '$longitude', NOW(), NULL)";
            echo 'SQL: ' . $sql . PHP_EOL;

            // if ($conn->query($sql) === TRUE) {
            //     echo "New record created successfully".PHP_EOL;
            // } else {
            //     echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
            // }
        }
    endforeach;
endforeach;
