#!/usr/bin/env python3

import sys
import csv
import plistlib
import os

files = [
    './csv/countries.csv',
    './csv/states.csv',
    './csv/cities.csv',
]

for csv_file in files:
    with open(csv_file, 'r', encoding='utf-8') as f:
        result = list(csv.DictReader(f))

    filename = os.path.basename(csv_file)
    plist_file = './plist/' + os.path.splitext(filename)[0] + '.plist'
    plist_file = open(plist_file, 'wb')
    plistlib.dump(result, plist_file)
