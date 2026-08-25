'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const {
  findPostcodeDuplicates,
  isSelfComparison,
  postcodeKey,
} = require('./detect-duplicates');

const base = {
  id: 1,
  code: '110001',
  country_code: 'IN',
  state_id: 4021,
  city_id: null,
  locality_name: 'Sansad Marg',
  type: 'full',
};

test('normalizes locality names in postcode comparison keys', () => {
  assert.equal(
    postcodeKey(base),
    postcodeKey({ ...base, locality_name: '  SANSAD MARG ' }),
  );
});

test('normalizes postcode case and whitespace in comparison keys', () => {
  assert.equal(
    postcodeKey(base),
    postcodeKey({ ...base, code: '  110001  ' }),
  );
  assert.equal(
    postcodeKey({ ...base, code: 'SW1A 1AA' }),
    postcodeKey({ ...base, code: 'sw1a   1aa' }),
  );
});

test('allows a shared postcode across different locality records', () => {
  const records = [
    base,
    { ...base, id: 2, locality_name: 'Connaught Place' },
    { ...base, id: 3, state_id: 4008 },
    { ...base, id: 4, city_id: 9001 },
    { ...base, id: 5, type: 'partial' },
  ];

  assert.deepEqual(findPostcodeDuplicates(records), { checked: 5, duplicates: [] });
});

test('reports each repeated full postcode key once in linear order', () => {
  const duplicate = { ...base, id: 2, locality_name: ' sansad marg ' };
  const result = findPostcodeDuplicates([base, duplicate, { ...duplicate, id: 3 }]);

  assert.equal(result.checked, 3);
  assert.deepEqual(result.duplicates.map(({ index, record, existing }) => ({
    index,
    id: record.id,
    existingId: existing.id,
  })), [
    { index: 1, id: 2, existingId: 1 },
    { index: 2, id: 3, existingId: 1 },
  ]);
});

test('ignores records without a postcode code', () => {
  assert.deepEqual(findPostcodeDuplicates([{ ...base, code: '' }]), {
    checked: 0,
    duplicates: [],
  });
});

test('skips only the same id-less source record', () => {
  const record = { name: 'Al Barsha', latitude: '25.1055', longitude: '55.2086' };

  assert.equal(isSelfComparison(record, record), true);
  assert.equal(isSelfComparison(record, { ...record }), false);
});

test('skips existing records with the same id', () => {
  assert.equal(isSelfComparison({ id: 10 }, { id: '10' }), true);
  assert.equal(isSelfComparison({ id: 10 }, { id: 11 }), false);
});
