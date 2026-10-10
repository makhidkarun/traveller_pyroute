"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
import math
import numpy as np
from collections import defaultdict
from typing import Any

try:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
except ModuleNotFoundError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except ImportError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except AttributeError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
from PyRoute.Pathfinding.LandmarkSchemes.LandmarkAvoidHelper import LandmarkAvoidHelper
from PyRoute.Pathfinding.single_source_dijkstra import explicit_shortest_path_dijkstra_distance_graph


class LandmarksTriaxialExtremes:

    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.route_reuse = galaxy.trade.route_reuse
        self._set_max_slots()
        self.graph_len = len(self.galaxy.stars)
        self.distgraph = self.galaxy.trade.star_graph
        self.floatinf = float('+inf')  # pragma: no mutate

    def _set_max_slots(self):
        if 500 < self.route_reuse:
            self.max_slots = 10
        elif 250 < self.route_reuse:
            self.max_slots = 12
        elif 125 < self.route_reuse:
            self.max_slots = 14
        else:
            self.max_slots = 15

    def get_landmarks(self, btn=None) -> tuple[list[dict], defaultdict[Any, set]]:
        comp = self.galaxy.trade.components
        max_size = max(comp.values(), default=1)  # pragma: no mutate
        num_slots = min(self.max_slots, self._size_to_landmarks(max_size))
        result = []
        component_landmarks = defaultdict(set)
        all_nodes = list(range(len(self.galaxy.star_mapping)))

        for _ in range(num_slots):
            result.append(dict())

        for component_id in self.galaxy.trade.components:
            comp_size = self.galaxy.trade.components[component_id]
            # No point generating landmarks for a singleton component, as it will never be used in pathfinding
            if 2 > comp_size:
                continue
            slots = min(self.max_slots, self._size_to_landmarks(comp_size), comp_size)

            stars = [item for item in self.galaxy.star_mapping.values() if component_id == item.component]
            max_r = (max(stars, key=lambda item: item.hex.r)).hex.r
            min_q = (min(stars, key=lambda item: item.hex.q)).hex.q
            min_r = (min(stars, key=lambda item: item.hex.r)).hex.r
            stars.sort(key=lambda item: item.wtn, reverse=True)
            first_star = stars[0]
            # active_nodes = [item.index for item in stars]
            # maximum q in component
            source = max(stars, key=lambda item: item.hex.q)
            result[0][component_id] = source.index
            component_landmarks[component_id].add(source.index)

            if 1 == slots:
                continue

            # minimum r in component
            source = min(stars, key=lambda item: item.hex.r if item.index not in component_landmarks[component_id] else max_r)
            result[1][component_id] = source.index
            component_landmarks[component_id].add(source.index)

            if 2 == slots:
                continue

            # minimum s in component
            source = min(stars, key=lambda item: -item.hex.q - item.hex.r if item.index not in component_landmarks[component_id] else -(min_q + min_r))
            result[2][component_id] = source.index
            component_landmarks[component_id].add(source.index)

            assert 3 == len(component_landmarks[component_id]),\
                f"Duplicate landmarks detected on component {component_id} early segment"
            if 3 == slots:
                continue

            if btn is not None:
                btn_split = [(s, n, d) for (s, n, d) in btn if s.component == component_id]
                counters = defaultdict(int)
                for item in btn_split:
                    firstdex = item[0].index
                    if firstdex in component_landmarks[component_id]:
                        continue
                    counters[firstdex] += 1  # pragma: no mutate
                if 0 == len(counters.values()):  # pragma: no mutate
                    btn = None  # pragma: no mutate
                else:
                    max_counter = max(counters.values())
                    max_candidates = {k: v for (k, v) in counters.items() if v == max_counter}
                    source_index = list(max_candidates.keys())[0]
                    result[3][component_id] = source_index
                    component_landmarks[component_id].add(source_index)

                if 4 == slots:  # pragma: no mutate
                    continue

            slotcount = 4 if btn is not None else 3
            seeds = [{component_id: item[component_id]} for item in result if component_id in item]
            assert slotcount == len(seeds), f"S-t transpose-trigger landmark skipped in component {component_id}"
            approx = ApproximateShortestPathForestUnified(source.index, self.galaxy.stars, epsilon=self.galaxy.trade.epsilon, sources=seeds)
            distances = self.galaxy.trade.star_graph.distances_from_target(all_nodes, first_star.index)
            min_cost = self.galaxy.trade.star_graph.min_cost(first_star.index)
            static = np.maximum(distances, min_cost)

            while slotcount < slots:
                lobound = approx.lower_bound_bulk(first_star.index)
                lobound = np.maximum(lobound, static)

                distance_labels = np.ones(self.graph_len) * float('+inf')  # pragma: no mutate
                distance_labels[first_star.index] = 0  # pragma: no mutate

                sp_distances, sp_parents, _, _ = explicit_shortest_path_dijkstra_distance_graph(self.distgraph, first_star.index,
                                                                                          distance_labels)
                inf_set = self.floatinf == sp_distances
                sp_distances[inf_set] = 0
                lobound[inf_set] = 0
                weights = LandmarkAvoidHelper.calc_weights(sp_distances, lobound)
                assert (weights[inf_set] == 0).all(), "Inf-set weights must be zero"  # pragma: no mutate
                sizes = LandmarkAvoidHelper.calc_sizes(weights, sp_parents, component_landmarks[component_id])
                nu_landmark = LandmarkAvoidHelper.traverse_sizes(sizes, first_star.index, sp_parents)
                if nu_landmark is None:
                    slots = slotcount
                    break
                result[slotcount][component_id] = nu_landmark
                component_landmarks[component_id].add(nu_landmark)

                reseed = {component_id: nu_landmark}
                approx.expand_forest(reseed)
                slotcount += 1  # pragma: no mutate

            assert slots == len(component_landmarks[component_id]),\
                f"Duplicate landmarks detected on component {component_id} avoid-powered segment"

        result = [item for item in result if 0 < len(item)]

        return result, component_landmarks

    @staticmethod
    def _size_to_landmarks(size):
        return math.ceil(2.5 * math.log10(size))
