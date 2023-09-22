"""
Created on Sep 23, 2023

@author: CyberiaResurrection

Thanks to @GamesByDavidE for original prototype and design discussions
"""
import numpy as np


class DistanceGraph:

    def __init__(self, graph):
        self._nodes = list(graph.nodes())
        self._indexes = {node: i for (i, node) in enumerate(self._nodes)}
        self._arcs = [
            [
                (self._indexes[v], graph.get_edge_data(u, v)["weight"])
                for v in graph.neighbors(u)
            ]
            for u in self._nodes
        ]


    def lighten_edge(self, u, v, weight):
        self._lighten_arc(u, v, weight)
        self._lighten_arc(v, u, weight)

    def _lighten_arc(self, u, v, weight):
        arcs = self._arcs[u]
        for i, (x, _) in enumerate(arcs):
            if x == v:
                arcs[i] = (v, weight)
                break
        else:
            assert False
