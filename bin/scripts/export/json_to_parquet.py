#!/usr/bin/env python3

"""
Parquet Export Script for Countries States Cities Database

Reads the canonical JSON exports and writes Parquet files to parquet/.
Translations (nested dicts) are serialised as JSON strings so the
columnar schema stays flat and tooling-friendly.

Usage:
    python3 bin/scripts/export/json_to_parquet.py [--tables regions subregions ...]
    python3 bin/scripts/export/json_to_parquet.py           # exports all tables
"""

import argparse
import json
import os
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

TABLES = ["regions", "subregions", "countries", "states", "cities"]

JSON_NESTED_COLS = {"translations", "timezones"}


def load_json(table: str) -> list:
    path = os.path.join(REPO_ROOT, "json", f"{table}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"JSON file not found: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array in {path}")
    return data


def flatten_row(row: dict) -> dict:
    """Serialise nested dicts/lists to JSON strings so every column is scalar."""
    out = {}
    for k, v in row.items():
        if isinstance(v, (dict, list)):
            out[k] = json.dumps(v, ensure_ascii=False) if v else None
        else:
            out[k] = v
    return out


def export_table(table: str, out_dir: str) -> int:
    data = load_json(table)
    if not data:
        print(f"  [skip] {table}: no records")
        return 0

    flat = [flatten_row(r) for r in data]
    df = pd.DataFrame(flat)

    out_path = os.path.join(out_dir, f"{table}.parquet")
    pq.write_table(
        pa.Table.from_pandas(df, preserve_index=False),
        out_path,
        compression="snappy",
    )
    print(f"  [ok] {table}: {len(df):,} rows → {out_path}")
    return len(df)


def main():
    parser = argparse.ArgumentParser(description="Export JSON tables to Parquet")
    parser.add_argument(
        "--tables",
        nargs="+",
        choices=TABLES,
        default=TABLES,
        metavar="TABLE",
        help=f"Tables to export (default: all). Choices: {', '.join(TABLES)}",
    )
    args = parser.parse_args()

    out_dir = os.path.join(REPO_ROOT, "parquet")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Exporting Parquet files to {out_dir}")
    total = 0
    for table in args.tables:
        total += export_table(table, out_dir)

    print(f"\nDone. Total rows exported: {total:,}")


if __name__ == "__main__":
    main()
