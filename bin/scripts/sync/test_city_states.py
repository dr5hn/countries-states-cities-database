"""Tests for the city state-pair preflight (import) and the sync's required state keys (v5: cities without a state)."""
import sys
import types
import unittest

for name in ('mysql', 'mysql.connector'):   # the importer needs a database driver only at run time
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules['mysql'].connector = sys.modules['mysql.connector']
from import_json_to_mysql import check_city_states  # noqa: E402

COUNTRIES = [{'id': 233, 'iso2': 'US'}, {'id': 244, 'iso2': 'EH'}]
STATES = [{'id': 1457, 'country_id': 233, 'state_code': 'LA', 'iso2': 'LA'}]
city = lambda **k: {'id': 1, 'name': 'X', 'country_id': 244, 'country_code': 'EH', **k}


class CityStatesTest(unittest.TestCase):
    """Each rule of the preflight, with one valid case for each kind of city."""

    def test_valid_cities_pass(self):
        """A stateless city of a country with no states, and a normal city, both pass."""
        ok = [city(state_id=None, state_code=None),
              city(id=2, country_id=233, country_code='US', state_id=1457, state_code='LA')]
        self.assertEqual(check_city_states(ok, COUNTRIES, STATES), [])

    def test_rejections(self):
        """Missing keys, half-null pairs, wrong types, unknown states, other countries and wrong codes all fail."""
        cases = {
            'required': city(),
            'no state, but country US has states': city(country_id=233, country_code='US', state_id=None, state_code=None),
            'both be set or both be null': city(state_id=None, state_code='LA'),
            'not a positive integer': city(country_id=233, state_id='1457', state_code='LA'),
            'does not exist': city(country_id=233, state_id=99, state_code='LA'),
            'belongs to country 233': city(state_id=1457, state_code='LA'),
            'does not match state': city(country_id=233, state_id=1457, state_code='XX'),
        }
        for expected, record in cases.items():
            errors = check_city_states([record], COUNTRIES, STATES)
            self.assertTrue(any(expected in e for e in errors), f'{expected}: {errors}')

    def test_bool_is_not_an_id(self):
        """True is not accepted as state id 1."""
        errors = check_city_states([city(country_id=233, state_id=True, state_code='LA')], COUNTRIES, STATES)
        self.assertTrue(any('not a positive integer' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
