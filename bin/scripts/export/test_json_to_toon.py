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


if __name__ == "__main__":
    unittest.main()
