<?php
require_once 'vendor/base.php';

$i = 0;
$j = 0;
$k = 0;
$l = 0;
$m = 0;

$countriesArray = array();
$statesArray = array();
$citiesArray = array();
$stateCityArray = array();
$countryStateArray = array();
$countryStateCityArray = array();
$stateNamesArray = array();
$cityNamesArray = array();

$rootDir = dirname(dirname(__FILE__));

// Fetching All Countries
$sql = "SELECT * FROM countries ORDER BY name";
$result = $conn->query($sql);
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        // Pushing it into Fresh Array
        $countriesArray[$m]['id'] = (int)$row['id'];
        $countriesArray[$m]['name'] = $row['name'];
        $countriesArray[$m]['iso3'] = $row['iso3'];
        $countriesArray[$m]['iso2'] = $row['iso2'];
        $countriesArray[$m]['phone_code'] = $row['phonecode'];
        $countriesArray[$m]['capital'] = $row['capital'];
        $countriesArray[$m]['currency'] = $row['currency'];
        $countriesArray[$m]['native'] = $row['native'];
        $countriesArray[$m]['emoji'] = $row['emoji'];
        $countriesArray[$m]['emojiU'] = $row['emojiU'];

        $m++;
    }
}

// Validating Country Names
foreach($countriesArray as $country) {

    $countryId = (int)$country['id'];
    $countryStateCityArray[$k]['id'] = $countryId;
    $countryStateCityArray[$k]['name'] = $country['name'];
    $countryStateCityArray[$k]['iso3'] = $country['iso3'];
    $countryStateCityArray[$k]['iso2'] = $country['iso2'];
    $countryStateCityArray[$k]['phone_code'] = $country['phone_code'];
    $countryStateCityArray[$k]['capital'] = $country['capital'];
    $countryStateCityArray[$k]['currency'] = $country['currency'];
    $countryStateCityArray[$k]['states'] = array();

    // Fetching All States Based on Country
    $sql = "SELECT * FROM states WHERE country_id=$countryId ORDER BY NAME";
    $stateResult = $conn->query($sql);

    $stateNamesArray = array();
    if ($stateResult->num_rows > 0) {
        while($state = $stateResult->fetch_assoc()) {

            // Only States Array
            $stateId = (int)$state['id'];
            $stateName = $state['name'];
            $statesArray[$i]['id'] = $stateId;
            $statesArray[$i]['name'] = $stateName;
            $statesArray[$i]['country_id'] = $countryId;
            $statesArray[$i]['country_code'] = $state['country_code'];
            $statesArray[$i]['state_code'] = $state['iso2'];

            // For Country State Array
            $stateArr = array(
                'id' => $stateId,
                'name' => $stateName,
                'state_code' => $state['iso2']
            );

            array_push($stateNamesArray, $stateArr);

            // Fetching All States Based on Country & State
            $sql = "SELECT * FROM cities WHERE country_id=$countryId AND state_id=$stateId ORDER BY NAME";
            $cityResult = $conn->query($sql);

            $cityNamesArray = array();
            if ($cityResult->num_rows > 0) {
                while($city = $cityResult->fetch_assoc()) {

                    // Only Cities Array
                    $cityId = (int)$city['id'];
                    $cityName = $city['name'];
                    $citiesArray[$j]['id'] = $cityId;
                    $citiesArray[$j]['name'] = $cityName;
                    $citiesArray[$j]['state_id'] = (int)$stateId;
                    $citiesArray[$j]['state_code'] = $city['state_code'];
                    $citiesArray[$j]['country_id'] = (int)$countryId;
                    $citiesArray[$j]['country_code'] = $city['country_code'];
                    $citiesArray[$j]['latitude'] = $city['latitude'];
                    $citiesArray[$j]['longitude'] = $city['longitude'];

                    // For State City Array
                    array_push($cityNamesArray, array(
                        'id' => $cityId,
                        'name' => $cityName,
                        'latitude' => $city['latitude'],
                        'longitude' => $city['longitude']
                    ));

                    $j++;
                }
            }

            // Completing CountryStateCity Array State by State
            $stateArr['cities'] = $cityNamesArray;
            array_push($countryStateCityArray[$k]['states'], $stateArr);

            // Completing StateCity Array
            $stateCityArray[$i]['id'] = $stateId;
            $stateCityArray[$i]['name'] = $stateName;
            $stateCityArray[$i]['state_code'] = $state['iso2'];
            $stateCityArray[$i]['country_id'] = $countryId;
            $stateCityArray[$i]['cities'] = $cityNamesArray;

            $i++;
        }
    }

    // Completing Country States Array
    $countryStateArray[$k]['name'] = $country['name'];
    $countryStateArray[$k]['iso3'] = $country['iso3'];
    $countryStateArray[$k]['iso2'] = $country['iso2'];
    $countryStateArray[$k]['phone_code'] = $country['phone_code'];
    $countryStateArray[$k]['capital'] = $country['capital'];
    $countryStateArray[$k]['currency'] = $country['currency'];
    $countryStateArray[$k]['states'] = $stateNamesArray;

    $k++;

}

echo 'Total Countries Count : '.count($countriesArray).PHP_EOL;
echo 'Total States Count : '.count($statesArray).PHP_EOL;
echo 'Total Cities Count : '.count($citiesArray).PHP_EOL;

// print_r($countriesArray);
$exportTo = $rootDir . '/countries.json';
$fp = fopen($rootDir . '/countries.json', 'w'); // Putting Array to JSON
fwrite($fp, json_encode($countriesArray,  JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($statesArray);
$exportTo = $rootDir . '/states.json';
$fp = fopen($rootDir . '/states.json', 'w'); // Putting Array to JSON
fwrite($fp, json_encode($statesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($citiesArray);
$exportTo = $rootDir . '/cities.json';
$fp = fopen($rootDir . '/cities.json', 'w'); // Putting Array to JSON
fwrite($fp, json_encode($citiesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($stateCityArray);
$exportTo = $rootDir . '/states+cities.json';
$fp = fopen($rootDir . '/states+cities.json', 'w'); // Putting Array to JSON
fwrite($fp, json_encode($stateCityArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($countryStateArray);
$exportTo = $rootDir . '/countries+states.json';
$fp = fopen($rootDir . '/countries+states.json', 'w'); // Putting Array to JSON
fwrite($fp, json_encode($countryStateArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// print_r($countryStateCityArray);
$exportTo = $rootDir . '/countries+states+cities.json';
$fp = fopen($exportTo, 'w'); // Putting Array to JSON
fwrite($fp, json_encode($countryStateCityArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
echo 'JSON Exported to ' .$exportTo . PHP_EOL;
fclose($fp);

// | JSON_ERROR_UTF8|JSON_ERROR_UTF16|JSON_THROW_ON_ERROR|JSON_ERROR_DEPTH

$conn->close();

// function _toIso($value) {
//     if (mb_detect_encoding($value) === 'UTF-8'):
//         echo 'old '.$value.PHP_EOL;
//         echo 'UTF-8'.PHP_EOL;
//         $value = iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $value);
//         echo 'omg '.$value.PHP_EOL;
//         echo gettype($value).PHP_EOL;
//         $char = "�";
//         echo var_dump(strpos($value, $char)).PHP_EOL;
//         if (strpos($value, strval('�')) !== false) {
//             $value = mb_convert_encoding($value, 'ISO-8859-15', 'UTF-8');
//             echo 'after '.$value.PHP_EOL;
//         }
//     endif;
//     return $value;
// }
