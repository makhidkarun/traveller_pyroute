'''
Created on Mar 2, 2014

@author: tjoneslo
'''
import logging
import re
import codecs
import os
import itertools
import networkx as nx

from Star import Star
from TradeCalculation import TradeCalculation, NoneCalculation, CommCalculation
from StatCalculation import ObjectStatistics
from AllyGen import AllyGen

class Subsector(object):
    def __init__(self, name, position, sector):
        self.sector = sector
        self.name = name
        self.position = position
        self.stats = ObjectStatistics()
        self.worlds = []

    def wiki_name(self):
        return '[[{0} Subsector|{0}]]'.format(self.name)

class Sector (object):
    def __init__ (self, name, position):
        self.name = name[1:].strip()
        self.x = int(position[1:].split(',')[0])
        self.y = int(position[1:].split(',')[1])
        self.dx = self.x * 32
        self.dy = self.y * 40
        self.subsectors = {}
        self.worlds = []
        self.stats = ObjectStatistics()
        self.spinward = None
        self.trailing = None
        self.coreward = None
        self.rimward = None
        
    def __str__(self):
        return "{} ({},{})".format(self.name, str(self.x), str(self.y))

    def wiki_name(self):
        if self.name.endswith('Sector'):
            name = self.name[:-7]
        else:
            name = self.name
        return '|[[{0} Sector|{0}]]'.format(name)

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
((\{ [+-]?[0-5] \}) +(\([0-9A-Z]{3}[+-]\d\)) +(\[[0-9A-Z]{4}\])|( ) ( ) ( )) +
(\w{1,5}|-) +
(\w\w?|-|\*) +
(\w|-) +
([0-9][0-9A-F][0-9A-F]) +
(\d{1,}| )+
([A-Z0-9-][A-Za-z0-9-]{1,3}) 
(.*)
"""
#(\{ [0-9] \}|\{ -[1-3] \}| ) +

        star_regex = ''.join([line.rstrip('\n') for line in regex])
        self.logger.debug("Pattern: %s" % star_regex)
        self.starline = re.compile(star_regex)
        self.stars = nx.Graph()
        self.ranges = nx.Graph()
        self.routes = nx.Graph()
        self.sectors = []
        self.alg = {}
        self.stats = ObjectStatistics()
        self.borders = AllyGen(self)
        self.output_path = 'maps'
        self.max_jump_range = max_jump
        self.min_btn = min_btn
        self.route_btn = route_btn
        
    def read_sectors (self, sectors, pop_code, match):
        for sector in sectors:
            try:
                lines = [line for line in codecs.open(sector,'r', 'utf-8')]
            except (OSError, IOError):
                self.logger.error("sector file %s not found" % sector)
                continue
            
            sec = Sector (lines[3], lines[4])
            
            lineno = 0
            for line in lines:
                lineno += 1
                if line.startswith ('Hex'):
                    lineno += 1
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
                        self.alg[algCode] = (algName, ObjectStatistics())
                    elif match == 'separate':
                        base = AllyGen.same_align(algCode)
                        if base not in self.alg: self.alg[base] = (algName, ObjectStatistics())
                        if algCode not in self.alg: self.alg[algCode] = (algName, ObjectStatistics())
                        pass
                
            for line in lines[lineno:]:
                if line.startswith('#') or len(line) < 20: 
                    continue
                star = Star (line, self.starline, sec, pop_code)
                sec.worlds.append(star)
                sec.subsectors[star.subsector()].worlds.append(star)
            
            self.sectors.append(sec)
            self.logger.info("Sector {} loaded {} worlds".format(sec, len(sec.worlds) ) )

        self.set_bounding_sectors()
        self.set_positions()
        
    def set_positions(self):
        for sector in self.sectors:
            if sector is None: continue
            for star in sector.worlds:
                self.stars.add_node(star)
                self.ranges.add_node(star)
                self.routes.add_node(star)
        self.logger.info("Total number of worlds: %s" % self.stars.number_of_nodes())
        
    def set_bounding_sectors(self):
        for sector, neighbor in itertools.combinations(self.sectors,2):
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
    
    def generate_routes(self, routes):
        if routes == 'trade':
            self.trade = TradeCalculation(self, self.min_btn, self.route_btn)
        elif routes == 'comm':
            self.trade = CommCalculation(self)
        elif routes == 'none':
            self.trade = NoneCalculation(self)

        self.trade.generate_routes()
        
    def set_borders(self, border_gen, match):
        self.logger.info('setting borders...')
        if border_gen == 'range':
            self.borders.create_borders(match)
        elif border_gen == 'allygen':
            self.borders.create_ally_map(match)
        else:
            pass

    def write_routes(self):
        path = os.path.join(self.output_path, 'routes.txt')
        with codecs.open(path, 'wb') as f:
            nx.write_edgelist(self.routes, f, data=True)
        path = os.path.join(self.output_path, 'ranges.txt')
        with codecs.open(path, "wb") as f:
            nx.write_edgelist(self.ranges, f, data=True)
        path = os.path.join(self.output_path, 'stars.txt')
        with codecs.open(path, "wb") as f:
            nx.write_edgelist(self.stars, f, data=True)
        path = os.path.join (self.output_path, 'borders.txt')
        with open(path, "wb") as f:
            for key, value in self.borders.borders.iteritems():
                f.write("{}-{}: border: {}\n".format(key[0],key[1], value))
    

    def process_owned_worlds(self):
        path = os.path.join(self.output_path, 'owned-worlds.txt')
        with codecs.open(path,'w+', 'utf-8') as f:

            for world in self.stars.nodes_iter():
                if world.ownedBy == world:
                    continue
                ownedBy = [star for star in self.stars.neighbors_iter(world) \
                            if star.tl >= 9 and star.popCode >= 6 and \
                               star.port in 'ABC' and star.ownedBy == star and \
                               star.alg[0:2] == world.alg[0:2]]
                
                ownedBy.sort(reverse=True,
                             key=lambda star: star.popCode)
                ownedBy.sort(reverse=True, 
                             key=lambda star: star.importance - (star.hex_distance(world) - 1))
                
                owner = None
                if len(world.ownedBy) > 4:
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
                    
                    
                elif len(world.ownedBy) == 4:
                    owner = world.sector.find_world_by_pos(world.ownedBy)
                self.logger.debug(u"Worlds {} is owned by {}".format(world,owner))
                f.write (u'"{}" : "{}", {}\n'.format(world, owner,
                                            (u', '.join(u'"' + repr(item) + u'"' for item in ownedBy[0:4]))))
                world.ownedBy = (owner, ownedBy[0:4])

