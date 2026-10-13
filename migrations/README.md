# Migrations: what changed between two releases

Every data release carries four files that tell you how its records relate to the previous release's, so you can
update ids stored in your own systems. They are generated, never edited by hand, by
[`bin/scripts/release/migrations.py`](../bin/scripts/release/migrations.py) from this folder's ledger and the two
releases' `contributions/`.

| File | What it holds |
|---|---|
| `removed_ids.jsonl` | One line per id that left the data: its table and id, the reviewed outcome, its targets and whether you may redirect automatically. |
| `removed_ids.csv` | The same, one row per relation (an id that became a county and also points to its seat town has two rows; an id with no successor has one row with empty targets). |
| `changed_fields.jsonl` | One line per changed field of a record that kept its id (`translations` per language, e.g. `translations.de`). |
| `release_manifest.json` | Both releases' commits, counts per table (removed, added, changed) and per field, and the SHA-256 of the three files above. |

## Outcomes

| Outcome | Meaning | Targets | Redirect automatically? |
|---|---|---|---|
| `merged_same_entity` | A proved duplicate of the same place at the same scope, kept under the older id. | the kept record | yes |
| `administrative_seat` | A row for an administrative unit, removed; the target is the town where the unit's seat is, a different place. | the seat town | no |
| `moved_dataset` | The record now lives in another dataset (e.g. a district moved from cities to counties). | the new record | no |
| `territorial_successor` | A unit replaced by another unit after a merger or reform. | the successor | no |
| `split_into` | A unit split into several units. | every successor | no |
| `namespace_replaced` | The values belonged to another code system (e.g. municipality codes stored as postcodes); no successor. | none | no |
| `invalid_record` | Not a real place or record; no successor. | none | no |
| `no_successor` | Withdrawn for a stated reason with no successor. | none | no |

Ids are never reused: a retired id never denotes another record.

## The ledger

`events.jsonl` holds one reviewed event per removed id, cumulative across releases, with at least `old_table`,
`old_id`, `outcome`, `targets` (`[{"table", "id", "relation"}]`), `automatic_redirect` and `review_status:
"reviewed"`, plus the evidence for the decision. A release is refused when a removed id has no reviewed event, a target
does not exist, a redirect is claimed for anything other than `merged_same_entity`, or a retired id is in use again.

## Generating the files

```bash
python3 bin/scripts/release/migrations.py --from <previous release tag> --to HEAD \
  --ledger migrations/events.jsonl --out build/migrations
```

The same inputs always give byte-identical files. Tests: `cd bin/scripts/release && python3 -m unittest test_migrations`.
