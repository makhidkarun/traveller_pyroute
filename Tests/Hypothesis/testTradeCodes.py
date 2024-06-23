import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, composite, sampled_from, lists, floats

from PyRoute.Galaxy import Sector
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.TradeCodes import TradeCodes
from PyRoute.Star import Star
from PyRoute.SystemData.UWP import UWP


tradecodes = []


@composite
def trade_code(draw):
    if 0 == len(tradecodes):
        tradecodes.extend(TradeCodes.pcodes)
        tradecodes.extend(TradeCodes.dcodes)
        tradecodes.extend(TradeCodes.ext_codes)
        tradecodes.extend(TradeCodes.allowed_residual_codes)

    strat = sampled_from(tradecodes)

    return draw(lists(strat, min_size=2, max_size=12))


@composite
def trade_line(draw):
    choice = draw(floats(min_value=0.0, max_value=1.0))

    if 0.5 > choice:
        return draw(text(min_size=15, max_size=36, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    return draw(trade_code())


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
    @example('Cp Cp Cp Cp Cp Cp Cp Cp Cp Cp')
    @example('Cp Cx Cs Mr Da RsA RsB RsG ')
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

    @given(from_regex(regex=UWP.match, alphabet='0123456789abcdefghjklmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWYXZ -{}()[]?\'+*'),
          trade_line())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))  # suppress slow-data health check, too-much filtering
    @example('A000000-0', '000000000000000')
    @example('A000100-0', '000000000000000')
    @example('A000400-0', '000000000000000')
    @example('A001000-0', '000000000000000')
    @example('A000600-0', '000000000000000')
    @example('A000700-0', '000000000000000')
    @example('A020000-0', '000000000000000')
    @example('A0A1000-0', '000000000000000')
    @example('A320000-0', '000000000000000')
    @example('A044400-0', '000000000000000')
    @example('A044500-0', '000000000000000')
    @example('A060500-0', '000000000000000')
    @example('A000800-0', '000000000000000')
    @example('A000900-0', '000000000000000')
    @example('A060600-0', '000000000000000')
    @example('A33A000-0', '000000000000000')
    @example('A655000-0', '000000000000000')
    @example('A000000-0', 'Ba')
    @example('ABDA000-0', '000000000000000')
    def test_verify_canonicalisation_is_idempotent(self, s, trade_line):
        s = s[0:9]
        if isinstance(trade_line, list):
            trade_line = ' '.join(trade_line)
        hyp_input = 'Hypothesis input: \'' + s + '\', \'' + trade_line + '\''
        starline = '0101 000000000000000 {} {}  - - A 000   0000D'.format(s, trade_line.ljust(38))
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'

        foo = None

        try:
            foo = Star.parse_line_into_star(starline, sector, pop_code, ru_calc)
        except KeyError:
            pass
        assume(foo is not None)
        # filter out malformed tradeCode objects while we're at it
        result, _ = foo.tradeCode.is_well_formed()
        assume(result)
        trade = foo.tradeCode

        result, msg = trade.check_canonical(foo)
        assume(0 < len(msg))

        trade.canonicalise(foo)
        result, msg = trade.check_canonical(foo)
        badline = '' if result else msg[0]
        self.assertEqual(0, len(msg), "Canonicalisation failed.  " + badline + '\n' + hyp_input)


if __name__ == '__main__':
    unittest.main()
