<?php
ini_set('display_errors',1);
ini_set('error_reporting',E_ALL);

$servername = "localhost";
$username = "root";
$password = "mysql";
$dbname = "world";

header('Content-type: text/plain');

$citiesJson = file_get_contents("data/us-cities.json");
$citiesArray = json_decode($citiesJson, true);

// print_r($citiesArray);
// die();

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = "SELECT * FROM cities ORDER BY name";
$result = $conn->query($sql);

updateCityTable($citiesArray, $conn);

$conn->close();

function updateCityTable($citiesArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($citiesArray as $k => $v) :

        // Checking if State Exists, IF Not Creating It
        $sql = "SELECT id, country_id FROM states WHERE country_id=233 AND name='".$k."'";
        $result = $conn->query($sql);
        
        if ($result->num_rows > 0) { // If Found Update It
			echo $k.' State Found... No Need to Update...'.PHP_EOL;
			while($row = $result->fetch_assoc()) {
                
                // print_r($row);
                extract($row);

                // Looping Through Each City for Insertion
                foreach($v as $city) :

                    // Checking if Cities Exists, IF Not Creating It
                    $sql = "SELECT * FROM cities WHERE state_id='$id' AND country_id='$country_id' AND name='ucwords(strtolower($city))'";
                    $result = $conn->query($sql);

                    if ($result->num_rows > 0) { // If Found Update It
                        echo ucwords(strtolower($city)).' City Found... Updating...'.PHP_EOL;
			            while($row = $result->fetch_assoc()) {
                            $city_name = ucwords(strtolower($city));
                            $sql = "UPDATE cities SET name='$city_name' WHERE id=".$row['id'];
                            if ($conn->query($sql) === TRUE) {
                                echo "Record updated successfully".PHP_EOL;
                            } else {
                                echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
                            }
                        }
                    } else {
                        echo ucwords(strtolower($city)).' City Not Found... Creating...'.PHP_EOL;
                        $city = mysqli_real_escape_string($conn,ucwords(strtolower($city)));
                        $sql = "INSERT INTO cities (name, country_id, state_id, created_at) VALUES ('$city', '$country_id', '$id', NOW())";

                        if ($conn->query($sql) === TRUE) {
                            echo "New record created successfully".PHP_EOL;
                        } else {
                            echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
                        }
                    }
                endforeach;
            }
        } else {
            echo $k.' State Not Found... Creating...'.PHP_EOL;
            $k = mysqli_real_escape_string($conn,$k);
			$sql = "INSERT INTO states (name, country_id, created_at) VALUES ('$k', 233, NOW())";

			if ($conn->query($sql) === TRUE) {
			    echo "New record created successfully".PHP_EOL;
			} else {
			    echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
			}
        }
		
	endforeach;

	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Ends'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;
}
?>