# Data versioning: what an id means and what a release may change

This page is the contract between the data and the people who store its ids. It applies from v5.0.0. It says what an
id denotes, what each kind of release may change, how to pin a release, and how to migrate stored ids between
releases.

## What an id denotes

A **key** is a table plus an id, for example `cities` 1403 or `states` 1509. A key identifies one geographic entity,
such as a town, a municipality or a region. It does not identify a fixed set of attributes.

- Facts about the entity are corrected under the same key: its spelling, local name, translations, point, clock,
  Wikidata item, type and level, and its links to a parent, county or state.
- A different entity never gets an existing key. A different settlement, territorial unit, part of a unit or
  successor after a reform gets its own key, and the records are linked.
- A retired key is never used again. The release that retires it says what became of the entity.
- One record may stand for a unit and its main place only where the country's documented model allows it
  (ADMINISTRATIVE_STRUCTURE.md, rule 7). Such a dual record does not make the seat town equal to the unit's
  territory.

Some records predate typing, and what they first denoted (a town, or the municipality around it) can no longer be
established. Each release lists these keys as `unresolved` in its identity file, with what is known. On these keys,
a municipal type states the national category, not a proved territorial boundary. If you need strict territorial
scope, exclude them by that list.

## What each kind of release may change

Releases are tagged `vMAJOR.MINOR.PATCH`, for example `v5.0.0` and then `v5.1.0`. The exports of a release are
tagged `v5.0.0-export.1`, `v5.0.0-export.2` and so on.

| Change | Regular release (minor or patch) | Major release |
|---|---|---|
| Correct a fact about the same entity (name, translation, point, clock, item, population) | yes | yes |
| Correct a type, level or parent under the published rules | yes | yes |
| Add records (new places, counties, postcodes) | yes | yes |
| Move a misfiled place to its proved state or country | yes | yes |
| Remove a key, or move it to another table | no | yes |
| Repair a key that came to denote another entity | no | yes |
| Change a field's meaning, a nullability, a table's scope or a documented query | no | yes |

Between majors, a record that turns out to be a unit, a duplicate or invalid stays in the data, typed as what it is.
Its removal is queued for the next major.

## Pinning and migrating

Pin a release by its tag or commit, not by "latest". The API and the packages report the data version they serve.

Each release attaches migration files, described in [migrations/README.md](migrations/README.md):

- `removed_ids.jsonl` and `removed_ids.csv`: every key that left the data, with its reviewed outcome and the records
  that exist now. Only `merged_same_entity` with `automatic_redirect: true` may be redirected without a look. A seat
  town is a different place from the unit whose seat it is.
- `added_ids.jsonl`, `changed_fields.jsonl` and `identity_changes.jsonl`: what was added, which fields changed (typed,
  with presence flags), and the identity decisions.
- `release_manifest.json`: the versions, both commits, the counts and the checksums.

To migrate stored ids, apply the files of each release since the one you pinned, in order. The files describe the
step from the previous published release. v5.0.0 also carries the cumulative files from v4.0.

Example: map stored city ids that were merged into another record.

```bash
python3 -c "
import json
for line in open('removed_ids.jsonl', encoding='utf-8'):
    e = json.loads(line)
    for t in e['current_targets']:
        if t['automatic_redirect']:
            print(e['old_table'], e['old_id'], '->', t['table'], t['id'])
"
```

## Support

When v5.0.0 is published, the API keeps serving v4 data for six months, and v4's downloads stay available. The release
notes give the exact dates.

## Where the rules come from

The rules for places, types and hierarchy are in [ADMINISTRATIVE_STRUCTURE.md](ADMINISTRATIVE_STRUCTURE.md) and
[TYPE_FIELD.md](TYPE_FIELD.md). The rules for disputed and special territories are in
[DISPUTED_AND_SPECIAL_TERRITORIES.md](DISPUTED_AND_SPECIAL_TERRITORIES.md). Source credits are in
[.github/licenses/SOURCES.txt](.github/licenses/SOURCES.txt).
