"""
Created on Nov 26, 2026

@author: CyberiaResurrection
"""
from PyRoute.AreaItems.Galaxy import Galaxy
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Calculation.CommCalculation import CommCalculation
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
from PyRoute.Position.Hex import Hex
from PyRoute.SystemData.UWP import UWP
from PyRoute.SystemData.StarList import StarList
from PyRoute.Star import Star
from PyRoute.TradeCodes import TradeCodes
from Tests.baseTest import baseTest

try:
    from PyRoute.Pathfinding.astar_numpy import astar_path_numpy
except ModuleNotFoundError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy
except ImportError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy
except AttributeError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy


class testCommCalculation(baseTest):

    def setUp(self) -> None:
        self.reset_logging()

    def test_get_route_between(self):
        sourcefile = [
            self.unpack_filename('DeltaFiles/Dagudashaag.sec'),
            self.unpack_filename('DeltaFiles/Zarushagar.sec')
        ]

        args = self._make_args()
        args.route_btn = 15
        readparms = ReadSectorOptions(sectors=sourcefile, pop_code=args.pop_code, ru_calc=args.ru_calc,
                                      route_reuse=args.route_reuse, trade_choice='comm', route_btn=args.route_btn,
                                      mp_threads=args.mp_threads, debug_flag=args.debug_flag, fix_pop=False,
                                      deep_space={}, map_type=args.map_type)

        galaxy = Galaxy(min_btn=15, max_jump=4)
        galaxy.read_sectors(readparms)

        calc = CommCalculation(galaxy)
        galaxy.trade = calc
        logger = calc.logger
        logger.manager.disable = 10

        calc.generate_routes()
        calc.calculate_components()

        source = max(galaxy.star_mapping.values(), key=lambda item: item.wtn)
        calc.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, galaxy.stars, calc.epsilon)

        max_edge = max(galaxy.ranges.edges(data=True), key=lambda x: x[2]['distance'] if x[0].component == x[1].component else 0)

        star = max_edge[0]
        target = max_edge[1]

        bulk = galaxy.heuristic_distance_bulk
        upbound = calc.shortest_path_tree.triangle_upbound(star.index, target.index) * 1.005
        route, _ = astar_path_numpy(calc.star_graph, star.index, target.index, bulk, upbound=upbound)

        exp_edges = []
        start = route[0]
        for i in range(1, len(route)):
            end = route[i]
            raw_edge = calc.star_graph.get_edge(start, end)
            exp_edges.append(raw_edge)

            start = end
        self.assertEqual(len(route) - 1, len(exp_edges), "Exp_edges should be 1 less element than route")

        calc.get_route_between(star, target)
        exp_lobounds = [32.5, 0]

        start = route[0]
        for i in range(1, len(route) - 1):
            end = route[i]
            exp_edge = exp_edges[i - 1]
            raw_edge = calc.star_graph.get_edge(start, end)
            self.assertGreater(exp_edge, raw_edge, "Edge " + str(i - 1) + " not decreased after get_route_between")
            exp_lobound = exp_lobounds[i - 1]
            lobound = calc.shortest_path_tree.lower_bound(start, end)
            self.assertAlmostEqual(exp_lobound, lobound, 4, "Lower bound for edge " + str(i - 1) + " not approx equal")
            start = end
