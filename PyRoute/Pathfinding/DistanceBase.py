"""
Created on Feb 25, 2024

@author: CyberiaResurrection
"""
import numpy as np


class DistanceBase:

    def __init__(self, graph):
        self._nodes = list(graph.nodes())
        self._indexes = {node: i for (i, node) in enumerate(self._nodes)}

    def __len__(self):
        return len(self._nodes)

    def lighten_edge(self, u, v, weight):
        raise NotImplementedError("Base Class")
