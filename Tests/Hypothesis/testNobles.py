import unittest

from hypothesis import given, assume
from hypothesis.strategies import text

from PyRoute.Nobles import Nobles


class testNobles(unittest.TestCase):

    @given(text(min_size=1, max_size=20, alphabet='ABcCDEfFGHI'))
    def test_nobles_creation(self, noble_line) -> None:
        hyp_line = "Hypothesis input: " + noble_line
        foo = Nobles()
        foo.count(noble_line)

        result, msg = foo.is_well_formed()
        self.assertTrue(result, msg + '.  ' + hyp_line)

    @given(text(min_size=1, max_size=6, alphabet='ABcCDEfFGHI'))
    def test_nobles_str_round_trip(self, noble_line) -> None:
        hyp_line = "Hypothesis input: " + noble_line
        foo = Nobles()
        foo.count(noble_line)
        assume(0 < foo.sum_value)

        str_rep = str(foo)

        nu_foo = Nobles()
        nu_foo.count(str_rep)

        nu_rep = str(nu_foo)
        self.assertEqual(str_rep, nu_rep, hyp_line)
