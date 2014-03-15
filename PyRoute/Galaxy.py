'''
Created on Mar 2, 2014

@author: tjoneslo
'''
import logging
import re
import codecs
import networkx as nx
from operator import attrgetter

from Star import Star
from TradeCalculation import TradeCalculation

class Sector (object):
    def __init__ (self, name, position):
        self.name = name[1:].strip()
        self.x = int(position[1:].split(',')[0])
        self.y = int(position[1:].split(',')[1])
        self.dx = self.x + 10 * 32
        self.dy = self.y + 10 * 40
        self.subsectors = {}
        self.alg = {}
        self.worlds = []

class Galaxy(object):
    '''
    classdocs
    '''
    def __init__(self, x, y):
        '''
        Constructor
        '''
        self.logger = logging.getLogger('PyRoute.Galaxy')
        regex = """
^(\d\d\d\d) +
(.{15,}) +
(\w\w\w\w\w\w\w-\w) +
(.{15,}) +
(\{ [-]?\d \}| ) +
(\([0-9A-Z]{3}[+-]\d\)| ) +
(\[[0-9A-Z]{4}\]| ) +
(\w{1,5}|-) +
(\w|-) +
(\w|-) +
([0-9][0-9A-F][0-9A-F]) +
(\d{1,}| )+
(\w\w) +
(.*)
"""
        star_regex = ''.join([line.rstrip('\n') for line in regex])
        self.logger.debug("Pattern: %s" % star_regex)
        self.starline = re.compile(star_regex)
        self.stars = nx.DiGraph()
        self.ranges = nx.DiGraph()
        self.sectors = {}
        self.dx = x * 32
        self.dy = y * 40
        #self.starpos = [[None for x in xrange(self.dx)] for x in xrange(self.dy)]
        self.starwtn = []
        self.trade = TradeCalculation(self)

        
    def read_sectors (self, sectors):
        for sector in sectors:
            try:
                lines = [line.strip() for line in codecs.open(sector,'r', 'utf-8')]
            except (OSError, IOError):
                self.logger.error("sector file %s not found" % sector)
                continue
            
            sec = Sector (lines[3], lines[4])
            
            self.logger.info("Sector: {} ({}, {})".format(sec.name, str(sec.x), str(sec.y)) )
            
            lineno = 0
            for line in lines:
                lineno += 1
                if line.startswith ('Hex'):
                    lineno += 1
                    break
                if line.startswith ('# Subsector'):
                    sec.subsectors[line[11:].split(':',1)[0].strip()] = line[11:].split(':',1)[1].strip()
                if line.startswith ('# Alleg:'):
                    sec.alg[line[8:].split(':',1)[0]] = line[8:].split(':',1)[1].strip().strip('"')
                
            for line in lines[lineno:]:
                if line.startswith('#') or len(line) < 20: 
                    continue
                star = Star (line, self.starline,sec.dx, sec.dy)
                sec.worlds.append(star)
            
            self.sectors[sec.name] = sec
            
            self.logger.info("processed %s worlds for %s" % (len(sec.worlds), sec.name))

    def set_positions(self):
        for sector in self.sectors.values():
            for star in sector.worlds:
                self.stars.add_node(star)
                self.ranges.add_node(star)
                self.starwtn.append(star);
        self.logger.info("graph node count: %s" % self.stars.number_of_nodes())
        self.starwtn = sorted(self.starwtn, key=attrgetter('wtn'), reverse=True)
        self.logger.debug("wtn array size: %s" % len (self.starwtn))
    
    def set_edges(self):
        self.set_positions()
        for star in self.stars.nodes_iter():
            for neighbor in self.stars.nodes_iter():
                dist = star.hex_distance (neighbor)
                if star == neighbor or\
                    neighbor.zone in ['R','F']:
                    continue
                max_dist = self.trade.btn_range[ min(max (0, star.wtn-8), 5)]
                if dist <= max_dist:
                    self.ranges.add_edge(star, neighbor, {'distance': dist})
                if dist <= 4 :               
                    self.stars.add_edge (star, neighbor, {'distance': dist,
                                                      'weight': star.weight(neighbor),
                                                      'trade': 0,
                                                      'btn': self.trade.get_btn(star, neighbor)})
        self.logger.info("Jump routes: %s - Distances: %s" % 
                         (self.stars.number_of_edges(), self.ranges.number_of_edges()))
    
        
    def write_routes(self):
        with open("./routes.txt", 'wb') as f:
            nx.write_edgelist(self.stars, f, data=True)
        with open("./ranges.txt", "wb") as f:
            nx.write_edgelist(self.ranges, f, data=True)
        
    def get_alg(self, new, old):
        if new == 'Na' or new == 'Ba' or new == 'Cs':
            return old
        if old is None:
            return new
        if new is None:
            return old
        if new == old:
            return new
        return new;
    
                    
    def set_borders(self):
        self.align = [[None for x in xrange(self.dx)] for x in xrange(self.dy)]
        for star in self.stars.nodes_iter():
            self.align[star.x][star.y] = star.alg

        for w in xrange(2):
            for x in xrange(self.dx):
                for y in xrange(self.dy):
                    if self.align[x][y] is not None: continue
                    al = None
                    al = get_alg(self.align[x-1][y], al)
                    al = get_alg() 
                    
    
        
        