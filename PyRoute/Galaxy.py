'''
Created on Mar 2, 2014

@author: tjoneslo
'''
import logging
import re
import bisect
import networkx as nx
from Star import Star
from operator import attrgetter

class Sector (object):
    def __init__ (self, name, position):
        self.name = name[1:].strip()
        self.x = int(position[1:].split(',')[0])
        self.y = int(position[1:].split(',')[1])
        self.dx = self.x + 10 * 32
        self.dy = self.y + 10 * 40
        self.subsectors = {}
        self.alg = {}
        self.worlds = {}

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
        self.stars = nx.Graph()
        self.sectors = {}
        self.dx = x * 32
        self.dy = y * 40
        #self.starpos = [[None for x in xrange(self.dx)] for x in xrange(self.dy)]
        self.starwtn = []
        
    def read_sectors (self, sectors):
        for sector in sectors:
            try:
                lines = [line.strip() for line in open(sector,'r')]
            except (OSError, IOError):
                self.logger.error("sector file %s not found" % sector)
                continue
            
            sec = Sector (lines[3], lines[4])
            
            self.logger.info("Sector: {} ({}, {})".format(sec.name, str(sec.x), str(sec.y)) )
            
            lineno = 0
            for line in lines:
                lineno += 1
                if line.startswith ('Hex'):
                    lineno += 2
                    break
                if line.startswith ('# Subsector'):
                    sec.subsectors[line[11:].split(':',1)[0].strip()] = line[11:].split(':',1)[1].strip()
                if line.startswith ('# Alleg:'):
                    sec.alg[line[8:].split(':',1)[0]] = line[8:].split(':',1)[1].strip().strip('"')
                
            for line in lines[lineno:]:
                star = Star (line, self.starline,sec.dx, sec.dy)
                sec.worlds[star.position] = star
            
            self.sectors[sec.name] = sec
            
            self.logger.info("processed %s worlds for %s" % (len(sec.worlds), sec.name))

    def set_positions(self):
        for sector in self.sectors.values():
            for star in sector.worlds.values():
                self.stars.add_node(star)
                self.starwtn.append(star);
        self.logger.info("graph node count: %s" % self.stars.number_of_nodes())
        self.starwtn = sorted(self.starwtn, key=attrgetter('wtn'), reverse=True)
        self.logger.info("wtn array size: %s" % len (self.starwtn))
    
    def set_edges(self):
        self.set_positions()
        for star in self.stars.nodes_iter():
            for neighbor in self.stars.nodes_iter():
                dist = star.hex_distance (neighbor)
                if star == neighbor or\
                    dist > 4 or \
                    neighbor.zone in ['R','F'] or \
                    self.stars.has_edge(neighbor, star):
                    continue
               
                self.stars.add_edge (star, neighbor, {'distance': dist,
                                                      'weight': star.weight(neighbor),
                                                      'trade': 0,
                                                      'btn': self.get_btn(star, neighbor)})
        self.logger.info("Jump routes: %s" % self.stars.number_of_edges())
    
    def get_btn (self, star1, star2):
        btn = star1.wtn + star2.wtn
        if (star1.agricultural and star2.nonAgricultural) or \
            (star1.nonAgricultural and star2.agricultural): 
            btn += 1
        if (star1.resources and star2.industrial) or \
            (star2.resources and star1.industrial): 
            btn += 1
        distance = star1.hex_distance(star2)
        jump_range = [(1, -1), (2, -2), (5, -3), (9, -4), (19, -5), (29, -6), (59, -7), (99, -8), (199, -9)]
        jump_mod = bisect.bisect_left(jump_range, distance)
        
        btn += jump_range[jump_mod][1]
        return btn
    
    def get_trade_to (self, star, trade):

        max_distance = [2, 9, 29, 59, 99, 299]
        
        max_jumps = max_distance[min(max(0, star.wtn - trade), 5)]
        
        
        max_jumps = 99 if star.wtn < 14 and max_jumps > 99 else max_jumps
        max_jumps = 29 if star.wtn < 13 and max_jumps > 29 else max_jumps
        max_jumps = 19 if star.wtn < 12 and max_jumps > 19 else max_jumps
        
        for target in self.stars.nodes_iter():
            if star.hex_distance(target) > max_jumps:
                continue
            route = nx.astar_path(self.stars,star,target)
            
            start = star
            for end in route:
                if end == start:
                    continue
                self.stars[start][end]['trade'] += self.get_btn(star, target);
                start = end
    
    def calculate_routes(self):
        for trade in xrange(15, 7, -1): 
            counter = 0;
            for star in self.starwtn:
                if star.wtn < trade:
                    break
                self.get_trade_to(star, trade)
                counter += 1
            self.logger.info('Processes %s routes at trade %s' % (counter, trade))
        
    def write_routes(self):
        with open("./routes.txt", 'wb') as f:
            nx.write_edgelist(self.stars, f, data=True)
        
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
                    
    
        
        