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
        self.borders.create_erode_border('separate')

        border_map = self.borders.allyMap
        borders = self.borders.borders

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

        self.assertEqual({(4, 35): 'ImDs'}, border_map, "Unexpected border map value")
        self.assertNotIn(bottom_hex, borders, "Hex below candidate hex should not be in border dict")
        self.assertNotIn(bottom_left_hex, borders, "Hex bottom-left of candidate hex should not be in border dict")
        self.assertNotIn(bottom_right_hex, borders, "Hex bottom-right of candidate hex should not be in border dict")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
