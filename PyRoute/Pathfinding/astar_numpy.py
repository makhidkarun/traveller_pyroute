"""
Created on Feb 22, 2024

@author: CyberiaResurrection

Compared to the ancestral networkx version of astar_path, this code:
    Does _not_ use a count() object reference to break ties, as nodes are directly-comparable integers
    Leans on numpy to handle neighbour nodes, edges to same and heuristic values in bulk
    Tracks upper-bounds on shortest-path cost as they are found
    Prunes neighbour candidates early - if this exhausts a node by leaving it no viable neighbour candidates, so be it
    Takes an optional externally-supplied upper bound
        - Sanity and correctness of this upper bound are the _caller_'s responsibility
        - If the supplied upper bound produces a pathfinding failure, so be it
    Grooms the node queue in the following cases:
        When a _longer_ path is found to a previously-queued node, discards queue entries whose g-values bust
            the corresponding node's distance label

"""
import networkx as nx
import numpy as np

from PyRoute.Pathfinding.astar_numpy_core import astar_numpy_core


def astar_path_numpy(G, source, target, bulk_heuristic, min_cost=None, upbound=None, diagnostics=False):

    G_succ = G._arcs  # For speed-up

    # pre-calc heuristics for all nodes to the target node
    potentials = bulk_heuristic(G._nodes, target)

    # Maps explored nodes to parent closest to the source.
    explored = {}
    # Length of graph G
    len_G = len(G)

    # Tracks shortest _complete_ path found so far
    floatinf = float('inf')
    upbound = floatinf if upbound is None else upbound
    assert upbound != floatinf, "Supplied upbound must not be infinite"
    # Traces lowest distance from source node found for each node
    distances = np.ones(len_G) * floatinf

    # pre-calc the minimum-cost edge on each node
    min_cost = np.zeros(len_G) if min_cost is None else min_cost
    bestpath, diag = astar_numpy_core(G_succ, diagnostics, distances, explored, min_cost, potentials, source, target,
                                      upbound)

    if 0 == len(bestpath):
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
    return bestpath, diag
