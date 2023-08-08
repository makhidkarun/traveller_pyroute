"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import argparse
import copy
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

    def test_drop_nodes_not_in_same_component(self):
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
        old_distances = copy.deepcopy(approx._distances)
        old_paths = copy.deepcopy(approx._paths)
        old_parent = copy.deepcopy(approx._parent)

        dropnodes = [item for item in stars if item.component != source.component]

        distances, paths, parent = approx.drop_nodes(dropnodes)
        self.assertEqual(old_distances, distances)
        self.assertEqual(old_paths, paths)
        self.assertEqual(old_parent, parent)

    def test_drop_nodes_leaf_in_same_component(self):
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

        leaves = [item for item in stars if -1 != str(item).find('Dorsiki')]

        distances, paths, parent, kids = approx.drop_nodes(leaves)
        self.assertEqual(481, len(distances))
        self.assertEqual(481, len(paths))
        self.assertEqual(481, len(parent))
        self.assertEqual(481, len(kids))
        self.assertNotIn(leaves[0], distances, "Leaf node not removed from distances")
        self.assertNotIn(leaves[0], paths, "Leaf node not removed from paths")
        self.assertNotIn(leaves[0], parent, "Leaf node not removed from parent")
        self.assertNotIn(leaves[0], kids, "Leaf node not removed from kids")

    def test_drop_first_level_intermediate_nodes_in_same_component(self):
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

        leaf = [item for item in stars if -1 != str(item).find('Dorsiki')][0]
        inter = approx._parent[leaf]

        check = copy.deepcopy(approx._kids[inter])
        check.add(inter)

        dropnodes = [inter]

        distances, paths, parent, kids = approx.drop_nodes(dropnodes)
        self.assertEqual(479, len(distances))
        self.assertEqual(479, len(paths))
        self.assertEqual(479, len(parent))
        self.assertEqual(479, len(kids))

        for node in check:
            self.assertNotIn(node, distances, "Node " + str(node) + " not removed from distances")
            self.assertNotIn(node, paths, "Node " + str(node) + " not removed from paths")
            self.assertNotIn(node, parent, "Node " + str(node) + " not removed from parent")
            self.assertNotIn(node, kids, "Node " + str(node) + " not removed from kids")

    def test_drop_third_level_intermediate_nodes_in_same_component(self):
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

        leaf = [item for item in stars if -1 != str(item).find('Dorsiki')][0]
        mid = approx._parent[leaf]
        hi = approx._parent[mid]
        inter = approx._parent[hi]

        check = set(approx._kids[inter])
        check.add(inter)
        num_check = 0

        while num_check != len(check):
            scratch = set()
            for item in check:
                for kid in approx._kids[item]:
                    scratch.add(kid)

            for item in scratch:
                check.add(item)

        dropnodes = [inter]

        distances, paths, parent, kids = approx.drop_nodes(dropnodes)
        self.assertEqual(475, len(distances))
        self.assertEqual(475, len(paths))
        self.assertEqual(475, len(parent))
        self.assertEqual(475, len(kids))

        for node in check:
            self.assertNotIn(node, distances, "Node " + str(node) + " not removed from distances")
            self.assertNotIn(node, paths, "Node " + str(node) + " not removed from paths")
            self.assertNotIn(node, parent, "Node " + str(node) + " not removed from parent")
            self.assertNotIn(node, kids, "Node " + str(node) + " not removed from kids")

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
