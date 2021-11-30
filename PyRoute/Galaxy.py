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

from Star import Star
from  TradeCalculation import TradeCalculation, NoneCalculation, CommCalculation, XRouteCalculation, \
    OwnedWorldCalculation
from StatCalculation import ObjectStatistics
from AllyGen import AllyGen


class AreaItem(object):
    def __init__(self, name):
        self.name = name
        self.worlds = []
        self.stats = ObjectStatistics()
        self.alg = {}
        self.alg_sorted = []
        self._wiki_name = '[[{}]]'.format(name)

    def wiki_title(self):
        return self.wiki_name()

    def wiki_name(self):
        return self._wiki_name

    def __str__(self):
        return self.name

    def world_count(self):
        return len(self.worlds)


class Allegiance(AreaItem):
    def __init__(self, code, name, base=False, population='Huma'):
        super(Allegiance, self).__init__(Allegiance.allegiance_name(name, code, base))
        self.code = code
        self.base = base
        self.population = population
        self._wiki_name = Allegiance.set_wiki_name(name, code, base)

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['alg_sorted']
        return state

    @staticmethod
    def allegiance_name(name, code, base):
        if base:
            return name
        names = name.split(',') if ',' in name else [name, '']
        if code.startswith('Na'):
            return '{} {}'.format(names[0], names[1].strip())
        elif code.startswith('Cs'):
            return '{}s of the {}'.format(names[0].strip(), names[1].strip())
        elif ',' in name:
            return '{}, {}'.format(names[0].strip(), names[1].strip())
        return '{}'.format(name.strip())


    @staticmethod
    def set_wiki_name(name, code, base):
        names = name.split(',') if ',' in name else [name, '']
        if code.startswith('Na'):
            return '[[{}]] {}'.format(names[0].strip(), names[1].strip())
        elif code.startswith('Cs'):
            return '[[{}]]s of the [[{}]]'.format(names[0].strip(), names[1].strip())
        elif ',' in name:
            if base:
                return '[[{}]]'.format(names[0].strip())
            else:
                return '[[{}]], [[{}]]'.format(names[0].strip(), names[1].strip())
        return '[[{}]]'.format(name.strip())

    def __str__(self):
        return '{} ([{})'.format(self.name, self.code)

    def is_unclaimed(self):
        return AllyGen.is_unclaimed(self)

    def is_wilds(self):
        return AllyGen.is_wilds(self)

    def is_client_state(self):
        return AllyGen.is_client_state(self)

    def are_allies(self, other):
        return AllyGen.are_allies(self.code, other.code)

class Subsector(AreaItem):
    def __init__(self, name, position, sector):
        super(Subsector, self).__init__(name)
        self.positions = ["ABCD", "EFGH", "IJKL", "MNOP"]
        self.sector = sector
        self.position = position
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None
        self.dx = sector.dx
        self.dy = sector.dy
        self._wiki_name = Subsector.set_wiki_name(name, sector.name, position)
    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['sector']
        del state['spinward']
        del state['trailing']
        del state['coreward']
        del state['rimward']
        del state['alg_sorted']
        del state['positions']
        return state

    @staticmethod
    def set_wiki_name(name, sector_name, position):
        if len(name) == 0:
            return "{0} location {1}".format(sector_name, position)
        else:
            if "(" in name:
                return '[[{0} Subsector|{1}]]'.format(name, name[:-7])
            else:
                return '[[{0} Subsector|{0}]]'.format(name)

    def wiki_title(self):
        return '{0} - {1}'.format(self.wiki_name(), self.sector.wiki_name())

    def subsector_name(self):
        if len(self.name) == 0:
            return "Location {}".format(self.position)
        else:
            return self.name[:-9] if self.name.endswith('Subsector') else self.name

    def set_bounding_subsectors(self):
        posrow = 0
        for row in self.positions:
            if self.position in row:
                pos = self.positions[posrow].index(self.position)
                break
            posrow += 1

        if posrow == 0:
            self.coreward = self.sector.coreward.subsectors[self.positions[3][pos]] if self.sector.coreward else None
        else:
            self.coreward = self.sector.subsectors[self.positions[posrow - 1][pos]]

        if pos == 0:
            self.spinward = self.sector.spinward.subsectors[self.positions[posrow][3]] if self.sector.spinward else None
        else:
            self.spinward = self.sector.subsectors[self.positions[posrow][pos - 1]]

        if posrow == 3:
            self.rimward = self.sector.rimward.subsectors[self.positions[0][pos]] if self.sector.rimward else None
        else:
            self.rimward = self.sector.subsectors[self.positions[posrow + 1][pos]]

        if pos == 3:
            self.trailing = self.sector.trailing.subsectors[self.positions[posrow][0]] if self.sector.trailing else None
        else:
            self.trailing = self.sector.subsectors[self.positions[posrow][pos + 1]]


