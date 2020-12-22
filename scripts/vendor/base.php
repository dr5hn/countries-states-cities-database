<?php
ini_set('display_errors', 1);
ini_set('memory_limit', '-1');
ini_set('max_execution_time', 300);
ini_set('error_reporting', E_ALL & ~E_NOTICE);
date_default_timezone_set('Asia/Kolkata');

require_once __DIR__.'/vendor/autoload.php';

header('Content-type: text/plain');

$NUMBER_OF_SECONDS = 1;
$API_KEY = '5fd075d43amshebc391ff2da4e29p1d5717jsn54d564ec97fa'; // Your RapidApi GeoDBCities Api Key

$servername = "127.0.0.1";
$username = "root";
$password = "root";
$dbname = "world";
$port = 8889;

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// change character set to utf8
if (!$conn->set_charset("utf8mb4")) {
    printf("Error loading character set utf8: %s\n", $conn->error);
} else {
    printf("Current character set: %s\n", $conn->character_set_name());
}
