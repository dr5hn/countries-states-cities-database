<?php
require_once 'base.php';

$statesJson = file_get_contents("../../states.json");
$statesArray = json_decode($statesJson, true);

print_r($statesArray);

if (!empty($statesArray)) :
    foreach($statesArray as $state) :
        $state_name = mysqli_real_escape_string($conn, $state['name']);
        $sql = "UPDATE states SET name='".$state_name."' WHERE id=".$state['id'];
        if ($conn->query($sql) === TRUE) {
            echo "Record updated successfully".PHP_EOL;
        } else {
            echo "Error updating record: ".$sql." ".$conn->error.PHP_EOL;
        }
    endforeach;
endif;
