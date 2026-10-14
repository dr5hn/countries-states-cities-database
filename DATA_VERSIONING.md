# Data versioning: what an id means and what a release may change

This page is the contract between the data and the people who store its ids. It applies from v5.0.0. It says what an
id denotes, what each kind of release may change, how to pin a release, and how to migrate stored ids between
releases.

## What an id denotes

A **key** is a table plus an id, for example `cities` 1403 or `states` 1509. A key identifies one geographic entity,
such as a town, a municipality or a province. It does not identify a fixed set of attributes.

- Facts about the entity are corrected under the same key: its spelling, local name, translations, coordinates
  (`latitude`, `longitude`), time zone (`timezone`), Wikidata item, type and level, and its links to a parent, county
  or state.
- A different entity never gets an existing key. A different settlement, territorial unit, part of a unit or
  successor after a reform gets its own key, and the records are linked.
- A retired key is never used for anything else. The release that retires it says what became of the entity. The
  only way back is a reviewed restoration of the **same** entity, checked against the row the key had when it was
  retired. Both rows must carry the same stable identifier, such as the Wikidata item or the ISO 3166-2 code, and no
  conflicting one. Åland (FI-01, `states` 1509) is the first.
- A `dual_role` decision needs evidence for both roles under the country's published model, and creates no automatic
  redirect. Under rule 7 of [ADMINISTRATIVE_STRUCTURE.md](ADMINISTRATIVE_STRUCTURE.md), an intermediate unit has its
  own county record, and a separately verified place keeps its city record, identity and level, linked through
  `county_id`. A shared Wikidata item allowed by that model does not make a seat town equal to the unit's territory.

Some records predate typing, and what they first denoted (a town, or the municipality around it) can no longer be
established. These keys get an `unresolved` identity decision, and never redirect automatically. A later type, local
type (`type_local`), level, `parent_id` or `county_id` is kept on such a key only when the evidence ties it to the
entity the key already denoted; otherwise the field keeps its v4.0 value, or stays absent if it had none. An unproved
change of Wikidata item keeps the v4.0 item; if evidence proves that old item wrong but proves no replacement, the key
has no item. Facts that are proved stay; unproved assertions that would tie the key to another entity do not ship.

`identity_changes.jsonl` holds the decisions made in its release's interval, so a key missing from a later file is
not resolved by that. Before v5.0.0 is published, its cumulative identity file must also provide a complete reviewed
baseline of every retained unresolved key, including legacy rows unchanged since v4.0. Starting from that verified
baseline, apply subsequent identity decisions in order and retain each key's latest decision. Absence from a later
file does not resolve a key. Strict territorial consumers exclude the keys whose latest decision is unresolved.

## What each kind of release may change

Releases are numbered `vMAJOR.MINOR.PATCH`, for example `v5.0.0` and then `v5.1.0`. Each published export of a
release has its own tag, `v5.0.0-export.1`, `v5.0.0-export.2` and so on, bound to the commit it was built from.
Exports can hold different data. Changes between published snapshots within one major follow the regular-release
rules below. The first published export of a new major may include the changes allowed only in a major.

| Change | Regular release (minor or patch) | Major release |
|---|---|---|
| Correct a fact about the same entity (name, translation, coordinates, time zone, item, population) | yes | yes |
| Correct a type, level or parent under the published rules | yes | yes |
| Add records (new places, counties, postcodes) | yes | yes |
| Move a misfiled place to its proved state or country | yes | yes |
| Remove a key, or move it to another table | no | yes |
| Repair a key that came to denote another entity (the key retires with its first meaning; the other entity gets a fresh, never-used key, or an existing key already proved to denote it) | no | yes |
| Change a field's meaning or nullability, an id namespace, a table's scope, how countries, codes or letter case are written, or an incompatible schema or documented query rule | no | yes |

The results of an unchanged query may change when facts about the same entity are corrected.

Between majors, existing keys stay lookupable. A record found to be a unit or invalid is classified or flagged only
where the published model allows it; otherwise that change is held. Both keys of a duplicate stay, with the proof
recorded. Removing a key or moving it to another table waits for the next major.

