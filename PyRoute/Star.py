'''
Created on Mar 5, 2014

@author: tjoneslo
'''

import logging

class Star (object):
    def __init__ (self, line, starline):
        self.logger = logging.getLogger('PyRoute.Star')

        popCodeM = [0, 10, 13, 17, 22, 28, 36, 47, 60, 78]
        
        self.logger.debug("processing %s" % line)
        data = starline.match(line).groups()
        self.position = data[0].strip().decode('utf-8')
        self.set_location(data[0])
        self.name = data[1].strip().decode('utf-8')
            
        self.uwp = data[2].strip()
        self.port = self.uwp[0]
        self.tradeCode = data[3].strip()
        self.baseCode = data[8].strip()
        self.zone = data[9].strip()
        self.ggCount = int(data[10][2])
        self.alg = data[12].strip()
        
        self.population =int (pow (10, int(data[2][4],16)) * popCodeM[int(data[10][0])] / 1000000) 
        
        self.rich = self.tradeCode.count("Ri ") != 0
        self.industrial = self.tradeCode.count("In ") != 0
        self.agricultural = self.tradeCode.count("Ag ") != 0
        self.poor = self.tradeCode.count("Po ") != 0
        self.nonIndustrial = self.tradeCode.count("Ni ") != 0
        self.nonAgricultural = False
        self.resources = False
        self.calculate_wtn()

    def __unicode(self):
        return u"%s (%s)" % (self.name, self.position)
        
    def __str__(self):
        name = u"%s (%s)" % (self.name, self.position)
        return name.encode('utf-8')

    def __repr__(self):
        return u"%s (%s)" % (self.name, self.position)
    
    def set_location (self, loc):
        self.x = int(loc[0:1])
        self.y = int(loc[2:3])
        
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
        
        dist = self.distance(star)
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
        tl = int(self.uwp[8],20)
        self.wtn -= 1 if tl == 0 else 0
        self.wtn += 1 if tl >= 5 else 0
        self.wtn += 1 if tl >= 9 else 0
        self.wtn += 1 if tl >= 15 else 0
        
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

