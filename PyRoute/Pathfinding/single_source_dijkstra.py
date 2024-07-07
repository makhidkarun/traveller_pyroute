"""
Restarted single-source all-target Dijkstra shortest paths.

Lifted from networkx repo (https://github.com/networkx/networkx/blob/main/networkx/algorithms/shortest_paths/weighted.py)
as at Add note about using latex formatting in docstring in the contributor…  (commit a63c8bd).

Major modifications here are ripping out gubbins unrelated to the single-source all-targets case, handling cases
where less than the entire shortest path tree needs to be regenerated due to a link weight change, and specialising to
the specific input format used in PyRoute.

"""
import heapq
import numpy as np


def implicit_shortest_path_dijkstra_distance_graph(graph, source, distance_labels, seeds=None, divisor=1, min_cost=None, max_labels=None):
    # return only distance_labels from the explicit version
    distance_labels, _, max_neighbour_labels = explicit_shortest_path_dijkstra_distance_graph(graph, source,
                                                                                              distance_labels, seeds,
                                                                                              divisor,
                                                                                              min_cost=min_cost,
                                                                                              max_labels=max_labels)
    return distance_labels, max_neighbour_labels


def explicit_shortest_path_dijkstra_distance_graph(graph, source, distance_labels, seeds=None, divisor=1, min_cost=None, max_labels=None):
    # assumes that distance_labels is already setup
    if seeds is None:
        seeds = {source}

    floatinf = float('+inf')
    min_cost = np.zeros(len(graph)) if min_cost is None else min_cost
    max_neighbour_labels = max_labels if max_labels is not None else np.ones(len(graph), dtype=float) * floatinf

    arcs = graph._arcs

    heap = [(distance_labels[seed], seed) for seed in seeds if 0 < len(arcs[seed][0])]
    heapq.heapify(heap)

    parents = np.ones(len(graph), dtype=int) * -100  # Using -100 to track "not considered during processing"
    parents[list(seeds)] = -1  # Using -1 to flag "root node of tree"

    while heap:
        dist_tail, tail = heapq.heappop(heap)

        if dist_tail > distance_labels[tail] or dist_tail + min_cost[tail] > max_neighbour_labels[tail]:
            # Since we've just dequeued a bad node (distance exceeding its current label, or too close to max-label),
            # remove other bad nodes from the list to avoid tripping over them later, and chuck out nodes who
            # can't give better distance labels
            heap = [(distance, tail) for (distance, tail) in heap if distance <= distance_labels[tail]
                    and distance + min_cost[tail] <= max_neighbour_labels[tail]]
            heapq.heapify(heap)
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
        max_neighbour_labels[tail] = max(active_labels)
        # It's not worth (time wise) being cute and trying to break this up, forcing jumps in and out of numpy
        keep = active_costs < (active_labels - dist_tail)
        active_nodes = active_nodes[keep]
        num_nodes = len(active_nodes)

        if 0 == num_nodes:
            continue
        active_weights = dist_tail + divisor * active_costs[keep]
        distance_labels[active_nodes] = active_weights

        parents[active_nodes] = tail

        if 1 == num_nodes:
            heapq.heappush(heap, (active_weights[0], active_nodes[0]))
        elif 2 == num_nodes:
            heapq.heappush(heap, (active_weights[0], active_nodes[0]))
            heapq.heappush(heap, (active_weights[1], active_nodes[1]))
        elif 3 == num_nodes:
            heapq.heappush(heap, (active_weights[0], active_nodes[0]))
            heapq.heappush(heap, (active_weights[1], active_nodes[1]))
            heapq.heappush(heap, (active_weights[2], active_nodes[2]))
        else:  # Only cop the iterator overhead if there's at least 4 neighbours to queue
            for index in range(0, num_nodes):
                heapq.heappush(heap, (active_weights[index], active_nodes[index]))

    return distance_labels, parents, max_neighbour_labels
