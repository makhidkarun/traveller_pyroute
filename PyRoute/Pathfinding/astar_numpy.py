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
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
import networkx as nx
import numpy as np
import typing
from _heapq import heappop, heappush, heapify


@cython.cdivision(True)
def _calc_branching_factor(nodes_queued: cython.int, path_len: cython.int):
    old: cython.float
    new: cython.float
    rhs: cython.float
    power: cython.float
    if path_len == nodes_queued or 1 > path_len or 1 > nodes_queued:
        return 1.0

    power = 1.0 / path_len
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

    old = 0.0
    new = 0.5 * (1 + nodes_queued ** (power))
    while 0.001 <= abs(new - old):
        old = new
        rhs = nodes_queued * new - nodes_queued + new
        new = rhs ** (power)

    return round(new, 3)


@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.wraparound(False)
def astar_path_numpy(G, source: cython.int, target: cython.int, bulk_heuristic,
                     min_cost: typing.Optional[cnp.ndarray[cython.float]] = None,
                     upbound=None, diagnostics: cython.bint = False):
    G_succ: list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]]
    potentials: cnp.ndarray[cython.float]
    len_G: cython.int
    floatinf: cython.float
    upbound: cython.float
    distances: cnp.ndarray[cython.float]
    G_succ = G._arcs  # For speed-up

    # pre-calc heuristics for all nodes to the target node
    potentials = bulk_heuristic(target)

    # Length of graph G
    len_G = len(G)

    # Tracks shortest _complete_ path found so far
    upbound = np.finfo(np.float64).max if upbound is None else upbound
    # Traces lowest distance from source node found for each node
    distances = np.ones(len_G) * float('inf')

    # pre-calc the minimum-cost edge on each node
    min_cost = np.zeros(len_G) if min_cost is None else min_cost
    bestpath, diag = astar_numpy_core(G_succ, diagnostics, distances, min_cost, potentials, source, target, upbound)

    if 0 == len(bestpath):
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
    return bestpath, diag


@cython.cfunc
@cython.infer_types(True)
@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
def astar_numpy_core(G_succ: list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]], diagnostics: cython.bint,
                     distances: cnp.ndarray[cython.float], min_cost: cnp.ndarray[cython.float],
                     potentials: cnp.ndarray[cython.float], source: cython.int, target: cython.int,
                     upbound: cython.float):
    min_cost[target] = 0.0
    upper_limit: cnp.ndarray[cython.float] = upbound - min_cost
    upper_limit_view: cython.double[:] = upper_limit
    upper_limit_view[source] = 0.0
    distances_view: cython.double[:] = distances
    distances_view[source] = 0.0
    potentials_view: cython.double[:] = potentials

    node_counter: cython.int = 0
    queue_counter: cython.int = 0
    revisited: cython.int = 0
    g_exhausted: cython.int = 0
    f_exhausted: cython.int = 0
    new_upbounds: cython.int = 0
    targ_exhausted: cython.int = 0
    revis_continue: cython.int = 0
    path: list[cython.int] = []
    diag = {}

    act_nod: cython.int
    act_wt: cython.float

    dist: cython.float
    curnode: cython.int
    parent: cython.int
    counter: cython.int

    # Maps explored nodes to parent closest to the source.
    explored: dict[cython.int, cython.int] = {}

    # The queue stores priority, cost to reach, node,  and parent.
    # Uses Python heapq to keep in priority order.
    # The nodes themselves, being integers, are directly comparable.
    queue = [(potentials_view[source], 0.0, source, -1)]

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
                return path, diag
            branch = _calc_branching_factor(queue_counter, len(path) - 1)
            neighbour_bound = node_counter - 1 + revis_continue - revisited
            un_exhausted = neighbour_bound - f_exhausted - g_exhausted - targ_exhausted
            diag = {'nodes_expanded': node_counter, 'nodes_queued': queue_counter, 'branch_factor': branch,
                           'num_jumps': len(path) - 1, 'nodes_revisited': revisited, 'neighbour_bound': neighbour_bound,
                           'new_upbounds': new_upbounds, 'g_exhausted': g_exhausted, 'f_exhausted': f_exhausted,
                           'un_exhausted': un_exhausted, 'targ_exhausted': targ_exhausted}
            return path, diag

        if curnode in explored:
            revisited += 1
            # Do not override the parent of starting node
            if explored[curnode] == -1:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost = distances_view[curnode]
            if qcost <= dist:
                queue = [item for item in queue if not (item[1] > upper_limit_view[item[2]])]
                heapify(queue)
                continue
            # If we've found a better path, update
            revis_continue += 1
            distances_view[curnode] = dist

        explored[curnode] = parent

        raw_nodes = G_succ[curnode]
        active_nodes = raw_nodes[0]
        active_weights = dist + raw_nodes[1]
        # Even if we have the target node as a candidate neighbour, of itself, that's _no_ guarantee that the target
        # as neighbour will give a better upper bound.
        keep = active_weights <= upper_limit[active_nodes]
        active_nodes = active_nodes[keep]
        active_weights = active_weights[keep]
        if 0 == len(active_nodes):
            g_exhausted += 1
            continue

        targdex = -1

        for i in range(len(active_nodes)):
            act_nod = active_nodes[i]
            if act_nod == target:
                targdex = i
                break

        if -1 != targdex:
            upbound = active_weights[targdex]
            new_upbounds += 1
            distances_view[target] = upbound
            upper_limit = np.minimum(upper_limit, upbound - min_cost)
            upper_limit_view = upper_limit

            # heappush(queue, (ncost + 0, ncost, target, curnode))
            heappush(queue, (upbound, upbound, target, curnode))
            queue_counter += 1

            # As we have a tighter upper bound, apply it to the neighbours as well - target will be excluded because
            # its augmented weight is _equal_ to upbound
            keep = active_nodes != target
            active_nodes = active_nodes[keep]
            if 0 == len(active_nodes):
                targ_exhausted += 1
                continue

            active_weights = active_weights[keep]

        # Now unconditionally queue _all_ nodes that are still active, worrying about filtering out the bound-busting
        # neighbours later.
        num_nodes = len(active_nodes)
        counter = 0
        for i in range(num_nodes):
            act_nod = active_nodes[i]
            act_wt = active_weights[i]
            aug_wt = act_wt + potentials_view[act_nod]
            if aug_wt >= upbound:
                continue
            distances_view[act_nod] = act_wt
            upper_limit_view[act_nod] = act_wt
            heappush(queue, (aug_wt, act_wt, act_nod, curnode))
            counter += 1

        if 0 == counter:
            if -1 != targdex:
                targ_exhausted += 1
            else:
                g_exhausted += 1
        else:
            queue_counter += counter

    return path, diagnostics
