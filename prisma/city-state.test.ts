// Run: node --test prisma/city-state.test.ts (Node 22.6+ strips the types)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cityStateId, type StateContext } from './city-state.ts';

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
    [{ ...eh, state_name: 'X' }, /state_name is set/],
    [{ ...us, state_code: null }, /both be set or both be null/],
    [{ ...us, state_id: '1457' as unknown as number }, /not a positive integer/],
    [{ ...us, state_id: 99 }, /does not exist/],
    [{ ...us, country_code: 'EH' }, /is in US, not EH/],
    [{ ...us, state_code: 'XX' }, /does not match/],
  ] as const;
  for (const [city, re] of bad) assert.throws(() => cityStateId(city, ctx), re);
  assert.throws(() => cityStateId(us, { ...ctx, seededStateId: new Map() }), /was not seeded/);
});
