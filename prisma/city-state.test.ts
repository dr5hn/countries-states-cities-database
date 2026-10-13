// Run: node --test prisma/city-state.test.ts (Node 23.6 or later reads the TypeScript directly)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cityStateId, countyStates, localStateIds, type StateContext } from './city-state.ts';

const ctx: StateContext = {
  sourceStates: new Map([[1457, { country_code: 'US', iso2: 'LA' }]]),
  countriesWithStates: new Set(['US']),
  seededStateId: new Map([[1457, 7]]),
};
const eh = { id: 1, name: 'Smara', country_code: 'EH', state_id: null, state_code: null, state_name: null };
const us = { id: 2, name: 'Baton Rouge', country_code: 'US', state_id: 1457, state_code: 'LA', state_name: 'Louisiana' };

test('maps a normal city to its seeded state and a stateless city to null', () => {
  assert.equal(cityStateId(us, ctx), 7);
  assert.equal(cityStateId(eh, ctx), null);
});

test('throws instead of dropping an inconsistent city', () => {
  const bad = [
    [{ id: 3, country_code: 'EH' }, /required/],
    [{ ...us, state_id: null, state_code: null, state_name: null }, /US has states/],
    [{ ...eh, state_name: 'X' }, /needs state_name: null/],
    [{ ...us, state_code: null }, /both be set or both be null/],
    [{ ...us, state_id: '1457' as unknown as number }, /not a positive integer/],
    [{ ...us, state_id: 99 }, /does not exist/],
    [{ ...us, country_code: 'EH' }, /is in US, not EH/],
    [{ ...us, state_code: 'XX' }, /does not match/],
  ] as const;
  for (const [city, re] of bad) assert.throws(() => cityStateId(city, ctx), re);
  assert.throws(() => cityStateId(us, { ...ctx, seededStateId: new Map() }), /was not seeded/);
});

test('same-named states of one country map by their code, never collapse', () => {
  const source = [{ id: 523, country_code: 'AZ', iso2: 'YEV' }, { id: 538, country_code: 'AZ', iso2: 'YE' }];   // both named Yevlakh
  const seeded = [{ id: 11, countryId: 16, iso2: 'YE' }, { id: 12, countryId: 16, iso2: 'YEV' }];
  const map = localStateIds(source, seeded, new Map([['AZ', 16]]));
  assert.deepEqual([...map], [[523, 12], [538, 11]]);
  assert.throws(() => localStateIds(source, [...seeded, { id: 13, countryId: 16, iso2: 'YE' }], new Map([['AZ', 16]])), /used twice/);
  assert.throws(() => localStateIds(source, seeded.slice(0, 1), new Map([['AZ', 16]])), /source state 523 .* has no seeded state/);
});

test('no escape paths: a stateless city needs state_name null, and a state needs its own code', () => {
  const { state_name, ...noName } = eh;
  assert.throws(() => cityStateId(noName, ctx), /needs state_name: null/);
  const noCode = { ...ctx, sourceStates: new Map([[1457, { country_code: 'US', iso2: null }]]) };
  assert.throws(() => cityStateId({ ...us, state_code: 'WRONG' }, noCode), /has no state code/);
});

// v5 (decision B6): a county of several regions has no state of its own and lists its regions
const nz: StateContext = {
  sourceStates: new Map([[4060, { country_code: 'NZ', iso2: 'MWT' }], [4061, { country_code: 'NZ', iso2: 'WKO' }],
    [1457, { country_code: 'US', iso2: 'LA' }]]),
  countriesWithStates: new Set(['NZ', 'US']),
  seededStateId: new Map([[4060, 30], [4061, 31], [1457, 7]]),
};
const regions = [{ state_id: 4060, state_code: 'MWT' }, { state_id: 4061, state_code: 'WKO' }];
const waitomo = { id: 9, name: 'Waitomo District', country_code: 'NZ', state_id: null, state_code: null, states: regions };

test('maps a county to its seeded state, or a county of several regions to its seeded regions', () => {
  assert.deepEqual(countyStates({ ...waitomo, state_id: 4061, state_code: 'WKO', states: null }, nz), { stateId: 31, regions: [] });
  assert.deepEqual(countyStates(waitomo, nz), { stateId: null, regions: [30, 31] });
});

test('throws instead of seeding an inconsistent county', () => {
  const bad = [
    [{ ...waitomo, states: undefined }, /two or more distinct regions/],
    [{ ...waitomo, states: [regions[0]] }, /two or more distinct regions/],
    [{ ...waitomo, states: [regions[0], regions[0]] }, /two or more distinct regions/],
    [{ ...waitomo, state_id: 4061, state_code: 'WKO' }, /cannot also list states/],
    [{ ...waitomo, state_code: 'WKO' }, /both be set or both be null/],
    [{ ...waitomo, states: [regions[0], { state_id: 1457, state_code: 'LA' }] }, /is in US, not NZ/],
    [{ ...waitomo, states: [regions[0], { state_id: 4061, state_code: 'XX' }] }, /does not match/],
  ] as const;
  for (const [county, re] of bad) assert.throws(() => countyStates(county, nz), re);
});
