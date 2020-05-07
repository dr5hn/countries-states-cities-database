#!/bin/bash
for f in ./*.json; do
    [ -e "$f" ] || continue
    filename="${f%.*}"
    filename="${filename:2}"
    plutil -convert xml1 "$f" -o ./plist/"$filename".plist
done
