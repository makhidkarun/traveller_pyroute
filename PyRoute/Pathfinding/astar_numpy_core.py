"""
Created on Aug 18, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
import numpy as np
from heapq import heappop, heappush, heapify


def astar_get_neighbours(g_succ: cython.list[tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]], curnode: cython.int,
                         dist: cython.float, potentials: cnp.ndarray[cython.float], upbound: cython.float,
                         upper_limit: cnp.ndarray[cython.float]) -> \
                         cython.tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float], cnp.ndarray[cython.float]]:
    raw_nodes: cython.tuple[cnp.ndarray[cython.int], cnp.ndarray[cython.float]]
    active_nodes: cnp.ndarray[cython.int]
    active_weights: cnp.ndarray[cython.float]
    augmented_weights: cnp.ndarray[cython.float]
    keep: cnp.ndarray[cython.py_bool]

    raw_nodes = g_succ[curnode]
    active_nodes = raw_nodes[0]
    active_weights = dist + raw_nodes[1]
    augmented_weights = active_weights + potentials[active_nodes]
    # Even if we have the target node as a candidate neighbour, of itself, that's _no_ guarantee that the target
    # as neighbour will give a better upper bound.
    keep = np.logical_and(augmented_weights < upbound, active_weights <= upper_limit[active_nodes])
    active_nodes = active_nodes[keep]
    active_weights = active_weights[keep]
    augmented_weights = augmented_weights[keep]
    return active_nodes, active_weights, augmented_weights


def astar_push_to_queue(active_nodes: cnp.ndarray[cython.int], active_weights: cnp.ndarray[cython.float],
                        augmented_weights: cnp.ndarray[cython.float], curnode: cython.int,
                        queue: list[tuple[cnp.ndarray[cython.float], cnp.ndarray[cython.float], cnp.ndarray[cython.int],
                                          cnp.ndarray[cython.int]]]):
    num_nodes: cython.int
    num_nodes = len(active_nodes)

    for i in range(num_nodes):
        heappush(queue, (augmented_weights[i], active_weights[i], active_nodes[i], curnode))
