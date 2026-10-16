# Migrations: what changed between two releases

From v5.0.0, each data release is meant to carry files that tell you how its records relate to an earlier
release's, so you can update ids stored in your own systems. They are generated, never edited by hand, by
[`bin/scripts/release/migrations.py`](../bin/scripts/release/migrations.py) from this folder's ledger and the git
history of `contributions/`.

**Status:** `events.jsonl` holds every removal since v4.0 (10,201) and the 1509 restoration, and every one is
reviewed. The generator accepts the cumulative interval from v4.0, and the export workflow (below) attaches its files
to each export release. A removal whose successor could not be proved is recorded as `no_successor` with no target;
it claims nothing beyond that.

## The files

| File | What it holds |
|---|---|
| `removed_ids.jsonl` | One line per removal in the interval, ids created and removed in between included. Each line has the reviewed event, the removed row (`before`), `present_at_from`, `present_at_to` and `current_targets`, which follows later removals to the records that exist in this release. The removal of a repurposed id also has `repurposed_at` and `later_entity_targets` (see below). `restored_at` marks an id the same entity got back later. |
| `removed_ids.csv` | v4.0's columns `record, old_id, name, country_code, state_code, outcome, new_table, new_id, source`, then `relation, automatic_redirect, event_commit`. One row per current target. A removal with no successor has one row with empty `new_table` and `new_id`. Rows for `later_entity_targets` follow, with a `relation` starting `later_entity>` and `automatic_redirect` `no`. |
| `added_ids.jsonl` | Every id present in this release and not in the earlier one: table, id, name, file and the commit that added it. An id a reviewed restoration brought back also has `restored` (its event and retirement commits). |
| `identity_changes.jsonl` | The reviewed unresolved snapshot (`baseline: true`) when its anchor is in the interval, then later identity decisions in first-parent order. Reviewed identity decisions on ids that kept their number at the time, with the row before and after and the current targets. A repurpose has `remediation`: the removal that retired the id and the other entity's replacement. A repurpose decided before `--from` is listed again, with `event_before_from: true`, when the removal that retires it (`retires_repurpose`) is in this interval; other earlier decisions are not repeated. |
| `changed_fields.jsonl` | One line per changed field of a record present in both releases. Each line gives `before` and `after` as typed JSON (`1`, `1.0` and `true` differ), plus `before_present` and `after_present`, so a missing field and a null one can be told apart. `translations` is compared per language (`translations.de`), or as a whole when one side is not an object. By policy, `created_at`, `updated_at` and `flag` are left out: they are bookkeeping, not facts about the place (the importer keeps the values a file gives and fills missing ones). |
| `release_manifest.json` | The release metadata (data, contract, policy and data-schema versions, notices), the two commit SHAs, the migration format version (3), totals per table at both ends, and the removed, added and changed counts, which reconcile (`from_total - removed + added = to_total`). It also has counts per field path and the SHA-256 of every file above. |

## Reviewed unresolved baseline

`unresolved_baseline.jsonl` is the reviewed inventory of every retained unresolved key at `baseline_commit`,
including rows unchanged since v4.0. It is an input, separate from `events.jsonl`: a snapshot disclosure does not
claim a scalar change happened at that commit. Each line has `schema_version: 1`, `table`, `id`, a full
`baseline_commit`, canonical full `row_sha256`, `outcome: "unresolved"`, `reason`, `decision_round`,
`review_status: "reviewed"`, `review` (reason and reviewer), and nonempty `evidence` with the ledger's URL/manifest
rules. Audit manifest pointers refer to the retained csc-data-audit evidence bundle; their SHA-256 identifies the
exact bytes. The generator checks their shape without fetching sources. Review establishes inventory completeness;
Git validates the keys and guards, not the semantic adequacy of the evidence.

The default input is `unresolved_baseline.jsonl` beside `--ledger`; `--baseline PATH` overrides that location.
The file is required; an empty inventory is valid only when review found no unresolved keys. All entries share one
anchor. Duplicate keys, malformed provenance, a missing/stale row at the anchor, a key already repurposed, removed
or reserved, an off-line anchor, or a conflicting identity event at that commit fail before output is written.
At the initial v5 pin every baseline key must remain present at `--to`; later reviewed removals and repurposes may
retire it through the normal ledger gates. Keep the baseline immutable and ship it with the generator and ledger.

