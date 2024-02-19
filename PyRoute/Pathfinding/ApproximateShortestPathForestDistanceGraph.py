"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
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
