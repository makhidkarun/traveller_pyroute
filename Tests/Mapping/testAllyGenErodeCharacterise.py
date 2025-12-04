from unittest.mock import patch

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.Mapping.testAllyGenBase import TestAllyGenBase


class TestAllyGenErodeCharacterise(TestAllyGenBase):

    def testErodeBorderOddClientState(self) -> None:
        self.setupOneWorldCoreSector("0503", 0, "CsIm")

        with patch.object(self.borders, 'is_well_formed', return_value=(True, '')) as mock_method:
            self.borders.create_erode_border('separate')
            mock_method.assert_called_once()

        border_map = self.borders.allyMap
        borders = self.borders.borders

        # Hexes which collapse to non-aligned shouldn't have _any_ borders
        self.assertEqual({(4, 35): 'Na'}, border_map, "Unexpected border map value")
        self.assertEqual({}, borders, "Unexpected borders value")

    def testErodeBorderOddImperialWorld(self) -> None:
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_borders = {
            (4, 34): ['green', 'yellow', None], (4, 35): ['blue', None, 'purple'], (5, 33): [None, 'red', None],
            (5, 34): [None, None, 'olive']
        }
        expected_borders_map = {}

        self.assertEqual({(4, 35): 'ImDs'}, ally_map, "Unexpected ally map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderTwoOddImperialWorlds(self) -> None:
        self.setupOneWorldCoreSector("0503", 0, "ImDs")
        self.setupOneWorldCoreSector("0504", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(4, 34): 'ImDs', (4, 35): 'ImDs'}
        expected_borders = {
            (4, 33): ['green', 'yellow', None], (4, 34): [None, 'yellow', 'purple'], (4, 35): ['blue', None, 'purple'],
            (5, 32): [None, 'red', None], (5, 33): [None, 'red', 'olive'], (5, 34): [None, None, 'olive']
        }
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderTwoEvenImperialWorlds(self) -> None:
        self.setupOneWorldCoreSector("0603", 0, "ImDs")
        self.setupOneWorldCoreSector("0604", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(5, 33): 'ImDs', (5, 34): 'ImDs'}
        expected_borders = {
            (5, 32): ['green', 'orange', 'black'], (5, 33): [None, 'orange', 'black'], (5, 34): ['blue', None, None],
            (6, 32): [None, 'maroon', 'pink'], (6, 33): [None, 'maroon', 'pink']
        }
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderTwoEvenImperialWorldsCollapse(self) -> None:
        self.setupOneWorldCoreSector("0603", 0, "ImDs")
        self.setupOneWorldCoreSector("0604", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_erode_border('collapse', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(5, 33): 'Im', (5, 34): 'Im'}
        expected_borders = {
            (5, 32): ['green', 'orange', 'black'], (5, 33): [None, 'orange', 'black'], (5, 34): ['blue', None, None],
            (6, 32): [None, 'maroon', 'pink'], (6, 33): [None, 'maroon', 'pink']
        }
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderTwoEvenImperialWorldsOneHexApart(self) -> None:
        self.setupOneWorldCoreSector("0603", 0, "ImDs")
        self.setupOneWorldCoreSector("0803", 1, "ImDs")
        self.assertEqual(2, len(self.galaxy.star_mapping), "Should be 2 worlds in galaxy")
        self.borders.create_erode_border('separate', False)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(5, 34): 'ImDs', (7, 33): 'ImDs'}
        expected_borders = {
            (5, 33): ['green', 'orange', 'black'], (5, 34): ['blue', None, None], (6, 33): [None, 'maroon', 'pink'],
            (7, 32): ['green', 'orange', 'black'], (7, 33): ['blue', None, None], (8, 32): [None, 'maroon', 'pink']
        }
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderOnIbaraSubsector(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        logger = self.borders.logger
        logger.manager.disable = 0

        with self.assertLogs(logger, "DEBUG") as logs:
            self.borders.create_erode_border('separate', False)
            output = logs.output

            exp_output = ['INFO:PyRoute.Borders:Processing worlds for erode map drawing',
                          'DEBUG:PyRoute.Borders:Change Count: 13']
            self.assertEqual(exp_output, output)

        ally_map = self.borders.allyMap
        borders = self.borders.borders
        borders_map = self.borders.borders_map

        expected_ally_map = {(-32, 6): 'ImDi', (-32, 7): 'ImDi', (-32, 8): 'ImDi', (-32, 9): 'ImDi', (-32, 10): 'ImDi',
                             (-32, 11): 'ImDi', (-32, 15): 'ImDi', (-31, 6): 'ImDi', (-31, 7): 'ImDi', (-31, 8): 'ImDi',
                             (-31, 9): 'ImDi', (-31, 10): 'ImDi', (-31, 11): 'ImDi', (-31, 12): 'ImDi',
                             (-31, 13): 'ImDi', (-31, 14): 'ImDi', (-30, 5): 'ImDi', (-30, 6): 'ImDi', (-30, 7): 'ImDi',
                             (-30, 8): 'ImDi', (-30, 9): 'ImDi', (-30, 10): 'ImDi', (-30, 11): 'ImDi', (-30, 12): 'ImDi',
                             (-30, 13): 'ImDi', (-29, 5): 'ImDi', (-29, 6): 'ImDi', (-29, 7): 'ImDi', (-29, 8): 'ImDi',
                             (-29, 9): 'ImDi', (-29, 10): 'ImDi', (-29, 11): 'ImDi', (-29, 12): 'ImDi',
                             (-29, 13): 'ImDi', (-28, 4): 'ImDi', (-28, 5): 'ImDi', (-28, 6): 'ImDi', (-28, 7): 'ImDi',
                             (-28, 8): 'ImDi', (-28, 9): 'ImDi', (-28, 10): 'ImDi', (-28, 11): 'ImDi',
                             (-28, 12): 'ImDi', (-27, 4): 'ImDi', (-27, 5): 'ImDi', (-27, 6): 'ImDi', (-27, 7): 'ImDi',
                             (-27, 8): 'ImDi', (-27, 9): 'ImDi', (-27, 10): 'ImDi', (-27, 11): 'ImDi',
                             (-27, 12): 'ImDi', (-26, 3): 'ImDi', (-26, 4): 'ImDi', (-26, 5): 'ImDi', (-26, 6): 'ImDi',
                             (-26, 7): 'ImDi', (-26, 8): 'ImDi', (-26, 9): 'ImDi', (-26, 10): 'ImDi', (-26, 11): 'ImDi',
                             (-26, 12): 'ImDi', (-25, 5): 'ImDi', (-25, 6): 'ImDi', (-25, 7): 'ImDi', (-25, 8): 'ImDi',
                             (-25, 9): 'ImDi', (-25, 10): 'ImDi', (-25, 11): 'ImDi'}
        expected_borders = {(-32, 5): ['white', 'white', None], (-32, 6): [None, 'white', 'white'], (-32, 7): [None, 'white', 'white'],
                            (-32, 8): [None, 'white', 'white'], (-32, 9): [None, 'white', 'white'], (-32, 10): [None, 'white', 'white'],
                            (-32, 11): ['white', None, 'white'], (-32, 14): ['white', 'white', None], (-32, 15): ['white', None, 'white'],
                            (-31, 4): [None, 'white', None], (-31, 5): ['white', None, None], (-31, 10): [None, 'white', None],
                            (-31, 11): [None, 'white', 'white'], (-31, 12): [None, 'white', 'white'], (-31, 13): [None, None, 'white'],
                            (-31, 14): ['white', None, 'white'], (-30, 4): ['white', 'white', None], (-30, 13): ['white', 'white', None],
                            (-29, 3): [None, 'white', None], (-29, 4): ['white', None, None], (-29, 12): [None, 'white', None],
                            (-29, 13): ['white', None, None], (-28, 3): ['white', 'white', None], (-28, 12): ['white', 'white', None],
                            (-27, 2): [None, 'white', None], (-27, 3): ['white', None, None], (-27, 11): [None, 'white', None],
                            (-27, 12): ['white', None, None], (-26, 2): ['white', 'white', None], (-26, 12): ['white', None, 'white'],
                            (-25, 1): [None, 'white', None], (-25, 2): [None, 'white', 'white'], (-25, 3): [None, 'white', 'white'],
                            (-25, 4): ['white', None, None], (-25, 11): ['white', None, 'white'], (-24, 4): [None, 'white', 'white'],
                            (-24, 5): [None, 'white', 'white'], (-24, 6): [None, 'white', 'white'], (-24, 7): [None, 'white', 'white'],
                            (-24, 8): [None, 'white', 'white'], (-24, 9): [None, 'white', 'white'], (-24, 10): [None, 'white', 'white']}
        expected_borders_map = {}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderOnFarFrontiersSector(self) -> None:
        sourcefile = self.unpack_filename('BorderGeneration/Far Frontiers.sec')
        mapfile = self.unpack_filename('BorderGeneration/Far Frontiers-erode-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Far Frontiers-erode-border.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        logger = self.borders.logger
        logger.manager.disable = 0

        with self.assertLogs(logger, "DEBUG") as logs:
            self.borders.create_erode_border('separate', True)
            output = logs.output

            exp_output = ['INFO:PyRoute.Borders:Processing worlds for erode map drawing',
                          'DEBUG:PyRoute.Borders:Change Count: 17']
            self.assertEqual(exp_output, output)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)

    def testErodeBorderOnVanguardReachesSector(self) -> None:
        sourcefile = self.unpack_filename('BorderGeneration/Vanguard Reaches.sec')
        mapfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-erode-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-erode-border.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        logger = self.borders.logger
        logger.manager.disable = 0

        with self.assertLogs(logger, "DEBUG") as logs:
            self.borders.create_erode_border('separate', True)
            output = logs.output

            exp_output = ['INFO:PyRoute.Borders:Processing worlds for erode map drawing',
                          'DEBUG:PyRoute.Borders:Change Count: 23']
            self.assertEqual(exp_output, output)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = {}

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
        result, msg = self.borders.is_well_formed()
        self.assertTrue(result, msg)
