"""Shortest paths and path lengths using the A* ("A star") algorithm.

Lifted from networkx repo (https://github.com/networkx/networkx/blob/main/networkx/algorithms/shortest_paths/astar.py)
as at Add note about using latex formatting in docstring in the contributor…  (commit a63c8bd).

Major modification here is tracking _upper_ bounds on shortest-path length as they are found
"""
from heapq import heappop, heappush, heapify

import networkx as nx

__all__ = ["astar_path_indexes"]


def astar_path_indexes(G, source, target, heuristic=None, weight="weight"):
    """Returns a list of nodes in a shortest path between source and target
    using the A* ("A-star") algorithm.

    There may be more than one shortest path.  This returns only one.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.
       If the heuristic is inadmissible (if it might
       overestimate the cost of reaching the goal from a node),
       the result may not be a shortest path.
       The algorithm does not support updating heuristic
       values for the same node due to caching the first
       heuristic calculation per node.

    weight : string or function
       If this is a string, then edge weights will be accessed via the
       edge attribute with this key (that is, the weight of the edge
       joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
       such edge attribute exists, the weight of the edge is assumed to
       be one.
       If this is a function, the weight of an edge is the value
       returned by the function. The function must accept exactly three
       positional arguments: the two endpoints of an edge and the
       dictionary of edge attributes for that edge. The function must
       return a number or None to indicate a hidden edge.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> print(nx.astar_path(G, 0, 4))
    [0, 1, 2, 3, 4]
    >>> G = nx.grid_graph(dim=[3, 3])  # nodes are two-tuples (x,y)
    >>> nx.set_edge_attributes(G, {e: e[1][0] * 2 for e in G.edges()}, "cost")
    >>> def dist(a, b):
    ...     (x1, y1) = a
    ...     (x2, y2) = b
    ...     return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    >>> print(nx.astar_path(G, (0, 0), (2, 2), heuristic=dist, weight="cost"))
    [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    See Also
    --------
    shortest_path, dijkstra_path

    """
    if source not in G or target not in G:
        msg = f"Either source {source} or target {target} is not in G"
        raise nx.NodeNotFound(msg)

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
    # Diagnostic dictionary
    diagnostics = {'nodes_expanded': 0, 'nodes_queued': 0, 'neighbours_checked': 0, 'heuristic_calls': 0}

    node_counter = 0

    while queue:
        # Pop the smallest item from queue.
        _, dist, curnode, parent = pop(queue)
        node_counter += 1

        if curnode == target:
            diagnostics['nodes_expanded'] = node_counter
            path = [curnode]
            node = parent
            while node is not None:
                path.append(node)
                node = explored[node]
            path.reverse()
            return path, diagnostics

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

        diagnostics['neighbours_checked'] += num_neighbours
        diagnostics['heuristic_calls'] += num_neighbours
        diagnostics['nodes_queued'] += num_neighbours
        if target == neighbours[0][0]:
            diagnostics['heuristic_calls'] -= 1
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
            if is_queue:
                diagnostics['heuristic_calls'] -= 1
                qcost, h = enqueued[neighbor]
                # if qcost <= ncost, a less costly path from the
                # neighbor to the source was already determined.
                # All such cases were stripped out during neighbour selection/filtering, above
                # Thus, we've found a less-costly path from neighbour to the source, so we'll update it
                # when we re-queue the neighbour
            else:
                h = heuristic(neighbor, target)

            # if ncost + h would bust the current _upper_ bound, there's no point continuing with the neighbour,
            # let alone queueing it
            # If neighbour is the target, h should be zero
            if ncost + h > upbound:
                if not is_queue:
                    # Queue the bound-busting neighbour so it can be pre-emptively removed in later iterations
                    enqueued[neighbor] = ncost, h
                else:
                    diagnostics['nodes_queued'] -= 1
                continue

            enqueued[neighbor] = ncost, h
            push(queue, (ncost + h, ncost, neighbor, curnode))

    raise nx.NetworkXNoPath(f"Node {target} not reachable from {source}")
