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

        distances = copy.deepcopy(self._distances)
        paths = copy.deepcopy(self._paths)
        parent = copy.deepcopy(self._parent)

        for node in nodedrop:
            del distances[node]
            del paths[node]
            del parent[node]
            if node in frontier:
                frontier.remove(node)

        kids = self._build_children(parent)

        # final pass - children of frontier nodes that haven't been dropped are frontier nodes themselves
        parent = set()
        extend = set()
        for node in frontier:
            for kid in self._kids[node]:
                if kid not in nodedrop:
                    extend.add(kid)

        while 0 < len(extend):
            for item in extend:
                frontier.add(item)
            parent = extend
            extend = set()
            for node in parent:
                for item in self._kids[node]:
                    if item not in nodedrop and item not in frontier:
                        extend.add(item)

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

    def _build_parents(self, source):
        self._parent = dict()
        self._parent[source] = None
        for path in self._paths:
            route = self._paths[path]
            for i in range(1, len(route)):
                if route[i] not in self._parent:
                    self._parent[route[i]] = route[i - 1]
