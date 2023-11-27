import argparse
import json
import os
import platform
import tempfile
import unittest
from collections import defaultdict

import pytest
from PyRoute.AllyGen import AllyGen
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest


class testAllyGenBorders(baseTest):

    maxDiff = 9001

    def test_create_ally_map_masionia_collapse(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = self.unpack_filename('DeltaFiles/create_ally_map_masionia_collapse/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_ally_map_masionia_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_ally_map_masionia_separate(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = self.unpack_filename('DeltaFiles/create_ally_map_masionia_separate/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_ally_map_masionia_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_erode_border_masionia_collapse(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = self.unpack_filename('DeltaFiles/create_erode_border_masionia_collapse/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_erode_border_masionia_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_erode_border_masionia_separate(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = self.unpack_filename('DeltaFiles/create_erode_border_masionia_separate/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_erode_border_masionia_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_masionia_collapse(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = self.unpack_filename('DeltaFiles/create_borders_masionia_collapse/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_borders_masionia_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_borders('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_masionia_separate(self):
        sourcefile = self.unpack_filename('DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = self.unpack_filename('DeltaFiles/create_borders_masionia_separate/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_borders_masionia_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_borders('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_district_268_collapse(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_borders('collapse')

        self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_district_268_separate(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_borders_district_268_separate/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_borders_district_268_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_borders('separate')

        self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_ally_map_district_268_collapse(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_ally_map_district_268_collapse/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_ally_map_district_268_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('collapse')

        self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
        self.assertDictEqual(expected_allies, allygen.allyMap)
        self.assertDictEqual(expected_borders, allygen.borders)

    def test_create_ally_map_district_268_collapse_trim(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_ally_map_district_268_collapse_trim/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_ally_map_district_268_collapse_trim/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_ally_map_district_268_collapse_trim/borders.json')

        foo = platform.platform()
        is_fnorda = '.fc' in foo

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('collapse')

        if is_fnorda:  # Write out current gubbins
            self.dump_expected_values(allygen, allymap, borderfile)
        else:  # Check stored gubbins
            expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)
            self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
            self.assertDictEqual(expected_allies, allygen.allyMap)
            self.assertDictEqual(expected_borders, allygen.borders)

    def test_create_borders_district_268_collapse_trim(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse_trim/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse_trim/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse_trim/borders.json')

        foo = platform.platform()
        is_fnorda = '.fc' in foo

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        allygen = AllyGen(galaxy)

        allygen.create_borders('collapse')

        if is_fnorda:  # Write out current gubbins
            self.dump_expected_values(allygen, allymap, borderfile)
        else:  # Check stored gubbins
            expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)
            self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
            self.assertDictEqual(expected_allies, allygen.allyMap)
            self.assertDictEqual(expected_borders, allygen.borders)

    def test_create_erode_border_district_268_collapse_trim(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_erode_border_district_268_collapse_trim/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_erode_border_district_268_collapse_trim/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_erode_border_district_268_collapse_trim/borders.json')

        foo = platform.platform()
        is_fnorda = '.fc' in foo

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('collapse')

        if is_fnorda:  # Write out current gubbins
            self.dump_expected_values(allygen, allymap, borderfile)
        else:  # Check stored gubbins
            expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)
            #self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
            self.assertDictEqual(dict(expected_allies), allygen.allyMap)
            self.assertDictEqual(dict(expected_borders), allygen.borders)

    def test_create_ally_map_district_268_separate(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_ally_map_district_268_separate/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_ally_map_district_268_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('separate')

        self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_erode_border_district_268_collapse(self):
        sourcefile = self.unpack_filename('DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_erode_border_district_268_collapse/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_erode_border_district_268_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('collapse')

        self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
        self.assertEqual(dict(expected_allies), allygen.allyMap)
        self.assertEqual(dict(expected_borders), allygen.borders)

    def test_create_erode_border_district_268_separate(self):
        sourcefile = self.unpack_filename(
            'DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = self.unpack_filename('DeltaFiles/create_erode_border_district_268_separate/allymap.json')
        borderfile = self.unpack_filename('DeltaFiles/create_erode_border_district_268_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        expected_allies, expected_borders = self.load_expected_values(allymap, borderfile)

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('separate')

        self.assertEqual(len(expected_allies), len(allygen.allyMap), "Unexpected allyMap length")
        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def load_expected_values(self, allymap, borderfile):
        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = defaultdict(set)
        for key in expected_string:
            trimkey = key.strip('()')
            bitz = trimkey.split(',')
            nukey = (int(bitz[0]), int(bitz[1]))
            expected_allies[nukey] = expected_string[key]
        # Load expected borders
        with open(borderfile, 'r') as file:
            expected_string = json.load(file)
        expected_borders = dict()
        for key in expected_string:
            trimkey = key.strip('()')
            bitz = trimkey.split(',')
            nukey = (int(bitz[0]), int(bitz[1]))
            expected_borders[nukey] = expected_string[key]
        return expected_allies, expected_borders

    def dump_expected_values(self, allygen, allymap, borderfile):
        with open(borderfile, 'w') as file:
            dump_dict = dict()
            for loc in allygen.borders:
                dump_dict[str(loc)] = allygen.borders[loc]
            foo_string = json.dumps(dump_dict)
            file.write(foo_string)
        # seed expected allymap
        with open(allymap, 'w') as file:
            dump_dict = dict()
            for loc in allygen.allyMap:
                dump_dict[str(loc)] = allygen.allyMap[loc]
            foo_string = json.dumps(dump_dict)
            file.write(foo_string)

    def _make_args(self):
        args = argparse.ArgumentParser(description='PyRoute input minimiser.')
        args.btn = 8
        args.max_jump = 2
        args.route_btn = 13
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.routes = 'trade'
        args.route_reuse = 10
        args.interestingline = None
        args.interestingtype = None
        args.maps = None
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False
        args.output = tempfile.gettempdir()
        args.debug_flag = False
        args.mp_threads = 1
        return args


if __name__ == '__main__':
    unittest.main()
