"""
Restarted single-source all-target Dijkstra shortest paths.

Lifted from networkx repo (https://github.com/networkx/networkx/blob/main/networkx/algorithms/shortest_paths/weighted.py)
as at Add note about using latex formatting in docstring in the contributor…  (commit a63c8bd).

Major modifications here are ripping out gubbins unrelated to the single-source all-targets case, and handling cases
where less than the entire shortest path tree needs to be regenerated due to a link weight change.

"""
import heapq


def implicit_shortest_path_dijkstra_indexes(graph, source, distance_labels=None, seeds=None):
    if distance_labels is None:
        # dig up nodes in same graph component as source - that's the ones we care about finding distance labels _for_
        if seeds is None:
            if isinstance(source, int):
                sourcecomp = graph.nodes[source]['star'].component
                distance_labels = {item: float('+inf') for item in graph if graph.nodes[item]['star'].component == sourcecomp}
            else:
                distance_labels = {item: float('+inf') for item in graph if source.component == item.component}
            seeds = {source}
        else:
            components = set()
            for source in seeds:
                sourcecomp = graph.nodes[source]['star'].component
                components.add(sourcecomp)
            distance_labels = {item: float('+inf') for item in graph if graph.nodes[item]['star'].component in components}
        for source in seeds:
            distance_labels[source] = 0

    heap = [(distance_labels[seed], seed) for seed in seeds]
    heapq.heapify(heap)

    while heap:
        dist_tail, tail = heapq.heappop(heap)
        if dist_tail > distance_labels[tail]:
            # Since we've just dequeued a bad node, remove other bad nodes from the list to avoid tripping
            # over them later
            heap = [(distance, tail) for (distance, tail) in heap if distance <= distance_labels[tail]]
            heapq.heapify(heap)
            continue

        # Link weights are strictly positive, thus lower bounded by zero. Thus, when the current dist_tail value exceeds
        # the corresponding node's distance label at the other end of the candidate edge, trim that edge.  Such edges
        # cannot _possibly_ result in smaller distance labels.  By a similar argument, filter the remaining edges
        # when the sum of dist_tail and that edge's weight equals or exceeds the corresponding node's distance label.
        neighbours = ((head, dist_tail + data['weight']) for (head, data) in graph[tail].items()
                      if dist_tail <= distance_labels[head] and dist_tail + data['weight'] < distance_labels[head]
                      )
        for head, dist_head in neighbours:
            distance_labels[head] = dist_head
            heapq.heappush(heap, (dist_head, head))
    return distance_labels


def implicit_shortest_path_dijkstra_distance_graph(graph, source, distance_labels, seeds=None, divisor=1):
    # assumes that distance_labels is already setup
    if seeds is None:
        seeds = {source}

    arcs = graph._arcs

    heap = [(distance_labels[seed], seed) for seed in seeds if 0 < len(arcs[seed][0])]
    heapq.heapify(heap)

    while heap:
        dist_tail, tail = heapq.heappop(heap)
        if dist_tail > distance_labels[tail]:
            # Since we've just dequeued a bad node, remove other bad nodes from the list to avoid tripping
            # over them later
            heap = [(distance, tail) for (distance, tail) in heap if distance <= distance_labels[tail]]
            heapq.heapify(heap)
            continue

        # Link weights are strictly positive, thus lower bounded by zero. Thus, when the current dist_tail value exceeds
        # the corresponding node's distance label at the other end of the candidate edge, trim that edge.  Such edges
        # cannot _possibly_ result in smaller distance labels.  By a similar argument, filter the remaining edges
        # when the sum of dist_tail and that edge's weight equals or exceeds the corresponding node's distance label.
        neighbours = arcs[tail]
        active_nodes = neighbours[0]
        active_costs = neighbours[1]
        active_weights = dist_tail + active_costs
        keep = active_weights < distance_labels[active_nodes]
        active_nodes = active_nodes[keep]
        num_nodes = len(active_nodes)

        if 0 == num_nodes:
            continue
        active_weights = dist_tail + divisor * active_costs[keep]
        distance_labels[active_nodes] = active_weights

        heapq.heappush(heap, (active_weights[0], active_nodes[0]))
        if 1 < num_nodes:  # Only cop the iterator overhead if there's at least 2 neighbours to queue
            for index in range(1, num_nodes):
                heapq.heappush(heap, (active_weights[index], active_nodes[index]))

    return distance_labels
