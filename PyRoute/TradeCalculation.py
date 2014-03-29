'''
Created on Mar 15, 2014

@author: tjoneslo
'''
import bisect
import logging


import networkx as nx

class TradeCalculation(object):
    '''
    classdocs
    '''


    def __init__(self, galaxy):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('PyRoute.TradeCalculation')
        self.galaxy = galaxy

        # Weight for route over a distance. The relative cost for
        # moving freight between two worlds a given distance apart
        # in a single jump.         
        self.distance_weight = [0, 30, 50, 80, 150, 240, 450 ]
        
        # Set an initial range for influence for worlds based upon their
        # wtn. For a given world look up the range given by (wtn-8) (min 0), 
        # and the system checks every other world in that range for trade 
        # opportunity. See the btn_jump_mod and min btn to see how  
        # worlds are excluded from this list. 
        self.btn_range = [2, 9, 29, 59, 99, 299]

        # BTN modifier for range. If the hex distance between two worlds 
        # or between two numbers in the jump range array, take jump modifier
        # to the right. E.g distance 4 would be a btn modifer of -3.  
        self.btn_jump_range = [ 1,  2,  5,  9, 19, 29, 59, 99, 199, 299]
        self.btn_jump_mod   =[0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10]
        
        # How aggressive should the route finder be about reusing existing routes?
        # Set higher to make the route less likely to be reused, Set lower to make
        # reuse more likely.
        # This works by reducing the weight of the route (see distance_weight) 
        # each time a route is selected (making it more likely to be selected
        # next time). Setting this to below 10 results in a lot of main routes
        # with a few spiky connectors. Setting it above 20 results in a lot of
        # nearby routes. This is also (if left as an integer) the lower limit on 
        # distance_weight settings. 
        self.route_reuse = 10

        # Minimum BTN to calculate routes for. BTN between two worlds less than
        # this value are ignored. Set lower to have more routes calculated, but
        # may not have have an impact on the overall trade flows.
        self.min_btn = 13
        
        # Maximum WTN to process routes for
        self.max_wtn = 15
        
        # Minimum WTN to process routes for
        self.min_wtn = 8

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
        
    def get_btn (self, star1, star2):
        btn = star1.wtn + star2.wtn
        if (star1.agricultural and (star2.nonAgricultural or star2.extreme)) or \
            ((star1.nonAgricultural or star1.extreme) and star2.agricultural): 
            btn += 1
        if (star1.nonIndustrial and star2.industrial) or \
            (star2.nonIndustrial and star1.industrial): 
            btn += 1
        
        if not self.galaxy.borders.are_allies(star1.alg, star2.alg):
            btn -= 1
                        
        distance = star1.hex_distance(star2)
        jump_index = bisect.bisect_right(self.btn_jump_range, distance)
        btn += self.btn_jump_mod[jump_index]
        
        max_btn = (min(star1.wtn, star2.wtn) * 2) + 1
        btn = min(btn, max_btn)
        return btn
    
    def get_trade_between(self, star, target):
        # Calculate the route between the stars
        # If we can't find a route (no jump 4 path) skip this pair
        try:
            route = nx.astar_path(self.galaxy.stars, star, target, heuristic)
        except  nx.NetworkXNoPath:
            return

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
    
    def get_trade_to (self, star, trade):
        ''' Calculate the trade route between starting star and all potential target'''
        
        # Loop through all the stars in the ranges list, i.e. all potential stars
        # within the range of the BTN route. 
        for (newstar, target, data) in self.galaxy.ranges.edges_iter(star, True):
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

    
    def calc_trade (self, btn):
        '''
        Convert the BTN trade number to a credit value. 
        '''
        if btn & 1:
            trade = (10 ** ((btn - 1)/2)) * 5
        else:
            trade = 10 ** (btn/2)
            
        return trade

    def route_weight (self, star, target):
        dist = star.hex_distance(target)
        if dist in [4,5,6]:
            dist = 4
        weight = self.distance_weight[dist]
        if target.alg != star.alg:
            weight += 25
        if star.port in ['C', 'D', 'E', 'X']:
            weight += 25
        if star.port in ['D', 'E', 'X']:
            weight += 25
        return weight
    
def heuristic(u, v):
    return u.hex_distance(v)
    