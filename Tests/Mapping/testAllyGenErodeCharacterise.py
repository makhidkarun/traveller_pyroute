import sys

from PyRoute.AllyGen import AllyGen
from PyRoute.Position.Hex import Hex
from Tests.Mapping.testAllyGenBase import TestAllyGenBase


class TestAllyGenErode(TestAllyGenBase):

    def testErodeBorderOddClientState(self):
        self.setupOneWorldCoreSector("0503", 0, "CsIm")
        self.borders.create_erode_border('separate')

        border_map = self.borders.allyMap
        borders = self.borders.borders

        # Hexes which collapse to non-aligned shouldn't have _any_ borders
        self.assertEqual({(4, 35): 'Na'}, border_map, "Unexpected border map value")
        self.assertEqual({}, borders, "Unexpected borders value")

    def testErodeBorderOddImperialWorld(self):
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        cand_hex = (4, 35)
        top_hex = (4, 36)
        bottom_hex = (4, 34)
        top_left_hex = Hex.get_neighbor(cand_hex, 3)
        top_right_hex = Hex.get_neighbor(cand_hex, 1)
        bottom_left_hex = Hex.get_neighbor(cand_hex, 4)
        bottom_right_hex = Hex.get_neighbor(cand_hex, 0)

        expected_borders = {
            cand_hex: 7, top_hex: Hex.BOTTOM, top_left_hex: Hex.BOTTOMRIGHT, top_right_hex: Hex.BOTTOMLEFT
        }
        expected_borders_map = {
            cand_hex: 3, top_hex: 5, bottom_right_hex: 2, top_right_hex: 4
        }

        self.assertEqual({(4, 35): 'ImDs'}, ally_map, "Unexpected ally map value")
        self.assertNotIn(bottom_hex, borders, "Hex below candidate hex should not be in border dict")
        self.assertNotIn(bottom_left_hex, borders, "Hex bottom-left of candidate hex should not be in border dict")
        self.assertNotIn(bottom_right_hex, borders, "Hex bottom-right of candidate hex should not be in border dict")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testErodeBorderTwoOddImperialWorlds(self):
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.setupOneWorldCoreSector("0504", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(4, 34): 'ImDs', (4, 35): 'ImDs'}
        expected_borders = {(3, 35): 2, (3, 36): 2, (4, 34): 7, (4, 35): 6, (4, 36): 1, (5, 34): 4, (5, 35): 4}
        expected_borders_map = {(4, 34): 3, (4, 35): 6, (4, 36): 5, (5, 33): 2, (5, 34): 6, (5, 35): 4}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testErodeBorderTwoEvenImperialWorlds(self):
        self.setupOneWorldCoreSector("0603", 0, "ImDs")
        self.setupOneWorldCoreSector("0604", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(5, 33): 'ImDs', (5, 34): 'ImDs'}
        expected_borders = {(4, 34): 2, (4, 35): 2, (5, 33): 7, (5, 34): 6, (5, 35): 1, (6, 33): 4, (6, 34): 4}
        expected_borders_map = {(5, 33): 7, (5, 34): 6, (5, 35): 1, (6, 33): 6, (6, 34): 6}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
