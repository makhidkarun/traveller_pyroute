"""
Created on Dec 16, 2025

@author: CyberiaResurrection
"""
import numpy as np

from PyRoute.DeltaDebug.DeltaDictionary import SectorDictionary, DeltaDictionary
from PyRoute.DeltaDebug.DeltaGalaxy import DeltaGalaxy
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from PyRoute.Pathfinding.single_source_dijkstra_core_fallback import dijkstra_core

from Tests.baseTest import baseTest


class testSingleSourceDijkstraCoreFallback(baseTest):

    def test_dijkstra_core_1(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, 4)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        dist_graph = DistanceGraph(galaxy.stars)
        graph_len = len(dist_graph)

        source = 0
        dist_labels = np.ones((graph_len), dtype=float) * float('+inf')
        dist_labels[source] = 0
        max_labels = np.ones((graph_len), dtype=float) * float('+inf')
        min_cost = dist_graph.min_cost(0, True)

        nu_labels, nu_parents, nu_max, nu_diagnostics = dijkstra_core(dist_graph._arcs, dist_labels, float(1.0 / 1.1),
                                                        [source], max_labels, min_cost)
        exp_labels = [0.0, 158.18181818181816, 199.99999999999997, 222.7272727272727, 241.81818181818178,
                      49.090909090909086, 114.54545454545453, 241.81818181818178, 67.27272727272727, 108.18181818181817,
                      132.72727272727272, 150.0, 216.36363636363637, 241.8181818181818, 90.9090909090909,
                      131.8181818181818, 173.63636363636363, 171.8181818181818, 194.54545454545453, 167.27272727272728,
                      166.36363636363635, 157.27272727272725, 197.27272727272725, 257.27272727272725,
                      172.72727272727272, 246.36363636363637, 213.63636363636363, 157.27272727272725,
                      157.27272727272725, 286.3636363636364, 326.3636363636364, 182.7272727272727, 200.90909090909088,
                      182.7272727272727, 179.99999999999997, 222.7272727272727, 216.36363636363635]
        self.assertEqual(exp_labels, list(nu_labels))
        exp_parents = [-1, 6, 1, 1, 2, 0, 5, 2, 0, 8, 8, 9, 11, 12, 0, 8, 9, 9, 15, 0, 0, 8, 15, 18, 9, 15, 11, 14, 14,
                       17, 26, 27, 27, 28, 28, 28, 24]
        self.assertEqual(exp_parents, list(nu_parents))
        exp_max = [167.27272727272728, 274.5454545454545, 258.1818181818182, float('+inf'), float('+inf'),
                   189.0909090909091, 271.8181818181818, float('+inf'), 206.36363636363637, 271.8181818181818,
                   249.09090909090907, 315.45454545454544, 326.3636363636364, float('+inf'), 207.27272727272725,
                   269.0909090909091, float('+inf'), 286.3636363636364, 357.27272727272725, float('+inf'),
                   float('+inf'), 247.27272727272725, float('+inf'), float('+inf'), 286.3636363636364,
                   float('+inf'), 326.3636363636364, 207.27272727272725, 315.45454545454544,
                   float('+inf'), float('+inf'), float('+inf'), float('+inf'), float('+inf'), float('+inf'),
                   float('+inf'), float('+inf')]
        self.assertEqual(exp_max, list(nu_max))
        exp_diagnostics = {'nodes_exceeded': 3, 'nodes_min_exceeded': 0, 'nodes_processed': 37, 'nodes_queued': 75,
                           'nodes_tailed': 18}
        self.assertEqual(exp_diagnostics, nu_diagnostics)

    def test_dijkstra_core_2(self) -> None:
        msg = None
        try:
            dijkstra_core(None, None, None, None, None, None)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('min_cost must be ndarray', msg)

    def test_dijkstra_core_3(self) -> None:
        msg = None
        array = np.ones(1)
        try:
            dijkstra_core(None, None, None, None, None, array)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('max_neighbour_labels must be ndarray', msg)

    def test_dijkstra_core_4(self) -> None:
        msg = None
        array = np.ones(1)
        try:
            dijkstra_core(None, None, None, None, array, array)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('distance_labels must be ndarray', msg)

    def test_dijkstra_core_5(self) -> None:
        msg = None
        array = np.ones(1)
        try:
            dijkstra_core(None, array, None, None, array, array)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('divisor must be float', msg)

    def test_dijkstra_core_6(self) -> None:
        msg = None
        array = np.ones(1)
        try:
            dijkstra_core(None, array, 0.0, None, array, array)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('divisor must be positive and <= 1.0', msg)

    def test_dijkstra_core_7(self) -> None:
        msg = None
        array = np.ones(1)
        try:
            dijkstra_core(None, array, 1.001, None, array, array)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('divisor must be positive and <= 1.0', msg)

    def test_dijkstra_core_8(self) -> None:
        sourcefile = self.unpack_filename('DeltaFiles/Zarushagar-Ibara.sec')

        sector = SectorDictionary.load_traveller_map_file(sourcefile)
        delta = DeltaDictionary()
        delta[sector.name] = sector

        args = self._make_args()

        galaxy = DeltaGalaxy(args.btn, 1)
        galaxy.read_sectors(delta, args.pop_code, args.ru_calc,
                            args.route_reuse, args.routes, args.route_btn, args.mp_threads, args.debug_flag)
        galaxy.output_path = args.output

        galaxy.generate_routes()
        dist_graph = DistanceGraph(galaxy.stars)
        graph_len = len(dist_graph)

        source = 0
        dist_labels = np.ones((graph_len), dtype=float) * float('+inf')
        dist_labels[source] = 0
        max_labels = np.ones((graph_len), dtype=float) * float('+inf')
        min_cost = dist_graph.min_cost(0, True)

        _, nu_parents, _, _ = dijkstra_core(dist_graph._arcs, dist_labels, 1.0, [source], max_labels, min_cost)
        exp_parents = [-1, -100, -100, -100, -100, 0, 9, -100, 5, 15, 15, 10, -100, -100, 8, 21, 15, 11, 17, 14, 14, 20,
                       17, -100, 25, 22, 22, -100, -100, 26, -100, -100, -100, -100, -100, -100, -100]
        self.assertEqual(exp_parents, list(nu_parents))
