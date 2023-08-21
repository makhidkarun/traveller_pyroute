"""
Restarted single-source all-target Dijkstra shortest paths.

Lifted from networkx repo (https://github.com/networkx/networkx/blob/main/networkx/algorithms/shortest_paths/weighted.py)
as at Add note about using latex formatting in docstring in the contributor…  (commit a63c8bd).

Major modifications here are ripping out gubbins unrelated to the single-source all-targets case, and handling cases
where less than the entire shortest path tree needs to be regenerated due to a link weight change.

"""
import heapq
from heapq import heappush, heappop
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function


def single_source_dijkstra(G, source, cutoff=None, distances=None, paths=None, frontier=None):
    """Find shortest weighted paths and lengths from a source node.

    Compute the shortest path length between source and all other
    reachable nodes for a weighted graph.

    Uses Dijkstra's algorithm to compute shortest paths and lengths
    between a source and all other reachable nodes in a weighted graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        Starting node for path

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.

    distances : dict of nodes, optional
        If provided, is assumed to be a dictionary of node-numeric pairs,
        reflecting the SPT distance from the node to source.
        Required with paths and/or frontier.

    paths : dict of nodes, optional
        If provided, is assumed to be a dictionary of node-list pairs,
        reflecting the already-found paths from the key node to the tree source.
        Required with distances and/or frontier.

    frontier : iterable of nodes, optional
        If provided, is assumed to be an iterable of nodes in distances to re-start
        the shortest-path search from.
        Required with distances and/or paths.

    Returns
    -------
    distance, path : pair of dictionaries, or numeric and list.
        The return value is a tuple of two dictionaries keyed by target nodes.
        The first dictionary stores distance to each target node.
        The second stores the path to each target node.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    Based on the Python cookbook recipe (119466) at
    https://code.activestate.com/recipes/119466/

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).
    """
    if not source:
        raise ValueError("source must not be empty")
    if source not in G:
        raise nx.NodeNotFound(f"Node {source} not found in graph")
    if (distances is None) != (paths is None) or (distances is None) != (frontier is None):
        raise nx.NetworkXException("Provide all of distances, paths and frontier, or none of them")

    paths = {source: [source]} if paths is None else paths  # dictionary of paths

    dist, diagnostics = _dijkstra_core(G, source, paths=paths, distances=distances, frontier=frontier)

    return (dist, paths, diagnostics)


