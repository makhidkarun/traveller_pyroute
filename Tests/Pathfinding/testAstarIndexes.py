"""
Created on Sep 21, 2023

@author: CyberiaResurrection
"""
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest
from PyRoute.Pathfinding.astar import astar_path_indexes


class testAStarIndexes(baseTest):

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

        source = galaxy.star_mapping[0]
        target = galaxy.star_mapping[36]

        galaxy.trade.shortest_path_tree = ApproximateShortestPathTree(source.index, galaxy.stars, 0)

        heuristic = galaxy.heuristic_distance_indexes

        exp_route = [0, 8, 9, 15, 24, 36]
        exp_diag = dict()
        exp_diag['heuristic_calls'] = 27
        exp_diag['neighbours_checked'] = 31
        exp_diag['nodes_expanded'] = 25
        exp_diag['nodes_queued'] = 31

        act_route, act_diag = astar_path_indexes(galaxy.stars, source.index, target.index, heuristic)
        self.assertEqual(exp_route, act_route)
        self.assertEqual(exp_diag, act_diag)
