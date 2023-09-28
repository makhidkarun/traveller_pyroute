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
            (np.array(graph.adj[u]), np.array([data['weight'] for data in list(graph.adj[u].values())], dtype=float))
            for u in self._nodes
        ]


    def lighten_edge(self, u, v, weight):
        self._lighten_arc(u, v, weight)
        self._lighten_arc(v, u, weight)

    def _lighten_arc(self, u, v, weight):
        arcs = self._arcs[u]
        flip = arcs[0] == v
        if flip.any():
            arcs[1][flip] = weight
        else:
            assert False
