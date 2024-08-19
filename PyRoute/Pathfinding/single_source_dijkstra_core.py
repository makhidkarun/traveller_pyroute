"""
Created on Aug 19, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
from _heapq import heappop, heappush, heapify


@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
def dijkstra_core(arcs: cython.list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]],
                  distance_labels: cnp.ndarray[cython.float], divisor: cython.float,
                  heap: cython.list[tuple[cnp.ndarray[cython.float], cnp.ndarray[cython.int]]],
                  max_neighbour_labels: cnp.ndarray[cython.float], min_cost: cnp.ndarray[cython.float],
                  parents: cnp.ndarray[cython.int]):
    neighbours: tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]
    active_nodes: cnp.ndarray[cython.int]
    active_costs: cnp.ndarray[cython.float]
    active_labels: cnp.ndarray[cython.float]
    active_weights: cnp.ndarray[cython.float]
    act_wt: cython.float
    act_nod: cython.int
    keep: cnp.ndarray[cython.py_bool]
    num_nodes: cython.size_t
    index: cython.size_t
    distance_labels_view: cython.double[:] = distance_labels
    max_neighbour_labels_view: cython.double[:] = max_neighbour_labels
    min_cost_view: cython.double[:] = min_cost
    active_nodes_view: cython.long[:]
    active_weights_view: cython.double[:]
    tail: cython.int
    dist_tail: cython.float
    distance: cython.float

    while heap:
        dist_tail, tail = heappop(heap)

        if dist_tail > distance_labels_view[tail] or dist_tail + min_cost_view[tail] > max_neighbour_labels_view[tail]:
            # Since we've just dequeued a bad node (distance exceeding its current label, or too close to max-label),
            # remove other bad nodes from the list to avoid tripping over them later, and chuck out nodes who
            # can't give better distance labels
            if heap:
                heap = [(distance, tail) for (distance, tail) in heap if distance <= distance_labels_view[tail]
                        and distance + min_cost_view[tail] <= max_neighbour_labels_view[tail]]
                heapify(heap)
            continue

        # Link weights are strictly positive, thus lower bounded by zero. Thus, when the current dist_tail value exceeds
        # the corresponding node's distance label at the other end of the candidate edge, trim that edge.  Such edges
        # cannot _possibly_ result in smaller distance labels.  By a similar argument, filter the remaining edges
        # when the sum of dist_tail and that edge's weight equals or exceeds the corresponding node's distance label.
        neighbours = arcs[tail]
        active_nodes = neighbours[0]
        active_costs = neighbours[1]
        active_labels = distance_labels[active_nodes]
        # update max label
        max_neighbour_labels_view[tail] = max(active_labels)
        # It's not worth (time wise) being cute and trying to break this up, forcing jumps in and out of numpy
        keep = active_costs < (active_labels - dist_tail)
        active_nodes = active_nodes[keep]
        num_nodes = len(active_nodes)

        if 0 == num_nodes:
            continue
        active_weights = dist_tail + divisor * active_costs[keep]

        parents[active_nodes] = tail
        active_nodes_view = active_nodes
        active_weights_view = active_weights

        for index in range(0, num_nodes):
            act_wt = active_weights_view[index]
            act_nod = active_nodes_view[index]
            distance_labels_view[act_nod] = act_wt
            #heappush(heap, (active_weights[index], active_nodes[index]))
            heappush(heap, (act_wt, act_nod))

    return distance_labels, parents, max_neighbour_labels
