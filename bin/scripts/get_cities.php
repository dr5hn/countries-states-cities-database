<?php
require_once 'base.php';

// Cities // 144153/10 = 14415.30
// 980/apicalls/day/apikey

$counter = "counter.txt";
$f = fopen($counter, "r") or die("Unable to open file!");
$offset = (int)fgets($f); // 9801
$limit = $offset + 9; // 9801 + 9 = 9810
fclose($f);

$file_name = "data/".date("Y_m_d").'_1.json';

for ($i=0; $i<990; $i++):
    $url = "https://wft-geo-db.p.rapidapi.com/v1/geo/cities?offset=".$offset."&limit=10";
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
    $offset = $limit + 1; // 9811
    $limit = $limit + 10; // 9820

    $fps = fopen($counter, 'w');
    fwrite($fps, $offset.PHP_EOL);
    fclose($fps);

    echo $offset.PHP_EOL;
    echo $limit.PHP_EOL;

    // print_r($response);
    // print_r($response->body->data);
endfor;
