from collections import defaultdict

from PyRoute.Position.Hex import Hex
from Tests.Mapping.testAllyGenBase import TestAllyGenBase


class TestAllyGenAllyGenCharacterise(TestAllyGenBase):

    def testAllyGenBorderOddClientState(self):
        self.setupOneWorldCoreSector("0503", 0, "CsIm")
        self.borders.create_ally_map('separate')

        ally_map = self.borders.allyMap
        borders = self.borders.borders

        expected_ally_map = defaultdict(set)
        expected_ally_map[(3, 35)] = None
        expected_ally_map[(3, 36)] = None
        expected_ally_map[(4, 34)] = None
        expected_ally_map[(4, 35)] = 'Na'
        expected_ally_map[(4, 36)] = None
        expected_ally_map[(5, 34)] = None
        expected_ally_map[(5, 35)] = None

        expected_borders = {}

        # Hexes which collapse to non-aligned shouldn't have _any_ borders
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")

    def testAllyGenBorderOddImperialWorld(self):
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.borders.create_ally_map('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = defaultdict(set)
        expected_ally_map[(4, 35)] = 'ImDs'

        expected_borders = {
            (3, 36): 2, (4, 35): 7, (4, 36): 1, (5, 35): 4
        }
        expected_borders_map = {
            (4, 35): 3, (4, 36): 5, (5, 34): 2, (5, 35): 4
        }

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderTwoOddImperialWorlds(self):
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.setupOneWorldCoreSector("0504", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_ally_map('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = defaultdict(set)
        expected_ally_map[(4, 35)] = 'ImDs'
        expected_ally_map[(4, 34)] = 'ImDs'

        expected_borders = {
            (3, 35): 2, (3, 36): 2, (4, 34): 7, (4, 35): 6, (4, 36): 1, (5, 34): 4, (5, 35): 4
        }
        expected_borders_map = {
            (4, 34): 3, (4, 35): 6, (4, 36): 5, (5, 33): 2, (5, 34): 6, (5, 35): 4
        }
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderTwoEvenImperialWorlds(self):
        self.setupOneWorldCoreSector("0603", 0, "ImDs")
        self.setupOneWorldCoreSector("0604", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_ally_map('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = defaultdict(set)
        expected_ally_map[(5, 34)] = 'ImDs'
        expected_ally_map[(5, 33)] = 'ImDs'

        expected_borders = {
            (4, 34): 2, (4, 35): 2, (5, 33): 7, (5, 34): 6, (5, 35): 1, (6, 33): 4, (6, 34): 4
        }
        expected_borders_map = {
            (5, 33): 7, (5, 34): 6, (5, 35): 1, (6, 33): 6, (6, 34): 6
        }
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
