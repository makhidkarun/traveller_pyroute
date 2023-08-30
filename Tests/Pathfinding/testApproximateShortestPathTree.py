"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import argparse
import copy
import json
import os
import tempfile
import unittest

import networkx as nx

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree


class testApproximateShortestPathTree(unittest.TestCase):
    def test_lower_bound_doesnt_overlap(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar.sec')


        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)
        self.assertEqual(482, len(approx._distances), "Distances dictionary has unexpected length")

        src = stars[2]
        targ = stars[80]

        expected = 540 / 1.2 - 239
        actual = approx.lower_bound(src, targ)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

    def test_lower_bound_does_overlap(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar.sec')


        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)

        src = stars[20]
        targ = stars[19]

        expected = 0
        actual = approx.lower_bound(src, targ)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

    def test_lower_bound_self_to_self(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar.sec')


        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)

        src = stars[2]

        expected = 0
        actual = approx.lower_bound(src, src)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

    def test_drop_first_level_intermediate_nodes_in_same_component(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)
        # verify that all distances as at ctor are finite
        distances = approx._distances
        old_num = len(distances)
        for node in distances:
            self.assertFalse(distances[node] == float('+inf'), "SPT distance for " + str(node) + " not finite")

        # auxiliary network dijkstra calculation to dish out parent nodes
        paths = nx.single_source_dijkstra_path(graph, source)

        leaf = [item for item in stars if -1 != graph.nodes[item]['star'].name.find('Dorsiki')][0]
        leafpath = paths[leaf]
        inter = leafpath[-2]

        edges = [(leaf, inter)]

        approx.update_edges(edges)
        self.assertEqual(old_num, len(approx._distances))

    def test_drop_third_level_intermediate_nodes_in_same_component_and_regenerate(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar.sec')


        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)

        # auxiliary network dijkstra calculation to dish out parent nodes
        paths = nx.single_source_dijkstra_path(graph, source)

        leaf = [item for item in stars if -1 != graph.nodes[item]['star'].name.find('Dorsiki')][0]
        leafpath = paths[leaf]
        mid = leafpath[-2]
        hi = leafpath[-3]
        inter = leafpath[-4]

        edges = [(inter, hi)]

        approx.update_edges(edges)
        self.assertEqual(482, len(approx._distances))

    def test_verify_changed_leaf_edge_trip_update(self):
        sourcefile = '../DeltaFiles/Zarushagar-Ibara.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar-Ibara.sec')

        jsonfile = '../PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'
        if not os.path.isfile(jsonfile):
            jsonfile = os.path.abspath('../Tests/PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars

        stars = list(graph.nodes)
        source = stars[0]
        distances, paths = nx.single_source_dijkstra(graph, source)
        leafnode = stars[30]
        subnode = stars[paths[leafnode][-2]]

        approx = ApproximateShortestPathTree(source, graph, 0)

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

        self.assertEqual(expected_distances, approx._distances, "Unexpected distances after SPT creation")

        # adjust weight
        galaxy.stars[subnode][leafnode]['weight'] -= 1

        # tell SPT weight has changed
        edge = (subnode, leafnode)
        approx.update_edges([edge])

        # verify update tripped
        self.assertEqual(expected_distances[leafnode] - 1, approx._distances[leafnode], "Leaf node distance not updated")

    def test_verify_near_root_edge_propagates(self):
        sourcefile = '../DeltaFiles/Zarushagar-Ibara.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = '../PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'
        if not os.path.isfile(jsonfile):
            jsonfile = os.path.abspath('../Tests/PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')


        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        leafnode = stars[30]

        approx = ApproximateShortestPathTree(source, graph, 0)

        # auxiliary network dijkstra calculation to dish out parent nodes
        paths = nx.single_source_dijkstra_path(graph, source)
        right = paths[leafnode][1]

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

        self.assertEqual(expected_distances, approx._distances, "Unexpected distances after SPT creation")

        # adjust weight
        galaxy.stars[source][right]['weight'] -= 1

        # tell SPT weight has changed
        edge = (source, right)
        dropnodes = [right]

        for item in expected_distances:
            if expected_distances[item] > 0 and 'Selsinia (Zarushagar 0201)' != str(graph.nodes[item]['star']):
                expected_distances[item] -= 1

        approx.update_edges([edge])

        self.assertEqual(expected_distances, approx._distances, "Unexpected distances after SPT restart")

    def test_verify_multiple_near_root_edges_propagate(self):
        sourcefile = '../DeltaFiles/dijkstra_restart_blowup/Lishun.sec'
        if not os.path.isfile(sourcefile):
            sourcefile = os.path.abspath('../Tests/DeltaFiles/dijkstra_restart_blowup/Lishun.sec')


        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[4]

        approx = ApproximateShortestPathTree(source, graph, 0)


        edges = [(stars[3], stars[2]), (stars[2], source)]

        for item in edges:
            graph[item[0]][item[1]]['weight'] *= 0.9

        approx.update_edges(edges)



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
