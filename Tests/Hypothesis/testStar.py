import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, composite, booleans

from PyRoute.Galaxy import Sector
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from PyRoute.Star import Star

@composite
def importance_starline(draw):
    keep_econ = draw(booleans())
    keep_imp = draw(booleans())
    if not keep_econ and not keep_imp:
        keep_social = True
    else:
        keep_social = draw(booleans())
    assume(keep_imp or keep_econ or keep_social)

    rawline = draw(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
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

class testStar(unittest.TestCase):

    """
    Given a regex-matching string, parse_line_to_star should return either a valid Star object or None
    """
    @given(from_regex(regex=ParseStarInput.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)], deadline=timedelta(1000))  # suppress slow-data health check, too-much filtering
    @example('0000 000000000000000 00000O0-0 000000000000000       - - 0 000   00')
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0)  - - - 0 000   00')
    @example('0000 000000000000000 00000ź0-0 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0000 000000000000000 ?000000-0 000000000000000 {0} (000-0) [0000] - - 0 000   00')
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
    @example('0101 000000000000000 ???????-? 000000000000000 {  -0} -  -  c -   000   00')
    @example('0101 000000000000000 A0000y0-0 000000000000000       - - 0 000   0000D')
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

        line = foo.parse_to_line()

        nu_foo = Star.parse_line_into_star(line, sector, pop_code, ru_calc)
        self.assertIsNotNone(nu_foo, "Output line did not reparse.  " + hyp_line)
        self.assertEqual(foo, nu_foo, "Reparsed star not _eq_ to original parsed star.  " + hyp_line)
        self.assertEqual(str(foo.nobles), str(nu_foo.nobles), "Reparsed nobles not equal.  " + hyp_line)
        self.assertEqual(str(foo.baseCode), str(nu_foo.baseCode), "Reparsed base not equal.  " + hyp_line)
        self.assertEqual(str(foo.zone), str(nu_foo.zone), "Reparsed zone not equal.  " + hyp_line)

        nu_line = nu_foo.parse_to_line()
        self.assertEqual(line, nu_line, "Reparsed line not equal to original line.  " + hyp_line)

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
    def test_star_line_extension_parsing(self, s):
        econ_match = r'\([0-9A-Z]{3}[+-]\d\)'
        soc_match = r'\[[0-9A-Z]{4}\]'
        imp_match = r'\{ *[+-]?[0-6] ?\}'
        keep_econ = False
        keep_social = False
        keep_imp = False
        # dig out if specific econ/cultural extensions were passed in
        econ_m = re.search(econ_match, s)
        soc_m = re.search(soc_match, s)
        imp_m = re.search(imp_match, s)
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

        if keep_econ:
            self.assertIsNotNone(foo.economics, "Ex required, not found.  " + hyp_line)

        if keep_social:
            self.assertIsNotNone(foo.social, "Cx required, not found.  " + hyp_line)

        if keep_imp:
            self.assertIsNotNone(foo.importance, "Ix required, not found.  " + hyp_line)

        foo.index = 0
        foo.allegiance_base = foo.alg_base_code
        self.assertTrue(foo.is_well_formed())

if __name__ == '__main__':
    unittest.main()
