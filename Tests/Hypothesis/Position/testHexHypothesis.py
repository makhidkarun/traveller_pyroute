import unittest

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import text, integers

from PyRoute.AreaItems.Sector import Sector
from PyRoute.Position.Hex import Hex


class testHexHypothesis(unittest.TestCase):

    """
    Given a hex co-ord pair, verify it converts cleanly to axial co-ordinates, and then back to the original hex co-ords
    """
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

    """
    Given a set of sector and within-sector co-ords, verify conversion to axial co-ords and that extracted sector
    co-ords match the original values
    """
    @given(integers(min_value=-10, max_value=10), integers(min_value=-10, max_value=10), integers(min_value=1, max_value=32), integers(min_value=1, max_value=40))
    @example(0, 0, 1, 1)
    @example(0, 0, 1, 40)
    @example(0, 0, 32, 1)
    @example(0, 0, 32, 40)
    @example(0, 0, 16, 20)
    @example(1, 0, 1, 1)
    def test_axial_to_sector_co_ords(self, sec_x, sec_y, x, y):
        hyp_line = "Hypothesis input: " + str(sec_x) + ", " + str(sec_y) + ', ' + str(x) + ', ' + str(y)
        sec_co_ords = '# ' + str(sec_x) + ', ' + str(sec_y)
        sector = Sector('# dummy', sec_co_ords)
        hex_co_ords = str(x).rjust(2, '0') + str(y).rjust(2, '0')
        cand_hex = Hex(sector, hex_co_ords)

        col, row = Hex.axial_to_sector(cand_hex.q, cand_hex.r)
        self.assertEqual(x, col, 'Col co-ord not unpacked.  ' + hyp_line)
        self.assertEqual(y, row, 'Row co-ord not unpacked.  ' + hyp_line)

        nu_hex_co_ords = str(col).rjust(2, '0') + str(row).rjust(2, '0')
        self.assertEqual(hex_co_ords, nu_hex_co_ords, "Position string did not round trip.  " + hyp_line)

    @given(integers(), integers(min_value=1, max_value=40))
    @example(0, 1)
    def test_dy_offset_and_reverse(self, sector_y, row):
        hyp_line = "Hypothesis input: " + str(sector_y) + ", " + str(row)
        dy_offset = Hex.dy_offset(row, sector_y)
        nu_row, nu_sector_y = Hex.dy_reverse(dy_offset)

        self.assertEqual(row, nu_row, "Row not round-tripped.  " + hyp_line)
        self.assertEqual(sector_y, nu_sector_y, "Sector_y not round-tripped.  " + hyp_line)

if __name__ == '__main__':
    unittest.main()
