import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, none, composite, integers

from PyRoute.SystemData.StarList import StarList


@composite
def star_list(draw):
    num_stars = draw(integers(min_value=1, max_value=10))
    starline = ''

    for i in range(num_stars):
        starchunk = draw(from_regex(StarList.stellar_match))
        starline += starchunk + ' '

    return starline


class testStarList(unittest.TestCase):

    """
    Given an input string, either reject it cleanly, or parse it to a well-formed StarList object
    """
    @given(star_list())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)])  # suppress slow-data health check, too-much filtering
    @example('OD ')
    @example('D ')
    @example('G5 V A4 V')
    @example('D D D D D D D D D')
    @example('A0Ia ')
    @example('G7 V M6 D')
    @example('K6 V M4 D')
    @example('F8 V M1 D')
    @example('F5 V M1 D')
    @example('G3 V M3 D M0 D')
    @example('K0 V M7 D')
    @example('F8 V M9 D')
    @example('F9 V M4 D')
    @example('M2 V M6 D M9 D')
    @example('G2 V M5 D')
    @example('G2 V M2 D')
    @example('M9 V M4 D')
    @example('K1 V M7 D')
    @example('G1 V M3 D')
    @example('F4 V M7 D')
    @example('F3 V M1 D')
    @example('F9 V M7 D')
    @example('F7 V M0 D M2 D')
    @example('F7 V M3 D M0 D')
    def test_star_list_generation(self, star_line):
        hyp_line = "Hypothesis input: " + star_line
        allowed_value_errors = [
            "No stars found",
            "Max number of stars is 8"
        ]
        list = None

        try:
            list = StarList(star_line)
        except ValueError as e:
            if str(e) in allowed_value_errors:
                pass
            else:
                raise e
        assume(isinstance(list, StarList))

        list.move_biggest_to_primary()

        result, msg = list.is_well_formed()
        self.assertTrue(result, msg + '.  ' + hyp_line)
