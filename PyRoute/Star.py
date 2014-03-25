'''
Created on Mar 5, 2014

@author: tjoneslo
'''

import logging

class Star (object):
    def __init__ (self, line, starline, sector):
        self.logger = logging.getLogger('PyRoute.Star')

        
        self.sector = sector
        self.logger.debug("processing [%s]" % line)
        data = starline.match(line).groups()
        self.position = data[0].strip()
        self.set_location(sector.dx, sector.dy)
        self.name = data[1].strip()
            
        self.uwp = data[2].strip()
        self.port = self.uwp[0]
        self.size = self.uwp[1]
        self.atmo = self.uwp[2]
        self.hydro = self.uwp[3]
        self.pop   = self.uwp[4]
        self.gov   = self.uwp[5]
        self.law   = self.uwp[6]
        self.tl = int(self.uwp[8],20)
        self.popCode = int(self.pop,16)

        self.uwpCodes = {'Starport': self.port,
                           'Size': self.size,
                           'Atmosphere': self.atmo,
                           'Hydrographics': self.hydro,
                           'Population': self.pop,
                           'Government': self.gov,
                           'Law Level': self.law,
                           'Tech Level': self.uwp[8],
                           'Pop Code': str(self.popCode)}

        self.tradeCode = data[3].strip().split()
        self.baseCode = data[8].strip()
        self.zone = data[9].strip()
        self.ggCount = int(data[10][2],16)
        self.popM = int(data[10][0])
        self.alg = data[12].strip()
        

        self.uwpCodes = {'Starport': self.port,
                           'Size': self.size,
                           'Atmosphere': self.atmo,
                           'Hydrographics': self.hydro,
                           'Population': self.pop,
                           'Government': self.gov,
                           'Law Level': self.law,
                           'Tech Level': self.uwp[8],
                           'Pop Code': str(self.popM)}
        
        self.rich = 'Ri' in self.tradeCode 
        self.industrial = 'In' in self.tradeCode 
        self.agricultural = 'Ag' in self.tradeCode 
        self.poor = 'Po' in self.tradeCode 
        self.nonIndustrial = 'Ni' in self.tradeCode 
        self.extreme = 'As' in self.tradeCode or 'Ba' in self.tradeCode or \
                'Fl' in self.tradeCode or 'Ic' in self.tradeCode or 'De' in self.tradeCode or \
                'Na' in self.tradeCode or 'Va' in self.tradeCode or 'Wa' in self.tradeCode
        self.nonAgricultural = 'Na' in self.tradeCode

        self.calculate_wtn()
        self.calculate_gwp()
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
     
    def calculate_gwp(self):
        calcGWP = [220, 350, 560, 560, 560, 895, 895, 1430, 2289, 3660, 3660, 3660, 5860, 5860, 9375, 15000, 24400, 24400, 39000, 39000]
        popCodeM = [0, 10, 13, 17, 22, 28, 36, 47, 60, 78]

        self.population =int (pow (10, self.popCode) * popCodeM[self.popM] / 1e7) 
        self.gwp = int (pow(10,self.popCode) * popCodeM[self.popM] * calcGWP[self.tl] / 1e10 )
        if self.rich:
            self.gwp = self.gwp * 16 / 10
        if self.industrial:
            self.gwp = self.gwp * 14 / 10
        if self.agricultural:
            self.gwp = self.gwp * 12 / 10
        if self.poor:
            self.gwp = self.gwp * 8 / 10
        if self.nonIndustrial:
            self.gwp = self.gwp * 8 / 10
        if self.extreme:
            self.gwp = self.gwp * 8 / 10    
        
    def calculate_wtn(self):
        self.wtn = self.popCode
        self.wtn -= 1 if self.tl == 0 else 0
        self.wtn += 1 if self.tl >= 5 else 0
        self.wtn += 1 if self.tl >= 9 else 0
        self.wtn += 1 if self.tl >= 15 else 0
        
        port = self.port
             
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
