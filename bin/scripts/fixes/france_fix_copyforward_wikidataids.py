#!/usr/bin/env python3
"""Re-match FR cities whose wikiDataId was copied forward from the previous row (2019 import bug).

The same bug as #1634 (Mexico): when the 2019 import found no Wikidata match for a row, it reused the
previous row's ID, so runs of consecutive records share one QID. Every record in such a shared-QID group
is matched again from scratch; nothing is inferred from the (wrong) shared ID.

How a record is matched
-----------------------
1. INSEE. French cities are communes, and every commune item on Wikidata carries its INSEE code (P374),
   which starts with the department number = the record's ``state_code``. The record takes the item in
   its department whose French label is its name. Several such items (a commune merger leaves the
   historic and the current item on one code) -> the one without a dissolution date (P576). Accepted
   only within ``INSEE_KM`` of the record.
2. Nearby named place. Otherwise: an inhabited place (settlement, neighbourhood or commune) within
   ``AROUND_KM`` whose label or alias, in any language, is the record's name. This catches renamed
   communes, Catalan names and records filed under the wrong department. Order of preference: the
   record's existing QID; an item whose French label is exactly the name (the locality Berck-Plage, not
   the commune Berck that lists it as an alias); a commune over other items (e.g. GeoNames-generated
   stubs), current communes first, then the main item (most Wikipedia articles). "Quartiers
   prioritaires" (urban-policy zones reusing a neighbourhood's name) are ignored.
3. Merged commune. Still nothing: the one commune in the department within ``AROUND_KM`` whose name
   starts with the record's name ("Tignieu" = Tignieu-Jameyzieu).
4. Otherwise blank: a missing ID is better than one pointing at another place.

A QID then on several records is either one place entered twice (all within ``AROUND_KM``; reported
for merging) or a conflict (the group record is blanked).

Usage
-----
    python3 bin/scripts/fixes/france_fix_copyforward_wikidataids.py --dry-run
    python3 bin/scripts/fixes/france_fix_copyforward_wikidataids.py

Wikidata lookups are cached in ``$CSC_CACHE_DIR`` (default: ``<tmp>/csc-copyforward-fr``), so a rerun
is fast and an interrupted run resumes. Idempotent: once no shared-QID groups remain, it changes
nothing. Only the ``wikiDataId`` field is written; the file keeps its formatting.
"""
import argparse
import http.client
import json
import math
import os
import re
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FR_JSON = REPO / 'contributions' / 'cities' / 'FR.json'
REPORT = Path(__file__).with_suffix('.report.json')
CACHE = Path(os.environ.get('CSC_CACHE_DIR') or Path(tempfile.gettempdir()) / 'csc-copyforward-fr')
UA = 'csc-copyforward-fr/1.0 (https://github.com/dr5hn/countries-states-cities-database)'
WDQS = 'https://query.wikidata.org/sparql'
WD_API = 'https://www.wikidata.org/w/api.php'

INSEE_KM, AROUND_KM = 5.0, 3.0
# human settlement, neighbourhood, quarter, and the commune types (a French commune is not a subclass of
# human settlement on Wikidata): commune of France, commune déléguée, commune associée, commune nouvelle
PLACE_ROOTS = ('Q486972', 'Q123705', 'Q2983893', 'Q484170', 'Q21869758', 'Q666943', 'Q2989454')
EXCLUDE_TYPES = {'Q30738636'}  # quartier prioritaire de la politique de la ville
CITY_PREFIXES = ('marseille ', 'lyon ', 'paris ')  # "Marseille Endoume" is the quartier "Endoume"


def log(level, msg):
    """Print a log line with a severity prefix."""
    print(f'[{level}] {msg}', flush=True)


def fold(s):
    """Lower-case, strip accents, unify hyphens/apostrophes/spaces for name comparison."""
    s = ''.join(c for c in unicodedata.normalize('NFKD', s.lower()) if not unicodedata.combining(c))
    return re.sub(r"[\s\-'’]+", ' ', s).strip()


