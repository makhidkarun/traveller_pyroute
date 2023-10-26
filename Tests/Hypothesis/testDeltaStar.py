import logging
import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, composite, integers, floats, lists, sampled_from

from PyRoute.DeltaStar import DeltaStar
from PyRoute.Galaxy import Sector
from PyRoute.TradeCodes import TradeCodes

tradecodes = []

@composite
def trade_code(draw):
    if 0 == len(tradecodes):
        tradecodes.extend(TradeCodes.pcodes)
        tradecodes.extend(TradeCodes.dcodes)
        tradecodes.extend(TradeCodes.ext_codes)
        tradecodes.extend(TradeCodes.allowed_residual_codes)

    strat = sampled_from(tradecodes)

    return draw(lists(strat, min_size=1, max_size=12))

@composite
def starline(draw):
    col = draw(integers(min_value=1, max_value=32))
    row = draw(integers(min_value=1, max_value=40))
    posn = str(col).rjust(2, '0') + str(row).rjust(2, '0')

    name = draw(text(min_size=1, max_size=15)).ljust(20)

    port = draw(text(min_size=1, max_size=1, alphabet="ABCDEX"))
    uwp_alphabet = '0123456789ABCDEFGH'

    uwp = port + draw(text(min_size=6, max_size=6, alphabet=uwp_alphabet)) + '-' + draw(text(min_size=1, max_size=1, alphabet=uwp_alphabet))

    # TODO - tradecode picks
    trade_array = draw(trade_code())
    tradeCodes = ' '.join(trade_array)

    extension_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # importance gets autogenned
    importance = '{ 0 }'

    # ex
    ex_tail = draw(integers(min_value=-5, max_value=5))
    if 0 > ex_tail:
        stub = str(ex_tail)
    else:
        stub = '+' + str(ex_tail)

    ex = '(' + draw(text(min_size=3, max_size=3, alphabet=extension_alphabet)) + stub + ')'

    # cx
    cx = '[' + draw(text(min_size=4, max_size=4, alphabet=extension_alphabet)) + ']'

    flip = draw(floats(min_value=0.0, max_value=1.0))

    noble_alphabet = 'BcCDeEfFGH'
    if 0.7 < flip:
        nobles = '-'
    else:
        nobles = draw(text(min_size=1, max_size=5, alphabet=noble_alphabet))

    base = '-'
    tradezone = draw(text(min_size=1, max_size=1, alphabet='-ARUF--'))

    pbg = draw(text(min_size=3, max_size=3, alphabet='0123456789'))

    worlds = str(draw(integers(min_value=0, max_value=12)))

    alg = 'NaHu'

    star = 'G5 V'

    starline = posn + ' ' + name + ' ' + uwp + ' ' + tradeCodes.ljust(38) + ' ' + importance + ' ' + ex + ' ' + cx + ' ' \
               + nobles + ' ' + base + ' ' + tradezone + ' ' + pbg + ' ' + worlds + ' ' + alg + ' ' + star

    return starline


class testDeltaStar(unittest.TestCase):

    """
    Given a Star object read in from a starline, trapping log error messages, ensure DeltaStar.check_canonical returns
    same number of messages
    """
    @given(starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)])
    @example('0101 0                    A000000-0                                       { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V ')
    @example('0101 0                    A000000-0                                       { 0 } (000+0) [0000] BBBBB - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (000+0) [0001] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 De                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Ga                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (000+0) [0010] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (000+0) [0100] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000100-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000200-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A00B000-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000400-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 Fl                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000000-0 As                                     { 0 } (00C+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A001000-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    @example('0101 0                    A000600-0 As                                     { 0 } (000+0) [0000] - - A 000 0 NaHu G5 V')
    def test_check_canonicalisation(self, starline):
        outer_logger = logging.getLogger("PyRoute.Star")
        inner_logger = logging.getLogger("PyRoute.TradeCodes")

        sector = Sector('# Core', '# 0, 0')

        with self.assertLogs(outer_logger, "DEBUG") as outer_logs:
            with self.assertLogs(inner_logger, "DEBUG") as inner_logs:
                star1 = DeltaStar.parse_line_into_star(starline, sector, 'fixed', 'fixed')
                self.assertIsNotNone(star1, "Fatal failure parsing line: " + starline)
                self.assertTrue(isinstance(star1, DeltaStar), "Error parsing line: " + starline)
                assume(0 < len(inner_logs.output))

                output = outer_logs.output
                output.extend(inner_logs.output)
                # trim complaints about calculated importance - that's fixed on import
                output = [line for line in output if "Calculated importance" not in line]
                # trim log lines of less than warning severity - "DEBUG" is set to ensure there will be output to grab
                output = [line for line in output if 'DEBUG:' not in line and 'INFO:' not in line]

                canonical_result, canonical_messages = star1.check_canonical()
                for msg in canonical_messages:
                    output = [line for line in output if msg not in line]

                num_output = len(output)
                tail = output[0] if 0 < len(output) else ''
                self.assertEqual(
                    0,
                    num_output,
                    "Mismatch between parsing logs and canonical-check: " + starline + '\n' + tail
                )


if __name__ == '__main__':
    unittest.main()
