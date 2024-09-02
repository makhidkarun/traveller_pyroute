"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
import argparse
import copy
import json
import os
import tempfile
import unittest

import networkx as nx
import numpy as np

from PyRoute.Pathfinding.LandmarkSchemes.LandmarksTriaxialExtremes import LandmarksTriaxialExtremes
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksWTNExtremes import LandmarksWTNExtremes
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
from Tests.baseTest import baseTest


class testApproximateShortestPathForest(baseTest):

    def test_trixial_bounds_in_bulk_unified(self):
        galaxy = self.set_up_zarushagar_sector()

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks, _ = foo.get_landmarks(index=True)
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2, sources=landmarks)
        self.assertEqual(9, approx.num_trees)

        active_nodes = [2, 80]
        target = 80
        expected = np.array([420.833, 0])
        actual = approx.lower_bound_bulk(target)
        self.assertIsNotNone(actual)
        actual = actual[active_nodes]

        np.testing.assert_array_almost_equal(expected, actual, 0.000001, "Unexpected bounds array")

    def test_unified_can_handle_singleton_landmarks(self):
        galaxy = self.set_up_zarushagar_sector()

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks, _ = foo.get_landmarks(index=True)
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2, sources=landmarks)
        self.assertEqual(9, approx.num_trees)

    def test_unified_can_handle_bulk_lobound_from_singleton_component(self):
        galaxy = self.set_up_zarushagar_sector()

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks, _ = foo.get_landmarks(index=True)
        graph = galaxy.stars
        source = [item for item in graph if graph.nodes()[item]['star'].component == 0][0]
        targ = [item for item in graph if graph.nodes()[item]['star'].component == 1][0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2, sources=landmarks)

        bulk_lo = approx.lower_bound_bulk(targ)
        # Approx-sp lower bounds to a singleton component should be zero, as they are irrelevant in actual pathfinding
        self.assertEqual(0, max(bulk_lo), "Unexpected lobound")

    def test_unified_can_handle_bulk_lobound_to_singleton_component(self):
        galaxy = self.set_up_zarushagar_sector()

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks, _ = foo.get_landmarks(index=True)
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        targ = [item for item in graph if graph.nodes()[item]['star'].component == 1][0]

        approx = ApproximateShortestPathForestUnified(source, graph, 0.2, sources=landmarks)

        bulk_lo = approx.lower_bound_bulk(source)
        self.assertEqual(float('+inf'), bulk_lo[targ])

    def test_verify_near_root_edge_propagates(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        jsonfile = self.unpack_filename('PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, 1, False)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]
        leafnode = stars[30]

        approx = ApproximateShortestPathForestUnified(source, graph, 0)

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

        distance_check = list(expected_distances.values()) == approx.distances[:,0]
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

    def test_add_tree_to_unified_forest(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, 1, False)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        galaxy.trade.calculate_components()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        seeds = [{0: 1}, {0: 2}, {0: 3}]

        approx = ApproximateShortestPathForestUnified(source, graph, epsilon=0.1, sources=seeds)
        self.assertEqual(3, approx.num_trees)
        oldbound = approx.lower_bound_bulk(source)

        nu_seed = {0: 4}
        approx.expand_forest(nu_seed)

        self.assertEqual(4, approx.num_trees)
        nubound = approx.lower_bound_bulk(source)

        delta = nubound - oldbound
        self.assertGreater(max(delta), 0, "At least one heuristic value should be improved by extra tree")

    def set_up_zarushagar_sector(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar.sec')
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
        return galaxy


if __name__ == '__main__':
    unittest.main()
