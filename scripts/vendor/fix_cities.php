<?php
require_once 'base.php';

$citiesJson = file_get_contents("../../cities.json");
$citiesArray = json_decode($citiesJson, true);

if (!empty($citiesArray)) :
    foreach($citiesArray as $city) :
        $city_name = mysqli_real_escape_string($conn, $city['name']);
        $sql = "UPDATE cities SET name='".$city_name."' WHERE id=".$city['id'];
        if ($conn->query($sql) === TRUE) {
            echo "Record updated successfully".PHP_EOL;
        } else {
            echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
        }
    endforeach;
endif;
