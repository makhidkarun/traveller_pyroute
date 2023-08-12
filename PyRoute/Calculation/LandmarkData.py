"""
Created on Aug 11, 2023

@author: CyberiaResurrection
"""
import numpy as np


class LandmarkData(object):

    def __init__(self, component_size):
        self.counter = 0
        self.component_size = component_size
        self.tracking = np.empty([component_size, 1], dtype=[('star', 'U40'), ('distance', np.uint32)])

    def add_distance(self, starname, stardist):
        self.tracking[self.counter] = (starname, stardist)
        self.counter += 1

    def get_bounds(self, base_dist, minimum):
        result = []

        clicker = 0
        for item in self.tracking:
            act_dist = item['distance'][0]
            if minimum <= abs(act_dist - base_dist):
                starname = item['star'][0]
                result.append((starname, act_dist))

            clicker += 1
            if self.counter <= clicker:
                break

        return result
