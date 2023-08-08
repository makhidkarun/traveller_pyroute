"""
Created on Mar 15, 2014

@author: tjoneslo
"""
import networkx as nx
from PyRoute.AllyGen import AllyGen
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.Pathfinding.astar import astar_path
from PyRoute.Star import Star


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

    # Stars that have been excluded, for whatever reason, from route generation
    redzone = set()

    def __init__(self, galaxy, min_btn=13, route_btn=8, route_reuse=10, debug_flag=False):
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

        # Are debugging gubbins turned on?
        self.debug_flag = debug_flag

    def base_route_filter(self, star, neighbor):
        if star in self.redzone or neighbor in self.redzone:
            return True
        if star.zone in ['R', 'F']:
            self.redzone.add(star)
            return True
        if neighbor.zone in ['R', 'F']:
            self.redzone.add(neighbor)
            return True
        if star.tradeCode.barren:
            self.redzone.add(star)
            return True
        if neighbor.tradeCode.barren:
            self.redzone.add(neighbor)
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
        # Filter out pathfinding attempts that can never return a route, as they're between two different
        # connected components in the underlying galaxy.stars graph - such pathfinding attempts are doomed
        # to failure.
        self.calculate_components()
        btn = [(s, n, d) for (s, n, d) in self.galaxy.ranges.edges(data=True) if s.component == n.component]
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
        assert 'actual distance' not in self.galaxy.ranges[target][star],\
            "This route from " + str(star) + " to " + str(target) + " has already been processed in reverse"

        try:
            route = astar_path(self.galaxy.stars, star, target, self.galaxy.heuristic_distance)
        except nx.NetworkXNoPath:
            return

        if self.debug_flag:
            fwd_weight = self.route_cost(route)
            route.reverse()
            rev_weight = self.route_cost(route)
            route.reverse()
            delta = fwd_weight - rev_weight
            assert 1e-16 > delta * delta,\
                "Route weight between " + str(star) + " and " + str(target) + " should not be direction sensitive.  Forward weight " + str(fwd_weight) + ", rev weight " + str(rev_weight) +", delta " + str(abs(delta))

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
        distance = self.route_distance(route)

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
            data = self.galaxy.stars[start][end]
            data['trade'] += tradeCr
            data['count'] += 1
            data['weight'] -= (data['weight'] - data['distance']) / self.route_reuse
            start = end

        return (tradeCr, tradePass)

    @staticmethod
    def route_distance(route):
        """
        Given a route, return its line length in parsec
        """
        distance = 0
        start = route[0]
        for end in route[1:]:
            distance += start.hex_distance(end)
            start = end
        return distance

    def route_cost(self, route):
        """
        Given a route, return its total cost via _compensated_ summation
        """
        total_weight = 0
        c = 0
        start = route[0]
        for end in route[1:]:
            y = float(self.galaxy.stars[start][end]['weight']) - c
            t = total_weight + y
            c = (t - total_weight) - y

            total_weight = t

            start = end
        return total_weight

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
                data = self.galaxy.stars[start][end]
                data['trade'] += tradeCr
                # Reduce the weight of this route. 
                # As the higher trade routes create established routes 
                # which are more likely to be followed by lower trade routes
                data['weight'] -= (data['weight'] - data['distance']) / self.route_reuse
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
        # Per https://www.baeldung.com/cs/dijkstra-vs-a-pathfinding , to ensure termination in finite time:
        # "the edges have strictly positive costs"
        assert 0 < weight, "Weight of edge between " + str(star) + " and " + str(
            target) + " must be positive"
        return weight

    def calculate_components(self):
        bitz = nx.connected_components(self.galaxy.stars)
        counter = -1

        for component in bitz:
            counter += 1
            for star in component:
                star.component = counter
        return


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
        assert 0 < weight, "Weight of edge between " + str(star) + " and " + str(
            target) + " must be positive"
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
            data = self.galaxy.stars[start][end]
            data['trade'] = trade
            data['count'] += 1
            if start == route[0] or end == route[-1]:
                data['weight'] = \
                    max(data['weight'] - 2,
                        self.route_reuse)
            else:
                data['weight'] -= (data['weight'] - data['distance']) / self.route_reuse
            start = end
