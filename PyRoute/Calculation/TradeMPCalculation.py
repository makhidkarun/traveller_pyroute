"""
@author: tjoneslo
"""
import os

import networkx as nx
from networkx import is_path
from PyRoute.AllyGen import AllyGen
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.Pathfinding.ApproximateShortestPathTree import ApproximateShortestPathTree
from PyRoute.Pathfinding.astar import astar_path_indexes
from multiprocessing import Queue, Pool
from queue import Empty

# Convert the TradeMPCalculation to a global variable to allow the child processes to access it, and all the data.
tradeCalculation = None


def intrasector_process(working_queue, processed_queue):
    """
    This is the core working function used by the child processes spawned by the start_mp_services() functions.
    :param working_queue: List of sectors to process
    :param processed_queue: List of routes found by the child process, consumed by the paraent.
    :return: None
    """
    global tradeCalculation
    while True:
        # Read the sector names from the queue created by parent process.
        # When the queue is empty we're done and can complete the process
        try:
            sector = working_queue.get(block=True, timeout=1)
        except Empty:
            break
        count = 0
        tradeCalculation.logger.info(f"starting work in {sector}")
        for (star, neighbor, data) in tradeCalculation.btn:

            # Here we're just doing the routes that are within the one sector we're currently processing
            # If other routes are to be done, this will have to change to select the routes from the BTN list.
            # TODO: Organized the tradeCalculation.btn to divided into sector / galaxy lists.
            if not (star.sector.name == sector and neighbor.sector.name == sector):
                continue

            # if this route has been processed, skip it, but still count it
            if data.get('jumps', False):
                count += 1
                continue

            try:
                rawroute, diag = astar_path_indexes(tradeCalculation.galaxy.stars, star.index, neighbor.index,
                                                    tradeCalculation.galaxy.heuristic_distance_indexes)
            except nx.NetworkXNoPath:
                continue


            # Update the routes in the child's internal list, like we would for the primary one,
            # But only for the child data. This makes sure the routes are properly reduced in weights for the next
            # route search.
            route = [tradeCalculation.galaxy.star_mapping[item] for item in rawroute]
            tradeCalculation.route_update_simple(route, True)

            # Put the rawroute (list of indexes) on the return queue to the parent process.
            processed_queue.put(rawroute)
            count += 1

        tradeCalculation.logger.info(f"Process for {sector} completed, {count} routes processed.")
    # And were done. Note this for the user.
    tradeCalculation.logger.info(f"child process {os.getpid()} completed.")


