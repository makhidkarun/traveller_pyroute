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

    def choose_sector(self, sector_choice):
        return self.sectors[sector_choice]


if __name__ == '__main__':
    unittest.main()
