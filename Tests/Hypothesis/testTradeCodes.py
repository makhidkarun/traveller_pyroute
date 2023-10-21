import unittest
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text

from PyRoute.TradeCodes import TradeCodes


class testTradeCodes(unittest.TestCase):

    """
    Given an otherwise-valid input string, it should parse cleanly to a well-formed TradeCodes object that then should
    cleanly round-trip to/from string
    """
    @given(text(min_size=15, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @example('(000000000000000000000000000000000000)')
    @example('000000000000000')
    def test_parse_text_to_trade_code(self, s):
        trade = TradeCodes(s)
        trade.trim_ill_formed_residual_codes()

        result, msg = trade.is_well_formed()
        self.assertTrue(result, msg)

        trade_string = str(trade)

        nu_trade = TradeCodes(trade_string)
        nu_trade.trim_ill_formed_residual_codes()
        result, msg = nu_trade.is_well_formed()
        self.assertTrue(result, msg)

        nu_trade_string = str(nu_trade)
        msg = "Re-parsed TradeCodes string does not equal original parsed string"
        self.assertEqual(trade_string, nu_trade_string, msg)


if __name__ == '__main__':
    unittest.main()
