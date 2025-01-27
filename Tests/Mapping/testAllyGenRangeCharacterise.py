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
            (2, 34): ['green', 'yellow', None], (2, 35): [None, 'yellow', 'purple'], (2, 36): [None, 'yellow', 'purple'],
            (2, 37): ['blue', None, 'purple'], (3, 33): ['green', None, 'black'], (3, 36): [None, 'orange', None],
            (3, 37): ['blue', None, None], (4, 32): ['green', 'yellow', None], (4, 37): ['blue', None, 'purple'],
            (5, 31): [None, 'red', None], (5, 32): ['green', None, None], (5, 36): ['blue', None, 'olive'],
            (6, 32): ['green', None, 'pink'], (6, 35): ['blue', 'maroon', None], (7, 31): [None, 'red', None],
            (7, 32): [None, 'red', 'olive'], (7, 33): [None, 'red', 'olive'], (7, 34): [None, None, 'olive']
        }
        expected_borders_map = {}

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
            (2, 33): ['green', 'yellow', None], (2, 34): [None, 'yellow', 'purple'], (2, 35): [None, 'yellow', 'purple'],
            (2, 36): [None, 'yellow', 'purple'], (2, 37): ['blue', None, 'purple'], (3, 32): ['green', None, 'black'],
            (3, 36): [None, 'orange', None], (3, 37): ['blue', None, None], (4, 31): ['green', 'yellow', None],
            (4, 37): ['blue', None, 'purple'], (5, 30): [None, 'red', None], (5, 31): ['green', None, None],
            (5, 36): ['blue', None, 'olive'], (6, 31): ['green', None, 'pink'], (6, 35): ['blue', 'maroon', None],
            (7, 30): [None, 'red', None], (7, 31): [None, 'red', 'olive'], (7, 32): [None, 'red', 'olive'],
            (7, 33): [None, 'red', 'olive'], (7, 34): [None, None, 'olive'],
        }
        expected_borders_map = {}
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
            (3, 32): ['green', 'orange', 'black'], (3, 33): [None, 'orange', 'black'], (3, 34): [None, 'orange', 'black'],
            (3, 35): [None, 'orange', 'black'], (3, 36): ['blue', None, None], (4, 31): ['green', 'yellow', None],
            (4, 36): ['blue', None, 'purple'], (5, 30): ['green', None, 'black'], (5, 35): [None, 'orange', None],
            (5, 36): ['blue', None, None], (6, 30): ['green', None, 'pink'], (6, 35): ['blue', 'maroon', None],
            (7, 29): [None, 'red', None], (7, 30): ['green', None, None], (7, 34): ['blue', None, 'olive'],
            (8, 30): [None, 'maroon', 'pink'], (8, 31): [None, 'maroon', 'pink'], (8, 32): [None, 'maroon', 'pink'],
            (8, 33): [None, 'maroon', 'pink'],
        }
        expected_borders_map = {}
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
        expected_borders = {(-34, 5): ['white', 'white', None], (-34, 6): [None, 'white', 'white'], (-34, 7): [None, 'white', 'white'],
                            (-34, 8): [None, 'white', 'white'], (-34, 9): [None, 'white', 'white'], (-34, 10): [None, 'white', 'white'],
                            (-34, 11): [None, 'white', 'white'], (-34, 12): ['white', None, 'white'], (-34, 14): ['white', 'white', None],
                            (-34, 15): [None, 'white', 'white'], (-34, 16): [None, 'white', 'white'], (-34, 17): ['white', None, 'white'],
                            (-33, 4): ['white', None, 'white'], (-33, 11): [None, 'white', None], (-33, 12): [None, 'white', 'white'],
                            (-33, 13): [None, None, 'white'], (-33, 16): [None, 'white', None], (-33, 17): ['white', None, None],
                            (-32, 3): ['white', 'white', None], (-32, 17): ['white', None, 'white'], (-31, 2): [None, 'white', None],
                            (-31, 3): ['white', None, None], (-31, 16): ['white', None, 'white'], (-30, 2): ['white', 'white', None],
                            (-30, 15): ['white', 'white', None], (-29, 1): [None, 'white', None], (-29, 2): ['white', None, None],
                            (-29, 14): ['white', None, 'white'], (-28, 1): ['white', 'white', None], (-28, 14): ['white', None, 'white'],
                            (-27, 0): [None, 'white', None], (-27, 1): ['white', None, None], (-27, 13): [None, 'white', None],
                            (-27, 14): ['white', None, None], (-26, 0): ['white', 'white', None], (-26, 14): ['white', None, 'white'],
                            (-25, -1): [None, 'white', None], (-25, 0): ['white', None, None], (-25, 13): ['white', None, 'white'],
                            (-24, 0): ['white', None, 'white'], (-24, 12): ['white', 'white', None], (-23, -1): [None, 'white', None],
                            (-23, 0): [None, 'white', 'white'], (-23, 1): [None, 'white', 'white'], (-23, 2): [None, 'white', 'white'],
                            (-23, 3): ['white', None, None], (-23, 11): ['white', None, 'white'], (-22, 3): [None, 'white', 'white'],
                            (-22, 4): [None, 'white', 'white'], (-22, 5): [None, 'white', 'white'], (-22, 6): [None, 'white', 'white'],
                            (-22, 7): [None, 'white', 'white'], (-22, 8): [None, 'white', 'white'], (-22, 9): [None, 'white', 'white'],
                            (-22, 10): [None, 'white', 'white']}
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testRangeBorderOnFarFrontiersSector(self):
        sourcefile = self.unpack_filename('BorderGeneration/Far Frontiers.sec')
        mapfile = self.unpack_filename('BorderGeneration/Far Frontiers-range-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Far Frontiers-range-border.json')
        bordermapfile = self.unpack_filename('BorderGeneration/Far Frontiers-range-bordermap.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_borders('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testRangeBorderOnVanguardReachesSector(self):
        sourcefile = self.unpack_filename('BorderGeneration/Vanguard Reaches.sec')
        mapfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-range-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-range-border.json')
        bordermapfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-range-bordermap.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_borders('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