def km(a, b):
    """Great-circle distance in km between (lat, lon) pairs."""
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def point(wkt):
    """Parse a WKT 'Point(lon lat)' literal into (lat, lon), or None."""
    m = re.match(r'Point\(([-\d.eE]+) ([-\d.eE]+)\)', wkt)
    return (float(m.group(2)), float(m.group(1))) if m else None


def dept_of(code):
    """Department of an INSEE code: 3 characters overseas (971…), else 2 (including 2A/2B)."""
    return code[:3] if code[:2] in ('97', '98') else code[:2]


def http_json(url, data=None, attempts=6):
    """GET/POST returning JSON, with exponential backoff on 429/5xx, dropped connections and truncated bodies."""
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=300) as fh:
                return json.loads(fh.read())
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or i == attempts - 1:
                raise
            wait = int(e.headers.get('Retry-After') or 0) or 2 ** (i + 2)
            log('WARNING', f'HTTP {e.code} from {urllib.parse.urlparse(url).netloc}, retrying in {wait}s')
            time.sleep(wait)
        except (json.JSONDecodeError, urllib.error.URLError, TimeoutError, http.client.HTTPException, ConnectionError) as e:
            if i == attempts - 1:
                raise
            log('WARNING', f'{type(e).__name__} from {urllib.parse.urlparse(url).netloc}, retrying')
            time.sleep(2 ** (i + 2))


def sparql(query):
    """Run a WDQS query and return its bindings."""
    return http_json(WDQS, data=urllib.parse.urlencode({'query': query, 'format': 'json'}).encode())['results']['bindings']


def load_cache(name):
    """Load a JSON cache file from CACHE, or {}."""
    path = CACHE / name
    return json.loads(path.read_text()) if path.exists() else {}


def save_cache(name, value):
    """Write a JSON cache file to CACHE."""
    (CACHE / name).write_text(json.dumps(value, ensure_ascii=False))


def insee_items():
    """{qid: {'insee': {code: ended}, 'labels': [fr labels], 'p31': [...], 'coords': [WKT]}} for every item
    with an INSEE code; fetched in ten chunks (one response for all would be truncated) and cached."""
    cached = load_cache('insee_items.json')
    if cached:
        return cached
    items = {}
    for digit in '0123456789':
        rows = sparql(f"""SELECT ?item ?insee ?end ?label ?type ?coord WHERE {{
          ?item p:P374 ?st . ?st ps:P374 ?insee . FILTER(STRSTARTS(?insee, "{digit}"))
          OPTIONAL {{ ?st pq:P582 ?end }}
          OPTIONAL {{ ?item rdfs:label ?label FILTER(LANG(?label) = "fr") }}
          OPTIONAL {{ ?item wdt:P31 ?type }}
          OPTIONAL {{ ?item wdt:P625 ?coord }} }}""")
        log('INFO', f'INSEE codes {digit}*: {len(rows)} rows')
        for b in rows:
            it = items.setdefault(b['item']['value'].rsplit('/', 1)[1], {'insee': {}, 'labels': set(), 'p31': set(), 'coords': set()})
            code = b['insee']['value']
            it['insee'][code] = it['insee'].get(code) or ('end' in b)
            if 'label' in b: it['labels'].add(b['label']['value'])
            if 'type' in b: it['p31'].add(b['type']['value'].rsplit('/', 1)[1])
            if 'coord' in b: it['coords'].add(b['coord']['value'])
        time.sleep(2)
    out = {q: {'insee': v['insee'], 'labels': sorted(v['labels']), 'p31': sorted(v['p31']), 'coords': sorted(v['coords'])}
           for q, v in items.items()}
    if len(out) < 30000:
        raise RuntimeError(f'only {len(out)} INSEE items fetched (expected ~40,000); WDQS may have truncated a response')
    save_cache('insee_items.json', out)
    return out


