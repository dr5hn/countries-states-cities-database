# Disputed and special territories

This page sets out how the database records places where sovereignty, recognition or administration is disputed or
unusual, and how far the data follows that policy today. It applies to `countries`, `states`, `counties` and `cities`.
Related pages: [ADMINISTRATIVE_STRUCTURE.md](ADMINISTRATIVE_STRUCTURE.md) (units and levels) and
[MULTI_LEVEL_TERRITORIES.md](MULTI_LEVEL_TERRITORIES.md) (territories that are both a country and a subdivision).

## Policy

**Codes are lookups, not rulings.** Country and subdivision codes give stable geographic lookups. A code, country
name, subdivision entry, flag, dialing code, translation or timezone does not express a position on recognition,
sovereignty, a territorial claim or the legal status of a settlement.

**Code catalogues.** ISO 3166-1 and ISO 3166-2 are the default catalogues. `XK` (with `XKX` and `926`) is a documented
extension used for Kosovo; it is not an ISO assignment. Subdivision codes that ISO does not
publish (Kosovo's seven `XK-*` codes, Hong Kong's eighteen `HK-*` district codes) are project codes. A national reform
that takes effect before ISO updates its list is recorded with its effective date, its official sources and a crosswalk
from the old units to the new ones.

**One place partition per case.** Each place record has one country, under the case rules below. A subdivision of
another country that covers the same ground stays in the states list as a catalogue entry, with no places from the other
country under it. A unit that overlaps a special territory only partly may still hold verified places of its own
country. Names and suffixes such as `(EH)` and `(EH-partial)` are not boundary evidence. A place is never stored twice to
satisfy two claims.

| Case | Places belong to | Overlapping catalogue entries |
|---|---|---|
| Taiwan | `TW` | `CN-TW` |
| Hong Kong, Macao | `HK`, `MO` | `CN-HK`, `CN-MO` |
| Western Sahara | Verified Western Sahara places use `EH` | Moroccan units keep their catalogue identities with no `EH` places under them; units that overlap only partly may keep verified `MA` places |
| Kosovo | `XK` | Serbia's `RS-KM` and `RS-25` to `RS-29` |
| Crimea, Sevastopol and other places in Ukraine | `UA` | none |
| Abkhazia, South Ossetia | `GE` | none |
| Transnistria | `MD` | none |
| Northern Cyprus | `CY` | none |
| Nagorno-Karabakh | `AZ` | none |
| Golan Heights | `SY` | none |
| Somaliland | `SO` | none |
| Kashmir | the `IN`, `PK` or `CN` unit that administers the place | none |
| Arunachal Pradesh | `IN` | none |
| Falkland Islands; South Georgia and the South Sandwich Islands | `FK`, `GS` | Argentina's county `6832` Islas del Atlántico Sur, an administrative-claim entry; it does not assign these places to `AR` |
| Gibraltar | `GI` | none |
| West Bank, including East Jerusalem | `PS` | none |
| Åland | `AX` | see the status table |

