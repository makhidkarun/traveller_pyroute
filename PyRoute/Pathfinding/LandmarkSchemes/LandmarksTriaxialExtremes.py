"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""
import math


class LandmarksTriaxialExtremes:

    def __init__(self, galaxy):
        self.galaxy = galaxy
        self.max_slots = 3

    def get_landmarks(self, index=False):
        max_size = max(self.galaxy.trade.components.values())
        num_slots = min(self.max_slots, 3 * math.ceil(math.log10(max_size)))
        result = []

        for i in range(num_slots):
            result.append(dict())

        for component_id in self.galaxy.trade.components:
            comp_size = self.galaxy.trade.components[component_id]
            # No point generating landmarks for a singleton component, as it will never be used in pathfinding
            if 2 > comp_size:
                continue
            # slots = min(self.max_slots, 3 * math.ceil(math.log10(comp_size)))

            stars = [item for item in self.galaxy.star_mapping.values() if component_id == item.component]
            # maximum q in component
            source = max(stars, key=lambda item: item.hex.q)
            if index:
                result[0][component_id] = source.index
            else:
                result[0][component_id] = source

            # minimum r in component
            source = min(stars, key=lambda item: item.hex.r)
            if index:
                result[1][component_id] = source.index
            else:
                result[1][component_id] = source

            # minimum s in component
            source = min(stars, key=lambda item: -item.hex.q - item.hex.r)
            if index:
                result[2][component_id] = source.index
            else:
                result[2][component_id] = source

        return result
