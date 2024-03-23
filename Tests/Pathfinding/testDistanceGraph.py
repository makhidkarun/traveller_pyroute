"""
Created on Mar 19, 2024

@author: CyberiaResurrection
"""
import numpy as np
import networkx as nx

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from Tests.baseTest import baseTest


class testDistanceGraph(baseTest):
    def test_min_cost_in_single_component(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        galaxy, graph, source, stars = self._setup_graph(sourcefile)
        components = galaxy.trade.components
        self.assertEqual(1, len(components))

        distgraph = DistanceGraph(graph)
        expected = [0.0, 46.0, 24.0, 24.0, 26.0, 26.0, 26.0, 26.0, 26.0, 25.0, 26.0, 27.0, 28.0, 28.0, 27.0, 25.0, 28.0,
                    24.0, 24.0, 32.0, 31.0, 29.0, 25.0, 47.0, 32.0, 32.0, 25.0, 28.0, 25.0, 29.0, 51.0, 28.0, 28.0,
                    25.0, 24.0, 24.0, 45.0]
        actual = distgraph.min_cost(range(37), 0)
        self.assertEqual(expected, list(actual), 'Unexpected min-cost vector')

        expected_extended = [0.0, 70.0, 48.0, 48.0, 50.0, 26.0, 51.0, 50.0, 26.0, 50.0, 50.0, 51.0, 52.0, 52.0, 52.0,
                             49.0, 52.0, 48.0, 48.0, 58.0, 56.0, 54.0, 49.0, 75.0, 56.0, 56.0, 49.0, 56.0, 49.0, 54.0,
                             80.0, 53.0, 52.0, 49.0, 48.0, 48.0, 69.0]
        extended = distgraph.min_cost(range(37), 0, indirect=True)
        self.assertEqual(expected_extended, list(extended), 'Unexpected indirect min-cost vector')

        distgraph.lighten_edge(1, 11, 40)
        expected_extended = [0.0, 64.0, 48.0, 48.0, 50.0, 26.0, 51.0, 50.0, 26.0, 50.0, 50.0, 51.0, 52.0, 52.0, 52.0,
                             49.0, 52.0, 48.0, 48.0, 58.0, 56.0, 54.0, 49.0, 75.0, 56.0, 56.0, 49.0, 56.0, 49.0, 54.0,
                             80.0, 53.0, 52.0, 49.0, 48.0, 48.0, 69.0]
        extended = distgraph.min_cost(range(37), 0, indirect=True)
        self.assertEqual(expected_extended, list(extended), 'Unexpected indirect min-cost vector after update')

        distgraph.lighten_edge(1, 11, 10)
        expected_extended = [0.0, 20.0, 34.0, 48.0, 50.0, 26.0, 36.0, 50.0, 26.0, 35.0, 36.0, 20.0, 52.0, 52.0, 52.0,
                             35.0, 38.0, 34.0, 34.0, 58.0, 56.0, 54.0, 35.0, 75.0, 56.0, 56.0, 49.0, 56.0, 49.0, 54.0,
                             80.0, 53.0, 52.0, 49.0, 48.0, 48.0, 69.0]
        extended = distgraph.min_cost(range(37), 0, indirect=True)
        self.assertEqual(expected_extended, list(extended), 'Unexpected indirect min-cost vector after update')

    def test_min_cost_in_multiple_components(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')
        galaxy, graph, source, stars = self._setup_graph(sourcefile)
        components = galaxy.trade.components
        self.assertEqual(8, len(components))

        active_nodes = []

        bitz = nx.connected_components(galaxy.stars)
        for component in bitz:
            if 2 < len(component):
                continue
            active_nodes.extend(component)

        distgraph = DistanceGraph(graph)

        expected = [0.0, 0.0, 0.0, 0.0, 0.0]
        actual = distgraph.min_cost(active_nodes, 0, indirect=True)
        self.assertEqual(expected, list(actual), 'Unexpected indiect min-cost vector')

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
        return galaxy, graph, source, stars
