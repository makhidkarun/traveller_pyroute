"""
Created on Aug 08, 2024

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from Tests.baseTest import baseTest
try:
    from PyRoute.Pathfinding.astar_numpy import astar_path_numpy
except ModuleNotFoundError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy
except ImportError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy
except AttributeError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy
try:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
except ModuleNotFoundError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except ImportError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified


class testTradeCalculation(baseTest):
    def test_nodes_not_duplicated(self) -> None:
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

    def test_nodes_not_duplicated_2(self) -> None:
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

    def test_route_update_simple(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/duplicate_node_blowup/Trojan Reach.sec')
        args = self._make_args()
        args.route_btn = 8
        args.route_reuse = 10
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()
        galaxy.trade.star_graph = DistanceGraph(galaxy.stars)

        btn_skipped = [(s, n) for (s, n) in galaxy.ranges.edges() if s.component != n.component]
        for s, n in btn_skipped:
            galaxy.ranges.remove_edge(s, n)

        btn = [(s, n, d) for (s, n, d) in galaxy.ranges.edges(data=True)]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)
        landmarks, galaxy.trade.component_landmarks = galaxy.trade.get_landmarks(index=True, btn=btn)

        btn_dex = 12
        star_dex = btn[btn_dex][0].index
        targ_dex = btn[btn_dex][1].index

        galaxy.trade.shortest_path_tree = ApproximateShortestPathForestUnified(1, galaxy.stars,
                                                                             0.1, sources=landmarks)

        rawroute, _ = astar_path_numpy(galaxy.trade.star_graph, star_dex, targ_dex,
                                          galaxy.trade.shortest_path_tree.lower_bound_bulk, upbound=float('+inf'))

        expected_rawroute = [9, 4, 6, 5, 11, 13]
        self.assertEqual(expected_rawroute, rawroute, "Unexpected raw route")
        route = [galaxy.star_mapping[item] for item in rawroute]
        distance = galaxy.trade.route_distance(route)

        tradeCr, tradePass, tradeDton = galaxy.trade.route_update_simple(route, True, distance=distance)
        self.assertEqual(50000000, tradeCr, "Unexpected tradeCr value")
        self.assertEqual(500, tradePass, "Unexpected tradePass value")
        self.assertEqual(1000, tradeDton, "Unexpected tradeDton value")

        ends = [9, 13]
        mids = [4, 6, 5, 11]

        for item in mids:
            self.assertEqual(tradeCr, galaxy.star_mapping[item].tradeOver)
            self.assertEqual(1, galaxy.star_mapping[item].tradeCount)
            self.assertEqual(tradePass, galaxy.star_mapping[item].passOver)
            self.assertEqual(0, galaxy.star_mapping[item].tradeIn)
            self.assertEqual(0, galaxy.star_mapping[item].passIn)

        for item in ends:
            self.assertEqual(tradeCr // 2, galaxy.star_mapping[item].tradeIn)
            self.assertEqual(0, galaxy.star_mapping[item].tradeCount)
            self.assertEqual(tradePass, galaxy.star_mapping[item].passIn)
            self.assertEqual(0, galaxy.star_mapping[item].tradeOver)
            self.assertEqual(0, galaxy.star_mapping[item].passOver)

        start = rawroute[0]
        expected_wt = [88.4, 166.0, 71.3, 142.6, 141.7]
        self.assertEqual(len(rawroute) - 1, len(expected_wt))
        counter = 0

        for end in rawroute[1:]:
            data = galaxy.stars[start][end]
            self.assertEqual(tradeCr, data['trade'])
            self.assertEqual(1, data['count'])
            self.assertEqual(expected_wt[counter], data['weight'], "Unexpected segment weight")

            start = end
            counter += 1

        data = galaxy.ranges[route[0]][route[-1]]
        self.assertEqual(16, data['actual distance'], "Unexpected route distance")
        self.assertEqual(5, data['jumps'], "Unexpected # of jumps")

    def test_sufficient_exhaust_value(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/insufficient_exhaust_value/Core.sec')
        args = self._make_args()
        args.route_btn = 8
        args.route_reuse = 10
        readparms = ReadSectorOptions(sectors=[sourcefile], pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice=args.routes, route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)
        galaxy.output_path = args.output
        galaxy.generate_routes()
