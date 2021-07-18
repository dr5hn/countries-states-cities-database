<?php
require_once 'base.php';

// Cities // 144153/10 = 14415.30
// 980/apicalls/day/apikey

$counter = "counter.txt";
$f = fopen($counter, "r") or die("Unable to open file!");
// $offset = (int)fgets($f); // 9801 - For Automated Fetch
$offset = 0; // For Manual Fetch
$limit = $offset + 9; // 9801 + 9 = 9810
fclose($f);

// RO-MM - 244
// RO-MS - 599

$countryWiki = 'CL';
$stateFips = 'RM';

$file_name = "data/".$countryWiki.'_'.$stateFips.'.json';

for ($i=0; $i<6; $i++): // 379 / 10
    $url = "https://wft-geo-db.p.rapidapi.com/v1/geo/countries/".$countryWiki."/regions/".$stateFips."/cities?offset=".$offset."&limit=10&types=CITY&sort=name";
    echo $url.PHP_EOL;
    $response = Unirest\Request::get($url,
        array(
            "X-RapidAPI-Host" => "wft-geo-db.p.rapidapi.com",
            "X-RapidAPI-Key" => $API_KEY
        )
    );

    $fp = fopen($file_name, 'a') or die("Unable to open file!");
    fwrite($fp, json_encode((array)$response->body->data, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_NUMERIC_CHECK).PHP_EOL);
    fclose($fp);

    if ($i%5 == 0): sleep($NUMBER_OF_SECONDS); endif;
    $offset = $limit + 1; // 9810
    $limit = $limit + 10; // 9820

    $fps = fopen($counter, 'w');
    fwrite($fps, $offset.PHP_EOL);
    fclose($fps);

    echo $offset.PHP_EOL;
    echo $limit.PHP_EOL;

    // print_r($response);
    // print_r($response->body->data);
endfor;
