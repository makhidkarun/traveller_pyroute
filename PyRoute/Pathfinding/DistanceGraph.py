"""
Created on Sep 23, 2023

@author: CyberiaResurrection

Thanks to @GamesByDavidE for original prototype and design discussions
"""
import copy

import numpy as np
from networkx.classes import Graph

from PyRoute.Pathfinding.DistanceBase import DistanceBase


class DistanceGraph(DistanceBase):

    __slots__ = '_arcs', '_positions', '_nodes', '_indexes', '_min_cost', '_min_indirect'

    def __init__(self, graph: Graph):
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

    def min_cost(self, target: int, indirect: bool = False) -> np.ndarray:
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

    def lighten_edge(self, u: int, v: int, weight: float) -> None:
        if v not in self._arcs[u][2]:
            assert False
        self._lighten_arc(u, v, weight)
        self._lighten_arc(v, u, weight)
        if weight < self._min_cost[u]:
            self._min_cost[u] = weight
        if weight < self._min_cost[v]:
            self._min_cost[v] = weight

        self._min_indirect[self._arcs[u][0]] = np.fmin(self._min_indirect[self._arcs[u][0]], weight)
        self._min_indirect[self._arcs[v][0]] = np.fmin(self._min_indirect[self._arcs[v][0]], weight)
