# distutils: language = c++
# cython: profile=True
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


"""
import cython
from cython.cimports.numpy import numpy as cnp
from cython.cimports.minmaxheap import MinMaxHeap, astar_t

import networkx as nx
import numpy as np

cnp.import_array()

float64max = np.finfo(np.float64).max


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
@cython.nonecheck(False)
def astar_path_numpy(G, source: cython.int, target: cython.int, bulk_heuristic,
                     upbound: cython.float = float64max, diagnostics: cython.bint = False):
    G_succ: list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]]
    potentials: cnp.ndarray[cython.float]
    upbound: cython.float
    distances: cnp.ndarray[cython.float]
    G_succ = G._arcs  # For speed-up

    # pre-calc heuristics for all nodes to the target node
    potentials = bulk_heuristic(target)

    # Traces lowest distance from source node found for each node
    distances = np.ones(len(G_succ), dtype=float) * upbound

    bestpath, diag = astar_numpy_core(G_succ, diagnostics, distances, potentials, source, target, upbound)

    if 0 == len(bestpath):
        raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
    return bestpath, diag


@cython.cfunc
@cython.infer_types(True)
@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
@cython.returns(tuple[list[cython.int], dict])
def astar_numpy_core(G_succ: list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]], diagnostics: cython.bint,
                     distances: cnp.ndarray[cython.float], potentials: cnp.ndarray[cython.float], source: cython.int,
                     target: cython.int, upbound: cython.float):
    distances_view: cython.double[:] = distances
    distances_view[source] = 0.0
    potentials_view: cython.double[:] = potentials
    active_nodes_view: cython.long[:]
    active_costs_view: cython.double[:]

    node_counter: cython.int = 0
    queue_counter: cython.int = 0
    revisited: cython.int = 0
    g_exhausted: cython.int = 0
    f_exhausted: cython.int = 0
    nu_upbound: cython.float
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
    queue: MinMaxHeap[astar_t] = MinMaxHeap[astar_t]()
    queue.reserve(500)
    queue.insert({'augment': potentials_view[source], 'dist': 0.0, 'curnode': source, 'parent': -1})

    while 0 < queue.size():
        # Pop the smallest item from queue.
        result = queue.popmin()
        dist = result.dist
        curnode = result.curnode
        parent = result.parent
        node_counter += 1

        if curnode == target:
            path.append(curnode)
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

            # We've found a bad path, just move on
            qcost = distances_view[curnode]
            if qcost <= dist:
                continue
            # If we've found a better path, update
            revis_continue += 1
            distances_view[curnode] = dist

        explored[curnode] = parent

        active_nodes_view = G_succ[curnode][0]
        active_costs_view = G_succ[curnode][1]

        targdex = -1

        num_nodes = len(active_nodes_view)
        for i in range(num_nodes):
            act_nod = active_nodes_view[i]
            if act_nod == target:
                targdex = i
                nu_upbound = dist + active_costs_view[targdex]
                if nu_upbound < upbound:
                    upbound = nu_upbound
                    new_upbounds += 1
                    distances_view[target] = upbound
                break

        # Now unconditionally queue _all_ nodes that are still active, worrying about filtering out the bound-busting
        # neighbours later.
        counter = 0
        for i in range(num_nodes):
            act_nod = active_nodes_view[i]
            act_wt = dist + active_costs_view[i]
            if act_wt > distances_view[act_nod]:
                continue
            aug_wt = act_wt + potentials_view[act_nod]
            if aug_wt > upbound:
                continue
            distances_view[act_nod] = act_wt
            queue.insert({'augment': aug_wt, 'dist': act_wt, 'curnode': act_nod, 'parent': curnode})
            counter += 1

        if 0 == counter:
            if -1 != targdex:
                targ_exhausted += 1
            else:
                g_exhausted += 1
        else:
            queue_counter += counter

    return path, diag
