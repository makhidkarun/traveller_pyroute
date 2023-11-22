import unittest

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, integers

from PyRoute.Position.Hex import Hex


class testHexHypothesis(unittest.TestCase):

    @given(integers(), integers())
    @example(1, 0)
    def test_axial_to_hex_and_hex_to_axial_round_trip(self, row, col):
        hyp_line = "Hypothesis input: " + str(row) + ", " + str(col)
        (q, r) = Hex.hex_to_axial(row, col)

        (nu_row, nu_col) = Hex.axial_to_hex(q, r)
        self.assertEqual(row, nu_row, "Row co-ord did not round-trip.  " + hyp_line)
        self.assertEqual(col, nu_col, "Col co-ord did not round trip.  " + hyp_line)

        (nu_q, nu_r) = Hex.hex_to_axial(nu_row, nu_col)
        self.assertEqual(q, nu_q, "Q co-ord did not round-trip.  " + hyp_line)
        self.assertEqual(r, nu_r, "R co-ord did not round-trip.  " + hyp_line)


if __name__ == '__main__':
    unittest.main()