The first cumulative v4-to-v5 file carries all baseline entries with `event_type: "identity"`, `baseline: true`,
`event_commit` equal to the reviewed anchor, identical `before`/`after` rows, no targets and no redirect. Its
`row_sha256` is a snapshot guard, not a `before_row_sha256` claim about an invented transition. Migration format
version 3 distinguishes this addition. The manifest records the baseline's SHA-256, anchor and key count.
The output is ordered by first-parent commit, then key; a step interval excludes decisions at or before `--from`.
A future anchor waits for its release. Historical guards are still checked when the anchor precedes `--from`.

Consumers start from the verified v5 baseline, apply later identity decisions in order and retain the latest outcome
per `(table, id)`; apply reviewed removals as retirements. An omitted key stays unresolved until an explicit later
decision resolves it or a reviewed removal retires it. Category-field admission alone does not replace an explicit
unresolved identity decision. The 117 listed rename keys and 12 Russian rayon mappings remain publication holds;
including them in this inventory does not approve their transfer assertions or close those holds.

A later review can resolve identity without editing the data: append a normal reviewed identity event with
`decision_only: true`, `before_row_sha256` and `after_row_sha256` guarding the unchanged row at that review commit.
Only `classification`, `dual_role` and `unresolved` allow this form; a repurpose still requires a real transition
and its existing remediation checks. Evidence, review, target and history checks remain mandatory.

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
  (`prior_identity`), which must exist at the event commit. If the earlier entity has no separate record there,
  use `targets: []` with an explicit `prior_entity`: `status` is `ended` (the entity ceased to exist) or `unrecorded`
  (it has no separate record), `reason` explains the finding, and `evidence` is a non-empty list with the same
  URL/manifest rules as event evidence. This declares absence of a record at conversion, not uncertainty about the original
  identity, and makes no claim that the later entity is its territorial successor. For example:
  `"prior_entity": {"status": "ended", "reason": "District tier ended on 2025-07-01; no separate original record",
  "evidence": [{"url": "https://example.org/reform-instrument"}]}`.
  If an original entity was unrecorded at conversion but gained a separate representation later, its declaration
  may include `recorded_later: {"event_commit": "<full SHA>", "target": {"table": "cities", "id": 123},
  "row_sha256": "<full row hash>"}`. The commit must follow the identity event on the same first-parent line;
  the target must be added or change there and match the full hash. The declaration needs evidence for that original identity,
  not just a matching item. Resolution starts at that later representation and follows subsequent events; it stays
  unrecorded for a release before that commit. `ended` cannot use this field.
  A nonempty `prior_identity` mapping and `prior_entity` are mutually exclusive; other outcomes cannot use it.
  Identity output retains the declaration; the remediation removal carries it alongside empty `current_targets`
  unless `recorded_later` applies. With no applicable later representation, a target chain entering such a repurpose
  ends with `end: "ended"` or `"unrecorded"` and the declaration.
  A repurposed id may not remain at `--to`. It must be retired by a later reviewed removal that
  says so in `retires_repurpose` (below), before it can be repurposed again: a second repurpose of an id whose first is
  not yet remediated is refused. The old id then keeps its earlier meaning: its `current_targets` are the
  repurpose's `prior_identity` (or its `recorded_later` representation), and the entity the number came to denote is listed apart in `later_entity_targets`.
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

## A data PR carries its own events

