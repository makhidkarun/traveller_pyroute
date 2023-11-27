import unittest
from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex

from PyRoute.Galaxy import Sector
from PyRoute.Star import Star


class testStar(unittest.TestCase):

    """
    Given a regex-matching string, parse_line_to_star should return either a valid Star object or None
    """
    @given(from_regex(regex=Star.starline, alphabet='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWYXZ -{}()[]?\'+*'))
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)])  # suppress slow-data health check, too-much filtering
    @example('0000 000000000000000 00000O0-0 000000000000000       - - 0 000   00')
    @example('0000 000000000000000 ???????-? 000000000000000 {0} (000-0)  - - - 0 000   00')
    @example('0000 000000000000000 00000ź0-0 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0000 000000000000000 ?000000-0 000000000000000 {0} (000-0) [0000] - - 0 000   00')
    @example('0100 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0150 000000000000000 ???????-? 000000000000000 {0} -  [0000] - - 0 000   00')
    @example('0101 000000000000000 ?000000-0 000000000000000 {0} (000-0) [0000] - - 0 000   00')
    @example('0101 000000000000000 ???????-? 0000000000000 0       - - 0 000   00')
    def test_parse_line_to_star(self, s):
        sector = Sector('# Core', '# 0, 0')
        pop_code = 'scaled'
        ru_calc = 'scaled'
        foo = Star.parse_line_into_star(s, sector, pop_code, ru_calc)
        assume(foo is not None)

        self.assertIsInstance(foo, Star)
        foo.index = 0
        foo.allegiance_base = foo.alg_base_code
        self.assertTrue(foo.is_well_formed())


if __name__ == '__main__':
    unittest.main()
