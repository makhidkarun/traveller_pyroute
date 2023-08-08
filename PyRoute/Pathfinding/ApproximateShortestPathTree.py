"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import copy

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
        self._kids = ApproximateShortestPathTree._build_children(self._parent)

    def lower_bound(self, source, target):
        left = self._distances[source]
        right = self._distances[target]
        big = max(left, right)
        little = min(left, right)

        bound = max(0, big / (1 + self._epsilon) - little)
        return bound

    def drop_nodes(self, nodes_to_drop):
        nodedrop = {item for item in nodes_to_drop if item.component == self._source.component}
        parent = nodedrop.copy()
        extend = set()

        for node in parent:
            for item in self._kids[node]:
                extend.add(item)

        while 0 < len(extend):
            for item in extend:
                nodedrop.add(item)
            parent = extend
            extend = set()
            for node in parent:
                for item in self._kids[node]:
                    extend.add(item)

        distances = copy.deepcopy(self._distances)
        paths = copy.deepcopy(self._paths)
        parent = copy.deepcopy(self._parent)

        for node in nodedrop:
            del distances[node]
            del paths[node]
            del parent[node]

        kids = self._build_children(parent)

        return distances, paths, parent, kids

    @staticmethod
    def _build_children(parents):
        kids = dict()
        for parent in parents:
            kid = parents[parent]
            if kid is None:
                continue
            if kid not in kids:
                kids[kid] = set()
            if parent not in kids:
                kids[parent] = set()
            kids[kid].add(parent)

        return kids