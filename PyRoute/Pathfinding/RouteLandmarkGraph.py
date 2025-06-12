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
            (np.array([], dtype=int), np.array([], dtype=float), dict())
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
        arcs = self._arcs[u]
        u_dict = arcs[2]
        if v not in u_dict:
            u_dict[v] = len(u_dict)
            u_first = np.append(arcs[0], [v], 0)
            u_last = np.append(arcs[1], [weight], 0)
            self._arcs[u] = (u_first, u_last, u_dict)
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