def long_route_process(working_queue, processed_queue):
    global tradeCalculation
    processed = 0
    total = working_queue.qsize()

    # Working queue here is sending a pair of star indexes to process.
    while True:
        try:
            (star,neighbor) = working_queue.get(block=True, timeout=1)
        except Empty:
            break

        try:
            route, diag = astar_path_indexes(tradeCalculation.galaxy.stars, star, neighbor,
                                             tradeCalculation.galaxy.heuristic_distance_indexes)
        except nx.NetworkXNoPath:
            continue

        # Route is a list of star indexes, which is what the parent process is assuming.
        processed_queue.put(route)
        processed += 1
        if total > 100 and processed % (total // 20) == 0:
            tradeCalculation.logger.info(f'Child {os.getpid()} processed {processed} routes, at {processed // (total // 100)}%')

    # And were done. Note this for the user.
    tradeCalculation.logger.info(f"child process {os.getpid()} completed, processed {processed} routes")


class TradeMPCalculation(RouteCalculation):
    """
    Perform the trade calculations by generating the routes
    between all the trade pairs using a multi-process route finder
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

    def __init__(self, galaxy, min_btn=13, route_btn=8, route_reuse=10, debug_flag=False, mp_threads=os.cpu_count()-1):
        super(TradeMPCalculation, self).__init__(galaxy)

        # Minimum BTN to calculate routes for. BTN between two worlds less than
        # this value are ignored. Set lower to have more routes calculated, but
        # may not have an impact on the overall trade flows.
        self.min_btn = min_btn

        # Minimum WTN to process routes for
        self.min_wtn = route_btn

        # Override the default setting for route-reuse from the base class
        # based upon program arguments. 
        self.route_reuse = route_reuse

        # Are debugging gubbins turned on?
        self.debug_flag = debug_flag
        self.btn = []
        self.mp_threads = mp_threads

    def base_route_filter(self, star, neighbor):
        return False

    def unilateral_filter(self, star):
        if star.zone in ['R', 'F']:
            return True
        if star.tradeCode.barren:
            return True
        return False

    def base_range_routes(self, star, neighbor):
        dist = star.distance(neighbor)
        max_dist = self.btn_range[min(max(0, max(star.wtn, neighbor.wtn) - self.min_wtn), 5)]
        btn = self.get_btn(star, neighbor, dist)
        # add all the stars in the BTN range, but  skip this pair
        # if there isn't enough trade to warrant a trade check
        if dist <= max_dist and btn >= self.min_btn:
            passBTN = self.get_passenger_btn(btn, star, neighbor)
            self.galaxy.ranges.add_edge(star, neighbor, distance=dist,
                                        btn=btn,
                                        passenger_btn=passBTN)
        return dist

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
        self.logger.info(f'Final route count {self.galaxy.stars.number_of_edges()}')

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
        self.btn = [(s, n, d) for (s, n, d) in self.galaxy.ranges.edges(data=True) if s.component == n.component]
        self.btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmarks - biggest WTN system in each graph component.  It worked out simpler to do this for _all_
        # components, even those with only one star.
        landmarks = self.get_landmarks(index=True)
        source = max(self.galaxy.star_mapping.values(), key=lambda item: item.wtn)
        source.is_landmark = True
        # Feed the landmarks in as roots of their respective shortest-path trees.
        # This sets up the approximate-shortest-path bounds to be during the first pathfinding call.
        self.shortest_path_tree = ApproximateShortestPathTree(source.index, self.galaxy.stars, 0.2, sources=landmarks)

        large_btn_index = next(i for i,v in enumerate(self.btn) if v[2]['btn'] == 18)

        # Do the large routes (btn 19 - 26) first. These are short and take only a short amount of time.
        self.process_routes(self.btn[0:large_btn_index-1])
        # Do the in-sector routes next. Again short, and famed across multiple processor to make this faster.
        self.start_mp_services()
        # Do the remaining routes, which are long and will take a while
        self.process_long_routes(self.btn[large_btn_index:])

    # This is the multiprocess method, which contains all the logic for using multi-process in the parent (core) process
    # When this is completed, all the child process should be completed.
    def start_mp_services (self):
        global tradeCalculation
        tradeCalculation = self

        # Create the Queues for sending data between processes.
        sector_queue = Queue()
        routes_queue = Queue()
        count = 0
        # write sector names to the queue
        for sector in self.galaxy.sectors.keys():
            sector_queue.put(sector)

        # This starts the child processes.
        # Use a "with ... as ..." to ensure the workers and everything is cleaned up
        # when the workers are completed.
        self.logger.info(f"Starting {self.mp_threads} child processes for sector route calculations")
        with Pool(processes=self.mp_threads, initializer=intrasector_process, initargs=(sector_queue, routes_queue)):
            # Loop over the routes found by the child processes.
            while True:
                try:
                    # Get a route from the child processes. This assumes the child processes (collectively)
                    # won't take more than 3 seconds to produce a route. And they will produce routes faster
                    # than the parent process can consume them. Which is why we have the queue.
                    # Once we run out of routes to process, break from the loop
                    route_list = routes_queue.get(block=True, timeout=3)
                except Empty:
                    if not sector_queue.empty():
                        continue
                    break
                # convert route_list (list of star indexes) to route (list of stars)
                route = [self.galaxy.star_mapping[item] for item in route_list]

                assert is_path(self.galaxy.stars, route_list), f"Route returned by mp process is not a correct path: {route}"

                # Using the route found by the child process update the stars / routes graphs in the parent process
                start = route[0]
                target = route[-1]
                tradeCr, tradePass = self.route_update_simple(route, True)
                self.update_statistics(start, target, tradeCr, tradePass)
                count += 1
        self.logger.info(f"Intra-sector route processing completed. Process {count} routes")

    def process_long_routes(self, btn):
        # Create the Queues for sending data between processes.
        find_queue = Queue()
        routes_queue = Queue()
        processed = 0

        for (start, target, data) in btn:
            # skip the routes already that have been processed
            if data.get('jumps', False):
                continue
            find_queue.put((start.index, target.index))

        total = find_queue.qsize()
        self.logger.info(f"Starting child processes for long route calculations. processing {total} routes")

        with Pool(processes=self.mp_threads, initializer=long_route_process, initargs=(find_queue, routes_queue)):
            # Loop over the routes found by the child processes.
            while True:
                try:
                    route_list = routes_queue.get(block=True, timeout=5)
                except Empty:
                    if not find_queue.empty():
                        continue
                    break
                route = [self.galaxy.star_mapping[item] for item in route_list]
                assert is_path(self.galaxy.stars, route_list), f"Route returned by mp process is not a correct path: {route}"

                if total > 100 and processed % (total // 20) == 0:
                    self.logger.info(f'processed {processed} routes, at {processed // (total // 100)}%')

                # Using the route found by the child process update the stars / routes graphs in the parent process
                start = route[0]
                target = route[-1]
                tradeCr, tradePass = self.route_update_simple(route, False)
                self.update_statistics(start, target, tradeCr, tradePass)
                processed += 1
        self.logger.info(f"Long route processing completed. process {processed} routes")

    def process_routes(self, btn):
        '''
        Do the other "half" of the routes, the ones not performed by the child process.
        :return: None
        '''
        base_btn = 0
        counter = 0
        processed = 0
        total = len(btn)
        for (star, neighbor, data) in btn:
            if base_btn != data['btn']:
                if counter > 0:
                    self.logger.info(f'processed {counter} routes at BTN {base_btn}')
                base_btn = data['btn']
                counter = 0
            if total > 100 and processed % (total // 20) == 0:
                self.logger.info(f'processed {processed} routes, at {processed // (total // 100)}%')

            # If the route has been processed in the child worker, skip it here. But count it toward the number of
            # processed routes.
            if data.get('jumps', False):
                counter += 1
                processed += 1
                continue

            # Do the trade route discovery and route calculation
            self.get_trade_between(star, neighbor)
            counter += 1
            processed += 1
        self.logger.info(f'processed {counter} routes at BTN {base_btn}')

    def get_trade_between(self, star, target):
        """
        Calculate the route between star and target
        If we can't find a route (no Jump 4 (or N) path), skip this pair
        otherwise update the trade information.
        """
        assert 'actual distance' not in self.galaxy.ranges[target][star],\
            f"This route from {star} to {target} has already been processed in reverse"

        try:
            rawroute, diag = astar_path_indexes(self.galaxy.stars, star.index, target.index, self.galaxy.heuristic_distance_indexes)
        except nx.NetworkXNoPath:
            return

        route = [self.galaxy.star_mapping[item] for item in rawroute]

        assert self.galaxy.route_no_revisit(route), \
            f"Route between {star}  and {target} revisits at least one star"

        if self.debug_flag:
            fwd_weight = self.route_cost(route)
            route.reverse()
            rev_weight = self.route_cost(route)
            route.reverse()
            delta = fwd_weight - rev_weight
            assert 1e-16 > delta * delta,\
                f"Route weight between {repr(star)} and {repr(target)} should not be direction sensitive.  Forward weight {fwd_weight}, rev weight {rev_weight}. delta {abs(delta)}"

        # Update the trade route (edges)
        tradeCr, tradePass = self.route_update_simple(route, True)
        self.update_statistics(star, target, tradeCr, tradePass)

    def update_statistics(self, star, target, tradeCr, tradePass):
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

    def route_update_simple(self, route, reweight=True):
        """
        Update the trade calculations based upon the route selected.
        - add the trade values for the worlds, and edges
        - add a count for the worlds and edges
        - reduce the weight of routes used to allow more trade to flow
        """
        distance = self.route_distance(route)

        source = route[0]
        target = route[-1]

        # Internal statistics
        rangedata = self.galaxy.ranges[source][target]
        rangedata['actual distance'] = distance
        rangedata['jumps'] = len(route) - 1

        # Gather basic statistics. 
        tradeBTN = self.get_btn(source, target, distance)
        tradeCr = self.calc_trade(tradeBTN)
        source.tradeIn += tradeCr // 2
        target.tradeIn += tradeCr // 2
        tradePassBTN = self.get_passenger_btn(tradeBTN, source, target)
        tradePass = self.calc_passengers(tradePassBTN)

        source.passIn += tradePass
        target.passIn += tradePass

        edges = []
        start = source
        for end in route[1:]:
            if end != target:
                end.tradeOver += tradeCr
                end.tradeCount += 1
                end.passOver += tradePass

            data = self.galaxy.stars[start.index][end.index]
            data['trade'] += tradeCr
            data['count'] += 1
            if reweight:
                data['weight'] -= (data['weight'] - data['distance']) / self.route_reuse
            edges.append((start.index, end.index))
            start = end

        # Feed the list of touched edges into the approximate-shortest-path machinery, so it can update whatever
        # distance labels it needs to stay within its approximation bound.
        self.shortest_path_tree.update_edges(edges)

        return (tradeCr, tradePass)

    @staticmethod
    def route_distance(route):
        """
        Given a route, return its line length in parsec
        """
        distance = 0
        start = route[0]
        for end in route[1:]:
            distance += start.distance(end)
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

    def route_weight(self, star, target):
        dist = star.distance(target)
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
        assert 0 < weight, f"Weight of edge between {star} and {target} must be positive"
        return weight
