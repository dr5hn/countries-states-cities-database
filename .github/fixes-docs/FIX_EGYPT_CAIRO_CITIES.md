# Fix Summary: Cairo-area cities added

## Issue Reference
- **Title:** [Bug]: Missing And incorrect Egypt data
- **Area:** Egypt cities (Cairo region)

## Country Addressed
- **Country:** Egypt (EG)
- **States:** Cairo Governorate (state_id: 3223, state_code: C), Qalyubia Governorate (state_id: 3232, state_code: KB)

## Changes Made
- Added **Nasr City** (Cairo) — lat `30.05000000`, lon `31.36667000`, timezone `Africa/Cairo`, wikiDataId `Q1309979`.
- Added **Downtown Cairo** (Cairo) — lat `30.04750000`, lon `31.23830000`, timezone `Africa/Cairo`, wikiDataId `Q2933230`.
- Added **Zamalek** (Cairo) — lat `30.06194444`, lon `31.22055556`, timezone `Africa/Cairo`, wikiDataId `Q145356`.
- Added **Al Rehab** (Cairo) — lat `30.05000000`, lon `31.36670000`, timezone `Africa/Cairo`, wikiDataId `Q7309740`.
- Added **New Cairo** (Cairo) — lat `30.03000000`, lon `31.47000000`, timezone `Africa/Cairo`, wikiDataId `Q12191144`.
- Added **Obour City** (Qalyubia) — lat `30.20500000`, lon `31.45750000`, timezone `Africa/Cairo`, wikiDataId `Q4120190`.
- Included native names and multilingual translations (≥5 languages each) for all new cities.

## Validation
- Coordinates, native names, and wikiDataIds verified via the corresponding Wikipedia/Wikidata entries for each city.
- Ran `python3 bin/scripts/validation/translation_enricher.py --file /tmp/eg_new_entries.json --type city` to seed translations from Wikipedia before merging into `contributions/cities/EG.json`.
- Loaded `contributions/cities/EG.json` with `python -m json.load` to confirm JSON validity.

