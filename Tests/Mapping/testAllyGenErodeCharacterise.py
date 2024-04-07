import json

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Position.Hex import Hex
from Tests.Mapping.testAllyGenBase import TestAllyGenBase


class TestAllyGenErodeCharacterise(TestAllyGenBase):

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

    def testErodeBorderOnIbaraSubsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_erode_border('separate', False)

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
                             (-25, 9): 'ImDi', (-25, 10): 'ImDi', (-25, 11): 'ImDi' }
        expected_borders = {(-33, 7): 2, (-33, 8): 2, (-33, 9): 2, (-33, 10): 2, (-33, 11): 2, (-33, 12): 2,
                            (-33, 16): 2, (-32, 6): 7, (-32, 7): 4, (-32, 8): 4, (-32, 9): 4, (-32, 10): 4,
                            (-32, 11): 4, (-32, 12): 3, (-32, 13): 2, (-32, 14): 2, (-32, 15): 5, (-32, 16): 1,
                            (-31, 6): 1, (-31, 12): 4, (-31, 13): 4, (-31, 14): 4, (-31, 15): 5, (-30, 5): 7,
                            (-30, 14): 7, (-29, 5): 1, (-29, 14): 1, (-28, 4): 7, (-28, 13): 7, (-27, 4): 1,
                            (-27, 13): 3, (-26, 3): 7, (-26, 4): 2, (-26, 5): 2, (-26, 13): 1, (-25, 3): 4, (-25, 4): 4,
                            (-25, 5): 3, (-25, 6): 2, (-25, 7): 2, (-25, 8): 2, (-25, 9): 2, (-25, 10): 2, (-25, 11): 2,
                            (-25, 12): 5, (-24, 5): 4, (-24, 6): 4, (-24, 7): 4, (-24, 8): 4, (-24, 9): 4, (-24, 10): 4,
                            (-24, 11): 4}
        expected_borders_map = {(-32, 6): 3, (-32, 7): 6, (-32, 8): 6, (-32, 9): 6, (-32, 10): 6, (-32, 11): 6,
                                (-32, 12): 5, (-32, 15): 3, (-32, 16): 5, (-31, 5): 2, (-31, 6): 1, (-31, 11): 2,
                                (-31, 12): 6, (-31, 13): 6, (-31, 14): 4, (-31, 15): 5, (-30, 5): 3, (-30, 14): 3,
                                (-29, 4): 2, (-29, 5): 1, (-29, 13): 2, (-29, 14): 1, (-28, 4): 3, (-28, 13): 3,
                                (-27, 3): 2, (-27, 4): 1, (-27, 12): 2, (-27, 13): 1, (-26, 3): 3, (-26, 13): 5,
                                (-25, 2): 2, (-25, 3): 6, (-25, 4): 6, (-25, 5): 1, (-25, 12): 5, (-24, 5): 6,
                                (-24, 6): 6, (-24, 7): 6, (-24, 8): 6, (-24, 9): 6, (-24, 10): 6, (-24, 11): 6}
        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testErodeBorderOnFarFrontiersSector(self):
        sourcefile = self.unpack_filename('BorderGeneration/Far Frontiers.sec')
        mapfile = self.unpack_filename('BorderGeneration/Far Frontiers-erode-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Far Frontiers-erode-border.json')
        bordermapfile = self.unpack_filename('BorderGeneration/Far Frontiers-erode-bordermap.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_erode_border('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = self.load_dict_from_json(bordermapfile)

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")

    def testErodeBorderOnVanguardReachesSector(self):
        sourcefile = self.unpack_filename('BorderGeneration/Vanguard Reaches.sec')
        mapfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-erode-allymap.json')
        borderfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-erode-border.json')
        bordermapfile = self.unpack_filename('BorderGeneration/Vanguard Reaches-erode-bordermap.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        self.galaxy = DeltaGalaxy(args.btn, args.max_jump)
        self.galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        self.borders = self.galaxy.borders
        self.borders.create_erode_border('separate', True)

        expected_ally_map = self.load_dict_from_json(mapfile)
        expected_borders = self.load_dict_from_json(borderfile)
        expected_borders_map = self.load_dict_from_json(bordermapfile)

        ally_map = dict(self.borders.allyMap)
        borders = dict(self.borders.borders)
        borders_map = dict(self.borders.borders_map)

        self.assertEqual(expected_ally_map, ally_map, "Unexpected ally_map value")
        self.assertEqual(expected_borders, borders, "Unexpected borders value")
        self.assertEqual(expected_borders_map, borders_map, "Unexpected borders_map value")
