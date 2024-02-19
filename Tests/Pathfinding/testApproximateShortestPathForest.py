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

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathForest import ApproximateShortestPathForest
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from Tests.baseTest import baseTest


class testApproximateShortestPathForest(baseTest):
    def test_source_only_should_wrap_single_tree(self):
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

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)
        self.assertEqual(482, len(approx._distances), "Distances dictionary has unexpected length")

        src = stars[2]
        targ = stars[80]

        expected = 540 - 239
        actual = approx.lower_bound(src, targ)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

        approx = ApproximateShortestPathForest(source, graph, 0.2)

        src = stars[2]
        targ = stars[80]

        expected = 540 - 239
        actual = approx.lower_bound(src, targ)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

if __name__ == '__main__':
    unittest.main()
