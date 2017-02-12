'''
Created on Mar 2, 2014

@author: tjoneslo
'''
import logging
import re
import codecs
import os
import ast
import itertools
import networkx as nx

from Star import Star
from TradeCalculation import TradeCalculation, NoneCalculation, CommCalculation, XRouteCalculation, OwnedWorldCalculation
from StatCalculation import ObjectStatistics
from AllyGen import AllyGen

class AreaItem(object):
    def __init__(self, name):
        self.name=name
        self.worlds = []
        self.stats = ObjectStatistics()

    def wiki_title(self):
        return self.wiki_name()

    def wiki_name(self):
        return u'[[{}]]'.format(self.name)

class Allegiance(AreaItem):
    def __init__(self, code, name):
        super(Allegiance, self).__init__(name)
        self.code = code

    def wiki_name(self):
        if self.code.startswith('Na'):
            names = self.name.split (',')
            return u'[[{}]] {}'.format(names[0], names[1].strip())
        elif self.code.startswith('Cs'):
            names = self.name.split(',')
            return u'[[{}]]s of the [[{}]]'.format(names[0].strip(), names[1].strip())
        elif ',' in self.name:
            names=self.name.split(',')
            return u'[[{}]], [[{}]]'.format(names[0].strip(), names[1].strip())
        return  u'[[{}]]'.format(self.name)

class Subsector(AreaItem):
    def __init__(self, name, position, sector):
        super(Subsector, self).__init__(name)
        self.positions = ["ABCD","EFGH","IJKL","MNOP"]
        self.sector = sector
        self.position = position
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None
        self.dx = sector.dx
        self.dy = sector.dy
        self.alg = {}

    def wiki_name(self):
        if len(self.name) == 0:
            return u'Position {0}'.format(self.position)
        else:
            if "(" in self.name:
                return u'[[{0} Subsector|{1}]]'.format(self.name, self.name[:-7])
            else:
                return u'[[{0} Subsector|{0}]]'.format(self.name)
    
    def wiki_title(self):
        return u'{0} - {1}'.format(self.wiki_name(), self.sector.wiki_name())
 
    def set_bounding_subsectors (self):
        posrow = 0
        for row in self.positions:
            if self.position in row:
                pos = self.positions[posrow].index(self.position)
                break
            posrow += 1

        if posrow == 0:
            self.coreward = self.sector.coreward.subsectors[self.positions[3][pos]] if self.sector.coreward else None
        else: 
            self.coreward = self.sector.subsectors[self.positions[posrow-1][pos]]

        if pos == 0:
            self.spinward = self.sector.spinward.subsectors[self.positions[posrow][3]] if self.sector.spinward else None
        else:
            self.spinward = self.sector.subsectors[self.positions[posrow][pos - 1]]

        if posrow == 3:
            self.rimward = self.sector.rimward.subsectors[self.positions[0][pos]] if self.sector.rimward else None
        else:
            self.rimward = self.sector.subsectors[self.positions[posrow+1][pos]]
            
        if pos == 3:
            self.trailing = self.sector.trailing.subsectors[self.positions[posrow][0]] if self.sector.trailing else None
        else:
            self.trailing = self.sector.subsectors[self.positions[posrow][pos + 1]]         

class Sector (AreaItem):
    def __init__ (self, name, position):
        super(Sector, self).__init__(name[1:].strip())

        self.x = int(position[1:].split(',')[0])
        self.y = int(position[1:].split(',')[1])
        self.dx = self.x * 32
        self.dy = self.y * 40
        self.subsectors = {}
        self.alg = {}
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None
        
    def __str__(self):
        return u"{} ({},{})".format(self.name, str(self.x), str(self.y))

    def sector_name (self):
        return self.name[:-7] if self.name.endswith(u'Sector') else self.name
    
    def wiki_name(self):
        return u'[[{0} Sector|{0}]]'.format(self.sector_name())

    def find_world_by_pos(self, pos):
        for world in self.worlds:
            if world.position == pos:
                return world
        return None
    

