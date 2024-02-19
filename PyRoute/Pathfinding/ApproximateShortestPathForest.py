"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree


class ApproximateShortestPathForest:

    def __init__(self, source, graph, epsilon, sources=None):
        self._trees = []

        if sources is None:
            nu_tree = ApproximateShortestPathTree(source, graph, epsilon)
            self._trees.append(nu_tree)

    def lower_bound(self, source, target):
        bound = 0
        for tree in self._trees:
            nu_bound = tree.lower_bound(source, target)
            if nu_bound > bound:
                bound = nu_bound
        return bound

    def update_edges(self, edges):
        for tree in self._trees:
            tree.update_edges(edges)

    def lighten_edge(self, u, v, weight):
        for tree in self._trees:
            tree.lighten_edge(u, v, weight)

    def is_well_formed(self):
        for tree in self._trees:
            result = tree.is_well_formed()
            if not result:
                return False
        return True
