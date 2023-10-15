import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex

from PyRoute.Galaxy import Sector
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Star import Star


class testStar(unittest.TestCase):

    """
    Given a regex-matching string, parse_line_to_star should return either a valid Star object or None
    """
    @given(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))  # suppress slow-data health check, too-much filtering
    @example('0101 000000000000000 00000O0-0 000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0)  - - - 0 000   00')
    @example('0101 000000000000000 00000ź0-0 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0101 000000000000000 ?000000-0 000000000000000 {0} (000-0) [0000] - - 0 000   00')
    @example('0100 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0150 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0101 000000000000000 ?000000-0 000000000000000 {0} (000-0) [0000] - - 0 000   00')
    @example('0101 000000000000000 ???????-? 0000000000000 0       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0)  - - - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   0000BDD')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 00A   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 0A0   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000       - -         0   000   0000D')
    @example('0101 000000000000000 ???????-? 000 0000000BCDEFG       - - 0 000   00')
    @example('0000 000000000000000 ???????-? (000000000000)00         - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   10 +')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   00 0')
    @example('0101 000000000000000 ???????-? 000000000000000         -   001   000')
    @example('0000 000000000000000 ???????-? 000000000000000         -   000   A00')
    @example('0000 000000000000000 ???????-? 000000000000000         -   000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - 000 0 ?00   00')
    @example('0000 000000000000000 0000000-0 000000000000000       0 0 0      000 000 000+')
    @example('0000 000000000000000 ???????-? {0}000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]   - a   000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       a -   000   00')
    @example('0101 000000000000000 ???????-? 00000000000+  0         - a 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       c -   000   00')
    @example('0101 000000000000000 ???????-? 00000000+  0000         -   000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]       - 0   000   0000D')
    def test_parse_line_to_star(self, s):
        hyp_line = "Hypothesis input: " + s
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        assume(foo is not None)
        # filter out malformed hex objects while we're at it
        result, _ = foo.hex.is_well_formed()
        assume(result)

        self.assertIsInstance(foo, Star)
        foo.index = 0
        foo.allegiance_base = foo.alg_base_code
        self.assertTrue(foo.is_well_formed())

        line = foo.parse_to_line()

        nu_foo = Star.parse_line_into_star(line, sector, pop_code, ru_calc)
        self.assertIsNotNone(nu_foo, "Output line did not reparse.  " + hyp_line)
        self.assertEqual(foo, nu_foo, "Reparsed star not _eq_ to original parsed star.  " + hyp_line)
        self.assertEqual(str(foo.nobles), str(nu_foo.nobles), "Reparsed nobles not equal.  " + hyp_line)
        self.assertEqual(str(foo.baseCode), str(nu_foo.baseCode), "Reparsed base not equal.  " + hyp_line)
        self.assertEqual(str(foo.zone), str(nu_foo.zone), "Reparsed zone not equal.  " + hyp_line)

        nu_line = nu_foo.parse_to_line()
        self.assertEqual(line, nu_line, "Reparsed line not equal to original line.  " + hyp_line)

    """
    Given a regex-matching string that results in a Star object when parsed, that Star should parse cleanly to an input
    line
    """
    @given(from_regex(regex=ParseStarInput.starline,
                      alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @settings(
        suppress_health_check=[HealthCheck(3), HealthCheck(2)],  # suppress slow-data health check, too-much filtering
        deadline = timedelta(1000))
    @example('0000 000000000000000 ???????-? 000000000000000       - - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]       - 0   000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {-0 } (000-0) [0000] -         - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0 } (000-0) [0000] -         - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 00A   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 0A0   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - -         0   000   00')
    @example('0101 000000000000000 ???????-? 00000000000000000000000000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0)  - - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       -       - 0   000   00')
    @example('0101 000000000000000 ???????-? (0000000000000000000000000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 0000000000 0000 {0} (000-0)  - - - 0 000   00')
    @example('0101 000000000000000 ???????-? 0000000000000000000000000000000000000)       - - 0 000   00')
    @example('0101 000000000000000 A000000-I 000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000000000000000000000000()       - - 0 000   00')
    @example('0101 000000000000000 ???????-? [0000000000000000000000000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? {0000000000000000000000000000000000000       - - 0 000   00')
    @example('0110 000000000000000 ???????-? 000000000000000 {0} (000-0)  -  Bc - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000 A0000 {0} (000-0)  - - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   00000 0 0 ')
    def test_parse_line_to_star_and_back(self, s):
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        assume(foo is not None)
        self.assertIsNotNone(foo._hash, "Hash not calculated for original star")

        foo.index = 0
        foo.allegiance_base = foo.alg_base_code
        self.assertTrue(foo.is_well_formed())

        parsed_line = foo.parse_to_line()
        self.assertIsNotNone(parsed_line)
        self.assertLessEqual(80, len(parsed_line), "Round-trip line unexpectedly short")

        nu_foo = Star.parse_line_into_star(parsed_line, sector, pop_code, ru_calc)
        self.assertTrue(isinstance(nu_foo, Star), "Round-trip line did not re-parse")
        nu_foo.index = 0
        nu_foo.allegiance_base = nu_foo.alg_base_code
        self.assertTrue(foo.is_well_formed())
        self.assertIsNotNone(foo._hash, "Hash not calculated for re-parsed star")

        self.assertEqual(foo, nu_foo, "Re-parsed star not __eq__ to original star.  Hypothesis input: " + s)
        self.assertEqual(
            str(foo.tradeCode),
            str(nu_foo.tradeCode),
            "Re-parsed trade codes not equal to original trade codes."
        )

        nu_parsed_line = nu_foo.parse_to_line()
        self.assertEqual(
            parsed_line,
            nu_parsed_line,
            "New reparsed starline does not equal original parse-to-line output.  Hypothesis input: " + s
        )

    def test_fallback_regexen_base_ix_ex_cx(self):
        regex = r"((\{ *[+-]?[0-6] ?\}) +(\([0-9A-Z]{3}[+-]\d\)|- ) +(\[[0-9A-Z]{4}\]|-)|( ) ( ) ( )) +(\w{1,5}|-| ) +(.*)"

        test_str = "{ -2 } (000-0) -      Bc   -  - 000 0  00 '\n"

        self._show_matches(regex, test_str)

    def test_fallback_regexen_ix_ex_cx_with_trade_code(self):
        regex = r"((.{15,}) +(\{ *[+-]?[0-6] ?\}) +(\([0-9A-Z]{3}[+-]\d\)|- ) +(\[[0-9A-Z]{4}\]|-)|( ) ( ) ( )) +(\w{1,5}|-| ) +(.*)"

        test_str = 'A0000                                 { -2 } (000-0) -      -    -  - 000 0  00 '

        self._show_matches(regex, test_str)

    def test_fallback_regex_noble_line(self):
        regex = r"(\w{1,3}|-|\*) +(\w|-| ) +(.*)"

        test_str = '-  - 000 0  00 '

        self._show_matches(regex, test_str)

    @staticmethod
    def _show_matches(regex, test_str):
        matches = re.finditer(regex, test_str, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):

            print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
                                                                                end=match.end(), match=match.group()))

            for groupNum in range(0, len(match.groups())):
                groupNum = groupNum + 1

                print("Group {groupNum} found at {start}-{end}: {group}".format(groupNum=groupNum,
                                                                                start=match.start(groupNum),
                                                                                end=match.end(groupNum),
                                                                                group=match.group(groupNum)))


if __name__ == '__main__':
    unittest.main()
