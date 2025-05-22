"""
Created on Sep 23, 2023

@author: CyberiaResurrection

Thanks to @GamesByDavidE for original prototype and design discussions
"""
import copy

import numpy as np

from PyRoute.Pathfinding.DistanceBase import DistanceBase


class DistanceGraph(DistanceBase):

    __slots__ = '_arcs', '_positions', '_nodes', '_indexes', '_min_cost', '_min_indirect'

    def __init__(self, graph):
        super().__init__(graph)
        self._arcs = [
            (
                np.array(graph.adj[u], dtype=int),
                np.array([data['weight'] for data in list(graph.adj[u].values())], dtype=float),
                {v: k for (k, v) in enumerate(list(graph.adj[u].keys()))}
            )
            for u in self._nodes
        ]
        self._min_cost = np.zeros(len(self._nodes))
        self._min_indirect = np.zeros(len(self._nodes))
        for i in range(0, len(self._nodes)):
            node_edges = self._arcs[i][1]
            if 0 < len(node_edges):
                self._min_cost[i] = min(node_edges)
        for i in range(0, len(self._nodes)):
            node_neighbours = self._arcs[i][0]
            if 0 < len(node_neighbours):
                self._min_indirect[i] = min(self._min_cost[node_neighbours])

    def min_cost(self, target, indirect=False):
        min_cost = copy.deepcopy(self._min_cost)
        min_cost[target] = 0

        if indirect is not True:
            return min_cost

        min_indirect = copy.deepcopy(self._min_indirect)
        neighbours = self._arcs[target][0]  # Skip neighbours of target and target itself in the indirect leg
        min_indirect[target] = 0
        min_indirect[neighbours] = 0

        min_cost += min_indirect

        return min_cost

    def lighten_edge(self, u, v, weight):
        neighbours = self._arcs[u][0]
        if not (neighbours == v).any():
            assert False

        self._lighten_arc(u, v, weight)
        self._lighten_arc(v, u, weight)
        self._min_cost[u] = min(self._min_cost[u], weight)
        self._min_cost[v] = min(self._min_cost[v], weight)

        self._min_indirect[neighbours] = np.fmin(self._min_indirect[neighbours], weight)
        neighbours = self._arcs[v][0]
        self._min_indirect[neighbours] = np.fmin(self._min_indirect[neighbours], weight)
