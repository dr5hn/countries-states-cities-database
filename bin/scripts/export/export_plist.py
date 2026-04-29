#!/usr/bin/env python3

import sys
import csv
import plistlib
import os

files = [
    './csv/regions.csv',
    './csv/subregions.csv',
    './csv/countries.csv',
    './csv/states.csv',
    './csv/cities.csv',
    './csv/postcodes.csv',
]

for csv_file in files:
    if not os.path.exists(csv_file):
        print('PLIST: skipping missing source {}'.format(csv_file))
        continue
    with open(csv_file, 'r', encoding='utf-8') as f:
        result = list(csv.DictReader(f))

    filename = os.path.basename(csv_file)
    plist_file_path = './plist/' + os.path.splitext(filename)[0] + '.plist'
    plist_file = open(plist_file_path, 'wb')
    plistlib.dump(result, plist_file)
    print('PLIST Exported to {}'.format(plist_file_path))
