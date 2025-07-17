"""
Created on Aug 09, 2023

@author: CyberiaResurrection
"""
from Allies.AllyGen import AllyGen
from Calculation.RouteCalculation import RouteCalculation


class NoneCalculation(RouteCalculation):
    def __init__(self, galaxy):
        super(NoneCalculation, self).__init__(galaxy)

    # Pure HG Base jump distance cost
    distance_weight = [0, 30, 50, 75, 130, 230, 490]

    def generate_routes(self) -> None:
        # self.generate_base_routes()
        pass

    def calculate_routes(self) -> None:
        pass

    def base_route_filter(self, star, neighbor) -> bool:
        return not AllyGen.are_owned_allies(star.alg_code, neighbor.alg_code)

    def base_range_routes(self, star, neighbor) -> int:
        return star.distance(neighbor)

    def route_weight(self, star, target) -> float:
        dist = star.distance(target)
        weight = self.distance_weight[dist]
        return weight

    def cross_check_totals(self) -> None:
        pass
