"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import networkx as nx


class ApproximateShortestPathTree:

    def __init__(self, source, graph, epsilon):
        self._source = source
        self._graph = graph
        self._epsilon = epsilon

        self._distances, self._paths = nx.single_source_dijkstra(self._graph, self._source)
        self._parent = dict()
        self._parent[source] = None
        for path in self._paths:
            route = self._paths[path]
            for i in range(1, len(route)):
                if route[i] not in self._parent:
                    self._parent[route[i]] = route[i-1]

    def lower_bound(self, source, target):
        left = self._distances[source]
        right = self._distances[target]
        big = max(left, right)
        little = min(left, right)

        bound = max(0, big / (1 + self._epsilon) - little)
        return bound
