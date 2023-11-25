import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, none, composite, integers

from PyRoute.SystemData.StarList import StarList


@composite
def star_list(draw, max_stars=10, cleanup=False):
    num_stars = draw(integers(min_value=1, max_value=max_stars))
    starline = ''

    for i in range(num_stars):
        starchunk = draw(from_regex(StarList.stellar_match))
        if cleanup:
            if 1 < len(starchunk) and ' ' not in starchunk and 'DD' in starchunk:
                starchunk = starchunk.replace('DD', 'D ')
            elif 1 < len(starchunk) and ' ' not in starchunk and starchunk.endswith('D') and not starchunk.endswith('BD'):
                starchunk = starchunk[:-1]

            if 5 < len(starchunk):
                match = StarList.stellar_match.findall(starchunk)
                if match:
                    headroom = max_stars - i
                    match = match[:headroom]
                    extra_matches = len(match) - 1
                    i += extra_matches
                    starchunk = ' '.join(match)

        starline += starchunk + ' '

    if cleanup:  # if we've gotten this far, we then assume that there's at least one stellar match
        matches = StarList.stellar_match.findall(starline)
        assume(0 < len(matches))

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
    @example('A0Ia A0Ia D D D D D DD ')
    @example('A0Ia A0Ia D D D D D NSD ')
    @example('A0Ia D D D D D D DD0 ')
    @example('A0Ia A0IaD0 D D D D D D ')
    @example('A0Ia D D D D D NSD0D0 ')
    @example('A0Ia D D D D D 0NSD0D0 ')
    @example('0 ')
    def test_star_list_generation(self, star_line):
        hyp_line = "Hypothesis input: " + star_line
        allowed_value_errors = [
            "No stars found",
            "Max number of stars is 8",
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

    """
    Given an otherwise valid input string that needs canonicalisation, verify that canonicalisation does what it says
    on the tin, and that canonicalisation is itself idempotent
    """
    @given(star_list(max_stars=8, cleanup=True))
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)])  # suppress slow-data health check, too-much filtering
    @example('K9 Ib ')
    @example('D ')
    @example('A0 D ')
    @example('O6 VI')
    @example('A0Ia M0IV')
    @example('K5IV')
    @example('F0VI')
    @example('D A0Ia')
    @example('A0Ia A0Ia ')
    @example('A0Ia B0Ib ')
    @example('O0Ia O0Ia ')
    @example('O0Ia F0Ia ')
    @example('A0Ia G0Ia ')
    @example('A0Ia K0Ia ')
    @example('A0Ia K5Ia ')
    @example('O0Ib O0Ib ')
    @example('B0Ib B0Ib ')
    @example('A0Ib A0Ib ')
    def test_star_list_canonical(self, star_line):
        hyp_line = "Hypothesis input: " + star_line

        list = None
        try:
            list = StarList(star_line, trim_stars=True)
        except Exception:
            self.assertTrue(False, hyp_line)
        result, msg = list.check_canonical()
        assume(not result)
        list.move_biggest_to_primary()

        list.canonicalise()

        result, msg = list.check_canonical()
        badline = '' if result else msg[0]
        badline += '\n  ' + hyp_line
        self.assertTrue(result, "Canonicalisation failed. " + badline)

    def test_stargen_class_ordering(self):
        cases = [
            ('O6 VI', 'O6 VI'),
            ('O6 VII', 'O6 D'),
            ('A9 III', 'A9 III'),
            ('A9 IV', 'A9 IV'),
            ('M3 V', 'M3 V')
        ]

        for star_line, expected in cases:
            starlist = StarList(star_line)
            self.assertEqual(expected, str(starlist))
