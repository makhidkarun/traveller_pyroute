"""
Created on Sep 23, 2023

@author: CyberiaResurrection

Thanks to @GamesByDavidE for original prototype and design discussions
"""
import numpy as np

from PyRoute.Pathfinding.DistanceBase import DistanceBase


class DistanceGraph(DistanceBase):

    def __init__(self, graph):
        super().__init__(graph)
        self._arcs = [
            (np.array(graph.adj[u]), np.array([data['weight'] for data in list(graph.adj[u].values())], dtype=float))
            for u in self._nodes
        ]
        self._min_cost = np.zeros(len(self._nodes))
        for i in range(0, len(self._nodes)):
            node_edges = self._arcs[i][1]
            if 0 < len(node_edges):
                self._min_cost[i] = min(node_edges)

    def lighten_edge(self, u, v, weight):
        self._lighten_arc(u, v, weight)
        self._lighten_arc(v, u, weight)
        self._min_cost[u] = min(self._min_cost[u], weight)
        self._min_cost[v] = min(self._min_cost[v], weight)
