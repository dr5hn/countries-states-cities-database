# Migrations: what changed between two releases

From v5.0.0, each data release is meant to carry files that tell you how its records relate to an earlier
release's, so you can update ids stored in your own systems. They are generated, never edited by hand, by
[`bin/scripts/release/migrations.py`](../bin/scripts/release/migrations.py) from this folder's ledger and the git
history of `contributions/`.

**Status:** the generator is in place, but the export workflow does not run it yet. `events.jsonl` holds every removal
since v4.0 (10,201) and the 1509 restoration. 9,862 removals are reviewed; 339 cities removals are still `held`, so
the generator refuses every release until they are decided. The workflow and those decisions come before v5.0.0 is
published. Until then, no release carries these files.

## The files

| File | What it holds |
|---|---|
| `removed_ids.jsonl` | One line per removal in the interval, ids created and removed in between included. Each line has the reviewed event, the removed row (`before`), `present_at_from`, `present_at_to` and `current_targets`, which follows later removals to the records that exist in this release. The removal of a repurposed id also has `repurposed_at` and `later_entity_targets` (see below). `restored_at` marks an id the same entity got back later. |
| `removed_ids.csv` | v4.0's columns `record, old_id, name, country_code, state_code, outcome, new_table, new_id, source`, then `relation, automatic_redirect, event_commit`. One row per current target. A removal with no successor has one row with empty `new_table` and `new_id`. Rows for `later_entity_targets` follow, with a `relation` starting `later_entity>` and `automatic_redirect` `no`. |
| `added_ids.jsonl` | Every id present in this release and not in the earlier one: table, id, name, file and the commit that added it. An id a reviewed restoration brought back also has `restored` (its event and retirement commits). |
| `identity_changes.jsonl` | Reviewed identity decisions on ids that kept their number at the time, with the row before and after and the current targets. A repurpose has `remediation`: the removal that retired the id and the other entity's replacement. A repurpose decided before `--from` is listed again, with `event_before_from: true`, when the removal that retires it (`retires_repurpose`) is in this interval; other earlier decisions are not repeated. |
| `changed_fields.jsonl` | One line per changed field of a record present in both releases. Each line gives `before` and `after` as typed JSON (`1`, `1.0` and `true` differ), plus `before_present` and `after_present`, so a missing field and a null one can be told apart. `translations` is compared per language (`translations.de`), or as a whole when one side is not an object. By policy, `created_at`, `updated_at` and `flag` are left out: they are bookkeeping, not facts about the place (the importer keeps the values a file gives and fills missing ones). |
| `release_manifest.json` | The release metadata (data, contract, policy and data-schema versions, notices), the two commit SHAs, the migration format version (2), totals per table at both ends, and the removed, added and changed counts, which reconcile (`from_total - removed + added = to_total`). It also has counts per field path and the SHA-256 of every file above. |

## Outcomes and relations

| Outcome | Meaning | Targets (relation) | Redirect automatically? |
|---|---|---|---|
| `merged_same_entity` | A proved duplicate of the same place, kept under another id in the same table | exactly one (`merged_same_entity`) | only when the event says `automatic_redirect: true` |
| `administrative_seat` | A row for an administrative unit, removed; the town where the unit's seat is is a different place | the seat town (`administrative_seat`), and the unit's own record elsewhere (`moved_dataset`) when one exists | no |
| `moved_dataset` | The record now lives in another table (e.g. a district moved from cities to counties) | the new record (`moved_dataset`), in another table | no |
| `territorial_successor` | A unit replaced after a merger or reform | the successor (`territorial_successor`) | no |
| `split_into` | A unit split into several | two or more (`split_into`) | no |
| `namespace_replaced`, `invalid_record`, `no_successor` | No successor, for the reviewed reason given | `[]` | no |

`automatic_redirect` must be `true` or `false` and may be `true` only for a reviewed `merged_same_entity`. A chain
(A merged into B, B later merged into C) resolves to C in `current_targets`. It redirects automatically only if every
hop does.

An identity event (`"event_type": "identity"`) records a review of what an id denotes, at the commit where its record
changed while keeping the number (the four outcomes of decisions_4_final.md):
- `classification`: the same entity, with its category or depth corrected. No targets.
- `dual_role`: the row stands for a place and its unit. The target, if any, is the unit's own record (`moved_dataset`).
- `repurpose`: the number came to denote another entity. The targets are where the earlier entity is now
  (`prior_identity`). A repurposed id may not remain at `--to`. It must be retired by a later reviewed removal that
  says so in `retires_repurpose` (below), before it can be repurposed again: a second repurpose of an id whose first is
  not yet remediated is refused. The old id then keeps its earlier meaning: its `current_targets` are the
  repurpose's `prior_identity`, and the entity the number came to denote is listed apart in `later_entity_targets`.
  Neither redirects automatically.
