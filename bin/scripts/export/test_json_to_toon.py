"""Regression tests for the TOON converter's edge cases."""
import unittest

from json_to_toon import json_to_toon


class JsonToToonTest(unittest.TestCase):
    """Edge cases of json_to_toon."""

    def test_empty_root_array_is_spec_form(self):
        """An empty dataset (e.g. counties before any are imported) encodes as [] per TOON spec 9.1."""
        self.assertEqual(json_to_toon("[]"), "[]")

    def test_non_array_still_rejected(self):
        """Anything other than a top-level array is still an error."""
        with self.assertRaises(ValueError):
            json_to_toon("{}")

    def test_null_is_the_null_literal(self):
        """A null value (e.g. the state of a city in a country with no states) encodes as null, not a blank cell."""
        out = json_to_toon('[{"id": 1, "state_id": null, "state_code": null}, {"id": 2, "state_id": 7, "state_code": "LA"}]')
        self.assertEqual(out.splitlines()[1:], ["  1,null,null", "  2,7,LA"])

    def test_literal_words_stay_strings(self):
        """A string spelled null, true or false is quoted so it decodes as a string."""
        out = json_to_toon('[{"name": "null"}, {"name": "true"}]')
        self.assertEqual(out.splitlines()[1:], ['  "null"', '  "true"'])

    def test_list_is_json_text(self):
        """A list (a county's states, v5) is one quoted cell of compact JSON, never a Python repr."""
        out = json_to_toon('[{"id": 9, "states": [{"state_id": 4060, "state_code": "MWT"}, {"state_id": 4061, "state_code": "WKO"}]}]')
        self.assertEqual(out.splitlines()[1], '  9,"[{\\"state_id\\":4060,\\"state_code\\":\\"MWT\\"},{\\"state_id\\":4061,\\"state_code\\":\\"WKO\\"}]"')

    def test_strings_that_look_like_numbers_stay_strings(self):
        """A string state code "1" or a coordinate string is quoted (it would decode as a number); numbers are not."""
        out = json_to_toon('[{"id": 4213, "state_id": 2062, "state_code": "1", "latitude": "-38.86700000", "code": "01"}]')
        self.assertEqual(out.splitlines()[1], '  4213,2062,"1","-38.86700000","01"')

    def test_quoting_matches_the_reference_encoder(self):
        """Colons, brackets, a leading # and backslashes are quoted and escaped as the TOON reference encoder does."""
        out = json_to_toon('[{"a": "x:y", "b": "[x]", "c": "#1", "d": "a\\\\b", "e": ""}]')
        self.assertEqual(out.splitlines()[1], '  "x:y","[x]","#1","a\\\\b",""')


if __name__ == "__main__":
    unittest.main()