Use a full `event_commit` SHA (existing ledgers keep working), or omit it and use a positive integer
`event_pr`, for removals, identity decisions and restorations alike. Each PR key requires a saved GitHub
association, `{"event_pr": 2050, "merge_commit_sha": "<full SHA>"}`, in `--pr-commits` (default:
`pr_commits.jsonl` beside the ledger). Missing, duplicate or malformed associations fail. The associated commit must
have exactly one parent and belong to the pinned ledger's first-parent line. Titles never establish an association:
merges, cherry-picks, reverts and edited suffixes cannot substitute for GitHub's `merge_commit_sha`.
The PR check and export wrapper fetch each PR-only key from GitHub's pulls API, require it to be merged, and refuse
any disagreement with saved associations in `migrations/pr_commits.jsonl` (initially empty). They need read access
only. The export saves the verified map as `pr_commits.jsonl` inside every migration archive, covered by the archive
checksum, so the same inputs can be replayed offline with `--pr-commits <saved-map>`; use trusted committed or
exported evidence for offline runs. Do not invent mappings from titles.
`--ledger-tip` pins the authoritative ledger history (default: HEAD, resolved once); it may include events after
`--to`. Such later events, including held events, wait for their release. For historical regeneration, supply the
ledger's pinned tip and its saved map, rather than searching arbitrary branches. Explicit `event_commit` keys
always take precedence, including in
pending mode: existing events may retain `event_pr` as metadata without changing their meaning. Generated JSONL and CSV always record the resolved full
`event_commit` SHA; JSONL also retains `event_pr`. Reference fields such as `retirement_commit`,
`retires_repurpose.identity_event_commit` and `recorded_later.event_commit` still require full historical SHAs.
The immutable unresolved baseline continues to use `baseline_commit`.

1. Open the data PR to obtain its number. Append reviewed events to `migrations/events.jsonl` in that same PR,
   replacing each new event's `event_commit` with `event_pr: <that number>` (a JSON integer). Include the evidence,
   review, outcome and targets as usual; no follow-up ledger PR is needed after squash merge.
2. For a removal, set `before_commit` to the merge preview's first parent (the current base-branch SHA),
   `before_path` to the row's original path, and `before_row_sha256` to its full canonical row hash at that parent.
   Refresh these guards when the base changes. Identity and restoration hashes keep their existing rules.
3. Finalise every new row's id before the check: id-less rows are allowed in intermediate history, not at `--to`.
   All existing review, target, retirement, repurpose, baseline and restoration gates remain in force. A repurpose
   that still leaves the id denoting the other entity at the preview is refused; PR keys do not waive remediation.
4. **Merge a PR that carries PR-keyed events with "Squash and merge".** The association must be a single-parent
   commit that holds the whole change: "Create a merge commit" gives a two-parent commit, and "Rebase and merge"
   spreads the change over several commits, so either leaves the events unresolvable and the next export refuses
   until the ledger is fixed. Nothing wrong is published; releases stop. Allowing only squash merging in the
   repository settings removes the risk.
5. The `Ledger migrations` PR job checks the merge preview with `--pending-pr <number>`. Only events naming that
   number bind directly to `--to`; other PR keys still require verified associations. Pending mode requires a
   two-parent preview and refuses a PR already present in the saved associations or the base's historical suffixes.
   CI also checks that the PR is still open and that the preview's second parent is the PR's current head (GitHub's
   live merge_commit_sha is not compared: it moves when the base advances). The preview's tree and first parent are
   the eventual squash inputs; all data gates run unchanged. After the merge, GitHub's merged SHA becomes the
   association; the title plays no part, so editing it is harmless. Without pending mode an unmerged PR key fails. Use pending mode only for a merge preview, never to generate published release files.

For example, a reviewed no-successor removal in PR 2050 uses this event shape (replace the guards and provenance):

```json
{"schema_version": 1, "old_table": "cities", "old_id": 123, "event_pr": 2050,
 "before_commit": "<full base SHA>", "before_path": "contributions/cities/XX.json",
 "before_row_sha256": "<canonical full-row SHA-256>", "outcome": "no_successor", "targets": [],
 "automatic_redirect": false, "review_status": "reviewed",
 "review": {"reason": "<reviewed finding>", "reviewer": "<reviewer>"},
 "evidence": [{"url": "https://example.org/source"}]}
```

The read-only [`ledger-migrations.yml`](../.github/workflows/ledger-migrations.yml) reports `Ledger migrations`
on every PR, including drafts. A complete local Git diff skips only the expensive validation step when no path
under `contributions/`, `migrations/`, `bin/scripts/release/` or the workflow itself changed; docs/export-only PRs
still receive a successful required status. Relevant PRs fetch full history and tags and compare v4.0 to the merge
preview. CI and export share source-metadata validation before adding `data_version`, derived from the validated
contract major (`5-candidate` for contract 5). The job publishes and comments nothing. Require `Ledger migrations`
in branch protection/rulesets. Its single walk takes about two minutes and 3.2 GB, with a 15-minute timeout;
newer runs cancel older runs for the same PR.

