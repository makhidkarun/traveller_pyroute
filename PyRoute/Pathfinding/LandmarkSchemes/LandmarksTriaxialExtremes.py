"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
import math
from collections import defaultdict


class LandmarksTriaxialExtremes:

    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.max_slots = 6

    def get_landmarks(self, index=False):
        max_size = max(self.galaxy.trade.components.values())
        num_slots = min(self.max_slots, 3 * math.ceil(math.log10(max_size)))
        result = []
        component_landmarks = defaultdict(set)

        for i in range(num_slots):
            result.append(dict())

        for component_id in self.galaxy.trade.components:
            comp_size = self.galaxy.trade.components[component_id]
            # No point generating landmarks for a singleton component, as it will never be used in pathfinding
            if 2 > comp_size:
                continue
            slots = min(self.max_slots, 3 * math.ceil(math.log10(comp_size)))

            stars = [item for item in self.galaxy.star_mapping.values() if component_id == item.component]
            stars.sort(key=lambda item: item.wtn, reverse=True)
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

        return result, component_landmarks
