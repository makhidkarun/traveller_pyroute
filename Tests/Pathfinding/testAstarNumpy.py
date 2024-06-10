"""
Created on Sep 21, 2023

@author: CyberiaResurrection
"""
from PyRoute.Pathfinding.ApproximateShortestPathTreeDistanceGraph import ApproximateShortestPathTreeDistanceGraph
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest
from PyRoute.Pathfinding.astar_numpy import astar_path_numpy


class testAStarNumpy(baseTest):

    def testAStarOverSubsector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()
        dist_graph = DistanceGraph(galaxy.stars)

        source = galaxy.star_mapping[0]
        target = galaxy.star_mapping[36]

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTreeDistanceGraph(source.index, galaxy.stars, 0)

        heuristic = galaxy.heuristic_distance_bulk

        exp_route = [0, 8, 9, 15, 24, 36]
        exp_diagnostics = {'branch_factor': 1.704, 'f_exhausted': 3, 'g_exhausted': 3, 'neighbour_bound': 14,
                            'new_upbounds': 1, 'nodes_expanded': 16, 'nodes_queued': 18, 'nodes_revisited': 1,
                            'num_jumps': 5, 'un_exhausted': 7, 'targ_exhausted': 1}

        upbound = galaxy.trade.shortest_path_tree.triangle_upbound(source, target) * 1.005
        act_route, diagnostics = astar_path_numpy(dist_graph, source.index, target.index, heuristic, upbound=upbound,
                                                  diagnostics=True)
        self.assertEqual(exp_route, act_route)
        self.assertEqual(exp_diagnostics, diagnostics)
