import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, none

from PyRoute.Galaxy import Sector
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Star import Star


class testStar(unittest.TestCase):

    """
    Given a regex-matching string, parse_line_to_star should return either a valid Star object or None
    """
    @given(from_regex(regex=ParseStarInput.starline,
                  alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
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
    @example('0101 000000000000000 ???????-? 000000000000000 { 0 }       -  -  - 000 0 000   00')
    def test_parse_line_to_star(self, s):
        hyp_line = "Hypothesis input: " + s
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        allowed = ['Input UWP malformed']
        foo = None

        try:
            foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        except ValueError as e:
            if str(e) in allowed:
                pass
            else:
                raise e
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

        line = nu_foo.parse_to_line()
        nu_foo = Star.parse_line_into_star(line, sector, pop_code, ru_calc)

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
        deadline=timedelta(1000))
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
    @example('1717 Vland                A967A9A-F Hi Cs [Vilani]            { 3 }  (D9F+5) [CD7H] BEFG N  - 310 7  ImDv F8 V           ')
    @example('0101 000000000000000 ???????-? (000000000000000000000000000000000000)       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 00000000000000( {1} (000-0)  -         - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0 } -       -   - 0 000   00')
    @example('0110 000000000000000 ???????-? 000000000000000 {1} -   - -         - 0 000   00')
    @example('0101 000000000000000 ???????-? 00000000000000( {1 } (000-0)  -  -         - 0 000   00')
    @example('0101 000000000000000 ???????-? 00000000000000( { 1} (000-0)  -  -       - 0   000   00')
    @example('0000 000000000000000 ???????-? 0000000000000 0 {0} -       -   - 0 000   00')
    @example('0101 000000000000000 ???????-? 00000000000000( { +0 } (000-0)  -         - 0 000   00')
    @example('2723 Lyndon               C9C68B7-9 Fl Ph Varg6 O:2723         { 0 }  (F79+1) [8859] - M  - 723 15 JuHl F0 V          ')
    @example('1627 Ricelun              C858598-9 Ag Ni C:1627                { 0 } (641+1) [4598] - -  - 802 9  Pd G6 V         ')
    @example('0101 000000000000000 ???????-? 00000000000000( { 1 } (000-0) [0000] -       - 0   000   00')
    @example('2405 Uurku                B986445-9 Ni Pa (Ashdak Meshukiiba) Sa          { 0 }  (A33-2) [2437] Bc   -  - 222 8  ImDv K1 V')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   0000V')
    @example('0110 000000000000000 ???????-? 00000000000000( {1} (000-0)       -   - 0 000   00')
    @example('0000 000000000000000 ???????-? 000000000000 {}       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 00000000000 { }       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000(0) 00       - - 0 000   00')
    @example('0101 000000000000000 ???????-? (0)000000000 00       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 00000000000(0)0       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000( )       - - 0 000   00')
    @example('0101 000000000000000 AzzzZxz-z 000000000000000 {0} (000-0) [0000] - - 0 000   00')
    @example('2202 Misaruu              C527747-7 Pi (Feime)? Re Sa                     { -1 } (967-1) [7657] BD   -  - 413 11 ImDv M1 V           ')
    @example('3015 Anix Nuno            C446953-B Hi In (Anixii)W Da          {  3 } (68A-5) [7CAC] - - A 901 11 HvFd M3 V M4 V')
    @example('3135                      ?478???-?                                     - - - ?02   Na')
    @example('0310                      ?776???-?                                     - - - ?03   Kk        ')
    @example('1001 Barnett 0201         X??????-?                                       - - A 013   Na K4 V                 ')
    @example('0302 Adams 0302           X3?????-?                                       - - - 001   Na K6 V                 ')
    @example('0610 Adams 0610           X21????-?                                       - - - 001   Na G8 V M3 V K2 V       ')
    @example('1732                      ?AFA???-? Fl Wa                               - - - ?13   Na        ')
    @example('1937 Osthoff 0307         X9C0???-? Pz                                    - - A 001   Na K1 V K4 V K2 V       ')
    @example('0615 Bespin II            EAA19AC-4 Fl Hi He In          {+0} (98b-1) [A935] - - - 223 9  Na G1 V           ')
    @example('0810                      ?124???-F                                     - - - ?03   Kk')
    @example('0401                      ?342???-B Po                                  - - - ?14   Kk        ')
    @example('1204 Barnett 0404         E756???-1 Ga Lt (minor)                         - - A 401   Na G9 V                 ')
    @example('0101 Raktegham            C529767-?                                      - K - 921   K3        ')
    @example('0403 Kirrughee            C110314-? Lo                                   - O - 223   K3        ')
    @example('0631 Closser              X100755-6 Na Va Pi Tz          {-2} (665+1) [5597} - - - 810 6  Na M5 V M7 V          ')
    @example('1036                      ?6319EJ-? Lk Po Sa                            - - - 601 7 Na G8 V G0 V K1 V K4 V     ')
    def test_parse_line_to_star_and_back(self, s):
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        allowed = ['Input UWP malformed']
        foo = None

        try:
            foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        except ValueError as e:
            if str(e) in allowed:
                pass
            else:
                raise e
        assume(foo is not None)
        foo.trim_self_ownership()
        foo.trim_self_colonisation()
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
        self.assertTrue(nu_foo.is_well_formed(log=False))
        self.assertIsNotNone(nu_foo._hash, "Hash not calculated for re-parsed star")

        self.assertEqual(foo, nu_foo, "Re-parsed star not __eq__ to original star.  Hypothesis input: " + s + '\n')
        self.assertEqual(
            str(foo.tradeCode),
            str(nu_foo.tradeCode),
            "Re-parsed trade codes not equal to original trade codes.  Hypothesis input: " + s + '\n'
        )
        self.assertEqual(
            len(foo.star_list),
            len(nu_foo.star_list),
            "Re-parsed star list different length to original star list.  Hypothesis input: " + s + '\n'
        )

        nu_parsed_line = nu_foo.parse_to_line()
        self.assertEqual(
            parsed_line,
            nu_parsed_line,
            "New reparsed starline does not equal original parse-to-line output.  Hypothesis input: " + s + '\n'
        )

    @given(from_regex(regex=r"(.{4,41})",
                      alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'),
           none())
    @example('0 0', '')
    @example('0', '')
    @example('A0 II', 'A0 II')
    @example('0BDD', 'D BD')
    @example('A0', 'A0 V')
    @example('M2 D F3 V M0 D M5 D', 'F3 V M2 D M0 D M5 D')
    @example('0000 V', '')
    def test_split_stellar_data(self, s, expected):
        sector = Sector('# Core', '# 0, 0')
        star = None

        allowed_messages = [
            'No stars found'
        ]

        try:
            star = Star()
            star.name = "Test Split Star"
            star.index = 0
            star.sector = sector
            star.allegiance_base = 'NaXX'
            star.stars = s
            star.split_stellar_data()
        except ValueError as e:
            if str(e) in allowed_messages:
                # reset generation attempt
                star = None
                pass
            else:
                raise e
        assume(star is not None)
        self.assertIsNotNone(star.star_list_object, "StarList object not set after parsing")

        result, msg = star.star_list_object.is_well_formed()
        self.assertTrue(result, msg)

        if expected is not None:
            self.assertEqual(expected, str(star.star_list_object))

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
