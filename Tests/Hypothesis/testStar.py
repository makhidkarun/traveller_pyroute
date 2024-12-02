import logging
import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings, reproduce_failure
from hypothesis.strategies import text, from_regex, composite, booleans, none

from PyRoute.AreaItems.Sector import Sector
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Position.Hex import Hex
from PyRoute.Star import Star
from PyRoute.SystemData.StarList import StarList
from PyRoute.SystemData.UWP import UWP
from PyRoute.TradeCodes import TradeCodes

@composite
def importance_starline(draw):
    keep_econ = draw(booleans())
    keep_imp = draw(booleans())
    if not keep_econ and not keep_imp:
        keep_social = True
    else:
        keep_social = draw(booleans())
    assume(keep_imp or keep_econ or keep_social)

    rawline = draw(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]\'+*?'))
    assume('???????-?' not in rawline)
    assume(160 > len(rawline))
    imp_match = r'\{ *[+-]?[0-6] ?\}'
    econ_match = r'\([0-9A-Z]{3}[+-]\d\)'
    soc_match = r'\[[0-9A-Z]{4}\]'

    if keep_econ:
        econs = re.search(econ_match, rawline)
        assume(econs is not None)

    if keep_social:
        socials = re.search(soc_match, rawline)
        assume(socials is not None)

    if keep_imp:
        imp = re.search(imp_match, rawline)
        assume(imp is not None)

    # if needed, patch up wonky hex position
    if rawline.startswith('0000'):
        rawline = '0101' + rawline[4:]
    elif rawline.startswith('00'):
        rawline = '01' + rawline[2:]

    return rawline

@composite
def canonical_check(draw):
    rawline = '1919 Khula                B575A77-E Hi In Pz Di(Khulans)      { 4 }  (D9G+4) [AE5E] BEf  N  A 510 10 ImDv M0 V'
    uwp_match = r'(\w\w\w\w\w\w\w-\w|\?\?\?\?\?\?\?-\?|[\w\?]{7,7}-[\w\?])'
    imp_match = r'\{ *[+-]?[0-6] ?\}'
    econ_match = r'\([0-9A-Z]{3}[+-]\d\)'
    soc_match = r'\[[0-9A-Z]{4}\]'

    uwp_draw = draw(from_regex(uwp_match))
    rawline = rawline.replace('B575A77-E', uwp_draw)
    imp_draw = draw(from_regex(imp_match))
    rawline = rawline.replace('{ 4 }', imp_draw)
    econ_draw = draw(from_regex(econ_match))
    rawline = rawline.replace('(D9G+4)', econ_draw)
    soc_draw = draw(from_regex(soc_match))
    rawline = rawline.replace('[AE5E]', soc_draw)

    return rawline


