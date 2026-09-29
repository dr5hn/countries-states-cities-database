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

const { isWithinBounds } = require('./utils');

test('bounds: a plain box, with and without the buffer', () => {
  const box = { minLat: 36.0, maxLat: 43.79, minLon: -9.3, maxLon: 4.33 };
  assert.equal(isWithinBounds(40.4, -3.7, box), true); // Madrid
  assert.equal(isWithinBounds(28.1, -16.7, box, 0.45), false); // Tenerife, outside the mainland box
  assert.equal(isWithinBounds(43.9, 0, box, 0.45), true); // within the buffer
});

test('bounds: several boxes cover remote territories', () => {
  const es = [
    { minLat: 36.0, maxLat: 43.79, minLon: -9.3, maxLon: 4.33 },
    { minLat: 27.6, maxLat: 29.5, minLon: -18.2, maxLon: -13.3 },
  ];
  assert.equal(isWithinBounds(28.1, -16.7, es, 0.45), true); // Tenerife
  assert.equal(isWithinBounds(41.4, 2.2, es, 0.45), true); // Barcelona
  assert.equal(isWithinBounds(18.4, -66.1, es, 0.45), false); // San Juan, Puerto Rico
});

test('bounds: a box crossing the 180° meridian', () => {
  const ru = { minLat: 41.19, maxLat: 81.86, minLon: 19.64, maxLon: -169.05 };
  assert.equal(isWithinBounds(55.75, 37.62, ru, 0.45), true); // Moscow
  assert.equal(isWithinBounds(64.73, 177.5, ru, 0.45), true); // Anadyr, east of 170°E
  assert.equal(isWithinBounds(66.0, -170.0, ru, 0.45), true); // Chukotka, west of 180°
  assert.equal(isWithinBounds(55.0, 0.0, ru, 0.45), false); // North Sea
  assert.equal(isWithinBounds(40.0, 60.0, ru, 0.45), false); // south of the box
});
