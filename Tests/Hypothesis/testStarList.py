import unittest

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import from_regex, none, composite, integers

from PyRoute.SystemData.StarList import StarList


@composite
def star_list(draw, min_stars=1, max_stars=10, cleanup=False) -> composite:
    num_stars = draw(integers(min_value=min_stars, max_value=max_stars))
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
                    i += extra_matches  # noqa
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
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2), HealthCheck(10)])  # suppress slow-data health check, too-much filtering
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
    def test_star_list_generation(self, star_line) -> None:
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
    @given(star_list(max_stars=8, cleanup=True), none())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2), HealthCheck(10)])  # suppress slow-data health check, too-much filtering
    @example('K9 Ib ', 'K9 II')
    @example('D ', '')  # Examples with expected value of '' do not make it far enough to check their starline
    @example('A0 D ', 'A0 V')
    @example('O6 VI', 'O6 V')
    @example('A0Ia M0IV', 'A0 Ia M0 V')
    @example('K5IV', 'K5 V')
    @example('F0VI', 'F0 V')
    @example('D A0Ia', 'A0 Ia')
    @example('A0Ia A0Ia ', 'A0 Ia A0 III')
    @example('A0Ia B0Ib ', 'A0 Ia B0 III')
    @example('O0Ia O0Ia ', 'O0 Ia O0 II')
    @example('O0Ia F0Ia ', 'O0 Ia F0 IV')
    @example('A0Ia G0Ia ', 'A0 Ia G0 V')
    @example('A0Ia K0Ia ', 'A0 Ia K0 V')
    @example('A0Ia K5Ia ', 'A0 Ia K5 V')
    @example('O0Ib O0Ib ', 'O0 Ib O0 III')
    @example('B0Ib B0Ib ', 'B0 Ib B0 III')
    @example('A0Ib A0Ib ', 'A0 Ib A0 IV')
    @example('A0Ib F0Ib ', 'A0 Ib F0 V')
    @example('D A0Ib ', 'A0 Ib')
    @example('A0Ib G0Ib ', 'A0 Ib G0 V')
    @example('A0Ib K0Ib ', 'A0 Ib K0 V')
    @example('A0Ib K6Ib ', 'A0 Ib K6 V')
    @example('A0Ib M0Ib ', 'A0 Ib M0 V')
    @example('A0Ia BD ', '')
    @example('F0Ia BD ', 'F0 II BD')
    @example('F5Ia BD ', 'F5 II BD')
    @example('G0Ia BD ', 'G0 II BD')
    @example('K0Ia BD ', 'K0 II BD')
    @example('K5Ia BD ', 'K5 II BD')
    @example('B0III K5III', 'B0 III K5 V')
    @example('B0III K0III', 'B0 III K0 IV')
    @example('F0Ib K0Ia ', 'F0 II K0 V')
    @example('F0III K0Ia', 'K0 II F0 V')
    @example('BH \U0008082aNS NS BD K9 IV BH PSR BH\U0008299e\xa0 ', 'K9 V NS NS BD BH BH PSR BH')
    def test_star_list_canonical(self, star_line, expected) -> None:
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

        if expected is not None:
            self.assertEqual(expected, str(list), "Unexpected final starline.  " + hyp_line)

    def test_stargen_class_ordering(self) -> None:
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

    @given(star_list(max_stars=1))
    @settings(suppress_health_check=[HealthCheck(10)])
    @example('PSR ')
    @example('A0Ia ')
    @example('D')
    @example('NS ')
    @example('BH ')
    @example('O0Ia ')
    @example('B0Ia ')
    @example('BD ')
    @example('F0Ia ')
    @example('G0Ia ')
    @example('K0Ia ')
    @example('M0Ia ')
    def test_primary_flux_bounds(self, star_line) -> None:
        hyp_line = "Hypothesis input: " + star_line

        list = StarList(star_line)
        max_flux, min_flux = list.primary_flux_bounds
        if max_flux is None:
            self.assertIsNone(min_flux, "If max-flux is None, so must be min-flux.  " + hyp_line)
        else:
            self.assertIsNotNone(min_flux, "if max-flux is not None, so must be min-flux.  " + hyp_line)
            self.assertTrue(max_flux >= min_flux, "Min-flux cannot exceed max-flux.  " + hyp_line)

    @given(star_list(min_stars=2, max_stars=2, cleanup=True), none())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2), HealthCheck(10)]
              )  # suppress slow-data health check, too-much filtering
    @example('O0Ia O0Ia ', 'O0 Ia O0 II')
    @example('O0Ia B0Ia ', 'O0 Ia B0 II')
    @example('O0Ia A0Ia ', 'O0 Ia A0 II')
    @example('O0Ia F0Ia ', 'O0 Ia F0 IV')
    @example('O0Ia G0Ia ', 'O0 Ia G0 IV')
    @example('O0Ia K0Ia ', 'O0 Ia K0 IV')
    @example('O0Ia M0Ia ', 'O0 Ia M0 II')
    @example('D A0Ia ', None)
    @example('B0Ia B0Ia ', 'B0 Ia B0 II')
    @example('B0Ia A0Ia ', 'B0 Ia A0 II')
    @example('B0Ia F0Ia ', 'B0 Ia F0 IV')
    @example('B0Ia G0Ia ', 'B0 Ia G0 IV')
    @example('B0Ia K0Ia ', 'B0 Ia K0 IV')
    @example('B0Ia M0Ia ', 'B0 Ia M0 II')
    @example('A0Ia A0Ia ', 'A0 Ia A0 III')
    @example('A0Ia F0Ia ', 'A0 Ia F0 V')
    @example('A0Ia G0Ia ', 'A0 Ia G0 V')
    @example('A0Ia K0Ia ', 'A0 Ia K0 V')
    @example('A0Ia M0Ia ', 'A0 Ia M0 III')
    @example('F0Ia F0Ia ', 'F0 II F0 V')
    @example('F0Ia G0Ia ', 'F0 II G0 V')
    @example('F0Ia K0Ia ', 'F0 II K0 V')
    @example('F0Ia M0Ia ', 'F0 II M0 V')
    @example('G0Ia G0Ia ', 'G0 II G0 V')
    @example('G0Ia K0Ia ', 'G0 II K0 V')
    @example('G0Ia M0Ia ', 'G0 II M0 V')
    @example('K0Ia K0Ia ', 'K0 II K0 VI')
    @example('K0Ia M0Ia ', 'K0 II M0 VI')
    @example('M0Ia M0Ia ', 'M0 II M0 VI')
    @example('D BD', 'D BD')
    def test_check_star_size_against_primary(self, star_line, expected) -> None:
        hyp_line = "Hypothesis input: " + star_line

        list = StarList(star_line)
        assume(2 == len(list.stars_list))
        assume(list.stars_list[1].is_stellar_not_dwarf)
        list.move_biggest_to_primary()
        list.primary.canonicalise()

        msg = []
        list.check_star_size_against_primary(list.stars_list[1], msg)
        assume(1 == len(msg))

        list.fix_star_size_against_primary(list.stars_list[1])

        nu_msg = []
        list.check_star_size_against_primary(list.stars_list[1], msg)
        self.assertEqual(0, len(nu_msg), "Incorrect star-size messages should be cleared by fix")

        if expected is not None:
            self.assertEqual(expected, str(list), "Unexpected final starline.  " + hyp_line)

    def test_handle_missing_and_wonky_star_sizes(self) -> None:
        cases = [
            ('Wrenton 1901', 'G7 M4 V', 'G7 V M4 V'),
            ('Blaskon 2824', 'M5 IC', 'M5 IV'),
            ('Ricenden 0210', 'M2 M5 M8 V', 'M2 V M5 V M8 V'),
            ('Tail End Charlie 1803', 'G2 II G3 V M9 ', 'G2 II G3 V M9 V'),
            ('Woop Woop 1824', 'M5 CI', 'M5 VI'),
            ('Woop Woop 3240', 'M5 C', 'M5 V')
        ]

        for msg, starline, expected in cases:
            if expected is None:
                continue
            with self.subTest(msg):
                starlist = StarList(starline)
                str_rep = str(starlist)
                self.assertEqual(expected, str_rep, "Unexpected parsing repair")
