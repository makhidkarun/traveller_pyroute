from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
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

    def testRangeBorderOnIbaraSubsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_borders('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(-34, 6): 'ImDi', (-34, 7): 'ImDi', (-34, 8): 'ImDi', (-34, 9): 'ImDi', (-34, 10): 'ImDi',
                             (-34, 11): 'ImDi', (-34, 12): 'ImDi', (-34, 15): 'ImDi', (-34, 16): 'ImDi',
                             (-34, 17): 'ImDi', (-33, 5): 'ImDi', (-33, 6): 'ImDi', (-33, 7): 'ImDi', (-33, 8): 'ImDi',
                             (-33, 9): 'ImDi', (-33, 10): 'ImDi', (-33, 11): 'ImDi', (-33, 12): 'ImDi',
                             (-33, 13): 'ImDi', (-33, 14): 'ImDi', (-33, 15): 'ImDi', (-33, 16): 'ImDi',
                             (-33, 17): 'ImDi', (-32, 4): 'ImDi', (-32, 5): 'ImDi', (-32, 6): 'ImDi', (-32, 7): 'ImDi',
                             (-32, 8): 'ImDi', (-32, 9): 'ImDi', (-32, 10): 'ImDi', (-32, 11): 'ImDi',
                             (-32, 12): 'ImDi', (-32, 13): 'ImDi', (-32, 14): 'ImDi',(-32, 15): 'ImDi',
                             (-32, 16): 'ImDi', (-32, 17): 'ImDi', (-31, 4): 'ImDi', (-31, 5): 'ImDi', (-31, 6): 'ImDi',
                             (-31, 7): 'ImDi', (-31, 8): 'ImDi', (-31, 9): 'ImDi', (-31, 10): 'ImDi', (-31, 11): 'ImDi',
                             (-31, 12): 'ImDi', (-31, 13): 'ImDi', (-31, 14): 'ImDi', (-31, 15): 'ImDi',
                             (-31, 16): 'ImDi', (-30, 3): 'ImDi', (-30, 4): 'ImDi', (-30, 5): 'ImDi', (-30, 6): 'ImDi',
                             (-30, 7): 'ImDi', (-30, 8): 'ImDi', (-30, 9): 'ImDi', (-30, 10): 'ImDi', (-30, 11): 'ImDi',
                             (-30, 12): 'ImDi', (-30, 13): 'ImDi', (-30, 14): 'ImDi', (-30, 15): 'ImDi',
                             (-29, 3): 'ImDi', (-29, 4): 'ImDi', (-29, 5): 'ImDi', (-29, 6): 'ImDi', (-29, 7): 'ImDi',
                             (-29, 8): 'ImDi', (-29, 9): 'ImDi', (-29, 10): 'ImDi', (-29, 11): 'ImDi',
                             (-29, 12): 'ImDi', (-29, 13): 'ImDi', (-29, 14): 'ImDi', (-28, 2): 'ImDi',
                             (-28, 3): 'ImDi', (-28, 4): 'ImDi', (-28, 5): 'ImDi', (-28, 6): 'ImDi', (-28, 7): 'ImDi',
                             (-28, 8): 'ImDi', (-28, 9): 'ImDi', (-28, 10): 'ImDi', (-28, 11): 'ImDi',
                             (-28, 12): 'ImDi', (-28, 13): 'ImDi', (-28, 14): 'ImDi', (-27, 2): 'ImDi',
                             (-27, 3): 'ImDi', (-27, 4): 'ImDi', (-27, 5): 'ImDi', (-27, 6): 'ImDi', (-27, 7): 'ImDi',
                             (-27, 8): 'ImDi', (-27, 9): 'ImDi', (-27, 10): 'ImDi', (-27, 11): 'ImDi',
                             (-27, 12): 'ImDi', (-27, 13): 'ImDi', (-27, 14): 'ImDi', (-26, 1): 'ImDi',
                             (-26, 2): 'ImDi', (-26, 3): 'ImDi', (-26, 4): 'ImDi', (-26, 5): 'ImDi', (-26, 6): 'ImDi',
                             (-26, 7): 'ImDi', (-26, 8): 'ImDi', (-26, 9): 'ImDi', (-26, 10): 'ImDi', (-26, 11): 'ImDi',
                             (-26, 12): 'ImDi', (-26, 13): 'ImDi', (-26, 14): 'ImDi', (-25, 1): 'ImDi',
                             (-25, 2): 'ImDi', (-25, 3): 'ImDi', (-25, 4): 'ImDi', (-25, 5): 'ImDi', (-25, 6): 'ImDi',
                             (-25, 7): 'ImDi', (-25, 8): 'ImDi', (-25, 9): 'ImDi', (-25, 10): 'ImDi', (-25, 11): 'ImDi',
                             (-25, 12): 'ImDi', (-25, 13): 'ImDi', (-24, 1): 'ImDi', (-24, 2): 'ImDi', (-24, 3): 'ImDi',
                             (-24, 4): 'ImDi', (-24, 5): 'ImDi', (-24, 6): 'ImDi', (-24, 7): 'ImDi', (-24, 8): 'ImDi',
                             (-24, 9): 'ImDi', (-24, 10): 'ImDi', (-24, 11): 'ImDi', (-24, 12): 'ImDi',
                             (-23, 4): 'ImDi', (-23, 5): 'ImDi', (-23, 6): 'ImDi', (-23, 7): 'ImDi', (-23, 8): 'ImDi',
                             (-23, 9): 'ImDi', (-23, 10): 'ImDi', (-23, 11): 'ImDi' }
        expected_borders = {(-35, 7): 2, (-35, 8): 2, (-35, 9): 2, (-35, 10): 2, (-35, 11): 2, (-35, 12): 2,
                            (-35, 13): 2, (-35, 16): 2, (-35, 17): 2, (-35, 18): 2, (-34, 6): 5, (-34, 7): 4,
                            (-34, 8): 4, (-34, 9): 4, (-34, 10): 4, (-34, 11): 4, (-34, 12): 4, (-34, 13): 3,
                            (-34, 14): 2, (-34, 15): 5, (-34, 16): 4, (-34, 17): 4, (-34, 18): 3, (-33, 5): 5,
                            (-33, 13): 4, (-33, 14): 4, (-33, 18): 3, (-32, 4): 7, (-32, 18): 1, (-31, 4): 1,
                            (-31, 17): 5, (-30, 3): 7, (-30, 16): 5, (-29, 3): 1, (-29, 15): 7, (-28, 2): 7,
                            (-28, 15): 3, (-27, 2): 1, (-27, 15): 3, (-26, 1): 7, (-26, 15): 1, (-25, 1): 3,
                            (-25, 14): 5, (-24, 1): 3, (-24, 2): 2, (-24, 3): 2, (-24, 4): 2, (-24, 13): 5, (-23, 1): 4,
                            (-23, 2): 4, (-23, 3): 4, (-23, 4): 3, (-23, 5): 2, (-23, 6): 2, (-23, 7): 2, (-23, 8): 2,
                            (-23, 9): 2, (-23, 10): 2, (-23, 11): 2, (-23, 12): 5, (-22, 4): 4, (-22, 5): 4,
                            (-22, 6): 4, (-22, 7): 4, (-22, 8): 4, (-22, 9): 4, (-22, 10): 4, (-22, 11): 4}
        expected_borders_map = {(-34, 6): 3, (-34, 7): 6, (-34, 8): 6, (-34, 9): 6, (-34, 10): 6, (-34, 11): 6,
                                (-34, 12): 6, (-34, 13): 5, (-34, 15): 3, (-34, 16): 6, (-34, 17): 6, (-34, 18): 5,
                                (-33, 5): 5, (-33, 12): 2, (-33, 13): 6, (-33, 14): 4, (-33, 17): 2, (-33, 18): 1,
                                (-32, 4): 3, (-32, 18): 5, (-31, 3): 2, (-31, 4): 1, (-31, 17): 5, (-30, 3): 3,
                                (-30, 16): 3, (-29, 2): 2, (-29, 3): 1, (-29, 15): 5, (-28, 2): 3, (-28, 15): 5,
                                (-27, 1): 2, (-27, 2): 1, (-27, 14): 2, (-27, 15): 1, (-26, 1): 3, (-26, 15): 5,
                                (-25, 0): 2, (-25, 1): 1, (-25, 14): 5, (-24, 1): 5, (-24, 13): 3, (-24, 13): 3,
                                (-23, 0): 2, (-23, 1): 6, (-23, 2): 6, (-23, 3): 6, (-23, 4): 1, (-23, 12): 5,
                                (-22, 4): 6, (-22, 5): 6, (-22, 6): 6, (-22, 7): 6, (-22, 8): 6, (-22, 9): 6,
                                (-22, 10): 6, (-22, 11): 6}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