def dissolved(qids):
    """{qid: True if the item has a dissolution date (P576)}; cached."""
    cache = load_cache('p576.json')
    need = sorted(set(qids) - set(cache))
    for i in range(0, len(need), 50):
        d = http_json(WD_API + '?' + urllib.parse.urlencode({
            'action': 'wbgetentities', 'ids': '|'.join(need[i:i + 50]), 'props': 'claims', 'format': 'json'}))
        for q, e in d.get('entities', {}).items():
            cache[q] = bool(e.get('claims', {}).get('P576'))
        save_cache('p576.json', cache)
        time.sleep(0.5)
    return {q: cache.get(q, False) for q in qids}


def item_facts(qids):
    """{qid: {'p31', 'dissolved', 'sitelinks', 'label_fr' (folded)}} for tie-breaks; cached."""
    cache = load_cache('facts.json')
    need = sorted(set(qids) - set(cache))
    for i in range(0, len(need), 50):
        d = http_json(WD_API + '?' + urllib.parse.urlencode({
            'action': 'wbgetentities', 'ids': '|'.join(need[i:i + 50]), 'props': 'claims|sitelinks|labels',
            'languages': 'fr', 'format': 'json'}))
        for q, e in d.get('entities', {}).items():
            cl = e.get('claims', {})
            cache[q] = {'p31': [c['mainsnak']['datavalue']['value']['id'] for c in cl.get('P31', []) if c['mainsnak'].get('datavalue')],
                        'dissolved': bool(cl.get('P576')), 'sitelinks': len(e.get('sitelinks', {})),
                        'label_fr': fold(e.get('labels', {}).get('fr', {}).get('value', ''))}
        save_cache('facts.json', cache)
        time.sleep(0.5)
    return {q: cache[q] for q in qids if q in cache}


def around(rec):
    """Inhabited places within AROUND_KM of the record: [(qid, km, [folded labels/aliases])]; cached per record."""
    cache = load_cache('around.json')
    key = str(rec['id'])
    if key not in cache:
        roots = ' '.join(f'wd:{q}' for q in PLACE_ROOTS)
        rows = sparql(f"""SELECT ?item ?dist ?name WHERE {{
          SERVICE wikibase:around {{ ?item wdt:P625 ?loc .
            bd:serviceParam wikibase:center "Point({rec['longitude']} {rec['latitude']})"^^geo:wktLiteral ;
                            wikibase:radius "{AROUND_KM}" ; wikibase:distance ?dist }}
          VALUES ?root {{ {roots} }} ?item wdt:P31/wdt:P279* ?root .
          ?item rdfs:label|skos:altLabel ?name . }}""")
        found = defaultdict(lambda: [9e9, set()])
        for b in rows:
            q = b['item']['value'].rsplit('/', 1)[1]
            found[q][0] = min(found[q][0], float(b['dist']['value']))
            found[q][1].add(fold(b['name']['value']))
        cache[key] = [(q, d, sorted(n)) for q, (d, n) in found.items()]
        save_cache('around.json', cache)
        time.sleep(1.0)
    return cache[key]


def name_forms(rec):
    """Folded forms of the record's name: as written, without a bracketed part, without a city prefix."""
    n = rec['name']
    forms = {fold(n), fold(re.sub(r'\s*\(.*?\)\s*', ' ', n))}
    forms |= {f[len(p):] for f in forms for p in CITY_PREFIXES if f.startswith(p)}
    return {f for f in forms if f}


