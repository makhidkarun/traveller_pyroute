"""
Created on Mar 06, 2024

@author: CyberiaResurrection
"""
import numpy as np

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from PyRoute.Pathfinding.LandmarkSchemes.LandmarkAvoidHelper import LandmarkAvoidHelper
from Tests.baseTest import baseTest
from single_source_dijkstra import explicit_shortest_path_dijkstra_distance_graph


class testLandmarkAvoidHelper(baseTest):

    def testLandmarkSelectFromScratch(self):
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        distgraph = DistanceGraph(graph)
        num_stars = len(stars)

        distance_labels = np.ones(len(graph)) * float('+inf')
        distance_labels[source] = 0
        actual_distances, actual_parents = explicit_shortest_path_dijkstra_distance_graph(distgraph, source,
                                                                                      distance_labels)
        lobound = np.zeros(num_stars, dtype=float)
        expected_weights = actual_distances
        actual_weights = LandmarkAvoidHelper.calc_weights(actual_distances, lobound)

        self.assertEqual(list(expected_weights), list(actual_weights), "Unexpected from-scratch node weights")

        expected_sizes = [7439, 980, 787, 263, 285, 306, 1125, 283, 7133, 5577, 145, 2064, 1476, 283, 252, 1958, 166,
                          687, 1686, 607, 875, 151, 213, 655, 1127, 223, 497, 482, 751, 263, 353, 255, 273, 253, 236,
                          238, 239]
        actual_sizes = LandmarkAvoidHelper.calc_sizes(actual_weights, actual_parents, [])
        self.assertEqual(list(expected_sizes), list(actual_sizes), "Unexpected from-scratch node sizes")

        expected_landmark = 30
        actual_landmark = LandmarkAvoidHelper.traverse_sizes(actual_sizes, source, actual_parents)
        self.assertEqual(expected_landmark, actual_landmark, "Unexpected new landmark choice")

        # Now verify subtrees containing existing landmarks get their sizes zeroed
        contains_landmark = [0, 8, 9, 11, 12, 18, 23, 30]
        for item in contains_landmark:
            expected_sizes[item] = 0

        actual_sizes = LandmarkAvoidHelper.calc_sizes(actual_weights, actual_parents, [actual_landmark])
        self.assertEqual(list(expected_sizes), list(actual_sizes), "Unexpected second-pass node sizes")

    def _setup_graph(self, sourcefile):
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector
        args = self._make_args()
        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, False)
        galaxy.output_path = args.output
        galaxy.generate_routes()
        galaxy.trade.calculate_components()
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        return graph, source, stars
