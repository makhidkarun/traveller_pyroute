"""
Created on Feb 25, 2024

@author: CyberiaResurrection
"""
import numpy as np
import networkx as nx

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.RouteLandmarkGraph import RouteLandmarkGraph
from Tests.baseTest import baseTest


class testRouteLandmarkGraph(baseTest):

    def test_subscript_bad(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        num_stars = len(stars)

        rlg = RouteLandmarkGraph(graph)
        self.assertEqual(num_stars, len(rlg))

        cases = [
            ('Non-integer', 'rhubarb'),
            ('Integer too low', -1),
            ('Integer too high', 37)
        ]

        for msg, input_val in cases:
            with self.subTest(msg):
                with self.assertRaises(IndexError) as ex:
                    _ = rlg[input_val]
                self.assertEqual('Index must be integer between 0 and 36', ex.exception.args[0])

    def test_subscript_empty(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        num_stars = len(stars)

        rlg = RouteLandmarkGraph(graph)
        self.assertEqual(num_stars, len(rlg))

        actual = rlg[1]

        self.assertTrue(isinstance(actual, tuple), "Subscript call should return tuple")
        self.assertEqual(2, len(actual), "Subscript call should return 2-tuple")
        self.assertTrue(isinstance(actual[0], np.ndarray), "First tuple element should be ndarray")
        self.assertTrue(isinstance(actual[1], np.ndarray), "Second tuple element should be ndarray")
        self.assertEqual(np.dtype('int64'), actual[0].dtype, "First tuple element type should be int64")
        self.assertEqual(np.dtype('float64'), actual[1].dtype, "Second tuple element type should be int64")
        self.assertEqual(0, len(actual[0]), "First tuple element should be empty")
        self.assertEqual(0, len(actual[1]), "Second tuple element should be empty")

    def test_add_single_then_subscript_nonempty(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        num_stars = len(stars)

        rlg = RouteLandmarkGraph(graph)
        self.assertEqual(num_stars, len(rlg))

        rlg.add_edge(1, 4, 11)

        actual = rlg[1]
        self.assertEqual(1, len(actual[0]), "u - First tuple element should have one element")
        self.assertEqual(1, len(actual[1]), "u - Second tuple element should have one element")
        self.assertEqual([4], actual[0], "u - index nodelist not updated")
        self.assertEqual([11], actual[1], "u - value list not updated")

        actual = rlg[4]
        self.assertEqual(1, len(actual[0]), "v - First tuple element should have one element")
        self.assertEqual(1, len(actual[1]), "v - Second tuple element should have one element")
        self.assertEqual([1], actual[0], "v - index nodelist not updated")
        self.assertEqual([11], actual[1], "v - value list not updated")

    def test_add_single_edge_twice_should_update_in_place(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        num_stars = len(stars)

        rlg = RouteLandmarkGraph(graph)
        self.assertEqual(num_stars, len(rlg))

        rlg.add_edge(1, 4, 11)
        rlg.add_edge(1, 4, 7.5)

        actual = rlg[1]
        self.assertEqual(1, len(actual[0]), "u - First tuple element should have one element")
        self.assertEqual(1, len(actual[1]), "u - Second tuple element should have one element")
        self.assertEqual([4], actual[0], "u - index nodelist not updated")
        self.assertEqual([7.5], actual[1], "u - value list not updated")

        actual = rlg[4]
        self.assertEqual(1, len(actual[0]), "v - First tuple element should have one element")
        self.assertEqual(1, len(actual[1]), "v - Second tuple element should have one element")
        self.assertEqual([1], actual[0], "v - index nodelist not updated")
        self.assertEqual([7.5], actual[1], "v - value list not updated")

    def test_verify_position_creation(self):
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')
        graph, source, stars = self._setup_graph(sourcefile)
        num_stars = len(stars)

        rlg = RouteLandmarkGraph(graph)
        self.assertEqual(num_stars, len(rlg))
        positions = rlg._positions
        self.assertEqual(len(rlg), len(positions), "Should be one position per node")

        raw_nodes = graph.nodes()
        targstar = raw_nodes[11]['star']

        targ_distances = rlg.distances_from_target(11)
        self.assertEqual(len(rlg), len(targ_distances), "Should be one distance-to-target per node")

        for i in range(len(rlg)):
            candstar = raw_nodes[i]['star']
            exp_dist = targstar.distance(candstar)
            self.assertEqual(exp_dist, targ_distances[i], "Unexpected to-target distance for " + str((candstar, i)))

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
        return graph, source, stars
