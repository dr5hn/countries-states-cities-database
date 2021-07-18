<?php
require_once 'base.php';

$country_code = 'CL';
$region_code = 'RM';

$file_name = $country_code.'_'.$region_code.'.json';
$citiesJson = file_get_contents("data/cities/".$file_name);
$citiesArray = json_decode($citiesJson, true);

if (!empty($citiesArray)) :
    foreach($citiesArray as $city) :
        echo '-------------------------------------'.PHP_EOL;
        echo 'Records Check Starts for '.$file_name.PHP_EOL;
        echo '-------------------------------------'.PHP_EOL;

        # Fetch State
        $sql = "SELECT id, country_id FROM states WHERE country_code='".$country_code."'AND iso2='".$region_code."' LIMIT 1";
        $result = $conn->query($sql) or die($conn->error);
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $region_id = $row['id'];
                $country_id = $row['country_id'];
                $city_name = $city['name'];
                $wikiDataId = $city['wikiDataId'];

                echo 'Checking For : '.$city_name.PHP_EOL;
                echo 'Checking For : '.$city['wikiDataId'].PHP_EOL;
                $city_name = mysqli_real_escape_string($conn, $city_name);

                $sql = "SELECT id, name, wikiDataId FROM cities WHERE state_id=".$region_id." AND country_id=".$country_id." AND name='".$city_name."';";
                // if ($wikiDataId) {
                //     $sql = "SELECT id, name FROM cities WHERE state_id=".$region_id." AND country_id=".$country_id." AND wikiDataId='".$wikiDataId."';";
                // }

                echo $sql.PHP_EOL;
                $result = $conn->query($sql) or die($conn->error);

                if ($result->num_rows > 0) { // If Found Update It
                    while($row = $result->fetch_assoc()) {
                        if (strlen($row['name']) == strlen($city_name) && $row['name'] == $city['name']) {
                            echo 'Name - No Difference..'.PHP_EOL;
                        } else if (ord($row['name']) != ord($city_name)) {
                            echo 'Found difference in name (new)'.$city['name'].' -- (old)'.$row['name'].PHP_EOL;
                            // echo 'Fixing Name...'.PHP_EOL;
                            // $sql = "UPDATE cities SET name='".$city['name']."' WHERE id=".$row['id'];
                            // if ($conn->query($sql) === TRUE) {
                            //     echo "Record updated successfully".PHP_EOL;
                            // } else {
                            //     echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                            // }
                        } else {
                            echo 'No Difference..'.PHP_EOL;
                        }

                        // Fix Duplicate Wiki Data ID Issue
                        if ($row['wikiDataId'] != $wikiDataId) {
                            echo 'Found difference in WikiDataId (new)'.$city['wikiDataId'].' -- (old)'.$row['wikiDataId'].PHP_EOL;
                            // echo 'Fixing WikiDataId...'.PHP_EOL;
                            // $sql = "UPDATE cities SET wikiDataId='".$city['wikiDataId']."' WHERE id=".$row['id'];
                            // if ($conn->query($sql) === TRUE) {
                            //     echo "Record updated successfully".PHP_EOL;
                            // } else {
                            //     echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                            // }
                        }
                    }
                } else { // Else Insert it
                    echo 'Not Found... Creating...'.PHP_EOL;
                    extract($city);
                    $name = mysqli_real_escape_string($conn, $name);

                    if ($wikiDataId) {
                        // $sql = "INSERT INTO cities (name, state_id, state_code, country_id, country_code, latitude, longitude, created_at, wikiDataId) VALUES ('$name', '$region_id', '$region_code', '$country_id', '$country_code', '$latitude', '$longitude', NOW(), '$wikiDataId')";

                        // if ($conn->query($sql) === TRUE) {
                        //     echo "New record created successfully".PHP_EOL;
                        // } else {
                        //     echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
                        // }
                    } else {
                        echo 'No WikiData ID Found...'.PHP_EOL;
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
