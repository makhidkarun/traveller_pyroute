'''
Created on Mar 15, 2014

@author: tjoneslo
'''
import bisect
import logging
import itertools
import networkx as nx
from AllyGen import AllyGen
from Star import Star

class RouteCalculation (object):
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

    def __init__(self, galaxy):
        self.logger = logging.getLogger('PyRoute.TradeCalculation')
        self.galaxy = galaxy

    def generate_routes (self):
        raise NotImplementedError("Base Class")
    
    def calculate_routes(self):
        raise NotImplementedError ("Base Class")

    def route_weight (self, star, target):
        raise NotImplementedError ("Base Class")
    
    @staticmethod
    def calc_trade (btn):
        '''
        Convert the BTN trade number to a credit value. 
        '''
        if btn & 1:
            trade = (10 ** ((btn - 1)/2)) * 5
        else:
            trade = 10 ** (btn/2)
            
        return trade

        
class NoneCalculation(RouteCalculation):
    def __init__(self, galaxy):
        super(NoneCalculation, self).__init__(galaxy)

    def generate_routes(self):
        pass
    
    def calculate_routes(self):
        pass


    
class TradeCalculation(RouteCalculation):
    '''
    Perform the trade calcuations by generating the routes
    between all the trade pairs
    '''
    # Weight for route over a distance. The relative cost for
    # moving freight between two worlds a given distance apart
    # in a single jump.         
    distance_weight = [0, 30, 50, 80, 150, 240, 450 ]
    # Set an initial range for influence for worlds based upon their
    # wtn. For a given world look up the range given by (wtn-8) (min 0), 
    # and the system checks every other world in that range for trade 
    # opportunity. See the btn_jump_mod and min btn to see how  
    # worlds are excluded from this list. 
    btn_range = [2, 9, 29, 59, 99, 299]

    # BTN modifier for range. If the hex distance between two worlds 
    # or between two numbers in the jump range array, take jump modifier
    # to the right. E.g distance 4 would be a btn modifer of -3.  
    btn_jump_range = [ 1,  2,  5,  9, 19, 29, 59, 99, 199, 299]
    btn_jump_mod   =[0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10]
    

    # Maximum WTN to process routes for
    max_wtn = 15


    def __init__(self, galaxy, min_btn=13, route_btn = 8):
        super(TradeCalculation, self).__init__(galaxy)

        # Minimum BTN to calculate routes for. BTN between two worlds less than
        # this value are ignored. Set lower to have more routes calculated, but
        # may not have have an impact on the overall trade flows.
        self.min_btn = min_btn

        # Minimum WTN to process routes for
        self.min_wtn = route_btn


    def generate_routes(self):
        ''' 
        Generate the basic routes between all the stars. This creates three sets
        of routes. 
        - Stars: The basic J4 (max-jump) routes for all pairs of stars. 
        - Routes: The truncated set of routes used for the A* Route finding
        - Ranges: The set of trade routes needing to be calculated. 
        '''
       
        self.logger.info('generating jumps...')
        
        for star,neighbor in itertools.combinations(self.galaxy.ranges.nodes_iter(), 2):
            if star.zone in ['R', 'F'] or neighbor.zone in ['R','F']:
                continue
            dist = star.hex_distance (neighbor)
            max_dist = self.btn_range[ min(max (0, max(star.wtn, neighbor.wtn) - self.min_wtn), 5)]
            btn = self.get_btn(star, neighbor)
            # add all the stars in the BTN range, but  skip this pair
            # if there there isn't enough trade to warrant a trade check
            if dist <= max_dist and btn >= self.min_btn:
                self.galaxy.ranges.add_edge(star, neighbor, {'distance': dist,
                                                      'btn': btn})
            if dist <= self.galaxy.max_jump_range: 
                weight = self.route_weight(star, neighbor)
                
                self.galaxy.stars.add_edge (star, neighbor, {'distance': dist,
                                                  'weight': weight,
                                                  'trade': 0,
                                                  'btn': btn,
                                                  'count': 0})
                self.galaxy.routes.add_edge (star, neighbor, {'distance': dist,
                                                  'weight': weight,
                                                  'trade': 0,
                                                  'btn': btn,
                                                  'count': 0})

        self.logger.info('calculating routes...')
        for star in self.galaxy.stars.nodes_iter():
            if len(self.galaxy.stars.neighbors(star)) < 11:
                continue
            neighbor_routes = [(s,n,d) for (s,n,d) in self.galaxy.stars.edges_iter([star], True)]
            neighbor_routes = sorted (neighbor_routes, key=lambda tn: tn[2]['btn'])
            neighbor_routes = sorted (neighbor_routes, key=lambda tn: tn[2]['distance'])
            neighbor_routes = sorted (neighbor_routes, key=lambda tn: tn[2]['weight'], reverse=True)
            
            length = len(neighbor_routes)
            
            for (s,n,d) in neighbor_routes:
                if len(self.galaxy.stars.neighbors(n)) < 15: 
                    continue
                if length <= 15:
                    break
                if self.galaxy.routes.has_edge(s, n):
                    self.galaxy.routes.remove_edge(s, n)
                length -= 1
            
        self.logger.info("Routes: %s  - jumps: %s - traders: %s" % 
                         (self.galaxy.routes.number_of_edges(), 
                          self.galaxy.stars.number_of_edges(), 
                          self.galaxy.ranges.number_of_edges()))
    
    def calculate_routes(self):
        '''
        The base calculate routes. Read through all the stars in WTN order.
        Do this order to allow the higher trade routes establish the basic routes
        for the lower routes to follow.
        '''
        self.logger.info('sorting routes...')
        btn = [(s,n,d) for (s,n,d) in  self.galaxy.ranges.edges_iter(data=True)]
        btn_array = sorted(btn, key=lambda tn: tn[2]['btn'], reverse=True)
        
        base_btn = 0
        counter = 0
        processed = 0
        total = len(btn_array)
        for (star,neighbor,data) in btn_array:
            if base_btn != data['btn']:
                if counter > 0:
                    self.logger.info('processed {} routes at BTN {}'.format(counter,base_btn))
                base_btn = data['btn']
                counter = 0
            if total > 100 and processed % (total/20) == 0:
                self.logger.info('processed {} routes, at {}%'.format(processed, processed/(total/100)))
            self.get_trade_between(star, neighbor)
            counter += 1
            processed += 1
        self.logger.info('processed {} routes at BTN {}'.format(counter,base_btn))
        self.logger.info('Routes: %s' % self.galaxy.routes.number_of_edges())
        
    
    def get_trade_between(self, star, target):
        '''
        Calculate the route between star and target
        If we can't find a route (no Jump 4 (or N) path), skip this pair
        otherwise update the trade information. 
        '''
        try:
            route = nx.astar_path(self.galaxy.routes, star, target, Star.huristicDistance)
        except  nx.NetworkXNoPath:
            return

        # Gather basic statistics. 
        tradeBTN = self.get_btn(star, target)
        tradeCr = self.calc_trade(tradeBTN)
        star.tradeIn += tradeCr / 2
        target.tradeIn += tradeCr / 2

        if star.sector != target.sector :
            star.sector.stats.tradeExt += tradeCr / 2
            target.sector.stats.tradeExt += tradeCr / 2
            star.sector.subsectors[star.subsector()].stats.tradeExt += tradeCr / 2
            target.sector.subsectors[target.subsector()].stats.tradeExt += tradeCr / 2
        else:
            star.sector.stats.trade += tradeCr
            if star.subsector() == target.subsector():
                star.sector.subsectors[star.subsector()].stats.trade += tradeCr
            else:
                star.sector.subsectors[star.subsector()].stats.tradeExt += tradeCr / 2
                target.sector.subsectors[target.subsector()].stats.tradeExt += tradeCr / 2
                
        if AllyGen.are_allies(star.alg, target.alg):
            self.galaxy.alg[AllyGen.same_align(star.alg)][1].trade += tradeCr
        else:
            self.galaxy.alg[AllyGen.same_align(star.alg)][1].tradeExt += tradeCr / 2
            self.galaxy.alg[AllyGen.same_align(target.alg)][1].tradeExt += tradeCr / 2
            
        self.galaxy.stats.trade += tradeCr
        
        # Update the trade route (edges)
        self.route_update_simple (route, tradeCr)
    
    
    def route_update_simple (self, route, tradeCr):
        '''
        Update the trade calculations based upon the route selected.
        - add the trade values for the worlds, and edges 
        - add a count for the worlds and edges
        - reduce the weight of routes used to allow more trade to flow
        '''
        start = route[0]
        for end in route[1:]:
            end.tradeOver += tradeCr if end != route[-1] else 0
            end.tradeCount += 1 if end != route[-1] else 0
            
            self.galaxy.stars[start][end]['trade'] += tradeCr
            self.galaxy.stars[start][end]['count'] += 1
            
            self.galaxy.routes[start][end]['trade'] += tradeCr
            self.galaxy.routes[start][end]['count'] += 1
            # Reduce the weight of this route. 
            # As the higher trade routes create established routes 
            # which are more likely to be followed by lower trade routes
            self.galaxy.routes[start][end]['weight'] -= \
                self.galaxy.routes[start][end]['weight'] / self.route_reuse
            self.galaxy.stars[start][end]['weight'] -= \
                self.galaxy.stars[start][end]['weight'] / self.route_reuse
            start = end
    
    def route_update_skip (self, route, tradeCr):
        '''
        Unused: This was an experiment in adding skip-routes, 
        i.e. longer, already calculated routes, to allow the 
        A* route finder to work faster. This needs better system 
        for selecting these routes as too many got added and it
        would slow the system down. 
        '''
        dist = 0
        weight = 0
        start = route[0]
        usesJumpRoute=False
        for end in route[1:]:
            end.tradeOver += tradeCr if end != route[-1] else 0
            if self.galaxy.routes.has_edge(start,end) and self.galaxy.routes[start][end].get('route', False):
                routeDist, routeWeight = self.route_update (self.galaxy.routes[start][end]['route'], tradeCr)
                dist += routeDist
                weight += routeWeight
                usesJumpRoute=True
                # Reduce the weight of this route. 
                # As the higher trade routes create established routes 
                # which are more likely to be followed by lower trade routes
                self.galaxy.routes[start][end]['weight'] -= \
                    self.galaxy.routes[start][end]['weight'] / self.route_reuse
            elif self.galaxy.stars.has_edge(start, end):
                self.galaxy.stars[start][end]['trade'] += tradeCr
                dist += self.galaxy.stars[start][end]['distance']
                weight += self.galaxy.stars[start][end]['weight']
                self.galaxy.routes[start][end]['weight'] -= \
                    self.galaxy.routes[start][end]['weight'] / self.route_reuse
            else:
                print start, end, self.galaxy.routes.has_edge(start, end)
            start = end
            
        if len(route) > 6 and not usesJumpRoute:
            weight -= weight / self.route_reuse
            self.galaxy.routes.add_edge (route[0], route[-1], {'distance': dist,
                                                 'weight': weight,
                                                  'trade': 0, 'route': route,
                                                  'btn': 0})
            start = route[0]
            for end in route[1:]:
                #self.galaxy.routes.remove_edge(start, end)
                start = end
        return dist, weight
    
    def get_trade_to (self, star, trade):
        ''' 
        Unused: 
        Calculate the trade route between starting star and all potential target.
        This was the direct copy algorthim from nroute for doing route calculation
        It was replaced by the process above which works better with the 
        pythonic data structures. It remains for historical purposes.  
        '''
        
        # Loop through all the stars in the ranges list, i.e. all potential stars
        # within the range of the BTN route. 
        for (newstar, target, _) in self.galaxy.ranges.edges_iter(star, True):
            if newstar != star:
                self.logger.error("edges_iter found newstar %s != star %s" % (newstar, star))
                continue

            #Skip this pair if we've already done the trade
            # usually from the other star first. 
            if target in star.tradeMatched: 
                continue
            
            # Calculate the route between the stars
            # If we can't find a route (no jump 4 path) skip this pair
            try:
                route = nx.astar_path(self.galaxy.stars, star, target)
            except  nx.NetworkXNoPath:
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


    def route_weight (self, star, target):
        dist = star.hex_distance(target)
        if dist in [4,5,6]:
            dist = 4
        weight = self.distance_weight[dist]
        if target.alg != star.alg:
            weight += 25
        if star.port in 'CDEX':
            weight += 25
        if star.port in 'DEX':
            weight += 25
        return weight

    @staticmethod
    def get_btn (star1, star2):
        '''
        Calculate the BTN between two stars, which is the sum of the worlds
        WTNs plus a modifier for types, minus a modifier for distance. 
        '''
        btn = star1.wtn + star2.wtn
        if (star1.agricultural and (star2.nonAgricultural or star2.extreme)) or \
            ((star1.nonAgricultural or star1.extreme) and star2.agricultural): 
            btn += 1
        if (star1.nonIndustrial and star2.industrial) or \
            (star2.nonIndustrial and star1.industrial): 
            btn += 1
        
        if not AllyGen.are_allies(star1.alg, star2.alg):
            btn -= 1
                        
        distance = star1.hex_distance(star2)
        jump_index = bisect.bisect_right(TradeCalculation.btn_jump_range, distance)
        btn += TradeCalculation.btn_jump_mod[jump_index]
        
        max_btn = (min(star1.wtn, star2.wtn) * 2) + 1
        btn = min(btn, max_btn)
        return btn
    
    
    
