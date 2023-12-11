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
    @example('Pi (Feime)? Re Sa ')
    @example('Cp Cp ')
    @example('000000000000000')
    @example('00000000000000000000000000000000000000')
    @example('(0000000000000000000000000000000000000')
    @example('0000000000 0000')
    @example('0000000000000000000000000000000000000)')
    @example('000000000000000000000000000000000000()')
    @example('[0000000000000000000000000000000000000')
    @example('{0000000000000000000000000000000000000')
    @example('000000000000000')
    @example('000000000 A0000 ')
    @example('000000000000000      ')
    @example('Hi Cs [Vilani]   ')
    @example(' Fl Ph Varg6 O:2723      ')
    @example('Ag Ni C:1627     ')
    @example('00000000000000( ')
    @example(' Ni Pa (Ashdak Meshukiiba) Sa     ')
    @example('000000000000 {} ')
    @example('00000000000 { } ')
    @example('000000000(0) 00   ')
    @example(' (0)000000000 00 ')
    @example('00000000000(0)0  ')
    @example(' 000000000000( )   ')
    @example(' Ga Lt (minor)  ')
    def test_parse_text_to_trade_code(self, s):
        trade = TradeCodes(s)

        result, msg = trade.is_well_formed()
        self.assertTrue(result, msg)

        trade_string = str(trade)

        nu_trade = TradeCodes(trade_string)
        result, msg = nu_trade.is_well_formed()
        self.assertTrue(result, msg)

        nu_trade_string = str(nu_trade)
        msg = "Re-parsed TradeCodes string does not equal original parsed string"
        self.assertEqual(trade_string, nu_trade_string, msg)

    @given(text(min_size=15, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    def test_verify_canonicalisation_is_idempotent(self, s):
        hyp_input = 'Hypothesis input: ' + s

        trade = TradeCodes(s)
        result, _ = trade.is_well_formed()
        assume(result)

        result, msg = trade.check_canonical()
        assume(0 < len(msg))

        trade.canonicalise()
        result, msg = trade.check_canonical()
        self.assertEqual(0, len(msg), "Canonicalisation failed.  " + hyp_input)


if __name__ == '__main__':
    unittest.main()
