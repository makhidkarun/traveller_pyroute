"""
@author: tjoneslo
"""
import math
import os

import networkx as nx
from networkx import is_path
from multiprocessing import Queue, Pool
from queue import Empty

from PyRoute.Calculation.TradeCalculation import TradeCalculation
from PyRoute.Pathfinding.DistanceGraph import DistanceGraph
try:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnified import ApproximateShortestPathForestUnified
except ModuleNotFoundError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
except ImportError:
    from PyRoute.Pathfinding.ApproximateShortestPathForestUnifiedFallback import ApproximateShortestPathForestUnified
try:
    from PyRoute.Pathfinding.astar_numpy import astar_path_numpy
except ModuleNotFoundError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy
except ImportError:
    from PyRoute.Pathfinding.astar_numpy_fallback import astar_path_numpy

# Convert the TradeMPCalculation to a global variable to allow the child processes to access it, and all the data.
tradeCalculation = None


def intrasector_process(working_queue, processed_queue) -> None:
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

        # Look through the worlds in the sector, then look at their trade neighbors
        # to determine which routes to process.
        for star in tradeCalculation.galaxy.sectors[sector].worlds:
            for neighbor in tradeCalculation.galaxy.ranges.neighbors(star):
                # Here we're just doing the routes that are within the one sector we're currently processing
                # If other routes are to be done, this will have to change to select the routes from the BTN list.
                if not (star.sector.name == sector and neighbor.sector.name == sector):
                    continue
                data = tradeCalculation.galaxy.ranges.get_edge_data(star, neighbor)

                # Skip the worlds already processed, both in the BTN 19+ cases, and in the A->B, now B->A cases.
                if data.get('jumps', False):
                    continue

                try:
                    upbound = tradeCalculation._preheat_upper_bound(star.index, neighbor.index)
                    # Increase a finite upbound value by 0.5%, and round result up to 3 decimal places
                    if float('+inf') != upbound:
                        upbound = round(upbound * 1.005 + 0.0005, 3)

                    rawroute, _ = astar_path_numpy(tradeCalculation.star_graph, star.index, neighbor.index,
                                               tradeCalculation.galaxy.heuristic_distance_bulk, upbound=upbound)
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


