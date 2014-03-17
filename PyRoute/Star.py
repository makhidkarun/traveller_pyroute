'''
Created on Mar 5, 2014

@author: tjoneslo
'''

import logging

class Star (object):
    def __init__ (self, line, starline, sector):
        self.logger = logging.getLogger('PyRoute.Star')

        popCodeM = [0, 10, 13, 17, 22, 28, 36, 47, 60, 78]
        
        self.sector = sector
        self.logger.debug("processing %s" % line)
        data = starline.match(line).groups()
        self.position = data[0].strip()
        self.set_location(sector.dx, sector.dy)
        self.name = data[1].strip()
            
        self.uwp = data[2].strip()
        self.port = self.uwp[0]
        self.tradeCode = data[3].strip().split()
        self.baseCode = data[8].strip()
        self.zone = data[9].strip()
        self.ggCount = int(data[10][2])
        self.alg = data[12].strip()
        
        self.population =int (pow (10, int(data[2][4],16)) * popCodeM[int(data[10][0])] / 10000000) 
        
        self.rich = 'Ri' in self.tradeCode 
        self.industrial = 'In' in self.tradeCode 
        self.agricultural = 'Ag' in self.tradeCode 
        self.poor = 'Po' in self.tradeCode 
        self.nonIndustrial = 'Ni' in self.tradeCode 
        self.resources = 'As' in self.tradeCode or 'Ba' in self.tradeCode or \
                'Fl' in self.tradeCode or 'Ic' in self.tradeCode or 'De' in self.tradeCode or \
                'Na' in self.tradeCode or 'Va' in self.tradeCode or 'Wa' in self.tradeCode
        self.nonAgricultural = 'Na' in self.tradeCode

        self.calculate_wtn()
        self.tradeIn  = 0
        self.tradeOver = 0
        self.tradeMatched = []
        
    def __unicode__(self):
        return u"%s (%s %s)" % (self.name, self.sector.name, self.position)
        
    def __str__(self):
        name = u"%s (%s %s)" % (self.name,self.sector.name, self.position)
        return name.encode('utf-8')

    def __repr__(self):
        return u"%s (%s %s)" % (self.name, self.sector.name, self.position)
    
    def set_location (self, dx, dy):
        # convert odd-q offset to cube
        q = int (self.position[0:2]) + dx -1
        r = int (self.position[2:4]) + dy -1
        self.x = q
        self.z = r - (q - (q & 1)) / 2
        self.y = -self.x - self.z
        
        # convert cube to axial
        self.q = self.x
        self.r = self.z
        self.col = q - dx + 1
        self.row = r - dy + 1
        
    def hex_distance(self, star):
        return max(abs(self.x - star.x), abs(self.y - star.y), abs(self.z -star.z))
        
    def distance (self, star):
        y1 = self.y * 2
        if not self.x % 2:
            y1 += 1
        y2 = star.y * 2
        if not star.y % 2:
            y2 += 1
        dy = y2 - y1
        if dy < 1:
            dy = -dy;
        dx = star.x - self.x
        if dx < 1:
            dx = -dx
        if dx > dy:
            return dx
        return dx + dy / 2


    def weight (self, star):
        distance_weight = [0, 30, 50, 80, 0, 0, 150 ]
        
        dist = self.hex_distance(star)
        if dist == 4 or dist == 5:
            dist = 6
        weight = distance_weight[dist]
        if self.alg != star.alg:
            weight += 25
        if self.port in ['C', 'D', 'E', 'X']:
            weight += 25
        if self.port in ['D', 'E', 'X']:
            weight += 25
        return weight
    
    def calculate_wtn(self):
        self.wtn = int(self.uwp[4], 16)
        self.tl = int(self.uwp[8],20)
        self.wtn -= 1 if self.tl == 0 else 0
        self.wtn += 1 if self.tl >= 5 else 0
        self.wtn += 1 if self.tl >= 9 else 0
        self.wtn += 1 if self.tl >= 15 else 0
        
        port = self.uwp[0]
             
        if port == 'A':
            self.wtn = (self.wtn * 3 + 13) / 4
        if port == 'B':
            self.wtn = (self.wtn * 3 + 11) / 4
        if port == 'C':
            if (self.wtn > 9):
                self.wtn = (self.wtn + 9) / 2
            else:
                self.wtn = (self.wtn * 3 + 9) / 4
        if port == 'D':
            if (self.wtn > 7):
                self.wtn = (self.wtn + 7) / 2
            else:
                self.wtn = (self.wtn * 3 + 7) / 4
        if port == 'E':
            if (self.wtn > 5):
                self.wtn = (self.wtn + 5) / 2
            else:
                self.wtn = (self.wtn * 3 + 5) / 4
        if port == 'X':
            self.wtn = (self.wtn - 5) / 2
            
        self.wtn = int(round(max(0, self.wtn)))
