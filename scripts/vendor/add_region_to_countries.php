<?php
require_once 'base.php';

$start_time = time();

$wikipediaJson = file_get_contents("data/wikipedia_tz.json");
$wikipediaArray = json_decode($wikipediaJson, true);

foreach($wikipediaArray as $wElemts) :
    $wkData[$wElemts['code'].'|'.$wElemts['timezone']] = $wElemts;
endforeach;

$countryTZ = [];

$getAllTimeZonesJson = file_get_contents("http://api.timezonedb.com/v2.1/list-time-zone?key=WTU4LLBZ20OF&format=json");
$getAllTimeZonesArray = json_decode($getAllTimeZonesJson, true);
$totalRecords = count($getAllTimeZonesArray['zones']);

foreach($getAllTimeZonesArray['zones'] as $key => $zones) :
    //Sleep my child - you are on the free version of the API
    sleep(1);
    
    $zoneInfoRaw = file_get_contents("http://api.timezonedb.com/v2.1/get-time-zone?key=WTU4LLBZ20OF&format=json&by=zone&zone=".$zones['zoneName']);
    $zoneInfoJson = json_decode($zoneInfoRaw);

    $zoneTmp = $zoneInfoJson->gmtOffset;
    $negative = false;
    if (stripos($zoneInfoJson->gmtOffset, '-') !== false) {
        $zoneTmp = ltrim($zoneInfoJson->gmtOffset, '-');
        $negative = true;
    }
    
    $zoneFinal = gmdate("H:i", $zoneTmp);

    if ($zoneInfoJson->gmtOffset == 0) {
        $zonePlace = 'UTC±00';
    } else if ($negative) {
        $zonePlace = 'UTC-'.$zoneFinal;
    } else {
        $zonePlace = 'UTC+'.$zoneFinal;
    }

    $search = $zoneInfoJson->abbreviation.'|'.$zonePlace;
    
    if (stripos($search, ':00') !== false) {
        $search = substr($search, 0, (strlen($search) - 3));
    }
    
    $temp = [];
    $temp['zoneName'] = $zoneInfoJson->zoneName;
    $temp['gmtOffset'] = $zoneInfoJson->gmtOffset;
    $temp['gmtOffsetName'] = $zonePlace;
    $temp['abbreviation'] = $zoneInfoJson->abbreviation;
    $temp['tzName'] = $wkData[$search]['name'];

    echo '-------------------------------------'.PHP_EOL;
    echo 'RECORD NO: '. ($key + 1) .'/'.$totalRecords.PHP_EOL;
    echo 'COUNTRY CODE: '.$zones['countryCode'].PHP_EOL;
    echo 'COUNTRY CODE: '.$zones['countryName'].PHP_EOL;
    echo 'ZONE NAME: '.$zones['zoneName'].PHP_EOL;
    echo 'GMT OFFSET : '.$zoneInfoJson->gmtOffset.PHP_EOL;
    echo 'GMT OFFSETNAME : '.$zonePlace.PHP_EOL;
    echo 'ABBR: '.$zoneInfoJson->abbreviation.PHP_EOL;
    echo 'SEARCH:'.$search.PHP_EOL;
    echo 'TIMEZONE NAME: '.$wkData[$search]['name'].PHP_EOL;

    if ( !isset($wkData[$search]['name']) ) {
        $invalid[] = $temp; 
    }

    $countryTZ[$zoneInfoJson->countryCode]['code'] = $zoneInfoJson->countryCode;
    $countryTZ[$zoneInfoJson->countryCode]['name'] = $zoneInfoJson->countryName;
    $countryTZ[$zoneInfoJson->countryCode]['timezones'][] = $temp;

endforeach;

echo '-------------------------------------'.PHP_EOL;
echo 'COUNT OF RECORDS WHICH DID NOT HAVE TZ NAME: '.count($invalid).PHP_EOL;
echo '-------------------------------------'.PHP_EOL;
print_r($invalid);

$fp = fopen('timezone_data.json', 'a') or die("Unable to open file!");
fwrite($fp, json_encode((array)$countryTZ, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_NUMERIC_CHECK).PHP_EOL);
fclose($fp);

echo 'Written to file: timezone_data.json in '.(time() - $start_time).' seconds'.PHP_EOL;

die();

$regionsJson = file_get_contents("data/regions_tz.json");
// print_r($regionsJson);
$regionsArray = json_decode($regionsJson, true);
// print_r($countriesArray);

$wikipediaJson = file_get_contents("http://api.timezonedb.com/v2.1/list-time-zone?key=WTU4LLBZ20OF&format=json");
$wikipediaArray = json_decode($wikipediaJson, true);
echo '<pre>';
print_r($wikipediaArray);
die();

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
