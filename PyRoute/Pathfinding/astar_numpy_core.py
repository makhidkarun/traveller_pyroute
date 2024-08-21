"""
Created on Aug 18, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
import numpy as np
from _heapq import heappop, heappush, heapify


@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
def astar_process_neighbours(active_nodes: cnp.ndarray[cython.int], active_weights: cnp.ndarray[cython.float],
                             augmented_weights: cnp.ndarray[cython.float], curnode: cython.int,
                             distances: cnp.ndarray[cython.float], min_cost: cnp.ndarray[cython.float],
                             new_upbounds: cython.int,
                             queue: list[tuple[cython.float, cython.float, cython.int, cython.int]],
                             queue_counter: cython.int, targ_exhausted: cython.int, target: cython.int,
                             upbound: cython.float, upper_limit: cnp.ndarray[cython.float]):
    i: cython.size_t
    active_nodes_view: cython.long[:] = active_nodes
    active_weights_view: cython.double[:] = active_weights
    augmented_weights_view: cython.double[:] = augmented_weights
    num_nodes: cython.int = len(active_nodes_view)
    targdex: cython.int = -1
    act_nod: cython.int
    act_wt: cython.double

    distances_view: cython.double[:] = distances
    upper_limit_view: cython.double[:]
    up_threshold: cnp.ndarray[cython.float]
    item: tuple[cython.float, cython.float, cython.int, cython.int]

    if 0 == len(active_nodes_view):
        return new_upbounds, queue, queue_counter, targ_exhausted, upbound, upper_limit

    for i in range(num_nodes):
        act_nod = active_nodes_view[i]
        if act_nod == target:
            targdex = i
            break

    if -1 != targdex:
        upbound = active_weights_view[targdex]
        new_upbounds += 1
        distances_view[target] = upbound
        upper_limit = np.minimum(upper_limit, upbound - min_cost)

        if 0 < len(queue):
            queue = [item for item in queue if item[0] < upbound]
            if 0 < len(queue):
                # While we're taking a brush-hook to queue, rip out items whose dist value exceeds enqueued value
                # or is too close to upbound
                queue = [item for item in queue if item[1] <= upper_limit[item[2]]]
                # Finally, dedupe the queue after cleaning all bound-busts out and 2 or more elements are left.
                # Empty or single-element sets cannot require deduplication, and are already heaps themselves.
                if 1 < len(queue):
                    queue = list(set(queue))
                    heapify(queue)
        # heappush(queue, (ncost + 0, ncost, target, curnode))
        heappush(queue, (upbound, upbound, target, curnode))
        queue_counter += 1

        # As we have a tighter upper bound, apply it to the neighbours as well - target will be excluded because
        # its augmented weight is _equal_ to upbound
        keep = augmented_weights < upbound
        active_nodes = active_nodes[keep]
        active_nodes_view = active_nodes
        if 0 == len(active_nodes):
            targ_exhausted += 1

        active_weights = active_weights[keep]
        augmented_weights = augmented_weights[keep]
        active_weights_view = active_weights
        augmented_weights_view = augmented_weights

    upper_limit_view = upper_limit
    # Now unconditionally queue _all_ nodes that are still active, worrying about filtering out the bound-busting
    # neighbours later.
    num_nodes = len(active_nodes_view)
    queue_counter += num_nodes
    for i in range(num_nodes):
        act_nod = active_nodes_view[i]
        act_wt = active_weights_view[i]
        distances_view[act_nod] = act_wt
        upper_limit_view[act_nod] = act_wt
        heappush(queue, (augmented_weights_view[i], act_wt, act_nod, curnode))
    return new_upbounds, queue, queue_counter, targ_exhausted, upbound, upper_limit