class Sector(AreaItem):
    def __init__(self, name, position):
        # The name as passed from the Galaxy read include the comment marker at the start of the line
        # So strip the comment marker, then strip spaces.
        super(Sector, self).__init__(name[1:].strip())
        self._wiki_name = '[[{0} Sector|{0}]]'.format(self.sector_name())

        # Same here, the position has a leading comment marker
        self.x = int(position[1:].split(',')[0])
        self.y = int(position[1:].split(',')[1])
        
        self.dx = self.x * 32
        self.dy = self.y * 40
        self.subsectors = {}
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None

    # For the JSONPickel work
    def __getstate__(self):
        state = self.__dict__.copy()
        del state['spinward']
        del state['trailing']
        del state['coreward']
        del state['rimward']
        del state['alg_sorted']
        return state

    def __str__(self):
        return '{} ({},{})'.format(self.name, str(self.x), str(self.y))

    def sector_name(self):
        return self.name[:-7] if self.name.endswith('Sector') else self.name

    def find_world_by_pos(self, pos):
        for world in self.worlds:
            if world.position == pos:
                return world
        return None


class Galaxy(AreaItem):
    """
    classdocs
    """
 
    def __init__(self, min_btn, max_jump=4, route_btn=8):
        """
       Constructor
        """
        super(Galaxy, self).__init__('Charted Space')
        self.logger = logging.getLogger('PyRoute.Galaxy')
        self.stars = nx.Graph()
        self.ranges = nx.Graph()
        self.sectors = {}
        self.borders = AllyGen(self)
        self.output_path = 'maps'
        self.max_jump_range = max_jump
        self.min_btn = min_btn
        self.route_btn = route_btn

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

    def read_sectors(self, sectors, pop_code, ru_calc):
        for sector in sectors:
            try:
                lines = [line for line in codecs.open(sector, 'r', 'utf-8')]
            except (OSError, IOError):
                self.logger.error("sector file %s not found" % sector)
                continue
            self.logger.debug('reading %s ' % sector)

            sec = Sector(lines[3], lines[4])
            sec.filename = os.path.basename(sector)

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
                star = Star.parse_line_into_star(line, sec, pop_code, ru_calc)
                if star:
                    sec.worlds.append(star)
                    sec.subsectors[star.subsector()].worlds.append(star)
                    star.alg_base_code = AllyGen.same_align(star.alg_code)

                    self.set_area_alg(star, self, self.alg)
                    self.set_area_alg(star, sec, self.alg)
                    self.set_area_alg(star, sec.subsectors[star.subsector()], self.alg)

                    star.tradeCode.sophont_list.append("{}A".format(self.alg[star.alg_code].population))

            self.sectors[sec.name] = sec
            self.logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds)))

        self.set_bounding_sectors()
        self.set_bounding_subsectors()
        self.set_positions()
        self.logger.debug("Allegiances: {}".format(self.alg))

    def set_area_alg(self, star, area, algs):
        full_alg = algs.get(star.alg_code, Allegiance(star.alg_code, 'Unknown Allegiance', base=False))
        base_alg = algs.get(star.alg_base_code, Allegiance(star.alg_base_code, 'Unknown Allegiance', base=True))

        area.alg.setdefault(star.alg_base_code, Allegiance(base_alg.code, base_alg.name, base=True)).worlds.append(star)
        if star.alg_code != star.alg_base_code:
            area.alg.setdefault(star.alg_code, Allegiance(full_alg.code, full_alg.name, base=False)).worlds.append(star)

    def set_positions(self):
        for sector in self.sectors.values():
            for star in sector.worlds:
                self.stars.add_node(star)
                self.ranges.add_node(star)
        self.logger.info("Total number of worlds: %s" % self.stars.number_of_nodes())

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

    def generate_routes(self, routes, reuse=10):
        if routes == 'trade':
            self.trade = TradeCalculation(self, self.min_btn, self.route_btn, reuse)
        elif routes == 'comm':
            self.trade = CommCalculation(self, reuse)
        elif routes == 'xroute':
            self.trade = XRouteCalculation(self)
        elif routes == 'owned':
            self.trade = OwnedWorldCalculation(self)
        elif routes == 'none':
            self.trade = NoneCalculation(self)

        self.trade.generate_routes()

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
                stars = [star for star in self.stars if star.tradeCount > 0]
                for star in stars:
                    f.write("{} - {}\n".format(star, star.tradeCount))

    def process_eti(self):
        self.logger.info("Processing ETI for worlds")
        for (world, neighbor) in self.stars.edges():
            distance = world.hex_distance(neighbor)
            distanceMod = int(distance / 2)
            CargoTradeIndex = int(round(math.sqrt(
                max(world.eti_cargo - distanceMod, 0) *
                max(neighbor.eti_cargo - distanceMod, 0))))
            PassTradeIndex = int(round(math.sqrt(
                max(world.eti_passenger - distanceMod, 0) *
                max(neighbor.eti_passenger - distanceMod, 0))))
            self.stars[world][neighbor]['CargoTradeIndex'] = CargoTradeIndex
            self.stars[world][neighbor]['PassTradeIndex'] = PassTradeIndex
            if CargoTradeIndex > 0:
                world.eti_cargo_volume += math.pow(10, CargoTradeIndex) * 10
                neighbor.eti_cargo_volume += math.pow(10, CargoTradeIndex) * 10
                world.eti_worlds += 1
                neighbor.eti_worlds += 1
            if PassTradeIndex > 0:
                world.eti_pass_volume += math.pow(10, PassTradeIndex) * 2.5
                neighbor.eti_pass_volume += math.pow(10, PassTradeIndex) * 2.5

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
                if world.ownedBy == world:
                    continue
                ownedBy = [star for star in self.stars.neighbors(world) \
                           if star.tl >= 9 and star.popCode >= 6 and \
                           star.port in 'ABC' and star.ownedBy == star and \
                           AllyGen.are_owned_allies(star.alg_code, world.alg_code)]

                ownedBy.sort(reverse=True,
                             key=lambda star: star.popCode)
                ownedBy.sort(reverse=True,
                             key=lambda star: star.importance - (star.hex_distance(world) - 1))

                owner = None
                if world.ownedBy is None:
                    owner = None
                elif world.ownedBy == 'Mr':
                    owner = 'Mr'
                elif world.ownedBy == 'Re':
                    owner = 'Re'
                elif world.ownedBy == 'Px':
                    owner = 'Px'
                elif len(world.ownedBy) > 4:
                    ownedSec = world.ownedBy[0:4]
                    ownedHex = world.ownedBy[5:]
                    owner = None
                    self.logger.debug(
                        "World {}@({},{}) owned by {} - {}".format(world, world.col, world.row, ownedSec, ownedHex))
                    if world.col < 4 and world.sector.spinward:
                        owner = world.sector.spinward.find_world_by_pos(ownedHex)
                    elif world.col > 28 and world.sector.trailing:
                        owner = world.sector.trailing.find_world_by_pos(ownedHex)

                    if world.row < 4 and owner is None and world.sector.coreward:
                        owner = world.sector.coreward.find_world_by_pos(ownedHex)
                    elif world.row > 36 and owner is None and world.sector.rimward:
                        owner = world.sector.rimward.find_world_by_pos(ownedHex)

                    # If we can't find world in the sector next door, try the this one
                    if owner is None:
                        owner = world.sector.find_world_by_pos(ownedHex)
                elif len(world.ownedBy) == 4:
                    owner = world.sector.find_world_by_pos(world.ownedBy)

                self.logger.debug("Worlds {} is owned by {}".format(world, owner))

                ow_path_items = ['"{}"'.format(world), '"{}"'.format(owner)]
                ow_path_items.extend(['"{}"'.format(item) for item in ownedBy[0:4]])
                ow_path_world = ', '.join(ow_path_items)
                f.write(ow_path_world + '\n')

                ow_list_items = [
                    '"{}"'.format(world.sector.name[0:4]),
                    '"{}"'.format(world.position),
                    '"{}"'.format(owner)
                ]
                ow_list_items.extend(['"O:{}"'.format(item.sec_pos(world.sector)) for item in ownedBy[0:4]])
                ow_list_world = ', '.join(ow_list_items)
                g.write(ow_list_world + '\n')

                world.ownedBy = (owner, ownedBy[0:4])
