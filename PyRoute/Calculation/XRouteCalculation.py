"""
Created on Aug 09, 2023

@author: CyberiaResurrection
"""
import networkx as nx

from PyRoute.Allies.AllyGen import AllyGen
from PyRoute.Calculation.RouteCalculation import RouteCalculation
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


class XRouteCalculation(RouteCalculation):
    distance_weight = [0, 95, 90, 85, 80, 75, 70]
    capSec_weight = [0, 95, 90, 85, 75, 75, 70]
    inSec_weight = [0, 140, 110, 85, 70, 95, 140]
    impt_weight = [0, 90, 80, 70, 70, 110, 140]

    def __init__(self, galaxy):
        super(XRouteCalculation, self).__init__(galaxy)
        self.route_reuse = 5

    def base_range_routes(self, star, neighbor):
        return star.distance(neighbor)

    def base_route_filter(self, star, neighbor):
        if not AllyGen.are_allies(star.alg_code, neighbor.alg_code):
            return True

        return False

    def generate_routes(self):
        self.distance_weight = self.capSec_weight
        self.generate_base_routes()
        self.capital = [star for star in self.galaxy.ranges if AllyGen.imperial_align(star.alg_code) and star.tradeCode.other_capital]
        self.secCapitals = [star for star in self.galaxy.ranges if AllyGen.imperial_align(star.alg_code) and star.tradeCode.sector_capital]
        self.subCapitals = [star for star in self.galaxy.ranges if AllyGen.imperial_align(star.alg_code) and star.tradeCode.subsector_capital]

    def routes_pass_1(self):
        # Pass 1: Get routes at J6  Capital and sector capitals
        # This should be 1 element long
        self.logger.info(self.capital)
        if len(self.capital) == 0:
            return
        for star in self.secCapitals:
            self.get_route_between(self.capital[0], star, self.calc_trade(25))

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
                    self.get_route_between(star, neighbor, self.calc_trade(25))

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
                        # if we couldn't find a nearest sector capital, don't try finding a route to one
                        if capital[0] is None:
                            continue
                        self.get_route_between(capital[0], star, self.calc_trade(23))
            else:
                for star in subCap:
                    if self.galaxy.ranges.has_edge(secCap[0], star):
                        continue
                    self.get_route_between(secCap[0], star, self.calc_trade(23))

        for star in self.subCapitals:
            routes = [neighbor for neighbor in self.subCapitals if neighbor != star and neighbor.distance(star) <= 40]
            for neighbor in routes:
                self.get_route_between(star, neighbor, self.calc_trade(23))

    def routes_pass_3(self):
        self.reweight_routes(self.impt_weight)
        important = [star for star in self.galaxy.ranges if AllyGen.imperial_align(star.alg_code) and star.tradeCount == 0
                     and (star.importance >= 4 or 'D' in star.baseCode or 'W' in star.baseCode)]

        jumpStations = [star for star in self.galaxy.ranges if star.tradeCount > 0]

        self.logger.info('Important worlds: {}, jump stations: {}'.format(len(important), len(jumpStations)))

        important2 = []
        for star in important:
            if star in jumpStations:
                continue
            for neighbor in self.galaxy.stars.neighbors(star.index):
                neighbour_world = self.galaxy.star_mapping[neighbor]
                if star.distance(neighbour_world) > 4:
                    continue
                if neighbor in jumpStations:
                    self.get_route_between(star, neighbor, self.calc_trade(21))
                    jumpStations.append(star)
            if star.tradeCount == 0:
                important2.append(star)

        important3 = []
        for star in important2:
            for neighbor in self.galaxy.stars.neighbors(star.index):
                if neighbor in jumpStations:
                    self.get_route_between(star, neighbor, self.calc_trade(21))
                    jumpStations.append(star)
            if star.tradeCount == 0:
                important3.append(star)
                self.logger.info("No route for important world: {}".format(star))

        capitalList = self.capital + self.secCapitals + self.subCapitals
        for star in important3:
            capital = self.find_nearest_capital(star, capitalList)
            self.get_route_between(capital[0], star, self.calc_trade(21))

    def calculate_routes(self):
        self.calculate_components()
        # Pick landmarks - biggest WTN system in each graph component.  It worked out simpler to do this for _all_
        # components, even those with only one star.
        landmarks, _ = self.get_landmarks(index=True)
        landmarks = None if 0 == len(landmarks) else landmarks
        source = max(self.galaxy.star_mapping.values(), key=lambda item: item.wtn)
        source.is_landmark = True
        # Feed the landmarks in as roots of their respective shortest-path trees.
        # This sets up the approximate-shortest-path bounds to be during the first pathfinding call.
        self.shortest_path_tree = ApproximateShortestPathForestUnified(source.index, self.galaxy.stars, self.epsilon, sources=landmarks)
        self.logger.info('XRoute pass 1')
        self.routes_pass_1()

        self.logger.info('XRoute pass 2')
        self.routes_pass_2()

        self.logger.info('XRoute pass 3')
        self.routes_pass_3()

    def reweight_routes(self, weightList):
        self.distance_weight = weightList
        for (star, neighbor, data) in self.galaxy.stars.edges(data=True):
            star_world = self.galaxy.star_mapping[star]
            neighbour_world = self.galaxy.star_mapping[neighbor]
            data['weight'] = self.route_weight(star_world, neighbour_world)
            for _ in range(1, min(data['count'], 5)):
                data['weight'] -= data['weight'] // self.route_reuse

    def find_nearest_capital(self, world, capitals):
        dist = (None, 9999)
        for capital in capitals:
            newDist = capital.distance(world)
            if newDist < dist[1]:
                dist = (capital, newDist)
        return dist

    def find_sector_capital(self, sector):
        for world in self.secCapitals:
            if world.sector == sector:
                return world
        return None

    def get_route_between(self, star, target, trade):
        try:
            upbound = self.shortest_path_tree.triangle_upbound(star.index, target.index) * 1.005
            route, _ = astar_path_numpy(self.star_graph, star.index, target.index,
                                           self.galaxy.heuristic_distance_bulk, upbound=upbound)
        except nx.NetworkXNoPath:
            return

        self.galaxy.ranges.add_edge(star, target, distance=star.distance(target))

        distance = 0
        start = route[0]
        startstar = self.galaxy.star_mapping[start]
        startstar.tradeCount += 1
        edges = []

        for end in route[1:]:
            endstar = self.galaxy.star_mapping[end]
            distance += startstar.distance(endstar)
            endstar.tradeCount += 1
            data = self.galaxy.stars[start][end]
            data['trade'] = max(trade, data['trade'])
            data['count'] += 1
            data['weight'] -= (data['weight'] - data['distance']) // self.route_reuse
            edges.append((start, end))
            start = end
            startstar = endstar

        startstar = self.galaxy.star_mapping[route[0]]
        endstar = self.galaxy.star_mapping[route[-1]]

        self.shortest_path_tree.update_edges(edges)
        self.galaxy.ranges[startstar][endstar]['actual distance'] = distance
        self.galaxy.ranges[startstar][endstar]['jumps'] = len(route) - 1

    def route_weight(self, star, target):
        dist = star.distance(target)
        weight = self.distance_weight[dist]
        if star.port in 'CDEX?' or target.port in 'CDEX?':
            weight += 25
        if star.port in 'DEX?' or target.port in 'DEX?':
            weight += 25
        if star.zone in 'RF' or target.zone in 'RF':
            weight += 50
        if star.popCode == 0 or target.popCode == 0:
            weight += 25
        if star.deep_space_station or target.deep_space_station:
            weight += 100
        weight -= 3 * (star.importance + target.importance)
        weight -= 6 if 'S' in star.baseCode or 'S' in target.baseCode else 0
        weight -= 6 if 'W' in star.baseCode or 'W' in target.baseCode else 0
        weight -= 3 if 'N' in star.baseCode or 'N' in target.baseCode else 0
        weight -= 3 if 'D' in star.baseCode or 'D' in target.baseCode else 0
        weight -= 6 if star.tradeCode.subsector_capital or target.tradeCode.subsector_capital else 0
        weight -= 6 if star.tradeCode.other_capital or target.tradeCode.other_capital else 0
        weight -= 6 if star.tradeCode.sector_capital or target.tradeCode.sector_capital else 0
        assert 0 < weight, "Weight of edge between " + str(star) + " and " + str(
            target) + " must be positive"

        return weight

    def unilateral_filter(self, star):
        if star.zone in ['R', 'F']:
            return True
        if not AllyGen.imperial_align(star.alg_code):
            return True
        return False
