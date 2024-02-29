"""
Created on Feb 25, 2024

@author: CyberiaResurrection
"""


class DistanceBase:

    def __init__(self, graph):
        self._nodes = list(graph.nodes())
        self._indexes = {node: i for (i, node) in enumerate(self._nodes)}

    def __len__(self):
        return len(self._nodes)

    def lighten_edge(self, u, v, weight):
        raise NotImplementedError("Base Class")

    def _lighten_arc(self, u, v, weight):
        arcs = self._arcs[u]
        flip = arcs[0] == v
        if flip.any():
            arcs[1][flip] = weight
        else:
            assert False