class CommCalculation(RouteCalculation):
    # Weight for route over a distance. The relative cost for
    # moving between two worlds a given distance apart
    # in a single jump.         
    distance_weight = [0, 70, 60, 50, 40, 50, 450 ]
    
    def __init__(self, galaxy):
        super(CommCalculation, self).__init__(galaxy)
        self.route_reuse = 5

    def generate_routes(self):
        self.logger.info('generating jumps...')
        
        worlds = [star for star in self.galaxy.ranges.nodes_iter() if \
                  len(set(['Cp', 'Cx', 'Cs']) & set(star.tradeCode)) > 0 or \
                  len(set(['D', 'W', 'X']) & set(star.baseCode)) > 0 or \
                  star.importance == 4 ]
        
        for star, neighbor in itertools.combinations(worlds, 2):
            if AllyGen.are_allies(star.alg, neighbor.alg):
                dist = star.hex_distance (neighbor)
                self.galaxy.ranges.add_edge(star, neighbor, {'distance': dist})
        
        for star,neighbor in itertools.combinations(self.galaxy.ranges.nodes_iter(), 2):
            if not AllyGen.are_allies(star.alg, neighbor.alg):
                continue
            dist = star.hex_distance (neighbor)
            if dist <= self.galaxy.max_jump_range: 

                weight = self.route_weight(star, neighbor)
                
                self.galaxy.stars.add_edge (star, neighbor, {'distance': dist,
                                                  'weight': weight,
                                                  'trade': 0,
                                                  'count': 0})
                self.galaxy.routes.add_edge (star, neighbor, {'distance': dist,
                                                  'weight': weight,
                                                  'trade': 0,
                                                  'count': 0})


    
    def calculate_routes(self):
        self.logger.info('sorting routes...')
        routes = [(s,n,d) for (s,n,d) in  self.galaxy.ranges.edges_iter(data=True)]
        routes.sort(key=lambda route : route[2]['distance'] )
        total = len(routes)
        processed = 0
        self.logger.info('Routes: {}'.format(total))
        for (star,neighbor,data) in routes:
            if total > 100 and processed % (total/20) == 0:
                self.logger.info('processed {} routes, at {}%'.format(processed, processed/(total/100)))
            self.get_route_between(star, neighbor)
            processed += 1

    def route_weight (self, star, target):
        dist = star.hex_distance(target)
        weight = self.distance_weight[dist]
        if star.port in 'CDEX':
            weight += 25
        if star.port in 'DEX':
            weight += 25
        #if star.zone in 'AU' or target.zone in 'AU':
        #    weight += 25
        if star.zone in 'RF' or target.zone in 'RF':
            weight += 50
        weight -= 3 * (star.importance + target.importance)
        weight -= 5 if 'S' in star.baseCode or 'S' in target.baseCode else 0
        
        return weight
    
    def get_route_between (self, star, target):
        try:
            route = nx.astar_path(self.galaxy.routes, star, target, self.heuristic)
        except  nx.NetworkXNoPath:
            return

        start = route[0]
        for end in route[1:]:
            end.tradeCount += 1 if end != route[-1] else 0
            self.galaxy.stars[start][end]['trade'] = self.calc_trade(21)
            self.galaxy.stars[start][end]['count'] += 1
            self.galaxy.routes[start][end]['trade'] = self.calc_trade(21)
            self.galaxy.routes[start][end]['count'] += 1
            self.galaxy.routes[start][end]['weight'] -= \
                self.galaxy.routes[start][end]['weight'] / self.route_reuse
            self.galaxy.stars[start][end]['weight'] -= \
                self.galaxy.stars[start][end]['weight'] / self.route_reuse
            start = end
