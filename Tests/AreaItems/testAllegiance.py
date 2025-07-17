"""
Created on Apr 17, 2025

@author: CyberiaResurrection
"""
import copy

from AreaItems.Allegiance import Allegiance
from AreaItems.Galaxy import Galaxy
from DataClasses.ReadSectorOptions import ReadSectorOptions
from DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest


class testAllegiance(baseTest):

    def testAslanAllegianceNotBeginningWithAs(self) -> None:
        code = "A8"
        name = "Aslan Hierate, Tlaukhu control, Seieakh (9), Akatoiloh (18), We'okurir (29)"
        pop = "Asla"

        alleg = Allegiance(code, name, False, pop)

        result, msg = alleg.is_well_formed()
        self.assertTrue(result, msg)

    def test_deep_copy_of_new_allegiance(self) -> None:
        code = "A8"
        name = "Aslan Hierate, Tlaukhu control, Seieakh (9), Akatoiloh (18), We'okurir (29)"
        pop = "Asla"

        alleg = Allegiance(code, name, False, pop)

        foo = copy.deepcopy(alleg)
        self.assertTrue(isinstance(foo, Allegiance))

    def test_allegiance_list_on_galaxy_read(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=11, max_jump=4)
        galaxy.read_sectors(readparms)

        expected_allegiances = {'As': 7, 'AsMw': 1, 'AsSc': 0, 'AsT0': 1, 'AsT1': 0, 'AsT2': 0, 'AsT3': 0, 'AsT4': 0,
                                'AsT5': 0, 'AsT6': 0, 'AsT7': 0, 'AsT8': 0, 'AsT9': 1, 'AsTv': 2, 'AsVc': 1, 'AsWc': 1,
                                'AsXX': 0, 'BlSo': 0, 'CsIm': 1, 'CsZh': 0, 'FlLe': 0, 'GlEm': 0, 'Im': 3, 'ImDd': 3,
                                'NaDr': 0, 'NaHu': 5, 'NaXX': 0, 'SeFo': 0, 'StCl': 0}
        actual_allegiances = list(galaxy.alg.keys())

        self.assertEqual(list(expected_allegiances.keys()), actual_allegiances, "Allegiance name list unexpected")
        for alg_name in expected_allegiances:
            expected_count = expected_allegiances[alg_name]
            actual_count = len(galaxy.alg[alg_name].worlds)
            self.assertEqual(expected_count, actual_count, "Unexpected world count for " + alg_name + " allegiance")
            if 0 != expected_count:
                actual_count = len(galaxy.sectors['Trojan Reach'].alg[alg_name].worlds)
                self.assertEqual(expected_count, actual_count, "Unexpected world count for " + alg_name + " allegiance")
            else:
                self.assertNotIn(alg_name, galaxy.sectors['Trojan Reach'].alg, "Unexpected allegiance " + alg_name)

    def test_allegiance_list_on_sector_dictionary_read(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)

        expected_allegiances = ['As', 'AsMw', 'AsSc', 'AsT0', 'AsT1', 'AsT2', 'AsT3', 'AsT4', 'AsT5', 'AsT6', 'AsT7',
                                'AsT8', 'AsT9', 'AsTv', 'AsVc', 'AsWc', 'AsXX', 'BlSo', 'CsIm', 'CsZh', 'FlLe', 'GlEm',
                                'Im', 'ImDd', 'NaDr', 'NaHu', 'NaXX', 'SeFo', 'StCl']
        actual_allegiances = list(sector.allegiances.keys())

        self.assertEqual(expected_allegiances, actual_allegiances, "Allegiance name list unexpected")

    def test_allegiance_list_on_delta_galaxy_read(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')

        args = self._make_args()
        args.route_btn = 15

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta['Trojan Reach'] = sector

        galaxy = DeltaGalaxy(min_btn=11, max_jump=4)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc, args.route_reuse, args.routes, args.route_btn,
                            1, False)

        expected_allegiances = {'As': 7, 'AsMw': 1, 'AsSc': 0, 'AsT0': 1, 'AsT1': 0, 'AsT2': 0, 'AsT3': 0, 'AsT4': 0,
                                'AsT5': 0, 'AsT6': 0, 'AsT7': 0, 'AsT8': 0, 'AsT9': 1, 'AsTv': 2, 'AsVc': 1, 'AsWc': 1,
                                'AsXX': 0, 'BlSo': 0, 'CsIm': 1, 'CsZh': 0, 'FlLe': 0, 'GlEm': 0, 'Im': 3, 'ImDd': 3,
                                'NaDr': 0, 'NaHu': 5, 'NaXX': 0, 'SeFo': 0, 'StCl': 0}
        actual_allegiances = list(galaxy.alg.keys())
        self.assertEqual(list(expected_allegiances.keys()), actual_allegiances, "Allegiance name list unexpected")
        for alg_name in expected_allegiances:
            expected_count = expected_allegiances[alg_name]
            actual_count = len(galaxy.alg[alg_name].worlds)
            self.assertEqual(expected_count, actual_count, "Unexpected world count for " + alg_name + " allegiance")
            if 0 != expected_count:
                actual_count = len(galaxy.sectors['Trojan Reach'].alg[alg_name].worlds)
                self.assertEqual(expected_count, actual_count, "Unexpected world count for " + alg_name + " allegiance")
            else:
                self.assertNotIn(alg_name, galaxy.sectors['Trojan Reach'].alg, "Unexpected allegiance " + alg_name)
