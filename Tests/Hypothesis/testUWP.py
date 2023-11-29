import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex, none

from PyRoute.SystemData.UWP import UWP


class testUWP(unittest.TestCase):

    """
    Given an otherwise valid input string, ensure the resulting UWP's string representation has no lowercase elements
    """
    @given(from_regex(UWP.match))
    @example('?000000-0')
    @example('?000000-00')
    @example('?000000-a')
    @example('a000000-0')
    @example('?a00000-0')
    @example('?0a0000-0')
    @example('?00a000-0')
    @example('?000a00-0')
    @example('?0000a0-0')
    @example('?00000a-0')
    @example('?000000-a')
    @example('?0000Y0-0')
    def test_initial_parsing(self, uwp_line):
        uwp = self.parse_uwp(uwp_line)

        assume(uwp is not None)

        result, msg = uwp.is_well_formed()
        hyp_input = 'Hypothesis input: ' + uwp_line
        self.assertTrue(result, msg + '.  ' + hyp_input)

        # Check UWP gubbins got dealt out
        self.assertEqual(uwp_line[0].upper(), uwp.port, hyp_input)
        self.assertEqual(uwp_line[1].upper(), uwp.size, hyp_input)
        self.assertEqual(uwp_line[2].upper(), uwp.atmo, hyp_input)
        self.assertEqual(uwp_line[3].upper(), uwp.hydro, hyp_input)
        self.assertEqual(uwp_line[4].upper(), uwp.pop, hyp_input)
        self.assertEqual(uwp_line[5].upper(), uwp.gov, hyp_input)
        self.assertEqual(uwp_line[6].upper(), uwp.law, hyp_input)
        self.assertEqual(uwp_line[8].upper(), uwp.tl, hyp_input)

    """
    Given an otherwise valid input string that needs canonicalisation, verify that canonicalisation does what it says
    on the tin, and that canonicalisation is itself idempotent
    """
    @given(from_regex(UWP.match), none())
    @settings(suppress_health_check=[HealthCheck(3), HealthCheck(2)])  # suppress slow-data health check, too-much filtering
    @example('?010000-0', '?000000-5')
    @example('?001000-0', '?000000-5')
    @example('?101000-0', '?100000-5')
    @example('??01000-0', '??01000-3')
    @example('?600000-0', '?610000-3')
    @example('?160000-0', '?160000-4')
    @example('?006000-0', '?000000-5')
    @example('?B00000-0', '?B61000-2')
    @example('?170000-0', '?160000-4')
    @example('?000060-0', '?000050-4')
    @example('?0005X0-0', '?0005X0-6')
    @example('?000F00-0', '?000FA5-8')
    @example('?000?x0-0', '?000?X0-5')
    @example('?0006X0-0', '?0006X0-5')  # Not sure exactly what to do with this one - Lintsec likes treating gov X as gov 0
    @example('?000F00-0', '?000FA5-8')
    @example('?0000G0-0', '?000050-4')
    @example('?000?F0-0', '?000?FA-4')
    @example('?000?Q0-0', '?000?FA-4')
    @example('?0000y0-0', None)
    @example('?0000Y0-0', None)
    @example('?40?6F0-0', '?40?6B6-3')
    def test_check_canonicalisation_and_verify_canonicalisation(self, uwp_line, expected):
        uwp = self.parse_uwp(uwp_line)
        assume(uwp is not None)

        old_rep = str(uwp)
        hyp_input = 'Hypothesis input: ' + uwp_line

        result, msg = uwp.check_canonical()
        assume(not result)  # ONLY care about UWP lines that _need_ canonicalisation - if they're (by chance) canonical, move on

        uwp.canonicalise()
        mid_rep = str(uwp)
        result, msg = uwp.check_canonical()
        badline = '' if result else msg[0]
        badline += '\n  ' + hyp_input
        self.assertTrue(result, 'Canonicalisation failed.  ' + badline)
        self.assertNotEqual(old_rep, mid_rep, "String rep unchanged despite requiring and receiving canonicalisation.")

        # verify canonicalisation is idempotent
        uwp.canonicalise()
        new_rep = str(uwp)
        result, msg = uwp.check_canonical()
        badline = '' if result else msg[0]
        badline += '\n  ' + hyp_input
        self.assertTrue(result, 'Re-canonicalisation failed.  ' + badline)
        self.assertEqual(mid_rep, new_rep, "Canonicalisation not idempotent.  " + badline)

        # finally, if an expected value was supplied, check it
        if expected is not None:
            self.assertEqual(expected, new_rep)

    def parse_uwp(self, uwp_line):
        allowed = [
            'Input UWP malformed'
        ]
        uwp = None
        try:
            uwp = UWP(uwp_line)
        except ValueError as e:
            msg = str(e)
            unexplained = True

            for line in allowed:
                if line in msg:
                    unexplained = False
                    break

            if unexplained:
                raise e
        return uwp


if __name__ == '__main__':
    unittest.main()
