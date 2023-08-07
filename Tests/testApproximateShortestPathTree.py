"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import argparse
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree


class MyTestCase(unittest.TestCase):
    def test_lower_bound_doesnt_overlap(self):
        sourcefile = 'DeltaFiles/Zarushagar.sec'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)
        self.assertTrue(isinstance(approx._parent, dict), "Parent-tree dictionary not generated")
        # In this case, giant component has 482 stars, so parent tree should have the same
        self.assertEqual(len(approx._paths), len(approx._parent), "Parent-tree dictionary has unexpected length")

        src = stars[2]
        targ = stars[80]

        expected = 540 / 1.2 - 239
        actual = approx.lower_bound(src, targ)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

    def test_lower_bound_does_overlap(self):
        sourcefile = 'DeltaFiles/Zarushagar.sec'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)

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
        sourcefile = 'DeltaFiles/Zarushagar.sec'

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, args.max_jump, args.route_btn)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc)
        galaxy.output_path = args.output

        galaxy.generate_routes(args.routes, args.route_reuse)

        graph = galaxy.stars
        stars = list(graph.nodes)
        source = stars[0]

        approx = ApproximateShortestPathTree(source, graph, 0.2)

        src = stars[2]

        expected = 0
        actual = approx.lower_bound(src, src)
        self.assertEqual(expected, actual, "Unexpected lower bound value")

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
