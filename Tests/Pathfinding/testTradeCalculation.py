"""
Created on Aug 08, 2024

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from Tests.baseTest import baseTest


class testTradeCalculation(baseTest):
    def test_nodes_not_duplicated(self):
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output

        self.assertEqual(1, len(galaxy.sectors))
        sector = galaxy.sectors['Trojan Reach']
        self.assertEqual(16, len(sector.subsectors))
        self.assertEqual(11, len(sector.alg))
        self.assertEqual(16, len(sector.worlds))

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()

    def test_nodes_not_duplicated_2(self):
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Verge.sec')

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output

        self.assertEqual(1, len(galaxy.sectors))
        sector = galaxy.sectors['Verge']
        self.assertEqual(16, len(sector.subsectors))
        self.assertEqual(2, len(sector.alg))
        self.assertEqual(13, len(sector.worlds))

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        galaxy.trade.calculate_routes()
