"""
Created on Apr 17, 2025

@author: CyberiaResurrection
"""
import copy

from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary
from Tests.baseTest import baseTest


class testAllegiance(baseTest):

    def testAslanAllegianceNotBeginningWithAs(self):
        code = "A8"
        name = "Aslan Hierate, Tlaukhu control, Seieakh (9), Akatoiloh (18), We'okurir (29)"
        pop = "Asla"

        alleg = Allegiance(code, name, False, pop)

        result, msg = alleg.is_well_formed()
        self.assertTrue(result, msg)

    def test_deep_copy_of_new_allegiance(self):
        code = "A8"
        name = "Aslan Hierate, Tlaukhu control, Seieakh (9), Akatoiloh (18), We'okurir (29)"
        pop = "Asla"

        alleg = Allegiance(code, name, False, pop)

        foo = copy.deepcopy(alleg)
        self.assertTrue(isinstance(foo, Allegiance))

    def test_allegiance_list_on_galaxy_read(self):
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=11, max_jump=4)
        galaxy.read_sectors(readparms)

        expected_allegiances = ['As', 'AsMw', 'AsSc', 'AsT0', 'AsT1', 'AsT2', 'AsT3', 'AsT4', 'AsT5', 'AsT6', 'AsT7',
                                'AsT8', 'AsT9', 'AsTv', 'AsVc', 'AsWc', 'AsXX', 'BlSo', 'CsIm', 'CsZh', 'FlLe', 'GlEm',
                                'Im', 'ImDd', 'NaDr', 'NaHu', 'NaXX', 'SeFo', 'StCl']
        actual_allegiances = list(galaxy.alg.keys())

        self.assertEqual(expected_allegiances, actual_allegiances, "Allegiance name list unexpected")

    def test_allegiance_list_on_sector_dictionary_read(self):
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)

        expected_allegiances = ['As', 'AsMw', 'AsSc', 'AsT0', 'AsT1', 'AsT2', 'AsT3', 'AsT4', 'AsT5', 'AsT6', 'AsT7',
                                'AsT8', 'AsT9', 'AsTv', 'AsVc', 'AsWc', 'AsXX', 'BlSo', 'CsIm', 'CsZh', 'FlLe', 'GlEm',
                                'Im', 'ImDd', 'NaDr', 'NaHu', 'NaXX', 'SeFo', 'StCl']
        actual_allegiances = list(sector.allegiances.keys())

        self.assertEqual(expected_allegiances, actual_allegiances, "Allegiance name list unexpected")