class Galaxy(object):
    '''
    classdocs
    '''
    def __init__(self, min_btn, max_jump=4, route_btn=8):
        '''
       Constructor
        '''
        self.logger = logging.getLogger('PyRoute.Galaxy')
        regex = """
^(\d\d\d\d) +
(.{15,}) +
(\w\w\w\w\w\w\w-\w) +
(.{15,}) +
((\{ [+-]?[0-5] \}) +(\([0-9A-Z]{3}[+-]\d\)|- ) +(\[[0-9A-Z]{4}\]| -)|( ) ( ) ( )) +
(\w{1,5}|-| ) +
(\w{1,3}|-|\*) +
(\w|-) +
([0-9X][0-9A-FX][0-9A-FX]) +
(\d{1,}| ) +
([A-Z0-9-][A-Za-z0-9?-]{1,3}) 
(.*)
"""
#(\{ [0-9] \}|\{ -[1-3] \}| ) +
        star_regex = ''.join([line.rstrip('\n') for line in regex])
        self.logger.debug("Pattern: %s" % star_regex)
        self.starline = re.compile(star_regex)
        self.stars = nx.Graph()
        self.ranges = nx.Graph()
        self.sectors = {}
        self.alg = {}
        self.stats = ObjectStatistics()
        self.borders = AllyGen(self)
        self.output_path = 'maps'
        self.max_jump_range = max_jump
        self.min_btn = min_btn
        self.route_btn = route_btn
        
    def read_sectors (self, sectors, pop_code, match, ru_calc):
        for sector in sectors:
            try:
                lines = [line for line in codecs.open(sector,'r', 'utf-8')]
            except (OSError, IOError):
                self.logger.error("sector file %s not found" % sector)
                continue
            self.logger.debug('reading %s ' % sector)
            
            sec = Sector (lines[3], lines[4])
            sec.filename = os.path.basename(sector)
            
            for lineno, line in enumerate(lines):
                if line.startswith ('Hex'):
                    break
                if line.startswith ('# Subsector'):
                    data = line[11:].split(':',1)
                    pos  = data[0].strip()
                    name = data[1].strip()
                    sec.subsectors[pos] = Subsector(name, pos, sec)
                if line.startswith ('# Alleg:'):
                    algCode = line[8:].split(':',1)[0].strip()
                    algName = line[8:].split(':',1)[1].strip().strip('"')
                    # Collapse same Aligned into one
                    if match == 'collapse':
                        algCode = AllyGen.same_align(algCode)
                        if algCode not in self.alg: self.alg[algCode] = Allegiance(algCode, algName) 
                    elif match == 'separate':
                        base = AllyGen.same_align(algCode)
                        if base not in self.alg: self.alg[base] = Allegiance(base, algName)
                        if algCode not in self.alg: self.alg[algCode] = Allegiance(algCode, algName)
                        pass
                
            for line in lines[lineno+2:]:
                if line.startswith('#') or len(line) < 20: 
                    continue
                star = Star (line, self.starline, sec, pop_code, ru_calc)
                sec.worlds.append(star)
                sec.subsectors[star.subsector()].worlds.append(star)
                
                self.set_area_alg(star, self, match, self.alg)
                self.set_area_alg(star, sec, match, self.alg)
                self.set_area_alg(star, sec.subsectors[star.subsector()], match, self.alg)

            self.sectors[sec.name] = sec
            self.logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds) ) )

        self.set_bounding_sectors()
        self.set_bounding_subsectors()
        self.set_positions()

    def set_area_alg(self, star, area, match, algs):
        base = AllyGen.same_align(star.alg)
        star.alg_base = base
        
        if match == 'collapse':
            base_alg = algs.get(base, Allegiance(base, 'Unknown Allegiance'))
            area.alg.setdefault(base, Allegiance(base_alg.code, base_alg.name)).worlds.append(star)
        elif match == 'separate':
            base_alg = algs.get(star.alg, Allegiance(star.alg, 'Unknown Allegiance'))
            area.alg.setdefault(star.alg, Allegiance(base_alg.code, base_alg.name)).worlds.append(star)
            
            if base != star.alg:
                base_alg = algs[base]
                area.alg.setdefault(base, Allegiance(base_alg.code, base_alg.name)).worlds.append(star)
                
    def set_positions(self):
        for sector in self.sectors.itervalues():
            for star in sector.worlds:
                self.stars.add_node(star)
                self.ranges.add_node(star)
        self.logger.info("Total number of worlds: %s" % self.stars.number_of_nodes())
        
    def set_bounding_sectors(self):
        for sector, neighbor in itertools.combinations(self.sectors.itervalues(),2):
            if sector.x - 1 == neighbor.x and sector.y == neighbor.y:
                sector.spinward = neighbor
                neighbor.trailing = sector
            elif sector.x + 1 == neighbor.x and sector.y == neighbor.y:
                sector.trailing = neighbor
                neighbor.spinward = sector
            elif sector.x == neighbor.x and sector.y - 1 == neighbor.y:
                sector.coreward = neighbor
                neighbor.rimward = sector
            elif sector.x == neighbor.x and sector.y + 1 == neighbor.y:
                sector.rimward = neighbor
                neighbor.coreward = sector
            elif sector.x == neighbor.x and sector.y == neighbor.y:
                self.logger.error("Duplicate sector %s and %s" % (sector.name, neighbor.name))

    def set_bounding_subsectors(self):
        for sector in self.sectors.itervalues():
            for subsector in sector.subsectors.itervalues():
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
        path = os.path.join (self.output_path, 'borders.txt')
        with codecs.open(path, "wb", "utf-8") as f:
            for key, value in self.borders.borders.iteritems():
                f.write(u"{}-{}: border: {}\n".format(key[0],key[1], value))

        if routes == 'xroute':
            path = os.path.join (self.output_path, 'stations.txt')
            with codecs.open(path, "wb", 'utf-8') as f:
                stars = [star for star in self.stars.nodes_iter() if star.tradeCount > 0]
                for star in stars:
                    f.write (u"{} - {}\n".format(star, star.tradeCount))
    
    def read_routes (self, routes=None):
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
                
                self.ranges.add_edge(world1, world2, routeData)
               

    def process_owned_worlds(self):
        ow_names = os.path.join(self.output_path, 'owned-worlds-names.csv')
        ow_list = os.path.join(self.output_path, 'owned-worlds-list.csv')
        with codecs.open(ow_names, 'w+', 'utf-8') as f, codecs.open(ow_list, 'w+', 'utf-8') as g:

            for world in self.stars.nodes_iter():
                if world.ownedBy == world:
                    continue
                ownedBy = [star for star in self.stars.neighbors_iter(world) \
                            if star.tl >= 9 and star.popCode >= 6 and \
                               star.port in 'ABC' and star.ownedBy == star and \
                               AllyGen.are_owned_allies(star.alg, world.alg)]
                
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
                    self.logger.debug(u"World {}@({},{}) owned by {} - {}".format(world, world.col, world.row, ownedSec, ownedHex))
                    if world.col < 4 and world.sector.spinward:
                        owner = world.sector.spinward.find_world_by_pos(ownedHex)
                    elif world.col > 28 and world.sector.trailing:
                        owner = world.sector.trailing.find_world_by_pos(ownedHex)

                    if world.row < 4 and owner is None and world.sector.coreward:
                        owner = world.sector.coreward.find_world_by_pos(ownedHex)
                    elif world.row > 36 and owner is None and world.sector.rimward:
                        owner = world.sector.rimward.find_world_by_pos(ownedHex)
                    
                    # If we can't find world in the sector next door, try the this one
                    if owner == None:
                        owner = world.sector.find_world_by_pos(ownedHex)
                elif len(world.ownedBy) == 4:
                    owner = world.sector.find_world_by_pos(world.ownedBy)

                self.logger.debug(u"Worlds {} is owned by {}".format(world,owner))
                
                ow_path_items = [u'"{}"'.format(world), u'"{}"'.format(owner)]
                ow_path_items.extend([u'"{}"'.format(item) for item in ownedBy[0:4]])
                ow_path_world = u', '.join(ow_path_items)
                f.write(ow_path_world + u'\n')
                
                
                ow_list_items = [u'"{}"'.format(world.sector.name[0:4])]
                ow_list_items.append(u'"{}"'.format(world.position))
                ow_list_items.append(u'"{}"'.format(owner))
                ow_list_items.extend([u'"O:{}"'.format(item.sec_pos(world.sector)) for item in ownedBy[0:4]])
                ow_list_world = u', '.join(ow_list_items)
                g.write(ow_list_world + u'\n')
                
                world.ownedBy = (owner, ownedBy[0:4])
