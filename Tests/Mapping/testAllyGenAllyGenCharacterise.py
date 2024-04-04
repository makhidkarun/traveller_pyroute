from collections import defaultdict

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
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

    def testAllyGenBorderOnIbaraSubsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_ally_map('separate', False)

        ally_map = dict(self.borders.allyMap)
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(-35, 6): 'ImDi', (-35, 7): 'ImDi', (-35, 8): 'ImDi', (-35, 9): 'ImDi', (-35, 10): 'ImDi',
                             (-35, 11): 'ImDi', (-35, 12): 'ImDi', (-35, 13): 'ImDi', (-34, 5): 'ImDi',
                             (-34, 6): 'ImDi', (-34, 7): 'ImDi', (-34, 8): 'ImDi', (-34, 9): 'ImDi', (-34, 10): 'ImDi',
                             (-34, 11): 'ImDi', (-34, 12): 'ImDi', (-34, 13): 'ImDi', (-34, 14): 'ImDi',
                             (-34, 15): 'ImDi', (-34, 16): 'ImDi', (-34, 17): 'ImDi', (-33, 4): None, (-33, 5): 'ImDi',
                             (-33, 6): 'ImDi', (-33, 7): 'ImDi', (-33, 8): 'ImDi', (-33, 9): 'ImDi', (-33, 10): 'ImDi',
                             (-33, 11): 'ImDi', (-33, 12): 'ImDi', (-33, 13): 'ImDi', (-33, 14): 'ImDi',
                             (-33, 15): 'ImDi', (-33, 16): 'ImDi', (-33, 17): 'ImDi', (-32, 3): None, (-32, 4): 'ImDi',
                             (-32, 5): 'ImDi', (-32, 6): 'ImDi',
                             (-32, 7): 'ImDi', (-32, 8): 'ImDi', (-32, 9): 'ImDi',
                             (-32, 10): 'ImDi', (-32, 11): 'ImDi', (-32, 12): 'ImDi', (-32, 13): 'ImDi',
                             (-32, 14): 'ImDi', (-32, 15): 'ImDi', (-32, 16): 'ImDi', (-32, 17): 'ImDi', (-31, 3): None,
                             (-31, 4): 'ImDi', (-31, 5): 'ImDi', (-31, 6): 'ImDi', (-31, 7): 'ImDi', (-31, 8): 'ImDi',
                             (-31, 9): 'ImDi', (-31, 10): 'ImDi', (-31, 11): 'ImDi', (-31, 12): 'ImDi',
                             (-31, 13): 'ImDi', (-31, 14): 'ImDi', (-31, 15): 'ImDi', (-31, 16): 'ImDi',
                             (-31, 17): 'ImDi', (-30, 2): None, (-30, 3): 'ImDi', (-30, 4): 'ImDi', (-30, 5): 'ImDi',
                             (-30, 6): 'ImDi', (-30, 7): 'ImDi', (-30, 8): 'ImDi', (-30, 9): 'ImDi', (-30, 10): 'ImDi',
                             (-30, 11): 'ImDi', (-30, 12): 'ImDi', (-30, 13): 'ImDi', (-30, 14): 'ImDi',
                             (-30, 15): 'ImDi', (-30, 16): 'ImDi', (-29, 2): None, (-29, 3): 'ImDi', (-29, 4): 'ImDi',
                             (-29, 5): 'ImDi', (-29, 6): 'ImDi', (-29, 7): 'ImDi', (-29, 8): 'ImDi', (-29, 9): 'ImDi',
                             (-29, 10): 'ImDi', (-29, 11): 'ImDi', (-29, 12): 'ImDi', (-29, 13): 'ImDi',
                             (-29, 14): 'ImDi', (-29, 15): 'ImDi', (-29, 16): 'ImDi', (-28, 1): None, (-28, 2): None,
                             (-28, 3): 'ImDi', (-28, 4): 'ImDi', (-28, 5): 'ImDi', (-28, 6): 'ImDi', (-28, 7): 'ImDi',
                             (-28, 8): 'ImDi', (-28, 9): 'ImDi', (-28, 10): 'ImDi', (-28, 11): 'ImDi',
                             (-28, 12): 'ImDi', (-28, 13): 'ImDi', (-28, 14): 'ImDi', (-28, 15): 'ImDi', (-27, 1): None,
                             (-27, 2): None, (-27, 3): 'ImDi', (-27, 4): 'ImDi', (-27, 5): 'ImDi', (-27, 6): 'ImDi',
                             (-27, 7): 'ImDi', (-27, 8): 'ImDi', (-27, 9): 'ImDi', (-27, 10): 'ImDi', (-27, 11): 'ImDi',
                             (-27, 12): 'ImDi', (-27, 13): 'ImDi', (-27, 14): 'ImDi', (-27, 15): 'ImDi', (-26, 1): None,
                             (-26, 2): None, (-26, 3): 'ImDi', (-26, 4): 'ImDi', (-26, 5): 'ImDi', (-26, 6): 'ImDi',
                             (-26, 7): 'ImDi', (-26, 8): 'ImDi', (-26, 9): 'ImDi', (-26, 10): 'ImDi', (-26, 11): 'ImDi',
                             (-26, 12): 'ImDi', (-26, 13): 'ImDi', (-26, 14): 'ImDi', (-26, 15): 'ImDi',
                             (-25, 1): None, (-25, 2): None, (-25, 3): 'ImDi', (-25, 4): 'ImDi', (-25, 5): 'ImDi',
                             (-25, 6): 'ImDi', (-25, 7): 'ImDi', (-25, 8): 'ImDi', (-25, 9): 'ImDi', (-25, 10): 'ImDi',
                             (-25, 11): 'ImDi', (-25, 12): 'ImDi', (-25, 13): 'ImDi', (-25, 14): 'ImDi', (-24, 2): None,
                             (-24, 3): 'ImDi', (-24, 4): 'ImDi', (-24, 5): 'ImDi', (-24, 6): 'ImDi', (-24, 7): 'ImDi',
                             (-24, 8): 'ImDi', (-24, 9): 'ImDi', (-24, 10): 'ImDi', (-24, 11): 'ImDi',
                             (-24, 12): 'ImDi', (-24, 13): 'ImDi', (-23, 2): None, (-23, 3): 'ImDi', (-23, 4): 'ImDi',
                             (-23, 5): 'ImDi', (-23, 6): 'ImDi', (-23, 7): 'ImDi', (-23, 8): 'ImDi', (-23, 9): 'ImDi',
                             (-23, 10): 'ImDi', (-23, 11): 'ImDi', (-23, 12): 'ImDi', (-22, 2): None, (-22, 3): 'ImDi',
                             (-22, 4): 'ImDi', (-22, 5): 'ImDi', (-22, 6): 'ImDi', (-22, 7): 'ImDi', (-22, 8): 'ImDi',
                             (-22, 9): 'ImDi', (-22, 10): 'ImDi', (-22, 11): None, (-21, 2): None, (-21, 3): None,
                             (-21, 4): None, (-21, 5): None, (-21, 6): None, (-21, 7): None, (-21, 8): None,
                             (-21, 9): None, (-21, 10): None}
        expected_borders = {(-36, 7): 2, (-36, 8): 2, (-36, 9): 2, (-36, 10): 2, (-36, 11): 2, (-36, 12): 2,
                            (-36, 13): 2, (-36, 14): 2, (-35, 6): 5, (-35, 7): 4, (-35, 8): 4, (-35, 9): 4,
                            (-35, 10): 4, (-35, 11): 4, (-35, 12): 4, (-35, 13): 4, (-35, 14): 3, (-35, 15): 2,
                            (-35, 16): 2, (-35, 17): 2, (-35, 18): 2, (-34, 5): 7, (-34, 14): 4, (-34, 15): 4,
                            (-34, 16): 4, (-34, 17): 4, (-34, 18): 3, (-33, 5): 1, (-33, 18): 3, (-32, 4): 7,
                            (-32, 18): 3, (-31, 4): 1, (-31, 18): 1, (-30, 3): 7, (-30, 17): 7, (-29, 3): 3,
                            (-29, 17): 1, (-28, 3): 3, (-28, 16): 7, (-27, 3): 3, (-27, 16): 3, (-26, 3): 3,
                            (-26, 16): 1, (-25, 3): 3, (-25, 15): 5, (-24, 3): 3, (-24, 14): 5, (-23, 3): 3,
                            (-23, 12): 2, (-23, 13): 5, (-22, 3): 3, (-22, 4): 2, (-22, 5): 2, (-22, 6): 2, (-22, 7): 2,
                            (-22, 8): 2, (-22, 9): 2, (-22, 10): 2, (-22, 11): 5, (-22, 12): 4, (-21, 3): 4,
                            (-21, 4): 4, (-21, 5): 4, (-21, 6): 4, (-21, 7): 4, (-21, 8): 4, (-21, 9): 4, (-21, 10): 4}
        expected_borders_map = {(-35, 6): 7, (-35, 7): 6, (-35, 8): 6, (-35, 9): 6, (-35, 10): 6, (-35, 11): 6,
                                (-35, 12): 6, (-35, 13): 6, (-35, 14): 1, (-34, 5): 3, (-34, 14): 6, (-34, 15): 6,
                                (-34, 16): 6, (-34, 17): 6, (-34, 18): 5, (-33, 4): 2, (-33, 5): 1, (-33, 17): 2,
                                (-33, 18): 1, (-32, 4): 3, (-32, 18): 5, (-31, 3): 2, (-31, 4): 1, (-31, 17): 2,
                                (-31, 18): 1, (-30, 3): 3, (-30, 17): 3, (-29, 2): 2, (-29, 3): 1, (-29, 16): 2,
                                (-29, 17): 1, (-28, 3): 5, (-28, 16): 3, (-27, 2): 2, (-27, 3): 1, (-27, 15): 2,
                                (-27, 16): 1, (-26, 3): 5, (-26, 16): 5, (-25, 2): 2, (-25, 3): 1, (-25, 15): 5,
                                (-24, 3): 5, (-24, 14): 3, (-23, 2): 2, (-23, 3): 1, (-23, 13): 5, (-22, 3): 5,
                                (-22, 11): 3, (-22, 12): 6, (-21, 2): 2, (-21, 3): 6, (-21, 4): 6, (-21, 5): 6,
                                (-21, 6): 6, (-21, 7): 6, (-21, 8): 6, (-21, 9): 6, (-21, 10): 4}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
