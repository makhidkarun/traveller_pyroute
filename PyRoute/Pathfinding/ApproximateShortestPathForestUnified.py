# cython: profile=True
"""
Created on Feb 29, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
import functools
from typing import Any

import numpy as np
from PyRoute.Star import Star
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
from PyRoute.Pathfinding.single_source_dijkstra import implicit_shortest_path_dijkstra_distance_graph
from single_source_dijkstra_core import dijkstra_core

cnp.import_array()

float64max = np.finfo(np.float64).max


@cython.cclass
class ApproximateShortestPathForestUnified:

    _graph: object
    _source: object
    _epsilon: cython.float
    _divisor: cython.float
    _sources: list
    _seeds: list
    _num_trees: cython.int
    _graph_len: cython.int
    _distances: cython.declare(cnp.ndarray(cython.float, ndim=2), 'readonly')
    _max_labels: cnp.ndarray(cython.float, ndim=2)

    def __init__(self, source, graph, epsilon, sources=None):
        seeds, source, num_trees = self._get_sources(graph, source, sources)
        self._graph = DistanceGraph(graph)
        self._source = source
        self._epsilon = epsilon
        # memoising this because its value gets used _heavily_ in lower bound calcs, called during heuristic generation
        self._divisor = 1 / (1 + epsilon)
        self._sources = sources
        self._seeds = seeds
        self._num_trees = num_trees
        self._graph_len = len(self._graph)
        self._distances = np.ones((self._graph_len, self._num_trees), dtype=float, order='F') * float('+inf')
        self._max_labels = np.ones((self._graph_len, self._num_trees), dtype=float) * float('+inf')

        min_cost = self._graph._min_cost
        # spin up initial distances
        for i in range(self._num_trees):
            raw_seeds = self._seeds[i] if isinstance(self._seeds[i], list) else list(self._seeds[i].values())
            self._distances[raw_seeds, i] = 0
            result = implicit_shortest_path_dijkstra_distance_graph(self._graph, self._source,
                                                                                   self._distances[:, i],
                                                                                   seeds=raw_seeds,
                                                                                   min_cost=min_cost,
                                                                                   divisor=self._divisor)
            self._distances[:, i], self._max_labels[:, i], _ = result

    def lower_bound(self, source, target) -> float:
        raw = np.abs(self._distances[source, :] - self._distances[target, :])
        raw = raw[~np.isinf(raw)]
        if 0 == len(raw):
            return 0
        return np.max(raw)

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    @cython.returns(cnp.ndarray)
    def lower_bound_bulk(self, target_node: cython.int) -> cnp.ndarray:
        raw: cnp.ndarray(cython.float, ndim=2)
        overdrive: cnp.ndarray[cython.bint]
        fastpath: cython.bint
        anypath: cython.bint
        overdrive, fastpath, anypath = self._mona_lisa_overdrive(target_node)

        if fastpath:  # Fastpath - all overdrive elements are _finite_, so all rows are retrieved
            raw = (self._distances - self._distances[target_node, :])
        else:
            # if we haven't got _any_ active lines, throw hands up and spit back zeros
            if not anypath:
                return np.zeros(self._graph_len, dtype=float)
            actives = self._distances[:, overdrive]
            target = self._distances[target_node, overdrive]

            raw = actives - target

        return np.max(np.abs(raw), axis=1)

    def triangle_upbound(self, source: cython.int, target: cython.int) -> float:
        raw: cnp.ndarray[cython.float]
        raw = self._distances[source, :] + self._distances[target, :]
        raw = raw[raw != float('+inf')]

        if 0 == len(raw):
            return float64max / 2

        return np.min(raw) * (1 + self._epsilon)

    #  Gratuitous William Gibson reference is gratuitous.
    @functools.cache
    @cython.cfunc
    def _mona_lisa_overdrive(self, target_node: cython.int) -> tuple[cnp.array[cython.bint], cython.bint, cython.bint]:
        result: cnp.ndarray[cython.bint]
        result = self._distances[target_node, :] != float('+inf')
        return result, result.all(), result.any()

    @cython.ccall
    @cython.infer_types(True)
    @cython.boundscheck(False)
    @cython.initializedcheck(False)
    @cython.nonecheck(False)
    @cython.wraparound(False)
    def update_edges(self, edges: list[tuple[cython.int, cython.int]]):  # noqa: ANN201
        dropnodes = set()
        dropspecific = []
        tree_dex = list(range(self._num_trees))
        targdex: cython.int = -1
        i: cython.int
        min_cost: cnp.ndarray[cython.float]
        shelf: tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]
        floatinf = float('+inf')
        arcs = self._graph._arcs

        for _ in tree_dex:
            dropspecific.append([])
        for item in edges:
            left = item[0]
            right = item[1]
            leftdist = self._distances[left, :]
            rightdist = self._distances[right, :]

            shelf = arcs[left]
            for i in range(len(shelf)):
                if shelf[0][i] == right:
                    targdex = i
                    break
            weight = shelf[1][targdex]
            weight_sq = weight * weight
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
            dropped: cython.bint = False
            for j in tree_dex:
                if floatinf == rightdist[j]:
                    rightdist[j] = 0
                delta = leftdist[j] - rightdist[j]
                if delta * delta >= weight_sq:
                    dropspecific[j].append(left)
                    dropspecific[j].append(right)
                    dropped = True

            if dropped:
                dropnodes.add(left)
                dropnodes.add(right)

        # if no nodes are to be dropped, nothing to do - bail out
        if 0 == len(dropnodes):
            return

        # Now we're updating at least one tree, grab the current min-cost vector to feed into implicit-dijkstra
        min_cost = self._graph._min_cost

        # Now we have the nodes incident to edges that bust the (1+eps) approximation bound, feed them into restarted
        # dijkstra to update the approx-SP tree/forest.  Some nodes in dropnodes may well be SP descendants of others,
        # but it wasn't worth the time or complexity cost to filter them out here.
        for i in tree_dex:
            if 0 == len(dropspecific[i]):
                continue
            self._distances[:, i], _, self._max_labels[:, i], _ = dijkstra_core(
                                                                  arcs,
                                                                  self._distances[:, i],
                                                                  self._divisor,
                                                                  dropspecific[i],
                                                                  self._max_labels[:, i],
                                                                  min_cost)

    def expand_forest(self, nu_seeds) -> None:
        raw_seeds = nu_seeds if isinstance(nu_seeds, list) else list(nu_seeds.values())
        nu_distances = np.ones((self._graph_len)) * float('+inf')
        nu_distances[raw_seeds] = 0
        nu_distances, nu_max_labels, _ = implicit_shortest_path_dijkstra_distance_graph(self._graph, self._source,
                                                                nu_distances,
                                                                seeds=raw_seeds,
                                                                divisor=self._divisor)
        result = np.zeros((self._graph_len, 1), dtype=float)
        result[:, 0] = list(nu_distances)
        maxresult = np.zeros((self._graph_len, 1), dtype=float)
        maxresult[:, 0] = list(nu_max_labels)
        self._distances = np.append(self._distances, result, 1)
        self._max_labels = np.append(self._distances, maxresult, 1)
        self._num_trees += 1

    def _get_sources(self, graph, source, sources):
        seeds = None
        num_trees = 1
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
            seeds = [[source]]
        if sources is not None:
            for src in sources:
                if isinstance(src, Star) and sources[src].component is None:
                    raise ValueError("Source node " + str(
                        sources[src]) + " has undefined component.  Has calculate_components() been run?")
                if isinstance(src, int):
                    if 'star' not in graph.nodes[src]:
                        raise ValueError("Source node # " + str(src) + " does not have star attribute")
                    if graph.nodes[src]['star'].component is None:
                        raise ValueError(
                            "Source node " + str(graph.nodes[src][
                                                     'star']) + " has undefined component.  Has calculate_components() been run?")
            if isinstance(sources, dict):
                seeds = [list(sources.values())]
            else:
                seeds = sources
                num_trees = len(sources)
        return seeds, source, num_trees

    def lighten_edge(self, u, v, weight) -> None:
        self._graph.lighten_edge(u, v, weight)

    @property
    def num_trees(self) -> int:
        return self._num_trees

    @property
    def distances(self) -> cnp.ndarray:
        return self._distances

    @property
    def graph(self) -> object:
        return self._graph

    @property
    def sources(self) -> Any:
        return self._sources