class testStar(unittest.TestCase):

    def setUp(self) -> None:
        logger = logging.getLogger('PyRoute.Star')
        logger.setLevel(logging.INFO)

    """
    Given a regex-matching string, parse_line_to_star should return either a valid Star object or None
    """
    @given(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)],
        deadline=timedelta(1000))  # suppress slow-data health check, too-much filtering
    @example('0101 000000000000000 00000O0-0 000000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0)  - - - 0 000   00')
    @example('0101 000000000000000 00000ź0-0 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0101 000000000000000 ?000000-0 000000000000000 {0} (000-0) [0000] - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   00')
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
    @example('0101 000000000000000 ???????-? (000000000000)00         - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   10 +')
    @example('0101 000000000000000 ???????-? 000000000000000       - - 0 000   00 0')
    @example('0101 000000000000000 ???????-? 000000000000000         -   001   000')
    @example('0101 000000000000000 ???????-? 000000000000000         -   000   A00')
    @example('0101 000000000000000 ???????-? 000000000000000         -   000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       - 000 0 ?00   00')
    @example('0101 000000000000000 0000000-0 000000000000000       0 0 0      000 000 000+')
    @example('0101 000000000000000 ???????-? {0}000000000000       - - 0 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0) [0000]   - a   000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       a -   000   00')
    @example('0101 000000000000000 ???????-? 00000000000+  0         - a 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000       c -   000   00')
    @example('0101 000000000000000 ???????-? 00000000+  0000         -   000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {  -0} -  -  c -   000   00')
    @example('0101 000000000000000 A0000y0-0 000000000000000       - - 0 000   0000D')
    @example('0110 000000000000000 ???????-? 000000000000000       H B A 000 0 00')
    @example('0110 000000000000000 ???????-? 000000000000000       e - A 000   00')
    @example('0101 000000000000000 0000000-0 0000000000000 B       - A A 000   00')
    @example('0101 000000000000000 0000000-0 [00000000000000 - -  [0000] - - A 000   00')
    @example('0110 000000000000000 ???????-? 0000000000 (000 - (000-0) [0000] - - A 000 0 00')
    @example('0101 000000000000000 0000000-0 000000000000000       BB A      A 000 0 00')
    @example('0101 000000000000000 ???????-? 0000000000000 0 0       B - A 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {-0} (000-0)     -    * A 000   00')
    @example('0101 000000000000000 ???????-? 000000000000000 {-0} (000-0) -  - - A 000   00')
    @example("0101 000000000000000  ?000000-0                 {3 }  (7TG-1) [2IBt]   EHEG  -    569 9 C5'")
    @example('0101 000000000000000 ???????-? 0000000000000 B       - - A 000   00')
    @example('0101 111111111111000 A000011-1  000000000000100 {0} (100-0) -  - - B 001   10')
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
        foo.baseCode = str(foo.baseCode).upper()
        self.assertTrue(foo.is_well_formed())
        old_skool = foo.oldskool

        line = foo.parse_to_line()

        nu_foo = Star.parse_line_into_star(line, sector, pop_code, ru_calc)
        self.assertIsNotNone(nu_foo, "Output line did not reparse.  " + hyp_line)
        self.assertEqual(foo, nu_foo, "Reparsed star not _eq_ to original parsed star.  " + hyp_line)
        self.assertEqual(str(foo.nobles), str(nu_foo.nobles), "Reparsed nobles not equal.  " + hyp_line)
        self.assertEqual(str(foo.baseCode), str(nu_foo.baseCode), "Reparsed base not equal.  " + hyp_line)
        self.assertEqual(str(foo.zone), str(nu_foo.zone), "Reparsed zone not equal.  " + hyp_line)

        nu_line = nu_foo.parse_to_line()
        self.assertEqual(line, nu_line, "Reparsed line not equal to original line.  " + hyp_line)
        new_skool = nu_foo.oldskool
        self.assertEqual(old_skool, new_skool, "Oldskool status should be invariant across reparsing.  " + hyp_line)

    @given(importance_starline())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)],
              deadline=timedelta(1000))  # suppress slow-data health check, too-much filtering
    @example('0101 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} -  [0000]         - 0 000   0000D')
    @example('0141 000000000000000 ???????-? 000000000000000 {0} (000-0) -  - - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0) -  - - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} -  [0000] -         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0 } (000-0) -         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} -  [0000] -         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 { 0} -  [0000]         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 { 0 } -  [0000]         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000 {0 {0} -  [0000] -         - 0 000   00+D')
    @example('0101 000000000000000 ???????-? 0000000000000 { {0} -  [0000] -         - 0 000   00+D')
    @example('0101 000000000000000 ???????-? 000000000000000 { 0 } -  [000a]         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0 } (a00-0) -         - 0 000   0000D')
    @example('0101 000000000000000 ???????-? 000000000000000 {0} (000-0)       -    - 0 000   0000A0')
    @example('0101 0000000000000-0 ???????-? 000000000000000 {0} - - - - 0 000   00')
    @example('0101 000000000000000 E000000-0 000000000000000 {0} (000-0) [0000] 0 0 0 000 0 00+D')
    @example('0101 000000000000000 ???????-? 0000000000000 0 {0} (000-0)       -    - 0 000   00')
    @example('0101 000000000000000 ?000000-0 0000000000000 B - (000-0)   [0000] - - A 000   00')
    @example('0101 000000000000000 ?000000-0 0000000000000 B {   0} (000-0) [0000] - - A 000 0 00')
    def test_star_line_extension_parsing(self, s):
        econ_match = r'[ ]\([0-9A-Za-z]{3}[+-]\d\)[ ]'
        soc_match = r'[ ]\[[0-9A-Za-z]{4}\][ ]'
        imp_match = r'\{ *[+-]?[0-6] ?\}'
        uwp_match = r' \w\w\w\w\w\w\w-\w|\?\?\?\?\?\?\?-\?|[\w\?]{7,7}-[\w\?]'
        keep_econ = False
        keep_social = False
        keep_imp = False
        # dig out if specific econ/cultural extensions were passed in
        econ_m = re.search(econ_match, s)
        soc_m = re.search(soc_match, s)
        imp_m = re.search(imp_match, s)
        uwp_m = re.findall(uwp_match, s)
        uwp_rumbled = 0 < len([match for match in uwp_m if '?' in match])
        if not uwp_rumbled:
            raw_uwp = uwp_m[0]
            if raw_uwp[1].isdigit():
                raw_uwp = ' X' + raw_uwp[2:]
                s = s.replace(uwp_m[0], raw_uwp)

        if econ_m:
            if '-' != econ_m[0].strip():
                keep_econ = True
        if soc_m:
            if '-' != soc_m[0].strip():
                keep_social = True
        if imp_m:
            keep_imp = True

        self.assertTrue(keep_econ or keep_social or keep_imp, "Must keep at least one of Ix and/or Ex and/or Cx")

        hyp_line = "Hypothesis input: " + s
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        assume(foo is not None)
        result, _ = foo.hex.is_well_formed()  # as we're interested in extensions, we assume hex is good
        assume(result is True)
        self.assertEqual(uwp_rumbled, foo.oldskool, hyp_line)

        if keep_econ:
            self.assertIsNotNone(foo.economics, "Ex required, not found.  " + hyp_line)
            upper_econ = foo.economics.upper()
            self.assertEqual(upper_econ, foo.economics, "Ex not capitalised.  " + hyp_line)

        if keep_social:
            self.assertIsNotNone(foo.social, "Cx required, not found.  " + hyp_line)
            upper_social = foo.social.upper()
            self.assertEqual(upper_social, foo.social, "Cx not capitalised.  " + hyp_line)

        if keep_imp:
            self.assertIsNotNone(foo.importance, "Ix required, not found.  " + hyp_line)

        foo.index = 0
        foo.allegiance_base = foo.alg_base_code
        self.assertTrue(foo.is_well_formed())

    @given(canonical_check())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(3000))
    @example('1919 Khula                ???????-? Hi In Pz Di(Khulans)      {0}  (000-0) [0000] BEf  N  A 510 10 ImDv M0 V')
    def test_star_canonicalise(self, s):
        hyp_line = "Hypothesis input: " + s
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        tradelogger = logging.getLogger('PyRoute.TradeCodes')
        logger = logging.getLogger('PyRoute.Star')
        logger.setLevel(logging.CRITICAL)
        tradelogger.setLevel(logging.CRITICAL)
        foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        logger.setLevel(logging.INFO)
        tradelogger.setLevel(logging.INFO)
        logger.manager.disable = 10
        self.assertTrue(logger.isEnabledFor(logging.INFO))
        assume(foo is not None)
        assume(foo.economics is not None)
        assume(foo.social is not None)

        foo.canonicalise()
        with self.assertLogs(logger) as cm:
            logger.info('Dummy log')
            foo.check_ex()
            foo.check_cx()

        self.assertEqual(
            ["INFO:PyRoute.Star:Dummy log"],
            cm.output,
            hyp_line
        )

    @given(from_regex(UWP.match, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'),
           from_regex(r'^\([0-9A-Za-z]{3}[+-]\d\)'),
           from_regex(r'^\[[0-9A-Za-z]{4}\]'),
           none())
    @example('?000000-0', '(000-0)', '[0000]', None)
    @example('?000000-0', '(000-0)0', '[0000]', 'Star Sample economics must be None or 7-char string')
    @example('?000000-0', '(000-0)', '[0000]0', 'Star Sample social must be None or 6-char string')
    @example('?000000-0', '000-0)', '[0000]', 'Star Sample economics must be None or 7-char string')
    @example('?000000-0', '(000-0)', '[000]', 'Star Sample social must be None or 6-char string')
    def test_check_economics_social_and_ru(self, uwp, ex, cx, well_formed_kaboom):
        assume('?' not in uwp)
        uwp_obj = None

        try:
            uwp_obj = UWP(uwp)
        except ValueError:
            pass
        assume(uwp_obj is not None)

        if well_formed_kaboom is None:
            ex = ex[0:7]
            cx = cx[0:6]

        foo = Star()
        foo.name = 'Sample'
        foo.sector = Sector('# Core', '# 0, 0')
        foo.hex = Hex(foo.sector, '0101')
        foo.alg_base_code = 'Na'
        foo.uwp = uwp_obj
        foo.tradeCode = TradeCodes('')
        foo.index = 0
        foo.allegiance_base = foo.alg_base_code
        foo.star_list_object = StarList('')
        foo.economics = ex
        foo.social = cx
        try:
            self.assertTrue(foo.is_well_formed())
        except AssertionError as e:
            if well_formed_kaboom is not None:
                self.assertEqual(well_formed_kaboom, str(e), "Unexpected well-formed check error")
                return
            else:
                raise e

        foo.calculate_importance()
        foo.check_ex()
        foo.check_cx()
        foo.calculate_ru('fixed')


if __name__ == '__main__':
    unittest.main()
