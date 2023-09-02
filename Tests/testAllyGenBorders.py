import argparse
import json
import os
import tempfile
import unittest

from AllyGen import AllyGen
from DeltaDictionary import SectorDictionary, DeltaDictionary
from DeltaGalaxy import DeltaGalaxy


class testAllyGenBorders(unittest.TestCase):
    def test_create_ally_map_masionia_collapse(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = os.path.abspath('../DeltaFiles/create_ally_map_masionia_collapse/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_ally_map_masionia_collapse/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_ally_map_masionia_collapse/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_ally_map_masionia_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_ally_map_masionia_separate(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = os.path.abspath('../DeltaFiles/create_ally_map_masionia_separate/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_ally_map_masionia_separate/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_ally_map_masionia_separate/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_ally_map_masionia_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_ally_map('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_erode_border_masionia_collapse(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = os.path.abspath('../DeltaFiles/create_erode_border_masionia_collapse/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_erode_border_masionia_collapse/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_erode_border_masionia_collapse/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_erode_border_masionia_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_erode_border_masionia_separate(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = os.path.abspath('../DeltaFiles/create_erode_border_masionia_separate/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_erode_border_masionia_separate/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_erode_border_masionia_separate/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_erode_border_masionia_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_erode_border('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_masionia_collapse(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = os.path.abspath('../DeltaFiles/create_borders_masionia_collapse/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_borders_masionia_collapse/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_borders_masionia_collapse/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_borders_masionia_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_borders('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_masionia_separate(self):
        sourcefile = os.path.abspath('../DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/comm_route_blowups/Lishun-Masionia.sec')
        allymap = os.path.abspath('../DeltaFiles/create_borders_masionia_separate/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_borders_masionia_separate/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_borders_masionia_separate/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_borders_masionia_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_borders('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_district_268_collapse(self):
        sourcefile = os.path.abspath('../DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = os.path.abspath('../DeltaFiles/create_borders_district_268_collapse/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_borders_district_268_collapse/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_borders_district_268_collapse/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_borders_district_268_collapse/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_borders('collapse')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

    def test_create_borders_district_268_separate(self):
        sourcefile = os.path.abspath('../DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/create_borders_district_268_collapse/Spinward Marches-District 268.sec')
        allymap = os.path.abspath('../DeltaFiles/create_borders_district_268_separate/allymap.json')
        if not os.path.isfile(allymap):
            allymap = os.path.abspath('../Tests/DeltaFiles/create_borders_district_268_separate/allymap.json')
        borderfile = os.path.abspath('../DeltaFiles/create_borders_district_268_separate/borders.json')
        if not os.path.isfile(borderfile):
            borderfile = os.path.abspath('../Tests/DeltaFiles/create_borders_district_268_separate/borders.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 4

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # Load expected allymap
        with open(allymap, 'r') as file:
            expected_string = json.load(file)
        expected_allies = dict()
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

        allygen = AllyGen(galaxy)

        allygen.create_borders('separate')

        self.assertEqual(expected_allies, allygen.allyMap)
        self.assertEqual(expected_borders, allygen.borders)

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
        return args

        # dump-out-allygen-guts code kept here for reference
        # seed expected borders
        #with open(borderfile, 'w') as file:
        #    dump_dict = dict()
        #    for loc in allygen.borders:
        #        dump_dict[str(loc)] = allygen.borders[loc]
        #    foo_string = json.dumps(dump_dict)
        #    file.write(foo_string)

        # seed expected allymap
        #with open(allymap, 'w') as file:
        #    dump_dict = dict()
        #    for loc in allygen.allyMap:
        #        dump_dict[str(loc)] = allygen.allyMap[loc]
        #    foo_string=json.dumps(dump_dict)
        #    file.write(foo_string)

if __name__ == '__main__':
    unittest.main()
