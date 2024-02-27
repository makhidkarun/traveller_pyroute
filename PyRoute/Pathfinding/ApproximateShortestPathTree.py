"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
from PyRoute.Pathfinding.single_source_dijkstra import implicit_shortest_path_dijkstra_indexes
from PyRoute.Star import Star


class ApproximateShortestPathTree:
    __slots__ = '_source', '_graph', '_epsilon', '_divisor', '_distances', '_sources', '_seeds'

    def __init__(self, source, graph, epsilon, sources=None):
        seeds, source = self._get_sources(graph, source, sources)

        self._source = source
        self._epsilon = epsilon
        # memoising this because its value gets used _heavily_ in lower bound calcs, called during heuristic generation
        self._divisor = 1 / (1 + epsilon)
        self._sources = sources
        self._seeds = seeds

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
            seeds = [source]
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
            if isinstance(sources, dict):
                seeds = sources.values()
            else:
                seeds = sources
        return seeds, source

    def lower_bound(self, source, target):
        raise NotImplementedError("Base Class")

    def update_edges(self, edges):
        raise NotImplementedError("Base Class")

    def lighten_edge(self, u, v, weight):
        raise NotImplementedError("Base Class")

    def lower_bound_bulk(self, active_nodes, target):
        raise NotImplementedError("Base Class")

    def is_well_formed(self):
        return True
