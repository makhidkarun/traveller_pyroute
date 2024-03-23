"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
import numpy as np


from PyRoute.Pathfinding.ApproximateShortestPathForest import ApproximateShortestPathForest
from PyRoute.Pathfinding.ApproximateShortestPathTreeDistanceGraph import ApproximateShortestPathTreeDistanceGraph


class ApproximateShortestPathForestDistanceGraph(ApproximateShortestPathForest):

    def __init__(self, source, graph, epsilon, sources=None):
        self._trees = []

        if sources is None:
            nu_tree = ApproximateShortestPathTreeDistanceGraph(source, graph, epsilon)
            self._trees.append(nu_tree)
        elif isinstance(sources, dict):
            nu_tree = ApproximateShortestPathTreeDistanceGraph(source, graph, epsilon, sources=sources)
            self._trees.append(nu_tree)
        elif isinstance(sources, list):
            for landmarks in sources:
                nu_tree = ApproximateShortestPathTreeDistanceGraph(source, graph, epsilon, sources=landmarks)
                self._trees.append(nu_tree)

        assert 0 < len(self._trees), "No approx-SP trees generated"

    def lower_bound_bulk(self, active_nodes, target):
        result = np.zeros(len(active_nodes))
        for tree in self._trees:
            interim = tree.lower_bound_bulk(active_nodes, target)
            result = np.maximum(result, interim)

        return result

    def triangle_upbound(self, source, target):
        result = 0
        for tree in self._trees:
            interim = tree.triangle_upbound(source, target)
            result = np.maximum(result, interim)

        return result