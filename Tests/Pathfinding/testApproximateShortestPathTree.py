"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import argparse
import copy
import json
import tempfile
import unittest

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from PyRoute.Pathfinding.relaxed_single_source_dijkstra import relaxed_single_source_dijkstra
from PyRoute.Pathfinding.single_source_dijkstra import single_source_dijkstra


class testApproximateShortestPathTree(unittest.TestCase):
    def test_lower_bound_doesnt_overlap(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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

        distances, paths, parent, _, _ = approx.drop_nodes(dropnodes)
        self.assertEqual(old_distances, distances)
        self.assertEqual(old_paths, paths)
        self.assertEqual(old_parent, parent)

    def test_drop_nodes_leaf_in_same_component(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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

        distances, paths, parent, kids, restart = approx.drop_nodes(leaves)
        self.assertEqual(481, len(distances))
        self.assertEqual(481, len(paths))
        self.assertEqual(481, len(parent))
        self.assertEqual(481, len(kids))
        self.assertNotIn(leaves[0], distances, "Leaf node not removed from distances")
        self.assertNotIn(leaves[0], paths, "Leaf node not removed from paths")
        self.assertNotIn(leaves[0], parent, "Leaf node not removed from parent")
        self.assertNotIn(leaves[0], kids, "Leaf node not removed from kids")

    def test_drop_first_level_intermediate_nodes_in_same_component(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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

        distances, paths, parent, kids, restart = approx.drop_nodes(dropnodes)
        self.assertEqual(479, len(distances))
        self.assertEqual(479, len(paths))
        self.assertEqual(479, len(parent))
        self.assertEqual(479, len(kids))

        for node in check:
            self.assertNotIn(node, distances, "Node " + str(node) + " not removed from distances")
            self.assertNotIn(node, paths, "Node " + str(node) + " not removed from paths")
            self.assertNotIn(node, parent, "Node " + str(node) + " not removed from parent")
            self.assertNotIn(node, kids, "Node " + str(node) + " not removed from kids")

    def test_drop_third_level_intermediate_nodes_in_same_component_and_regenerate(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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
            num_check = len(check)
            scratch = set()
            for item in check:
                for kid in approx._kids[item]:
                    scratch.add(kid)

            for item in scratch:
                check.add(item)

        dropnodes = [inter]

        distances, paths, parent, kids, restart = approx.drop_nodes(dropnodes)
        self.assertEqual(475, len(distances))
        self.assertEqual(475, len(paths))
        self.assertEqual(475, len(parent))
        self.assertEqual(475, len(kids))
        self.assertEqual(1, len(restart))

        for node in check:
            self.assertNotIn(node, distances, "Node " + str(node) + " not removed from distances")
            self.assertNotIn(node, paths, "Node " + str(node) + " not removed from paths")
            self.assertNotIn(node, parent, "Node " + str(node) + " not removed from parent")
            self.assertNotIn(node, kids, "Node " + str(node) + " not removed from kids")

        new_distances, new_paths, new_diagnostics = single_source_dijkstra(graph, source, distances=distances,
                                                                           paths=paths, frontier=restart)
        self.assertEqual(482, len(new_distances), "Removed node distances should be added by restart")
        self.assertEqual(482, len(new_paths), "Removed node paths should be added by restart")

    def test_recurrently_dropped_nodes_dont_turn_up_in_restart(self):
        sourcefile = '../DeltaFiles/Zarushagar.sec'

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

        dropnodes = [inter, hi, mid, leaf]

        _, _, _, _, restart = approx.drop_nodes(dropnodes)
        self.assertEqual(1, len(restart), "Restart nodes shouldn't be parents of other restart nodes")

    def test_verify_changed_leaf_edge_trip_update(self):
        sourcefile = '../DeltaFiles/Zarushagar-Ibara.sec'
        jsonfile = '../PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'

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
        leafnode = stars[30]
        subnode = stars[23]

        approx = ApproximateShortestPathTree(source, graph, 0)
        expected_diag = {'neighbours_checked': 115, 'nodes_expanded': 43, 'nodes_queued': 43}
        self.assertEqual(expected_diag, approx._diag, "Unexpected diagnostics dict")

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

        self.assertEqual(expected_distances, approx._distances, "Unexpected distances after SPT creation")

        # adjust weight
        galaxy.stars[subnode][leafnode]['weight'] -= 1

        # tell SPT weight has changed
        edge = (subnode, leafnode)
        approx.update_edges([edge])

        # verify update tripped
        self.assertNotEqual(expected_diag, approx._diag, "Diagnostics dict did not change")
        self.assertEqual(expected_distances[leafnode] - 1, approx._distances[leafnode], "Leaf node distance not updated")
        expected_diag = {'neighbours_checked': 1, 'nodes_expanded': 2, 'nodes_queued': 2}
        self.assertEqual(expected_diag, approx._diag, "Unexpected diagnostics dict")

    def test_verify_near_root_edge_propagates(self):
        sourcefile = '../DeltaFiles/Zarushagar-Ibara.sec'
        jsonfile = '../PathfindingFiles/single_source_distances_ibara_subsector_from_0101.json'

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
        leafnode = stars[30]

        approx = ApproximateShortestPathTree(source, graph, 0)

        right = approx._paths[leafnode][1]

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

        self.assertEqual(expected_distances, approx._distances, "Unexpected distances after SPT creation")

        # adjust weight
        galaxy.stars[source][right]['weight'] -= 1

        # tell SPT weight has changed
        edge = (source, right)
        dropnodes = [right]

        for item in expected_distances:
            if expected_distances[item] > 0 and 'Selsinia (Zarushagar 0201)' != str(item):
                expected_distances[item] -= 1

        # verify frontier generation
        _, _, _, kids, frontier = approx.drop_nodes(dropnodes)
        self.assertEqual(4, len(frontier), "Unexpected frontier set size")

        approx.update_edges([edge])

        self.assertEqual(expected_distances, approx._distances, "Unexpected distances after SPT restart")

    def test_verify_multiple_near_root_edges_propagate(self):
        sourcefile = '../DeltaFiles/dijkstra_restart_blowup/Lishun.sec'

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
