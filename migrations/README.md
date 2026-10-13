# Migrations: what changed between two releases

From v5.0.0, each data release is meant to carry files that tell you how its records relate to an earlier
release's, so you can update ids stored in your own systems. They are generated, never edited by hand, by
[`bin/scripts/release/migrations.py`](../bin/scripts/release/migrations.py) from this folder's ledger and the git
history of `contributions/`.

**Status:** the generator is in place, but the export workflow does not run it yet and `events.jsonl` is still empty.
Both are done before v5.0.0 is published. Until then, no release carries these files.

## The files

| File | What it holds |
|---|---|
| `removed_ids.jsonl` | One line per removal in the interval, ids created and removed in between included. Each line has the reviewed event, the removed row (`before`), `present_at_from` and `current_targets`, which follows later removals to the records that exist in this release. |
| `removed_ids.csv` | v4.0's columns `record, old_id, name, country_code, state_code, outcome, new_table, new_id, source`, then `relation, automatic_redirect, event_commit`. One row per current target. A removal with no successor has one row with empty `new_table` and `new_id`. |
| `added_ids.jsonl` | Every id present in this release and not in the earlier one: table, id, name, file and the commit that added it. |
| `identity_changes.jsonl` | Reviewed identity events for ids that kept their number, with the row before and after (see below). |
| `changed_fields.jsonl` | One line per changed field of a record present in both releases. Each line gives `before` and `after` as typed JSON (`1`, `1.0` and `true` differ), plus `before_present` and `after_present`, so a missing field and a null one can be told apart. `translations` is compared per language (`translations.de`), or as a whole when one side is not an object. `created_at`, `updated_at` and `flag` are left out, because MySQL sets them. |
| `release_manifest.json` | The release metadata (data, contract, policy and data-schema versions, notices), the two commit SHAs, the migration format version (2), totals per table at both ends, and the removed, added and changed counts, which reconcile (`from_total - removed + added = to_total`). It also has counts per field path and the SHA-256 of every file above. |

## Outcomes and relations

| Outcome | Meaning | Targets (relation) | Redirect automatically? |
|---|---|---|---|
| `merged_same_entity` | A proved duplicate of the same place, kept under another id in the same table | exactly one (`merged_same_entity`) | only when the event says `automatic_redirect: true` |
| `administrative_seat` | A row for an administrative unit, removed; the town where the unit's seat is is a different place | the seat town (`administrative_seat`), plus the unit's own record elsewhere (`moved_dataset`) | no |
| `moved_dataset` | The record now lives in another table (e.g. a district moved from cities to counties) | the new record (`moved_dataset`), in another table | no |
| `territorial_successor` | A unit replaced after a merger or reform | the successor (`territorial_successor`) | no |
| `split_into` | A unit split into several | two or more (`split_into`) | no |
| `namespace_replaced`, `invalid_record`, `no_successor` | No successor, for the reviewed reason given | `[]` | no |

`automatic_redirect` must be `true` or `false` and may be `true` only for a reviewed `merged_same_entity`. A chain
(A merged into B, B later merged into C) resolves to C in `current_targets`. It redirects automatically only if every
hop does.

An identity event (`"event_type": "identity"`) records an id that kept its number while what it denotes was reviewed.
- `reclassified_same_entity`: the same place, with its category or depth corrected. No targets.
- `dual_role`: the row stands for both a unit and its seat. The target, if any, is the unit's own record (`moved_dataset`).
- `repurposed`: the number came to denote another entity. The targets are where the earlier entity is now
  (`prior_identity`).

## The ledger (`events.jsonl`)

There is one JSON object per line, cumulative across releases. A removal event has:

```json
{"schema_version": 1, "old_table": "cities", "old_id": 819,
 "event_commit": "<the first-parent commit where the id disappeared>", "before_commit": "<its first parent>",
 "before_path": "contributions/cities/AR.json", "before_row_sha256": "<SHA-256 of the removed row>",
 "outcome": "administrative_seat", "automatic_redirect": false,
 "targets": [{"table": "cities", "id": 1403, "relation": "administrative_seat"},
             {"table": "counties", "id": 6711, "relation": "moved_dataset"}],
 "review_status": "reviewed", "review": {"reason": "...", "reviewer": "..."}, "evidence": [{"...": "..."}]}
```

`before_row_sha256` is the SHA-256 of the row as UTF-8
`json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':'))`. An event may also carry the full
`before` row, which must hash to that value. Other fields (`event_pr_url`, `effective_date`, ...) are passed through.
An identity event uses `table` and `id` in place of `old_table` and `old_id`, and has no `before_commit` or
`before_path`. A `held` event is a placeholder: it fails the release wherever it applies.

## The reserved ids

`--reserved` names every id that left the data before `--from` and must never return, as `{"table", "id"}` per
line. Removals in ledger events before `--from` are added automatically. The list for v5.0.0 starts from v4.0's
published `removed_ids_v3.2_to_v4.0.csv`. It is prepared with the workflow integration.

## What makes the generator refuse

It exits 1 and writes nothing when any of these happens:

- A removal at any first-parent commit between the two releases has no reviewed event for that commit.
- An event's `before_commit`, `before_path` or `before_row_sha256` does not match the actual removal, or an event in
  the interval matches no removal.
- A target does not exist right after the event's commit.
- The ledger breaks the outcome rules above.
- An id is missing at either end, malformed, duplicated across files, or a retired or reserved id is in use.

Ids may be missing in between: contributors may omit ids on new rows until the import assigns them. Every id must
be final at `--to`.

## Generating the files

Pass commit SHAs, not branch names. `--from` is the previous **successful published** snapshot, not a failed draft
or a feature tag. `--to` is the release candidate. Both must be on one first-parent line and come from a full clone.
For v5.0.0, run it twice: v4.0 to v5 (cumulative) and export.51 to v5 (the step since the last export).

```bash
python3 bin/scripts/release/migrations.py --from <published snapshot sha> --to <candidate sha> \
  --ledger migrations/events.jsonl --reserved <reserved_ids.jsonl> --meta <release_meta.json> --out build/migrations
```

`release_meta.json` looks like this:

```json
{"data_version": "5.0.0", "contract_version": "5", "policy_version": "<date>", "data_schema_version": "5",
 "notices": [".github/licenses/SOURCES.txt"]}
```

The same inputs always give byte-identical files. On today's repository, a run reads about a million rows, needs
about 2.4 GB of memory and takes 25 to 65 seconds.

Tests: `cd bin/scripts/release && python3 -m unittest test_migrations`. The tests run on scratch git repositories.
