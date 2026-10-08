'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { isWithinBounds, normalizePostcodeCode, validateRecord } = require('./utils');

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

test('bounds: the buffer wraps across the 180° meridian', () => {
  const east = { minLat: -1, maxLat: 1, minLon: 179, maxLon: 179.9 };
  assert.equal(isWithinBounds(0, -179.9, east, 0.45), true); // 0.2° past the east edge
  assert.equal(isWithinBounds(0, -179.3, east, 0.45), false); // 0.8° past it
  const west = { minLat: -1, maxLat: 1, minLon: -179.9, maxLon: -179 };
  assert.equal(isWithinBounds(0, 179.9, west, 0.45), true); // 0.2° past the west edge
  const nearlyAll = { minLat: -1, maxLat: 1, minLon: -179.5, maxLon: 179.5 };
  assert.equal(isWithinBounds(0, 180, nearlyAll, 0.45), false); // 0.5° from both edges: in the 0.1° gap
  assert.equal(isWithinBounds(0, 180, nearlyAll, 0.5), true); // buffered width reaches 360°: every longitude
  assert.equal(isWithinBounds(5, 0, nearlyAll, 0.5), false); // latitude still applies
});

const bounds = require('../data/country-bounds.json');

test('bounds: FR southern islands are inside, Madagascar and Mozambique are not', () => {
  const B = 0.45; // validate-coordinates.js BUFFER_DEGREES
  assert.equal(isWithinBounds(-49.237442, 69.622759, bounds.FR, B), true); // TAAF state record (Kerguelen)
  assert.equal(isWithinBounds(-49.35, 70.22, bounds.FR, B), true); // Port-aux-Français, Kerguelen
  assert.equal(isWithinBounds(-46.4075, 51.7575, bounds.FR, B), true); // Île de la Possession, Crozet
  assert.equal(isWithinBounds(-37.825833, 77.554722, bounds.FR, B), true); // Île Amsterdam
  assert.equal(isWithinBounds(-38.73, 77.522222, bounds.FR, B), true); // Île Saint-Paul
  assert.equal(isWithinBounds(-22.368333, 40.363333, bounds.FR, B), true); // Europa
  assert.equal(isWithinBounds(-21.4825, 39.671944, bounds.FR, B), true); // Bassas da India
  assert.equal(isWithinBounds(-17.054444, 42.725, bounds.FR, B), true); // Juan de Nova
  assert.equal(isWithinBounds(-11.55, 47.333333, bounds.FR, B), true); // Glorioso Islands
  assert.equal(isWithinBounds(-15.892222, 54.524722, bounds.FR, B), true); // Tromelin
  assert.equal(isWithinBounds(-18.91368, 47.53613, bounds.FR, B), false); // Antananarivo, Madagascar
  assert.equal(isWithinBounds(-14.56257, 40.68538, bounds.FR, B), false); // Nacala, Mozambique
});

test('bounds: CN Paracel and Spratly records are inside, Borneo is not', () => {
  const B = 0.45;
  assert.equal(isWithinBounds(16.8322714, 112.3338391, bounds.CN, B), true); // Sansha (Woody Island)
  assert.equal(isWithinBounds(16.4811321, 111.9302363, bounds.CN, B), true); // Xisha district
  assert.equal(isWithinBounds(9.5453158, 112.8869688, bounds.CN, B), true); // Nansha district (Fiery Cross Reef)
  assert.equal(isWithinBounds(9.916667, 115.533333, bounds.CN, B), true); // Mischief Reef
  assert.equal(isWithinBounds(5.9749, 116.0724, bounds.CN, B), false); // Kota Kinabalu, Malaysia
  assert.equal(isWithinBounds(4.39928, 113.99163, bounds.CN, B), false); // Miri, Malaysia
});

test('type_local is a known optional field on cities and states', () => {
  const city = {
    name: 'Strasbourg', state_id: 5035, state_code: '67', country_id: 75, country_code: 'FR',
    latitude: '48.58', longitude: '7.75', type: 'municipality', type_local: 'commune', level: 4,
  };
  const state = { name: 'Bas-Rhin', country_id: 75, country_code: 'FR', type: 'metropolitan department', type_local: 'département', level: 2 };
  assert.deepEqual(validateRecord(city, 'cities', 0), { errors: [], warnings: [] });
  assert.deepEqual(validateRecord(state, 'states', 0), { errors: [], warnings: [] });
});

test('an over-long type_local is flagged', () => {
  const city = {
    name: 'X', state_id: 1, state_code: 'X', country_id: 1, country_code: 'FR',
    latitude: '1', longitude: '1', type_local: 'x'.repeat(192),
  };
  assert.match(validateRecord(city, 'cities', 0).warnings.join('\n'), /type_local.*191/);
});
