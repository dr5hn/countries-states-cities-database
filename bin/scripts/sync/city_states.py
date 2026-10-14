"""Reference checks shared by the importer and the sync (v5: cities without a state; counties of several regions).

check_references(countries, states, cities) and check_counties(countries, states, counties, cities) return every
problem as a readable string, so a caller can refuse the whole import or sync before touching the database or any
file. They need no database driver.
"""
import re

ISO2 = re.compile(r'[A-Z]{2}')


def positive_id(v):
    """True for a JSON integer above zero (booleans are not ids)."""
    return type(v) is int and v > 0


def _countries(countries, errors):
    """Countries by id after checking ids and ISO2 codes are valid and unique."""
    by_id, codes = {}, set()
    for n, c in enumerate(countries):
        if not isinstance(c, dict) or not positive_id(c.get('id')) or not ISO2.fullmatch(str(c.get('iso2') or '')):
            errors.append(f'country row {n}: needs a positive integer id and a two-letter iso2')
            continue
        if c['id'] in by_id or c['iso2'] in codes:
            errors.append(f"country {c['id']} {c['iso2']}: id or iso2 is duplicated")
            continue
        by_id[c['id']] = c
        codes.add(c['iso2'])
    return by_id


def _states(states, countries, errors):
    """States by id after checking each belongs to a real country with the matching code and has its own code."""
    by_id = {}
    for n, s in enumerate(states):
        if not isinstance(s, dict) or not positive_id(s.get('id')):
            errors.append(f'state row {n}: needs a positive integer id')
            continue
        # True, 1.0 and 1 are equal dictionary keys, so the type is checked before the lookup
        country = countries.get(s['country_id']) if positive_id(s.get('country_id')) else None
        if s['id'] in by_id:
            errors.append(f"state {s['id']}: id is duplicated")
        elif not positive_id(s.get('country_id')):
            errors.append(f"state {s['id']}: country_id {s.get('country_id')!r} is not a positive integer")
        elif country is None:
            errors.append(f"state {s['id']}: country_id {s.get('country_id')!r} is not a known country")
        elif s.get('country_code') != country['iso2']:
            errors.append(f"state {s['id']}: country_code {s.get('country_code')!r} is not {country['iso2']}")
        elif not isinstance(s.get('iso2'), str) or not s['iso2']:
            errors.append(f"state {s['id']}: has no state code (iso2)")
        else:
            by_id[s['id']] = s
    return by_id


def check_references(countries, states, cities):
    """Errors for invalid countries, states or city state pairs. A city's pair is both null only when its country has
    no states (v5); otherwise it is a positive integer id of a state of the same country, with that state's code."""
    errors = []
    by_country = _countries(countries, errors)
    by_state = _states(states, by_country, errors)
    if errors:
        return errors   # an inventory that is itself wrong cannot tell which countries have states
    with_states = {s['country_id'] for s in by_state.values()}
    for c in cities:
        if not isinstance(c, dict):
            errors.append('a city row is not an object')
            continue
        label = f"city {c.get('id', '(new)')} {c.get('name', '')}".rstrip()
        if not positive_id(c.get('country_id')):
            errors.append(f"{label}: country_id {c.get('country_id')!r} is not a positive integer")
            continue
        country = by_country.get(c['country_id'])
        if country is None or c.get('country_code') != country['iso2']:
            errors.append(f"{label}: country_id {c.get('country_id')!r} and country_code {c.get('country_code')!r} do not name one known country")
            continue
        if 'state_id' not in c or 'state_code' not in c:
            errors.append(f'{label}: state_id and state_code are required (null only for a country with no states)')
            continue
        sid, code = c['state_id'], c['state_code']
        if sid is None and code is None:
            if country['id'] in with_states:
                errors.append(f"{label}: no state, but country {country['iso2']} has states")
        elif sid is None or code is None:
            errors.append(f'{label}: state_id and state_code must both be set or both be null')
        elif not positive_id(sid):
            errors.append(f'{label}: state_id {sid!r} is not a positive integer')
        elif sid not in by_state:
            errors.append(f'{label}: state_id {sid} does not exist')
        elif by_state[sid]['country_id'] != country['id']:
            errors.append(f"{label}: state {sid} belongs to country {by_state[sid]['country_code']}, not {country['iso2']}")
        elif code != by_state[sid]['iso2']:
            errors.append(f"{label}: state_code {code!r} does not match state {sid} ({by_state[sid]['iso2']})")
    return errors


