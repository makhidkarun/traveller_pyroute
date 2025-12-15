"""
Created on Dec 16, 2025

@author: CyberiaResurrection
"""
import numpy as np

from PyRoute.Pathfinding.single_source_dijkstra import explicit_shortest_path_dijkstra_distance_graph
from Tests.baseTest import baseTest


class testShortestPathDijkstraDistance(baseTest):

    def test_explicit_shortest_path_dijkstra_distance_1(self) -> None:
        msg = None
        try:
            explicit_shortest_path_dijkstra_distance_graph(None, None, None)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('source must be integer', msg)

    def test_explicit_shortest_path_dijkstra_distance_2(self) -> None:
        msg = None
        try:
            explicit_shortest_path_dijkstra_distance_graph(None, 0, None)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('distance labels must be ndarray', msg)

    def test_explicit_shortest_path_dijkstra_distance_3(self) -> None:
        msg = None
        dist_labels = np.array([np.nan], dtype=float)
        try:
            explicit_shortest_path_dijkstra_distance_graph(None, 0, dist_labels)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('distance labels must not be None', msg)

    def test_explicit_shortest_path_dijkstra_distance_4(self) -> None:
        msg = None
        dist_labels = np.array([-1], dtype=float)
        try:
            explicit_shortest_path_dijkstra_distance_graph(None, 0, dist_labels)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('All distance labels must be non-negative', msg)

    def test_explicit_shortest_path_dijkstra_distance_5(self) -> None:
        msg = None
        dist_labels = np.array([0], dtype=float)
        try:
            explicit_shortest_path_dijkstra_distance_graph(None, 0, dist_labels)
        except ValueError as e:
            msg = str(e)
        self.assertEqual('At least one distance label must be nonzero', msg)
