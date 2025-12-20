"""
Restarted single-source all-target Dijkstra shortest paths.

Lifted from networkx repo (https://github.com/networkx/networkx/blob/main/networkx/algorithms/shortest_paths/weighted.py)
as at Add note about using latex formatting in docstring in the contributor…  (commit a63c8bd).

Major modifications here are ripping out gubbins unrelated to the single-source all-targets case, handling cases
where less than the entire shortest path tree needs to be regenerated due to a link weight change, and specialising to
the specific input format used in PyRoute.

"""
import numpy as np


try:
    from PyRoute.Pathfinding.single_source_dijkstra_core import dijkstra_core
except ModuleNotFoundError:
    from PyRoute.Pathfinding.single_source_dijkstra_core_fallback import dijkstra_core
except ImportError:
    from PyRoute.Pathfinding.single_source_dijkstra_core_fallback import dijkstra_core
except AttributeError:
    from PyRoute.Pathfinding.single_source_dijkstra_core_fallback import dijkstra_core


def implicit_shortest_path_dijkstra_distance_graph(graph, source, distance_labels, seeds=None, divisor=1.0, min_cost=None, max_labels=None) -> tuple:
    # return only distance_labels from the explicit version
    distance_labels, _, max_neighbour_labels, diagnostics = explicit_shortest_path_dijkstra_distance_graph(graph, source,
                                                                                              distance_labels, seeds,
                                                                                              divisor,
                                                                                              min_cost=min_cost,
                                                                                              max_labels=max_labels)
    return distance_labels, max_neighbour_labels, diagnostics


def explicit_shortest_path_dijkstra_distance_graph(graph, source, distance_labels, seeds=None, divisor=1.0, min_cost=None, max_labels=None) -> tuple:
    if not isinstance(source, int):
        raise ValueError("source must be integer")
    if not isinstance(distance_labels, np.ndarray):
        raise ValueError("distance labels must be ndarray")
    if np.isnan(distance_labels).any():
        raise ValueError("distance labels must not be None")
    if (distance_labels < 0).any():
        raise ValueError("All distance labels must be non-negative")
    if (distance_labels == 0).all():
        raise ValueError("At least one distance label must be nonzero")

    # assumes that distance_labels is already setup
    if seeds is None:
        seeds = {source}

    seeds = list(seeds)
    min_cost = np.zeros(len(graph)) if min_cost is None else min_cost
    max_neighbour_labels = max_labels if max_labels is not None else np.ones(len(graph)) * float('+inf')  # pragma: no mutate

    arcs = graph._arcs

    return dijkstra_core(arcs, distance_labels, divisor, seeds, max_neighbour_labels, min_cost)