To reproduce a PR check in a full clone with `gh` signed in, prepare the same verified inputs, then run the generator:

```bash
export PENDING_PR=2050 MERGE_SHA=<merge-preview-sha>
python3 - <<'PYCODE'
import json, os, sys
from pathlib import Path
sys.path.insert(0, 'bin/scripts/release')
from release_migrations import github_pr_commits, load_source_meta
meta = load_source_meta('migrations/release_meta.json')
meta['data_version'] = f"{meta['contract_version']}-candidate"
Path('/tmp/ledger-meta.json').write_text(json.dumps(meta))
Path('/tmp/ledger-prs.jsonl').write_text(github_pr_commits(
    Path.cwd(), 'migrations/events.jsonl', 'migrations/pr_commits.jsonl',
    int(os.environ['PENDING_PR']), os.environ['MERGE_SHA']))
PYCODE
python3 bin/scripts/release/migrations.py --from v4.0 --to "$MERGE_SHA" --pending-pr "$PENDING_PR" \
  --ledger-tip "$MERGE_SHA" --pr-commits /tmp/ledger-prs.jsonl \
  --ledger migrations/events.jsonl --reserved migrations/reserved_ids.jsonl \
  --meta /tmp/ledger-meta.json --out <scratch-output-folder>
```

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

- A PR-keyed event has no verified association to a single-parent commit on the pinned ledger line, or a pending PR already occurs in base history.
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

The export workflow's `migrations` job runs
[`bin/scripts/release/release_migrations.py`](../bin/scripts/release/release_migrations.py) on a full clone after a
successful build, and the publish job attaches what it writes to the release, checked against its checksums:

| Asset | What it is |
|---|---|
| `migrations-from-<tag>.tar.gz` | The files above, from that published release to this one. One is cumulative, from the newest feature release of the previous major (v4.0 for v5 data); one is a step, from the newest export release of the same major (from v5.0.0's second export on). A single archive when both are the same commit. |
| `MIGRATIONS_SHA256SUMS` | The SHA-256 of each archive. |

[`release_meta.json`](release_meta.json) holds the contract, policy and data-schema versions and the notices. The run
adds `data_version`: the newest published feature release of the contract's major, which names the export, or
`<major>-candidate` before that release is cut. A production run refuses until it is cut, so v5 data is never
published as a v4.0 export. A failed `migrations` job stops publishing; a candidate build still keeps its exports.

Every id must be final at the candidate commit (assign ids with the import and sync, or `normalize_json.py`, first),
so each export's tag can be the start of the next step file. v4.0-export.51's tag cannot: its 10,851 Spanish postcodes
got their ids at export and were synced back later. So v5.0.0's first export carries only the cumulative file from
v4.0. It lists every id event since v4.0, so a user of any v4.0 export can look up each id they store (where a
removed one went). Its added ids and changed fields are relative to v4.0, not to a later export: users of a later
export load the v5 data fresh and use the file to remap the ids they store, not to patch their copy.

```bash
python3 bin/scripts/release/release_migrations.py --to <candidate sha> --out <new folder> [--production]
```

To run the generator by hand instead:

Pass commit SHAs, not branch names. `--repo` may name any folder inside the repository; every read runs from its
top level. `--from` is the previous **successful published** snapshot, not a failed draft
or a feature tag. `--to` is the release candidate. Both must be on one first-parent line and come from a full clone.
For v5.0.0, from v4.0 (the cumulative file; see above for why not from export.51).

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
| v4.0 to master `2a04cd21`, cumulative, every event reviewed (15 October) | 229 | 117 s | 3.2 GB |

Tests: `python3 -m unittest bin/scripts/release/test_migrations.py` from the repository root, or
`cd bin/scripts/release && python3 -m unittest test_migrations test_release_migrations`. The tests run on scratch git repositories.
