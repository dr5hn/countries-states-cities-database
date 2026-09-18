# Fix Summary: Rename "Ahmednagar" to "Ahilyanagar" (Maharashtra, India)

## Issue Reference
**Original Issue:** [#1615](https://github.com/dr5hn/countries-states-cities-database/issues/1615) — Update the city name -> ahmadnagar to ahilyanagar

## Executive Summary

Ahmednagar (Maharashtra, India, city id `147670`) was officially renamed **Ahilyanagar** in honor of the 18th-century Maratha queen Ahilyabai Holkar. The Maharashtra government announced the rename on 31 May 2023, the state cabinet formally approved it on 13 March 2024, and the state government notified the change on 8 October 2024. Wikipedia's own article on the city now opens "Ahmednagar, officially Ahilyanagar," and Wikidata's (`Q223517`) English and Marathi labels already reflect the new name.

## Changes Made

Updated `contributions/cities/IN.json`, city id `147670`:

| Field | Before | After |
|-------|--------|-------|
| `name` | `Ahmednagar` | `Ahilyanagar` |
| `native` | `अहमदनगर` | `अहिल्यानगर` |
| `translations.br` | `Ahmednagar` | `Ahilyanagar` |
| `translations.pt-BR` | `Ahmednagar` | `Ahilyanagar` |
| `translations.pt` | `Ahmednagar` | `Ahilyanagar` |
| `translations.nl` | `Ahmednagar` | `Ahilyanagar` |
| `translations.hr` | `Ahmednagar` | `Ahilyanagar` |
| `translations.de` | `Ahmednagar` | `Ahilyanagar` |
| `translations.es` | `Ahmednagar` | `Ahilyanagar` |
| `translations.fr` | `Ahmednagar` | `Ahilyanagar` |
| `translations.it` | `Ahmednagar` | `Ahilyanagar` |
| `translations.tr` | `Ahmednagar` | `Ahilyanagar` |
| `translations.pl` | `Ahmednagar` | `Ahilyanagar` |

## Deliberately NOT changed — known gap

`translations.ko`, `.fa`, `.ja`, `.zh-CN`, `.ru`, `.uk`, `.hi`, `.ar` were left as their old-name transliterations (`아메드나가르`, `احمدنگر`, `アフマドナガル`, `艾哈迈德讷格尔`, `Ахмаднагар`, `Ахмеднагар`, `अहमदनगर`, `أحمد نجار`).

Checked Wikidata `Q223517` directly before editing: only its **English** and **Marathi** labels have been updated to the Ahilyanagar form so far — its Hindi, Russian, Ukrainian, Japanese, Korean, Persian, Arabic, and Chinese labels still show old-name transliterations as of this fix. Fabricating new transliterations into 8 non-Latin scripts without an authoritative source risks introducing incorrect data, so this dataset intentionally mirrors Wikidata's current (incomplete) state for those fields rather than guessing. `native` was updated because Marathi — the region's own language, and the field this dataset uses in place of a `translations.mr` entry — is confirmed renamed on Wikidata.

The `hi` (Hindi) translation was left unchanged for the same reason: Wikidata's own Hindi label is still the old-name form.

## Scope precedent

This follows the same shape as the prior [Gurgaon → Gurugram rename](./FIX_GURGAON_GURUGRAM_RENAME.md): update `name`, `native`, and the Latin-script translation fields (which this dataset otherwise stores as plain copies of the English name).

Postcode locality names in `contributions/postcodes/IN.json` (`Ahmednagar`, `Ahmednagar Camp`, `Ahmednagar R.S.`) were **not** touched — those are India Post's own postal-circle names, a separate naming authority from the municipal/administrative rename, and out of scope for this issue.

## Verification
- Wikipedia (`en.wikipedia.org/wiki/Ahmednagar`): confirms rename date and current official name.
- Wikidata `Q223517`: confirms per-language label state as described above.
- JSON validated after edit (`python3 -m json.tool` / `json.load`).

## Files Changed
- `contributions/cities/IN.json` — rename one record (id `147670`).
