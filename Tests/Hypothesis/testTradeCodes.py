import unittest
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text

from TradeCodes import TradeCodes


class testTradeCodes(unittest.TestCase):

    """
    Given an otherwise-valid input string, it should parse cleanly to a well-formed TradeCodes object
    """
    @given(text(min_size=15, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @example('(000000000000000000000000000000000000)')
    def test_parse_text_to_trade_code(self, s):
        trade = TradeCodes(s)

        result, msg = trade.is_well_formed()
        self.assertTrue(result, msg)


if __name__ == '__main__':
    unittest.main()
