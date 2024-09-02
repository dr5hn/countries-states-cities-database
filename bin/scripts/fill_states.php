<?php
require_once 'base.php';

$countriesJson = file_get_contents("data/countries.json");
$countriesArray = json_decode($countriesJson, true);

foreach($countriesArray as $country) :
    $country_code = $country['code'];
    $file_name = $country_code.'.json';
    echo '-------------------------------------'.PHP_EOL;
    echo 'Records Check Starts for '.$file_name.PHP_EOL;
    echo '-------------------------------------'.PHP_EOL;
    $statesJson = file_get_contents("data/states/".$file_name);
    $statesArray = json_decode($statesJson, true);

    $sql = "SELECT id FROM countries WHERE iso2='".$country_code."' LIMIT 1";
    $result = $conn->query($sql) or die($conn->error);
    echo "number of rows: " . $result->num_rows.PHP_EOL;
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $country_id = $row['id'];

            if (!empty($statesArray)) :
                foreach($statesArray as $state) :
                    echo 'Checking For : '.$state['name'].PHP_EOL;
                    $state_name = mysqli_real_escape_string($conn,$state['name']);
                    $sql = "SELECT id FROM states WHERE country_id=".$country_id." AND name='".$state_name."'";
                    $result = $conn->query($sql);

                    if (!empty($result) && $result->num_rows > 0) { // If Found Update It
                        echo 'Found... Updating...'.PHP_EOL;
                        while($row = $result->fetch_assoc()) {

                            $sql = "UPDATE states SET name='".$state_name."' WHERE id=".$row['id'];
                            if ($conn->query($sql) === TRUE) {
                                echo "Record updated successfully".PHP_EOL;
                            } else {
                                echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                            }
                        }
                    } else { // Else Insert it
                        echo 'Not Found... Creating...'.PHP_EOL;
                        extract($state);
                        $name = mysqli_real_escape_string($conn,$name);
                        $sql = "INSERT INTO states (name, fips_code, iso2, country_id, country_code, created_at, wikiDataId) VALUES ('$name', '$fipsCode', '$isoCode', '$country_id', '$country_code', NOW(), '$wikiDataId')";

                        if ($conn->query($sql) === TRUE) {
                            echo "New record created successfully".PHP_EOL;
                        } else {
                            echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
                        }
                    }

                    echo PHP_EOL;
                endforeach;
            else:
                echo 'State '.$file_name.' is Empty'.PHP_EOL;
            endif;
        }
    }
endforeach;

$conn->close();