def _dijkstra_core(G, source, paths=None, cutoff=None, distances=None, frontier=None):
    """Uses Dijkstra's algorithm to find shortest weighted paths

     Parameters
     ----------
     G : NetworkX graph

     source : non-empty iterable of nodes
         Starting node for paths. If this is just an iterable containing
         a single node, then all paths computed by this function will
         start from that node.

     paths: dict, optional (default=None)
         dict to store the path list from source to each node, keyed by node.
         If None, paths are not stored.

     cutoff : integer or float, optional
         Length (sum of edge weights) at which the search is stopped.
         If cutoff is provided, only return paths with summed weight <= cutoff.

    distances : dict of nodes, optional
        If provided, is assumed to be a dictionary of node-numeric pairs,
        reflecting the SPT distance from the node to source.

    frontier : iterable of nodes, optional
        If provided, is assumed to be an iterable of nodes in distances to re-start
        the shortest-path search from.


     Returns
     -------
     distance : dictionary
         A mapping from node to shortest distance to that node from one
         of the source nodes.

    diagnostics : dictionary
        A dictionary containing the following entries:
        nodes_expanded : Number of nodes expanded during search
        nodes_queued : Number of nodes queued during search
        neighbours_checked : Number of node neighbours considered during search

     Raises
     ------
     NodeNotFound
         If any of `sources` is not in `G`.

     Notes
     -----
     The optional predecessor and path dictionaries can be accessed by
     the caller through the original pred and paths objects passed
     as arguments. No need to explicitly return pred or paths.

     """
    G_succ = G._adj  # For speed-up (and works for both directed and undirected graphs)

    push = heappush
    pop = heappop

    dist = {}  # dictionary of final distances
    seen = {}
    diagnostics = { 'nodes_expanded': 0, 'nodes_queued': 0, 'neighbours_checked': 0}

    if frontier is not None:
        for node in distances:
            act_distance = distances[node]
            if node in frontier:
                seen[node] = act_distance
            else:
                dist[node] = act_distance

    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()
    fringe = []

    # set up the source
    if frontier is None:
        seen[source] = 0
        push(fringe, (0, next(c), source))
        diagnostics['nodes_queued'] += 1
    else:
        for node in frontier:
            push(fringe, (distances[node], next(c), node))
            diagnostics['nodes_queued'] += 1

    while fringe:
        (d, _, v) = pop(fringe)
        diagnostics['nodes_expanded'] += 1
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        neighbours = ((u, e) for (u, e) in G_succ[v].items() if ((u not in dist) or (d + e['weight'] <= dist[u])) and
                      ((u not in seen) or (d + e['weight'] <= seen[u]))
                      )
        for u, e in neighbours:
            diagnostics['neighbours_checked'] += 1
            cost = e['weight']
            # since we have a cost from v to u, _and_ a shortest-cost-so-far from source to v, that
            # gives an upper bound on the SPT cost from source to u
            vu_dist = d + cost
            # if we've already searched u:
            if u in dist:
                u_dist = dist[u]
                # if we've found a shorter path than the canonical "shortest" path, we've violated an invariant
                if vu_dist < u_dist:
                    raise ValueError("Contradictory paths found for " + str(u) + ":", "negative weights?")
            # if either this is the first time we've hit u, or we've found a shorter path to u:
            elif u not in seen or vu_dist < seen[u]:
                # set/update the tentative cost
                seen[u] = vu_dist
                # queue u for processing
                push(fringe, (vu_dist, next(c), u))
                diagnostics['nodes_queued'] += 1
                # if we're recording paths, record the path from source to u via v:
                if paths is not None:
                    paths[u] = paths[v] + [u]

    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist, diagnostics


def implicit_shortest_path_dijkstra(graph, source, distance_labels=None, seeds=None):
    if distance_labels is None:
        # dig up nodes in same graph component as source - that's the ones we care about finding distance labels _for_
        if seeds is None:
            distance_labels = {item: float('+inf') for item in graph if item.component == source.component}
            seeds = {source}
        else:
            components = [seed.component for seed in seeds]
            distance_labels = {item: float('+inf') for item in graph if item.component in components}
        for source in seeds:
            distance_labels[source] = 0

    c = count()
    heap = [(distance_labels[seed], next(c), seed) for seed in seeds]
    heapq.heapify(heap)

    while heap:
        dist_tail, _, tail = heapq.heappop(heap)
        if dist_tail > distance_labels[tail]:
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
            heapq.heappush(heap, (dist_head, next(c), head))
    return distance_labels


def implicit_shortest_path_dijkstra_indexes(graph, source, distance_labels=None, seeds=None):
    if distance_labels is None:
        # dig up nodes in same graph component as source - that's the ones we care about finding distance labels _for_
        if seeds is None:
            if isinstance(source, int):
                distance_labels = {item: float('+inf') for item in graph}
            else:
                distance_labels = {item: float('+inf') for item in graph if source.component == item.component}
            seeds = {source}
        else:
            distance_labels = {item: float('+inf') for item in graph}
        for source in seeds:
            distance_labels[source] = 0

    c = count()
    heap = [(distance_labels[seed], next(c), seed) for seed in seeds]
    heapq.heapify(heap)

    while heap:
        dist_tail, _, tail = heapq.heappop(heap)
        if dist_tail > distance_labels[tail]:
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
            heapq.heappush(heap, (dist_head, next(c), head))
    return distance_labels
