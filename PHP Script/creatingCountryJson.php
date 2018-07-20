<?php
ini_set('display_errors',1);
ini_set('error_reporting',E_ALL);

$servername = "localhost";
$username = "root";
$password = "mysql";
$dbname = "test";

header('Content-type: text/plain');

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = "SELECT * FROM countries ORDER BY name";
$result = $conn->query($sql);
$countriesArray = array();
$i=0;
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        // Removing Unwanted Keys
        unset($row['is_published']);
        unset($row['updated_by']);
        unset($row['updated_on']);

        // Pushing it into Fresh Array
        $countriesArray[$i]['id'] = (int)$row['id'];
        $countriesArray[$i]['name'] = $row['name'];
        $countriesArray[$i]['iso3'] = $row['iso3'];
        $countriesArray[$i]['iso2'] = $row['iso2'];
        $countriesArray[$i]['country_code'] = $row['countrycode'];
        $countriesArray[$i]['phone_code'] = $row['phonecode'];
        $countriesArray[$i]['capital'] = $row['capital'];
        $countriesArray[$i]['currency'] = $row['currency'];

        $i++;
    }
} else {
    echo "0 results";
}

// Putting Array to JSON
$fp = fopen('data/countries.json', 'w');
fwrite($fp, json_encode($countriesArray, JSON_PRETTY_PRINT));
fclose($fp);

$conn->close();