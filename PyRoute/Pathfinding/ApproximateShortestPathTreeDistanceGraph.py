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
        super().__init__(source, graph, epsilon, sources)
        self._graph = DistanceGraph(graph)
        distances = np.ones(len(graph)) * float('+inf')
        for seed in self._seeds:
            distances[seed] = 0

        self._distances = implicit_shortest_path_dijkstra_distance_graph(self._graph, self._source, distances, seeds=self._seeds, divisor=self._divisor)

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
            # Given distance labels, L, on nodes u and v, assuming u's label being smaller,
            # and edge cost between u and v of d(u, v):
            # L(u) + d(u, v) <= L(v)
            # Or, after rearranging,
            # d(u, v) <= L(v) - L(u)
            # u and v do _NOT_ have to be shortest-path parent/child for this bound to hold

            # Allowing an approximation tolerance of epsilon (say 0.1), that bound becomes
            # d(u, v) * (1 + epsilon) <= L(v) - L(u)

            # If that bound no longer holds, it's due to the edge (u, v) having its weight decreased during pathfinding.
            # Tag each incident node as needing updates.

            if delta >= weight:
                dropnodes.add(left)
                dropnodes.add(right)

        # if no nodes are to be dropped, nothing to do - bail out
        if 0 == len(dropnodes):
            return

        # Now we have the nodes incident to edges that bust the (1+eps) approximation bound, feed them into restarted
        # dijkstra to update the approx-SP tree/forest.  Some nodes in dropnodes may well be SP descendants of others,
        # but it wasn't worth the time or complexity cost to filter them out here.
        self._distances = implicit_shortest_path_dijkstra_distance_graph(self._graph, self._source,
                                                                         distance_labels=self._distances,
                                                                         seeds=dropnodes, divisor=self._divisor)

    def lower_bound(self, source, target):
        return abs(self._distances[source] - self._distances[target])

    def lower_bound_bulk(self, active_nodes, target):
        result = np.abs(self._distances[active_nodes] - self._distances[target])
        return result

    def lighten_edge(self, u, v, weight):
        self._graph.lighten_edge(u, v, weight)
