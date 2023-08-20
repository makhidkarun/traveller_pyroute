"""
Created on Aug 09, 2023

@author: CyberiaResurrection
"""
from PyRoute.AllyGen import AllyGen
from PyRoute.Calculation.RouteCalculation import RouteCalculation


class OwnedWorldCalculation(RouteCalculation):
    def __init__(self, galaxy):
        super(OwnedWorldCalculation, self).__init__(galaxy)

    # Pure HG Base jump distance cost
    distance_weight = [0, 30, 50, 75, 130, 230, 490]

    def generate_routes(self):
        self.generate_base_routes()
        pass

    def calculate_routes(self):
        pass

    def base_route_filter(self, star, neighbor):
        return not AllyGen.are_owned_allies(star.alg_code, neighbor.alg_code)

    def base_range_routes(self, star, neighbor):
        return star.hex_distance(neighbor)

    def route_weight(self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        return weight
