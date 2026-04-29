# FIX #1039 — `postcodes` Table (Tier 4 Architecture)

**Issue:** [#1039 — Can we add a postcode for this?](https://github.com/dr5hn/countries-states-cities-database/issues/1039)
**Scope:** New entity table for postal codes (Tier 4 from the roadmap).
**Date:** 2026-04-25
**Companion PR:** Country-level `postal_code_format`/`postal_code_regex` backfill (#1391).

## Decision

After exploring four shape options for postcode storage:
- **Shape A** — single prefix string per state (lossy: ~40% of states have multiple prefixes)
- **Shape B** — array of prefixes per state (lossy at sub-state granularity)
- **Shape C** — min/max range per state (fails for non-contiguous and alphanumeric systems)
- **Shape D** — separate `postcodes` table with FKs to country/state/city ✅

**Shape D was chosen** because:
- Lossless at every granularity (full / outward / sector / district / area)
- Naturally handles "state has many postcodes" (US, UK, DE, etc.)
- Naturally handles "postcode spans multiple states" (rare but real — some US ZIPs)
- FK to existing `cities` lets postcodes be denormalised against the existing city dataset
- Independent of state-level schema decisions made earlier or later

## Schema Shape

```sql
CREATE TABLE `postcodes` (
  `id`             int unsigned NOT NULL AUTO_INCREMENT,
  `code`           varchar(20) NOT NULL,
  `country_id`     mediumint unsigned NOT NULL,           -- FK countries.id
  `country_code`   char(2) NOT NULL,                       -- denormalised
  `state_id`       mediumint unsigned NULL,                -- FK states.id (nullable)
  `state_code`     varchar(255) NULL,                      -- denormalised
  `city_id`        mediumint unsigned NULL,                -- FK cities.id (nullable)
  `locality_name`  varchar(255) NULL,
  `type`           varchar(32) NULL,                       -- full | outward | sector | district | area
  `latitude`       decimal(10,8) NULL,
  `longitude`      decimal(11,8) NULL,
  `source`         varchar(64) NULL,                       -- attribution: openplz | wikidata | census | ...
  `wikiDataId`     varchar(255) NULL,
  `created_at`     timestamp NOT NULL DEFAULT '2014-01-01 12:01:01',
  `updated_at`     timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `flag`           tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `idx_postcodes_code` (`code`),
  KEY `idx_postcodes_country_code` (`country_id`,`code`),
  KEY `idx_postcodes_state` (`state_id`),
  KEY `idx_postcodes_city` (`city_id`),
  CONSTRAINT `postcodes_country_fk` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`),
  CONSTRAINT `postcodes_state_fk`   FOREIGN KEY (`state_id`)   REFERENCES `states`    (`id`) ON DELETE SET NULL,
  CONSTRAINT `postcodes_city_fk`    FOREIGN KEY (`city_id`)    REFERENCES `cities`    (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## What this PR includes (foundation only)

- Phinx migration: `bin/db/migrations/20260425000000_create_postcodes_table.php`
- Manual mirror in `bin/db/schema.sql` so reviewers can read the schema without running Phinx
- New contributions directory: `contributions/postcodes/` with `README.md` documenting field shape and sourcing plan
- Importer support: `import_postcodes()` in `bin/scripts/sync/import_json_to_mysql.py` — gracefully skips if table or directory is absent
- Validator support: `postcodes` entity recognised in `.github/scripts/utils.js` with field rules
- Cross-reference validator: FK checks for `country_id`, `state_id`; format check against `countries.postal_code_regex`
- Docs in `.github/fixes-docs/`

## What this PR does NOT include (deliberate)

1. **Country data** — no `contributions/postcodes/{ISO2}.json` files yet. Each country comes in a follow-up PR sourced from one of the providers in the sourcing plan.
2. **Export commands** — `bin/Commands/Export*.php` still emit only `regions, subregions, countries, states, cities`. Adding `postcodes` to each of the 7 export formats (Csv, Json, MongoDB, Plist, SqlServer, Xml, Yaml) is a separate PR — that work is mechanical but touches every format and needs separate review.
3. **`sync_mysql_to_json.py`** — the reverse-sync script does not yet know about `postcodes`. Same scope decision as exports; add in follow-up.
4. **PR validator updates beyond cross-reference** — `validate-coordinates.js` and `detect-duplicates.js` are not yet postcode-aware; coordinates on postcodes are coarse centroids and duplicate detection has different semantics for postcodes (exact-code-match vs. fuzzy-name-match).

## Sourcing Plan (Combo B, GeoNames-free)

Per discussion in the issue, GeoNames is excluded. Each country is sourced from one of:

| Source | License | Countries |
|--------|---------|-----------|
| **OpenPLZ API** (https://openplzapi.org) | **ODbL-1.0** ← matches repo | DE, AT, CH, LI |
| **Wikidata P281** (SPARQL) | CC-0 | Long-tail backfill |
| **US Census ZCTA** | Public domain | US |
| **India Post pincode CSV** | Open (gov.in) | IN |
| **Japan Post KEN_ALL.csv** | Free | JP |
| **France La Poste** (data.gouv.fr) | etalab-2.0 | FR |
| **Australia Post Boundaries** | CC-BY 4.0 | AU |
| **Statistics Canada FSA** | Open Government | CA |

The `source` field on each postcode record tracks attribution, so README/footer attribution can be programmatically generated from data presence.

**Coverage projection:** Combo B can reach ~30–40% of the world's postcodes by row count. Reaching higher coverage (UK Royal Mail, Eircode, Deutsche Post) is structurally blocked by license restrictions, not by effort.

## Validation Strategy

PRs adding `contributions/postcodes/{ISO2}.json` are validated by:

1. **Schema validator** (`validate-schema.js`) — required fields, type rules, no auto-managed fields
2. **Cross-reference validator** (`validate-cross-reference.js`) — `country_id` and `country_code` agreement, `state_id` belongs to declared country, postcode `code` matches `countries.postal_code_regex` if defined
3. **JSON syntax** — standard JSON parsing
4. **PR format checks** — source URL required in PR body for license attribution

## Roll-Out Plan (Suggested)

| PR | Country | Source | Approx rows | Notes |
|----|---------|--------|-------------|-------|
| **This PR** | (foundation only) | — | 0 | Schema + infra |
| Next | Liechtenstein | OpenPLZ | ~9 | Smallest, proves OpenPLZ adapter |
| | Luxembourg | OpenPLZ-style or PT.LU | ~200 | Small, fits in tiny JSON |
| | Iceland | Iceland Post | ~150 | Small |
| | Estonia | Eesti Post | ~700 | Small |
| | Switzerland | OpenPLZ | ~3,200 | DACH first wave |
| | Austria | OpenPLZ | ~2,100 | DACH first wave |
| | Germany | OpenPLZ | ~8,200 | Largest DACH |
| | India | India Post | ~19,000 | First non-DACH at scale |
| | France | La Poste | ~6,400 | etalab license |
| | Australia | Australia Post | ~3,500 | CC-BY |
| | Japan | KEN_ALL | ~150,000 | Largest single pipeline; will need `.gz` distribution |
| | US | Census ZCTA | ~33,000 | Public domain |

After ~5 country PRs, schedule the export-command update PR (touches all 7 formats).

## Rollback

If the postcodes table or any country data needs to be removed:

```sql
DROP TABLE IF EXISTS `postcodes`;
```

The Phinx migration is a `change()` method without an explicit `down()`; rollback is via the manual DROP above. Removing `contributions/postcodes/` is a plain directory deletion.

No existing tables or columns are modified by this PR; rollback is clean.
