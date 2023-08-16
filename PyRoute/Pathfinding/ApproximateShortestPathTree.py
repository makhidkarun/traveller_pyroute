"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import copy

import networkx as nx

from PyRoute.Pathfinding.single_source_dijkstra import single_source_dijkstra, implicit_shortest_path_dijkstra


class ApproximateShortestPathTree:

    def __init__(self, source, graph, epsilon):
        if source.component is None:
            raise ValueError("Source node " + str(source) + " has undefined component.  Has calculate_components() been run?")

        self._source = source
        self._graph = graph
        self._epsilon = epsilon

        self._distances = implicit_shortest_path_dijkstra(self._graph, self._source)

    def lower_bound(self, source, target):
        if self._source.component != source.component:
            return 0

        left = self._distances[source]
        right = self._distances[target]
        big = max(left, right)
        little = min(left, right)

        bound = max(0, big / (1 + self._epsilon) - little)
        return bound

    def update_edges(self, edges):
        dropnodes = set()
        for item in edges:
            left = item[0]
            right = item[1]
            if self._source.component != left.component:
                continue
            leftdist = self._distances[left]
            rightdist = self._distances[right]
            weight = self._graph[left][right]['weight']
            delta = abs(leftdist - rightdist)
            # check if (1+eps) approximation is busted
            if delta >= (1 + self._epsilon) * weight:
                dropnodes.add(left)
                dropnodes.add(right)

        # if no nodes are to be dropped, nothing to do - bail out
        if 0 == len(dropnodes):
            return

        self._distances = implicit_shortest_path_dijkstra(self._graph, self._source, distance_labels=self._distances, seeds=dropnodes)

    def is_well_formed(self):
        return True
