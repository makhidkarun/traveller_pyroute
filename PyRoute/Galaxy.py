'''
Created on Mar 2, 2014

@author: tjoneslo
'''
import logging
import re

class Star (object):
    def __init__ (self, line, starline):
        self.logger = logging.getLogger('PyRoute.Star')

        popCodeM = [0, 10, 13, 17, 22, 28, 36, 47, 60, 78]
        
        self.logger.debug("processing %s" % line)
        data = starline.match(line).groups()
        self.position = data[0]
        self.name = data[1]
        self.uwp = data[2]
        self.tradeCode = data[3].strip()
        self.baseCode = data[8]
        self.zone = data[9]
        self.ggCount = int(data[10][2])
        self.alg = data[12]
        
        self.population = pow (10, int(data[2][4],16)) * popCodeM[int(data[10][0])] 
        self.wtn = 0
    
    
    
class Sector (object):
    def __init__ (self, name, position):
        self.name = name[1:].strip()
        self.x = int(position[1:].split(',')[0])
        self.y = int(position[1:].split(',')[1])
        self.subsectors = {}
        self.alg = {}
        self.worlds = {}

class Galaxy(object):
    '''
    classdocs
    '''


    def __init__(self):
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

        
    def read_sectors (self, sectors):
        for sector in sectors:
            try:
                lines = [line.strip() for line in open(sector)]
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
                star = Star (line, self.starline)
                sec.worlds[star.position] = star
                
            self.logger.info("processes %s worlds" % len(sec.worlds))
                