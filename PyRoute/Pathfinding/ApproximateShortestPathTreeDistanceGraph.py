"""
Created on Sep 23, 2023

@author: CyberiaResurrection
"""
import numpy as np
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from PyRoute.Pathfinding.single_source_dijkstra import implicit_shortest_path_dijkstra_distance_graph


class ApproximateShortestPathTreeDistanceGraph(ApproximateShortestPathTree):

    def __init__(self, source, graph, epsilon, sources=None):
        seeds, source = self._get_sources(graph, source, sources)

        self._source = source
        self._graph = DistanceGraph(graph)
        self._epsilon = epsilon
        # memoising this because its value gets used _heavily_ in lower bound calcs, called during heuristic generation
        self._divisor = 1 / (1 + epsilon)
        self._sources = sources

        distances = np.ones(len(graph)) * float('+inf')
        for seed in seeds:
            distances[seed] = 0

        self._distances = implicit_shortest_path_dijkstra_distance_graph(self._graph, self._source, distances, seeds=seeds)

    def update_edges(self, edges):
        dropnodes = set()
        for item in edges:
            left = item[0]
            right = item[1]
            leftdist = self._distances[left]
            rightdist = self._distances[right]
            shelf = self._graph._arcs[left]
            keep = shelf[0] == right
            weight = shelf[1][keep][0]
            delta = abs(leftdist - rightdist)

            if delta >= (1 + self._epsilon) * weight:
                dropnodes.add(left)
                dropnodes.add(right)

        # if no nodes are to be dropped, nothing to do - bail out
        if 0 == len(dropnodes):
            return

        self._distances = implicit_shortest_path_dijkstra_distance_graph(self._graph, self._source,
                                                                         distance_labels=self._distances,
                                                                         seeds=dropnodes)

    def lighten_edge(self, u, v, weight):
        self._graph.lighten_edge(u, v, weight)