def long_route_process(working_queue, processed_queue) -> None:
    global tradeCalculation
    processed = 0
    total = working_queue.qsize()

    # Working queue here is sending a pair of star indexes to process.
    while True:
        try:
            (star, neighbor) = working_queue.get(block=True, timeout=1)
        except Empty:
            break

        try:
            upbound = tradeCalculation._preheat_upper_bound(star, neighbor)

            rawroute, _ = astar_path_numpy(tradeCalculation.star_graph, star, neighbor,
                                       tradeCalculation.galaxy.heuristic_distance_bulk, upbound=upbound)
        except nx.NetworkXNoPath:
            continue

        # Route is a list of star indexes, which is what the parent process is assuming.
        processed_queue.put(rawroute)
        processed += 1
        if total > 100 and processed % (total // 20) == 0:
            tradeCalculation.logger.info(f'Child {os.getpid()} processed {processed} routes, at {processed // (total // 100)}%')

    # And were done. Note this for the user.
    tradeCalculation.logger.info(f"child process {os.getpid()} completed, processed {processed} routes")


class TradeMPCalculation(TradeCalculation):
    """
    Perform the trade calculations by generating the routes
    between all the trade pairs using a multi-process route finder
    """

    def __init__(self, galaxy, min_btn=13, route_btn=8, route_reuse=10, debug_flag=False, mp_threads=os.cpu_count() - 1):
        super(TradeMPCalculation, self).__init__(galaxy, min_btn, route_btn, route_reuse, debug_flag)

        self.btn = []
        self.mp_threads = mp_threads
        self.total_processed = 0

    def calculate_routes(self) -> None:
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

        btn_skipped = [(s, n) for (s, n) in self.galaxy.ranges.edges() if s.component != n.component]
        self.logger.debug(f"Found {len(btn_skipped)} non-component linked routes, removing from ranges graph")
        for s, n in btn_skipped:
            self.galaxy.ranges.remove_edge(s, n)

        self.btn = [(s, n, d) for (s, n, d) in self.galaxy.ranges.edges(data=True)]
        self.btn.sort(key=lambda tn: tn[2]['btn'], reverse=True)

        # Pick landmarks - biggest WTN system in each graph component.  It worked out simpler to do this for _all_
        # components, even those with only one star.
        landmarks, self.component_landmarks = self.get_landmarks(index=True)
        source = max(self.galaxy.star_mapping.values(), key=lambda item: item.wtn)
        source.is_landmark = True
        # Feed the landmarks in as roots of their respective shortest-path trees.
        # This sets up the approximate-shortest-path bounds to be during the first pathfinding call.
        self.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, self.galaxy.stars, self.epsilon, sources=landmarks)
        self.star_graph = DistanceGraph(self.galaxy.stars)
        self.star_len_root = max(1, math.floor(math.sqrt(len(self.star_graph))) // 2)

        large_btn_index = 0
        if self.btn[0][2]['btn'] >= 18:
            large_btn_index = next(i for i, v in enumerate(self.btn) if v[2]['btn'] == 18)

        # Do the large routes (btn 19 - 26) first. These are short and take only a short amount of time.
        self.process_routes(self.btn[0:(large_btn_index - 1)])
        # Do the in-sector routes next. Again short, and famed across multiple processor to make this faster.
        self.start_mp_services()
        # Do the remaining routes, which are long and will take a while
        self.process_long_routes(self.btn[large_btn_index:])
        self.multilateral_balance_trade()
        self.multilateral_balance_pass()

    # This is the multiprocess method, which contains all the logic for using multi-process in the parent (core) process
    # When this is completed, all the child process should be completed.
    def start_mp_services(self) -> None:
        global tradeCalculation
        tradeCalculation = self

        # Create the Queues for sending data between processes.
        sector_queue = Queue()
        routes_queue = Queue()
        count = 0
        # write sector names to the queue
        for sector in self.galaxy.sectors:
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

                distance = self.route_distance(route)
                btn = self.get_btn(route[0], route[-1], distance)
                count += 1
                if self.min_btn > btn:
                    self.penumbra_routes += 1
                    continue

                # Using the route found by the child process update the stars / routes graphs in the parent process
                start = route[0]
                target = route[-1]
                tradeCr, tradePass, tradeDton = self.route_update_simple(route, True)
                self.update_statistics(start, target, tradeCr, tradePass, tradeDton)

        self.logger.info(f"Intra-sector route processing completed. Processed {count} routes")
        self.total_processed += count

    def process_long_routes(self, btn) -> None:

        self.shortest_path_tree = ApproximateShortestPathForestUnified(0, self.galaxy.stars,
                                             0, sources=self.shortest_path_tree.sources)

        # Create the Queues for sending data between processes.
        find_queue = Queue()
        routes_queue = Queue()
        processed = 0

        for (start, target, data) in btn:
            # skip the routes already that have been processed, in the intra-sector processing
            if data.get('jumps', False):
                continue
            find_queue.put((start.index, target.index))

        total = find_queue.qsize()
        self.logger.info(f"Starting {self.mp_threads} child processes for long route calculations. processing {total} routes")

        with Pool(processes=self.mp_threads, initializer=long_route_process, initargs=(find_queue, routes_queue)):
            # Loop over the routes found by the child processes.
            while True:
                try:
                    # Get a route from the child processes. This assumes the child processes (collectively)
                    # won't take more than 5 seconds to produce a route. And they will produce routes faster
                    # than the parent process can consume them. Which is why we have the queue.
                    route_list = routes_queue.get(block=True, timeout=5)
                except Empty:
                    if not find_queue.empty():
                        continue
                    break
                route = [self.galaxy.star_mapping[item] for item in route_list]
                assert is_path(self.galaxy.stars, route_list), f"Route returned by mp process is not a correct path: {route}"

                distance = self.route_distance(route)
                btn = self.get_btn(route[0], route[-1], distance)
                processed += 1
                if self.min_btn > btn:
                    self.penumbra_routes += 1
                    continue

                if total > 100 and processed % (total // 20) == 0:
                    self.logger.info(f'processed {processed} routes, at {processed // (total // 100)}%')

                # Using the route found by the child process update the stars / routes graphs in the parent process
                start = route[0]
                target = route[-1]
                tradeCr, tradePass, tradeDton = self.route_update_simple(route, False)
                self.update_statistics(start, target, tradeCr, tradePass, tradeDton)

        self.logger.info(f"Long route processing completed. process {processed} routes")
        self.total_processed += processed
        self.logger.info('{} penumbra routes included out of {}'.format(self.penumbra_routes, self.total_processed))

    def process_routes(self, btn) -> None:
        """
        Do the first "half" of the routes, the ones not performed by the child process.
        :return: None
        """
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
        self.total_processed += processed

    def get_trade_between(self, star, target) -> None:
        """
        Calculate the route between star and target
        If we can't find a route (no Jump 4 (or N) path), skip this pair
        otherwise update the trade information.
        """
        assert 'actual distance' not in self.galaxy.ranges[target][star],\
            f"This route from {star} to {target} has already been processed in reverse"

        try:
            upbound = self._preheat_upper_bound(star.index, target.index)
            # Increase a finite upbound value by 0.5%, and round result up to 3 decimal places
            if float('+inf') != upbound:
                comp_id = star.component
                upbound = round(upbound * 1.005 + 0.0005, 3)
                if star.index in self.component_landmarks[comp_id] and \
                    target.index not in self.component_landmarks[comp_id]:
                    target, star = star, target

            rawroute, _ = astar_path_numpy(self.star_graph, star.index, target.index,
                                           self.galaxy.heuristic_distance_bulk, upbound=upbound)
        except nx.NetworkXNoPath:
            return

        route = [self.galaxy.star_mapping[item] for item in rawroute]

        assert self.galaxy.route_no_revisit(route), \
            f"Route between {star}  and {target} revisits at least one star"

        distance = self.route_distance(route)
        btn = self.get_btn(star, target, distance)
        if self.min_btn > btn:
            self.penumbra_routes += 1
            return

        if self.debug_flag:
            fwd_weight = self.route_cost(route)
            route.reverse()
            rev_weight = self.route_cost(route)
            route.reverse()
            delta = fwd_weight - rev_weight
            assert 1e-16 > delta * delta,\
                f"Route weight between {repr(star)} and {repr(target)} should not be direction sensitive.  Forward weight {fwd_weight}, rev weight {rev_weight}. delta {abs(delta)}"

        # Update the trade route (edges)
        tradeCr, tradePass, tradeDton = self.route_update_simple(route, True)
        self.update_statistics(star, target, tradeCr, tradePass, tradeDton)
