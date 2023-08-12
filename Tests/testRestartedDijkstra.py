import argparse
import json
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.single_source_dijkstra import single_source_dijkstra


class MyTestCase(unittest.TestCase):
    def test_from_single_node(self):
        sourcefile = 'DeltaFiles/Zarushagar-Ibara.sec'
        jsonfile = 'PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # pick source
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        self.assertIsNotNone(source.component, "Source component not set")

        # seed expected distances
        with open(jsonfile, 'r') as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars if item.component == source.component]
        for item in component:
            exp_dist = 0
            if str(item) in expected_string:
                exp_dist = expected_string[str(item)]
            expected_distances[item] = exp_dist

        actual_distances, paths, _ = single_source_dijkstra(graph, source)
        self.assertEqual(37, len(actual_distances), "Unexpected number of stars in shortest-path tree")
        self.assertEqual(37, len(paths), "Unexpected number of star paths in shortest-path tree")

        self.assertEqual(expected_distances, actual_distances)

    def test_regenerate_single_trimmed_leaf(self):
        sourcefile = 'DeltaFiles/Zarushagar-Ibara.sec'
        jsonfile = 'PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # pick source
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        self.assertIsNotNone(source.component, "Source component not set")

        # seed expected distances
        with open(jsonfile, 'r') as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars if item.component == source.component]
        for item in component:
            exp_dist = 0
            if str(item) in expected_string:
                exp_dist = expected_string[str(item)]
            expected_distances[item] = exp_dist

        # generate original SPT
        distances, paths, diagnostics = single_source_dijkstra(graph, source)

        self.assertEqual(43, diagnostics['nodes_expanded'])
        self.assertEqual(43, diagnostics['nodes_queued'])
        self.assertEqual(230, diagnostics['neighbours_checked'])

        # select node and trim inputs to set up for regeneration
        leafnode = stars[30]
        self.assertEqual('New Orlando (Zarushagar 0710)', str(leafnode))
        del distances[leafnode]
        del paths[leafnode]

        # generate frontier node list - those connected to any of the removed nodes
        frontier = list(graph[leafnode].keys())

        # regenerate SPT
        new_distances, new_paths, new_diagnostics = single_source_dijkstra(graph, source, distances=distances, paths=paths, frontier=frontier)

        self.assertEqual(37, len(new_distances), "Unexpected number of stars in shortest-path tree")
        self.assertEqual(37, len(new_paths), "Unexpected number of star paths in shortest-path tree")

        self.assertEqual(expected_distances, new_distances)
        self.assertEqual(4, new_diagnostics['nodes_expanded'])
        self.assertEqual(4, new_diagnostics['nodes_queued'])
        self.assertEqual(10, new_diagnostics['neighbours_checked'])

    def test_regenerate_first_level_intermediate_node(self):
        sourcefile = 'DeltaFiles/Zarushagar-Ibara.sec'
        jsonfile = 'PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        # pick source
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        self.assertIsNotNone(source.component, "Source component not set")

        # seed expected distances
        with open(jsonfile, 'r') as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars if item.component == source.component]
        for item in component:
            exp_dist = 0
            if str(item) in expected_string:
                exp_dist = expected_string[str(item)]
            expected_distances[item] = exp_dist

        # generate original SPT
        distances, paths, diagnostics = single_source_dijkstra(graph, source)

        self.assertEqual(43, diagnostics['nodes_expanded'])
        self.assertEqual(43, diagnostics['nodes_queued'])
        self.assertEqual(230, diagnostics['neighbours_checked'])

        # select node and trim inputs to set up for regeneration
        subnode = stars[30]
        leafnode = stars[23]
        self.assertEqual('Toulon-Cadiz (Zarushagar 0510)', str(leafnode))
        droplist = {subnode, leafnode}
        del distances[leafnode]
        del distances[subnode]
        del paths[leafnode]
        del paths[subnode]

        # generate frontier node list - those connected to any of the removed nodes
        toptier = set(graph[leafnode].keys())
        subtier = set(graph[subnode].keys())
        frontier = toptier.union(subtier).difference(droplist)

        # regenerate SPT
        new_distances, new_paths, new_diagnostics = single_source_dijkstra(graph, source, distances=distances, paths=paths, frontier=frontier)

        self.assertEqual(37, len(new_distances), "Unexpected number of stars in shortest-path tree")
        self.assertEqual(37, len(new_paths), "Unexpected number of star paths in shortest-path tree")

        self.assertEqual(expected_distances, new_distances)
        self.assertEqual(6, new_diagnostics['nodes_expanded'])
        self.assertEqual(6, new_diagnostics['nodes_queued'])
        self.assertEqual(22, new_diagnostics['neighbours_checked'])


    def _make_args(self):
        args = argparse.ArgumentParser(description='PyRoute input minimiser.')
        args.btn = 8
        args.max_jump = 2
        args.route_btn = 13
        args.pop_code = 'scaled'
        args.ru_calc = 'scaled'
        args.routes = 'trade'
        args.route_reuse = 10
        args.interestingline = None
        args.interestingtype = None
        args.maps = None
        args.borders = 'range'
        args.ally_match = 'collapse'
        args.owned = False
        args.trade = True
        args.speculative_version = 'CT'
        args.ally_count = 10
        args.json_data = False
        args.output = tempfile.gettempdir()
        return args

if __name__ == '__main__':
    unittest.main()
