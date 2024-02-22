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

    G_succ = G._adj  # For speed-up (and works for both directed and undirected graphs)

    # The queue stores priority, cost to reach, node,  and parent.
    # Uses Python heapq to keep in priority order.
    # The nodes themselves, being integers, are directly comparable.
    queue = [(0, 0, source, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}
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
                path.append(node)
                node = explored[node]
            path.reverse()
            return path, {}

        if 0 == node_counter % 49 and 0 < len(queue):
            # Trim queue items that can not result in a shorter path
            queue = [item for item in queue if not (item[2] in enqueued and item[1] > enqueued[item[2]][0])]
            heapify(queue)

        if curnode in explored:
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost, h = enqueued[curnode]
            if qcost < dist:
                queue = [item for item in queue if not (item[2] in enqueued and item[1] > enqueued[item[2]][0])]
                heapify(queue)
                continue
            # If we've found a better path, update
            enqueued[curnode] = dist, h

        explored[curnode] = parent

        # Shims to support numpy conversion
        raw_nodes = list(G_succ[curnode].keys())
        active_nodes = np.array(raw_nodes)
        active_heuristics = bulk_heuristic(active_nodes, target)
        active_dict = dict(zip(active_nodes, range(len(raw_nodes))))
        # Pre-filter neighbours
        # Remove neighbour nodes that are already enqueued and won't result in shorter paths to them
        # Explicitly retain target node (if present) to give a chance of finding a better upper bound
        # Explicitly _exclude_ source node (if present) because re-considering it is pointless
        neighbours = [(k, dist + v['weight'], k in enqueued) for (k, v) in G_succ[curnode].items()
                      if not (k in enqueued and dist + v['weight'] >= enqueued[k][0] and not (k == target)) and not (k == source)]
        if upbound != floatinf and 0 < len(neighbours):
            # Remove neighbour nodes who will bust the upper bound as it currently stands
            neighbours = [(k, v, is_queue) for (k, v, is_queue) in neighbours if v <= upbound]
            # remove enqueued neighbour nodes whose cost plus stored heuristic value will bust upper bound
            neighbours = [(k, v, is_queue) for (k, v, is_queue) in neighbours if not (is_queue and v + enqueued[k][1] > upbound)]

        # if neighbours list is empty, go around
        num_neighbours = len(neighbours)
        if 0 == num_neighbours:
            continue

        # if neighbours list has at least 2 elements, sort it, putting the target node first, then by ascending weight
        if 1 < num_neighbours:
            neighbours.sort(key=lambda item: 2 if item[0] == target else 0 + 1 if item[2] else 0, reverse=True)
            if neighbours[0][0] == target:  # If first item is the target node, drop all neighbours with higher weights
                targ_weight = neighbours[0][1]
                neighbours = [(k, v, is_queue) for (k, v, is_queue) in neighbours if v <= targ_weight
                              and not (is_queue and v + enqueued[k][1] > targ_weight)]
                num_neighbours = len(neighbours)

        if target == neighbours[0][0]:
            ncost = neighbours[0][1]
            better_bound = upbound > ncost
            is_queue = neighbours[0][2]
            queue_targ = True
            if is_queue:
                qcost, h = enqueued[target]
                if qcost <= ncost:
                    queue_targ = False

            if better_bound:
                upbound = ncost
                if 0 < len(queue):
                    queue = [item for item in queue if item[0] <= upbound]
                    # While we're taking a brush-hook to queue, rip out items whose dist value exceeds enqueued value
                    queue = [item for item in queue if not (item[2] in enqueued and item[1] > enqueued[item[2]][0])]
                    heapify(queue)
            # either way, target node has been processed, drop it from neighbours
            neighbours = [(k, v, is_queue) for (k, v, is_queue) in neighbours if v <= upbound and k != target]

            if queue_targ and better_bound:
                h = 0
                enqueued[target] = ncost, h
                push(queue, (ncost + h, ncost, target, curnode))

            # if there _was_ one neighbour to process, that was the target, so neighbour list is now empty.
            if 1 == num_neighbours:
                continue

        for neighbor, ncost, is_queue in neighbours:
            h = active_heuristics[active_dict[neighbor]]

            # if ncost + h would bust the current _upper_ bound, there's no point continuing with the neighbour,
            # let alone queueing it
            # If neighbour is the target, h should be zero
            if ncost + h > upbound:
                if not is_queue:
                    # Queue the bound-busting neighbour so it can be pre-emptively removed in later iterations
                    enqueued[neighbor] = ncost, h
                continue

            enqueued[neighbor] = ncost, h
            push(queue, (ncost + h, ncost, neighbor, curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