## Pinning and migrating

Pin the exact export tag and its commit, or the commit of the snapshot your product actually ships, not "latest". A
package version or an API protocol version alone does not name a data snapshot. The API and the packages report the
data version they serve; a live API client picks its data version as the API documentation describes.

Each release attaches migration files to its GitHub release, described in
[migrations/README.md](migrations/README.md). They cover `countries`, `states`, `counties`, `cities` and `postcodes`.
They do not describe changes to the separate `regions` and `subregions` grouping tables.

- `removed_ids.jsonl` and `removed_ids.csv`: every removal event in the interval, with its reviewed outcome. This is a
  history of events, not the list of keys absent at the end: check `present_at_from` and `present_at_to`. A key
  present at the end is not retired because a removal event names it. `restored_at` marks a removal undone later by a
  reviewed restoration; its `current_targets` then follow the restored key. `present_at_from: false` marks a key
  your baseline never held.
- `current_targets` follows each removal's relations to the end of the interval. It may list one or more
  `{table, id}` targets (several after a split), be empty when the outcome has no successor, or hold a terminal
  `{"table": null, "id": null, "end": <outcome>}` when a chain ends in a removal with no successor. Only a target with
  `automatic_redirect: true` may be redirected without a look: every step to it is a reviewed `merged_same_entity`,
  and a repurpose or an `unresolved` decision on the way ends that. A seat town is a different place from the unit
  whose seat it is.
- For a repaired key, `current_targets` is the entity it first denoted, and `later_entity_targets` the replacement key
  of the entity it came to denote: check which one you stored. The removal's `retires_repurpose.replacement_kind`
  says whether the replacement is `fresh` (never used before) or `existing`, and the identity decision's `remediation`
  records it too. Neither mapping redirects automatically. An existing replacement may appear in `added_ids.jsonl` if
  it was absent from your baseline and is present at the target; `replacement_kind` is not an added-file membership
  test.
- `added_ids.jsonl`: keys present at the end and not at the start. A restored key appears with `restored` when your
  baseline lacks it; a key present at both ends does not appear, even if it was removed and restored in between.
- `changed_fields.jsonl`: the fields that changed on keys present at both ends, typed, with presence flags.
- `identity_changes.jsonl`: the identity decisions made in the interval (see above).
- `release_manifest.json`: the versions, both commits (`from.sha` and `to.sha`), the counts and the checksums.

To migrate stored ids, take a set whose `release_manifest.json` starts at your snapshot (`from.sha`) and ends at the
one you move to (`to.sha`), and apply it; then do the same with the next release's set. Each set describes the step
from the previous published snapshot. v5.0.0 carries two: the cumulative set from v4.0, and the step from the last v4
export (`v4.0-export.51`). Apply the one whose `from.sha` is your snapshot, never both.

Example: list the stored city ids that may be redirected to another record.

```bash
python3 -c "
import json
for line in open('removed_ids.jsonl', encoding='utf-8'):
    e = json.loads(line)
    if e['old_table'] != 'cities':
        continue
    for t in e['current_targets']:
        if t['automatic_redirect']:
            print(e['old_table'], e['old_id'], '->', t['table'], t['id'])
"
```

It prints the mappings; updating your stored ids is up to you.

## Support

When v5.0.0 is published, the API keeps serving v4 data for six months, and v4's downloads stay available. The release
notes give the exact dates.

## Where the rules come from

The rules for places, types and hierarchy are in [ADMINISTRATIVE_STRUCTURE.md](ADMINISTRATIVE_STRUCTURE.md) and
[TYPE_FIELD.md](TYPE_FIELD.md). The rules for disputed and special territories are in
[DISPUTED_AND_SPECIAL_TERRITORIES.md](DISPUTED_AND_SPECIAL_TERRITORIES.md). Source credits are in
[.github/licenses/SOURCES.txt](.github/licenses/SOURCES.txt).
