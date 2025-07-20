"""
Created on Aug 08, 2024

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from Tests.baseTest import baseTest


class testTradeMPCalculation(baseTest):
    def test_direct_route_doesnt_blow_up(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/direct_routes_on_trade_mp/Lishun.sec')

        args = self._make_args()
        args.route_reuse = 30
        args.route_btn = 8
        args.mp_threads = 2
        args.routes = "trade-mp"

        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.set_borders(args.borders, args.ally_match)
        galaxy.trade.calculate_routes()

    def test_direct_route_doesnt_blow_up_2(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/direct_routes_on_trade_mp/Lishun.sec')

        args = self._make_args()
        args.route_reuse = 30
        args.min_btn = 15
        args.mp_threads = 2
        args.routes = "trade-mp"

        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.set_borders(args.borders, args.ally_match)
        galaxy.trade.calculate_routes()
