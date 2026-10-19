"""The sync writes MySQL DECIMAL coordinates as plain fixed-point text, never in exponent form."""
import unittest
from decimal import Decimal

from sync_mysql_to_json import MySQLToJSONSync


class CoordinateTextTest(unittest.TestCase):
    """process_row() on coordinate columns, without a database."""

    def convert(self, value):
        """The text the sync writes for one latitude value."""
        sync = MySQLToJSONSync.__new__(MySQLToJSONSync)   # process_row needs no connection
        return sync.process_row({'latitude': value}, ['latitude'], set())['latitude']

    def test_zero_is_written_with_its_scale_not_as_an_exponent(self):
        """MySQL returns 0.00000000 as Decimal('0E-8'); str() would write '0E-8'."""
        self.assertEqual(self.convert(Decimal('0E-8')), '0.00000000')

    def test_ordinary_values_keep_their_text(self):
        """Values the earlier code already wrote correctly are unchanged."""
        for text in ('-12.34560000', '38.71670000', '100.40000000', '-0.00010000'):
            self.assertEqual(self.convert(Decimal(text)), text)

    def test_null_stays_null(self):
        """A null coordinate stays null."""
        self.assertIsNone(self.convert(None))


if __name__ == '__main__':
    unittest.main()
