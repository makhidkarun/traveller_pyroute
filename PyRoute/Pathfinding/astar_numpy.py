"""
Created on Feb 22, 2024

@author: CyberiaResurrection
"""
from heapq import heappop, heappush, heapify

import networkx as nx
import numpy as np


def astar_path_numpy(G, source, target, bulk_heuristic):

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

        raw_nodes = G_succ[curnode]
        active_nodes = raw_nodes[0]
        active_weights = dist + raw_nodes[1]
        # filter out nodes whose active weights exceed _either_ the node's distance label _or_ the current upper bound
        # - the current node can _not_ result in a shorter path
        keep = active_weights <= np.minimum(distances[active_nodes], upbound)
        active_nodes = active_nodes[keep]

        # if neighbours list is empty, go around
        num_neighbours = len(active_nodes)
        if 0 == num_neighbours:
            continue

        active_weights = active_weights[keep]
        active_heuristics = bulk_heuristic(active_nodes, target)
        augmented_weights = active_weights + active_heuristics

        if target in active_nodes:
            drop = active_nodes == target
            ncost = active_weights[drop][0]
            better_bound = upbound > ncost

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
            # active_heuristics = active_heuristics[keep]
            augmented_weights = augmented_weights[keep]

            if better_bound:
                distances[target] = ncost
                #push(queue, (ncost + 0, ncost, target, curnode))
                push(queue, (ncost, ncost, target, curnode))

            # if there _was_ one neighbour to process, that was the target, so neighbour list is now empty.
            if 1 == num_neighbours:
                continue

        # Now we have the latest upper bound, use it to filter out nodes whose augmented weights will bust the upper
        # bound. We still need to _queue_ the bound-busting nodes' active costs, as that allows us to dodge about a
        # quarter of the nodes we would otherwise have to spin through - if it's stupid, but it works, it isn't stupid.
        # As a result, unconditionally queue _all_ nodes that are still active, and filter out the bound-busting
        # neighbours.
        distances[active_nodes] = active_weights

        keep = augmented_weights <= upbound
        active_nodes = active_nodes[keep]
        active_weights = active_weights[keep]
        # active_heuristics = active_heuristics[keep]
        augmented_weights = augmented_weights[keep]

        for i in range(0, len(active_nodes)):
            push(queue, (augmented_weights[i], active_weights[i], active_nodes[i], curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")


def astar_path_numpy_bucket(G, source, target, bulk_heuristic):

    G_succ = G._arcs  # For speed-up

    # Traces lowest distance from source node found for each node
    distances = np.ones(len(G)) * float('+inf')
    distances[source] = 0
    # Tracks shortest _complete_ path found so far
    floatinf = float('inf')
    upbound = floatinf
    # Tracks node parents
    parents = [None] * len(G)
    # pre-calc heuristics for all nodes to the target node
    potentials = bulk_heuristic(G._nodes, target)

    # the buckets array does a couple of things:
    # 1 - the kth bucket stores all nodes with f values between k, inclusive, and k+1, exclusive
    # 2 - nodes in a bucket are not sorted, to dodge the overhead that regular A* would incur
    buckets = [[(0, source)]]
    i = 0

    while i < len(buckets):
        if distances[target] < i:
            break
        for dist_u, u in buckets[i]:
            if dist_u != distances[u]:
                continue
            neighbours = G_succ[u]
            active_nodes = neighbours[0]
            augmented_weights = dist_u + neighbours[1] + potentials[active_nodes]
            keep = augmented_weights < np.minimum(distances[active_nodes], distances[target])
            active_nodes = active_nodes[keep]
            num_nodes = len(active_nodes)
            if 0 == num_nodes:  # if active_nodes is empty, bail out now to avoid the pointless iterator setup
                continue
            augmented_weights = augmented_weights[keep]
            distances[active_nodes] = augmented_weights
            for k in range(0, num_nodes):
                v = active_nodes[k]
                dist_v = augmented_weights[k]
                parents[v] = u
                j = int(dist_v)
                while len(buckets) <= j:
                    buckets.append([])
                buckets[j].append((dist_v, v))
        i += 1
    if distances[target] == floatinf:
        return None
    path = [target]
    node = parents[target]
    while node is not None:
        assert node not in path, "Node " + str(node) + " duplicated in discovered path"
        path.append(node)
        node = parents[node]
    path.reverse()
    return path, {}
