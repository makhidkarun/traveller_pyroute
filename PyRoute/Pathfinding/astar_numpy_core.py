"""
Created on Aug 18, 2024

@author: CyberiaResurrection
"""
import cython
from cython.cimports.numpy import numpy as cnp
cnp.import_array()
import numpy as np
from _heapq import heappop, heappush, heapify


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


@cython.infer_types(True)
def astar_numpy_core(G_succ, diagnostics, distances: cnp.ndarray[cython.float], explored, min_cost, potentials,
                     source: cython.int, target: cython.int, upbound):
    upper_limit: cnp.ndarray[cython.float] = upbound - min_cost
    upper_limit_view: cython.double[:] = upper_limit
    upper_limit_view[source] = 0.0
    distances_view: cython.double[:] = distances

    node_counter: cython.int = 0
    queue_counter: cython.int = 0
    revisited: cython.int = 0
    g_exhausted: cython.int = 0
    f_exhausted: cython.int = 0
    new_upbounds: cython.int = 0
    targ_exhausted: cython.int = 0
    revis_continue: cython.int = 0
    path = []
    diag = {}

    act_nod: cython.int
    act_wt: cython.float

    dist: cython.float
    curnode: cython.int
    parent: cython.int

    # The queue stores priority, cost to reach, node,  and parent.
    # Uses Python heapq to keep in priority order.
    # The nodes themselves, being integers, are directly comparable.
    queue = [(potentials[source], 0.0, source, -1)]

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
                queue = [item for item in queue if not (item[1] > distances_view[item[2]])]
                heapify(queue)
                continue
            # If we've found a better path, update
            revis_continue += 1
            distances_view[curnode] = dist

        explored[curnode] = parent

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
            if 0 == len(active_nodes):
                targ_exhausted += 1
                continue

            active_weights = active_weights[keep]
            augmented_weights = augmented_weights[keep]

        # Now unconditionally queue _all_ nodes that are still active, worrying about filtering out the bound-busting
        # neighbours later.
        num_nodes = len(active_nodes)
        queue_counter += num_nodes
        for i in range(num_nodes):
            act_nod = active_nodes[i]
            act_wt = active_weights[i]
            distances_view[act_nod] = act_wt
            upper_limit_view[act_nod] = act_wt
            heappush(queue, (augmented_weights[i], act_wt, act_nod, curnode))
    return path, diagnostics
