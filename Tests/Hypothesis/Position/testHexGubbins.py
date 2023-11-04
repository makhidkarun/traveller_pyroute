import copy
import logging
import re
import unittest
from datetime import timedelta

from hypothesis import given, assume, example, HealthCheck, settings
from hypothesis.strategies import composite, integers

from PyRoute.Position.Hex import Hex
from PyRoute.Galaxy import Sector

@composite
def star_pos(draw):
    col = draw(integers(min_value=1, max_value=32))
    row = draw(integers(min_value=1, max_value=40))
    posn = str(col).rjust(2, '0') + str(row).rjust(2, '0')

    return posn


class testHexGubbins(unittest.TestCase):
    def setUp(self):
        self.sectors = {0: Sector('# Core', '# 0, 0'),
                        1: Sector('# Lishun', '# 0, 1'),
                        2: Sector('# Dagudashaag', '# -1, 0'),
                        3: Sector('# Fornast', '# 1, 0'),
                        4: Sector('# Massilia', '# 0, -1')}

        self.coreSector = Sector('# Core', '# 0, 0')

    @given(star_pos(), integers(min_value=0, max_value=5), integers(min_value=1, max_value=200))
    def test_get_neighbour_round_trip(self, pos_string, direction, distance):
        start = Hex(self.coreSector, pos_string)
        start_pos = start.hex_position()
        neighbour = Hex.get_neighbor(start_pos, direction, distance)

        rev_direction = (direction + 3) % 6
        restart_pos = Hex.get_neighbor(neighbour, rev_direction, distance)

        self.assertEqual(start_pos, restart_pos, "Restart should be same hex as starting position")

    @given(integers(min_value=-200, max_value=200), integers(min_value=-200, max_value=200))
    @example(1, 0)
    @example(1, 1)
    @example(1, -1)
    @example(0, 0)
    @example(0, 1)
    @example(0, -1)
    @example(-1, 0)
    @example(-1, 1)
    @example(-1, -1)
    def test_hex_to_axial_round_trip(self, row, col):
        q, r = Hex.hex_to_axial(row, col)

        nu_row, nu_col = Hex.axial_to_hex(q, r)
        inputs = str((row, col))
        self.assertEqual(row, nu_row, "Row co-ordinate not round-tripped.  Hypothesis input: " + inputs)
        self.assertEqual(col, nu_col, "Column co-ordinate not round-tripped.  Hypothesis input: " + inputs)

    @given(star_pos(), integers(min_value=0, max_value=4), integers(min_value=0, max_value=4))
    @example('0101', 0, 0)
    @example('0101', 0, 1)
    def test_self_equality(self, pos_string, sector_choice, nu_choice):
        sector = self.choose_sector(sector_choice)
        self.assertIsNotNone(sector, "Source sector not picked")

        nu_sector = self.choose_sector(nu_choice)
        self.assertIsNotNone(nu_sector, "Nu sector not picked")

        cand_hex = Hex(sector, pos_string)
        nu_hex = Hex(nu_sector, pos_string)

        inputs = str((pos_string, sector_choice, nu_choice))

        if sector_choice == nu_choice:
            msg = str(sector) + " " + str(pos_string) + " not equal to self.\nHypothesis input: " + inputs
            self.assertEqual(cand_hex, nu_hex, msg)
        else:
            msg = "Hex with position " + str(pos_string) + " should not be equal in different sectors.\nHypothesis input: " + inputs
            self.assertNotEqual(cand_hex, nu_hex, msg)

    @given(star_pos(), integers(min_value=0, max_value=4))
    @example('0202', 0)
    @example('0101', 0)
    @example('0101', 1)
    def test_parse_from_axial_around_core(self, pos_string, sector_choice):
        sector = self.choose_sector(sector_choice)
        self.assertIsNotNone(sector, "Source sector not picked")

        cand_hex = Hex(sector, pos_string)

        nu_hex = Hex.parse_from_axial(cand_hex.q, cand_hex.r)
        self.assertIsNotNone(nu_hex)

        inputs = str((pos_string, sector_choice))

        self.assertEqual(cand_hex, nu_hex, str(cand_hex) + " vs " + str(nu_hex) + '\nHypothesis input:' + inputs)

    @given(star_pos(), integers(max_value=5, min_value=-5), integers(max_value=5, min_value=-5))
    @settings(max_examples=300)
    def test_parse_from_axial_beyond_core(self, pos_string, sector_x, sector_y):
        assume(1 < abs(sector_x) + abs(sector_y))
        sector = Sector('# dummy', '# ' + str(sector_x) + ", " + str(sector_y))

        cand_hex = Hex(sector, pos_string)

        nu_hex = Hex.parse_from_axial(cand_hex.q, cand_hex.r)
        self.assertIsNotNone(nu_hex)

        inputs = str((pos_string, sector_x, sector_y))

        self.assertEqual(cand_hex, nu_hex, str(cand_hex) + " vs " + str(nu_hex) + '\nHypothesis input:' + inputs)

    def choose_sector(self, sector_choice):
        return self.sectors[sector_choice]


if __name__ == '__main__':
    unittest.main()
