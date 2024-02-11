import sys

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

        expected_borders = {(4, 34): 4, (4, 35): 3, (4, 36): 1, (5, 34): 2, (5, 35): 4}

        self.assertEqual({(4, 35): 'ImDs'}, border_map, "Unexpected border map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
