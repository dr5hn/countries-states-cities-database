# Fix Summary: Rename "Ahmednagar" to "Ahilyanagar" (Maharashtra, India)

## Issue Reference
**Original Issue:** [#1615](https://github.com/dr5hn/countries-states-cities-database/issues/1615) — Update the city name -> ahmadnagar to ahilyanagar

## Executive Summary

Ahmednagar (Maharashtra, India, city id `147670`) was officially renamed **Ahilyanagar** in honor of the 18th-century Maratha queen Ahilyabai Holkar. The Maharashtra government announced the rename on 31 May 2023, the state cabinet formally approved it on 13 March 2024, and the state government notified the change on 8 October 2024. Wikipedia's own article on the city now opens "Ahmednagar, officially Ahilyanagar."

## Changes Made

Updated `contributions/cities/IN.json`, city id `147670`:

| Field | Before | After |
|-------|--------|-------|
| `name` | `Ahmednagar` | `Ahilyanagar` |
| `native` | `अहमदनगर` | `अहिल्यानगर` |
| `translations.hi` | `अहमदनगर` | `अहिल्यानगर` |

No other fields were touched.

## Revision history on this fix

The first version of this fix additionally changed 11 Latin-script `translations` fields (`br`, `pt-BR`, `pt`, `nl`, `hr`, `de`, `es`, `fr`, `it`, `tr`, `pl`) to `Ahilyanagar`, on the assumption — based on the precedent set by the prior [Gurgaon → Gurugram rename](./FIX_GURGAON_GURUGRAM_RENAME.md) — that simple Latin-alphabet copies of the English name would track the rename automatically, and left `translations.hi` unchanged based on an initial (incorrectly summarized) read of Wikidata `Q223517`'s labels.

Both of those were wrong, caught by an automated PR review (Pullfrog) and independently confirmed by querying Wikidata's raw entity JSON directly (`https://www.wikidata.org/wiki/Special:EntityData/Q223517.json`) rather than a rendered/summarized page fetch:

- `Q223517`'s **Hindi** (`hi`) and **Marathi** (`mr`) labels *are* `अहिल्यानगर` — the rename did propagate there. `translations.hi` needed to change; the original fix had this backwards.
- `Q223517`'s labels for **every one of the 11 Latin-script languages touched** are still on an *old*-name form — several aren't even `Ahmednagar`; `fr`/`pt`/`pt-BR` are `Ahmadnagar`, a different transliteration entirely. None of them had adopted `Ahilyanagar`. Those 11 fields were reverted to their original pre-fix values.

Lesson for future similar fixes: don't infer that Latin-script "plain copy" translation fields will track a rename just because that pattern happened to hold in an earlier, different fix — check each per-language Wikidata label directly (via the raw `Special:EntityData/<Q-id>.json` endpoint, not a summarized page render, which can misreport which script/field it's reading) before changing it.

## Deliberately NOT changed — known gap

`translations.ko`, `.fa`, `.ja`, `.zh-CN`, `.ru`, `.uk`, `.ar` were left as their old-name transliterations (`아메드나가르`, `احمدنگر`, `アフマドナガル`, `艾哈迈德讷格尔`, `Ахмаднагар`, `Ахмеднагар`, `أحمد نجار`) — confirmed via Wikidata's raw entity data that none of these languages' labels have been updated for this rename as of this fix. `translations.br`, `.pt-BR`, `.pt`, `.nl`, `.hr`, `.de`, `.es`, `.fr`, `.it`, `.tr`, `.pl` were likewise left on the old name for the same reason (see revision history above).

Fabricating new transliterations/translations into scripts and languages Wikidata itself hasn't updated risks introducing incorrect data, so this dataset intentionally mirrors Wikidata's current (incomplete) per-language state rather than guessing.

## Scope precedent

`native` was updated because Marathi — the region's own language, and the field this dataset uses in place of a `translations.mr` entry — is confirmed renamed on Wikidata.

Postcode locality names in `contributions/postcodes/IN.json` (`Ahmednagar`, `Ahmednagar Camp`, `Ahmednagar R.S.`) were **not** touched — those are India Post's own postal-circle names, a separate naming authority from the municipal/administrative rename, and out of scope for this issue.

## Verification
- Wikipedia (`en.wikipedia.org/wiki/Ahmednagar`): confirms rename date and current official name.
- Wikidata `Q223517` raw entity JSON (`Special:EntityData/Q223517.json`): confirms the exact per-language label state described above — this is the authoritative check; a rendered-page summary was checked first but proved unreliable and was superseded by this direct JSON read.
- JSON validated after edit (`python3 -m json.tool` / `json.load`).

## Files Changed
- `contributions/cities/IN.json` — rename one record (id `147670`); 3 fields changed (`name`, `native`, `translations.hi`).
