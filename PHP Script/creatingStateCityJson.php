<?php
ini_set('display_errors',1);
ini_set('error_reporting',E_ALL);
header('Content-type: text/plain');
date_default_timezone_set('Asia/Kolkata');

$servername = "localhost";
$username = "root";
$password = "mysql";
$dbname = "test"; // Database Name

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$i = 0;
$j = 0;
$k = 0;
$l = 0;

$statesArray = array();
$citiesArray = array();
$stateCityArray = array();
$countryStateArray = array();
$countryStateCityArray = array();

$countriesJson = file_get_contents("data/countries.json");
$countriesArray = json_decode($countriesJson, true);

$cscJson = file_get_contents("data/world.json");
$cscArray = json_decode($cscJson, true);


// Validating Country Names
foreach($cscArray['Countries'] as $country) {

    $countryName = mysqli_real_escape_string($conn,$country['CountryName']);
    $sql = "SELECT * FROM countries WHERE name='".$countryName."'";
    $result = $conn->query($sql);
    $states = $country['States'];

    if ($result->num_rows > 0) {

        //Get Country ID
        while($row = $result->fetch_assoc()) {
            $countryId = $row['id'];
            $countryCode = $row['iso2'];
            $stateNamesArray = array();
            $cityNamesArray = array();

            $countryStateCityArray[$k]['id'] = (int)$row['id'];
            $countryStateCityArray[$k]['name'] = $row['name'];
            $countryStateCityArray[$k]['iso3'] = $row['iso3'];
            $countryStateCityArray[$k]['iso2'] = $row['iso2'];
            $countryStateCityArray[$k]['country_code'] = $row['countrycode'];
            $countryStateCityArray[$k]['phone_code'] = $row['phonecode'];
            $countryStateCityArray[$k]['capital'] = $row['capital'];
            $countryStateCityArray[$k]['currency'] = $row['currency'];

            if(count($states)) : foreach($states as $state) :
            
                $stateId = $i+1;
                $stateName = mysqli_real_escape_string($conn,$state["StateName"]);
                $cities = $state['Cities'];
                $statesArray[$i]['id'] = $stateId;
                $statesArray[$i]['name'] = $stateName;
                $statesArray[$i]['country_id'] = (int)$countryId;
                $statesArray[$i]['country_code'] = $countryCode;
                
                // print_r($statesArray);
                $stateCityArray[$i]['id'] = $stateId;
                $stateCityArray[$i]['name'] = $stateName;
                $stateCityArray[$i]['country_id'] = $countryId;
                $stateCityArray[$i]['country_code'] = $countryCode;
                $stateCityArray[$i]['cities'] = $cities;

                array_push($stateNamesArray,$stateName);
                $countryStateCityArray[$k]['states'][$stateName] = $cities;
    
                $i++;

                if(count($cities)) : foreach($cities as $city) :
                    $cityId = $j+1;
                    $citiesArray[$j]['id'] = $cityId;
                    $citiesArray[$j]['name'] = mysqli_real_escape_string($conn,$city);
                    $citiesArray[$j]['state_id'] = $stateId;
                    $citiesArray[$j]['country_id'] = (int)$countryId;
                    $citiesArray[$j]['country_code'] = $countryCode;

                    $j++;
                endforeach; endif;
    
            endforeach; endif;
 
            $countryStateArray[$k]['id'] = (int)$row['id'];
            $countryStateArray[$k]['name'] = $row['name'];
            $countryStateArray[$k]['iso3'] = $row['iso3'];
            $countryStateArray[$k]['iso2'] = $row['iso2'];
            $countryStateArray[$k]['country_code'] = $row['countrycode'];
            $countryStateArray[$k]['phone_code'] = $row['phonecode'];
            $countryStateArray[$k]['capital'] = $row['capital'];
            $countryStateArray[$k]['currency'] = $row['currency'];
            $countryStateArray[$k]['states'] = $stateNamesArray;

            $k++;

        }
    } 
    
}

// print_r(count($statesArray));
// Putting Array to JSON
$fp = fopen('data/states.json', 'w');
fwrite($fp, json_encode($statesArray, JSON_PRETTY_PRINT));
fclose($fp);

// print_r($citiesArray);
// Putting Array to JSON
$fp = fopen('data/cities.json', 'w');
fwrite($fp, json_encode($citiesArray, JSON_PRETTY_PRINT));
fclose($fp);

// print_r($stateCityArray);
// Putting Array to JSON
$fp = fopen('data/states+cities.json', 'w');
fwrite($fp, json_encode($stateCityArray, JSON_PRETTY_PRINT));
fclose($fp);

// print_r($countryStateArray);
// Putting Array to JSON
$fp = fopen('data/countries+states.json', 'w');
fwrite($fp, json_encode($countryStateArray, JSON_PRETTY_PRINT));
fclose($fp);

// print_r($countryStateCityArray);
// Putting Array to JSON
$fp = fopen('data/countries+states+cities.json', 'w');
fwrite($fp, json_encode($countryStateCityArray, JSON_PRETTY_PRINT));
fclose($fp);


?>