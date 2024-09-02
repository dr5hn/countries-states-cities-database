<?php
require_once 'base.php';

$numericJson = file_get_contents(__DIR__."/data/numeric_codes.json", true);
// print_r($numericJson);
$numericArray = json_decode($numericJson, true);
// print_r($numericArray);

updateCountryTable($numericArray, $conn);

$conn->close();

function updateCountryTable($numericArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($numericArray as $code) :

        echo 'Checking For : '.$code['name']." ".$code['iso3'].PHP_EOL;

        $sql = "SELECT id FROM countries WHERE iso3='".$code['iso3']."'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) { // If Found Update It
            echo 'Found... Updating...'.PHP_EOL;
            while($row = $result->fetch_assoc()) {
                $sql = "UPDATE countries SET numeric_code='".$code['numericCode']."' WHERE id=".$row['id'];
                if ($conn->query($sql) === TRUE) {
                    echo "Record updated successfully".PHP_EOL;
                } else {
                    echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                }
            }
        } else { // Else Insert it
            echo 'Not Found... Creating...'.PHP_EOL;
        }

        echo PHP_EOL;
    endforeach;

    echo '-------------------------------------'.PHP_EOL;
    echo 'Records Check Ends'.PHP_EOL;
    echo '-------------------------------------'.PHP_EOL;
}
