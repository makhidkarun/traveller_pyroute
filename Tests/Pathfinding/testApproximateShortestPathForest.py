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

from PyRoute.Pathfinding.LandmarkSchemes.LandmarksTriaxialExtremes import LandmarksTriaxialExtremes
from PyRoute.Pathfinding.LandmarkSchemes.LandmarksWTNExtremes import LandmarksWTNExtremes
from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathForest import ApproximateShortestPathForest
from PyRoute.Pathfinding.ApproximateShortestPathForestDistanceGraph import ApproximateShortestPathForestDistanceGraph
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from Tests.baseTest import baseTest


class testApproximateShortestPathForest(baseTest):
    def test_source_only_should_wrap_single_tree(self):
        galaxy = self.set_up_zarushagar_sector()

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)
        self.assertEqual(482, len(approx._distances), "Distances dictionary has unexpected length")

        src = stars[2]
        targ = stars[80]

        expected = 254.167
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

        approx = ApproximateShortestPathForest(source, graph, 0.2)

        src = stars[2]
        targ = stars[80]

        expected = 254.167
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

        approx = ApproximateShortestPathForestDistanceGraph(source, graph, 0.2)

        src = stars[2]
        targ = stars[80]

        expected = 254.167
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

    def test_dict_of_sources_should_wrap_single_tree(self):
        galaxy = self.set_up_zarushagar_sector()

        landmarks = galaxy.trade.get_landmarks(index=True)[0]
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2, sources=landmarks)
        self.assertEqual(496, len(approx._distances), "Distances dictionary has unexpected length")

        src = stars[2]
        targ = stars[80]

        expected = 185.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

        approx = ApproximateShortestPathForest(source, graph, 0.2, sources=landmarks)

        src = stars[2]
        targ = stars[80]

        expected = 185.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

        approx = ApproximateShortestPathForestDistanceGraph(source, graph, 0.2, sources=landmarks)

        src = stars[2]
        targ = stars[80]

        expected = 185.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

    def test_triaxial_bounds_should_wrap_three_trees(self):
        galaxy = self.set_up_zarushagar_sector()

        foo = LandmarksTriaxialExtremes(galaxy)
        landmarks = foo.get_landmarks(index=True)
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForest(source, graph, 0.2, sources=landmarks)
        self.assertEqual(3, len(approx._trees), "Unexpected number of approx-SP trees")

        src = stars[2]
        targ = stars[80]

        expected = 310.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

        approx = ApproximateShortestPathForestDistanceGraph(source, graph, 0.2, sources=landmarks)
        self.assertEqual(3, len(approx._trees), "Unexpected number of approx-SP trees")

        src = stars[2]
        targ = stars[80]

        expected = 310.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

    def test_wtn_bounds_should_wrap_one_trees(self):
        galaxy = self.set_up_zarushagar_sector()

        foo = LandmarksWTNExtremes(galaxy)
        landmarks = foo.get_landmarks(index=True)
        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathForest(source, graph, 0.2, sources=landmarks)
        self.assertEqual(1, len(approx._trees), "Unexpected number of approx-SP trees")

        src = stars[2]
        targ = stars[80]

        expected = 185.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

        approx = ApproximateShortestPathForestDistanceGraph(source, graph, 0.2, sources=landmarks)
        self.assertEqual(1, len(approx._trees), "Unexpected number of approx-SP trees")

        src = stars[2]
        targ = stars[80]

        expected = 185.833
        actual = approx.lower_bound(src, targ)
        self.assertAlmostEqual(expected, actual, 3, "Unexpected lower bound value")

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
