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
    def test_star_list_generation(self, star_line):
        hyp_line = "Hypothesis input: " + star_line
        allowed_value_errors = [
            "No stars found"
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

        result, msg = list.is_well_formed()
        self.assertTrue(result, msg + '.  ' + hyp_line)
