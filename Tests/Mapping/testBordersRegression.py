"""
Created on Sep 21, 2025

@author: CyberiaResurrection
"""
import tempfile

from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary, SectorDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Inputs.ParseStarInput import ParseStarInput
from Tests.baseTest import baseTest


class testBordersRegression(baseTest):

    def setUp(self) -> None:
        ParseStarInput.deep_space = {}

    def test_border_regression_zdiedeiant_sector_minimised(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/border_blowup_1/Zdiedeiant.sec')

        galaxy = DeltaGalaxy(min_btn=15, max_jump=4)
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.route_reuse = 10
        args.trade_choice = 'trade'
        args.fix_pop = False
        args.route_btn = 8
        args.output = tempfile.gettempdir()
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.trade_choice, args.route_btn, 1, False)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.set_borders(args.borders, args.ally_match)
        result, msg = galaxy.borders.is_well_formed()
        self.assertTrue(result, msg)

    def test_border_regression_zdiedeiant_sector_minimised_no_border(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/border_blowup_2/Zdiedeiant.sec')

        galaxy = DeltaGalaxy(min_btn=15, max_jump=4)
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.route_reuse = 10
        args.trade_choice = 'trade'
        args.fix_pop = False
        args.route_btn = 8
        args.output = tempfile.gettempdir()
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.trade_choice, args.route_btn, 1, False)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.set_borders(args.borders, args.ally_match)
        result, msg = galaxy.borders.is_well_formed()
        self.assertTrue(result, msg)
        exp_borders = {
            (-223, 237): [None, None, None],
            (-223, 238): [None, None, None],
            (-222, 236): [None, None, None],
            (-222, 238): [None, None, None],
            (-221, 235): [None, None, None],
            (-221, 237): [None, None, None],
            (-221, 238): [None, None, None],
            (-221, 239): [None, None, None],
            (-220, 235): [None, None, None],
            (-220, 239): [None, None, None],
            (-219, 234): [None, None, None],
            (-219, 235): [None, None, None],
            (-219, 238): [None, None, None],
            (-218, 235): [None, None, None],
            (-218, 236): [None, None, None],
            (-218, 237): [None, None, None]
        }
        self.assertEqual(exp_borders, galaxy.borders.borders)

    def test_border_regression_raakaan_sector_minimised(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/border_blowup_3/Raakaan.sec')

        galaxy = DeltaGalaxy(min_btn=15, max_jump=4)
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.route_reuse = 10
        args.trade_choice = 'trade'
        args.fix_pop = False
        args.route_btn = 8
        args.output = tempfile.gettempdir()
        args.borders = 'allygen'
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.trade_choice, args.route_btn, 1, False)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.set_borders(args.borders, args.ally_match)
        result, msg = galaxy.borders.is_well_formed()
        self.assertTrue(result, msg)
        exp_borders = {
            (202, -31): ['green', 'green', None], (202, -30): ['green', None, 'green'],
            (203, -32): [None, 'green', None], (203, -31): [None, None, 'green']
        }
        self.assertEqual(exp_borders, galaxy.borders.borders)
