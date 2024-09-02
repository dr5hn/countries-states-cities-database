<?php
require_once 'base.php';

// Countries // 190/10
$limit = 10;
$offset = 0;
$MAX_LIMIT = 1;
for ($i=0; $i<25; $i++):
    $url = "https://wft-geo-db.p.rapidapi.com/v1/geo/countries?offset=".$offset."&limit=10";
    echo $url.PHP_EOL;
    $response = Unirest\Request::get($url,
        array(
            "X-RapidAPI-Host" => "wft-geo-db.p.rapidapi.com",
            "X-RapidAPI-Key" => $API_KEY
        )
    );
    $fp = fopen('data/countries.json', 'a');
    fwrite($fp, json_encode((array)$response->body->data, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_NUMERIC_CHECK).PHP_EOL);
    fclose($fp);
    if ($i%5 == 0): sleep($NUMBER_OF_SECONDS); endif;
    $offset = $limit + 1;
    $limit = $limit + 10;
    echo $offset.PHP_EOL;
    echo $limit.PHP_EOL;

    // print_r($response);
    // print_r($response->body->data);

endfor;
