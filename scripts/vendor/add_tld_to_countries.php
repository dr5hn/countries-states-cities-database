<?php
require_once 'base.php';

$tldJson = file_get_contents("data/tld.json");
// print_r($tldJson);
$tldArray = json_decode($tldJson, true);
// print_r($tldArray);

updateCountryTable($tldArray, $conn);

$conn->close();

function updateCountryTable($tldArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($tldArray as $tld) :

        echo 'Checking For : '.$tld['name']." ".$tld['alpha3Code'].PHP_EOL;

        $sql = "SELECT id FROM countries WHERE iso3='".$tld['alpha3Code']."'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) { // If Found Update It
            echo 'Found... Updating...'.PHP_EOL;
            while($row = $result->fetch_assoc()) {
                $sql = "UPDATE countries SET tld='".$tld['topLevelDomain'][0]."' WHERE id=".$row['id'];
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
