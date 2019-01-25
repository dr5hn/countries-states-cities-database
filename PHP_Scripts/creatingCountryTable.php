<?php
ini_set('display_errors',1);
ini_set('error_reporting',E_ALL);

$servername = "localhost";
$username = "root";
$password = "mysql";
$dbname = "world";

header('Content-type: text/plain');

$countriesJson = file_get_contents("data/countries.json");
$countriesArray = json_decode($countriesJson, true);
// print_r($countriesArray);

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = "SELECT * FROM countries ORDER BY name";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row

    echo '-------------------------------------'.PHP_EOL;
	echo 'DB Data Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;
    while($row = $result->fetch_assoc()) {
        echo $row['name'].PHP_EOL;
    }
    echo '-------------------------------------'.PHP_EOL;
	echo 'DB Data Ends'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

	echo '-------------------------------------'.PHP_EOL;
	echo 'JSON Data Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;
	foreach($countriesArray as $country) :
		echo $country['name']." - ".$country['iso3'].PHP_EOL;
	endforeach;
	echo '-------------------------------------'.PHP_EOL;
	echo 'JSON Data Ends'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

} else {
    echo "No Records Found..";
    echo PHP_EOL;
}

updateCountryTable($countriesArray, $conn);

$conn->close();

function updateCountryTable($countriesArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($countriesArray as $country) :

        echo 'Checking For : '.$country['name']." ".$country['iso3'].PHP_EOL;
        $capital = mysqli_real_escape_string($conn,$country['capital']);

		$sql = "SELECT id FROM countries WHERE iso3='".$country['iso3']."'";
		$result = $conn->query($sql);

		if ($result->num_rows > 0) { // If Found Update It
			echo 'Found... Updating...'.PHP_EOL;
			while($row = $result->fetch_assoc()) {
				$sql = "UPDATE countries SET countrycode=".$country['country_code'].", phonecode='".$country['phone_code']."', iso2='".$country['iso2']."', capital='".$capital."', currency='".$country['currency']."' WHERE id=".$row['id'];
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
            $capital = mysqli_real_escape_string($conn,$capital);

			$sql = "INSERT INTO countries (name, iso3, iso2, countrycode, phonecode, capital, currency, created_at) VALUES ('$name', '$iso3', '$iso2', $country_code, '$phone_code', '$capital','$currency', NOW())";

			if ($conn->query($sql) === TRUE) {
			    echo "New record created successfully".PHP_EOL;
			} else {
			    echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
			}
		}

		echo PHP_EOL;
	endforeach;

	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Ends'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;
}
?>