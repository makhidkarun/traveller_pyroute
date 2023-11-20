import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, from_regex

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
    def test_initial_parsing(self, uwp_line):
        uwp = UWP(uwp_line)

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


if __name__ == '__main__':
    unittest.main()