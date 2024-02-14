from PyRoute.Position.Hex import Hex
from Tests.Mapping.testAllyGenBase import TestAllyGenBase


class TestAllyGenRangeCharacterise(TestAllyGenBase):

    def testRangeBorderOddClientState(self):
        self.setupOneWorldCoreSector("0503", 0, "CsIm")
        self.borders.create_borders('separate')

        ally_map = self.borders.allyMap
        borders = self.borders.borders

        expected_ally_map = {(2, 35): 'Na', (2, 36): 'Na', (2, 37): 'Na', (3, 34): 'Na', (3, 35): 'Na', (3, 36): 'Na',
 (3, 37): 'Na', (4, 33): 'Na', (4, 34): 'Na', (4, 35): 'Na', (4, 36): 'Na', (4, 37): 'Na', (5, 33): 'Na', (5, 34): 'Na',
 (5, 35): 'Na', (5, 36): 'Na', (6, 33): 'Na', (6, 34): 'Na', (6, 35): 'Na'}
        expected_borders = {}

        # Hexes which collapse to non-aligned shouldn't have _any_ borders
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")

    def testRangeBorderOddImperialWorld(self):
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.borders.create_borders('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {
            (2, 35): 'ImDs', (2, 36): 'ImDs', (2, 37): 'ImDs', (3, 34): 'ImDs',
            (3, 35): 'ImDs', (3, 36): 'ImDs', (3, 37): 'ImDs', (4, 33): 'ImDs',
            (4, 34): 'ImDs', (4, 35): 'ImDs', (4, 36): 'ImDs', (4, 37): 'ImDs',
            (5, 33): 'ImDs', (5, 34): 'ImDs', (5, 35): 'ImDs', (5, 36): 'ImDs',
            (6, 33): 'ImDs', (6, 34): 'ImDs', (6, 35): 'ImDs'
        }

        expected_borders = {
            (1, 36): 2, (1, 37): 2, (1, 38): 2, (2, 35): 5,
            (2, 36): 4, (2, 37): 4, (2, 38): 3, (3, 34): 5,
            (3, 38): 3, (4, 33): 7, (4, 38): 1, (5, 33): 3,
            (5, 37): 5, (6, 33): 3, (6, 34): 2, (6, 35): 2,
            (6, 36): 5, (7, 33): 4, (7, 34): 4, (7, 35): 4
        }
        expected_borders_map = {
            (2, 35): 3, (2, 36): 6, (2, 37): 6, (2, 38): 5,
            (3, 34): 5, (3, 37): 2, (3, 38): 1, (4, 33): 3,
            (4, 38): 5, (5, 32): 2, (5, 33): 1, (5, 37): 5,
            (6, 33): 5, (6, 36): 3, (7, 32): 2, (7, 33): 6,
            (7, 34): 6, (7, 35): 4
        }

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testRangeBorderTwoOddImperialWorlds(self):
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.setupOneWorldCoreSector("0504", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_borders('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {
            (2, 34): 'ImDs', (2, 35): 'ImDs', (2, 36): 'ImDs', (2, 37): 'ImDs',
            (3, 33): 'ImDs', (3, 34): 'ImDs', (3, 35): 'ImDs', (3, 36): 'ImDs',
            (3, 37): 'ImDs', (4, 32): 'ImDs', (4, 33): 'ImDs', (4, 34): 'ImDs',
            (4, 35): 'ImDs', (4, 36): 'ImDs', (4, 37): 'ImDs', (5, 32): 'ImDs',
            (5, 33): 'ImDs', (5, 34): 'ImDs', (5, 35): 'ImDs', (5, 36): 'ImDs',
            (6, 32): 'ImDs', (6, 33): 'ImDs', (6, 34): 'ImDs', (6, 35): 'ImDs'}
        expected_borders = {
            (1, 35): 2, (1, 36): 2, (1, 37): 2, (1, 38): 2, (2, 34): 5, (2, 35): 4, (2, 36): 4, (2, 37): 4,
            (2, 38): 3, (3, 33): 5, (3, 38): 3, (4, 32): 7, (4, 38): 1, (5, 32): 3, (5, 37): 5, (6, 32): 3,
            (6, 33): 2, (6, 34): 2, (6, 35): 2, (6, 36): 5, (7, 32): 4, (7, 33): 4, (7, 34): 4, (7, 35): 4
        }
        expected_borders_map = {
            (2, 34): 3, (2, 35): 6, (2, 36): 6, (2, 37): 6, (2, 38): 5, (3, 33): 5, (3, 37): 2, (3, 38): 1,
            (4, 32): 3, (4, 38): 5, (5, 31): 2, (5, 32): 1, (5, 37): 5, (6, 32): 5, (6, 36): 3, (7, 31): 2,
            (7, 32): 6, (7, 33): 6, (7, 34): 6, (7, 35): 4
        }
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testRangeBorderTwoEvenImperialWorlds(self):
        self.setupOneWorldCoreSector("0603", 0, "ImDs")
        self.setupOneWorldCoreSector("0604", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_borders('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {
            (3, 33): 'ImDs', (3, 34): 'ImDs', (3, 35): 'ImDs', (3, 36): 'ImDs',
            (4, 32): 'ImDs', (4, 33): 'ImDs', (4, 34): 'ImDs', (4, 35): 'ImDs',
            (4, 36): 'ImDs', (5, 31): 'ImDs', (5, 32): 'ImDs', (5, 33): 'ImDs',
            (5, 34): 'ImDs', (5, 35): 'ImDs', (5, 36): 'ImDs', (6, 31): 'ImDs',
            (6, 32): 'ImDs', (6, 33): 'ImDs', (6, 34): 'ImDs', (6, 35): 'ImDs',
            (7, 31): 'ImDs', (7, 32): 'ImDs', (7, 33): 'ImDs', (7, 34): 'ImDs'
        }
        expected_borders = {
            (2, 34): 2, (2, 35): 2, (2, 36): 2, (2, 37): 2, (3, 33): 5, (3, 34): 4, (3, 35): 4, (3, 36): 4,
            (3, 37): 3, (4, 32): 5, (4, 37): 3, (5, 31): 7, (5, 37): 1, (6, 31): 3, (6, 36): 5, (7, 31): 3,
            (7, 32): 2, (7, 33): 2, (7, 34): 2, (7, 35): 5, (8, 31): 4, (8, 32): 4, (8, 33): 4, (8, 34): 4
        }
        expected_borders_map = {
            (3, 33): 7, (3, 34): 6, (3, 35): 6, (3, 36): 6, (3, 37): 1, (4, 32): 3, (4, 37): 5, (5, 31): 5,
            (5, 36): 2, (5, 37): 1, (6, 31): 5, (6, 36): 3, (7, 30): 2, (7, 31): 1, (7, 35): 5, (8, 31): 6,
            (8, 32): 6, (8, 33): 6, (8, 34): 6
        }
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
