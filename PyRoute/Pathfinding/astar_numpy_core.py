"""
Created on Aug 18, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
import numpy as np


def astar_get_neighbours(G_succ: list[tuple[cnp.ndarray(cython.int), cnp.ndarray(cython.float)]], curnode: cython.int,
                         dist: cython.float, potentials, upbound: cython.float, upper_limit):
    raw_nodes: tuple[cnp.ndarray(cython.int), cnp.ndarray(cython.float)]

    raw_nodes = G_succ[curnode]
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
