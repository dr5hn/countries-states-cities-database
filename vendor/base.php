<?php
ini_set('display_errors', 1);
ini_set('error_reporting', E_ALL);

require_once __DIR__.'/vendor/autoload.php';

header('Content-type: text/plain');

$NUMBER_OF_SECONDS = 1;
$API_KEY = ''; // Your RapidApi GeoDBCities Api Key

function slugify($text)
{
  // replace non letter or digits by -
  $text = preg_replace('~[^\pL\d]+~u', '-', $text);

  // transliterate
  $text = iconv('utf-8', 'us-ascii//TRANSLIT', $text);

  // remove unwanted characters
  $text = preg_replace('~[^-\w]+~', '', $text);

  // trim
  $text = trim($text, '-');

  // remove duplicate -
  $text = preg_replace('~-+~', '-', $text);

  // lowercase
  $text = strtolower($text);

  if (empty($text)) {
    return 'n-a';
  }

  return $text;
}
