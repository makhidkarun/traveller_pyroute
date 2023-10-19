"""
Created on Oct 19, 2023

@author: CyberiaResurrection
"""
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.StatCalculation import StatCalculation
from Tests.baseTest import baseTest


class testStatCalcRegression(baseTest):

    def testStatsCalcWithZeroPopulation(self):
        sourcefile = self.unpack_filename('DeltaFiles/stat_calc_division_by_zero_population/Dagudashaag-zero.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()
        args.max_jump = 2
        args.min_btn = 15

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()

        stats = StatCalculation(galaxy)
        stats.calculate_statistics(args.ally_match)
        stats.write_statistics(args.ally_count, args.ally_match, args.json_data)
