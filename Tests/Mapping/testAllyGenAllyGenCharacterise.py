from collections import defaultdict

from DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.Mapping.testAllyGenBase import TestAllyGenBase


class TestAllyGenAllyGenCharacterise(TestAllyGenBase):

    def testAllyGenBorderOddClientState(self) -> None:
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

    def testAllyGenBorderOddImperialWorld(self) -> None:
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.borders.create_ally_map('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = defaultdict(set)
        expected_ally_map[(4, 35)] = 'ImDs'

        expected_borders = {
            (4, 34): ['green', 'yellow', None], (4, 35): ['blue', None, 'purple'],
            (5, 33): [None, 'red', None], (5, 34): [None, None, 'olive']
        }
        expected_borders_map = {}

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderTwoOddImperialWorlds(self) -> None:
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
            (4, 33): ['green', 'yellow', None], (4, 34): [None, 'yellow', 'purple'], (4, 35): ['blue', None, 'purple'],
            (5, 32): [None, 'red', None], (5, 33): [None, 'red', 'olive'], (5, 34): [None, None, 'olive']
        }
        expected_borders_map = {}

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderTwoEvenImperialWorlds(self) -> None:
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
            (5, 32): ['green', 'orange', 'black'], (5, 33): [None, 'orange', 'black'], (5, 34): ['blue', None, None],
            (6, 32): [None, 'maroon', 'pink'], (6, 33): [None, 'maroon', 'pink']
        }
        expected_borders_map = {}

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderOnIbaraSubsector(self) -> None:
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
        expected_borders = {(-35, 5): ['white', 'white', 'white'], (-35, 6): [None, 'white', 'white'], (-35, 7): [None, 'white', 'white'],
                            (-35, 8): [None, 'white', 'white'], (-35, 9): [None, 'white', 'white'], (-35, 10): [None, 'white', 'white'],
                            (-35, 11): [None, 'white', 'white'], (-35, 12): [None, 'white', 'white'], (-35, 13): ['white', None, None],
                            (-34, 4): ['white', 'white', None], (-34, 13): [None, 'white', 'white'], (-34, 14): [None, 'white', 'white'],
                            (-34, 15): [None, 'white', 'white'], (-34, 16): [None, 'white', 'white'], (-34, 17): ['white', None, 'white'],
                            (-33, 3): [None, 'white', None], (-33, 4): ['white', None, None], (-33, 16): [None, 'white', None],
                            (-33, 17): ['white', None, None], (-32, 3): ['white', 'white', None], (-32, 17): ['white', None, 'white'],
                            (-31, 2): [None, 'white', None], (-31, 3): ['white', None, None], (-31, 16): [None, 'white', None],
                            (-31, 17): ['white', None, None], (-30, 2): ['white', 'white', None], (-30, 16): ['white', 'white', None],
                            (-29, 1): [None, 'white', None], (-29, 2): ['white', None, None], (-29, 15): [None, 'white', None],
                            (-29, 16): ['white', None, None], (-28, 2): ['white', None, 'white'], (-28, 15): ['white', 'white', None],
                            (-27, 1): [None, 'white', None], (-27, 2): ['white', None, None], (-27, 14): [None, 'white', None],
                            (-27, 15): ['white', None, None], (-26, 2): ['white', None, 'white'], (-26, 15): ['white', None, 'white'],
                            (-25, 1): [None, 'white', None], (-25, 2): ['white', None, None], (-25, 14): ['white', None, 'white'],
                            (-24, 2): ['white', None, 'white'], (-24, 13): ['white', 'white', None], (-23, 1): [None, 'white', None],
                            (-23, 2): ['white', None, None], (-23, 12): ['white', None, 'white'], (-22, 2): ['white', None, 'white'],
                            (-22, 10): ['white', 'white', None], (-22, 11): [None, 'white', 'white'], (-21, 1): [None, 'white', None],
                            (-21, 2): [None, 'white', 'white'], (-21, 3): [None, 'white', 'white'], (-21, 4): [None, 'white', 'white'],
                            (-21, 5): [None, 'white', 'white'], (-21, 6): [None, 'white', 'white'], (-21, 7): [None, 'white', 'white'],
                            (-21, 8): [None, 'white', 'white'], (-21, 9): [None, None, 'white']}
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderOnFarFrontiersSector(self) -> None:
        sourcefile = self.unpack_filename('BorderGeneration/Far Frontiers.sec')
        mapfile = self.unpack_filename('BorderGeneration/Far Frontiers-allymap-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Far Frontiers-allymap-border.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_ally_map('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        if expected_ally_map != ally_map:
            combo = dict(expected_ally_map.items() & ally_map.items())
            expected_ally_map = {key: expected_ally_map[key] for key in expected_ally_map if key not in combo}
            ally_map = {key: ally_map[key] for key in ally_map if key not in combo}
            self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        if expected_borders != borders:
            combo = dict(expected_borders.items() & borders.items())
            expected_borders = {key: expected_borders[key] for key in expected_borders if key not in combo}
            borders = {key: borders[key] for key in borders if key not in combo}
            self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderOnFarFrontiersPartialSector(self) -> None:
        sourcefile = self.unpack_filename('BorderGeneration/Far Frontiers - partial.sec')
        mapfile = self.unpack_filename('BorderGeneration/Far Frontiers-partial-allymap-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Far Frontiers-partial-allymap-border.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_ally_map('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        if expected_ally_map != ally_map:
            combo = dict(expected_ally_map.items() & ally_map.items())
            expected_ally_map = {key: expected_ally_map[key] for key in expected_ally_map if key not in combo}
            ally_map = {key: ally_map[key] for key in ally_map if key not in combo}
            self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        if expected_borders != borders:
            combo = dict(expected_borders.items() & borders.items())
            expected_borders = {key: expected_borders[key] for key in expected_borders if key not in combo}
            borders = {key: borders[key] for key in borders if key not in combo}
            self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testAllyGenBorderOnVanguardReachesSector(self) -> None:
        sourcefile = self.unpack_filename('BorderGeneration/Vanguard Reaches.sec')
        mapfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-allymap-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-allymap-border.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_ally_map('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        if expected_ally_map != ally_map:
            combo = dict(expected_ally_map.items() & ally_map.items())
            expected_ally_map = {key: expected_ally_map[key] for key in expected_ally_map if key not in combo}
            ally_map = {key: ally_map[key] for key in ally_map if key not in combo}
            self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        if expected_borders != borders:
            combo = dict(expected_borders.items() & borders.items())
            expected_borders = {key: expected_borders[key] for key in expected_borders if key not in combo}
            borders = {key: borders[key] for key in borders if key not in combo}
            self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
