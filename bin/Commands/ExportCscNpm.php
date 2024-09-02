<?php


namespace bin\Commands;

use bin\Support\Config;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;

class ExportCscNpm extends Command
{
    protected static $defaultName = 'export:export-csc-npm';

    protected function execute(InputInterface $input, OutputInterface $output)
    {
        $db = Config::getConfig()->getDB();
        $rootDir = PATH_BASE . '../..';

        $i = 0;
        $j = 0;
        $k = 0;

        $countriesArray = array();
        $statesArray = array();
        $citiesArray = array();

        $sql = "SELECT * FROM countries";
        $result = $db->query($sql);
        if ($result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                // Pushing it into Fresh Array
                $countriesArray[$i]['isoCode'] = $row['iso2'];
                $countriesArray[$i]['name'] = $row['name'];
                $countriesArray[$i]['phonecode'] = $row['phonecode'];
                $countriesArray[$i]['flag'] = $row['emoji'];
                $countriesArray[$i]['currency'] = $row['currency'];
                $countriesArray[$i]['latitude'] = $row['latitude'];
                $countriesArray[$i]['longitude'] = $row['longitude'];
                $countriesArray[$i]['timezones'] = json_decode($row['timezones'], true);

                $i++;
            }
        }


        $sql = "SELECT * FROM states";
        $result = $db->query($sql);
        if ($result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                // Pushing it into Fresh Array
                $statesArray[$j]['name'] = $row['name'];
                $statesArray[$j]['isoCode'] = $row['iso2'];
                $statesArray[$j]['countryCode'] = $row['country_code'];
                $statesArray[$j]['latitude'] = $row['latitude'];
                $statesArray[$j]['longitude'] = $row['longitude'];

                $j++;
            }
        }


        $sql = "SELECT * FROM cities";
        $result = $db->query($sql);
        if ($result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                // Pushing it into Fresh Array
                $citiesArray[$k]['name'] = $row['name'];
                $citiesArray[$k]['countryCode'] = $row['country_code'];
                $citiesArray[$k]['stateCode'] = $row['state_code'];
                $citiesArray[$k]['latitude'] = $row['latitude'];
                $citiesArray[$k]['longitude'] = $row['longitude'];

                $k++;
            }
        }

        $output->writeln('Total Countries Count : ' . count($countriesArray));
        $output->writeln('Total States Count : ' . count($statesArray));
        $output->writeln('Total Cities Count : ' . count($citiesArray));


        $exportTo = $rootDir . '/csc/country.json';
        if(!is_dir($rootDir . '/csc')){
            mkdir($rootDir . '/csc', 777, true);
        }
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($countriesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL);
        $output->writeln('JSON Exported to ' . $exportTo);
        fclose($fp);


        $exportTo = $rootDir . '/csc/state.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($statesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL);
        $output->writeln('JSON Exported to ' . $exportTo);
        fclose($fp);


        $exportTo = $rootDir . '/csc/city.json';
        $fp = fopen($exportTo, 'w'); // Putting Array to JSON
        fwrite($fp, json_encode($citiesArray, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL);
        $output->writeln('JSON Exported to ' . $exportTo);
        fclose($fp);

        $db->close();
        return 1;

    }
}