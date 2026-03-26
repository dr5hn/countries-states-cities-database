# Fix: Rename "Gurgaon" to "Gurugram" (Haryana, India)

## Issue Reference

Resolves: [Bug]: Replace outdated city name "Gurgaon" with "Gurugram"
GitHub Issue: https://github.com/dr5hn/countries-states-cities-database/issues (search "Gurgaon")

## Problem

The city of Gurugram, Haryana, India was officially renamed from "Gurgaon" to "Gurugram"
by the Haryana government in April 2016. The database still used the outdated name "Gurgaon".

## Countries/Regions Addressed

- **Country**: India (IN, country_id: 101)
- **State**: Haryana (HR, state_id: 4007)
- **City ID**: 132032

## Changes Made

Updated `contributions/cities/IN.json` for city ID 132032:

| Field | Old Value | New Value |
|-------|-----------|-----------|
| `name` | Gurgaon | Gurugram |
| `native` | गुडगाँव | गुरुग्राम |
| `translations.br` | Gurgaon | Gurugram |
| `translations.ko` | 구르가온 | 구루그람 |
| `translations.pt-BR` | Gurgaon | Gurugram |
| `translations.pt` | Gurgaon | Gurugram |
| `translations.nl` | Gurgaon | Gurugram |
| `translations.hr` | Gurgaon | Gurugram |
| `translations.fa` | گورگان | گوروگرام |
| `translations.de` | Gurgaon | Gurugram |
| `translations.es` | Gurgaon | Gurugram |
| `translations.fr` | Gurgaon | Gurugram |
| `translations.ja` | グルガオン | グルグラム |
| `translations.it` | Gurgaon | Gurugram |
| `translations.zh-CN` | 古尔冈 | 古鲁格拉姆 |
| `translations.tr` | Gurgaon | Gurugram |
| `translations.ru` | Гургаон | Гуруграм |
| `translations.uk` | Гургаон | Гуруграм |
| `translations.pl` | Gurgaon | Gurugram |
| `translations.hi` | गुडगाँव | गुरुग्राम |
| `translations.ar` | جورجاون | غوروغرام |

## Source / Validation

- The Haryana government officially renamed Gurgaon to Gurugram on April 12, 2016.
- Wikipedia article: https://en.wikipedia.org/wiki/Gurugram (redirects from "Gurgaon")
- WikiData entry: https://www.wikidata.org/wiki/Q1815766
