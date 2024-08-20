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
        When a new upper bound is found, discards queue entries whose f-values bust the new upper bound
        When a _longer_ path is found to a previously-queued node, discards queue entries whose g-values bust
            the corresponding node's distance label

"""
from heapq import heappop, heappush, heapify

import networkx as nx
import numpy as np

from PyRoute.Pathfinding.astar_numpy_core import astar_get_neighbours, astar_process_neighbours


def _calc_branching_factor(nodes_queued, path_len):
    if path_len == nodes_queued:
        return 1.0

    # Letting nodes_queued be S, and path_len be d, we're trying to solve for the value of r in the following:
    # S = r * ( r ^ (d-1) - 1 ) / ( r - 1 )
    # Applying some sixth-grade algebra:
    # Sr - S = r * ( r ^ (d-1) - 1 )
    # Sr - S = r ^ d - r
    # Sr - S + r = r ^ d
    # r ^ d = Sr - S + r
    #
    # That final line is an ideal form to apply fixed-point iteration to, starting with an initial guess for r
    # and feeding it into:
    # r* = (Sr - S + r) ^ (1/d)
    # iterating until r* and r sufficiently converge.

    old = 0
    new = 0.5 * (1 + nodes_queued ** (1 / path_len))
    while 0.001 <= abs(new - old):
        old = new
        rhs = nodes_queued * new - nodes_queued + new
        new = rhs ** (1 / path_len)

    return round(new, 3)


def astar_path_numpy(G, source, target, bulk_heuristic, min_cost=None, upbound=None, diagnostics=False):

    G_succ = G._arcs  # For speed-up

    # pre-calc heuristics for all nodes to the target node
    potentials = bulk_heuristic(G._nodes, target)

    # The queue stores priority, cost to reach, node,  and parent.
    # Uses Python heapq to keep in priority order.
    # The nodes themselves, being integers, are directly comparable.
    queue = [(potentials[source], 0.0, source, -1)]

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
    distances[source] = 0.0

    # pre-calc the minimum-cost edge on each node
    min_cost = np.zeros(len_G) if min_cost is None else min_cost
    min_cost[target] = 0.0
    up_threshold = upbound - min_cost
    upper_limit = up_threshold
    upper_limit[source] = 0.0

    node_counter = 0
    queue_counter = 0
    revisited = 0
    g_exhausted = 0
    f_exhausted = 0
    new_upbounds = 0
    targ_exhausted = 0
    revis_continue = 0

    while queue:
        # Pop the smallest item from queue.
        _, dist, curnode, parent = heappop(queue)
        node_counter += 1

        if curnode == target:
            path = [curnode]
            node = parent
            while node != -1:
                assert node not in path, "Node " + str(node) + " duplicated in discovered path"
                path.append(node)
                node = explored[node]
            path.reverse()
            if diagnostics is not True:
                return path, {}
            branch = _calc_branching_factor(queue_counter, len(path) - 1)
            neighbour_bound = node_counter - 1 + revis_continue - revisited
            un_exhausted = neighbour_bound - f_exhausted - g_exhausted - targ_exhausted
            diagnostics = {'nodes_expanded': node_counter, 'nodes_queued': queue_counter, 'branch_factor': branch,
                           'num_jumps': len(path) - 1, 'nodes_revisited': revisited, 'neighbour_bound': neighbour_bound,
                           'new_upbounds': new_upbounds, 'g_exhausted': g_exhausted, 'f_exhausted': f_exhausted,
                           'un_exhausted': un_exhausted, 'targ_exhausted': targ_exhausted}
            return path, diagnostics

        if curnode in explored:
            revisited += 1
            # Do not override the parent of starting node
            if explored[curnode] == -1:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost = distances[curnode]
            if qcost <= dist:
                queue = [item for item in queue if not (item[1] > distances[item[2]])]
                heapify(queue)
                continue
            # If we've found a better path, update
            revis_continue += 1
            distances[curnode] = dist

        explored[curnode] = parent

        active_nodes, active_weights, augmented_weights, g_exhausted = astar_get_neighbours(G_succ, curnode, dist,
                                                                                            g_exhausted, potentials,
                                                                                            upbound, upper_limit)

        new_upbounds, queue, queue_counter, targ_exhausted, upbound, upper_limit = astar_process_neighbours(
            active_nodes, active_weights, augmented_weights, curnode, distances, min_cost, new_upbounds, queue,
            queue_counter, targ_exhausted, target, upbound, upper_limit)

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
