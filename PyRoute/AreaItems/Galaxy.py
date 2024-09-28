"""
Created on Mar 2, 2014

@author: tjoneslo
"""
import logging
import re
import codecs
import os
import ast
import itertools
import math
import networkx as nx
import numpy as np

from PyRoute.AllyGen import AllyGen
from PyRoute.AreaItems.AreaItem import AreaItem
from PyRoute.AreaItems.Allegiance import Allegiance
from PyRoute.AreaItems.Subsector import Subsector
from PyRoute.AreaItems.Sector import Sector
from PyRoute.Star import Star
from PyRoute.Calculation.TradeCalculation import TradeCalculation
from PyRoute.Calculation.TradeMPCalculation import TradeMPCalculation
from PyRoute.Calculation.CommCalculation import CommCalculation
from PyRoute.Calculation.OwnedWorldCalculation import OwnedWorldCalculation
from PyRoute.Calculation.NoneCalculation import NoneCalculation
from PyRoute.Calculation.XRouteCalculation import XRouteCalculation
from PyRoute.DataClasses.ReadSectorOptions import ReadSectorOptions
from PyRoute.Pathfinding.RouteLandmarkGraph import RouteLandmarkGraph


class Galaxy(AreaItem):
    """
    classdocs
    """
 
    def __init__(self, min_btn, max_jump=4):
        """
       Constructor
        """
        super(Galaxy, self).__init__('Charted Space')
        self.logger = logging.getLogger('PyRoute.Galaxy')
        self.ranges = nx.Graph()
        self.stars = nx.Graph()
        self.sectors = {}
        self.borders = AllyGen(self)
        self.output_path = 'maps'
        self.max_jump_range = max_jump
        self.min_btn = min_btn
        self.historic_costs = None
        self.big_component = None
        self.star_mapping = dict()
        self.trade = None

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['stars']
        del state['ranges']
        del state['borders']
        del state['logger']
        del state['trade']
        del state['sectors']
        del state['alg_sorted']
        return state

    # def read_sectors(self, sectors, pop_code, ru_calc,
    #                 route_reuse, trade_choice, route_btn, mp_threads, debug_flag, fix_pop=False):
    def read_sectors(self, options):
        assert isinstance(options, ReadSectorOptions), "options parm not ReadSectorOptions, is " + type(options).__name__
        route_reuse = options.route_reuse
        trade_choice = options.trade_choice
        route_btn = options.route_btn
        mp_threads = options.mp_threads
        debug_flag = options.debug_flag
        sectors = options.sectors
        pop_code = options.pop_code
        ru_calc = options.ru_calc
        fix_pop = options.fix_pop
        self._set_trade_object(route_reuse, trade_choice, route_btn, mp_threads, debug_flag)
        star_counter = 0
        loaded_sectors = set()
        from PyRoute.Inputs.ParseStarInput import ParseStarInput
        ParseStarInput.deep_space = {} if (options.deep_space is None or not isinstance(options.deep_space, dict)) else options.deep_space
        for sector in sectors:
            try:
                lines = [line for line in codecs.open(sector, 'r', 'utf-8')]
            except (OSError, IOError):
                self.logger.error("sector file %s not found" % sector)
                continue
            self.logger.debug('reading %s ' % sector)

            sec = Sector(lines[3], lines[4])
            sec.filename = os.path.basename(sector)
            if str(sec) not in loaded_sectors:
                loaded_sectors.add(str(sec))
            else:
                self.logger.error("sector file %s loads duplicate sector %s" % (sector, str(sec)))
                continue

            for lineno, line in enumerate(lines):
                if line.startswith('Hex'):
                    break
                if line.startswith('# Subsector'):
                    data = line[11:].split(':', 1)
                    pos = data[0].strip()
                    name = data[1].strip()
                    sec.subsectors[pos] = Subsector(name, pos, sec)
                if line.startswith('# Alleg:'):
                    alg_code = line[8:].split(':', 1)[0].strip()
                    alg_name = line[8:].split(':', 1)[1].strip().strip('"')

                    # A work around for the base Na codes which may be empire dependent.
                    alg_race = AllyGen.population_align(alg_code, alg_name)

                    base = AllyGen.same_align(alg_code)
                    if base not in self.alg:
                        self.alg[base] = Allegiance(base, AllyGen.same_align_name(base, alg_name), base=True, population=alg_race)
                    if alg_code not in self.alg:
                        self.alg[alg_code] = Allegiance(alg_code, alg_name, base=False, population=alg_race)

            for line in lines[lineno + 2:]:
                if line.startswith('#') or len(line) < 20:
                    continue
                star = Star.parse_line_into_star(line, sec, pop_code, ru_calc, fix_pop=fix_pop)
                if star:
                    assert star not in sec.worlds, "Star " + str(star) + " duplicated in sector " + str(sec)
                    star.index = star_counter
                    star_counter += 1
                    self.star_mapping[star.index] = star

                    sec.worlds.append(star)
                    sec.subsectors[star.subsector()].worlds.append(star)
                    star.alg_base_code = AllyGen.same_align(star.alg_code)

                    self.set_area_alg(star, self, self.alg)
                    self.set_area_alg(star, sec, self.alg)
                    self.set_area_alg(star, sec.subsectors[star.subsector()], self.alg)

                    star.tradeCode.sophont_list.append("{}A".format(self.alg[star.alg_code].population))
                    star.is_redzone = self.trade.unilateral_filter(star)
                    star.allegiance_base = self.alg[star.alg_base_code]
                    star.is_well_formed()

            self.sectors[sec.name] = sec
            self.logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds)))

        self.set_bounding_sectors()
        self.set_bounding_subsectors()
        self.set_positions()
        self.logger.debug("Allegiances: {}".format(self.alg))

    def add_star_to_galaxy(self, star: Star, star_counter: int, sec: Sector):
        assert star not in sec.worlds, "Star " + str(star) + " duplicated in sector " + str(sec)
        star.index = star_counter
        self.star_mapping[star.index] = star

        sec.worlds.append(star)
        sec.subsectors[star.subsector()].worlds.append(star)
        star.alg_base_code = AllyGen.same_align(star.alg_code)

        self.set_area_alg(star, self, self.alg)
        self.set_area_alg(star, sec, self.alg)
        self.set_area_alg(star, sec.subsectors[star.subsector()], self.alg)

        star.tradeCode.sophont_list.append("{}A".format(self.alg[star.alg_code].population))
        star.is_redzone = self.trade.unilateral_filter(star)
        star.allegiance_base = self.alg[star.alg_base_code]
        star.is_well_formed()
        return star_counter + 1

    def set_area_alg(self, star, area, algs: dict):
        full_alg = algs.get(star.alg_code, Allegiance(star.alg_code, 'Unknown Allegiance', base=False))
        base_alg = algs.get(star.alg_base_code, Allegiance(star.alg_base_code, 'Unknown Allegiance', base=True))

        area.alg.setdefault(star.alg_base_code, Allegiance(base_alg.code, base_alg.name, base=True)).worlds.append(star)
        if star.alg_code != star.alg_base_code:
            area.alg.setdefault(star.alg_code, Allegiance(full_alg.code, full_alg.name, base=False)).worlds.append(star)

    def set_positions(self):
        shadow_len = self.stars.number_of_nodes()
        for sector in self.sectors.values():
            for star in sector.worlds:
                if star not in self.ranges:
                    self.stars.add_node(star.index, star=star)
                self.ranges.add_node(star)
        self.logger.info("Total number of worlds: %s" % self.stars.number_of_nodes())
        shadow_len = self.stars.number_of_nodes()
        map_len = len(self.star_mapping)
        assert map_len == shadow_len, "Mismatch between shadow stars and stars mapping, " + str(shadow_len) + " and " + str(map_len)
        for item in self.stars.nodes:
            assert 'star' in self.stars.nodes[item], "Star attribute not set for item " + str(item)
        self.historic_costs = RouteLandmarkGraph(self.stars)

    def set_bounding_sectors(self):
        for sector, neighbor in itertools.combinations(self.sectors.values(), 2):
            if sector.x - 1 == neighbor.x and sector.y == neighbor.y:
                sector.spinward = neighbor
                neighbor.trailing = sector
            elif sector.x + 1 == neighbor.x and sector.y == neighbor.y:
                sector.trailing = neighbor
                neighbor.spinward = sector
            elif sector.x == neighbor.x and sector.y - 1 == neighbor.y:
                sector.rimward = neighbor
                neighbor.coreward = sector
            elif sector.x == neighbor.x and sector.y + 1 == neighbor.y:
                sector.coreward = neighbor
                neighbor.rimward = sector
            elif sector.x == neighbor.x and sector.y == neighbor.y:
                self.logger.error("Duplicate sector %s and %s" % (sector.name, neighbor.name))

    def set_bounding_subsectors(self):
        for sector in self.sectors.values():
            for subsector in sector.subsectors.values():
                subsector.set_bounding_subsectors()

    def generate_routes(self):
        self.trade.generate_routes()

    def _set_trade_object(self, reuse, routes, route_btn, mp_threads, debug_flag):
        # if trade object already set, bail out
        if self.trade is not None:
            return
        self.is_well_formed()
        if routes == 'trade':
            self.trade = TradeCalculation(self, self.min_btn, route_btn, reuse, debug_flag)
        elif routes == 'trade-mp':
            self.trade = TradeMPCalculation(self, self.min_btn, route_btn, reuse, debug_flag, mp_threads)
        elif routes == 'comm':
            self.trade = CommCalculation(self, reuse)
        elif routes == 'xroute':
            self.trade = XRouteCalculation(self)
        elif routes == 'owned':
            self.trade = OwnedWorldCalculation(self)
        elif routes == 'none':
            self.trade = NoneCalculation(self)

    def set_borders(self, border_gen, match):
        self.logger.info('setting borders...')
        if border_gen == 'range':
            self.borders.create_borders(match)
        elif border_gen == 'allygen':
            self.borders.create_ally_map(match)
        elif border_gen == 'erode':
            self.borders.create_erode_border(match)
        else:
            pass

    def write_routes(self, routes=None):
        path = os.path.join(self.output_path, 'ranges.txt')
        with open(path, "wb") as f:
            nx.write_edgelist(self.ranges, f, data=True)
        path = os.path.join(self.output_path, 'stars.txt')
        with open(path, "wb") as f:
            nx.write_edgelist(self.stars, f, data=True)
        path = os.path.join(self.output_path, 'borders.txt')
        with codecs.open(path, "wb", "utf-8") as f:
            for key, value in self.borders.borders.items():
                f.write("{}-{}: border: {}\n".format(key[0], key[1], value))

        if routes == 'xroute':
            path = os.path.join(self.output_path, 'stations.txt')
            with codecs.open(path, "wb", 'utf-8') as f:
                stars = [star for star in self.star_mapping.values() if star.tradeCount > 0]
                for star in stars:
                    f.write("{} - {}\n".format(star, star.tradeCount))

    def process_eti(self):
        self.logger.info("Processing ETI for worlds")
        for (world, neighbor) in self.stars.edges():
            worldstar = self.star_mapping[world]
            neighborstar = self.star_mapping[neighbor]
            distance = worldstar.distance(neighborstar)
            distanceMod = int(distance / 2)
            CargoTradeIndex = int(round(math.sqrt(
                max(worldstar.eti_cargo - distanceMod, 0) *
                max(neighborstar.eti_cargo - distanceMod, 0))))
            PassTradeIndex = int(round(math.sqrt(
                max(worldstar.eti_passenger - distanceMod, 0) *
                max(neighborstar.eti_passenger - distanceMod, 0))))
            self.stars[world][neighbor]['CargoTradeIndex'] = CargoTradeIndex
            self.stars[world][neighbor]['PassTradeIndex'] = PassTradeIndex
            if CargoTradeIndex > 0:
                worldstar.eti_cargo_volume += math.pow(10, CargoTradeIndex) * 10
                neighborstar.eti_cargo_volume += math.pow(10, CargoTradeIndex) * 10
                worldstar.eti_worlds += 1
                neighborstar.eti_worlds += 1
            if PassTradeIndex > 0:
                worldstar.eti_pass_volume += math.pow(10, PassTradeIndex) * 2.5
                neighborstar.eti_pass_volume += math.pow(10, PassTradeIndex) * 2.5

    def read_routes(self, routes=None):
        route_regex = "^({1,}) \(({3,}) (\d\d\d\d)\) ({1,}) \(({3,}) (\d\d\d\d)\) (\{.*\})"
        routeline = re.compile(route_regex)
        path = os.path.join(self.output_path, 'ranges.txt')
        with open(path, "wb") as f:
            for line in f:
                data = routeline.match(line).group()
                sec1 = data[2].strip()
                hex1 = data[3]
                sec2 = data[4].strip()
                hex2 = data[5]
                routeData = ast.literal_eval(data[6])

                world1 = self.sectors[sec1].find_world_by_pos(hex1)
                world2 = self.sectors[sec2].find_world_by_pos(hex2)

                self.ranges.add_edge_from([world1, world2, routeData])

    def process_owned_worlds(self):
        ow_names = os.path.join(self.output_path, 'owned-worlds-names.csv')
        ow_list = os.path.join(self.output_path, 'owned-worlds-list.csv')
        with codecs.open(ow_names, 'w+', 'utf-8') as f, codecs.open(ow_list, 'w+', 'utf-8') as g:

            for world in self.stars:
                worldstar = self.star_mapping[world]
                if worldstar.ownedBy == worldstar:
                    continue
                neighbours = [self.star_mapping[item] for item in self.stars.neighbors(world)]
                ownedBy = [star for star in neighbours if star.tl >= 9 and star.popCode >= 6 and star.port in 'ABC'
                           and star.ownedBy == star and AllyGen.are_owned_allies(star.alg_code, worldstar.alg_code)]

                ownedBy.sort(reverse=True,
                             key=lambda star: star.popCode)
                ownedBy.sort(reverse=True,
                             key=lambda star: star.importance - (star.distance(worldstar) - 1))

                owner = None
                if worldstar.ownedBy is None:
                    owner = None
                elif worldstar.ownedBy == 'Mr':
                    owner = 'Mr'
                elif worldstar.ownedBy == 'Re':
                    owner = 'Re'
                elif worldstar.ownedBy == 'Px':
                    owner = 'Px'
                elif len(worldstar.ownedBy) > 4:
                    ownedSec = worldstar.ownedBy[0:4]
                    ownedHex = worldstar.ownedBy[5:]
                    owner = None
                    self.logger.debug(
                        "World {}@({},{}) owned by {} - {}".format(worldstar, worldstar.col, worldstar.row, ownedSec, ownedHex))
                    if worldstar.col < 4 and worldstar.sector.spinward:
                        owner = worldstar.sector.spinward.find_world_by_pos(ownedHex)
                    elif worldstar.col > 28 and worldstar.sector.trailing:
                        owner = worldstar.sector.trailing.find_world_by_pos(ownedHex)

                    if worldstar.row < 4 and owner is None and worldstar.sector.coreward:
                        owner = worldstar.sector.coreward.find_world_by_pos(ownedHex)
                    elif worldstar.row > 36 and owner is None and worldstar.sector.rimward:
                        owner = worldstar.sector.rimward.find_world_by_pos(ownedHex)

                    # If we can't find world in the sector next door, try the this one
                    if owner is None:
                        owner = worldstar.sector.find_world_by_pos(ownedHex)
                elif len(worldstar.ownedBy) == 4:
                    owner = worldstar.sector.find_world_by_pos(worldstar.ownedBy)

                self.logger.debug("Worlds {} is owned by {}".format(worldstar, owner))

                ow_path_items = ['"{}"'.format(worldstar), '"{}"'.format(owner)]
                ow_path_items.extend(['"{}"'.format(item) for item in ownedBy[0:4]])
                ow_path_world = ', '.join(ow_path_items)
                f.write(ow_path_world + '\n')

                ow_list_items = [
                    '"{}"'.format(worldstar.sector.name[0:4]),
                    '"{}"'.format(worldstar.position),
                    '"{}"'.format(owner)
                ]
                ow_list_items.extend(['"O:{}"'.format(item.sec_pos(worldstar.sector)) for item in ownedBy[0:4]])
                ow_list_world = ', '.join(ow_list_items)
                g.write(ow_list_world + '\n')

                worldstar.ownedBy = (owner, ownedBy[0:4])

    def is_well_formed(self):
        for item in self.sectors:
            sector = self.sectors[item]
            assert isinstance(sector, Sector), "Galaxy sectors must be instance of Sector object"
            result, msg = sector.is_well_formed()
            assert result, msg
        for item in self.alg:
            allegiance = self.alg[item]
            assert isinstance(allegiance, Allegiance), "Galaxy allegiances must be instance of Allegiance object"
            result, msg = allegiance.is_well_formed()
            assert result, msg

        for item in self.stars.nodes:
            assert isinstance(item, int), "Star nodes must be integers"
            assert 'star' in self.stars.nodes[item], "Star attribute not set for item " + str(item)
            star = self.star_mapping[item]
            star.is_well_formed()

    def heuristic_distance_bulk(self, target):
        active_nodes = self.stars.nodes.values()
        raw = self.trade.shortest_path_tree.lower_bound_bulk(target)
        distances = self.trade.star_graph.distances_from_target(active_nodes, target)
        # Case-wise maximum of 2 or more admissible heuristics (approx-SP bound, existing route distances) is itself
        # admissible
        raw = np.maximum(raw, distances)

        return raw

    def route_cost(self, route):
        """
        Given a route, return its total cost via _compensated_ summation
        """
        total_weight = 0
        c = 0
        start = route[0]
        for end in route[1:]:
            y = float(self.stars[start][end]['weight']) - c
            t = total_weight + y
            c = (t - total_weight) - y

            total_weight = t

            start = end
        return total_weight

    '''
    Check that route doesn't revisit any stars
    '''
    def route_no_revisit(self, route):
        visited = set()

        for item in route:
            name = str(item)
            if name in visited:
                return False
            visited.add(name)

        return True
