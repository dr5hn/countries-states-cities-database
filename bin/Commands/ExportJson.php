<?php
namespace bin\Commands;

use bin\Support\Config;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;

class ExportJson extends Command
{

    // the name of the command (the part after "bin/console")
    protected static $defaultName = 'export:export-json';

    protected function execute(InputInterface $input, OutputInterface $output)
    {
        $db =  Config::getConfig()->getDB();

        $rootDir = PATH_BASE . '../..';

        $r = 0; // regions
        $s = 0; // suberegions
        $i = 0; // states && states-cities
        $j = 0; // cities
        $k = 0; // countries-states-cities && countries-states
        $l = 0;
        $m = 0; // countries

        $countriesArray = array();
        $statesArray = array();
        $citiesArray = array();
        $stateCityArray = array();
        $countryStateArray = array();
        $countryCityArray = array();
        $countryStateCityArray = array();
        $regionsArray = array();
        $subregionsArray = array();
        $stateNamesArray = array();
        $cityNamesArray = array();


        // Fetching All Countries
        $sql = "SELECT * FROM countries ORDER BY name";
        $result = $db->query($sql);
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                // Pushing it into Fresh Array
                $countriesArray[$m]['id'] = (int)$row['id'];
                $countriesArray[$m]['name'] = $row['name'];
                $countriesArray[$m]['iso3'] = $row['iso3'];
                $countriesArray[$m]['iso2'] = $row['iso2'];
                $countriesArray[$m]['numeric_code'] = $row['numeric_code'];
                $countriesArray[$m]['phone_code'] = $row['phonecode'];
                $countriesArray[$m]['capital'] = $row['capital'];
                $countriesArray[$m]['currency'] = $row['currency'];
                $countriesArray[$m]['currency_name'] = $row['currency_name'];
                $countriesArray[$m]['currency_symbol'] = $row['currency_symbol'];
                $countriesArray[$m]['tld'] = $row['tld'];
                $countriesArray[$m]['native'] = $row['native'];
                $countriesArray[$m]['region'] = $row['region'];
                $countriesArray[$m]['region_id'] = $row['region_id'];
                $countriesArray[$m]['subregion'] = $row['subregion'];
                $countriesArray[$m]['subregion_id'] = $row['subregion_id'];
                $countriesArray[$m]['nationality'] = $row['nationality'];
                $countriesArray[$m]['timezones'] = json_decode($row['timezones'], true);
                $countriesArray[$m]['translations'] = json_decode($row['translations'], true);
                $countriesArray[$m]['latitude'] = $row['latitude'];
                $countriesArray[$m]['longitude'] = $row['longitude'];
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
            $countryStateCityArray[$k]['numeric_code'] = $country['numeric_code'];
            $countryStateCityArray[$k]['phone_code'] = $country['phone_code'];
            $countryStateCityArray[$k]['capital'] = $country['capital'];
            $countryStateCityArray[$k]['currency'] = $country['currency'];
            $countryStateCityArray[$k]['currency_name'] = $country['currency_name'];
            $countryStateCityArray[$k]['currency_symbol'] = $country['currency_symbol'];
            $countryStateCityArray[$k]['tld'] = $country['tld'];
            $countryStateCityArray[$k]['native'] = $country['native'];
            $countryStateCityArray[$k]['region'] = $country['region'];
            $countryStateCityArray[$k]['region_id'] = $country['region_id'];
            $countryStateCityArray[$k]['subregion'] = $country['subregion'];
            $countryStateCityArray[$k]['subregion_id'] = $country['subregion_id'];
            $countryStateCityArray[$k]['nationality'] = $country['nationality'];
            $countryStateCityArray[$k]['timezones'] = $country['timezones'];
            $countryStateCityArray[$k]['translations'] = $country['translations'];
            $countryStateCityArray[$k]['latitude'] = $country['latitude'];
            $countryStateCityArray[$k]['longitude'] = $country['longitude'];
            $countryStateCityArray[$k]['emoji'] = $country['emoji'];
            $countryStateCityArray[$k]['emojiU'] = $country['emojiU'];

            // BREAK:: Sneaking in between to prepare country city array
            array_push($countryCityArray, $countryStateCityArray[$k]);
            $countryCityArray[$k]['cities'] = array();

            // CONTINUE:: Filling up CountryStateCity Arry
            $countryStateCityArray[$k]['states'] = array();

            // Fetching All States Based on Country
            $sql = "SELECT states.*, countries.name AS country_name FROM states JOIN countries ON states.country_id = countries.id WHERE country_id=$countryId ORDER BY NAME";
            $stateResult = $db->query($sql);

            $stateNamesArray = array();
            if ($stateResult->num_rows > 0) {
                while($state = $stateResult->fetch_assoc()) {

                    // Only States Array
                    $stateId = (int)$state['id'];
                    $stateName = $state['name'];
                    $countryName = $state['country_name'];
                    $statesArray[$i]['id'] = $stateId;
                    $statesArray[$i]['name'] = $stateName;
                    $statesArray[$i]['country_id'] = $countryId;
                    $statesArray[$i]['country_code'] = $state['country_code'];
                    $statesArray[$i]['country_name'] = $state['country_name'];
                    $statesArray[$i]['state_code'] = $state['iso2'];
                    $statesArray[$i]['type'] = $state['type'];
                    $statesArray[$i]['latitude'] = $state['latitude'];
                    $statesArray[$i]['longitude'] = $state['longitude'];

                    // For Country State Array
                    $stateArr = array(
                        'id' => $stateId,
                        'name' => $stateName,
                        'state_code' => $state['iso2'],
                        'latitude' => $state['latitude'],
                        'longitude' => $state['longitude'],
                        'type' => $state['type']
                    );

                    array_push($stateNamesArray, $stateArr);

                    // Fetching All Cities Based on Country & State
                    $sql = "SELECT * FROM cities WHERE country_id=$countryId AND state_id=$stateId ORDER BY NAME";
                    $cityResult = $db->query($sql);

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
                            $citiesArray[$j]['state_name'] = $stateName;
                            $citiesArray[$j]['country_id'] = (int)$countryId;
                            $citiesArray[$j]['country_code'] = $city['country_code'];
                            $citiesArray[$j]['country_name'] = $countryName;
                            $citiesArray[$j]['latitude'] = $city['latitude'];
                            $citiesArray[$j]['longitude'] = $city['longitude'];
                            $citiesArray[$j]['wikiDataId'] = $city['wikiDataId'];

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
                    $stateCityArray[$i]['latitude'] = $state['latitude'];
                    $stateCityArray[$i]['longitude'] = $state['longitude'];
                    $stateCityArray[$i]['country_id'] = $countryId;
                    $stateCityArray[$i]['cities'] = $cityNamesArray;

                    $i++;
                }
            }

            // Completing Country States Array
            $countryStateArray[$k]['name'] = $country['name'];
            $countryStateArray[$k]['iso3'] = $country['iso3'];
            $countryStateArray[$k]['iso2'] = $country['iso2'];
            $countryStateArray[$k]['numeric_code'] = $country['numeric_code'];
            $countryStateArray[$k]['phone_code'] = $country['phone_code'];
            $countryStateArray[$k]['capital'] = $country['capital'];
            $countryStateArray[$k]['currency'] = $country['currency'];
            $countryStateArray[$k]['currency_name'] = $country['currency_name'];
            $countryStateArray[$k]['currency_symbol'] = $country['currency_symbol'];
            $countryStateArray[$k]['tld'] = $country['tld'];
            $countryStateArray[$k]['native'] = $country['native'];
            $countryStateArray[$k]['region'] = $country['region'];
            $countryStateArray[$k]['region_id'] = $country['region_id'];
            $countryStateArray[$k]['subregion'] = $country['subregion'];
            $countryStateArray[$k]['subregion_id'] = $country['subregion_id'];
            $countryStateArray[$k]['nationality'] = $country['nationality'];
            $countryStateArray[$k]['timezones'] = $country['timezones'];
            $countryStateArray[$k]['translations'] = $country['translations'];
            $countryStateArray[$k]['latitude'] = $country['latitude'];
            $countryStateArray[$k]['longitude'] = $country['longitude'];
            $countryStateArray[$k]['emoji'] = $country['emoji'];
            $countryStateArray[$k]['emojiU'] = $country['emojiU'];
            $countryStateArray[$k]['states'] = $stateNamesArray;

            // Fetching All Cities Based on Country
            $sql = "SELECT id, name, latitude, longitude FROM cities WHERE country_id=$countryId ORDER BY NAME";
            $citiesResult = $db->query($sql);

            $citiesNamesArray = array();
            if ($citiesResult->num_rows > 0) {
                while($city = $citiesResult->fetch_assoc()) {
                    // For State City Array
                    array_push($citiesNamesArray, array(
                        'id' => (int)$city['id'],
                        'name' => $city['name'],
                        'latitude' => $city['latitude'],
                        'longitude' => $city['longitude']
                    ));
                }
            }

            $countryCityArray[$k]['cities'] = $citiesNamesArray;

            $k++;

        }

// Fetching All Regions
        $sql = "SELECT * FROM regions ORDER BY name";
        $result = $db->query($sql);
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                // Pushing it into Fresh Array
                $regionsArray[$r]['id'] = (int)$row['id'];
                $regionsArray[$r]['name'] = $row['name'];
                $regionsArray[$r]['translations'] = json_decode($row['translations'], true);
                $regionsArray[$r]['wikiDataId'] = $row['wikiDataId'];

