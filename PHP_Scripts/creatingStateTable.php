<?php
ini_set('display_errors',1);
ini_set('error_reporting',E_ALL);

$servername = "localhost";
$username = "root";
$password = "mysql";
$dbname = "world";

header('Content-type: text/plain');

$statesJson = file_get_contents("data/states.json");
$statesArray = json_decode($statesJson, true);
// print_r($statesArray);

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = "SELECT * FROM states ORDER BY name";
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
	foreach($statesArray as $state) :
		echo $state['name'].PHP_EOL;
	endforeach;
	echo '-------------------------------------'.PHP_EOL;
	echo 'JSON Data Ends'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

} else {
    echo "No Records Found..";
    echo PHP_EOL;
}

updateStateTable($statesArray, $conn);

$conn->close();

function updateStateTable($statesArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($statesArray as $state) :

		echo 'Checking For : '.$state['name'].PHP_EOL;

		$sql = "SELECT id FROM states WHERE country_id=".$state['country_id']." AND name='".$state['name']."'";
		$result = $conn->query($sql);

		if ($result->num_rows > 0) { // If Found Update It
			echo 'Found... Updating...'.PHP_EOL;
			while($row = $result->fetch_assoc()) {
				$sql = "UPDATE states SET name=".$state['name']." WHERE id=".$row['id'];
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
			$sql = "INSERT INTO states (name, country_id, created_at) VALUES ('$name', '$country_id', NOW())";

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