#!/bin/bash

# Convert MySQL to CSV
for f in 'countries' 'states' 'cities'; do
    mysql -uroot -proot world -e "SELECT * FROM ${f} INTO OUTFILE 'csv/${f}.csv' FIELDS TERMINATED BY '|' LINES TERMINATED BY '\n';"
done
