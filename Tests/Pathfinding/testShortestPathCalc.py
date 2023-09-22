import json
import unittest

from DeltaDictionary import SectorDictionary, DeltaDictionary
from DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest
from single_source_dijkstra import implicit_shortest_path_dijkstra_indexes


class testShortestPathCalc(baseTest):
    def test_shortest_path_by_dijkstra(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = self.unpack_filename('PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        graph, source, stars = self._setup_graph(sourcefile)

        # seed expected distances
        with open(jsonfile, 'r') as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars if graph.nodes[item]['star'].component == graph.nodes[source]['star'].component]
        for item in component:
            exp_dist = 0
            rawstar = graph.nodes[item]['star']
            if str(rawstar) in expected_string:
                exp_dist = expected_string[str(rawstar)]
            expected_distances[item] = exp_dist

        actual_distances = implicit_shortest_path_dijkstra_indexes(graph, source)

        self.assertEqual(expected_distances, actual_distances, "Unexpected distances after SPT creation")

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
