'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { normalizePostcodeCode, validateRecord } = require('./utils');

const postcode = {
  code: 'SW1A 1AA',
  country_id: 232,
  country_code: 'GB',
  type: 'street',
};

test('normalizes postcode codes for indexed lookup', () => {
  assert.equal(normalizePostcodeCode(' sw1a   1aa '), 'SW1A 1AA');
});

test('accepts a canonical postcode and current source type', () => {
  assert.deepEqual(validateRecord(postcode, 'postcodes', 0).errors, []);
});

test('blocks non-canonical postcode codes', () => {
  const { errors } = validateRecord({ ...postcode, code: ' sw1a   1aa ' }, 'postcodes', 0);
  assert.equal(errors.length, 1);
  assert.match(errors[0], /expected "SW1A 1AA"/);
});
