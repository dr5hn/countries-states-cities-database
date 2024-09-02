<?php
require_once '../base.php';

$spainProvinces = file_get_contents(__DIR__ . '/../data/ES_provinces.json');
$spainProArray = json_decode($spainProvinces, true);

$spainCities = file_get_contents(__DIR__ . '/../data/cities/ES_cities.json');
$spainCityArray = json_decode($spainCities, true);
// print_r($spainCityArray);
// die();

foreach ($spainProArray as $pro) :
    $filterCities = array_filter($spainCityArray, function ($city) use ($pro) {
        // return $city['province_id'] === $pro['id'];
        return $city['province_id'] === $pro['id'] && $pro['id'] === 35;
    });
    // print_r($filterCities);

    if (!empty($filterCities)) {
        foreach ($filterCities as $city) :
            $name = $city['name'];
            $new_state_id = 1158;
            $new_state_code = 'M';
            echo PHP_EOL . 'Checking for: ' . $name . PHP_EOL;
            echo '-----------' . PHP_EOL;
            $sqld = "SELECT id, name, state_id FROM cities WHERE country_id=207 AND name='" . $name . "' ORDER BY state_id";
            $cityResult = $conn->query($sqld);
            if ($cityResult->num_rows > 0) {
                while ($cr = $cityResult->fetch_assoc()) {
                    // Write what to do with duplicate
                    echo 'Found Name & ID: ' . $cr["name"] . ' [' . $cr["id"] . ']' . ' [' . $cr["state_id"] . ']' . PHP_EOL;
                    // if ($cr['state_id'] == 5108) {
                        $sql = "UPDATE cities SET state_id=$new_state_id, state_code='$new_state_code' WHERE id=" . $cr['id'];
                        echo 'SQL U: ' . $sql . PHP_EOL;
                        // if ($conn->query($sql) === TRUE) {
                        //     echo "Record updated successfully" . PHP_EOL;
                        // } else {
                        //     echo "Error updating record: " . $sql . " " . $conn->error . PHP_EOL;
                        // }
                    // }
                }
            } else {
                echo 'Not found' . PHP_EOL;
                $name = mysqli_real_escape_string($conn, $name);
                $sql = "INSERT INTO cities (name, state_id, state_code, country_id, country_code, latitude, longitude, created_at, wikiDataId) VALUES ('$name', $new_state_id, '$new_state_code', 207, 'ES', '0.0', '0.0', NOW(), NULL)";
                echo 'SQL C: ' . $sql . PHP_EOL;

                // if ($conn->query($sql) === TRUE) {
                //     echo "New record created successfully" . PHP_EOL;
                // } else {
                //     echo "Error: " . $sql . " " . $conn->error . PHP_EOL;
                // }
            }
        endforeach;
    }
endforeach;
