import json
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from Tests.baseTest import baseTest
from PyRoute.Pathfinding.single_source_dijkstra import implicit_shortest_path_dijkstra_distance_graph,\
    explicit_shortest_path_dijkstra_distance_graph
import numpy as np


class testShortestPathCalc(baseTest):

    def test_shortest_path_by_distance_graph(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = self.unpack_filename('PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        graph, source, stars = self._setup_graph(sourcefile)
        distgraph = DistanceGraph(graph)

        # seed expected distances
        with open(jsonfile, 'r', encoding="utf-8") as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars]
        for item in component:
            exp_dist = 0.0
            rawstar = graph.nodes[item]['star']
            if str(rawstar) in expected_string:
                exp_dist = expected_string[str(rawstar)]
            expected_distances[item] = exp_dist

        expected_distances[19] = 175
        distance_labels = np.ones(len(graph)) * float('+inf')
        distance_labels[source] = 0.0
        actual_distances, _ = implicit_shortest_path_dijkstra_distance_graph(distgraph, source, distance_labels)

        self.assertEqual(list(expected_distances.values()), list(actual_distances), "Unexpected distances after SPT creation")

    def test_shortest_explicit_path_by_distance_graph(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = self.unpack_filename('PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        graph, source, stars = self._setup_graph(sourcefile)
        distgraph = DistanceGraph(graph)

        # seed expected distances
        with open(jsonfile, 'r', encoding="utf-8") as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars]
        for item in component:
            exp_dist = 0.0
            rawstar = graph.nodes[item]['star']
            if str(rawstar) in expected_string:
                exp_dist = expected_string[str(rawstar)]
            expected_distances[item] = exp_dist

        expected_distances[19] = 175.0
        distance_labels = np.ones(len(graph)) * float('+inf')
        distance_labels[source] = 0.0
        expected_parents = np.ones(len(graph), dtype=int) * -1
        expected_parents[1] = 6
        expected_parents[2] = 1
        expected_parents[3] = 2
        expected_parents[4] = 2
        expected_parents[5] = 0
        expected_parents[6] = 9
        expected_parents[7] = 12
        expected_parents[8] = 0
        expected_parents[9] = 8
        expected_parents[10] = 9
        expected_parents[11] = 9
        expected_parents[12] = 18
        expected_parents[13] = 12
        expected_parents[14] = 5
        expected_parents[15] = 9
        expected_parents[16] = 9
        expected_parents[17] = 15
        expected_parents[18] = 11
        expected_parents[19] = 8
        expected_parents[20] = 8
        expected_parents[21] = 14
        expected_parents[22] = 11
        expected_parents[23] = 12
        expected_parents[24] = 15
        expected_parents[25] = 24
        expected_parents[26] = 17
        expected_parents[27] = 19
        expected_parents[28] = 24
        expected_parents[29] = 26
        expected_parents[30] = 23
        expected_parents[31] = 27
        expected_parents[32] = 34
        expected_parents[33] = 34
        expected_parents[34] = 24
        expected_parents[35] = 24
        expected_parents[36] = 24
        actual_distances, actual_parents, _ = explicit_shortest_path_dijkstra_distance_graph(distgraph, source, distance_labels)

        self.assertEqual(list(expected_distances.values()), list(actual_distances), "Unexpected distances after SPT creation")
        self.assertEqual(list(expected_parents), list(actual_parents), "Unexpected parent relations")

    def test_masked_gubbins(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        graph, _, _ = self._setup_graph(sourcefile)

        expected_parents = np.ones(len(graph), dtype=int) * -1
        expected_parents[1] = 6
        expected_parents[2] = 1
        expected_parents[3] = 2
        expected_parents[4] = 2
        expected_parents[5] = 0
        expected_parents[6] = 9
        expected_parents[7] = 12
        expected_parents[8] = 0
        expected_parents[9] = 8

        items = np.array(range(37), dtype=int)
        mask = items > 6

        hiver = np.ma.array(expected_parents, mask=mask)

        self.assertEqual(9, max(hiver), "Unexpected max value in masked array")
        expected_parents[6] = 0
        self.assertEqual(6, max(hiver), "Unexpected max value in masked array after original max clobbered")

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


if __name__ == '__main__':
    unittest.main()
