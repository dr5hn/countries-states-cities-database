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
    $temp['abbr'] = $zoneInfoJson->abbreviation;
    $temp['tzName'] = (isset($wkData[$search]['name']) ? $wkData[$search]['name'] : "");

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

$fr = fopen('data/timezone_data.json', 'r');
if ($fr === false) {
    $fp = fopen('data/timezone_data.json', 'w+') or die("Unable to open file!");
    fwrite($fp, json_encode((array)$countryTZ, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_NUMERIC_CHECK).PHP_EOL);
    fclose($fp);
} else {
    $countryTZ = file_get_contents('data/timezone_data.json');
    $countryTZ = json_decode($countryTZ, true);
}
fclose($fr);

// Update kar lo
foreach ($countryTZ as $key => $value) : 
    $tzData = mysqli_real_escape_string($conn, json_encode($value['timezones']));
    $sql = "UPDATE countries SET timezones = '$tzData' WHERE iso2 = '$key';";

    if ($conn->query($sql) === TRUE) {
        echo "Record updated successfully for ". $value['name'].PHP_EOL;
    } else {
        echo "Error: " . $sql ." ". $conn->error.PHP_EOL;
    }
endforeach;

echo 'Written to file: timezone_data.json in '.(time() - $start_time).' seconds'.PHP_EOL;
