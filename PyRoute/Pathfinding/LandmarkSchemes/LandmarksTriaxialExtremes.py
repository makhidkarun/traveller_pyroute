"""
Created on Feb 19, 2024

@author: CyberiaResurrection
"""


class LandmarksTriaxialExtremes:

    def __init__(self, galaxy):
        self.galaxy = galaxy

    def get_landmarks(self, index=False):
        result = []

        result.append(dict())
        result.append(dict())
        result.append(dict())
        for component_id in self.galaxy.trade.components:
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
