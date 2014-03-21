'''
Created on Mar 15, 2014

@author: tjoneslo
'''
import bisect
import logging
import sys

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
        
        self.btn_range = [2, 9, 29, 59, 99, 299]

        # BTN modifier for range. If the hex distance between two worlds 
        # or between two numbers in the jump range array, take jump modifier
        # to the right. E.g distance 4 would be a btn modifer of -3.  
        self.btn_jump_range = [ 1,  2,  5,  9, 19, 29, 59, 99,199]
        self.btn_jump_mod   = [-1, -2, -3, -4, -5, -6, -7, -8, -9]
        # How aggressive should the route finder be about reusing existing routes?
        # Set higher to make the route less likely to be reused, Set lower to make
        # reuse more likely.
        self.route_reuse = 5
        # Minimum BTN to calculate routes for. BTN between two worlds less than
        # this value are ignored. Set lower to have more routes calculated, but
        # may not have have an impact on the overall trade flows.
        self.min_btn = 14

    def calculate_routes(self):
        '''
        The base calculate routes. Read through all the stars in WTN order.
        Do this order to allow the higher trade routes establish the basic routes
        for the lower routes to follow.
        '''
        
        for trade in xrange(15, 7, -1): 
            counter = 0;
            for star in self.galaxy.starwtn[counter:]:
                if star.wtn < trade:
                    break
                self.get_trade_to(star, trade)
                counter += 1
                sys.stdout.write(".")
                sys.stdout.flush()
            sys.stdout.write("\n")
            self.logger.info('Processes %s routes at trade %s' % (counter, trade))

    def get_btn (self, star1, star2):
        btn = star1.wtn + star2.wtn
        if (star1.agricultural and star2.nonAgricultural) or \
            (star1.nonAgricultural and star2.agricultural): 
            btn += 1
        if (star1.resources and star2.industrial) or \
            (star2.resources and star1.industrial): 
            btn += 1
            
        if (star1.alg != star2.alg) :
            btn -= 1
                        
        distance = star1.hex_distance(star2)
        jump_index = bisect.bisect_right(self.btn_jump_range, distance)
        btn += self.btn_jump_mod[jump_index]
        return btn
    
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
            
            # skip this pair if there's no trade 
            # Or rather if there isn't enough trade to warrant a trade check
            tradeBTN = self.get_btn(star, target)
            if tradeBTN < self.min_btn:
                continue
            
            # Calculate the route between the stars
            route = nx.astar_path(self.galaxy.stars, star, target)
            
            # Gather basic statistics. 
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
                # As the higher trade routes make established routes 
                # which are more likely to be followed 
                self.galaxy.stars[start][end]['weight'] -= \
                    self.galaxy.stars[start][end]['weight'] / self.route_reuse
                start.tradeOver += tradeCr
                start = end

    
    def calc_trade (self, btn):
        '''
        Convert the BTN trade number to a credit value. 
        '''
        if btn & 1:
            trade = 10 ** ((btn - 1)/2) * 5 
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
    