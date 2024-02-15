"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
from PyRoute.Pathfinding.single_source_dijkstra import implicit_shortest_path_dijkstra_indexes
from PyRoute.Star import Star


class ApproximateShortestPathTree:
    __slots__ = '_source', '_graph', '_epsilon', '_divisor', '_distances', '_sources'

    def __init__(self, source, graph, epsilon, sources=None):
        seeds, source = self._get_sources(graph, source, sources)

        self._source = source
        self._graph = graph
        self._epsilon = epsilon
        # memoising this because its value gets used _heavily_ in lower bound calcs, called during heuristic generation
        self._divisor = 1 / (1 + epsilon)
        self._sources = sources

        # now we're all set up, seed the approximate-SP tree/forest (tree with seeds in 1 component, forest otherwise)
        self._distances = implicit_shortest_path_dijkstra_indexes(self._graph, self._source, seeds=seeds)

    def _get_sources(self, graph, source, sources):
        seeds = None
        if isinstance(source, Star) and source.component is None:
            raise ValueError(
                "Source node " + str(source) + " has undefined component.  Has calculate_components() been run?")
        if isinstance(source, int):
            if 'star' not in graph.nodes[source]:
                raise ValueError("Source node # " + str(source) + " does not have star attribute")
            if graph.nodes[source]['star'].component is None:
                raise ValueError(
                    "Source node " + str(graph.nodes[source][
                                             'star']) + " has undefined component.  Has calculate_components() been run?")
        if sources is not None:
            for source in sources:
                if isinstance(source, Star) and sources[source].component is None:
                    raise ValueError("Source node " + str(
                        sources[source]) + " has undefined component.  Has calculate_components() been run?")
                if isinstance(source, int):
                    if 'star' not in graph.nodes[source]:
                        raise ValueError("Source node # " + str(source) + " does not have star attribute")
                    if graph.nodes[source]['star'].component is None:
                        raise ValueError(
                            "Source node " + str(graph.nodes[source][
                                                     'star']) + " has undefined component.  Has calculate_components() been run?")
            seeds = sources.values()
        return seeds, source

    def lower_bound(self, source, target):
        left = self._distances[source]
        right = self._distances[target]
        return abs(left - right)

    def update_edges(self, edges):
        dropnodes = set()
        for item in edges:
            left = item[0]
            right = item[1]
            leftdist = self._distances[left]
            rightdist = self._distances[right]
            weight = self._graph[left][right]['weight']
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
        self._distances = implicit_shortest_path_dijkstra_indexes(self._graph, self._source, distance_labels=self._distances, seeds=dropnodes)

    def lighten_edge(self, u, v, weight):
        pass

    def is_well_formed(self):
        return True