**Names.** Country display names follow a documented, versioned convention based on Unicode CLDR (edition 48.2.0 for
this policy), including deliberately chosen short or variant forms: the English name chosen for `PS` in the next major
release is CLDR's short form "Palestine". Each change records the CLDR edition, locale and key it used; a same-entity
form that differs from the CLDR default is not an error for that reason alone. A translation that names a different
entity is an error and is corrected in an ordinary release. Changing a translation that names the right entity with a
political qualifier is a display-convention change: the owner checks the proposed forms and their effect on apps first,
the change is announced in advance, and it ships in the next major release, because apps display these names and some
markets require a particular form. `native` is the place's attested local name in its own script; other local or historical forms go in
`translations` where that language has a key. A translation names the same place in that language; it does not move the
place to another country. The full naming rule is in
[contributions/README.md](contributions/README.md#names-native-names-and-translations).

**Clocks, dialing codes and flags.** `timezone` follows the IANA time zone database, which can differ from a country's
usual zone (Crimea uses `Europe/Simferopol`). Dialing codes follow the ITU allocations and flags encode the stored code.
None of these is evidence of sovereignty or of a place's identity.

**No invented codes.** No country or ISO subdivision code is made up to fill a gap. The Cyprus sovereign base areas
have no code; a place proved to lie only inside a base area needs its own documented exception first.

**Changes.** Regular data releases correct facts about the same places under the published model, including moving a
proved misfiled record to its right country or state; query results change as facts are corrected. Within a major, every
existing id keeps working; a crosswalk alone does not achieve that. Removing ids, moving a record to another dataset or
scope, changing how a country or case is stored, and incompatible schema or query-rule changes ship only in a major
release, coordinated across the exports, API and packages. A unit record stays distinct from its seat town, and both ids
of a proved duplicate stay until the removal ships in a major. Every release names its data snapshot and carries its
removal mappings and changed fields; a mapping says whether it is the same place merged, an administrative seat, a move
to another dataset, a split or an invalid record. Ids are never reused for a different place.

## Status on master

The policy above is the target. This table shows where the data stands today, so nobody reads it as a claim that every
record already complies.

| Case | Today | Still to do |
|---|---|---|
| Taiwan | `TW`: 22 states, 377 cities. `CN-TW` (state 2255) still has 20 rows, 159996 to 160015, for Taiwan's own units. The Japanese and Chinese country translations carry a qualifier (台湾（中華民国）, 中国台湾). | Retire the 20 rows with a crosswalk to the matching `TW` states. The CLDR form 台湾 for both translations. Both in the major release. |
| Hong Kong, Macao | `HK`: 18 districts, 27 cities. `MO`: no states or cities yet (a coverage gap). `CN-HK` (state 2267) still has 18 district rows, 159978 to 159995; `CN-MO` (2266) has none. | Retire the 18 rows with a crosswalk to the matching `HK` states (major release). |
| Western Sahara | `EH` has no states or cities. Three cities sit under the Moroccan unit Oued Ed-Dahab (EH): 67064 Aousserd, 67134 Imlili, 67182 Oued-Ed-Dahab. | Seven records are under review one by one (67064, 67089, 67127, 67134, 67154, 67182, 67220). Places proved to be in Western Sahara move to `EH` once a city can be stored without a state, as `EH` has no ISO subdivisions (schema change, major release). Imlili's wrong Wikidata item was cleared in #2009. |
| Kosovo | `XK`: 7 states, 59 cities. Serbia's six Kosovo units, states 5688 to 5693, hold no places. | None. |
| Palestine | `PS`: 16 states, 132 cities. English name "Palestinian Territory Occupied", and "occupied" forms in five translations (ru, uk, pl, hi, ar). East Jerusalem's point fixed in #2009. Har Adar (57475) and Modiin Ilit (57514), West Bank settlements, are stored under `IL`. | English display name "Palestine" (CLDR 48.2.0 short form), keeping the old name as an alias, and the CLDR forms of the five translations (major release, after the owner's check). Move the two settlements to `PS` with their governorate after review. Nirit (57526) and Bāqa el Gharbīya (164832) stay held for boundary review; the whole of Jerusalem stays a record distinct from its parts. |
| Ukraine | Crimea and Sevastopol: 369 cities under `UA`, all on `Europe/Simferopol` since #2009. Ten rows named "Gorodskoy okrug …" (109610 to 109619) use Russian unit names. | Review the ten rows as units, and reopen the 286 Crimean and Sevastopol records held in #2005 under the current Ukrainian codifier (KATOTTG), its enacted names and romanisation. All 286 still exist; 285 still share a Wikidata item with another record, and 110403 needs its own identity check. |
| Cyprus | `CY`: 6 states, 96 cities. Turkish country name "Kıbrıs" since #2009. | None. |
| Georgia, Moldova, Azerbaijan, Syria, Somalia | Places stored under `GE`, `MD`, `AZ`, `SY`, `SO`. | Membership is kept. Local-name, item, scope and clock reviews remain open where found, including dated renaming research in Azerbaijan for Askyaran (8046), Martakert (8114) and Novyy Karanlug (8125). Somalia's state 5700 has the native name Maroodi Jeex, the name the Somaliland administration uses; whether it covers the same ground as ISO's Woqooyi Galbeed is under review. |
| Kashmir, Arunachal Pradesh | Places stored under `IN`, `PK` and `CN` units. | Not yet checked place by place. |
| Falkland Islands; South Georgia and the South Sandwich Islands | `FK` and `GS` have no states or cities yet (coverage gaps). Argentina's county 6832 has no cities linked to it. | Coverage is incomplete; county 6832's point source and represented scope are under review. |
| Gibraltar | `GI` has no states or cities yet (a coverage gap). | Coverage is incomplete. |
| Åland | `AX`: 16 states, 12 cities. Finland's states do not include `FI-01` Åland. | Decided: restore `FI-01` as an empty catalogue state of `FI` in a separate data PR, keeping `AX`'s places. The former state 1509 is checked before it is restored, and #1144's removal of duplicate Finnish place rows stands. |

