import unittest

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, integers

from PyRoute.Galaxy import Sector
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

    @given(integers(min_value=-10, max_value=10), integers(min_value=-10, max_value=10), integers(min_value=1, max_value=32), integers(min_value=1, max_value=40))
    @example(0, 0, 1, 1)
    def test_axial_to_sector_co_ords(self, sec_x, sec_y, x, y):
        hyp_line = "Hypothesis input: " + str(sec_x) + ", " + str(sec_y) + ', ' + str(x) + ', ' + str(y)
        sec_co_ords = '# ' + str(sec_x) + ', ' + str(sec_y)
        sector = Sector('# dummy', sec_co_ords)
        hex_co_ords = str(x).rjust(2, '0') + str(y).rjust(2, '0')
        hex = Hex(sector, hex_co_ords)

        row, col = Hex.axial_to_sector(hex.q, hex.r)
        self.assertEqual(y, col, 'Col co-ord not unpacked.  ' + hyp_line)
        self.assertEqual(x, row, 'Row co-ord not unpacked.  ' + hyp_line)


if __name__ == '__main__':
    unittest.main()
