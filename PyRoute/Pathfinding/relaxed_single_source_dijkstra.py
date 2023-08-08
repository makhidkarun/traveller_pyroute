"""
Restarted single-source all-target Dijkstra shortest paths.

Lifted from networkx repo (https://github.com/networkx/networkx/blob/main/networkx/algorithms/shortest_paths/weighted.py)
as at Add note about using latex formatting in docstring in the contributor…  (commit a63c8bd).

Major modifications here are being able to start from an existing partial shortest-path tree after some subtree of it
has been removed (say an edge weight has changed) without requiring a full recalculation from scratch.

"""
from heapq import heappush, heappop
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function


def relaxed_single_source_dijkstra(G, source, weight, parent, paths, distances, restart):
    sources = [source]
    weight = _weight_function(G, weight)

    return _dijkstra_multisource(G, sources, weight, pred=parent, paths=paths, dist=distances, restart=restart)


def _dijkstra_multisource(
    G, sources, weight, pred=None, paths=None, target=None, dist=None, restart=None
):

    G_succ = G._succ if G.is_directed() else G._adj

    push = heappush
    pop = heappop
    # dictionary of final distances
    dist = {} if dist is None else dist
    seen = {} if dist is None else dist
    # fringe is heapq with 3-tuples (distance,c,node)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()
    fringe = []
    if restart is None:
        for source in sources:
            if source not in G:
                raise nx.NodeNotFound(f"Source {source} not in G")
            seen[source] = 0
            push(fringe, (0, next(c), source))
    else:
        for source in restart:
            if source not in G:
                raise nx.NodeNotFound(f"Restart node {source} not in G")
            push(fringe, (dist[source], next(c), source))
            del dist[source]

    while fringe:
        (d, _, v) = pop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        if v == target:
            break
        neighbours = [(u, e) for (u, e) in G_succ[v].items() if u not in dist]
        for u, e in neighbours:
            cost = weight(v, u, e)
            if cost is None:
                continue
            vu_dist = dist[v] + cost
            if u in dist:
                u_dist = dist[u]
                if vu_dist < u_dist:
                    raise ValueError("Contradictory paths found:", "negative weights?")
                elif pred is not None and vu_dist == u_dist:
                    pred[u] = v
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, next(c), u))
                if paths is not None:
                    paths[u] = paths[v] + [u]
                if pred is not None:
                    pred[u] = v
            elif vu_dist == seen[u]:
                if pred is not None:
                    pred[u] = v

    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist