"""
Created on Aug 08, 2023

@author: CyberiaResurrection
"""
import copy

import networkx as nx

from PyRoute.Pathfinding.single_source_dijkstra import single_source_dijkstra


class ApproximateShortestPathTree:

    def __init__(self, source, graph, epsilon):
        self._source = source
        self._graph = graph
        self._epsilon = epsilon

        self._distances, self._paths, self._diag = single_source_dijkstra(self._graph, self._source)
        self._build_parents(source)
        self._kids = ApproximateShortestPathTree._build_children(self._parent)
        self.is_well_formed()

    def lower_bound(self, source, target):
        left = self._distances[source]
        right = self._distances[target]
        big = max(left, right)
        little = min(left, right)

        bound = max(0, big / (1 + self._epsilon) - little)
        return bound

    def drop_nodes(self, nodes_to_drop):
        # need to verify partition

        nodedrop = {item for item in nodes_to_drop if item.component == self._source.component}
        parent = nodedrop.copy()
        extend = set()
        frontier = set()

        for node in parent:
            parnode = self._parent[node]
            if parnode is not None:
                frontier.add(parnode)
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

        # now nodedrop is populated, properly populate restart
        for node in nodedrop:
            nodes_to_add = (k for k in self._graph[node].keys() if k not in nodedrop and k not in frontier)
            for item in nodes_to_add:
                frontier.add(item)

        distances = dict()
        for node in self._distances:
            if node not in nodedrop:
                distances[node] = self._distances[node]

        parent = dict()
        for node in self._parent:
            if node not in nodedrop:
                parent[node] = self._parent[node]

        paths = dict()
        for node in self._paths:
            if node not in nodedrop:
                chunk = []
                chunk.extend(self._paths[node])
                paths[node] = chunk

        for node in nodedrop:
            if node in frontier:
                frontier.remove(node)

        kids = self._build_children(parent)

        # final pass - children of frontier nodes that haven't been dropped are frontier nodes themselves
        gather = set()
        extend = set()
        for node in frontier:
            for kid in self._kids[node]:
                if kid not in nodedrop and kid not in frontier:
                    extend.add(kid)

        while 0 < len(extend):
            for item in extend:
                frontier.add(item)
            gather = extend
            extend = set()
            for node in gather:
                for item in self._kids[node]:
                    if item not in nodedrop and item not in frontier:
                        extend.add(item)
                nodes_to_add = (k for k in self._graph[node].keys() if k not in nodedrop and k not in frontier)
                for item in nodes_to_add:
                    extend.add(item)

        if self._source in frontier:
            frontier = set()
            frontier.add(self._source)
            distances = {self._source: 0}
            paths = {self._source: [self._source]}
            parent = {self._source: None}
            kids = {self._source: []}

        ApproximateShortestPathTree._check_frontier(parent, frontier)

        return distances, paths, parent, kids, frontier

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

    def update_edges(self, edges):
        dropnodes = []
        for item in edges:
            left = item[0]
            right = item[1]
            leftdist = self._distances[left]
            rightdist = self._distances[right]
            weight = self._graph[left][right]['weight']
            delta = abs(leftdist - rightdist)
            # check if (1+eps) approximation is busted
            if delta >= (1 + self._epsilon) * weight:
                # if left is right's parent
                if left == self._parent[right]:
                    dropnodes.append(right)
                # if right is left's parent
                elif right == self._parent[left]:
                    dropnodes.append(left)
                else:
                    dropnodes.append(left)
                    dropnodes.append(right)

        # if no nodes are to be dropped, nothing to do - bail out
        if 0 == len(dropnodes):
            return

        distances, paths, parent, kids, frontier = self.drop_nodes(dropnodes)

        self._distances, self._paths, self._diag = single_source_dijkstra(self._graph, self._source, distances=distances, frontier=frontier, paths=paths)
        self._build_parents(self._source)
        self._kids = ApproximateShortestPathTree._build_children(self._parent)

    def _build_parents(self, source):
        self._parent = dict()
        self._parent[source] = None
        for path in self._paths:
            route = self._paths[path]
            for i in range(1, len(route)):
                if route[i] not in self._parent:
                    self._parent[route[i]] = route[i - 1]

    def is_well_formed(self):
        # for each node, all of its children should have it as parent
        for parent in self._parent:
            for kid in self._kids[parent]:
                assert parent == self._parent[kid], "Parent-child mismatch between " + str(parent) + " and " + str(kid)
        return True

    @staticmethod
    def _check_frontier(parents, frontier):
        for node in parents:
            parnode = parents[node]
            if node not in frontier and parnode is not None:
                assert parnode not in frontier, "Non-frontier node " + str(node) + " has frontier parent " + str(parnode)

        return True
