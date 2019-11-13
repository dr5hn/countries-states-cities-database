<?php
ini_set('display_errors',1);
ini_set('error_reporting',E_ALL);

$servername = "127.0.0.1";
$username = "root";
$password = "mysql";
$dbname = "world";

header('Content-type: text/plain');

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$file_name = 'ohio.json';
$citiesJson = file_get_contents("data/cities/".$file_name);
$citiesArray = json_decode($citiesJson, true);

if (!empty($citiesArray)) :
    foreach($citiesArray as $city) :
        echo '-------------------------------------'.PHP_EOL;
        echo 'Records Check Starts for '.$file_name.PHP_EOL;
        echo '-------------------------------------'.PHP_EOL;
        $country_code = $city['countryCode'];
        $region_code = $city['regionCode'];

        # Fetch State
        $sql = "SELECT id, country_id FROM states WHERE country_code='".$country_code."'AND iso2='".$region_code."' LIMIT 1";
        $result = $conn->query($sql) or die($conn->error);
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $region_id = $row['id'];
                $country_id = $row['country_id'];
                $city_name = $city['name'];

                echo 'Checking For : '.$city_name.PHP_EOL;
                $city_name = mysqli_real_escape_string($conn, $city_name);
                $sql = "SELECT id FROM cities WHERE state_id=".$region_id." AND country_id=".$country_id." AND name='".$city_name."'";
                $result = $conn->query($sql) or die($conn->error);

                if ($result->num_rows > 0) { // If Found Update It
                    echo 'Found... Updating...'.PHP_EOL;
                    while($row = $result->fetch_assoc()) {
                        $sql = "UPDATE cities SET name='".$city_name."' WHERE id=".$row['id'];
                        if ($conn->query($sql) === TRUE) {
                            echo "Record updated successfully".PHP_EOL;
                        } else {
                            echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                        }
                    }
                } else { // Else Insert it
                    echo 'Not Found... Creating...'.PHP_EOL;
                    extract($city);
                    $name = mysqli_real_escape_string($conn, $name);
                    $sql = "INSERT INTO cities (name, state_id, state_code, country_id, country_code, latitude, longitude, created_at, wikiDataId) VALUES ('$name', '$region_id', '$region_code', '$country_id', '$country_code', '$latitude', '$longitude', NOW(), '$wikiDataId')";

                    if ($conn->query($sql) === TRUE) {
                        echo "New record created successfully".PHP_EOL;
                    } else {
                        echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
                    }
                }

                echo PHP_EOL;
            }
        }
    endforeach;
else:
    echo 'City '.$file_name.' is Empty'.PHP_EOL;
endif;

$conn->close();
