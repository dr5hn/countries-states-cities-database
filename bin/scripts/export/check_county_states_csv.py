#!/usr/bin/env python3
"""Check that csv/county_states.csv lists exactly the regions of the counties of several regions in json/counties.json
(v5, decision B6), so the CSV release asset is complete. Run from the repository root after the exports; exits 1 with
the difference, or 0."""
import csv
import json
import sys


def main():
    """Compare the two listings; return the process exit code."""
    with open('json/counties.json', encoding='utf-8') as fh:
        counties = json.load(fh)
    want = sorted((c['id'], s['state_id'], s['state_code']) for c in counties for s in c.get('states') or [])
    with open('csv/county_states.csv', encoding='utf-8', newline='') as fh:
        got = sorted((int(r['county_id']), int(r['state_id']), r['state_code']) for r in csv.DictReader(fh))
    if got != want:
        print(f'[ERROR] csv/county_states.csv: missing {sorted(set(want) - set(got))[:5]}, extra {sorted(set(got) - set(want))[:5]}')
        return 1
    print(f'[INFO] csv/county_states.csv lists the {len(want)} regions of {len({w[0] for w in want})} counties of several regions')
    return 0


if __name__ == '__main__':
    sys.exit(main())
