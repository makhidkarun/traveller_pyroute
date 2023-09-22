"""
Created on Sep 21, 2023

@author: CyberiaResurrection
"""
import functools

from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree


class ApproximateShortestPathTreeZeroCaching(ApproximateShortestPathTree):

    def __init__(self, source, graph, epsilon, sources=None):
        super(ApproximateShortestPathTreeZeroCaching, self).__init__(source, graph, 0, sources)

    @functools.cache
    def lower_bound(self, source, target):
        return super(ApproximateShortestPathTreeZeroCaching, self).lower_bound(source, target)

    def update_edges(self, edges):
        raise UnboundLocalError("Pointless when caching")