                $r++;
            }
        }


        $sql = "SELECT * FROM subregions ORDER BY name";
        $result = $db->query($sql);
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                // Pushing it into Fresh Array
                $subregionsArray[$s]['id'] = (int)$row['id'];
                $subregionsArray[$s]['name'] = $row['name'];
                $subregionsArray[$s]['region_id'] = $row['region_id'];
                $subregionsArray[$s]['translations'] = json_decode($row['translations'], true);
                $subregionsArray[$s]['wikiDataId'] = $row['wikiDataId'];
                $s++;
            }
        }

        $output->writeln('Total Regions Count : '.count($regionsArray) );
        $output->writeln('Total Subregions Count : '.count($subregionsArray));
        $output->writeln('Total Countries Count : '.count($countriesArray));
        $output->writeln('Total States Count : '.count($statesArray));
        $output->writeln('Total Cities Count : '.count($citiesArray));
        
        $exportTo = $rootDir . '/countries.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($countriesArray,  JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln('JSON Exported to ' .$exportTo );
        fclose($fp);


        $exportTo = $rootDir . '/states.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($statesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/cities.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($citiesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/states+cities.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($stateCityArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/countries+states.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($countryStateArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/countries+cities.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($countryCityArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/countries+states+cities.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($countryStateCityArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/regions.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($regionsArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo );
        fclose($fp);
        
        $exportTo = $rootDir . '/subregions.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($subregionsArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT).PHP_EOL);
        $output->writeln( 'JSON Exported to ' .$exportTo  );
        fclose($fp);
        

        $db->close();

        
        return 1;
    }


}