def _state_pair_errors(label, sid, code, country, by_state):
    """Errors for one (state_id, state_code) pair that must name a state of this country by its own code."""
    if not positive_id(sid):
        return [f'{label}: state_id {sid!r} is not a positive integer']
    if sid not in by_state:
        return [f'{label}: state_id {sid} does not exist']
    if by_state[sid]['country_id'] != country['id']:
        return [f"{label}: state {sid} belongs to country {by_state[sid]['country_code']}, not {country['iso2']}"]
    if code != by_state[sid]['iso2']:
        return [f"{label}: state_code {code!r} does not match state {sid} ({by_state[sid]['iso2']})"]
    return []


def check_counties(countries, states, counties, cities):
    """Errors for invalid counties or city county links (v5, decision B6). A county either has one state (state_id and
    state_code set, no states list) or spans several regions (both null, and states lists two or more distinct
    {state_id, state_code} pairs of its country; it then needs an explicit id). A city linked to a county must have
    its own state among the county's states."""
    errors = []
    by_country = _countries(countries, errors)
    by_state = _states(states, by_country, errors)
    if errors:
        return errors
    regions = {}   # county id -> the set of state ids it covers
    for k in counties:
        if not isinstance(k, dict):
            errors.append('a county row is not an object')
            continue
        label = f"county {k.get('id', '(new)')} {k.get('name', '')}".rstrip()
        country = by_country.get(k.get('country_id')) if positive_id(k.get('country_id')) else None
        if country is None or k.get('country_code') != country['iso2']:
            errors.append(f"{label}: country_id {k.get('country_id')!r} and country_code {k.get('country_code')!r} do not name one known country")
            continue
        if 'state_id' not in k or 'state_code' not in k:
            errors.append(f'{label}: state_id and state_code are required (null only for a county of several regions)')
            continue
        sid, code, listed = k['state_id'], k['state_code'], k.get('states')
        if (sid is None) != (code is None):
            errors.append(f'{label}: state_id and state_code must both be set or both be null')
            continue
        if sid is not None:
            if listed is not None:
                errors.append(f'{label}: has a state, so it cannot also list states (states is only for a county of several regions)')
                continue
            problems = _state_pair_errors(label, sid, code, country, by_state)
            errors += problems
            covered = set() if problems else {sid}
        else:
            if listed is None:
                errors.append(f'{label}: no state: list its regions in states (two or more), or set its state')
                continue
            if not isinstance(listed, list):
                errors.append(f'{label}: states must be a list of {{state_id, state_code}}')
                continue
            if not positive_id(k.get('id')):
                errors.append(f'{label}: a county of several regions needs an explicit id')
            covered, problems = set(), []
            for entry in listed:
                if not isinstance(entry, dict) or set(entry) != {'state_id', 'state_code'}:
                    problems.append(f'{label}: each entry of states needs only state_id and state_code')
                    continue
                entry_problems = _state_pair_errors(f"{label}: states entry", entry['state_id'],
                                                    entry['state_code'], country, by_state)
                problems += entry_problems
                if not entry_problems:
                    covered.add(entry['state_id'])
            if not problems and (len(covered) < 2 or len(covered) != len(listed)):
                problems.append(f'{label}: states must list two or more distinct regions')
            errors += problems
        if positive_id(k.get('id')):
            if k['id'] in regions:
                errors.append(f'{label}: id is duplicated')
            regions[k['id']] = (covered, sid)
    for c in cities:
        if not isinstance(c, dict) or c.get('county_id') is None:
            continue
        label = f"city {c.get('id', '(new)')} {c.get('name', '')}".rstrip()
        if c['county_id'] not in regions or not positive_id(c['county_id']):
            errors.append(f"{label}: county_id {c['county_id']!r} does not exist")
            continue
        covered, own = regions[c['county_id']]
        if covered and c.get('state_id') not in covered:
            errors.append(f"{label}: state {c.get('state_id')} is not county {c['county_id']}'s state ({own})" if own is not None
                          else f"{label}: state {c.get('state_id')} is not one of county {c['county_id']}'s regions")
    return errors
