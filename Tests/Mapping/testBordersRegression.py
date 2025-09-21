"""
Created on Sep 21, 2025

@author: CyberiaResurrection
"""
import tempfile

from PyRoute.DeltaDebug.DeltaDictionary import DeltaDictionary, SectorDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest


class testBordersRegression(baseTest):

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
