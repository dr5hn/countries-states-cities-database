# Fix Summary: Belgium English city-name translations

## Context
**Source:** Export customer report (Miguel Stevens, Studiomonty) — selecting "English" in the export
tool returned Dutch city names (`Antwerpen`, `Gent`, `Brugge`) instead of English.

## Root Cause
The export tool's language selector reads `translations[lang]` and falls back to the stored `name`
when that key is missing. Belgium had **0 of 549** cities with `translations.en`, and the `name`
field holds the local Dutch/French endonym for ~150 BE cities — so "English" fell back to Dutch.

## Fix
Backfilled `translations.en` for all **549** Belgian cities using English labels from Wikidata
(every BE record has a `wikiDataId`; 100% coverage).

### Integrity guard (important)
Wikidata labels were **not** trusted blindly. Each `wikiDataId` was verified by requiring the
record's `name` or `native` to match the entity's Dutch/French label or alias before adopting its
English label.

| Outcome | Count | Handling |
|---------|-------|----------|
| QID verified → Wikidata English label applied | 508 | 18 are genuine exonyms (Antwerp, Ghent, Bruges, Kelmis, Nieuport, province names…); the rest equal `name` |
| QID **unverified** → fell back to stored `name` | 41 | See below — safe (`name` is the correct English for these) |

The guard prevented 41 wrong English names from being written (e.g. Liège would have become "Lint").

## Secondary finding — 41 wrong `wikiDataId`s in BE.json (follow-up)
The 41 unverified records have a `wikiDataId` that resolves to a **different** Belgian municipality,
and many also have machine-translated garbage `native` values. Examples:

| name | bad `native` | `wikiDataId` resolves to |
|------|-------------|--------------------------|
| Liège | `Aan het zeren` ("aching") | Lint |
| Charleroi | Charleroi | Chapelle-lez-Herlaimont |
| Mons | `Keren` | Momignies |
| Roeselare | Roeselare | Rochefort |
| Frameries | `Kloppen` ("knocking") | Fosses-la-Ville |
| Herstal | `Van haar` ("of her") | Herselt |

This is a pre-existing data-integrity bug (same class as the Iran native-name issue #1587) and is
**not** fixed in this PR — tracked as a follow-up to correct the `wikiDataId`s and `native` values.

## Verification
- ✅ 549/549 BE cities now have `translations.en`
- ✅ Diff touches only the `translations` object (549 `en` keys added); no other field changed
- ✅ JSON re-validated at 549 records; encoding/formatting preserved

## Files Changed
- `contributions/cities/BE.json` — add `translations.en` to all 549 records.
