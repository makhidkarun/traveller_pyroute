"""
Created on Aug 09, 2023

@author: CyberiaResurrection
"""
import bisect
import functools
import itertools
import logging

import networkx as nx

from PyRoute.AllyGen import AllyGen


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
        self.logger = logging.getLogger('PyRoute.TradeCalculation')
        self.galaxy = galaxy

        # component level tracking
        self.components = dict()

    def generate_routes(self):
        raise NotImplementedError("Base Class")

    def calculate_routes(self):
        raise NotImplementedError("Base Class")

    def route_weight(self, star, target):
        raise NotImplementedError("Base Class")

    def base_route_filter(self, star, neighbor):
        """
            Used in the generate_base_routes to filter (i.e. skip making a route)
            between the star and neighbor. Used to remove un-helpful world links,
            links across borders, etc.
            Return True to filter (ie. skip) creating a link between these two worlds
            Return False to accept (i.e. create) a link between these two worlds.
        """
        raise NotImplementedError("Base Class")

    def base_range_routes(self, star, neighbor):
        """
            Add the route between the pair to the range collection
            Called prior to the setting of the routes/stars based upon
            jump distance.
        """
        raise NotImplementedError("Base Class")

    def generate_base_routes(self):
        self.logger.info('generating jumps...')
        self.galaxy.is_well_formed()
        for star, neighbor in itertools.combinations(self.galaxy.ranges, 2):
            if self.base_route_filter(star, neighbor):
                continue

            dist = self.base_range_routes(star, neighbor)

            if dist <= self.galaxy.max_jump_range:
                weight = self.route_weight(star, neighbor)
                btn = self.get_btn(star, neighbor)
                self.galaxy.stars_shadow.add_edge(star, neighbor, distance=dist,
                                           weight=weight, trade=0, btn=btn, count=0)
                self.check_existing_routes(star, neighbor)

        self.logger.info("base routes: %s  -  ranges: %s" %
                         (self.galaxy.stars_shadow.number_of_edges(),
                          self.galaxy.ranges.number_of_edges()))

    def check_existing_routes(self, star, neighbor):
        for route in star.routes:
            if len(route) == 7:
                route_des = route[3:]
            else:
                route_des = route[8:]
            if neighbor.position == route_des:
                if route.startswith('Xb'):
                    self.galaxy.stars_shadow[star][neighbor]['xboat'] = True
                elif route.startswith('Tr'):
                    self.galaxy.stars_shadow[star][neighbor]['comm'] = True

    @staticmethod
    def get_btn(star1, star2, distance=None):
        """
        Calculate the BTN between two stars, which is the sum of the worlds
        WTNs plus a modifier for types, minus a modifier for distance.
        """
        btn = star1.wtn + star2.wtn
        code1 = star1.tradeCode
        code2 = star2.tradeCode
        if code1.agricultural or code2.agricultural:
            if (code1.agricultural and (code2.nonagricultural or code2.extreme)) or \
               ((code1.nonagricultural or code1.extreme) and code2.agricultural):
                btn += 1
        if code1.industrial or code2.industrial:
            if (code1.nonindustrial and code2.industrial) or (code2.nonindustrial and code1.industrial):
                btn += 1

        if not AllyGen.are_allies(star1.alg_code, star2.alg_code):
            btn -= 1

        if star1.alg_code == 'Wild' or star2.alg_code == 'Wild':
            btn -= 1

        if not distance:
            distance = star1.hex_distance(star2)

        jump_index = bisect.bisect_left(RouteCalculation.btn_jump_range, distance)
        # if distance <= 3:
        #    logging.getLogger('PyRoute.TradeCalculation').info("{} -> index {}".format(distance, jump_index))
        btn += RouteCalculation.btn_jump_mod[jump_index]

        max_btn = (min(star1.wtn, star2.wtn) * 2) + 1
        btn = min(btn, max_btn)
        return btn

    @staticmethod
    def get_passenger_btn(btn, star, neighbor):
        passBTN = btn + star.passenger_btn_mod + neighbor.passenger_btn_mod
        return passBTN

    @staticmethod
    @functools.cache
    def calc_trade(btn):
        """
        Convert the BTN trade number to a credit value.
        """
        if btn & 1:
            trade = (10 ** ((btn - 1) // 2)) * 5
        else:
            trade = 10 ** (btn // 2)

        return trade

    @staticmethod
    @functools.cache
    def calc_passengers(btn):
        trade = 0
        if (btn <= 10):
            trade = 0
        elif btn & 1:
            trade = (10 ** ((btn - 11) // 2)) * 5
        else:
            trade = 10 ** ((btn - 10) // 2)
        return trade

    def calculate_components(self):
        bitz = nx.connected_components(self.galaxy.stars_shadow)
        counter = -1

        for component in bitz:
            counter += 1
            self.components[counter] = len(component)
            for star in component:
                self.galaxy.stars_shadow.nodes[star]['star'].component = counter
                # star.component = counter
        return
