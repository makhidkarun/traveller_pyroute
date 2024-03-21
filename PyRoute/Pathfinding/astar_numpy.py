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
    Grooms the node queue in the following cases:
        When a new upper bound is found, discards queue entries whose f-values bust the new upper bound
        When a _longer_ path is found to a previously-queued node, discards queue entries whose g-values bust
            the corresponding node's distance label
        Every 49 nodes, discards queue entries who bust their corresponding node's distance label

"""
from heapq import heappop, heappush, heapify

import networkx as nx
import numpy as np


def _sum_branch(branch_fac, path_len):
    total = 0
    for i in range(1, path_len + 1):
        total += branch_fac ** i
    return total


def _calc_branching_factor(nodes_queued, path_len):
    if path_len == nodes_queued:
        return 1.0

    hibound = nodes_queued ** (1/path_len)
    hires = _sum_branch(hibound, path_len) - nodes_queued
    lobound = 1
    lores = path_len - nodes_queued

    while 0.001 <= abs(hibound - lobound):
        mid = round(0.5 * (hibound + lobound), 3)
        if mid == hibound or mid == lobound:
            break
        midres = _sum_branch(mid, path_len) - nodes_queued
        if 0 < midres:
            hibound = mid
            hires = midres
        else:
            lobound = mid
            lores = midres

    return mid


def astar_path_numpy(G, source, target, bulk_heuristic, min_cost=None, upbound=None):

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
    upbound = floatinf if upbound is None else upbound
    # pre-calc heuristics for all nodes to the target node
    potentials = bulk_heuristic(G._nodes, target)
    # pre-calc the minimum-cost edge on each node
    min_cost = np.zeros(len(G)) if min_cost is None else min_cost
    min_cost[target] = 0

    node_counter = 0
    queue_counter = 0
    revisited = 0
    neighbour_bound = 0
    g_exhausted = 0
    f_exhausted = 0
    new_upbounds = 0
    un_exhausted = 0
    has_bound = upbound != floatinf

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
            branch = _calc_branching_factor(queue_counter, len(path) - 1)
            diagnostics = {'nodes_expanded': node_counter, 'nodes_queued': queue_counter, 'branch_factor': branch,
                           'num_jumps': len(path) - 1, 'nodes_revisited': revisited, 'neighbour_bound': neighbour_bound,
                           'new_upbounds': new_upbounds, 'g_exhausted': g_exhausted, 'f_exhausted': f_exhausted,
                           'un_exhausted': un_exhausted}
            path.reverse()
            return path, diagnostics

        if 0 == node_counter % 49 and 0 < len(queue):
            # Trim queue items that can not result in a shorter path
            queue = [item for item in queue if not (item[1] > distances[item[2]])]
            heapify(queue)

        if curnode in explored:
            revisited += 1
            # Do not override the parent of starting node
            if explored[curnode] is None:
                continue

            # Skip bad paths that were enqueued before finding a better one
            qcost = distances[curnode]
            if qcost <= dist:
                queue = [item for item in queue if not (item[1] > distances[item[2]])]
                heapify(queue)
                continue
            # If we've found a better path, update
            distances[curnode] = dist

        explored[curnode] = parent
        neighbour_bound += 1

        raw_nodes = G_succ[curnode]
        active_nodes = raw_nodes[0]
        active_weights = dist + raw_nodes[1]
        # filter out nodes whose active weights exceed _either_ the node's distance label _or_ the current upper bound
        # - the current node can _not_ result in a shorter path
        if has_bound:
            keep = active_weights <= np.minimum(distances[active_nodes], upbound - min_cost[active_nodes])
        else:
            keep = active_weights <= distances[active_nodes]
        # if we're not keeping anything, go around
        active_nodes = active_nodes[keep]
        num_neighbours = len(active_nodes)
        if 0 == num_neighbours:
            g_exhausted += 1
            continue
        active_weights = active_weights[keep]
        augmented_weights = active_weights + potentials[active_nodes]

        # Even if we have the target node as a candidate neighbour, of itself, that's _no_ guarantee that the target
        # as neighbour will give a better upper bound.  The has_bound check also works out faster than the
        # target in active_nodes check.
        if has_bound:
            keep = augmented_weights < upbound
            if not keep.all():
                active_nodes = active_nodes[keep]
                num_neighbours = len(active_nodes)
                if 0 == num_neighbours:
                    f_exhausted += 1
                    continue
                active_weights = active_weights[keep]
                augmented_weights = augmented_weights[keep]

        if target in active_nodes:
            drop = active_nodes == target
            ncost = active_weights[drop][0]

            upbound = ncost
            new_upbounds += 1
            distances[target] = ncost
            has_bound = True
            if 0 < len(queue):
                queue = [item for item in queue if item[0] < upbound]
                # While we're taking a brush-hook to queue, rip out items whose dist value exceeds enqueued value
                queue = [item for item in queue if not (item[1] > distances[item[2]])]
                # And while we're here, trim elements who are too close to upbound
                queue = [item for item in queue if item[1] + min_cost[item[2]] <= upbound]
                # Finally, dedupe the queue after cleaning all bound-busts out and 2 or more elements are left.
                # Empty or single-element sets cannot require deduplication, and are already heaps themselves.
                if 1 < len(queue):
                    queue = list(set(queue))
                    heapify(queue)
            # push(queue, (ncost + 0, ncost, target, curnode))
            push(queue, (ncost, ncost, target, curnode))
            queue_counter += 1
            #  If target node is only active node, and is neighbour node of only active queue element, bail out now
            #  and dodge the now-known-to-be-pointless neighbourhood bookkeeping.
            if 1 == len(queue) and 1 == len(active_nodes):
                continue
            # target node has been processed, drop it from neighbours
            keep = active_nodes != target
            # As we have a tighter upper bound, apply it to the neighbours as well
            keep = np.logical_and(keep, augmented_weights < upbound)
            active_nodes = active_nodes[keep]
            active_weights = active_weights[keep]
            augmented_weights = augmented_weights[keep]

            # if there _was_ one neighbour to process, that was the target, so neighbour list is now empty.
            # Likewise, if the new upper bound has emptied the neighbour list, go around.
            if 1 == num_neighbours or 0 == len(active_nodes):
                continue

        # Now we have the latest upper bound, use it to filter out nodes whose augmented weights will bust the upper
        # bound. We still need to _queue_ the bound-busting nodes' active costs, as that allows us to dodge about a
        # quarter of the nodes we would otherwise have to spin through - if it's stupid, but it works, it isn't stupid.
        # As a result, unconditionally queue _all_ nodes that are still active, and filter out the bound-busting
        # neighbours.
        distances[active_nodes] = active_weights
        un_exhausted += 1

        remain = zip(augmented_weights, active_weights, active_nodes)
        queue_counter += len(active_nodes)

        for augmented_weight, active_weight, active_node in remain:
            push(queue, (augmented_weight, active_weight, active_node, curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