def build_plan(recs, items):
    """Return (plan entries for every record in a shared-QID group, duplicate pairs, conflicts)."""
    by_name = defaultdict(set)
    for q, it in items.items():
        for code in it['insee']:
            for lab in it['labels']:
                by_name[(dept_of(code), fold(lab))].add(q)
    groups = defaultdict(list)
    for r in recs:
        if r.get('wikiDataId'):
            groups[r['wikiDataId']].append(r)
    in_group = [r for v in groups.values() if len(v) > 1 for r in v]
    log('INFO', f'{sum(1 for v in groups.values() if len(v) > 1)} shared-QID groups, {len(in_group)} records')

    multi = {q for r in in_group for f in name_forms(r) for q in by_name.get((r['state_code'], f), ())
             if len(by_name[(r['state_code'], f)]) > 1}
    gone = dissolved(sorted(multi))
    plan, pending = [], []
    for r in in_group:
        rc = (float(r['latitude']), float(r['longitude']))
        cands = {q for f in name_forms(r) for q in by_name.get((r['state_code'], f), ())}
        if len(cands) > 1:
            cands = {q for q in cands if not gone.get(q)}
        entry = {'id': r['id'], 'name': r['name'], 'state': r['state_code'], 'type': r.get('type'), 'old': r['wikiDataId']}
        if len(cands) == 1:
            q = next(iter(cands))
            d = min((km(rc, p) for p in map(point, items[q]['coords']) if p), default=None)
            if d is not None and d <= INSEE_KM:
                entry.update(new=q, km=round(d, 3), how='insee')
                plan.append(entry)
                continue
            entry['insee_reject'] = f'{q} at {d if d is None else round(d, 1)} km'
        elif len(cands) > 1:
            entry['insee_reject'] = f'{len(cands)} current communes: {sorted(cands)}'
        pending.append((r, entry))

    log('INFO', f'INSEE matches: {len(plan)} | nearby-place lookups: {len(pending)}')
    for n, (r, entry) in enumerate(pending, 1):
        rc = (float(r['latitude']), float(r['longitude']))
        hits = [(q, d) for q, d, names in around(r) if name_forms(r) & set(names)]
        if len({q for q, _ in hits}) > 1:
            facts = item_facts(sorted({q for q, _ in hits}))
            hits = [h for h in hits if not set(facts.get(h[0], {}).get('p31', [])) & EXCLUDE_TYPES]
        mine = [h for h in hits if h[0] == r['wikiDataId']]
        if len({q for q, _ in hits}) > 1:
            facts = item_facts(sorted({q for q, _ in hits}))
            exact = [h for h in hits if facts.get(h[0], {}).get('label_fr') in name_forms(r)]
            hits = exact or hits
        communes = [h for h in hits if h[0] in items]
        if len({q for q, _ in communes}) > 1:
            facts = item_facts(sorted({q for q, _ in communes}))
            rank = lambda h: (not facts[h[0]]['dissolved'], facts[h[0]]['sitelinks'])
            best = max(communes, key=rank)
            communes = [best] if sum(1 for h in communes if rank(h) == rank(best)) == 1 else communes
        if mine:
            entry.update(new=mine[0][0], km=round(mine[0][1], 3), how='kept: named place nearby')
        elif len(communes) == 1:
            entry.update(new=communes[0][0], km=round(communes[0][1], 3), how='named commune nearby')
        elif len({q for q, _ in hits}) == 1 and not communes:
            entry.update(new=hits[0][0], km=round(hits[0][1], 3), how='named place nearby')
        elif hits:
            entry.update(new=None, km=None, how=f'ambiguous: {sorted(hits, key=lambda h: h[1])[:3]}')
        else:
            pre = {q for f in name_forms(r) for (d, lab), qs in by_name.items() if d == r['state_code']
                   and lab.startswith(f + ' ') for q in qs}
            near = [(q, min(km(rc, p) for p in map(point, items[q]['coords']) if p)) for q in pre
                    if any(point(c) for c in items[q]['coords'])]
            near = [(q, d) for q, d in near if d <= AROUND_KM]
            if len(near) == 1:
                entry.update(new=near[0][0], km=round(near[0][1], 3), how='merged commune bearing its name')
            else:
                entry.update(new=None, km=None, how='no verified match')
        plan.append(entry)
        if n % 50 == 0:
            log('INFO', f'nearby-place lookups {n}/{len(pending)}')

    by_q = defaultdict(list)
    for p in plan:
        if p['new']:
            by_q[p['new']].append(p)
    single = {q for q, v in groups.items() if len(v) == 1}
    rec_by_id = {r['id']: r for r in recs}
    dups, conflicts = [], []
    for q, ps in by_q.items():
        holders = [rec_by_id[p['id']] for p in ps] + (groups[q] if q in single else [])
        if len(holders) < 2:
            continue
        pos = [(float(h['latitude']), float(h['longitude'])) for h in holders]
        if all(km(a, b) <= AROUND_KM for i, a in enumerate(pos) for b in pos[i + 1:]):
            dups.append({'qid': q, 'records': [[h['id'], h['name']] for h in holders]})
            continue
        conflicts.append({'qid': q, 'records': [[h['id'], h['name'], h['state_code']] for h in holders]})
        ordered = sorted(ps, key=lambda p: p['km'] if p['km'] is not None else 9e9)
        for p in ordered[0 if q in single else 1:]:
            p.update(new=None, km=None, how=f"conflict: {q} also matched {[h['id'] for h in holders if h['id'] != p['id']]}")
    return plan, dups, conflicts


