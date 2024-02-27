"""
Created on Aug 09, 2023

@author: CyberiaResurrection
"""
import copy

import networkx as nx

from PyRoute.AllyGen import AllyGen
from PyRoute.Calculation.RouteCalculation import RouteCalculation
from PyRoute.Pathfinding.ApproximateShortestPathForestDistanceGraph import ApproximateShortestPathForestDistanceGraph
from PyRoute.Pathfinding.astar_numpy import astar_path_numpy


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
        if not AllyGen.are_allies(star.alg_code, neighbor.alg_code):
            return True
        return False

    def base_range_routes(self, star, neighbor):
        if not getattr(self.galaxy.alg[star.alg_base_code], 'min_importance', False):
            return
        min_importance = self.galaxy.alg[star.alg_base_code].min_importance
        if self.endpoint_selection(star, min_importance) and self.endpoint_selection(neighbor, min_importance):
            dist = star.distance(neighbor)

            if ((self.capitals(star) or self.bases(star)) and
                (self.capitals(neighbor) or self.bases(neighbor)) and dist < 100) or \
                    dist < 20:
                flags = [self.capitals(star) and self.capitals(neighbor),
                         self.capitals(star) or self.capitals(neighbor),
                         self.bases(star) or self.bases(neighbor),
                         self.important(star, min_importance) or self.important(neighbor, min_importance),
                         self.is_rich(star) or self.is_rich(neighbor)]
                self.galaxy.ranges.add_edge(star, neighbor, distance=dist, flags=flags)
            return dist

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
            if AllyGen.is_nonaligned(alg.code):
                continue
            # No comm routes for small empires
            if len(alg.worlds) < 20:
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
            d = route[2]
            imp = self.galaxy.alg[route[0].alg_base_code].min_importance
            if (len(self.galaxy.alg[route[0].alg_base_code].worlds) < 100 and d['distance'] > 1) or \
                    len(self.galaxy.alg[route[0].alg_base_code].worlds) < 25:
                continue
            star = self.more_important(route[0], route[1], imp)
            if star is not None:
                removed += 1
                neighbors = list(self.galaxy.ranges.neighbors(star))
                for neighbor in neighbors:
                    self.galaxy.ranges.remove_edge(star, neighbor)
            else:
                self.logger.info("Route considered but not removed: {}".format(route))

        self.logger.info("Removed {} worlds".format(removed))
        self.logger.info("Routes: %s  -  connections: %s" %
                         (self.galaxy.stars.number_of_edges(),
                          self.galaxy.ranges.number_of_edges()))

    def calculate_routes(self):
        self.calculate_components()
        # Pick landmarks - biggest WTN system in each graph component.  It worked out simpler to do this for _all_
        # components, even those with only one star.
        landmarks = self.get_landmarks(index=True)
        source = max(self.galaxy.star_mapping.values(), key=lambda item: item.wtn)
        source.is_landmark = True
        # Feed the landmarks in as roots of their respective shortest-path trees.
        # This sets up the approximate-shortest-path bounds to be during the first pathfinding call.
        self.shortest_path_tree = ApproximateShortestPathForestDistanceGraph(source.index, self.galaxy.stars, self.epsilon, sources=landmarks)

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
        dist = star.distance(target)
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
            mincost = copy.deepcopy(self.star_graph._min_cost)
            route, _ = astar_path_numpy(self.star_graph, star.index, target.index,
                                           self.galaxy.heuristic_distance_bulk, min_cost=mincost)
        except nx.NetworkXNoPath:
            return

        trade = self.calc_trade(19) if AllyGen.are_allies('As', star.alg_code) else self.calc_trade(23)
        start = route[0]
        edges = []
        for end in route[1:]:
            end_star = self.galaxy.star_mapping[end]
            end_star.tradeCount += 1 if end != route[-1] else 0
            data = self.galaxy.stars[start][end]
            data['trade'] = trade
            data['count'] += 1
            if start == route[0] or end == route[-1]:
                data['weight'] = \
                    max(data['weight'] - 2,
                        self.route_reuse)
            else:
                data['weight'] -= (data['weight'] - data['distance']) / self.route_reuse
            edges.append((start, end))
            start = end

        self.shortest_path_tree.update_edges(edges)

    def unilateral_filter(self, star):
        if star.zone in ['R', 'F']:
            return True
        return False
