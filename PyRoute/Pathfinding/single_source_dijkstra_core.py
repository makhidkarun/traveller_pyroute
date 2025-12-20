# distutils: language = c++
# cython: profile=True
"""
Created on Aug 19, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
from cython.cimports.minmaxheap import MinMaxHeap, dijkstra_t

import numpy as np

cnp.import_array()


@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
def dijkstra_core(arcs: cython.list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]],
                  distance_labels: cnp.ndarray[cython.float], divisor: cython.float,
                  seeds: cython.list[cython.int],
                  max_neighbour_labels: cnp.ndarray[cython.float], min_cost: cnp.ndarray[cython.float]) -> tuple:
    if not isinstance(min_cost, cnp.ndarray):
        raise ValueError("min_cost must be ndarray")
    if not isinstance(max_neighbour_labels, cnp.ndarray):
        raise ValueError("max_neighbour_labels must be ndarray")
    if not isinstance(distance_labels, cnp.ndarray):
        raise ValueError("distance_labels must be ndarray")
    if not 0 < divisor <= 1.0:
        raise ValueError("divisor must be positive and <= 1.0")

    neighbours: tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]
    act_wt: cython.float
    act_nod: cython.int
    num_nodes: cython.size_t
    index: cython.size_t
    distance_labels_view: cython.double[:] = distance_labels
    max_neighbour_labels_view: cython.double[:] = max_neighbour_labels
    min_cost_view: cython.double[:] = min_cost
    parents: cnp.ndarray[cython.int] = np.ones(len(arcs), dtype=int) * -100  # Using -100 to track "not considered during processing"
    parents_view: cython.long[:] = parents
    active_nodes_view: cython.long[:]
    active_costs_view: cython.double[:]
    tail: cython.int
    dist_tail: cython.float
    heap: MinMaxHeap[dijkstra_t]
    diagnostics = {'nodes_processed': 0, 'nodes_queued': 0, 'nodes_exceeded': 0, 'nodes_min_exceeded': 0,
                   'nodes_tailed': 0}

    heap = MinMaxHeap[dijkstra_t]()
    heap.reserve(1000)
    for index in range(len(seeds)):
        act_nod = seeds[index]
        if 0 == len(arcs[act_nod][0]):
            continue
        if -1 == parents_view[act_nod]:
            continue
        parents_view[act_nod] = -1  # Using -1 to flag "root node of tree"
        heap.insert({'act_wt': distance_labels_view[act_nod], 'act_nod': act_nod})
        diagnostics['nodes_queued'] += 1

    while 0 < heap.size():
        result = heap.popmin()
        dist_tail = result.act_wt
        tail = result.act_nod

        if dist_tail > distance_labels_view[tail] or dist_tail + min_cost_view[tail] > max_neighbour_labels_view[tail]:
            if dist_tail > distance_labels[tail] - 1e-8:
                diagnostics['nodes_exceeded'] += 1
            else:
                diagnostics['nodes_min_exceeded'] += 1
            continue

        diagnostics['nodes_processed'] += 1

        # Link weights are strictly positive, thus lower bounded by zero. Thus, when the current dist_tail value exceeds
        # the corresponding node's distance label at the other end of the candidate edge, trim that edge.  Such edges
        # cannot _possibly_ result in smaller distance labels.  By a similar argument, filter the remaining edges
        # when the sum of dist_tail and that edge's weight equals or exceeds the corresponding node's distance label.
        neighbours = arcs[tail]
        active_nodes_view = neighbours[0]
        num_nodes = len(active_nodes_view)

        active_costs_view = neighbours[1]

        for index in range(0, num_nodes):
            act_nod = active_nodes_view[index]
            if dist_tail + active_costs_view[index] >= distance_labels_view[act_nod]:
                diagnostics['nodes_tailed'] += 1
                continue
            act_wt = dist_tail + divisor * active_costs_view[index]

            distance_labels_view[act_nod] = act_wt
            parents_view[act_nod] = tail
            heap.insert({'act_wt': act_wt, 'act_nod': act_nod})
            diagnostics['nodes_queued'] += 1

        # update max label _after_ neighbours are processed, to minimise the max_label as far as possible
        max_neighbour_labels_view[tail] = max(distance_labels[neighbours[0]])

    return distance_labels, parents, max_neighbour_labels, diagnostics
