<?php
require_once 'base.php';

$latlongJson = file_get_contents("data/latlong_countries.json");
// print_r($latlongJson);
$latlongArray = json_decode($latlongJson, true);
// print_r($latlongArray);

// echo '-------------------------------------'.PHP_EOL;
// echo 'JSON Data Starts'.PHP_EOL;
// echo '-------------------------------------'.PHP_EOL;
// foreach($latlongArray as $latlong) :
//     echo $latlong['name']." - ".$latlong['iso3'].PHP_EOL;
// endforeach;
// echo '-------------------------------------'.PHP_EOL;
// echo 'JSON Data Ends'.PHP_EOL;
// echo '-------------------------------------'.PHP_EOL;

updateCountryTable($latlongArray, $conn);

$conn->close();

function updateCountryTable($latlongArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($latlongArray as $latlong) :
        echo 'Checking For : '.$latlong['name']." ".$latlong['iso3'].PHP_EOL;

        $sql = "SELECT id FROM countries WHERE iso3='".$latlong['iso3']."'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) { // If Found Update It
            echo 'Found... Updating...'.PHP_EOL;
            while($row = $result->fetch_assoc()) {
                $sql = "UPDATE countries SET latitude='".$latlong['latitude']."',longitude='".$latlong['longitude']."' WHERE id=".$row['id'];
                if ($conn->query($sql) === TRUE) {
                    echo "Record updated successfully".PHP_EOL;
                } else {
                    echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                }
            }
        }

        echo PHP_EOL;
    endforeach;

    echo '-------------------------------------'.PHP_EOL;
    echo 'Records Check Ends'.PHP_EOL;
    echo '-------------------------------------'.PHP_EOL;
}
