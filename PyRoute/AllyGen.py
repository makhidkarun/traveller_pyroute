'''
Created on Mar 26, 2014

@author: tjoneslo
'''
from operator import attrgetter,itemgetter
from collections import defaultdict
import os

class AllyGen(object):
    '''
    classdocs
    '''


    def __init__(self, galaxy):
        '''
        Constructor
        '''
        self.galaxy = galaxy
        self.noOne = ['Ba']
        self.nonAligned = ['Na', 'Va']
        self.sameAligned = [ ('Im', 'Cs')]
        self.borders = {} # 2D array using (q,r) as key, with flags for data
        
    def create_borders (self):
        """
            create borders around various allegiances, Algorithm one.
            From the nroute.c generation system. Every world controls a
            two hex radius. Where the allegiances are the same, the area
            of control is contigious. Every Non-aligned world is
        """
        allyMap = {}

        for star in self.galaxy.stars.nodes_iter():
            alg = star.alg
            # Skip the non-entity worlds
            if alg in self.noOne:
                continue;
            # Collapse non-aligned into each their own 
            if alg in self.nonAligned:
                alg = self.nonAligned[0]
            # Collapse same Aligned into one
            for sameAlg in self.sameAligned:
                if alg in sameAlg:
                    alg = sameAlg[0]
            allyMap[(star.q, star.r)] = alg

        #self._output_map(allyMap, 0)
        
        allyMap = self.step_map(allyMap)
        #self._output_map(allyMap, 1)

        allyMap = self.step_map(allyMap)
        #self._output_map(allyMap, 2)

        self._generate_borders(allyMap)

    def _generate_borders(self, allyMap):
        '''
        Convert the allyMap, which is a dict of (q,r) keys with allegiance codes
        as values, into the borders, which is a dict of (q.r) keys with flags
        indicating which side of the Hex needs to have a border drawn on:
        1: top or bottom 
        2: upper left or upper right
        4: lower left or lower right
        
        This is a bit of a mess because the line drawing in HexMap is a little strange,
        So the complexity is here to make the draw portion quick. 
        '''
        for Hex in allyMap.iterkeys():
            if self._set_border(allyMap, Hex, 2): # up
                neighbor = self._get_neighbor(Hex, 2)
                self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 1
            if self._set_border(allyMap, Hex, 5): # down
                self.borders[Hex] = self.borders.setdefault(Hex, 0) | 1
            if self._set_border(allyMap, Hex, 1): # upper right
                neighbor = self._get_neighbor(Hex, 1)
                if Hex[0] & 1:
                    self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 2
                else:
                    self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 4
            if self._set_border(allyMap, Hex, 3): # upper left
                if Hex[0] & 1:
                    self.borders[Hex] = self.borders.setdefault(Hex, 0) | 2
                else:
                    self.borders[(Hex[0],Hex[1]-1)] = self.borders.setdefault((Hex[0],Hex[1]-1), 0) | 4
            if self._set_border(allyMap, Hex, 0): # down right
                neighbor = self._get_neighbor(Hex, 0)
                if Hex[0] & 1:
                    self.borders[(Hex[0]+1,Hex[1]-1)] = self.borders.setdefault((Hex[0]+1,Hex[1]-1), 0) | 4
                else:
                    self.borders[neighbor] = self.borders.setdefault(neighbor, 0) | 2
            if self._set_border(allyMap, Hex, 4): # down left
                if Hex[0] & 1:
                    self.borders[Hex] = self.borders.setdefault(Hex, 0) | 4
                else:
                    self.borders[Hex] = self.borders.setdefault(Hex, 0) | 2

    def _set_border (self, allyMap, Hex, direction):
        '''
        Determine if the allegiance is different in the direction,
        hence requiring adding a border to the map.
        returns True if border needed, False if not
        '''
        neighbor = self._get_neighbor(Hex, direction)
        # if this is a non-aligned controlled hex, 
        # and the neighbor has no setting ,
        # or the neighbor is aligned 
        # Then no border . 
        if allyMap[Hex] == self.nonAligned[0] and \
            (allyMap.get(neighbor, True) or \
            allyMap.get(neighbor, None) != self.nonAligned[0]):
            return False
        # If not matched allegiance, need a border.
        elif allyMap[Hex] != allyMap.get(neighbor, None):
            return True
        return False

    def _get_neighbor (self, Hex, direction, distance = 1):
        '''
        determine neighboring hex from the q,r position and direction
        '''
        neighbors = [
           [+1,  0], [+1, -1], [ 0, -1],
           [-1,  0], [-1, +1], [ 0, +1]
        ]
        d = neighbors[direction]
        qn = Hex[0] + (d[0] * distance)
        rn = Hex[1] + (d[1] * distance)
        return (int(qn), int(rn))
    
    def step_map(self, allyMap):
        newMap = {}
        for Hex in allyMap.iterkeys():
            self._check_direction(allyMap, Hex, newMap)
        return newMap

    def _check_direction(self, allyMap, Hex, newMap):
        newMap[Hex] = allyMap[Hex]
        for direction in xrange(6):
            neighbor = self._get_neighbor(Hex, direction)
            if not allyMap.get(neighbor, False):
                newMap[neighbor] = allyMap[Hex]
                
    def _output_map(self, allyMap, stage):
        path = os.path.join (self.galaxy.output_path, 'allyMap%s.txt' % stage)
        with open(path, "wb") as f:
            for key, value in allyMap.iteritems():
                f.write("{}-{}: border: {}\n".format(key[0],key[1], value))
        
    def are_allies(self, alg1, alg2):
        '''
        Public function to determine if the Allegiance of two 
        worlds are considered allied for trade purposes or not.
        '''
        if alg1 in self.noOne or alg2 in self.noOne:
            return False
        if alg1 in self.nonAligned or alg2 in self.nonAligned:
            return False
        if alg1 == alg2:
            return True
        for sameAlg in self.sameAligned:
            if alg1 in sameAlg and alg2 in sameAlg:
                return True
        return False
    
              
    def create_ally_map(self):
        # Sort stars by:
        # Better Port, Higher TL, Higher Population
        stars = [star for star in self.galaxy.stars.nodes_iter()]
        stars = sorted(stars, key=attrgetter('popCode'), reverse=True)
        stars = sorted(stars, key=attrgetter('tl'), reverse=True)
        stars = sorted(stars, key=attrgetter('port'))

        allyMap = defaultdict(set)
        allyCount = defaultdict(int)
        # Mark the map with all the stars        
        for star in stars:
            alg = star.alg
            # Collapse non-aligned into one value
            if alg in self.nonAligned or alg in self.noOne:
                alg = self.nonAligned[0]
            # Collapse same Aligned into one
            for sameAlg in self.sameAligned:
                if alg in sameAlg:
                    alg = sameAlg[0]
            allyMap[(star.q, star.r)].add((alg,0))
            allyCount[alg] += 1

        self._output_map(allyMap, 0)
        
        #Pass 1: generate initial allegiance arrays, 
        # with overlapping maps
        for star in stars:
            # skip the E/X ports 
            if star.port in ['E', 'X']: continue
            Hex = (star.q, star.r)
            alg = star.alg
            
            maxRange = ['D','C','B','A'].index(star.port) + 1
            if alg in self.nonAligned:
                maxRange = 2
            for dist in xrange (maxRange):
                neighbor = self._get_neighbor(Hex, 4, dist)
                for direction in xrange(6):
                    for scale in xrange(dist):
                        allyMap[neighbor].add((alg,dist))
                        allyCount[alg] += 1 if alg != self.nonAligned[0] else 0
                        neighbor = self._get_neighbor(neighbor, direction)

        self._output_map(allyMap, 1)

        # Pass 2: find overlapping areas and reduce
        # 1. Non-aligned remain unchanged, 
        # 2. Select neighboring world if any
        # 3. Select largest empire
        for Hex in allyMap.iterkeys():
            if len (allyMap[Hex]) == 1:
                allyMap[Hex] = allyMap[Hex].pop()[0]
            else:
                allyList = sorted([algs for algs in allyMap[Hex]], key=itemgetter(1))
                if allyList[0][1] == 0:
                    allyMap[Hex] = allyList[0][0]
                else:
                    for alg,scope in allyList:
                        pass
                
        self._output_map(allyMap, 2)
        
        self._generate_borders(allyMap)
        