def main():
    """Build the plan, write the report, and (unless --dry-run) apply it to FR.json."""
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--dry-run', action='store_true', help='build the plan and report, but do not write FR.json')
    args = ap.parse_args()
    if not FR_JSON.is_file() or not os.access(FR_JSON, os.R_OK | (0 if args.dry_run else os.W_OK)):
        sys.exit(f'[ERROR] {FR_JSON} is missing or not {"readable" if args.dry_run else "writable"}; run from a repo checkout.')
    CACHE.mkdir(parents=True, exist_ok=True)
    text = FR_JSON.read_text(encoding='utf-8')
    recs = json.loads(text)
    plan, dups, conflicts = build_plan(recs, insee_items())

    changes = [p for p in plan if p['new'] != p['old']]
    how = Counter(p['how'].split(':')[0] for p in plan)
    log('INFO', f"kept {sum(1 for p in plan if p['new'] and p['new'] == p['old'])} | new "
                f"{sum(1 for p in plan if p['new'] and p['new'] != p['old'])} | blank {sum(1 for p in plan if not p['new'])} | {dict(how)}")
    log('INFO', f'duplicate places: {len(dups)} | conflicts blanked: {len(conflicts)}')
    REPORT.write_text(json.dumps({
        'summary': {'records_in_groups': len(plan), 'changed': len(changes), 'how': dict(how)},
        'blank': [{k: p.get(k) for k in ('id', 'name', 'state', 'type', 'old', 'how', 'insee_reject') if p.get(k) is not None}
                  for p in plan if not p['new']],
        'duplicate_places': dups, 'conflicts': conflicts,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    log('INFO', f'report written to {REPORT.relative_to(REPO)}')
    if args.dry_run or not changes:
        log('INFO', 'dry run: FR.json not written' if args.dry_run else 'no shared-QID groups left: nothing to change')
        return

    by_id = {r['id']: r for r in recs}
    stale = [p['id'] for p in plan if by_id[p['id']].get('wikiDataId') != p['old']]
    if stale:
        sys.exit(f'[ERROR] {len(stale)} records changed while planning (first: {stale[:5]}); nothing written. Rerun.')
    for p in changes:
        by_id[p['id']]['wikiDataId'] = p['new']
    FR_JSON.write_text(json.dumps(recs, ensure_ascii=False, indent=2) + ('\n' if text.endswith('\n') else ''), encoding='utf-8')
    log('INFO', f'FR.json: wikiDataId updated on {len(changes)} records')


if __name__ == '__main__':
    try:
        main()
    except urllib.error.URLError as e:
        sys.exit(f'[ERROR] Wikidata unreachable ({e}). Check network access to wikidata.org and rerun; finished lookups are cached.')
    except (RuntimeError, json.JSONDecodeError) as e:
        sys.exit(f'[ERROR] {e}. Delete the cache directory {CACHE} and rerun.')