- `unresolved`: what the row first denoted is not established. No targets.

`current_targets` follows each target forward in history. A removal passes to its own targets. A repurpose passes to
the earlier entity (`prior_identity`), and an `unresolved` decision keeps the key: both end any automatic redirect. A
removal followed by a restoration of the same id continues at that id, with the relation `restored` and no automatic
redirect; the removal's own line then maps the id to itself. A
path that ends in a removal with no successor is listed with `"end": <outcome>` and no table or id. Each step moves to a
later event, so every path ends. Identical results are listed once. More than 1,000,000 steps from one record (only
possible with a large fan-out of splits) is refused as an expansion limit.

A restoration (`"event_type": "restoration"`) brings a retired id back for the **same** entity, such as Finland's
state FI-01 (states 1509), retired by #1144 and restored by #2020. It is checked against history: the id returns at
`event_commit` with the row hashed in `restored_row_sha256`; it left its whole table at `retirement_commit`, earlier on
the same first-parent line, with the row hashed in `retired_row_sha256`; both rows hold the values in `same_identity`;
and no stable identifier (`wikiDataId`, `iso3166_2`, `iso3`) that both rows hold differs. `retirement_commit` must be
the id's latest disappearance in the history read, and a removal that remediated a repurpose (it took away the later
entity) cannot be restored. A restored id that leaves again, even before `--from` without a ledger event, needs a new
restoration to return. `same_identity` must bind at
least one of those three with a nonblank value: a shared country, category or name does not prove the same entity. An
id a reviewed removal retired may return only this way, before `--from` as well as inside the interval; a reserved id
may not be present at `--from` or return inside the interval without it.

## The ledger (`events.jsonl`)

There is one JSON object per line, cumulative across releases. A removal event has:

```json
{"schema_version": 1, "old_table": "cities", "old_id": 819,
 "event_commit": "<the first-parent commit where the id disappeared>", "before_commit": "<its first parent>",
 "before_path": "contributions/cities/AR.json", "before_row_sha256": "<SHA-256 of the removed row>",
 "outcome": "administrative_seat", "automatic_redirect": false,
 "targets": [{"table": "cities", "id": 1403, "relation": "administrative_seat"},
             {"table": "counties", "id": 6711, "relation": "moved_dataset"}],
 "review_status": "reviewed", "review": {"reason": "...", "reviewer": "..."},
 "evidence": [{"manifest": "research/<manifest>.json", "sha256": "<its SHA-256>"}]}
```

`before_row_sha256` is the SHA-256 of the row as UTF-8
`json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':'))`. An event may also carry the full
`before` row, which must hash to that value. Other fields (`event_pr_url`, `effective_date`, ...) are passed through.
An identity event uses `table` and `id` in place of `old_table` and `old_id`, and has no `before_commit` or
`before_path`.

`evidence` is a non-empty list. Each item is either a source URL, `{"url": "https://<host>/<path>"}` (http or https,
with a host and no spaces), or a research manifest and its hash, `{"manifest": "research/<file>.json", "sha256":
"<64 hex digits>"}`. Only the shape is checked; sources are not fetched. Research manifests are kept in the maintainers' audit workspace,
not in this repository; `event_pr_url` links the public PR that made the change.

The removal that retires a repurposed id names the repair:

```json
{"retires_repurpose": {"identity_event_commit": "<the repurpose's event_commit>",
                       "replacement": {"table": "cities", "id": 166001}, "replacement_kind": "fresh"}}
```

The replacement must be one of the removal's targets, and the removal cannot redirect automatically. `fresh` means a
never-used id: it first appears after the repurpose, was never removed (and so never restored) in the history read,
and is not reserved. `existing` means an id that was already there before this removal, proved the same entity by the
review.

A restoration event:

```json
{"schema_version": 1, "event_type": "restoration", "table": "states", "id": 1509,
 "event_commit": "<commit where the id returns>", "retirement_commit": "<commit that removed it>",
 "retired_row_sha256": "<SHA-256 of the removed row>", "restored_row_sha256": "<SHA-256 of the returned row>",
 "same_identity": {"iso3166_2": "FI-01", "wikiDataId": "Q5689"},
 "review_status": "reviewed", "review": {"reason": "...", "reviewer": "..."},
 "evidence": [{"url": "https://github.com/dr5hn/countries-states-cities-database/pull/2020"}]}
```

