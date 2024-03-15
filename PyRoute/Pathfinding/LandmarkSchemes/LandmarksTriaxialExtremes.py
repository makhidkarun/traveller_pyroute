"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
import math
import numpy as np
from collections import defaultdict

from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
from PyRoute.Pathfinding.LandmarkSchemes.LandmarkAvoidHelper import LandmarkAvoidHelper
from single_source_dijkstra import explicit_shortest_path_dijkstra_distance_graph


class LandmarksTriaxialExtremes:

    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.max_slots = 15
        self.graph_len = len(self.galaxy.stars)
        self.distgraph = self.galaxy.trade.star_graph
        self.floatinf = float('+inf')

    def get_landmarks(self, index=False, btn=None):
        max_size = max(self.galaxy.trade.components.values())
        num_slots = min(self.max_slots, self._size_to_landmarks(max_size))
        result = []
        component_landmarks = defaultdict(set)
        all_nodes = list(range(len(self.galaxy.star_mapping)))

        for i in range(num_slots):
            result.append(dict())

        for component_id in self.galaxy.trade.components:
            comp_size = self.galaxy.trade.components[component_id]
            # No point generating landmarks for a singleton component, as it will never be used in pathfinding
            if 2 > comp_size:
                continue
            slots = min(self.max_slots, self._size_to_landmarks(comp_size))

            stars = [item for item in self.galaxy.star_mapping.values() if component_id == item.component]
            stars.sort(key=lambda item: item.wtn, reverse=True)
            first_star = stars[0]
            # active_nodes = [item.index for item in stars]
            # maximum q in component
            source = max(stars, key=lambda item: item.hex.q)
            if index:
                result[0][component_id] = source.index
                component_landmarks[component_id].add(source.index)
            else:
                result[0][component_id] = source

            if 1 == slots:
                continue

            # minimum r in component
            source = min(stars, key=lambda item: item.hex.r)
            if index:
                result[1][component_id] = source.index
                component_landmarks[component_id].add(source.index)
            else:
                result[1][component_id] = source

            if 2 == slots:
                continue

            # minimum s in component
            source = min(stars, key=lambda item: -item.hex.q - item.hex.r)
            if index:
                result[2][component_id] = source.index
                component_landmarks[component_id].add(source.index)
            else:
                result[2][component_id] = source

            if 3 == slots:
                continue

            # minimum q in component
            source = min(stars, key=lambda item: item.hex.q)
            if index:
                result[3][component_id] = source.index
                component_landmarks[component_id].add(source.index)
            else:
                result[3][component_id] = source

            if 4 == slots:
                continue

            # maximum r in component
            source = max(stars, key=lambda item: item.hex.r)
            if index:
                result[4][component_id] = source.index
                component_landmarks[component_id].add(source.index)
            else:
                result[4][component_id] = source

            if 5 == slots:
                continue

            # maximum s in component
            source = max(stars, key=lambda item: -item.hex.q - item.hex.r)
            if index:
                result[5][component_id] = source.index
                component_landmarks[component_id].add(source.index)
            else:
                result[5][component_id] = source

            if 6 == slots:
                continue

            btn_split = [(s, n, d) for (s, n, d) in btn if s.component == component_id]
            counters = defaultdict(int)
            for item in btn_split:
                firstdex = item[0].index
                seconddex = item[1].index
                if seconddex in component_landmarks[item[0].component]:
                    continue
                counters[firstdex] += 1
            max_counter = max(counters.values())
            max_candidates = {k: v for (k, v) in counters.items() if v == max_counter}
            source = list(max_candidates.keys())[0]
            if index:
                result[6][component_id] = source
                component_landmarks[component_id].add(source)
            else:
                nusource = [item for item in stars if stars.index == source]
                result[6][component_id] = nusource[0]

            if 7 == slots:
                continue

            slotcount = 7
            seeds = [{component_id: item[component_id]} for item in result if component_id in item]
            approx = ApproximateShortestPathForestUnified(source, self.galaxy.stars, epsilon=self.galaxy.trade.epsilon, sources=seeds)
            distances = self.galaxy.trade.star_graph.distances_from_target(all_nodes, first_star.index)
            min_cost = self.galaxy.trade.star_graph.min_cost(all_nodes, first_star.index)
            static = np.maximum(distances, min_cost)

            while slotcount < slots:
                lobound = approx.lower_bound_bulk(all_nodes, first_star.index)
                lobound = np.maximum(lobound, static)

                distance_labels = np.ones(self.graph_len) * float('+inf')
                distance_labels[first_star.index] = 0

                sp_distances, sp_parents = explicit_shortest_path_dijkstra_distance_graph(self.distgraph, first_star.index,
                                                                                          distance_labels)
                inf_set = self.floatinf == sp_distances
                sp_distances[inf_set] = 0
                lobound[inf_set] = 0
                weights = LandmarkAvoidHelper.calc_weights(sp_distances, lobound)
                sizes = LandmarkAvoidHelper.calc_sizes(weights, sp_parents, component_landmarks[component_id])
                nu_landmark = LandmarkAvoidHelper.traverse_sizes(sizes, first_star.index, sp_parents)
                if index:
                    result[slotcount][component_id] = nu_landmark
                    component_landmarks[component_id].add(nu_landmark)
                else:
                    nusource = [item for item in stars if stars.index == nu_landmark]
                    result[slotcount][component_id] = nusource[0]

                reseed = {component_id: nu_landmark}
                approx.expand_forest(reseed)
                slotcount += 1

        return result, component_landmarks

    @staticmethod
    def _size_to_landmarks(size):
        return math.ceil(3 * math.log10(size))
