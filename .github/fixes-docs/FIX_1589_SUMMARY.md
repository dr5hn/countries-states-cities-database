# Fix Summary: SQL Server export INSERT/CREATE TABLE column mismatch

## Issue Reference
**Original Issue:** [#1589](https://github.com/dr5hn/countries-states-cities-database/issues/1589) — Incorrect data for sqlserver release v3.2-export.5

## Executive Summary

The generated SQL Server export (`sqlserver/*.sql`, `sqlserver/world.sql`) produced `INSERT`
statements referencing columns that the accompanying `CREATE TABLE` definitions do not declare,
causing imports to fail with "invalid column name" errors.

## Root Cause

`bin/Commands/ExportSqlServer.php` builds each table's `CREATE TABLE` from a hardcoded schema, but
builds the `INSERT` column list dynamically from the JSON source:

```php
$columns = array_keys($data[0]);
```

The exported JSON (`json/states.json`, `json/cities.json`) carries **denormalized convenience
fields** that are joins in the relational model, not stored columns:

| Table  | Extra JSON field(s) with no matching column |
|--------|---------------------------------------------|
| states | `country_name`                              |
| cities | `state_name`, `country_name`                |

Because these fields have no column in `CREATE TABLE`, the generated `INSERT` statements are invalid.
`countries`, `regions`, and `subregions` were unaffected (no extra fields).

## Fix

Restrict the `INSERT` column list to columns actually declared in the table schema. A new
`getTableColumns()` helper parses the column names out of `generateTableSchema()` (single source of
truth), and `generateSqlServerInsert()` intersects the JSON keys with them:

```php
$tableColumns = $this->getTableColumns($tableName);
$columns = array_values(array_intersect(array_keys($data[0]), $tableColumns));
```

This keeps the SQL Server schema consistent with the canonical MySQL schema (the `*_name` fields
remain obtainable via a join), rather than denormalizing one export format.

## Verification

Exercised the private methods against the real `json/` data via reflection:

| Table     | Columns dropped from INSERT | Result |
|-----------|-----------------------------|--------|
| countries | *(none)*                    | unchanged |
| states    | `country_name`              | INSERT now matches schema |
| cities    | `state_name`, `country_name`| INSERT now matches schema |

Every resulting `INSERT` column list is a subset of its `CREATE TABLE` column set. `php -l` passes.

## Files Changed

- `bin/Commands/ExportSqlServer.php` — add `getTableColumns()`; filter INSERT columns to the schema.
