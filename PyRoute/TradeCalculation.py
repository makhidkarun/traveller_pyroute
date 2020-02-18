"""
Created on Mar 15, 2014

@author: tjoneslo
"""
import bisect
import logging
import itertools
import networkx as nx
from AllyGen import AllyGen
from Star import Star


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
        for star, neighbor in itertools.combinations(self.galaxy.ranges, 2):
            dist = star.hex_distance(neighbor)
            if self.base_route_filter(star, neighbor):
                continue

            self.base_range_routes(star, neighbor)

            if dist <= self.galaxy.max_jump_range:
                weight = self.route_weight(star, neighbor)
                btn = self.get_btn(star, neighbor)
                self.galaxy.stars.add_edge(star, neighbor, distance=dist,
                                           weight=weight, trade=0, btn=btn, count=0)
                self.check_existing_routes(star, neighbor)

        self.logger.info("base routes: %s  -  ranges: %s" %
                         (self.galaxy.stars.number_of_edges(),
                          self.galaxy.ranges.number_of_edges()))

    def check_existing_routes(self, star, neighbor):
        for route in star.routes:
            if len(route) == 7:
                route_des = route[3:]
            else:
                route_des = route[8:]
            if neighbor.position == route_des:
                if route.startswith('Xb'):
                    self.galaxy.stars[star][neighbor]['xboat'] = True
                elif route.startswith('Tr'):
                    self.galaxy.stars[star][neighbor]['comm'] = True

    @staticmethod
    def get_btn(star1, star2, distance=None):
        """
        Calculate the BTN between two stars, which is the sum of the worlds
        WTNs plus a modifier for types, minus a modifier for distance.
        """
        btn = star1.wtn + star2.wtn
        if (star1.tradeCode.agricultural and (star2.tradeCode.nonagricultural or star2.tradeCode.extreme)) or \
                ((star1.tradeCode.nonagricultural or star1.tradeCode.extreme) and star2.tradeCode.agricultural):
            btn += 1
        if (star1.tradeCode.nonindustrial and star2.tradeCode.industrial) or \
                (star2.tradeCode.nonindustrial and star1.tradeCode.industrial):
            btn += 1

        if not AllyGen.are_allies(star1.alg_code, star2.alg_code):
            btn -= 1

        if star1.alg_code == 'Wild' or star2.alg_code == 'Wild':
            btn -= 1

        if not distance:
            distance = star1.hex_distance(star2)
        jump_index = bisect.bisect_left(TradeCalculation.btn_jump_range, distance)
        # if distance <= 3:
        #    logging.getLogger('PyRoute.TradeCalculation').info("{} -> index {}".format(distance, jump_index))
        btn += TradeCalculation.btn_jump_mod[jump_index]

        max_btn = (min(star1.wtn, star2.wtn) * 2) + 1
        btn = min(btn, max_btn)
        return btn

    @staticmethod
    def get_passenger_btn(btn, star, neighbor):
        rich = 1 if star.tradeCode.rich or neighbor.tradeCode.rich else 0
        subsector_capital = 1 if star.tradeCode.subsector_capital or neighbor.tradeCode.subsector_capital else 0
        sector_capital = 2 if star.tradeCode.sector_capital or neighbor.tradeCode.sector_capital else 0
        other_capital = 2 if star.tradeCode.other_capital or neighbor.tradeCode.other_capital else 0

        passBTN = btn + rich + subsector_capital + sector_capital + other_capital
        return passBTN

    @staticmethod
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
    def calc_passengers(btn):
        trade = 0
        if (btn <= 10):
            trade = 0
        elif btn & 1:
            trade = (10 ** ((btn - 11) // 2)) * 5
        else:
            trade = 10 ** ((btn - 10) // 2)
        return trade


class NoneCalculation(RouteCalculation):
    def __init__(self, galaxy):
        super(NoneCalculation, self).__init__(galaxy)

    # Pure HG Base jump distance cost
    distance_weight = [0, 30, 50, 75, 130, 230, 490]

    def generate_routes(self):
        # self.generate_base_routes()
        pass

    def calculate_routes(self):
        pass

    def base_route_filter(self, star, neighbor):
        if not AllyGen.are_owned_allies(star.alg_code, neighbor.alg_code):
            return True
        return False

    def base_range_routes(self, star, neighbor):
        pass

    def route_weight(self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        return weight


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
        pass

    def route_weight(self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        return weight


class XRouteCalculation(RouteCalculation):
    distance_weight = [0, 95, 90, 85, 80, 75, 70]
    capSec_weight = [0, 95, 90, 85, 75, 75, 70]
    inSec_weight = [0, 140, 110, 85, 70, 95, 140]
    impt_weight = [0, 90, 80, 70, 70, 110, 140]

    def __init__(self, galaxy):
        super(XRouteCalculation, self).__init__(galaxy)
        self.route_reuse = 5

    def base_range_routes(self, star, neighbor):
        pass

    def base_route_filter(self, star, neighbor):
        if not AllyGen.are_allies(star.alg_code, neighbor.alg_code):
            return True
        if not AllyGen.imperial_align(star.alg_code):
            return True
        if star.zone in ['R', 'F'] or neighbor.zone in ['R', 'F']:
            return True

        return False

    def generate_routes(self):
        self.distance_weight = self.capSec_weight
        self.generate_base_routes()
        self.capital = [star for star in self.galaxy.ranges if \
                        AllyGen.imperial_align(star.alg_code) and star.tradeCode.other_capital]
        self.secCapitals = [star for star in self.galaxy.ranges if \
                            AllyGen.imperial_align(star.alg_code) and star.tradeCode.sector_capital]
        self.subCapitals = [star for star in self.galaxy.ranges if \
                            AllyGen.imperial_align(star.alg_code) and star.tradeCode.subsector_captial]

    def routes_pass_1(self):
        # Pass 1: Get routes at J6  Capital and sector capitals 
        # This should be 1 element long
        self.logger.info(self.capital)
        if len(self.capital) == 0:
            return
        for star in self.secCapitals:
            self.get_route_between(self.capital[0], star, self.calc_trade(25), Star.heuristicDistance)

        for star in self.secCapitals:
            localCapital = {'coreward': None, 'spinward': None, 'trailing': None, 'rimward': None,
                            'corespin': None, 'coretrail': None, 'rimspin': None, 'rimtrail': None}

            if star.sector.coreward:
                localCapital['coreward'] = self.find_sector_capital(star.sector.coreward)
                if localCapital['coreward'] and localCapital['coreward'].sector.spinward:
                    localCapital['corespin'] = self.find_sector_capital(localCapital['coreward'].sector.spinward)
                if localCapital['coreward'] and localCapital['coreward'].sector.trailing:
                    localCapital['coretrail'] = self.find_sector_capital(localCapital['coreward'].sector.trailing)
            if star.sector.rimward:
                localCapital['rimward'] = self.find_sector_capital(star.sector.rimward)
                if localCapital['rimward'] and localCapital['rimward'].sector.spinward:
                    localCapital['rimspin'] = self.find_sector_capital(localCapital['rimward'].sector.spinward)
                if localCapital['rimward'] and localCapital['rimward'].sector.trailing:
                    localCapital['rimtrail'] = self.find_sector_capital(localCapital['rimward'].sector.trailing)
            if star.sector.spinward:
                localCapital['spinward'] = self.find_sector_capital(star.sector.spinward)
                if localCapital['spinward'] and localCapital['spinward'].sector.coreward and not localCapital[
                    'corespin']:
                    localCapital['corespin'] = self.find_sector_capital(localCapital['spinward'].sector.coreward)
                if localCapital['spinward'] and localCapital['spinward'].sector.rimward and not localCapital['rimspin']:
                    localCapital['rimwspin'] = self.find_sector_capital(localCapital['spinward'].sector.rimward)
            if star.sector.trailing:
                localCapital['trailing'] = self.find_sector_capital(star.sector.trailing)
                if localCapital['trailing'] and localCapital['trailing'].sector.coreward and not localCapital[
                    'coretrail']:
                    localCapital['coretrail'] = self.find_sector_capital(localCapital['trailing'].sector.coreward)
                if localCapital['trailing'] and localCapital['trailing'].sector.rimward and not localCapital[
                    'rimtrail']:
                    localCapital['rimtrail'] = self.find_sector_capital(localCapital['trailing'].sector.rimward)

            for neighbor in localCapital.values():
                if neighbor and not self.galaxy.ranges.has_edge(star, neighbor):
                    self.get_route_between(star, neighbor, self.calc_trade(25), Star.heuristicDistance)

    def routes_pass_2(self):
        # Step 2a - re-weight the routes to be more weighted to J4 than J6
        self.reweight_routes(self.inSec_weight)

        secCapitals = self.secCapitals + self.capital
        for sector in self.galaxy.sectors.values():

            secCap = [star for star in secCapitals if star.sector == sector]
            self.logger.info(secCap)
            subCap = [star for star in self.subCapitals if star.sector == sector]

            if len(secCap) == 0:
                if len(subCap) == 0:
                    continue
                else:
                    self.logger.info("{} has subsector capitals but no sector capital".format(sector.name))
                    for star in subCap:
                        capital = self.find_nearest_capital(star, secCapitals)
                        self.get_route_between(capital[0], star, self.calc_trade(23), Star.heuristicDistance)
            else:
                for star in subCap:
                    if self.galaxy.ranges.has_edge(secCap[0], star):
                        continue
                    self.get_route_between(secCap[0], star, self.calc_trade(23), Star.heuristicDistance)

        for star in self.subCapitals:
            routes = [neighbor for neighbor in self.subCapitals if \
                      neighbor != star and neighbor.hex_distance(star) <= 40]
            for neighbor in routes:
                self.get_route_between(star, neighbor, self.calc_trade(23), Star.heuristicDistance)

    def routes_pass_3(self):
        self.reweight_routes(self.impt_weight)
        important = [star for star in self.galaxy.ranges if \
                     AllyGen.imperial_align(star.alg_code) and star.tradeCount == 0
                     and (star.importance >= 4 or 'D' in star.baseCode or 'W' in star.baseCode)]

        jumpStations = [star for star in self.galaxy.ranges if star.tradeCount > 0]

        self.logger.info('Important worlds: {}, jump stations: {}'.format(len(important), len(jumpStations)))

        important2 = []
        for star in important:
            if star in jumpStations:
                continue
            for neighbor in self.galaxy.stars.neighbors_iter(star):
                if star.hex_distance(neighbor) > 4:
                    continue
                if neighbor in jumpStations:
                    self.get_route_between(star, neighbor, self.calc_trade(21), None)
                    jumpStations.append(star)
            if star.tradeCount == 0:
                important2.append(star)

        important3 = []
        for star in important2:
            for neighbor in self.galaxy.stars.neighbors_iter(star):
                if neighbor in jumpStations:
                    self.get_route_between(star, neighbor, self.calc_trade(21), None)
                    jumpStations.append(star)
            if star.tradeCount == 0:
                important3.append(star)
                self.logger.info("No route for important world: {}".format(star))

        capitalList = self.capital + self.secCapitals + self.subCapitals
        for star in important3:
            capital = self.find_nearest_capital(star, capitalList)
            self.get_route_between(capital[0], star, self.calc_trade(21), None)

    def calculate_routes(self):
        self.logger.info('XRoute pass 1')
        self.routes_pass_1()

        self.logger.info('XRoute pass 2')
        self.routes_pass_2()

        self.logger.info('XRoute pass 3')
        self.routes_pass_3()

    def reweight_routes(self, weightList):
        self.distance_weight = weightList
        for (star, neighbor, data) in self.galaxy.stars.edges(data=True):
            data['weight'] = self.route_weight(star, neighbor)
            for _ in range(1, min(data['count'], 5)):
                data['weight'] -= data['weight'] // self.route_reuse

    def find_nearest_capital(self, world, capitals):
        dist = (None, 9999)
        for capital in capitals:
            newDist = capital.hex_distance(world)
            if newDist < dist[1]:
                dist = (capital, newDist)
        return dist

    def find_sector_capital(self, sector):
        for world in self.secCapitals:
            if world.sector == sector:
                return world
        return None

    def get_route_between(self, star, target, trade, heuristic):
        try:
            route = nx.astar_path(self.galaxy.stars, star, target, heuristic)
        except nx.NetworkXNoPath:
            return
        self.galaxy.ranges.add_edge(star, target, distance=star.hex_distance(target))

        distance = 0
        start = route[0]
        start.tradeCount += 1
        for end in route[1:]:
            distance += start.hex_distance(end)
            end.tradeCount += 1
            self.galaxy.stars[start][end]['trade'] = max(trade, self.galaxy.stars[start][end]['trade'])
            self.galaxy.stars[start][end]['count'] += 1
            self.galaxy.stars[start][end]['weight'] -= \
                self.galaxy.stars[start][end]['weight'] // self.route_reuse
            start = end

        self.galaxy.ranges[route[0]][route[-1]]['actual distance'] = distance
        self.galaxy.ranges[route[0]][route[-1]]['jumps'] = len(route) - 1

    def route_weight(self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        if star.port in 'CDEX':
            weight += 25
        if star.port in 'DEX':
            weight += 25
        if star.zone in 'RF' or target.zone in 'RF':
            weight += 50
        if star.popCode == 0 or target.popCode == 0:
            weight += 25
        weight -= 3 * (star.importance + target.importance)
        weight -= 6 if 'S' in star.baseCode or 'S' in target.baseCode else 0
        weight -= 6 if 'W' in star.baseCode or 'W' in target.baseCode else 0
        weight -= 3 if 'N' in star.baseCode or 'N' in target.baseCode else 0
        weight -= 3 if 'D' in star.baseCode or 'D' in target.baseCode else 0
        weight -= 6 if star.tradeCode.subsecor_capital or target.tradeCode.subsector_capital else 0
        weight -= 6 if star.tradeCode.other_capital or target.tradeCode.other_capital else 0
        weight -= 6 if star.tradeCode.sector_capital or target.tradeCode.sector_capital else 0

        return weight


class TradeCalculation(RouteCalculation):
    """
    Perform the trade calculations by generating the routes
    between all the trade pairs
    """
    # Weight for route over a distance. The relative cost for
    # moving freight between two worlds a given distance apart
    # in a single jump.
    # These are made up from whole cloth.          
    # distance_weight = [0, 30, 50, 70, 90, 120, 140 ]

    # GT Weights based upon one pass estimate
    # distance_weight = [0, 30, 50, 70, 110, 170, 300]

    # Pure HG weights
    # distance_weight = [0, 30, 50, 75, 130, 230, 490]

    # MGT weights
    # distance_weight = [0, 30, 60, 105, 190, 410, 2470]

    # T5 Weights, now with Hop Drive
    distance_weight = [0, 30, 50, 75, 130, 230, 490, 9999, 9999, 9999, 300]

    # max_connections = [6, 18, 36, 60, 90, 126, 168, 216, 270, 330]
    max_connections = [6, 12, 18, 30, 45, 63, 84, 108, 135, 165]

    # Set an initial range for influence for worlds based upon their
    # wtn. For a given world look up the range given by (wtn-8) (min 0), 
    # and the system checks every other world in that range for trade 
    # opportunity. See the btn_jump_mod and min btn to see how  
    # worlds are excluded from this list. 
    btn_range = [2, 9, 29, 59, 99, 299]

    # Maximum WTN to process routes for
    max_wtn = 15

    def __init__(self, galaxy, min_btn=13, route_btn=8, route_reuse=10):
        super(TradeCalculation, self).__init__(galaxy)

        # Minimum BTN to calculate routes for. BTN between two worlds less than
        # this value are ignored. Set lower to have more routes calculated, but
        # may not have have an impact on the overall trade flows.
        self.min_btn = min_btn

        # Minimum WTN to process routes for
        self.min_wtn = route_btn

        # Override the default setting for route-reuse from the base class
        # based upon program arguments. 
        self.route_reuse = route_reuse

    def base_route_filter(self, star, neighbor):
        if star.zone in ['R', 'F'] or neighbor.zone in ['R', 'F']:
            return True
        if star.tradeCode.barren or neighbor.tradeCode.barren:
            return True
        return False

    def base_range_routes(self, star, neighbor):
        dist = star.hex_distance(neighbor)
        max_dist = self.btn_range[min(max(0, max(star.wtn, neighbor.wtn) - self.min_wtn), 5)]
        btn = self.get_btn(star, neighbor, dist)
        # add all the stars in the BTN range, but  skip this pair
        # if there there isn't enough trade to warrant a trade check
        if dist <= max_dist and btn >= self.min_btn:
            passBTN = self.get_passenger_btn(btn, star, neighbor)
            self.galaxy.ranges.add_edge(star, neighbor, distance=dist,
                                        btn=btn,
                                        passenger_btn=passBTN)

    def generate_routes(self):
        """
        Generate the basic routes between all the stars. This creates two sets
        of routes.
        - Stars: The basic J4 (max-jump) routes for all pairs of stars.
        - Ranges: The set of trade routes needing to be calculated.
        """
        self.generate_base_routes()

        self.logger.info('calculating routes...')
        for star in self.galaxy.stars:
            if len(self.galaxy.stars[star]) < 11:
                continue
            neighbor_routes = [(s, n, d) for (s, n, d) in self.galaxy.stars.edges([star], True)]
            # Need to do two sorts here:
            # BTN low to high to find them first
            # Range high to low to find them first 
            neighbor_routes.sort(key=lambda tn: tn[2]['btn'])
            neighbor_routes.sort(key=lambda tn: tn[2]['distance'], reverse=True)

            length = len(neighbor_routes)

            # remove edges from the list which are 
            # A) The most distant first
            # B) The lowest BTN for equal distant routes
            # If the neighbor has only a few (<15) connections don't remove that one
            # until there are 20 connections left. 
            # This may be reduced by other stars deciding you are too far away.             
            for (s, n, d) in neighbor_routes:
                if len(self.galaxy.stars[n]) < 15:
                    continue
                if length <= self.max_connections[self.galaxy.max_jump_range - 1]:
                    break
                if d.get('xboat', False) or d.get('comm', False):
                    continue
                self.galaxy.stars.remove_edge(s, n)
                length -= 1
        self.logger.info('Final route count {}'.format(self.galaxy.stars.number_of_edges()))

    def calculate_routes(self):
        """
        The base calculate routes. Read through all the stars in WTN order.
        Do this order to allow the higher trade routes establish the basic routes
        for the lower routes to follow.
        """
        self.logger.info('sorting routes...')
        btn = [(s, n, d) for (s, n, d) in self.galaxy.ranges.edges(data=True)]
        btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        base_btn = 0
        counter = 0
        processed = 0
        total = len(btn)
        for (star, neighbor, data) in btn:
            if base_btn != data['btn']:
                if counter > 0:
                    self.logger.info('processed {} routes at BTN {}'.format(counter, base_btn))
                base_btn = data['btn']
                counter = 0
            if total > 100 and processed % (total // 20) == 0:
                self.logger.info('processed {} routes, at {}%'.format(processed, processed // (total // 100)))
            self.get_trade_between(star, neighbor)
            counter += 1
            processed += 1
        self.logger.info('processed {} routes at BTN {}'.format(counter, base_btn))

    def get_trade_between(self, star, target):
        """
        Calculate the route between star and target
        If we can't find a route (no Jump 4 (or N) path), skip this pair
        otherwise update the trade information.
        """
        try:
            route = nx.astar_path(self.galaxy.stars, star, target, Star.heuristicDistance)
        except nx.NetworkXNoPath:
            return

        # TODO: Generate the routes in both directions- A->B and B->A. 
        # if they produce different routes (they might), select the the lower cost one
        # Update the trade route (edges)
        tradeCr, tradePass = self.route_update_simple(route)

        if star.sector != target.sector:
            star.sector.stats.tradeExt += tradeCr // 2
            target.sector.stats.tradeExt += tradeCr // 2
            star.sector.subsectors[star.subsector()].stats.tradeExt += tradeCr // 2
            target.sector.subsectors[target.subsector()].stats.tradeExt += tradeCr // 2
            star.sector.stats.passengers += tradePass // 2
            target.sector.stats.passengers += tradePass // 2
        else:
            star.sector.stats.trade += tradeCr
            star.sector.stats.passengers += tradePass
            if star.subsector() == target.subsector():
                star.sector.subsectors[star.subsector()].stats.trade += tradeCr
            else:
                star.sector.subsectors[star.subsector()].stats.tradeExt += tradeCr // 2
                target.sector.subsectors[target.subsector()].stats.tradeExt += tradeCr // 2

        if AllyGen.are_allies(star.alg_code, target.alg_code):
            self.galaxy.alg[AllyGen.same_align(star.alg_code)].stats.trade += tradeCr
            self.galaxy.alg[AllyGen.same_align(star.alg_code)].stats.passengers += tradePass
        else:
            self.galaxy.alg[AllyGen.same_align(star.alg_code)].stats.tradeExt += tradeCr // 2
            self.galaxy.alg[AllyGen.same_align(target.alg_code)].stats.tradeExt += tradeCr // 2
            self.galaxy.alg[AllyGen.same_align(star.alg_code)].stats.passengers += tradePass // 2
            self.galaxy.alg[AllyGen.same_align(target.alg_code)].stats.passengers += tradePass // 2

        self.galaxy.stats.trade += tradeCr
        self.galaxy.stats.passengers += tradePass

    def route_update_simple(self, route):
        """
        Update the trade calculations based upon the route selected.
        - add the trade values for the worlds, and edges
        - add a count for the worlds and edges
        - reduce the weight of routes used to allow more trade to flow
        """
        distance = 0
        start = route[0]
        for end in route[1:]:
            distance += start.hex_distance(end)
            start = end

        # Internal statistics
        self.galaxy.ranges[route[0]][route[-1]]['actual distance'] = distance
        self.galaxy.ranges[route[0]][route[-1]]['jumps'] = len(route) - 1

        # Gather basic statistics. 
        tradeBTN = self.get_btn(route[0], route[-1], distance)
        tradeCr = self.calc_trade(tradeBTN)
        route[0].tradeIn += tradeCr // 2
        route[-1].tradeIn += tradeCr // 2
        tradePassBTN = self.get_passenger_btn(tradeBTN, route[0], route[-1])
        tradePass = self.calc_passengers(tradePassBTN)

        route[0].passIn += tradePass
        route[-1].passIn += tradePass

        start = route[0]
        for end in route[1:]:
            end.tradeOver += tradeCr if end != route[-1] else 0
            end.tradeCount += 1 if end != route[-1] else 0
            end.passOver += tradePass if end != route[-1] else 0
            self.galaxy.stars[start][end]['trade'] += tradeCr
            self.galaxy.stars[start][end]['count'] += 1
            self.galaxy.stars[start][end]['weight'] -= \
                self.galaxy.stars[start][end]['weight'] / self.route_reuse
            start = end

        return (tradeCr, tradePass)

    def route_update_skip(self, route, tradeCr):
        """
        Unused: This was an experiment in adding skip-routes,
        i.e. longer, already calculated routes, to allow the
        A* route finder to work faster. This needs better system
        for selecting these routes as too many got added and it
        would slow the system down.
        """
        dist = 0
        weight = 0
        start = route[0]
        usesJumpRoute = False
        for end in route[1:]:
            end.tradeOver += tradeCr if end != route[-1] else 0
            if self.galaxy.routes.has_edge(start, end) and self.galaxy.routes[start][end].get('route', False):
                routeDist, routeWeight = self.route_update(self.galaxy.routes[start][end]['route'], tradeCr)
                dist += routeDist
                weight += routeWeight
                usesJumpRoute = True
                # Reduce the weight of this route. 
                # As the higher trade routes create established routes 
                # which are more likely to be followed by lower trade routes
            elif self.galaxy.stars.has_edge(start, end):
                self.galaxy.stars[start][end]['trade'] += tradeCr
                dist += self.galaxy.stars[start][end]['distance']
                weight += self.galaxy.stars[start][end]['weight']
            else:
                print((start, end, self.galaxy.routes.has_edge(start, end)))
            start = end

        if len(route) > 6 and not usesJumpRoute:
            weight -= weight // self.route_reuse
            self.galaxy.routes.add_edge(route[0], route[-1], distance=dist,
                                        weight=weight, trade=0, route=route,
                                        btn=0)
            start = route[0]
            for end in route[1:]:
                # self.galaxy.routes.remove_edge(start, end)
                start = end
        return dist, weight

    def get_trade_to(self, star, trade):
        """
        Unused:
        Calculate the trade route between starting star and all potential target.
        This was the direct copy algorithm from nroute for doing route calculation
        It was replaced by the process above which works better with the
        pythonic data structures. It remains for historical purposes.
        """

        # Loop through all the stars in the ranges list, i.e. all potential stars
        # within the range of the BTN route. 
        for (newstar, target) in self.galaxy.ranges.edges(star, False):
            if newstar != star:
                self.logger.error("edges found newstar %s != star %s" % (newstar, star))
                continue

            # Skip this pair if we've already done the trade
            # usually from the other star first. 
            if target in star.tradeMatched:
                continue

            # Calculate the route between the stars
            # If we can't find a route (no jump 4 path) skip this pair
            try:
                route = nx.astar_path(self.galaxy.stars, star, target)
            except nx.NetworkXNoPath:
                continue

            # Gather basic statistics. 
            tradeBTN = self.get_btn(star, target)
            tradeCr = self.calc_trade(tradeBTN)
            star.tradeIn += tradeCr
            target.tradeIn += tradeCr
            target.tradeMatched.append(star)

            # Update the trade route (edges)
            start = star
            for end in route:
                if end == start:
                    continue
                self.galaxy.stars[start][end]['trade'] += tradeCr
                # Reduce the weight of this route. 
                # As the higher trade routes create established routes 
                # which are more likely to be followed by lower trade routes
                self.galaxy.stars[start][end]['weight'] -= \
                    self.galaxy.stars[start][end]['weight'] / self.route_reuse
                end.tradeOver += tradeCr if end != target else 0
                start = end

    def route_weight(self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        if target.alg_code != star.alg_code:
            weight += 25
        if star.port in 'CDEX':
            weight += 25
        if star.port in 'DEX':
            weight += 25
        weight -= star.importance + target.importance
        return weight


class CommCalculation(RouteCalculation):
    # Weight for route over a distance. The relative cost for
    # moving between two worlds a given distance apart
    # in a single jump.         
    distance_weight = [0, 70, 65, 60, 70, 100, 130, 9999, 9999, 9999, 300]

    def __init__(self, galaxy, reuse=5):
        super(CommCalculation, self).__init__(galaxy)
        self.route_reuse = reuse
        self.min_importance = 4

    def base_route_filter(self, star, neighbor):
        if star.zone in ['R', 'F'] or neighbor.zone in ['R', 'F']:
            return True
        if not AllyGen.are_allies(star.alg_code, neighbor.alg_code):
            return True
        return False

    def base_range_routes(self, star, neighbor):
        if not getattr(self.galaxy.alg[star.alg_base_code], 'min_importance', False):
            return
        min_importance = self.galaxy.alg[star.alg_base_code].min_importance
        if self.endpoint_selection(star, min_importance) and self.endpoint_selection(neighbor, min_importance):
            dist = star.hex_distance(neighbor)

            if ((self.capitals(star) or self.bases(star)) and
                (self.capitals(neighbor) or self.bases(neighbor)) and dist < 100) or \
                    dist < 20:
                flags = [self.capitals(star) and self.capitals(neighbor),
                         self.capitals(star) or self.capitals(neighbor),
                         self.bases(star) or self.bases(neighbor),
                         self.important(star, min_importance) or self.important(neighbor, min_importance),
                         self.is_rich(star) or self.is_rich(neighbor)]
                self.galaxy.ranges.add_edge(star, neighbor, distance=dist, flags=flags)

    def capitals(self, star):
        # Capital of sector, subsector, or empire are in the list
        return star.tradeCode.capital

    def bases(self, star):
        # if it has a Depot, Way station, or XBoat station,
        # or external naval base or (aslan) Tlaukhu base
        return len({'D', 'W', 'K', 'T'} & set(star.baseCode)) > 0

    def comm_bases(self, star):
        # Imperial scout or naval base, external military base, or Aslan clan base
        return len({'S', 'N', 'M', 'R'} & set(star.baseCode)) > 0

    def important(self, star, min_importance):
        return star.importance > min_importance

    def is_rich(self, star):
        return star.ru > 10000

    def endpoint_selection(self, star, min_importance):
        return self.capitals(star) or self.bases(star) or \
               self.important(star, min_importance) or self.is_rich(star)

    def generate_routes(self):
        for alg in self.galaxy.alg.values():
            # No comm routes for the non-aligned worlds. 
            if AllyGen.is_nonaligned(alg):
                continue
            # No comm routes for small empires
            if len(alg.worlds) < 25:
                self.logger.info("skipping Alg: {} with {} worlds".format(alg.name, len(alg.worlds)))
                continue
            alg.min_importance = 4
            self.logger.info("Alg {} has {} worlds".format(alg.name, len(alg.worlds)))
            ix5_worlds = [star for star in alg.worlds if star.importance > alg.min_importance]
            self.logger.info("Alg {} has {} ix 5 worlds".format(alg.name, len(ix5_worlds)))
            if len(ix5_worlds) == 0 or len(ix5_worlds) < len(alg.worlds) / 1000:
                alg.min_importance = 3

                ix4_worlds = [star for star in alg.worlds if star.importance > 3]
                self.logger.info("Alg {} has {} ix 5/4 worlds".format(alg.name, len(ix4_worlds)))
                if len(ix4_worlds) == 0 or len(ix4_worlds) < len(alg.worlds) // 100:
                    alg.min_importance = 2
                    self.logger.info("setting {} min importance to 2".format(alg.name))
                else:
                    self.logger.info("setting {} min importance to 3".format(alg.name))

        self.generate_base_routes()

        routes = [(s, n, d) for (s, n, d) in self.galaxy.ranges.edges(data=True) if d['distance'] < 3]

        self.logger.info("considering {} worlds for removal".format(len(routes)))
        removed = 0
        for route in routes:
            imp = self.galaxy.alg[route[0].alg_base_code].min_importance
            if (len(self.galaxy.alg[route[0].alg_base_code].worlds) < 100 and d['distance'] > 1) or \
                    len(self.galaxy.alg[route[0].alg_base_code].worlds) < 25:
                continue
            star = self.more_important(route[0], route[1], imp)
            if star is not None:
                removed += 1
                neighbors = self.galaxy.ranges.neighbors(star)
                for neighbor in neighbors:
                    self.galaxy.ranges.remove_edge(star, neighbor)
            else:
                self.logger.info("Route considered but not removed: {}".format(route))

        self.logger.info("Removed {} worlds".format(removed))
        self.logger.info("Routes: %s  -  connections: %s" %
                         (self.galaxy.stars.number_of_edges(),
                          self.galaxy.ranges.number_of_edges()))

    def calculate_routes(self):
        self.logger.info('sorting routes...')
        routes = [(s, n, d) for (s, n, d) in self.galaxy.ranges.edges(data=True)]
        routes.sort(key=lambda route: route[2]['distance'])
        routes.sort(key=lambda route: route[2]['flags'], reverse=True)
        total = len(routes)
        processed = 0
        self.logger.info('Routes: {}'.format(total))
        for (star, neighbor, data) in routes:
            if total > 100 and processed % (total // 20) == 0:
                self.logger.info('processed {} routes, at {}%'.format(processed, processed // (total // 100)))
            self.get_route_between(star, neighbor)
            processed += 1

        active = [(s, n, d) for (s, n, d) in self.galaxy.stars.edges(data=True) if d['count'] > 0]
        active_graph = nx.Graph()

        active_graph.add_edges_from(active)
        # for (star, neighbor, data) in self.galaxy.stars.edges(data=True):
        #    pass

    def route_weight(self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        if star.port in 'CDEX':
            weight += 25
        if star.port in 'DEX':
            weight += 25
        # if star.zone in 'A' or target.zone in 'A':
        #    weight += 25
        if star.zone in 'RF' or target.zone in 'RF':
            weight += 50
        if star.popCode == 0 or target.popCode == 0:
            weight += 25
        weight -= 2 * (star.importance + target.importance)
        weight -= 6 if self.comm_bases(star) or self.comm_bases(target) else 0
        weight -= 6 if self.capitals(star) or self.capitals(target) else 0
        weight -= 6 if self.bases(star) or self.bases(target) else 0
        weight -= 3 if self.is_rich(star) or self.is_rich(target) else 0
        return weight

    def more_important(self, star, neighbor, imp):
        set1 = [self.capitals(star), self.bases(star), self.important(star, imp), self.is_rich(star)]
        set2 = [self.capitals(neighbor), self.bases(neighbor), self.important(neighbor, imp), self.is_rich(neighbor)]

        if set1 > set2:
            return neighbor
        elif set1 < set2:
            return star
        else:
            if self.bases(star) and self.bases(neighbor):
                return self.lesser_importance(star, neighbor)
            if self.is_rich(star) and self.is_rich(neighbor):
                return self.lesser_importance(star, neighbor)
            return None

    def lesser_importance(self, star, neighbor):
        if star.importance > neighbor.importance:
            return neighbor
        elif star.importance < neighbor.importance:
            return star
        else:
            return None

    def get_route_between(self, star, target):
        try:
            route = nx.astar_path(self.galaxy.stars, star, target, Star.heuristicDistance)
        except nx.NetworkXNoPath:
            return

        trade = self.calc_trade(19) if AllyGen.are_allies('As', star.alg_code) else self.calc_trade(23)
        start = route[0]
        for end in route[1:]:
            end.tradeCount += 1 if end != route[-1] else 0
            self.galaxy.stars[start][end]['trade'] = trade
            self.galaxy.stars[start][end]['count'] += 1
            if start == route[0] or end == route[-1]:
                self.galaxy.stars[start][end]['weight'] = \
                    max(self.galaxy.stars[start][end]['weight'] - 2,
                        self.route_reuse)
            else:
                self.galaxy.stars[start][end]['weight'] -= \
                    self.galaxy.stars[start][end]['weight'] / self.route_reuse
            start = end
