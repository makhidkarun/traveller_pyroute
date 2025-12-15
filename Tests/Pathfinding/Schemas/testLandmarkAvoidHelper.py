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
from PyRoute.Pathfinding.single_source_dijkstra import explicit_shortest_path_dijkstra_distance_graph


class testLandmarkAvoidHelper(baseTest):

    def testLandmarkSelectFromScratch(self) -> None:
        sourcefile = self.unpack_filename('../DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        distgraph = DistanceGraph(graph)
        num_stars = len(stars)

        distance_labels = np.ones(len(graph)) * float('+inf')
        distance_labels[source] = 0
        actual_distances, actual_parents, _, _ = explicit_shortest_path_dijkstra_distance_graph(distgraph, source,
                                                                                                distance_labels)
        lobound = np.zeros(num_stars, dtype=float)
        expected_weights = actual_distances
        actual_weights = LandmarkAvoidHelper.calc_weights(actual_distances, lobound)

        self.assertEqual(list(expected_weights), list(actual_weights), "Unexpected from-scratch node weights")

        expected_sizes = [7894, 980, 787, 263, 285, 331, 1125, 283, 7563, 6558, 145, 2114, 1526, 283, 277, 2864, 191,
                          737, 1736, 757, 174, 176, 213, 705, 1983, 273, 547, 582, 239, 313, 403, 305, 281, 261, 778,
                          263, 239]
        actual_sizes = LandmarkAvoidHelper.calc_sizes(actual_weights, actual_parents, [])
        self.assertEqual(list(expected_sizes), list(actual_sizes), "Unexpected from-scratch node sizes")

        expected_landmark = 32
        actual_landmark = LandmarkAvoidHelper.traverse_sizes(actual_sizes, source, actual_parents)
        self.assertEqual(expected_landmark, actual_landmark, "Unexpected new landmark choice")

        # Now verify subtrees containing existing landmarks get their sizes zeroed
        contains_landmark = [0, 8, 9, 15, 24, 32, 34]
        for item in contains_landmark:
            expected_sizes[item] = 0.0

        landmarks = [actual_landmark]
        old_mark = [actual_landmark]
        actual_sizes = LandmarkAvoidHelper.calc_sizes(actual_weights, actual_parents, landmarks)
        self.assertEqual(list(expected_sizes), list(actual_sizes), "Unexpected second-pass node sizes")
        self.assertEqual(old_mark, landmarks, "Landmark set unexpectedly altered")

    def _setup_graph(self, sourcefile):
        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        self.assertIsNotNone(sector, "Sector file not loaded from " + sourcefile)
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