A `held` event is a placeholder. It fails the release wherever it applies, before `--from` as well as inside the
interval; only a later release's events are ignored.

## The reserved ids

`--reserved` names every id that left the data before `--from` and must never return, as `{"table", "id"}` per
line. Removals in ledger events before `--from` are added automatically. The list for v5.0.0 starts from v4.0's
published `removed_ids_v3.2_to_v4.0.csv`: its 4,492 ids are in [`reserved_ids.jsonl`](reserved_ids.jsonl).

The importer (`bin/scripts/sync/import_json_to_mysql.py`) reads the same files, `events.jsonl` (its removals) and
`migrations/reserved_ids.jsonl`, and starts the ids it assigns to new records above the highest retired or reserved id
of each table, so a retired id is never handed to a new record. MySQL also keeps them above the highest id present. A
malformed line in either file stops the import.

## What makes the generator refuse

It exits 1 and writes nothing when any of these happens:

- An event's commit is not on the release line: inside the interval, before `--from` on its first-parent history,
  or after `--to` on a later release's (also when `--to` is the first commit).
- A removal at any first-parent commit between the two releases has no reviewed event for that commit.
- An event's `before_commit`, `before_path` or `before_row_sha256` does not match the actual removal, or an event
  matches no removal. Events before `--from` get the same checks as those inside the interval, targets and holds
  included: the walk starts at the first parent of the oldest of them.
- A target does not exist right after the event's commit.
- The ledger breaks the outcome rules above, or an evidence item is not a URL with a host or a manifest with its hash.
- An id is missing at either end, malformed, or duplicated, at any commit the walk reads; a retired or reserved id
  is in use without a reviewed restoration; a restoration binds no stable identifier, or the two rows' identifiers
  differ.
- A repurposed id still denotes the other entity at `--to`, is repurposed again before the first repurpose is
  remediated, or is removed without `retires_repurpose`, or its replacement is not what `replacement_kind` says.
- An input holds a value that is not standard JSON (`NaN`, `Infinity`, a number too large for a float), or bytes that
  are not UTF-8. The message names the file, and the commit for a source file.

Ids may be missing in between: contributors may omit ids on new rows until the import assigns them. Every id must
be final at `--to`.

## Generating the files

Pass commit SHAs, not branch names. `--repo` may name any folder inside the repository; every read runs from its
top level. `--from` is the previous **successful published** snapshot, not a failed draft
or a feature tag. `--to` is the release candidate. Both must be on one first-parent line and come from a full clone.
For v5.0.0, run it twice: v4.0 to v5 (cumulative) and export.51 to v5 (the step since the last export).

```bash
python3 bin/scripts/release/migrations.py --from <published snapshot sha> --to <candidate sha> \
  --ledger migrations/events.jsonl --reserved migrations/reserved_ids.jsonl --meta <release_meta.json> --out build/migrations
```

`release_meta.json` looks like this:

```json
{"data_version": "5.0.0", "contract_version": "5", "policy_version": "<date>", "data_schema_version": "5",
 "notices": [".github/licenses/SOURCES.txt"]}
```

The same inputs always give byte-identical files. The files are written to a new staging folder
(`.<out>.staging-<random>`) and swapped in at the end, so a failed run keeps the earlier output; when writing fails,
the error says where that output is. If a run is stopped between the two renames of the swap, the last complete
output is in `.<out>.previous`. When a validated run reaches the write stage, it restores `.<out>.previous` before
creating its staging folder. If validation fails earlier, the last complete files remain in that backup. Run one
generator at a time per output folder. A staging folder left by a stopped run is never reused; delete it by hand.

Measured on a laptop (Apple silicon), on the repository of 14 October 2026 (master `2f0ce218`, about 1,018,000 keyed
rows, 543 MB of source JSON). With earlier events the walk starts at the oldest of them, so the cost follows the
commits walked, not the length of the interval:

| Interval | Commits walked | Time | Peak memory |
|---|---:|---:|---:|
| #2009 to master (9 commits), checking 9,862 earlier events and the 1509 restoration | 203 | 68 s | 2.8 GB |
| v4.0 to master, cumulative (refused on exactly the 339 held events) | 208 | 66 s | 3.5 GB |

Tests: `python3 -m unittest bin/scripts/release/test_migrations.py` from the repository root, or
`cd bin/scripts/release && python3 -m unittest test_migrations`. The tests run on scratch git repositories.
