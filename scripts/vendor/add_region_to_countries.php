<?php
require_once 'base.php';

$regionsJson = file_get_contents("data/regions.json");
// print_r($regionsJson);
$regionsArray = json_decode($regionsJson, true);
// print_r($countriesArray);

echo '-------------------------------------'.PHP_EOL;
echo 'JSON Data Starts'.PHP_EOL;
echo '-------------------------------------'.PHP_EOL;
foreach($regionsArray as $region) :
    echo $region['name']." - ".$region['alpha3Code'].PHP_EOL;
endforeach;
echo '-------------------------------------'.PHP_EOL;
echo 'JSON Data Ends'.PHP_EOL;
echo '-------------------------------------'.PHP_EOL;

updateCountryTable($regionsArray, $conn);

$conn->close();

function updateCountryTable($regionsArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($regionsArray as $region) :

        echo 'Checking For : '.$region['name']." ".$region['alpha3Code'].PHP_EOL;

        $sql = "SELECT id FROM countries WHERE iso3='".$region['alpha3Code']."'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) { // If Found Update It
            echo 'Found... Updating...'.PHP_EOL;
            while($row = $result->fetch_assoc()) {
                $sql = "UPDATE countries SET region='".$region['region']."',subregion='".$region['subregion']."' WHERE id=".$row['id'];
                if ($conn->query($sql) === TRUE) {
                    echo "Record updated successfully".PHP_EOL;
                } else {
                    echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                }
            }
        } else { // Else Insert it
            echo 'Not Found... Creating...'.PHP_EOL;

            extract($country);
            $name = mysqli_real_escape_string($conn,$name);
            $currency = $currencyCodes[0];

            // $sql = "INSERT INTO countries (name, iso2, currency, created_at, wikiDataId) VALUES ('$name', '$code', '$currency', NOW(), '$wikiDataId')";

            // if ($conn->query($sql) === TRUE) {
            //     echo "New record created successfully".PHP_EOL;
            // } else {
            //     echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
            // }
        }

        echo PHP_EOL;
    endforeach;

    echo '-------------------------------------'.PHP_EOL;
    echo 'Records Check Ends'.PHP_EOL;
    echo '-------------------------------------'.PHP_EOL;
}
