<?php
require_once 'base.php';

$translationsJson = file_get_contents(__DIR__."/data/translations.json", true);
// print_r($translationsJson);
$translationsArray = json_decode($translationsJson, true);
// print_r($translationsArray);

echo '-------------------------------------'.PHP_EOL;
echo 'JSON Data Starts'.PHP_EOL;
echo '-------------------------------------'.PHP_EOL;
foreach($translationsArray as $trans) :
    echo $trans['name']." - ".$trans['alpha3Code'].PHP_EOL;
endforeach;
echo '-------------------------------------'.PHP_EOL;
echo 'JSON Data Ends'.PHP_EOL;
echo '-------------------------------------'.PHP_EOL;

updateCountryTable($translationsArray, $conn);

$conn->close();

function updateCountryTable($translationsArray, $conn) {
	echo '-------------------------------------'.PHP_EOL;
	echo 'Records Check Starts'.PHP_EOL;
	echo '-------------------------------------'.PHP_EOL;

    foreach($translationsArray as $trans) :

        echo 'Checking For : '.$trans['name']." ".$trans['alpha3Code'].PHP_EOL;

        $sql = "SELECT id FROM countries WHERE iso3='".$trans['alpha3Code']."'";
        $result = $conn->query($sql);

        if ($result->num_rows > 0) { // If Found Update It
            echo 'Found... Updating...'.PHP_EOL;
            while($row = $result->fetch_assoc()) {
                $sql = "UPDATE countries SET translations='".json_encode($trans['translations'], JSON_UNESCAPED_UNICODE)."' WHERE id=".$row['id'];
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
