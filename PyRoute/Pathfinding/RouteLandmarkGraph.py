"""
Created on Feb 25, 2024

@author: CyberiaResurrection
"""
import functools
import numpy as np

from PyRoute.Pathfinding.DistanceBase import DistanceBase


class RouteLandmarkGraph(DistanceBase):

    def __init__(self, graph):
        super().__init__(graph)
        self._arcs = [
            (np.array([], dtype=int), np.array([], dtype=float))
            for u in self._nodes
        ]

    def __getitem__(self, item):
        self._check_index(item)
        return self._arcs[item]

    def add_edge(self, u, v, weight):
        self._check_index(u)
        self._check_index(v)
        self._extend_arc(u, v, weight)
        self._extend_arc(v, u, weight)

    def _extend_arc(self, u, v, weight):
        u_first = self._arcs[u][0]
        u_last = self._arcs[u][1]
        if v not in u_first:
            u_first = np.append(u_first, [v])
            u_last = np.append(u_last, [weight])
            self._arcs[u] = (u_first, u_last)
        else:
            self._lighten_arc(u, v, weight)

    @functools.cache
    def _check_index(self, item):
        if not isinstance(item, int):
            raise IndexError("Index must be integer between 0 and " + str(len(self) - 1))
        if 0 > item:
            raise IndexError("Index must be integer between 0 and " + str(len(self) - 1))
        if len(self) <= item:
            raise IndexError("Index must be integer between 0 and " + str(len(self) - 1))

    def lighten_edge(self, u, v, weight):
        self._lighten_arc(u, v, weight)
        self._lighten_arc(v, u, weight)
