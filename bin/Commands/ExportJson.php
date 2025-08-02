<?php

namespace bin\Commands;

use bin\Support\Config;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;
use Symfony\Component\Filesystem\Filesystem;

class ExportJson extends Command
{
    protected static $defaultName = 'export:json';
    protected static $defaultDescription = 'Export data to JSON format';

    private Filesystem $filesystem;

    public function __construct()
    {
        parent::__construct(self::$defaultName);
        $this->filesystem = new Filesystem();
    }

    protected function configure(): void
    {
        $this->setHelp('This command exports the database to JSON format');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $db = Config::getConfig()->getDB();
        $rootDir = dirname(PATH_BASE);

        $io->title('Exporting JSON data to ' . $rootDir);

        try {
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
                while ($row = $result->fetch_assoc()) {
                    // Pushing it into Fresh Array
                    $countriesArray[$m]['id'] = (int)$row['id'];
                    $countriesArray[$m]['name'] = $row['name'];
                    $countriesArray[$m]['iso3'] = $row['iso3'];
                    $countriesArray[$m]['iso2'] = $row['iso2'];
                    $countriesArray[$m]['numeric_code'] = $row['numeric_code'];
                    $countriesArray[$m]['phonecode'] = $row['phonecode'];
                    $countriesArray[$m]['capital'] = $row['capital'];
                    $countriesArray[$m]['currency'] = $row['currency'];
                    $countriesArray[$m]['currency_name'] = $row['currency_name'];
                    $countriesArray[$m]['currency_symbol'] = $row['currency_symbol'];
                    $countriesArray[$m]['tld'] = $row['tld'];
                    $countriesArray[$m]['native'] = $row['native'];
                    $countriesArray[$m]['region'] = $row['region'];
                    $countriesArray[$m]['region_id'] = (int)$row['region_id'];
                    $countriesArray[$m]['subregion'] = $row['subregion'];
                    $countriesArray[$m]['subregion_id'] = (int)$row['subregion_id'];
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
            foreach ($countriesArray as $country) {

                $countryId = (int)$country['id'];
                $countryStateCityArray[$k]['id'] = $countryId;
                $countryStateCityArray[$k]['name'] = $country['name'];
                $countryStateCityArray[$k]['iso3'] = $country['iso3'];
                $countryStateCityArray[$k]['iso2'] = $country['iso2'];
                $countryStateCityArray[$k]['numeric_code'] = $country['numeric_code'];
                $countryStateCityArray[$k]['phonecode'] = $country['phonecode'];
                $countryStateCityArray[$k]['capital'] = $country['capital'];
                $countryStateCityArray[$k]['currency'] = $country['currency'];
                $countryStateCityArray[$k]['currency_name'] = $country['currency_name'];
                $countryStateCityArray[$k]['currency_symbol'] = $country['currency_symbol'];
                $countryStateCityArray[$k]['tld'] = $country['tld'];
                $countryStateCityArray[$k]['native'] = $country['native'];
                $countryStateCityArray[$k]['region'] = $country['region'];
                $countryStateCityArray[$k]['region_id'] = (int)$country['region_id'];
                $countryStateCityArray[$k]['subregion'] = $country['subregion'];
                $countryStateCityArray[$k]['subregion_id'] = (int)$country['subregion_id'];
                $countryStateCityArray[$k]['nationality'] = $country['nationality'];
                $countryStateCityArray[$k]['timezones'] = $country['timezones'];
                $countryStateCityArray[$k]['translations'] = $country['translations'];
                $countryStateCityArray[$k]['latitude'] = $country['latitude'];
                $countryStateCityArray[$k]['longitude'] = $country['longitude'];
                $countryStateCityArray[$k]['emoji'] = $country['emoji'];
                $countryStateCityArray[$k]['emojiU'] = $country['emojiU'];

                // BREAK:: Sneaking in between to prepare country city array
                $countryCityArray[$k]['name'] = $country['name'];
                $countryCityArray[$k]['cities'] = array();

                // CONTINUE:: Filling up CountryStateCity Arry
                $countryStateCityArray[$k]['states'] = array();

                // Fetching All States Based on Country
                $sql = "SELECT states.*, countries.name AS country_name FROM states JOIN countries ON states.country_id = countries.id WHERE country_id=$countryId ORDER BY NAME";
                $stateResult = $db->query($sql);

                $stateNamesArray = array();
                if ($stateResult->num_rows > 0) {
                    while ($state = $stateResult->fetch_assoc()) {

                        // Only States Array
                        $stateId = (int)$state['id'];
                        $stateName = $state['name'];
                        $countryName = $state['country_name'];
                        $statesArray[$i]['id'] = $stateId;
                        $statesArray[$i]['name'] = $stateName;
                        $statesArray[$i]['country_id'] = $countryId;
                        $statesArray[$i]['country_code'] = $state['country_code'];
                        $statesArray[$i]['country_name'] = $state['country_name'];
                        $statesArray[$i]['iso2'] = $state['iso2'];
                        $statesArray[$i]['fips_code'] = $state['fips_code'];
                        $statesArray[$i]['type'] = $state['type'];
                        $statesArray[$i]['level'] = $state['level'];
                        $statesArray[$i]['parent_id'] = $state['parent_id'];
                        $statesArray[$i]['latitude'] = $state['latitude'];
                        $statesArray[$i]['longitude'] = $state['longitude'];

                        // For Country State Array
                        $stateArr = array(
                            'id' => $stateId,
                            'name' => $stateName,
                            'iso2' => $state['iso2'],
                            'latitude' => $state['latitude'],
                            'longitude' => $state['longitude'],
                            'type' => $state['type']
                        );

                        array_push($stateNamesArray, $stateName);

                        // Fetching All Cities Based on Country & State
                        $sql = "SELECT * FROM cities WHERE country_id=$countryId AND state_id=$stateId ORDER BY NAME";
                        $cityResult = $db->query($sql);

                        $cityNamesArray = array();
                        if ($cityResult->num_rows > 0) {
                            while ($city = $cityResult->fetch_assoc()) {

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

                        $i++;
                    }
                }

                // Completing Country States Array
                $countryStateArray[$k]['name'] = $country['name'];
                $countryStateArray[$k]['states'] = $stateNamesArray;

                // Fetching All Cities Based on Country
                $sql = "SELECT name FROM cities WHERE country_id=$countryId ORDER BY NAME";
                $citiesResult = $db->query($sql);

                $citiesNamesArray = array();
                if ($citiesResult->num_rows > 0) {
                    while ($city = $citiesResult->fetch_assoc()) {
                        // For State City Array
                        array_push($citiesNamesArray, $city['name']);
                    }
                }

                $countryCityArray[$k]['cities'] = $citiesNamesArray;

                $k++;
            }

            // Fetching All Regions
            $sql = "SELECT * FROM regions ORDER BY name";
            $result = $db->query($sql);
            if ($result->num_rows > 0) {
                while ($row = $result->fetch_assoc()) {
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
                while ($row = $result->fetch_assoc()) {
                    // Pushing it into Fresh Array
                    $subregionsArray[$s]['id'] = (int)$row['id'];
                    $subregionsArray[$s]['name'] = $row['name'];
                    $subregionsArray[$s]['region_id'] = (int)$row['region_id'];
                    $subregionsArray[$s]['translations'] = json_decode($row['translations'], true);
                    $subregionsArray[$s]['wikiDataId'] = $row['wikiDataId'];
                    $s++;
                }
            }

            $io->writeln('Total Regions Count : ' . count($regionsArray));
            $io->writeln('Total Subregions Count : ' . count($subregionsArray));
            $io->writeln('Total Countries Count : ' . count($countriesArray));
            $io->writeln('Total States Count : ' . count($statesArray));
            $io->writeln('Total Cities Count : ' . count($citiesArray));

            // Add a Space
            $io->newLine();

            $exports = [
                '/json/regions.json' => $regionsArray,
                '/json/subregions.json' => $subregionsArray,
                '/json/countries.json' => $countriesArray,
                '/json/states.json' => $statesArray,
                '/json/cities.json' => $citiesArray,
                '/json/countries+states.json' => $countryStateArray,
                '/json/countries+cities.json' => $countryCityArray,
                '/json/countries+states+cities.json' => $countryStateCityArray
            ];

            foreach ($exports as $file => $data) {
                $this->filesystem->dumpFile(
                    $rootDir . $file,
                    json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) . PHP_EOL
                );
                $io->success("Exported to $file");
            }

            $db->close();
            return Command::SUCCESS;
        } catch (\Exception $e) {
            $io->error("Export failed: {$e->getMessage()}");
            return Command::FAILURE;
        }
    }
}
