"""
Created on Feb 22, 2024

@author: CyberiaResurrection
"""
from heapq import heappop, heappush, heapify

import networkx as nx
import numpy as np


def astar_path_numpy(G, source, target, heuristic, bulk_heuristic):

    push = heappush
    pop = heappop

    G_succ = G._arcs  # For speed-up

    # The queue stores priority, cost to reach, node,  and parent.
    # Uses Python heapq to keep in priority order.
    # The nodes themselves, being integers, are directly comparable.
    queue = [(0, 0, source, None)]

    # Maps explored nodes to parent closest to the source.
    explored = {}
    # Traces lowest distance from source node found for each node
    distances = np.ones(len(G)) * float('+inf')
    distances[source] = 0
    # Tracks shortest _complete_ path found so far
    floatinf = float('inf')
    upbound = floatinf

    node_counter = 0

    while queue:
        # Pop the smallest item from queue.
        _, dist, curnode, parent = pop(queue)
        node_counter += 1

        if curnode == target:
            path = [curnode]
            node = parent
            while node is not None:
                assert node not in path, "Node " + str(node) + " duplicated in discovered path"
                path.append(node)
                node = explored[node]
            path.reverse()
            return path, {}

        if 0 == node_counter % 49 and 0 < len(queue):
            # Trim queue items that can not result in a shorter path
            queue = [item for item in queue if not (item[1] > distances[item[2]])]
            heapify(queue)

        if curnode in explored:
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost = distances[curnode]
            if qcost < dist:
                queue = [item for item in queue if not (item[1] > distances[item[2]])]
                heapify(queue)
                continue
            # If we've found a better path, update
            distances[curnode] = qcost

        explored[curnode] = parent

        # Shims to support numpy conversion
        raw_nodes = G_succ[curnode]
        active_nodes = raw_nodes[0]
        active_weights = dist + raw_nodes[1]
        # filter out nodes whose distance labels are strictly less than their active weights
        # - the current node can _not_ result in a shorter path
        keep = distances[active_nodes] >= active_weights
        below_bound = active_weights <= upbound
        keep = np.logical_and(keep, below_bound)
        active_nodes = active_nodes[keep]

        # if neighbours list is empty, go around
        num_neighbours = len(active_nodes)
        if 0 == num_neighbours:
            continue

        active_weights = active_weights[keep]
        active_heuristics = bulk_heuristic(active_nodes, target)
        augmented_weights = active_weights + active_heuristics
        # Pre-filter neighbours
        # Remove neighbour nodes that are already enqueued and won't result in shorter paths to them
        # Explicitly retain target node (if present) to give a chance of finding a better upper bound
        # Explicitly _exclude_ source node (if present) because re-considering it is pointless
        # TODO: fill in

        if target in active_nodes:
            drop = active_nodes == target
            ncost = active_weights[drop][0]
            better_bound = upbound > ncost
            queue_targ = True
            if ncost > distances[target]:
                queue_targ = False

            if better_bound:
                upbound = ncost
                if 0 < len(queue):
                    queue = [item for item in queue if item[0] <= upbound]
                    # While we're taking a brush-hook to queue, rip out items whose dist value exceeds enqueued value
                    queue = [item for item in queue if not (item[1] > distances[item[2]])]
                    heapify(queue)
            # either way, target node has been processed, drop it from neighbours
            keep = active_nodes != target
            below_bound = active_weights <= upbound  # As we have a tighter upper bound, apply it to the neighbours as well
            keep = np.logical_and(keep, below_bound)
            active_nodes = active_nodes[keep]
            active_weights = active_weights[keep]
            active_heuristics = active_heuristics[keep]
            augmented_weights = augmented_weights[keep]

            if queue_targ and better_bound:
                h = 0
                distances[target] = ncost
                push(queue, (ncost + h, ncost, target, curnode))

            # if there _was_ one neighbour to process, that was the target, so neighbour list is now empty.
            if 1 == num_neighbours:
                continue

        # Now we have the latest upper bound, use it to filter out nodes whose augmented weights will bust the upper
        # bound. We still need to _queue_ the bound-busting nodes' active costs, as that allows us to dodge about a
        # quarter of the nodes we would otherwise have to spin through - if it's stupid, but it works, it isn't stupid.
        bust = augmented_weights > upbound
        bust_nodes = active_nodes[bust]
        bust_weights = active_weights[bust]
        distances[bust_nodes] = bust_weights

        keep = augmented_weights <= upbound
        active_nodes = active_nodes[keep]
        active_weights = active_weights[keep]
        active_heuristics = active_heuristics[keep]
        augmented_weights = augmented_weights[keep]

        for i in range(0, len(active_nodes)):
            neighbour = active_nodes[i]
            ncost = active_weights[i]
            # h = active_heuristics[i]
            augment = augmented_weights[i]

            distances[neighbour] = ncost
            push(queue, (augment, ncost, neighbour, curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
