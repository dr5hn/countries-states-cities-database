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


if __name__ == "__main__":
    unittest.main()
