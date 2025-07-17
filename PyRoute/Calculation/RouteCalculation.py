"""
Created on Aug 09, 2023

@author: CyberiaResurrection
"""
import bisect
import functools
import itertools
import logging
import math
from collections import defaultdict
from typing import Any, Optional

import networkx as nx

from Allies.AllyGen import AllyGen
from Pathfinding.DistanceGraph import DistanceGraph
from Pathfinding.LandmarkSchemes.LandmarksTriaxialExtremes import LandmarksTriaxialExtremes


class RouteCalculation(object):
    # How aggressive should the route finder be about reusing existing routes?
    # Set higher to make the route less likely to be reused, Set lower to make
    # reuse more likely.
    # This works by reducing the weight of the route (see distance_weight)
    # each time a route is selected (making it more likely to be selected
    # next time). Setting this to below 10 results in a lot of main routes
    # with a few spiky connectors. Setting it above 20 results in a lot of
    # nearby routes. This is also (if left as an integer) the lower limit on
    # distance_weight settings.
    route_reuse = 10
    # BTN modifier for range. If the hex distance between two worlds
    # or between two numbers in the jump range array, take jump modifier
    # to the right. E.g distance 4 would be a btn modifier of -3.
    btn_jump_range = [1, 2, 5, 9, 19, 29, 59, 99, 199, 299]
    btn_jump_mod = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10]

    def __init__(self, galaxy):
        from AreaItems.Galaxy import Galaxy
        self.logger = logging.getLogger('PyRoute.TradeCalculation')
        self.galaxy: Galaxy = galaxy
        self.epsilon = 0.2

        # component level tracking
        self.components = dict()
        self.component_landmarks = defaultdict(set)

        self.shortest_path_tree = None
        self.star_graph = None

    def generate_routes(self) -> None:
        raise NotImplementedError("Base Class")

    def calculate_routes(self) -> None:
        raise NotImplementedError("Base Class")

    def route_weight(self, star, target) -> float:
        raise NotImplementedError("Base Class")

    def base_route_filter(self, star, neighbor) -> bool:
        """
            Used in the generate_base_routes to filter (i.e. skip making a route)
            between the star and neighbor. Used to remove un-helpful world links,
            links across borders, etc.
            Return True to filter (ie. skip) creating a link between these two worlds
            Return False to accept (i.e. create) a link between these two worlds.
        """
        raise NotImplementedError("Base Class")

    def base_range_routes(self, star, neighbor) -> Optional[int]:
        """
            Add the route between the pair to the range collection
            Called prior to the setting of the routes/stars based upon
            jump distance.
        """
        raise NotImplementedError("Base Class")

    def generate_base_routes(self) -> None:
        self.logger.info('generating jumps...')
        self.galaxy.is_well_formed()
        raw_ranges = self._raw_ranges()
        ratio = 1 - 1 / self.route_reuse
        multiplier = -1 / math.log(ratio)
        epsilon = max(0.001, self.epsilon)
        for star, neighbor in raw_ranges:
            if self.base_route_filter(star, neighbor):
                continue

            dist = self.base_range_routes(star, neighbor)
            if dist is None:
                continue

            if dist <= self.galaxy.max_jump_range:
                weight = self.route_weight(star, neighbor)
                btn = self.get_btn(star, neighbor, dist)
                excess = (weight / (dist * epsilon) - 1)
                exhaust = 1 + math.ceil(math.log(excess) * multiplier)
                assert (weight - dist) * (ratio ** exhaust) <= epsilon * dist,\
                    'Edge between %s and %s has insufficient exhaust value, %i' % (star, neighbor, exhaust)
                self.galaxy.stars.add_edge(star.index, neighbor.index, distance=dist,
                                           weight=weight, trade=0, btn=btn, count=0, exhaust=exhaust)
                self.check_existing_routes(star, neighbor)

        self.star_graph = DistanceGraph(self.galaxy.stars)

        self.logger.info("base routes: %s  -  ranges: %s" %
                         (self.galaxy.stars.number_of_edges(),
                          self.galaxy.ranges.number_of_edges()))

    def _raw_ranges(self):
        raw_ranges = ((star, neighbour) for (star, neighbour) in itertools.combinations(self.galaxy.ranges, 2) if
                      not star.is_redzone and not neighbour.is_redzone)
        return raw_ranges

    def check_existing_routes(self, star, neighbor) -> None:
        for route in star.routes:
            route_des = route[3:] if len(route) == 7 else route[8:]
            if neighbor.position == route_des:
                if route.startswith('Xb'):
                    self.galaxy.stars[star.index][neighbor.index]['xboat'] = True
                elif route.startswith('Tr'):
                    self.galaxy.stars[star.index][neighbor.index]['comm'] = True

    @staticmethod
    def get_btn(star1, star2, distance=None) -> int:
        """
        Calculate the BTN between two stars, which is the sum of the worlds
        WTNs plus a modifier for types, minus a modifier for distance.
        """
        btn = star1.wtn + star2.wtn
        code1 = star1.tradeCode
        code2 = star2.tradeCode
        if code1.agricultural or code2.agricultural:
            btn += 1 if code1.match_ag_codes(code2) else 0
        if code1.industrial or code2.industrial:
            btn += 1 if code1.match_in_codes(code2) else 0

        if not AllyGen.are_allies(star1.alg_code, star2.alg_code):
            btn -= 1

            if star1.alg_code == 'Wild' or star2.alg_code == 'Wild':
                btn -= 1

        if not distance:
            distance = star1.distance(star2)

        btn += RouteCalculation.get_btn_offset(distance)

        return min(btn, RouteCalculation.get_max_btn(star1.wtn, star2.wtn))

    @staticmethod
    def _get_btn_upper_bound(star1, star2, max_range, min_btn, distance=None):
        """
        Return an _upper bound_ on the BTN between star1 and star2.  If the upper bound on BTN
        doesn't meet/beat the minimum BTN, then the _actual_ BTN, which also doesn't meet/beat
        the minimum, doesn't need to be calculated.  If star1 and star2 are less than the supplied
        max_range apart in pc, set the returned BTN upper bound to greater of upper-bounded BTN and
        supplied min_btn.
        """
        # Assuming BTN, as per self.get_btn, is boosted by both agricultural and industrial matches
        btn = star1.wtn + star2.wtn + 2

        if not distance:
            distance = star1.distance(star2)

        btn += RouteCalculation.get_btn_offset(distance)
        btn = min(btn, RouteCalculation.get_max_btn(star1.wtn, star2.wtn))
        return min_btn if min_btn > btn and distance <= max_range else btn

    @staticmethod
    def get_passenger_btn(btn, star, neighbor) -> int:
        passBTN = btn + star.passenger_btn_mod + neighbor.passenger_btn_mod
        return passBTN

    @staticmethod
    @functools.cache
    def get_btn_offset(distance) -> int:
        jump_index = bisect.bisect_left(RouteCalculation.btn_jump_range, distance)
        return RouteCalculation.btn_jump_mod[jump_index]

    @staticmethod
    @functools.cache
    def get_vol_offset(distance) -> int:
        if distance < 50:
            return 0
        elif distance < 100:
            return -1
        elif distance < 500:
            return -2
        elif distance < 1000:
            return -3
        return -4

    @staticmethod
    @functools.cache
    def get_max_btn(star_wtn, neighbour_wtn) -> int:
        if neighbour_wtn > star_wtn:
            return RouteCalculation.get_max_btn(neighbour_wtn, star_wtn)
        return (neighbour_wtn * 2) + 1

    @staticmethod
    @functools.cache
    def calc_trade(btn) -> int:
        """
        Convert the BTN trade number to a credit value.
        """
        trade = 10 ** ((btn - 1) // 2) * 5 if btn & 1 else 10 ** (btn // 2)

        return trade

    @staticmethod
    def calc_trade_tonnage(btn, distance) -> int:
        offset = RouteCalculation.get_vol_offset(distance)
        dton = btn + offset - 9

        if 0 > dton:
            return 0
        return RouteCalculation.calc_trade(dton)

    @staticmethod
    @functools.cache
    def calc_passengers(btn) -> int:
        trade = 0
        if (btn <= 10):
            trade = 0
        elif btn & 1:
            trade = (10 ** ((btn - 11) // 2)) * 5
        else:
            trade = 10 ** ((btn - 10) // 2)
        return trade

    def calculate_components(self) -> None:
        bitz = nx.connected_components(self.galaxy.stars)
        counter = -1

        for component in bitz:
            counter += 1
            self.components[counter] = len(component)
            for star in component:
                self.galaxy.star_mapping[star].component = counter
        return

    def get_landmarks(self, index=False, btn=None) -> tuple[list[dict], defaultdict[Any, set]]:
        schema = LandmarksTriaxialExtremes(self.galaxy)
        return schema.get_landmarks(index, btn=btn)

    def unilateral_filter(self, star) -> bool:
        """
        Routes can be filtered either bilaterally (some combination of the endpoints means the route needs filtering)
        or unilaterally, where at least one of the endpoints requires the route to be filtered (eg red trade zone in
        TradeCalculation).

        @type star: Star
        @param star: The star object to check
        @return: Whether the star can be unilaterally filtered
        """
        return False

    def is_sector_trade_balanced(self) -> None:
        pass

    def is_sector_pass_balanced(self) -> None:
        pass

    def is_sector_trade_volume_balanced(self) -> None:
        pass

    def is_allegiance_trade_balanced(self) -> None:
        pass

    def is_allegiance_pass_balanced(self) -> None:
        pass

    def is_allegiance_trade_volume_balanced(self) -> None:
        pass

    def multilateral_balance_trade(self) -> None:
        pass

    def multilateral_balance_pass(self) -> None:
        pass

    def multilateral_balance_trade_volume(self) -> None:
        pass
