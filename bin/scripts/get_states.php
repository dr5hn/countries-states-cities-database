<?php
require_once 'base.php';

// Regions
$countriesJson = file_get_contents("data/countries.json");
$countriesArray = json_decode($countriesJson, true);
foreach($countriesArray as $country) :
    $limit = 10;
    $offset = 0;
    $MAX_LIMIT = 1;

    for ($i=0; $i<$MAX_LIMIT; $i++):
        $url = "https://wft-geo-db.p.rapidapi.com/v1/geo/countries/".$country['wikiDataId']."/regions?offset=".$offset."&limit=10";
        echo $url.PHP_EOL;
        $response = Unirest\Request::get($url,
            array(
                "X-RapidAPI-Host" => "wft-geo-db.p.rapidapi.com",
                "X-RapidAPI-Key" => $API_KEY
            )
        );

        if (!empty($response->body->data)) {
            $file_name = $country['code'].'.json';
            $fp = fopen('data/states/'.$file_name, 'a');
            fwrite($fp, json_encode((array)$response->body->data, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT|JSON_NUMERIC_CHECK).PHP_EOL);
            fclose($fp);
            if ($i%5 == 0): sleep($NUMBER_OF_SECONDS); endif;
            $offset = $limit + 1;
            $limit = $limit + 10;

            // Set Dynamic
            $TOTAL_COUNT = $response->body->metadata->totalCount;
            echo $TOTAL_COUNT;
            if ($TOTAL_COUNT > 10): $MAX_LIMIT = ceil($TOTAL_COUNT/10); endif;
            echo 'OK SET '.$MAX_LIMIT.PHP_EOL;
        }

        // print_r($response);
        // print_r($response->body->data);

    endfor;
endforeach;