Counts and ids are from `contributions/` on master at `dea03811` (13 October 2026). They describe stored rows, not
complete coverage or a finished place-by-place check of identity, language, clock or point source. Changes already made
have their sources and record ids in [FIX_1643_SUMMARY.md](.github/fixes-docs/FIX_1643_SUMMARY.md); open work is listed
here.

## Earlier methods replaced from 13 October 2026

Older fix notes record the method used at the time; they do not authorise repeating it.

- ADMINISTRATIVE_STRUCTURE.md rules 1 to 8 replace the old three-level-only model, the removal of regional units and the
  blanket refusal of sub-city places (#168, #367, #375, #427, #443, #461, #476, #531, #926). Each proposed place still
  needs its own evidence.
- Rule 8 and the source-rights policy replace copying points from Google Maps links without a documented basis to
  redistribute them (#207, #364). Older points are checked one by one; this is not a finding that any point infringes.
- Only the same current place at the same scope is merged. A shared name, distance, population, Wikidata item or code
  only nominates a pair (#236, and the population test in #1643's first checklist). A proved merge also follows the
  release rule above.
- The versioned release rule above replaces flush-and-reload upgrade advice (#818).
- Attested local names replace the country-primary-language and all-India Devanagari rule for `native` (#1379's native
  rule, #1741). #1379's English or international `name` rule stays; #1339's refusal to lose valid units or add unsourced
  translations still stands.
- Attested translations replace machine translation and copying the record's name into a language with no label
  (#1148, and #1602, #1707, #1721, #1722, #1725, #1729, #1730, #1733, #1734, #1735, #1738, #1739, #1741, #1743,
  #1746). No new value is copied from `name`. Existing copies are decided per language and place: kept where that form is
  attested, replaced by an attested name, or removed where proved wrong; unresolved ones are held. None is removed only
  because it equals `name`. `translation_enricher.py` is not to be used until its sources and identity checks are
  reviewed.
- The Australian and Spanish postcode mirrors from #1434 and #1437 were replaced in #1973 and #1974. The wrong Turkish
  name for Cyprus from #425 was corrected in #2009. The Taiwan and Hong Kong unit rows added under China in #1289 wait
  for the major-release crosswalk.

## Past decisions this policy keeps

- Western Sahara stays a separate entry, following ISO 3166 (#1329, #1334).
- Kosovo is its own entry with its own places (#99, #102); Serbia's ISO units were restored without places (#1184, #1261).
- Hong Kong and Macao stay separate entries, by design (#337, #1025).
- Taiwan stays a separate entry with no political stance intended (#337). #574 was pointed to that discussion, #585 was
  closed as a duplicate, and #586 was asked for an authoritative source and closed unmerged; none adopted "Taiwan,
  China" or "Taipei" as the display name.
