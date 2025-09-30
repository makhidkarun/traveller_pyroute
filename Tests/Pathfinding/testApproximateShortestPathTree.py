"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import argparse
import json
import tempfile
import unittest

import networkx as nx
import numpy as np

try:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
except ModuleNotFoundError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except ImportError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except AttributeError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from Tests.baseTest import baseTest


class testApproximateShortestPathTree(baseTest):
    def test_lower_bound_doesnt_overlap(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2)
        self.assertEqual(496, len(approx.distances), "Distances dictionary has unexpected length")

        src = stars[2]
        targ = stars[80]

        expected = 254.167
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

    def test_lower_bound_does_overlap(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2)

        src = stars[20]
        targ = stars[19]

        expected = 0.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

    def test_lower_bound_self_to_self(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2)

        src = stars[2]

        expected = 0
        actual = approx.lower_bound(src, src)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

    def test_bulk_lower_bound_on_distance_graph(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        approx = ApproximateShortestPathForestUnified(source, graph, 0.2)

        active_nodes = [20, 19, 1]
        target = 1

        result = approx.lower_bound_bulk(target)
        self.assertIsNotNone(result)
        result = result[active_nodes]
        expected = np.array([15.833, 15, 0])
        np.testing.assert_array_almost_equal(expected, result, 0.000001, "Unexpected bounds array")

    def test_drop_first_level_intermediate_nodes_in_same_component(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2)
        # verify that all distances as at ctor are finite
        distances = approx.distances
        old_num = len(distances)

        # auxiliary network dijkstra calculation to dish out parent nodes
        paths = nx.single_source_dijkstra_path(graph, source)

        leaf = [item for item in stars if -1 != graph.nodes[item]['star'].name.find('Dorsiki')][0]
        leafpath = paths[leaf]
        inter = leafpath[-2]

        edges = [(leaf, inter)]

        approx.update_edges(edges)
        self.assertEqual(old_num, len(approx.distances))

    def test_drop_third_level_intermediate_nodes_in_same_component_and_regenerate(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2)

        # auxiliary network dijkstra calculation to dish out parent nodes
        paths = nx.single_source_dijkstra_path(graph, source)

        leaf = [item for item in stars if -1 != graph.nodes[item]['star'].name.find('Dorsiki')][0]
        leafpath = paths[leaf]
        hi = leafpath[-3]
        inter = leafpath[-4]

        edges = [(inter, hi)]

        approx.update_edges(edges)
        self.assertEqual(496, len(approx.distances))

    def test_verify_changed_leaf_edge_trip_update(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = self.unpack_filename('PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars

        stars = list(graph.nodes)
        source = stars[0]
        _, paths = nx.single_source_dijkstra(graph, source)
        leafnode = stars[30]
        subnode = stars[paths[leafnode][-2]]

        approx = ApproximateShortestPathForestUnified(source, graph, 0)

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

        distance_check = list(expected_distances.values()) == approx.distances[:, 0]
        self.assertTrue(distance_check.all(), "Unexpected distances after SPT creation")

        # adjust weight
        oldweight = galaxy.stars[subnode][leafnode]['weight']
        galaxy.stars[subnode][leafnode]['weight'] -= 1
        galaxy.trade.star_graph.lighten_edge(subnode, leafnode, oldweight - 1)
        approx.graph.lighten_edge(subnode, leafnode, oldweight - 1)

        # tell SPT weight has changed
        edge = (subnode, leafnode)
        approx.update_edges([edge])

        # verify update tripped
        self.assertEqual(expected_distances[leafnode] - 1, approx.distances[leafnode], "Leaf node distance not updated")

    def test_verify_near_root_edge_propagates(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = self.unpack_filename('PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        self.assertEqual(37, len(stars))
        source = stars[0]
        leafnode = stars[30]

        approx = ApproximateShortestPathForestUnified(source, graph, 0)

        # auxiliary network dijkstra calculation to dish out parent nodes
        paths = nx.single_source_dijkstra_path(graph, source)
        right = paths[leafnode][1]

        # seed expected distances
        with open(jsonfile, 'r', encoding="utf-8") as file:
            expected_string = json.load(file)

        expected_distances = dict()
        component = [item for item in stars]
        for item in component:
            exp_dist = 0
            rawstar = graph.nodes[item]['star']
            if str(rawstar) in expected_string:
                exp_dist = expected_string[str(rawstar)]
            expected_distances[item] = exp_dist

        distance_check = list(expected_distances.values()) == approx.distances[:, 0]
        self.assertTrue(distance_check.all(), "Unexpected distances after SPT creation")

        # adjust weight
        oldweight = galaxy.stars[source][right]['weight']
        galaxy.stars[source][right]['weight'] -= 1
        galaxy.trade.star_graph.lighten_edge(source, right, oldweight - 1)
        approx.graph.lighten_edge(source, right, oldweight - 1)

        # tell SPT weight has changed
        edge = (source, right)

        for item in expected_distances:
            if expected_distances[item] > 0 and 'Selsinia (Zarushagar 0201)' != str(graph.nodes[item]['star']):
                expected_distances[item] -= 1

        approx.update_edges([edge])

        distance_check = list(expected_distances.values()) == approx.distances[:, 0]
        self.assertTrue(distance_check.all(), "Unexpected distances after SPT restart")

    def test_verify_multiple_near_root_edges_propagate(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/dijkstra_restart_blowup/Lishun.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debugflag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[4]

        approx = ApproximateShortestPathForestUnified(source, graph, 0)

        edges = [(stars[3], stars[2]), (stars[2], source)]

        for item in edges:
            graph[item[0]][item[1]]['weight'] *= 0.9

        approx.update_edges(edges)

    def _make_args(self) -> argparse.ArgumentParser:
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
        args.debugflag = False
        args.mp_threads = 1
        return args


if __name__ == '__main__':
    unittest.main()
